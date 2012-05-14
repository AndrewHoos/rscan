## Author: Andrew Hoos
## File: rscan.py
## Purpose: the purpose of this script is to take a GAMESS file and scan over one of the coordinates 
## Limitations: The input file must be a GAMESS input file prepared for execution with the geometry of an optimized minimum 
## usage: python3 rscan.py molecule.inp > molecule.log
## Version: 0.1
## Last edited: 5/10/12





import os
import sys
import re
import operator
from subprocess import call

#CONSTANTS 
SCR_LOCATION = "~/Desktop/gamess/scr/"
FIRST_COORD_ROW = 5



#Found on http://code.activestate.com/recipes/442460-increment-numbers-in-a-string/
def increment(s):
    """ look for the last sequence of number(s) in a string and increment """
    lastNum = re.compile(r'(?:[^\d]*(\d+)[^\d]*)+')
    match = lastNum.search(s)
    if match:
        next = str(int(match.group(1))+1)
        start, end = match.span(1)
        s = s[:max(end-len(next), start)] + next + s[end:]
    return s

def DETParse(s):
	element = re.compile((r'([a-zA-Z][a-zA-Z]?)'))
	match = element.match(s)
	c = match.group(1).lower()
	if c == 'h':
		return (0,1,1)
	elif c == 'he':
		return (1,0,0)
	elif c == 'li':
		return (1,4,1)
	elif c == 'be':
		return (1,4,2)
	elif c == 'b':
		return (1,4,3)
	elif c == 'c':
		return (1,4,4)
	elif c == 'n':
		return (1,4,5)
	elif c == 'o':
		return (1,4,6)
	elif c == 'f':
		return (1,4,7)
	elif c == 'cl':
		return (5,4,7)	
		
def DETGroup(DET):
	outString = " $DET NCORE="
	outString += str(DET[0])
	outString += " NACT="
	outString += str(DET[1])
	outString += " NELS="
	outString += str(DET[2])
	outString += " $END\n"
	return outString

# takes the name of the last input file opens the corresponding out file and returns the 
# optimized coordinate
def readCoordinateFromLastFile(lastFile,coordinate):

	outFileName = re.sub(".inp", ".out",lastFile)
	outFile = open(outFileName)
	
	cIndex=0
	startCount=0
	for line in outFile:
		if re.search("EQUILIBRIUM GEOMETRY LOCATED",line):
			startCount=1
		if startCount == 5:
			if re.match(" *\d.*\d+\.\d+ +(\d+\.\d+)",line):
				cIndex+=1
				if cIndex==coordinate:
					return re.match(" *\d.*\d+\.\d+ +(\d+\.\d+)",line).group(1)
			else:
				startCount =0
		if startCount> 0 and startCount<5:
			if re.search("-+\n",line):
				startCount+=1

#returns a type of coordinate for a coordinate index
def typeForCoordinateIndex(coordinateIndex):
	if coordinateIndex%3==1 or  coordinateIndex==2:
		return "bond"
	elif coordinateIndex%3==2 and coordinateIndex>3 or coordinateIndex ==3: 
		return "angle"
	elif coordinateIndex%3==0 and coordinateIndex>3:
		return "dihedral"
	else:
		return "error"

#return coordinate number for a coordinate index
# e.g. numberForCoordinateIndex(3) returns 1 for the the first angle
def numberForCoordinateIndex(coordinateIndex):
	type = typeForCoordinateIndex(coordinateIndex)
	#print("hey " + type)
	if type == "bond":
		if coordinateIndex > 3:
			return coordinateIndex//3 + 2
		else:
			return coordinateIndex
	elif type == "angle":
		if coordinateIndex > 3:
			return coordinateIndex//3+1
		else:
			return 1
	elif type == "dihedral":
		return coordinateIndex//3 - 1
	else:
		print("numberForCoordinateIndex: invalid type")
		sys.exit()

