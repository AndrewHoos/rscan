import re
import sys
from collections import OrderedDict

class GMSGroup(OrderedDict):
	def __init__(self,group_name):
		self.name = group_name
		super(GMSGroup,self).__init__()
		

	def __str__(self):
		return_string="$" + self.name
		for variable in self:
			return_string += " "+variable+"="+self[variable]
		return_string += " $END"
		return return_string
		
class GMSFile(OrderedDict):
	
	def parse_group(groupContent):
		split =re.split("\s+",groupContent)
		groupName = re.search("\$([A-Z]+)",split[0]).group(1)
		
		if groupName == "DATA" or groupName == "VEC" or groupName =="ZMAT":
			return groupContent
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
			return groupContent

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