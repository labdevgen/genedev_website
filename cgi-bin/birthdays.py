#!C:\Python27\python.exe -u

import datetime
import cgi
import cgitb; cgitb.enable()
import os

try: # Windows needs stdio set for binary mode.
    import msvcrt
    msvcrt.setmode (0, os.O_BINARY) # stdin  = 0
    msvcrt.setmode (1, os.O_BINARY) # stdout = 1
except ImportError:
    pass

def print_header():
	print """
		<html>

		<head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"><title>Lab birthdays</title></head>
	
		<body>"""

def print_footer():
	print "</body></html>"
	
		
def print_add_form():
	print """<form method="post" action="birthdays.py" enctype="multipart/form-data">
	<b>Add following item:</b>
	<table>
	<tr>
	<td>First Name:</td><td><input type='text' name='FirstName' value='FirstName' /></td>
	</tr>
	<tr>
	<td>Last Name: </td><td><input type='text' name='LastName' value='LastName' /></td><br>
	</tr>
	<tr>
	<td>Year: </td><td><input type='text' name='Year' value='1900' onkeypress='return event.charCode >= 48 && event.charCode <= 57' /></td><br>
	</tr>
	<tr>
	<td>Month: </td><td><input type='text' name='Month' value='01' onkeypress='return event.charCode >= 48 && event.charCode <= 57' /></td><br>
	</tr>
	<tr>
	<td>Day: </td><td><input type='text' name='Day' value='01' onkeypress='return event.charCode >= 48 && event.charCode <= 57' /></td><br>
	</tr>
	<tr>
	<td>Email: </td><td><input type='text' name='Mail' value='mail@mail.mail'/></td><br>
	</tr>
	</table>
	</p>
	<input type="submit" value="Add!"></p>
	</form>
	<br><hr>"""

def print_del_form(res):
	print """<p><b>Delete following item:</b></p>
	<form method="post" action="birthdays.py" enctype="multipart/form-data">"""
	for person in res.keys():
		print "<input type='radio' name='person' value='"+str(person)+"'>",\
			res[person][0].decode("cp1251").encode("UTF-8"),\
			" ",res[person][1].decode("cp1251").encode("UTF-8"),\
			" ",".".join(res[person][2:5])," ",res[person][5],"<br>"
	print """
	<input type="submit" value="Delete!"></p>
	</form>
	<br><hr>"""

	
def parse_birthdays_file(fname):
	res={}
	with open(fname) as f:
		for line in f:
			if len(line.strip()) == 0:
				continue
			line=line.strip().split("\t")
			if len(line) != 7:
				print "Warning! wrong line ",line
				continue
			assert not (line[0] in res.keys())
			res[line[0]]=line[1:]
	return res

def del_person(fname,form):
	if "person" in form.keys():
		person = form["person"].value
		birthdays = parse_birthdays_file(fname)
		with open(fname,"w") as f:
			for i in birthdays.keys():
				if i != person:
					f.write(i+"\t"+"\t".join(birthdays[i])+"\n")
	else:
		print "Please choose a person<br>"
	

def add_person(fname,form):
	def check(form):
		if "FirstName" in form.keys() and \
			"LastName" in form.keys() and \
			"Year" in form.keys() and \
			"Month" in form.keys() and \
			"Day" in form.keys() and \
			"Mail" in form.keys(): 
				pass
		else:
			return False
		
		if not "@" in form["Mail"].value or not "." in form["Mail"].value:
			return False
		
		try:
			Year = int(form["Year"].value)
			Month = int(form["Month"].value)
			Day = int(form["Day"].value)
			data = datetime.date(Year, Month, Day)
			
		except:
			return False
		return 3650<=(datetime.datetime.now().date()-data).days<=30000
	
	if not check(form):
		print "Invalid input!"
	else:
		with open(fname,"r") as f:
			lines = [l.strip() for l in f.readlines() if l.strip() != ""]
		if len(lines) == 0:
			lastind = -1
		else:
			lastind = int(lines[-1].split("\t")[0])

		with open(fname,"a") as f:
			f.write(str(lastind+1)+"\t"+"\t".join([form["FirstName"].value,
													form["LastName"].value,
													form["Year"].value,
													form["Month"].value,
													form["Day"].value,
													form["Mail"].value]
													) + "\n"
					)

print_header()
fname = "birthdays.txt"
birthdays = parse_birthdays_file(fname)
form = cgi.FieldStorage()
if len(form.keys()) != 0:
	if "person" in form.keys():
		del_person(fname,form)
		birthdays = parse_birthdays_file(fname)
	if "FirstName" in form.keys():
		add_person(fname,form)
		birthdays = parse_birthdays_file(fname)


print_add_form()
print_del_form(birthdays)
print_footer()