#increments the coordinate corresponding to coordinateIndex in a row of the DATA group by stepSize
def lineFromLastOutputWithIncrement(lastInFileName, line, coordinate, stepSize):
	
	#finds the type and row
	type = typeForCoordinateIndex(coordinate)
	dataRow = dataRowForCoordinate(coordinate)
	
	
	
	returnLine = ""
	if dataRow == FIRST_COORD_ROW:
		nonCoordinates =re.split("\d+\.\d+",line)
		returnLine += nonCoordinates[0]
		returnLine += str(float(readCoordinateFromLastFile(lastInFileName,1))+ stepSize)
		returnLine += "\n"
	elif dataRow == FIRST_COORD_ROW + 1:
		
		nonCoordinates =re.split("\d+\.\d+",line)
		returnLine += nonCoordinates[0]
		
		if type == "bond":
			returnLine += str(float(readCoordinateFromLastFile(lastInFileName,2))+ stepSize)
		else:
			returnLine += readCoordinateFromLastFile(lastInFileName,2)
		
		returnLine += nonCoordinates[1]
		
		if type == "angle":
			returnLine += str(float(readCoordinateFromLastFile(lastInFileName,3))+ stepSize)
		else:
			returnLine += readCoordinateFromLastFile(lastInFileName,3)
		
		returnLine += "\n"
		
	elif dataRow >= FIRST_COORD_ROW + 2:
		
		nonCoordinates =re.split("\d+\.\d+",line)
		returnLine += nonCoordinates[0]
		
		if type == "bond":
			returnLine += str(float(readCoordinateFromLastFile(lastInFileName,3*dataRow-17))+ stepSize)
		else:
			returnLine += readCoordinateFromLastFile(lastInFileName,3*dataRow-17)
		
		returnLine += nonCoordinates[1]
		
		if type == "angle":
			returnLine += str(float(readCoordinateFromLastFile(lastInFileName,3*dataRow-16))+ stepSize)
		else:
			returnLine += readCoordinateFromLastFile(lastInFileName,3*dataRow-16)
	
		returnLine += nonCoordinates[2]
		
		if type == "dihedral":
			returnLine += str(float(readCoordinateFromLastFile(lastInFileName,3*dataRow-15))+ stepSize)
		else:
			returnLine += readCoordinateFromLastFile(lastInFileName,3*dataRow-15)
		returnLine += "\n"
		
	return returnLine
	
def lineFromLastOutput(lastInFileName,line,dataRow):
	returnLine = ""
	if dataRow == FIRST_COORD_ROW:
		nonCoordinates =re.split("\d+\.\d+",line)
		returnLine += nonCoordinates[0]
		returnLine += readCoordinateFromLastFile(lastInFileName,1)
		returnLine += "\n"
	elif dataRow == FIRST_COORD_ROW + 1:
		nonCoordinates =re.split("\d+\.\d+",line)
		returnLine += nonCoordinates[0]
		returnLine += readCoordinateFromLastFile(lastInFileName,2)
		returnLine += nonCoordinates[1]
		returnLine += readCoordinateFromLastFile(lastInFileName,3)
		returnLine += "\n"
	elif dataRow >= FIRST_COORD_ROW + 2:
		nonCoordinates =re.split("\d+\.\d+",line)
		returnLine += nonCoordinates[0]
		returnLine += readCoordinateFromLastFile(lastInFileName,3*dataRow-17)
		returnLine += nonCoordinates[1]
		returnLine += readCoordinateFromLastFile(lastInFileName,3*dataRow-16)
		returnLine += nonCoordinates[2]
		returnLine += readCoordinateFromLastFile(lastInFileName,3*dataRow-15)
		returnLine += "\n"
	return returnLine

def prepareFirstFile(coordinate, stepSize):

	
	#openFirstFile
	lastInFile = open(sys.argv[1], 'r')
	#add the 1 postfix before file type e.g. test.inp > test1.inp
	nextInFileName = re.search("(.*)\.inp",sys.argv[1]).group(1)+"1"+".inp"
	nextInFile = open(nextInFileName, 'w')
	
	
	#find the coordinateRow
	if (coordinate-1)//3 > 0:
		coordinateRow = 6 + (coordinate-1)//3
	elif (coordinate-1)//3 == 0:
		if coordinate == 1:
			coordinateRow = 5
		else:
			coordinateRow = 6
	else:
		sys.exit()
	
	#copy file
	dataRow = 0
	DET = [0,0,0]
	
	for line in lastInFile:
		#check for $DATA group
		datagroup = re.compile(r'\$DATA')
		dataMatch = datagroup.search(line)
		
		#if line begins $DATA section
		if dataMatch:
			dataRow += 1
		
	
		#check for $END token	
		datagroup = re.compile(r'\$END')
		endMatch = datagroup.search(line)
		
		#if the $END token is for the $DATA group then stop counting
		if dataRow  and endMatch:
			dataRow = 0
			# This code was removed because it is assumed that the 
			# starting file is already minimzed and thus must have a
			# DET group if needed
			
			#DET
			##write the last line and replace it with the DET group
			#outFile.write(line)
			#line = DETGroup(DET)
			#END DET
		
		#if inside the data group	
		if dataRow:

			if dataRow >= FIRST_COORD_ROW and dataRow != coordinateRow:
				line = lineFromLastOutput(sys.argv[1], line, dataRow)
			#if we ne to increment a coorinate in this line
			if dataRow >= FIRST_COORD_ROW and dataRow == coordinateRow:
				line = lineFromLastOutputWithIncrement(sys.argv[1], line, coordinate, stepSize)
				
			#DET	
			#if dataRow >= FIRST_COORD_ROW-1:	
				#DET = tuple(map(sum,zip(DET,DETParse(line))))	
			#END DET
			dataRow += 1
			
			
			
		#Always write the line
		nextInFile.write(line)
		
	#Increase MAXIT for convergence 
	nextInFile.write(" $MCSCF MAXIT=200 $END\n")
	
	#Freeze coorinate in STATPT
	nextInFile.write(" $STATPT IFREEZ(1)=" +str(coordinate)+" $END\n")
	
	
	
	# TODO: v0.2 add $GUESS group
	#outFile.write(" $GUESS GUESS=MOREAD MORB="+str(orbitalCount)+" $END")
	
	lastInFile.close()
	nextInFile.close()
	return nextInFileName

