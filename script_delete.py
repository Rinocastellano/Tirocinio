import json
import csv
import requests
import time
from crate import client
import os
import datetime

import docker
##DA UTILIZZARE SOLO ALL'INIZIO





url = "http://localhost:1026/v2/subscriptions"
headers = {'header': 'Content-Type: application/json'}
response = requests.request("GET", url, headers=headers, verify=False)

data=json.loads(response.text.encode('utf-8'))

for n in range(len(data)):
	datax=data[n]['id']
	print(datax)
	
	url=f"http://localhost:1026/v2/subscriptions/{datax}"
	url1=url
	headers= {'Content-Type' : 'application/json'}
	payload={}
	response=requests.request('DELETE', url1)
	print(response.text.encode('utf-8'))
with open("./Threshold_WaterStation.csv", newline="",encoding="ISO-8859-1") as filecsv1:
		#Ora prendiamo i valori dal Threshold csv
		#header1=nomi dei parametri col threshold
		#dati1= riga dei valori di soglia
		lettore1=csv.reader(filecsv1,delimiter=",")
		header1=next(lettore1)
		dati1=[row1 for row1 in lettore1]
		
		#per ogni header vedo se c'è almeno una sub sul limite, se non c'è creerò io stesso
		
		for n in range(len(header1)):
			print(header1[n])
			print(dati1[0][n])
			f=open("my_ip.txt","r")
			my_ip=f.read()
			f.close()
			

			url = "http://localhost:1026/v2/subscriptions"
			payload =f"{{\"description\":\"Notify me of Overcoming threshold {header1[n]} parameter in WaterStation:1\",\"subject\": {{\"entities\": [{{\"idPattern\": \"WaterStation:1\", \"type\": \"WaterStation\"}}],\"condition\": {{\"attrs\": [\"{header1[n]}\"],\"expression\": {{\"q\": \"{header1[n]} > {dati1[0][n]}\"}}}}}},\"notification\": {{\"http\": {{\"url\": \"{my_ip}\"}},\"attrs\":[\"{header1[n]}\",\"dateModified\"],\"metadata\":[\"dateModified\"]}},\"throttling\": 5}}"
			payload1=f"{{\"description\":\"change {header1[n]} parameter in WaterStation:1\",\"subject\": {{\"entities\": [{{\"idPattern\": \"WaterStation:1\", \"type\": \"WaterStation\"}}],\"condition\": {{\"attrs\": [\"{header1[n]}\"]}}}},\"notification\": {{\"http\": {{\"url\": \"http://quantumleap:8668/v2/notify\"}},\"attrs\":[\"{header1[n]}\",\"dateModified\"],\"metadata\":[\"dateModified\"]}},\"throttling\": 5}}"
			print(payload)
			print(payload1)
			y=json.loads(payload)
			payload=json.dumps(y)
			x=json.loads(payload1)
			payload1=json.dumps(x)
			headers= {'Content-Type' : 'application/json'}
			response = requests.request("POST", url, headers=headers, data = payload)
			response1 = requests.request("POST", url, headers=headers, data = payload1)
			
			print(response.text.encode('utf-8'))
			print(response1.text.encode('utf-8'))
		
		#Prendiamo già tutto il data inerente alle subs
	#data= tutte le sub che ho

