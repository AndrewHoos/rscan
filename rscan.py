#! /usr/local/bin/python3

## Author: Andrew Hoos
## File: rscan.py
## Purpose: the purpose of this script is to take a GAMESS file and scan over one of the coordinates 
## Limitations: The input file must be a GAMESS input file prepared for execution with the geometry of an optimized minimum 
## usage: python3 rscan.py molecule.inp > molecule.log
## or rscan.py molecule.inp > molecule.log
## Version: 0.4
## Last edited: 6/1/12



import os
import sys
import re
import operator
from subprocess import call
import GAMESS
from GAMESSFile import *
from GMSUtil import *

#CONSTANTS 
FIRST_COORD_LINE = 5

#Found on http://code.activestate.com/recipes/442460-increment-numbers-in-a-string/
def nextInputFleNameFromLastInputFileName(s):
   
    lastNum = re.compile(r'(?:[^\d]*(\d+)[^\d]*)+')
    match = lastNum.search(s)
    if match:
        next = str(int(match.group(1))+1)
        start, end = match.span(1)
        s = s[:max(end-len(next), start)] + next + s[end:]
    return s

# takes the name of the last input file opens the corresponding out file and returns the 
# optimized coordinate
def readCoordinateFromLastFile(lastFileName,coordinate):
  
  try:
    lastOutFile = open(re.sub("\.inp", ".out",lastFileName))
  except IOError as e:
    try:
      lastOutFile = open(re.sub("\.inp", ".log",lastFileName))
    except IOError as e:
      print("I was unable to find the output for the lastFile")
      print(lastFileName)
      print(re.sub("\.inp", ".log",lastFileName))
      sys.exit()
  
  

  ##Two competing file types
  
  coordinateLineNumber = GAMESS.coordinateLine(coordinate)  
  coordinateType = GAMESS.ZMATCoordinateType(coordinate)
  lineNumber=0
  flag=False
  returnLine=""
  
  ZMATMode=False
  COORDMode=False
  
  dashedLineCount=0
  coordinateLineCount=0
  for line in lastOutFile:
    if re.search("fail",line.lower()):
      print("WARNING:The last file failed to converged")
  
    # found equilibrium geometry
    if re.search("EQUILIBRIUM GEOMETRY LOCATED",line):
      flag=True
      dashedLineCount=1
    
    # if the coordinates in ZMatrix mode use this 
    if flag and re.search("THE CURRENT FULLY SUBSTITUTED Z-MATRIX IS",line):
      ZMATMode=True
      flag = False
      lineNumber=FIRST_COORD_LINE-2
      
      
    if lineNumber == coordinateLineNumber and ZMATMode:
      if lineNumber == FIRST_COORD_LINE:
        returnLine = re.match(".*(\d+\.\d+)",line).group(1)
      elif lineNumber == FIRST_COORD_LINE + 1:
        if coordinateType == "bond":
          returnLine = re.match(".*(\d+\.\d+).* +(-?\d+\.\d+)",line).group(1)
        else:
          returnLine = re.match(".*(\d+\.\d+).* +(-?\d+\.\d+)",line).group(2)
      elif lineNumber >= FIRST_COORD_LINE + 2:
        if coordinateType == "bond":

          returnLine = re.match(".* +(\d+\.\d+).* +(-?\d+\.\d+).* +(-?\d+\.\d+)",line).group(1)
        elif coordinateType == "angle":
          returnLine = re.match(".* +(\d+\.\d+).* +(-?\d+\.\d+).* +(-?\d+\.\d+)",line).group(2)
        else:
          returnLine = re.match(".* +(\d+\.\d+).* +(-?\d+\.\d+).* +(-?\d+\.\d+)",line).group(3)
      
    if lineNumber:
      lineNumber+=1
    
    
    #if the coordinates are given in list mode
    if flag and re.search("INTERNAL COORDINATES",line):
      COORMode = True
      flag = False
    
    
    if dashedLineCount == 5:
      if re.match(" *\d.*\d+\.\d+ +(-?\d+\.\d+)",line):
        coordinateLineCount+=1
        if coordinateLineCount==coordinate:
          returnLine = re.match(" *\d.*\d+\.\d+ +(-?\d+\.\d+)",line).group(1)
      else:
        dashedLineCount = 0
    
    if dashedLineCount> 0 and dashedLineCount<5:
      if re.search("-+\n",line):
        dashedLineCount+=1
      
  if returnLine == "":
    print("ERROR: No minimum was found in the last file")
    sys.exit()
  else:  
    lastOutFile.close()  
    return returnLine      

def prepareFirstInput(coordinate, stepSize):
  
  #read the first file 
  gmsFile = GMSFile(sys.argv[1])
  
  # increase MAXIT
  gmsFile["CONTRL"]["MAXIT"]=200
  if "MCSCF" in gmsFile:
    gmsFile["MCSCF"]["MAXIT"]=200
  
  # add the freeze point
  gmsFile["STATPT"]["IFREEZ(1)"] = coordinate
  
  #increment the coordinate
  gmsFile["DATA"][coordinate-1] = float(gmsFile["DATA"][coordinate-1]) +stepSize

  # read the vec
  VEC=GAMESS.readVECGroupsFromFile(re.sub("\.inp",".dat",sys.argv[1]))[-1]
  
  # prepare GUESS group
  if "GUESS" not in gmsFile:
    gmsFile["GUESS"] = GMSFile.parse_group("$GUESS GUESS=MOREAD $END")
  else:
    gmsFile["GUESS"]["GUESS"]="MOREAD"
  gmsFile["GUESS"]["NORB"]= GAMESS.numberOfOrbitalsinVEC(VEC)
  
  # add VEC group
  try:
    del gmsFile["VEC"]
  except:
    pass
  gmsFile["VEC"]=VEC.strip()
  
  if gmsFile["CONTRL"]["SCFTYP"] == "UHF":
    del gmsFile["GUESS"]
  
  
  #add the 1 postfix before file type e.g. test.inp > test1.inp
  nextInFileName = re.sub("\.inp","1.inp",sys.argv[1])
  #write the file
  nextInFile = open(nextInFileName, 'w')
  nextInFile.write(str(gmsFile))
  nextInFile.close()
  
  return nextInFileName
  