#returns the line number in the data group of the coordinate number
def dataRowForCoordinate(coordinate):
	row = 0
	if (coordinate-1)//3 > 0:
		row = FIRST_COORD_ROW + 1 + (coordinate-1)//3
	elif (coordinate-1)//3 == 0:
		if coordinate == 1:
			row = FIRST_COORD_ROW
		else:
			row = FIRST_COORD_ROW + 1
	else:
		sys.exit()
	return row 


def prepareNextFile(currentFileName, coordinateIndex, stepSize):
	# open previous input file
	inFile = open(currentFileName, 'r')
	# create new input file 
	outFile = open(increment(currentFileName), 'w')
	
	#find the coordinateRow
	coordinateRow = dataRowForCoordinate(coordinateIndex)
	
	#copy file
	dataRow = 0
	# copy 
	for line in inFile:
		#check for $DATA group
		datagroup = re.compile(r'\$DATA')
		dataMatch = datagroup.search(line)
		
		#if line begins $DATA section
		if dataMatch:
			dataRow += 1
		
	
		#check for $END token	
		datagroup = re.compile(r'\$END')
		endMatch = datagroup.search(line)
		
		#if the $END token is for the $DATA group then stop counting
		if dataRow  and endMatch:
			dataRow = 0

		
		#if inside the data group	
		if dataRow:
			
			if dataRow >= FIRST_COORD_ROW and dataRow != coordinateRow:
				line = lineFromLastOutput(currentFileName, line, dataRow)
			#if we ne to increment a coorinate in this line
			if dataRow >= FIRST_COORD_ROW and dataRow == coordinateRow:
				line = lineFromLastOutputWithIncrement(line, coordinateIndex, stepSize)
				
			dataRow += 1
			
			
		#Always write the line
		outFile.write(line)
	
		
	inFile.close()
	outFile.close()

	return increment(currentFileName)
	
def outFile(inFileName):
	print(inFileName)
	return re.sub(r'.inp', r'.log',inFileName)
	
def runFile(inFileName):
	outFileName = outFile(inFileName)
	print(outFileName)
	
	call(["rungms", str(inFileName)] ,stdout = open(str(outFileName),"w")  )
	
# returns a list containing coordinate step size and step count 
def askForCoordinateStepAndStepCount():
	
	#open the input file
	inFile = open(sys.argv[1], 'r')
	
	print("The Data section of the input file is listed below:")
	dataRow = 0
	for line in inFile:
		#check for $DATA group
		datagroup = re.compile(r'\$DATA')
		dataMatch = datagroup.search(line)
		
		#if line begins $DATA section
		if dataMatch:
			dataRow += 1
			
		#check for $END token	
		datagroup = re.compile(r'\$END')
		endMatch = datagroup.search(line)
		
		#if the $END token is for the $DATA group then stop counting
		if dataRow  and endMatch:
			sys.stdout.write(line)
			dataRow = 0
			
		
		#if inside the data group	
		if dataRow:
			sys.stdout.write(line)
			dataRow += 1
	
	inFile.close()

	
	print("")
	coordinateIndex = int(input("which coordinate do you want to scan over?  "))
	
	
	#define coordinate type and number
	number = numberForCoordinateIndex(coordinateIndex)
	type = typeForCoordinateIndex(coordinateIndex)
	
	
	print("")
	numberOfSteps = int(input("numberOfSteps?  "))
	print("")	
	stepSize = float(input("stepSize?  "))
	
	print("")
	print("You have selected to scan " + type + " " + str(number) + " over " + str(numberOfSteps) + " steps in increments of " + str(stepSize))
	abort = input("Do you wish to confirm or abort?(C/A)  ")
	
	if abort.lower() == "a":
		sys.exit()
	else:
		return [coordinateIndex,numberOfSteps,stepSize]
	


##########################################
####       BEGIN PROGRAM HERE         ####
##########################################


		
		
			
	



#ask which coordinate to scan over
#scan = askForCoordinateStepAndStepCount()
scan = [1,1,.1]
#prepare and run the first file
currentFileName = prepareFirstFile(scan[0], scan[2])

runFile(currentFileName)

# for each step 
# note: the - 1 is for the first file prepared

for i in range(scan[1]-1):
	currentFileName = prepareNextFile(currentFileName, scan[0], scan[2])
	runFile(currentFileName)
	

	

	