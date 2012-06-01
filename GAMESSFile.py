import re
import sys
from collections import OrderedDict

class GMSGroup(OrderedDict):
	def __init__(self,group_name):
		self.name = group_name
		super(GMSGroup,self).__init__()
		

	def __str__(self):
		return_string="$" + self.name
		i=0
		for variable in self:
			i += 1
			return_string += " "+str(variable)+"="+str(self[variable])
			if i % 5 == 0:
				return_string += "\n "	
		return_string += " $END"
		return return_string
		
		
class GMSDATAGroup(list):
	def __init__(self,group_content):
		super(GMSDATAGroup,self).__init__()
		lines = re.split("\n",group_content)
		self.name = "DATA"
		self.atoms = []
		self.indexes = []
		self.title = lines[1].strip()
		self.point_group = lines[2].strip()
		for line in lines[3:-1]:
			match = re.search("([a-zA-Z]+)( +(\d+) +(-?\d+.\d+))?( +(\d+) +(-?\d+.\d+))?( +(\d+) +(-?\d+.\d+))?",line)
			if	match:
				regex_groups = list(match.groups())
				#add the atom
				self.atoms.append(regex_groups[0])
				
				# construct a list of indicies and add them to the class variable once full
				ind = []
				
				if regex_groups[1]:
					ind.append(regex_groups[2])
					self.append(regex_groups[3])
				if regex_groups[4]:
					ind.append(regex_groups[5])
					self.append(regex_groups[6])
				if regex_groups[7]:
					ind.append(regex_groups[8])
					self.append(regex_groups[9])
				
				if len(ind):
					self.indexes.append(ind)
			else:
				print("Logic error")
				
	def __str__(self):
		return_string = ""
		return_string += "$" + self.name+"\n"
		return_string += self.title + "\n"
		return_string += self.point_group + "\n"
		return_string += self.atoms[0] + "\n"
		if len(self.atoms) >= 2:
			return_string += str(self.atoms[1]) + "    " 
			return_string += str(self.indexes[0][0]) +"    "+ str(self[0]) +"\n"
		if len(self.atoms) >= 3:
			return_string += str(self.atoms[2]) + "    " 
			return_string += str(self.indexes[1][0]) +"    "+ str(self[1]) +"    " 
			return_string += str(self.indexes[1][1]) +"    "+ str(self[2]) +"\n"
		if len(self.atoms) >= 4:
			for i in range(3,len(self.atoms)):
				return_string += str(self.atoms[i]) + "    " 
				return_string += str(self.indexes[i-1][0]) +"    "+ str(self[3*i-6]) +"    " 
				return_string += str(self.indexes[i-1][1]) +"    "+ str(self[3*i-5]) +"    "
				return_string += str(self.indexes[i-1][2]) +"    "+ str(self[3*i-4]) +"\n"
		return_string +=" $END"
		return return_string
		
		
		
		
		
class GMSFile(OrderedDict):
	
	def parse_group(group_content):
		split =re.split("\s+",group_content)
		groupName = re.search("\$([A-Z]+)",split[0]).group(1)
		if groupName == "DATA":
			return GMSDATAGroup(group_content)
		elif groupName == "VEC" or groupName =="ZMAT":
			return group_content
		try:
			
			del split[0]
			del split[-1]
			variables = GMSGroup(groupName)
			for i in split:	
				variableName=re.search("(.*)=(.*)",i).group(1)
				variableValue = re.search("(.*)=(.*)",i).group(2)
				variables[variableName] = variableValue
			return variables
		except:
			return group_content

	def __init__(self, file_path=None):
		super(GMSFile,self).__init__()
		if file_path:
			GFile = open(file_path, "r")
			groupName = ""
			groupContent = ""
			for line in GFile:
				# If this is name and content and end
				if re.search("\$[A-Z]+ .+ \$END",line.strip()):
					groupName = re.search("\$([A-Z]+)",line.strip()).group(1)
					groupContent = line.strip()
					self[groupName] = GMSFile.parse_group(groupContent)
				# If this is name and content
				elif re.search("\$([A-Z]+) ",line.strip()) and not re.search("\$END",line):
					groupName = re.search("\$([A-Z]+)",line).group(1).strip()
					groupContent = line.strip()+"\n"
				# If this is content and end 
				elif not re.match(" \$([A-Z]+)",line) and re.search("\$END",line):
					groupContent += line.rstrip()
					self[groupName] = GMSFile.parse_group(groupContent)
				# If this is content
				elif not re.search("\$([A-Z]+)",line):
					groupContent += line.strip()+"\n"
				# If this is name
				elif re.search("\$[A-Z]+",line.strip()) and not re.search("\$END",line.strip()):
					groupName = re.search("\$([A-Z]+)",line.strip()).group(1)
					groupContent = line.strip()+"\n"
				# If this is end
				elif re.match("\$END",line.strip()):
					groupContent += line.rstrip()
					self[groupName] = GMSFile.parse_group(groupContent)
			GFile.close()

	def __str__(self):
		return_string=""
		for group in self:
			return_string += " " +str(self[group]) + "\n"
		return return_string