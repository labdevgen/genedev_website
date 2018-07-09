import datetime
import sys
import smtplib

def send_mail(cc,msg):
	fromaddr = 'zakazserov@gmail.com'
	toaddrs = 'minja-f@ya.ru'
	username = 'zakazserov@gmail.com'
	password = 'razvitie'
	server = smtplib.SMTP('smtp.gmail.com:587')
	server.ehlo()
	server.starttls()
	server.login(username,password)
	msg = "\r\n".join([
	  "From: zakazserov@gmail.com",
	  "To: "+toaddrs,
	  "Subject: Brthday reminder from Minja",
	  "Cc: "+",".join(cc),
	  msg
	  ])

	server.sendmail(fromaddr, toaddrs, msg)
	server.quit()


curr_birsdays=[]
all_mails=[]
with open() as f:
	for line in f:
		line=line.strip().split("\t")
		if len(line) != 7:
			print "Warning, wrong line",line
			continue
		try:
			month = int(line[4])
			day = int(line[5])
			year = datetime.today().year
			left = datetime.date(year,month,day)-datetime.today()
			if (left.months==0) and (left.days>=0) and (left.days<0):
				curr_birsdays.append(line[1:])
			all_mails.append(line[-1])
			
for b in curr_birsdays:
#	send_mail([m for m in all_mails if m != b[-1]]," ".join(b[:-1]))
	send_mail(["minja.fishman@gmail.com","natasaprygina@gmail.com"]," ".join(b[:-1]))