def prepareNextFile(LastInputFileName, coordinate, stepSize):
  
  #read the first file 
  gmsFile = GMSFile(LastInputFileName)
  
  # increase MAXIT
  gmsFile["CONTRL"]["MAXIT"]=200
  if "MCSCF" in gmsFile:
    gmsFile["MCSCF"]["MAXIT"]=200
  
  # add the freeze point
  gmsFile["STATPT"]["IFREEZ(1)"] = coordinate
  
  #read the optimized geometry
  gmsFile["DATA"] = GMSFile.parse_group(GMSFileReader.read_data_group(re.sub("\.inp",".log",LastInputFileName)))
  
  #increment the coordinate
  gmsFile["DATA"][coordinate-1] = float(gmsFile["DATA"][coordinate-1]) +stepSize

  # read the vec
  VEC=GAMESS.readVECGroupsFromFile(re.sub("\.inp",".dat",sys.argv[1]))[-1]
  
  # add VEC group
  try:
    del gmsFile["VEC"]
  except:
    pass
  gmsFile["VEC"]=VEC.strip()
  
  #add the 1 postfix before file type e.g. test.inp > test1.inp
  nextInFileName = nextInputFleNameFromLastInputFileName(LastInputFileName)
  #write the file
  nextInFile = open(nextInFileName, 'w')
  nextInFile.write(str(gmsFile))
  nextInFile.close()
  
  return nextInFileName

def outFile(inFileName):
  return re.sub(r'.inp', r'.log',inFileName)
  


def runFile(inFileName):
  outFileName = outFile(inFileName)
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
  number = GAMESS.coordinateNumber(coordinateIndex)
  type = GAMESS.ZMATCoordinateType(coordinateIndex)
  
  
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
  

def prepareHessian(inputFileName, coordinate, stepSize):
  # create the GMSFile
  
  gFile = GMSFile(inputFileName)
  # remove STATPT group
  if "STATPT" in gFile:
    del gFile["STATPT"]
   # Add the FORCE group
  gms_group = GMSFile.parse_group("$FORCE METHOD=SEMINUM VIBSIZ=0.010000 VIBANL=.TRUE. $END")
  gFile["FORCE"]=gms_group
   # set the RUNTYP to HESSIAN
  gFile["CONTRL"]["RUNTYP"]="HESSIAN"
  
  #unstep the coordinate
  gFile["DATA"][coordinate-1] = float(gFile["DATA"][coordinate-1]) - stepSize
  
  # create the new file name
  match = re.search("(.*)(\d+)\.inp",inputFileName)
  hessFileName = match.group(1)+str(int(match.group(2))-1)+"h"+".inp"
  # write file
  hessFile = open(hessFileName,"w")
  hessFile.write(str(gFile))
  hessFile.close()
  return hessFileName
  
  

def prepareMP2(inputFileName, coordinate, stepSize):
  # create the GMSFile
  gFile = GMSFile(inputFileName)
  # remove STATPT group
  if "STATPT" in gFile:
    del gFile["STATPT"]
  gFile["CONTRL"]["MPLEVL"]="2"
  gFile["CONTRL"]["RUNTYP"]="ENERGY"
  
  #unstep the coordinate
  gFile["DATA"][coordinate-1] = float(gFile["DATA"][coordinate-1]) - stepSize
  
  # create the new file name
  match = re.search("(.*)(\d+)\.inp",inputFileName)
  MP2FileName = match.group(1)+str(int(match.group(2))-1)+"MP"+".inp"
  # write file
  MP2File = open(MP2FileName,"w")
  MP2File.write(str(gFile))
  MP2File.close()
  return MP2FileName


##########################################
####       BEGIN PROGRAM HERE         ####
##########################################






#ask which coordinate to scan over
scan = askForCoordinateStepAndStepCount()

#prepare first Files
currentFileName = prepareFirstInput(scan[0], scan[2])
#run first files
runFile(currentFileName)


#for each step
for i in range(scan[1]-1):
  #prepare the next input
  currentFileName = prepareNextFile(currentFileName, scan[0], scan[2])
  #prepare the hess and MP2 for the last step
  currentHessian = prepareHessian(currentFileName, scan[0], scan[2])
  currentMP2 = prepareMP2(currentFileName, scan[0], scan[2])
  runFile(currentHessian)
  runFile(currentMP2)
  runFile(currentFileName)
#create next file to run last hessian and MP2
currentFileName = prepareNextFile(currentFileName, scan[0], scan[2])
currentHessian = prepareHessian(currentFileName, scan[0], scan[2])
currentMP2 = prepareMP2(currentFileName, scan[0], scan[2])
runFile(currentHessian)
runFile(currentMP2)