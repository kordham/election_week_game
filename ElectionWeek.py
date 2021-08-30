#Mohammad Kordzanganeh
#2 Nov 2018
#Election Week game

#importing the necessary packages

import matplotlib.pyplot as plt
import matplotlib.image as img

#Numpy, of course
import numpy as np

# tkinter library to build a GUI
from tkinter import * 
from tkinter import messagebox
from matplotlib.animation import FuncAnimation

#Creating a GUI, first line is initialising it, second line giving its dimensions
outer_frame = Tk(className ="_Election Week_")
outer_frame.geometry("450x100")

#Welcoming and instructions using message boxes. They will run in order.
messagebox.showinfo("Welcome!","Hey, what's up? It's a tight election, we've got to sway as many voters as we can to our side")
messagebox.showinfo("Rules","most important rule: Never close any of the windows manually, they throw exceptions that are far beyond me to handle -it looked ugly without the top ribbon so I decided to leave it be - and also that would lose you the election, so why would you?")
messagebox.showinfo("Objective","For each city/town you'll stand a 50% chance to sway all of its population, score as many followers as you can")
messagebox.showinfo("Instructions","Type down the name of the city/town and click proceed, you can click the Map button to get a geographic feeling for the places. If you win, you'll get to move there on the StarFlight and get all its population, Good luck - you'll need it for London")

# we need to build 3 sets of coordinates, 0th set for the coordinates of all the points, 1st set for wins,2nds for losses
x = [[],[],[]]
y = [[],[],[]]
#content, which will contain everything -but the first line- from the GBplaces.csv
content = []
#initialising variables

#total number of followers, set to zero as is at the beginning
TotalPeople = 0
#inserting a figure and its axes into plt (remember from matplotlib.pyplot)
fig, ax = plt.subplots()
#Counter, counting how many total rounds the games has gone on for, how many wins, losses and an indicator to see if the player won on the previous turn
Counter = [0,0,0,False]
#Total number of rounds allowed for the player
TotalPoints = 10

#A very simple search algorithm:
#takes in a variable name
def search(name):
	#initially, it's not found, so found is set to false
	found = False
	#iterates through the file - to be filled later on
	for index in range(0,len(content)):
		#wherever the string equivalent to name is found, this function sets found to true and return the index of that line in content
		if (content[index][0].lower() == name):
			found = True
			return index
	# if the string, name, isn't found, which could be the case with typos etc, found is false and a value of -1 is returned
	# the -1 is better than a False, because it could get mixed up with 0 which would be the index for plymouth
	if(found==False):
		return -1


try:
	# read in the GBplaces and generate a script, put it in readFile
	readFile = open('GBplaces.csv','r')
	#read in the map
	image = img.imread('map.jpg')
except:
	#if the file isn't in the folder, or is named something else by mistake, this will catch it and alter the user
	messagebox.showinfo("Error"," File(s) not found, try running the program again after checking for any missing files")
	exit()

#we must skip the first line to have consistent reading in, so we make the following boolean variable, indicating whether we've skipped the first line
FirstLineSkipped = False
#now we go through every line in the readFile
for line in readFile:
	#is first line skipped?
	if(FirstLineSkipped):
		#create a 2D array from the file, note that rstrip is to get rid of the \n's and the splitting helps create a 2D array rather than 1D
		content.append((line.rstrip()).split(','))
	#it would be now, and so equate this to true and it'll remain true
	FirstLineSkipped = True
#We're done with the file, close it
readFile.close()

#Mercator map projection: 
#OK, this was much harder than I thought, but using Mercator Projection which is a cylindrical projection - according to Wolfram - we could map a spherical map
#such as earth's into a flat map
for i in range(0,len(content)):
	#turning the values of latitude and longtitude into radians
	try:
		#checking if the values are all float-able
		latRad = float(content[i][3])*np.pi/180
		longRad = float(content[i][4])*np.pi/180
	except:
		messagebox.showinfo("Error","The file must contain only numeric values for latitude and longitude.")
		exit()
	#So Mercator mapping says that x on the map is the same as the longitude on the sphere, although it makes good sense because we're mapping same-latitude lines
	#on a vertical cylinder, however y is slightly done differently, using the below formula. yAct stands for y Actual.
	yAct = np.log(np.tan(latRad)+(np.cos(latRad))**(-1))
	#To appropriately apply the points to the map.jpg, I had to find the scalling semi-experimentally. First choosing some points and trying linear scalling,
	#then amending the scale and translation very slightly to get the desired result. 
	xScaled = longRad*1000+218
	yScaled = yAct*1250-1170
	
	#We add the scaled coordinates to content and x[0] and y[0] for future use
	content[i].append(xScaled)
	content[i].append(yScaled)
	x[0].append(xScaled)
	y[0].append(yScaled)
	

