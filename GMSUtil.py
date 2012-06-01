import re

class GMSFileReader:
	CART_OUT_REGEX = "(.*) +(\d+\.\d+) +(-?\d+\.\d+) +(-?\d+\.\d+) +(-?\d+\.\d+)"
	INTERNAL_COORD_REGEX="(\d+) +([A-Z]+) +(\d+) +(\d+)? +(\d+)? +(\d+)? +(-?\d+\.\d+) +(-?\d+\.\d+)"
	SCR_PATH="/Users/mac/Desktop/gamess/scr/"
	
	
	def read_data_group(file_path, mode="ZMAT"):
		if mode not in ["ZMAT","UNIQUE"]:
			# the mode is unsupported
			pass
		
		gms_file = open(file_path,"r")
		
		if re.search("\.inp",file_path):
			# the file type is input
			pass
		elif re.search("\.log",file_path):
			return_string ="$DATA\n"
			
			found_run_title = False
			
			geometry_found=False
			returnLine=""
			
			dashed_line_count=0
			coordinateLineCount=0
			
			for line in gms_file:				
				# Find the title
				if found_run_title and not re.search("-+",line.strip()):
					return_string += line.strip() + "\n"
					found_run_title = False
				if re.search("RUN TITLE",line.strip()):
					found_run_title = True
				# end find title
				
				# Find point group
				if re.search("THE POINT GROUP OF THE MOLECULE IS (.+)",line.strip()):
					return_string += re.search("THE POINT GROUP OF THE MOLECULE IS (.+)",line.strip()).group(1)+"\n"
				# end point group
					
				# Find coordinates
				
				if mode == "UNIQUE":
					pass
				elif mode == "ZMAT":	
						if re.search("EQUILIBRIUM GEOMETRY LOCATED",line):
							geometry_found=True
							data_line=list()
						if geometry_found:
							
							if dashed_line_count == 1:
								
								regex_groups = re.search(GMSFileReader.CART_OUT_REGEX,line.strip())
								if regex_groups:
									regex_groups = regex_groups.groups()
									atom = regex_groups[0].strip()
									data_line.append(atom)
							elif dashed_line_count == 4:
								regex_groups = re.search(GMSFileReader.INTERNAL_COORD_REGEX,line.strip())
								if regex_groups:
									regex_groups = list(regex_groups.groups())
									print(regex_groups)
									atom_number = int(regex_groups[2])-1
									if regex_groups[5]:
										data_line[atom_number]+="    "+regex_groups[5]
									elif regex_groups[4]:
										data_line[atom_number]+="    "+regex_groups[4]
									elif regex_groups[3]:
										data_line[atom_number]+="    "+regex_groups[3]
									else:
										pass
									data_line[atom_number]+="    "+regex_groups[-1]
								else:
									break	
							elif dashed_line_count == 4:
								dashed_line_count = 0
								break
							if not re.search("[a-zA-Z]",line.strip()) and re.search("--+",line.strip()):
								dashed_line_count += 1
						#end if geometry_found
			if data_line:
				for i in data_line:
					return_string += i +"\n"
				return_string += " $END"
		elif re.search("\.dat",file_path):
			pass
		else:
			pass
			# the file type is unrecognized
		
		gms_file.close()
		return return_string
		
	def read_vec_group(file_path):
		dat_file = open(GMSFileReader.SCR_PATH+file_path, "r")
		
		VECList=[]
		VECNumber=0
		lineNumber=0
		for line in dat_file:
			
			if re.search("\$VEC",line):
				VECList.append("")
				VECList[VECNumber]+=line.lstrip()
				lineNumber+=1
				continue
						
			if re.search("END",line) and lineNumber:
				VECList[VECNumber]+=line
				VECNumber+=1
				lineNumber=0
				
			if lineNumber:
				VECList[VECNumber]+=line
				lineNumber+=1
				
		dat_file.close()
		print(len(VECList))
		return VECList