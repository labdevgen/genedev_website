#!C:\Python27\python.exe -u


from Bio.Seq import Seq
from Bio.SeqFeature import SeqFeature
from Bio.SeqFeature import FeatureLocation
from Bio.SeqFeature import ExactPosition
from Bio import SeqIO
import cgi
import cgitb; cgitb.enable()
import os

try: # Windows needs stdio set for binary mode.
    import msvcrt
    msvcrt.setmode (0, os.O_BINARY) # stdin  = 0
    msvcrt.setmode (1, os.O_BINARY) # stdout = 1
except ImportError:
    pass


def print_def_form():
	print """

	<form method="post" action="PrimersAligner.py" enctype="multipart/form-data">
		<p><b>Enter DNA sequence:</b><br><textarea name="DNAseq" rows="20" cols="70"></textarea><br>
		<p><b>Annotate file: <input type="file" name="upload" /></b></p>
		<input type="submit" value="Submit!"></p>
	</form>
	<b><a href="http://fishminja/primertool/current.primers.txt">Download primers database</a></b>"""


print "Content-type: text/html"
print
print """
	<html>

	<head><title>Pick primers</title></head>
	
	<body>"""
	

form = cgi.FieldStorage()
message = form.getvalue("DNAseq", None)
if 'upload' in form.keys():
	filedata = form['upload']
	print "File ",filedata.filename," recieved<br>"
else:
	filedata = None
	print "filedata set to None"

#message = "aaaaaaaaaaaaaaaaaaaaaa"
DNA_seq  = None
record = None
if (message != None) and (message != ""):
	DNA_seq = message.strip()
else:
	DNA_seq = ""
	if (filedata != None) and (filedata.filename != None) and (filedata.filename != ""):
		count = 0
		for record in SeqIO.parse(filedata.file,"genbank"):
			count += 1
			DNA_seq+=record.seq.lower()
		if count >1:
			print "<b>---Error! > 1 record in genbank file----</b>"

if (DNA_seq != None) and (DNA_seq != ""):
	primerslib = "../htdocs/primertool/current.primers.txt"
	f=open(primerslib,"r")
	primersdict = {}

	#reading primers from database into dict
#	print "Parsing primers file"
	for line in f:
		line = line.strip().split("\t")
#		if (line[0]+"_"+line[1]) in primersdict.keys():
#			print "Primer",line[0]+"_"+line[1],"was found twice<br>"
		primersdict[line[0]+"_"+line[1]] = line[1]
	print "Identified ",len(primersdict)," primers in database<br>"
	f.close()
	
	found_primer_count = 0
	print "<table border=1><b><tr align='center'><td>Strand</td><td>Name</td><td>Sequence</td></tr><b>"
	
	for primer_name in primersdict.keys():
		primer = primersdict[primer_name]
		primer_name="".join(primer_name.split("_")[:-1])
		primer = primer[max(0,len(primer)-20):len(primer)]
		primer_reversed = str(Seq(primer).reverse_complement()).lower()
		position = DNA_seq.lower().find(primer.lower())
		qualifiers_dict={}
		qualifiers_dict['label']=primer_name
		qualifiers_dict['ApEinfo_revcolor']='yellow'
		qualifiers_dict['ApEinfo_fwdcolor']='pink'
		

		
		if  position != -1:
			print "<tr><td>+</td><td>",primer_name,"</td><td>",primer,"</td></tr>"
			found_primer_count += 1
			if record != None:
				loc = FeatureLocation(ExactPosition(position),ExactPosition(position+20))
				feature = SeqFeature(location=loc,type="primer",strand=1,id=primer_name,qualifiers=qualifiers_dict)
#				qualifiers_dict['ApEinfo_graphicformat']="arrow_data {{0 1 2 0 0 -1} {} 0}\nwidth 5 offset 0"
				record.features.append(feature)
		position = DNA_seq.lower().find(primer_reversed.lower())				
		if DNA_seq.lower().find(primer_reversed) != -1:
			print "<tr><td>-</td><td>",primer_name,"</td><td>",primer,"</td></tr>"
			found_primer_count += 1
			if record != None:
				loc = FeatureLocation(ExactPosition(position),ExactPosition(position+20))
#				qualifiers_dict['ApEinfo_graphicformat']="arrow_data {{0 1 2 0 0 -1} {} 1}\nwidth 5 offset 0"
				feature = SeqFeature(location=loc,type="primer",strand=-1,id=primer_name,qualifiers=qualifiers_dict)
				record.features.append(feature)
	print "<tr><b>Found ",found_primer_count," primers<br></b></tr>"
	print "</table>"
	if record != None:
		print "<a href='../"+filedata.filename+"_annotated.gbk'>Download annotated sequence in GenBank format</a>"
		f=open("../htdocs/"+filedata.filename+"_annotated.gbk","w")
		SeqIO.write(record, f, "genbank")
		f.close()
		
print_def_form()
print """</body>
	</html>"""