#Display - everything that is the in the invoked screen happens here
def Display():
	
	#set the axis, again very dependent on the map.jpg
	ax.set_xlim(0,300)
	ax.set_ylim(0,500)
	#importing the image into the current session of plt
	imgplot = plt.imshow(image,extent=[0, 300,0, 500])
	
	#The three following statements mark all the places red, winnings purple and losses black respectively.
	plt.plot(x[0],y[0],'ro',markersize=3)
	# #8e00cc is a hex colour code for a purple I thought was close to the Manchester Uni colour
	plt.plot(x[1],y[1],'o',color=('#8e00cc'),markersize=5)
	plt.plot(x[2],y[2],'ko',markersize=5)
	#Turn the axes off
	plt.axis('off')
	#Give plt a title
	plt.title("Map")
	
	#This function animates the start that is moving from a sucessful place to another
	def animate(startingx,startingy,endingx,endingy):
		#To do that, we ought to know the gradient of the straight line the star is going to move through
		gradient = (endingy-startingy)/(endingx-startingx)
		# two variables for xdata and ydata to have something to pop in the first update - more on that soon 
		xdata, ydata = [0],[0]
		#Plot the moving star as an animated blue star with no coordinates
		movingStar, = plt.plot([], [], 'b*', animated=True)
		
		#Initialising the movingStar
		#This could've been done more simply, but this way there is more room for expansion
		def init():
			movingStar, = plt.plot([], [], 'b*', animated=True)
			return movingStar,
		
		#This function updates the position of the star whenever it moves around and about
		def update(frame):
			#popping the first two values, to remove the trail of the star
			xdata.pop(len(xdata)-1)
			ydata.pop(len(ydata)-1)
			#this is very important, because the numpy.linspace only accepts +ve values, the star can't move back to smaller x's without the next line
			if(startingx>endingx):
				frame = -frame
			#2D line equation using a time variable : X = t + X0 and Y = at + Y0 where a is the gradient
			xdata.append(frame+startingx)
			ydata.append(gradient*frame+startingy)
			#then we feed the data to the moving star and return it
			movingStar.set_data(xdata, ydata)
			return movingStar,
		# Counter[3] must be set to False to indicate that the animation has been gone through and there's no need to do it again 
		Counter[3]=False
		#animate the above, with 0.1 sec intervals and alter the t from 0 to the difference between their x.
		ani = FuncAnimation(fig, update, interval=100,frames=np.linspace(0, np.absolute(endingx-startingx)), init_func=init, blit=True,repeat=False)
		#Graphically generate everything
		plt.show()
		del movingStar,
	#Now, we can only use the updating when we have won two places at least and we want it to run only when we have just won a new place
	if(Counter[2]>=2 and Counter[3]==True):
		#Animate, using the x's and y's provided, note that because of the directly-above condition, we don't get OutOfBoundary Exception
		animate(x[1][len(x[1])-2],y[1][len(y[1])-2],x[1][len(x[1])-1],y[1][len(y[1])-1])
		
	else:
		#generate the map without animations
		plt.show()



#First line of the frame making for our GUI, it's top-aligned
first_line = Frame(outer_frame)
first_line.pack(side=TOP)

#Button 1 shows the map with throught the display function, it's left-aligned
button1 = Button(first_line, text="Map", command=Display)
button1.pack(side=LEFT)

#Entry for capturing the user's text input
entry = Entry(outer_frame)
entry.pack()

