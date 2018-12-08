#!C:\Python27\python.exe -u

from __future__ import print_function
import cgi
import cgitb; cgitb.enable()
import os
import random
random.seed()

class CDataStorage():
	pass

try: # Windows needs stdio set for binary mode.
	import msvcrt
	msvcrt.setmode (0, os.O_BINARY) # stdin  = 0
	msvcrt.setmode (1, os.O_BINARY) # stdout = 1
except ImportError:
	pass

def run_conversion(args):
	#import argparse
	#parser = argparse.ArgumentParser()
	#parser.add_argument("-s","--species", required=True) # name of species - Aalb, Aatr, Acol, Aste
	#parser.add_argument("-t","--track", required=True) # path to file with bed-track
	#parser.add_argument("-o","--out", required=True) # path to output directory
	#parser.add_argument("-r","--reverse", required=True) # if True, liftovered varya to old assembly. if False, liftoveres old to varya #assembly.
	#args = parser.parse_args()
	path_chain = args.path_chain #e.g. 'C:/Desktop/Arbeit/AllData/ANOPHELES/2chr.ex/liftmap/' # path to lifovered file - '.liftmap' 
	Chain = {}
	if args.reverse == 'False':
		args.reverse = False
		rev = 'varya', 'old'
	else:
		args.reverse = True
		rev = 'old','varya'
	print (args.reverse)
	f = open( path_chain+args.species+'.liftmap' ,'r')
	lines = f.readlines()
	f.close()
	if args.reverse == False:
		for i in range(len(lines)-1,-1,-1):
			parse = lines[i].split()
			if Chain.has_key(parse[0]) == True:
				Chain[parse[0]].append( ( int(parse[1]), int(parse[2]), parse[3], int(parse[4]), int(parse[5]) ) )
			else:
				Chain[parse[0]] = [ ( int(parse[1]), int(parse[2]), parse[3], int(parse[4]), int(parse[5]) ) ]
			del lines[i]
	else:
		for i in range(len(lines)-1,-1,-1):
			parse = lines[i].split()
			r1 = int(parse[4])
			r2 = int(parse[5])
			if r1 < r2:
				if Chain.has_key(parse[3]) == True:
					Chain[parse[3]].append( ( r1, r2, parse[0], int(parse[1]), int(parse[2]) ) )
				else:
					Chain[parse[3]] = [ ( r1, r2, parse[0], int(parse[1]), int(parse[2]) ) ]
			else:
				if Chain.has_key(parse[3]) == True:
					Chain[parse[3]].append( ( r2, r1, parse[0], int(parse[2]), int(parse[1]) ) )
				else:
					Chain[parse[3]] = [ ( r2, r1, parse[0], int(parse[2]), int(parse[1]) ) ]
			del lines[i]

	GNs = []
	f = open( args.track,'r')
	lines = f.readlines()
	f.close()
	for i in range(len(lines)-1,-1,-1):
		parse = lines[i].split()
		try: GNs.append( ( parse[0], int(parse[1]), int(parse[2]), parse[3] ) )
		except IndexError: GNs.append( ( parse[0], int(parse[1]), int(parse[2]) ) )
		del lines[i]
	c = [0,0,0,0]
	f = open( '%s/%s.%s.liftovered.full.bed' % (args.out,args.species,rev[0]),'w')
	f2 = open( '%s/%s.%s.liftovered.partial.bed' % (args.out,args.species,rev[0]),'w')
	f3 = open( '%s/%s.%s.non.bed' % (args.out,args.species,rev[1]),'w')
	for k in GNs:
		B = True
		remap = [-1,-1]
		try:
			for N in Chain[k[0]]:
				if k[1] >= N[0] and k[2] <= N[1]:
					if N[3] < N[4]: remap = N[3] + (k[1]-N[0]) , N[3] + (k[2]-N[0])
					else: remap = N[3] - (k[2]-N[0]) , N[3] - (k[1]-N[0])
					try: print >> f, '%s\t%i\t%i\t%s' % (N[2], remap[0], remap[1], k[3])
					except IndexError: print >> f, '%s\t%i\t%i' % (N[2], remap[0], remap[1])
					c[0] += 1
					c[1] += 1
					B = False
					break
				elif k[1] < N[0] and k[2] > N[0]: 
					if N[3] < N[4]: remap = N[3] + (k[1]-N[0]) , N[3] + (k[2]-N[0])
					else: remap = N[3] - (k[2]-N[0]) , N[3] - (k[1]-N[0])
					try: print >> f2, '%s\t%i\t%i\t%s' % (N[2], remap[0], remap[1], k[3])
					except IndexError: print >> f2, '%s\t%i\t%i' % (N[2], remap[0], remap[1])
					c[0] += 1
					c[2] += 1
					B = False
					break
				elif k[1] < N[1] and k[2] > N[1]: 
					if N[3] < N[4]: remap = N[3] + (k[1]-N[0]) , N[3] + (k[2]-N[0])
					else: remap = N[3] - (k[2]-N[0]) , N[3] - (k[1]-N[0])
					try: print >> f2, '%s\t%i\t%i\t%s' % (N[2], remap[0], remap[1], k[3])
					except IndexError: print >> f2, '%s\t%i\t%i' % (N[2], remap[0], remap[1])
					c[0] += 1
					c[2] += 1
					B = False
					break
				else: pass
		except KeyError:
			try: print >> f3, '%s\t%i\t%i\t%s' % ( k[0], k[1], k[2], k[3])
			except IndexError: print >> f3, '%s\t%i\t%i' % ( k[0], k[1], k[2])
			B = False
			c[0] += 1
			c[2] += 1
		if B == True: 
			try: print >> f3, '%s\t%i\t%i\t%s' % ( k[0], k[1], k[2], k[3])
			except IndexError: print >> f3, '%s\t%i\t%i' % ( k[0], k[1], k[2])
			c[0] += 1
			c[3] += 1
	f.close()
	f2.close()
	f3.close()
	del GNs
	del Chain
	print (c)
	return ('%s/%s.%s' % (args.out,args.species,rev[1]))

def print_html_template():
	print ("""Content-type: text/html
		<html><head><title>Anopheles Liftover</title></head><body>
		<form method="post" action="Anopheles_liftover.py" enctype="multipart/form-data">
		<p><b>Select species:</b><input name="Species"></input><br>
		<p><b>Enter regions in bed format:</b><br><textarea name="BedData" rows="20" cols="70"></textarea><br>
		<p><b>or upload file<input type="file" name="upload" /></b></p>
		<input type="submit" value="Submit!"></p>
	</form>
	""")

def print_footer():
	print ("</body></html>")

def run_conversion(input_file):
	pass

def print_results(result):
	for title,href in zip([".liftovered.full.bed",".liftovered.partial.bed",".non.bed"],
						  ["full","partial","non"]):
		print ("<br><a href="+result + href+">"+title+"</a>")

def recieve_data():
	args = CDataStorage()
	form = cgi.FieldStorage()
	message = form.getvalue("BedData", None)
	if 'upload' in form.keys():
		filedata = form['upload']
		print ("<br><i>File ",filedata.filename," recieved</i><br>")
	else:
		filedata = None

	if (message != None and message.strip() != "" and filedata == None):
		filedata = str(random.randint(1,1000000))+ ".bed"
		with open(filedata) as fin:
			fin.write(message)
	args.track = filedata
	args.species = form.getvalue("Species")
	args.reverse = False
	args.out = "liftover/"
	return args

print_html_template()
args = recieve_data()
if (args.track != None):
	results = run_conversion(args)
	print_results(results)
else:
	print ("<br><b>No data recieved</b><br>")
print_footer()
