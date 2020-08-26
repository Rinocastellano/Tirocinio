
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64
import os
import requests
import json
import smtplib
import csv

'''server = smtplib.SMTP('smtp.gmail.com',587)
server.starttls()
server.login('tirociniocastellanofiware@gmail.com','pinocchio1')

#sending email
message=MIMEMultipart('alternative')
message['From']='tirociniocastellanofiware@gmail.com'
message['To']='chiara.organari@gmail.com'
message['Subject']='Prova'
message.attach(MIMEText('<h1>SONO IL MAGNIFICO RETTORE DELL\'UNIVR DI FERMO E STO PER FARLE UNA GRANDE COMUNICAZIONE</h1><body>No scherzo sono pino e sto facendo una prova se funzione il codice automatico che scrive le mail da sole, ciao bebi </body>', 'html'))
text=message.as_string()
server.sendmail('tirociniocastellanofiware@gmail.com', 'chiara.organari@gmail.com', text)

#log out
server.quit()
array_role=['0']
i=0
field=["account","password","role"]
with open("./role settings.csv", 'r') as csv_file:
	reader=csv.DictReader(csv_file)
	for row in reader:
		array_role[i]=row
		print(array_role[i])
		i+=1
	for x in range(len(array_role)):
		print(array_role[x]['account'])
with open("./role settings.csv","w") as csv_file2:
	account="ok"
	password="si"
	writer=csv.DictWriter(csv_file2, fieldnames=field)
	writer.writeheader()
	writer.writerow({'account':account, 'password':password,"role":"admin"})
	for z in range(len(array_role)):
		writer.writerow({'account':array_role[z]['account'],'password':array_role[z]['password'],'role':array_role[z]['role']})'''
json_file=open("./role settings.json", 'r')
elenco=json.load(json_file)
json_file.close()
to='rinoinini'
json_file2=open("./role settings.json","w")
new_dict={}
new_dict['users']=[]
for user in elenco['users']:
	new_dict['users'].append({'account':user['account'], 'password':user['password'], 'role':user['role']})	
new_dict['users'].append({'account':to, 'password':'-',"role":"slave"})
json.dump(new_dict, json_file2)
json_file2.close()		