#Showing the scores
lScoreTxt = Label(outer_frame,text="Number of followers: ")
lScore = Label(outer_frame, text="Nobody yet!")


def proceed():
	#-1 returned from the search proves useful here, if the item isn't found a pop-up message showss up
	if(search(entry.get().lower())!=-1):
		#if the searching is succesful, the index is returned here
		index = search(entry.get().lower())
		#Checking if this line has already been looked - or appended in this case
		if(len(content[index])==7):
			#random function generates a number between 0 and 1
			luckIndicator = np.random.rand()
			#if the number is higher than 0.5 this the user wins, giving them 50-50 chance of winning
			if(luckIndicator>0.5):
				#adding the winning coordinates to the winning database
				x[1].append(content[index][5])
				y[1].append(content[index][6])
				#Calling the TotalPeople global variable & adding the population to it
				global TotalPeople
				try:
					#Checking if all the population values are positive integers
					TotalPeople+=int(content[index][2])
				except:
					messagebox.showinfo("Error","Population values must all be positive integers, check the file")
					exit()
				#Altering the labels and counter as appropriate
				lScore.config(text=str(TotalPeople))
				Counter[2]+=1
				lWon.config(text="Won: " + str(Counter[2]))
				#Alert in form of a message box indicating a win 
				messagebox.showinfo("Win","Congratulations, we won "+ content[index][0])
				#setting Counter[3] to True to run the animation
				Counter[3]=True
			else:
				#If they lose, add this point to the losing database
				x[2].append(content[index][5])
				y[2].append(content[index][6])
				#appropriate values for labels and counter and a little thing extra for London
				Counter[1]+=1
				lLoss.config(text="Lost: " + str(Counter[1])) 
				if(content[index][0].lower()=='london'):
					messagebox.showinfo("Loss","Oh NO! We lost London!! RIP xd")
				else:
					#indicating which city/town has been lost
					messagebox.showinfo("Loss","We lost " + content[index][0] + ", but that's ok, we'll catch up")
				#Redundant but useful to avoid errors and just to be more complete, set the Counter[3] to False to stop animating
				Counter[3]=False
			#Increment this city/town's line to indicate that it's already been visited
			content[index].append(True)
			#increment the round and alter the labels as appropriate
			Counter[0]+=1
			lRemaining.config(text="Remaining: "+str(TotalPoints - Counter[0]))
			
			#When user runs out of rounds, they will see this message along with their score, the program exits afterwards
			if(Counter[0]>=TotalPoints):
				messagebox.showinfo("Done!", "You managed to gather %d followers, well done. Hey- give it another try!"%TotalPeople)
				exit()
			#Win or Loss, Display the results	
			Display()
			
		#Do none of the above if this city/town has been visited before:	
		else:
			messagebox.showinfo("Error","You have already visited this "+content[index][1].lower() + ".")
	
		
	#Give an error if the name doesn't exist
	else:
	   messagebox.showinfo("Error", "The selected place, "+entry.get()+", is not in our database - I wouldn't worry too much about there.")
#clearing and showing the initial value for entry 
entry.delete(0, END)
entry.insert(0, "Manchester")

#second line stacked on the outer_frame, it's top-aligned
second_line = Frame(outer_frame)
second_line.pack(side=TOP)

#Attaching the 
lScoreTxt.pack(side=LEFT)
lScore.pack(side=LEFT)

#programming the exit button and attaching it
def buttonExit():
	exit()
buttonExit = Button(second_line, text='exit', command=buttonExit)
buttonExit.pack()

#Attaching the ProceedButton
buttonProceed = Button(first_line, text='Proceed',command=proceed)
buttonProceed.pack(side=LEFT)

#Third line stacked on the outer_frame, it's auto-aligned
third_line = Frame(outer_frame)
third_line.pack()

#Labels given appropriate values
lRemaining = Label(third_line, text ="Remaining: "+ str(TotalPoints))
lWon = Label(third_line, text ="Won: " + "0")
lLoss = Label(third_line,text ="Loss: " +"0")
lWon.pack(side=LEFT)
lLoss.pack(side=LEFT)
lRemaining.pack(side=LEFT)

#Closing the tkinter outer_frame here
outer_frame.mainloop()




