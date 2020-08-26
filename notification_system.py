
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64
import os
import requests
import json
import smtplib

#Scriviamo lo script che mi logga nel mio account
def login(account, password, smtp_server, smtp_port, to, subject, body):
	
	#login
	server = smtplib.SMTP(smtp_server,smtp_port)
	server.starttls()
	server.login(account,password)
	
	#sending email
	message=MIMEMultipart('alternative')
	message['From']=account
	message['To']=to
	message['Subject']=subject
	message.attach(MIMEText(body, 'html'))
	text=message.as_string()
	server.sendmail(account, to, text)
	
	#log out
	server.quit()
	
#FUNZIONE CHE INSERISCE LA MAIL DI NOSTRO INTERESSE NEL JSON
def insert_admin(name_mail):
	url = "http://localhost:1026/v2/entities/WaterStation:1/attrs"
	payload = f"{{\"Mail\":{{\"type\":\"text\",\"value\":\"pinopigo@gmail.com\"}}}}"
	y=json.loads(payload)
	payload=json.dumps(y)
	headers = {'Content-Type': 'application/json'}
	response = requests.request("PATCH", url, headers=headers, data = payload)

'''#FUNZIONE CHE SERVE PER GENERARE LA MAIL, GLI ARGOMENTI SONO ABBASTANZA LOGICI
#Ritorna un oggetto contenente un base64url encoded email object
def create_message(sender, to, subject, message_text):
	message=MIMEText(message_text)
	message['to']=to
	message['from']=sender
	message['subject']=subject
	return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}
	
	
#FUNZIONE CHE INVIA IL MESSAGGIO GERENATO
#Service: servizio di API utilizzato
#user_id:la mail a cui voglio inviare il messaggio
#ritorna il messaggio inviato
def send_message(service, user_id, message):
	try:
		message=(service.users().messages().send(userId=user_id, body=message).execute())
		print('Message Id: {}'.format(message['id']))
		return message
	except:
		print('An error occured')
		

	
#funzione inviante mail solo agli admin 
def notification(sender, subject, notification):
	#ottengo prima di tutto la mail a cui devo scrivere
	url = "http://localhost:1026/v2/entities/WaterStation:1?attrs=Mail"
	headers = {'header': 'Content-Type: application/json'}
	response = requests.request("GET", url, headers=headers, verify=False)
	
	data=json.loads(response.text.encode('utf-8'))
	
	SCOPES = 'https://mail.google.com/'
	message = create_message(sender, data['Mail']['value'], subject, notification)
	creds = None
	if os.path.exists('token.pickle'):
		with open('token.pickle', 'rb') as token:
			creds = pickle.load(token)
		#We use login if no valid credentials
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow =   InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
			creds = flow.run_local_server(port=0)
			# Save the credentials for the next run
		with open('token.pickle', 'wb') as token:
			pickle.dump(creds, token)
			service = build('gmail', 'v1', credentials=creds)
	send_message(service, sender, message)
    
    
notification('rino','ciao','come stai?')'''
	
