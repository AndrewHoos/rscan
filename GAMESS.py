#! /usr/local/bin/python3

import sys

bond="bond"

angle="angle"

dihedral="dihedral"

FIRST_COORD_LINE=5

# coordinate type for coordinate
# expects a positive integer
# returns a string
def ZMATCoordinateType(coordinate):
	if coordinate % 3 == 1 or coordinate == 2:
		return bond
	elif (coordinate % 3 == 2 and coordinate > 3) or coordinate == 3: 
		return angle
	elif coordinate % 3 == 0 and coordinate > 3:
		return dihedral
	else:
		print("GAMESS.typeForCoordinate(coordinate)")
		print("invalid coordinate: " + str(coordinate))
		sys.exit()

# The coordinate number i.e. bond 1 bond 2 
# expects a positive integer
# returns a positive integer
def coordinateNumber(coordinate):
	type = ZMATCoordinateType(coordinate)
	if type == "bond":
		if coordinate > 3:
			return coordinate//3 + 2
		else:
			return coordinate
	elif type == "angle":
		if coordinate > 3:
			return coordinate//3+1
		else:
			return 1
	elif type == "dihedral":
		return coordinate//3 - 1
	else:
		print("GAMESS.coordinateLineNumber")
		print("invalid coordinate: " + str(coordinate))
		sys.exit()
		
# Returns the line number of a coordinate in the $DATA group
# Expects a positive integer
# Returns a positive integer
# Note: The line number is numbered from the beginning of the $DATA group
def CoordinateLine(coordinate):
	line = 0
	if (coordinate-1)//3 > 0:
		line = FIRST_COORD_LINE + 1 + (coordinate-1)//3
	elif (coordinate-1)//3 == 0:
		if coordinate == 1:
			line = FIRST_COORD_LINE
		else:
			line = FIRST_COORD_LINE + 1
	else:
		print("GAMESS.CoordinateLine")
		print("invalid coordinate: " + str(coordinate))
		sys.exit()
	
	return line 