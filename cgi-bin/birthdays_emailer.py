import datetime
import sys
import smtplib

def send_mail(cc,msg):
	fromaddr = 'zakazserov@gmail.com'
#	toaddrs = 'minja-f@ya.ru'
	username = 'zakazserov@gmail.com'
	password = 'razvitie'
	server = smtplib.SMTP('smtp.gmail.com:587')
	server.ehlo()
	server.starttls()
	server.login(username,password)
	for toaddrs in cc:
		if toaddrs == "zakazserov@gmail.com":
			continue
		msg2 = "\r\n".join([
		"From: zakazserov@gmail.com",
		"To: "+toaddrs,
		"Subject: Birthday reminder from Minja",
	#	"Cc: "+",".join(cc),
		"Cc: ",
		msg
		])
		print msg2
		server.sendmail(fromaddr, toaddrs, msg2)
	server.quit()


curr_birsdays=[]
all_mails=[]
with open("D:/Apache24/cgi-bin/birthdays.txt") as f:
	for line in f:
		line=line.strip().split("\t")
		if len(line) != 7:
			print "Warning, wrong line",line
			continue
#		try:
		else:
			month = int(line[4])
			day = int(line[5])
			year = datetime.date.today().year
			left = datetime.date(year,month,day)-datetime.date.today()
			if (left.days>=0) and (left.days<=2):
				curr_birsdays.append(line[1:])
			all_mails.append(line[-1])
#		except:
#			print "Something went wrong with the line",line
			
for b in curr_birsdays:
	print "Sending mail"
	message="Birthday is coming soon!\n"
	message += " ".join(b[:-1])
	message += "\n if you don't want to recieve these emails, please ask Minja (minja-f@ya.ru)"
	#send_mail(["minja.fishman@gmail.com","minja-f@ya.ru"],message)
	send_mail([m for m in all_mails if m != b[-1]],message)
	
with open("D:/Apache24/cgi-bin/birthdays_emailer.log","a") as fout:
	fout.write(str(datetime.datetime.now())+" Executed sucessfully\n")