import redis 
from string import Template
from flask import Flask, request, jsonify, render_template
import time
import json
import csv
import requests
from crate import client
import datetime
import json 
import os
import notification_system

#Tale funzione ha come scopo quello di controllare se l'utente ha modificato la soglia dei parametri e se è stato cambiato l'indirizzo IP del web server
#ovviamente tale controllo è effettuato soltanto sulle subscription che comprendono l'expression di superamento soglia
def control_threshold(data,header):
	cont_val_sub=[]
	cont_head_sub=[]
	cont_out_sub=[]
	
	#Ora prendiamo i valori dal Threshold csv
	#header1=nomi dei parametri col threshold
	#dati1= riga dei valori di soglia
	header1,threshold,limit,counter,counter_exit=reading_threshold_file()
	
	#per ogni header vedo se c'è almeno una sub sul limite, se non c'è creerò io stesso
	
	for p in range(len(header1)):
	
	
		
		cont=0
		
		for n in range(len(data)):
		##lettura valore
   		##header= elenco dei parametri in subscription con le expression
    		
		##La prima condizione è che devo avere una espressione di condizione
		##Se non c'è, non viene considerato, perchè è la classica sub utile a Grafana
			
				
			
				
				
			if (header1[p]==header[n] and 'expression' in data[n]['subject']['condition']):
				cont+=1
				
				#leggo il file my_ip.txt per avere il valore di ip corretto da testare nella funzione
				f=open("my_ip.txt","r")
				my_ip=f.read()
				
				
				if (threshold[p] not in data[n]['subject']['condition']['expression']['q'] or data[n]['notification']['http']['url']!=my_ip):
					
					#modify new sub
					url = f"http://tirociniofiware_orion_1:1026/v2/subscriptions/{data[n]['id']}"
					payload = f"{{\"description\":\"Notify me of Overcoming threshold {header[n]} parameter in WaterStation:1\",\"subject\": {{\"entities\": [{{\"idPattern\": \"WaterStation:1\", \"type\": \"WaterStation\"}}],\"condition\": {{\"attrs\": [\"{header[n]}\"],\"expression\": {{\"q\": \"{header[n]} > {threshold[p]}\"}}}}}},\"notification\": {{\"http\": {{\"url\": \"{my_ip}\"}},\"attrs\":[\"{header[n]}\",\"dateModified\"],\"metadata\":[\"dateModified\"]}},\"throttling\": 5}}"
					y=json.loads(payload)
					payload=json.dumps(y)
					headers = {'Content-Type' :'application/json'}
					response = requests.request("PATCH", url, headers=headers, data = payload)
	
		##condizione, se non ho mai confermato condizioni precedenti(presenza 
		##di sub con expression) -> la creo io coi val di threshold, finito 
		##il for
		if cont==0:
			cont_head_sub.append(header1[p])
			cont_val_sub.append(threshold[p])
	return cont_head_sub,cont_val_sub
				
				
				
		
		
##########################################################################################
#Questa funzione mi permette di ottenere le subscription di mio interesse, ovvero quelle con le expression
#la funzione control_threshold  ha uno scopo di manipolazione del dato quindi ho preferito
#svilupparlo alternativamente senza l'utilizzo di questa funzione
def get_sub(timesSent,header):
	url = "http://tirociniofiware_orion_1:1026/v2/subscriptions"
	#Prendiamo già tutto il data inerente alle subs
	#data= tutte le sub che ho

	
	headers = {'header': 'Content-Type: application/json'}
	response = requests.request("GET", url, headers=headers, verify=False)
	
	data=json.loads(response.text.encode('utf-8'))
	array_del=[]
	
	#con il seguente for elimino dal mio personale jsonArray di data sub le sub che non mi interessano
	for n in range(len(data)):
		if 'expression' in data[n]['subject']['condition']:
			
		
			header.append(data[n]['subject']['condition']['attrs'][0])
			if 'timesSent' in data[n]['notification']:
				timesSent.append(data[n]['notification']['timesSent'])
			else:
				timesSent.append(0)
		else:
			array_del.append(n)
	for p in range(len(array_del) -1,-1,-1):
			
		del data[array_del[p]]
			
	
	return data
	
#########################################################################################
#Funzione attivata solo in caso di POST request nel mio web_server
def case_post(timesSent,timesSent1,data):
	alert_list=[]
	
	
	if len(timesSent)==len(timesSent1):
		#apertura file Threshold_waterStation
		header1,threshold,limit,counter,counter_exit=reading_threshold_file()
		for n in range(len(data)):

			for name_param in header1:
				#Se il nome del parametro all'interno del file di threshold coincide con l'attributo della sub avviene l'analisi del threshold
				if name_param==data[n]['subject']['condition']['attrs'][0]:
					
					#dal db di crate ottengo gli utlimi n parametri, definiti sempre nel file di threshold
					parametri=get_crate_param(name_param,header1,counter)
					
					#otteniamo il tempo più recente da cui poi far partire eventuale notifica di alert
					dateModified=datetime.datetime.fromtimestamp(parametri[0][0]/1000)
					dateModified=str(dateModified).replace(' ','T')
					
					
					
					#per prevenire eliminiamo il wait di uscita dall'alert per poi reinserirlo se il trend viene confermato
					url=f"http://tirociniofiware_orion_1:1026/v2/entities/WaterStation:1/attrs/Wait_{name_param}_Exit_Alert"
					response = requests.request("DELETE", url)
				
					#HP che ogni minuto ricevo sempre un nuovo paramentro, se no avrei valori ipoteticamente inutili  poichè distanti
					cont=0
					
					#controllo degli ultimi parametri se confermano il trend negativo. 
					for x in parametri:
						
						if int(x[1]) > int(threshold[header1.index(name_param)]):
							cont+=1
					
					#prima di tutto analisi dell'ultimo valore se superata la soglia. SE tale ipotesi non viene confermata -> wait exit alert
					if int(parametri[0][1]) > int(threshold[header1.index(name_param)]):
						
						#controllo sul trend parametri. Tale controllo è utile ai fini del contenuto dell'alert
						if cont > int(limit[header1.index(name_param)]):
							alert_list.append(f"Anomaly in the trend param of {name_param}, exceeding threshold confirmed")
						
						else:
							alert_list.append(f"Anomaly value of {name_param}, not anomaly trend. Only {cont} exceeding.")

						#Pubblichiamo un alert
						
						url = "http://tirociniofiware_orion_1:1026/v2/op/update"
						payload = f"{{\"actionType\":\"APPEND\",\"entities\":[{{\"id\": \"WaterStation:1\", \"type\":\"WaterStation\",\"Alert{name_param}\":{{\"type\":\"Text\",\"value\":\"{alert_list[len(alert_list)-1]}\",\"metadata\":{{\"dateModified\":{{\"type\":\"DateTime\",\"value\":\"{dateModified}\"}}}}}}}}]}}"
						y=json.loads(payload)
						payload=json.dumps(y)
						headers = {'Content-Type': 'application/json'}
						response = requests.request("POST", url, headers=headers, data = payload)
						print(response.text.encode('utf-8'))
						 
						#inviamo anche una mail al supervisore dei parametri
						
					
					#se l'ipotesi precedente non è stata confermata -> controllo della condizione di uscita dall'alert (wait exit alert)
					else:
					
						#delete dell'alert perchè sicuramente se siamo entrati in questa condizione vuol dire che non siamo in condizione di alert
						url=f"http://tirociniofiware_orion_1:1026/v2/entities/WaterStation:1/attrs/Alert{data[n]['subject']['condition']['attrs'][0]}"
						response = requests.request("DELETE", url)
						cont_right=0
						
						#lettura degli ultimi n valori. Se il limite di threshold viene superato n volte, definito sempre dal file di threshold, allora verrà pubblicato
						#un wait exit alert, altrimenti non si è più in una situazione di pericolo
						for x in parametri:
							if int(x[1])<int(threshold[header1.index(name_param)]):
								cont_right+=1
								if cont_right==int(counter_exit[header1.index(name_param)]):
									break
							elif int(x[1])>int(counter_exit[header1.index(name_param)]):
								cont_right=-1
							
								alert_list.append(f"Waiting for the {name_param} to stabilize.")
								url = "http://tirociniofiware_orion_1:1026/v2/op/update"
								payload = f"{{\"actionType\":\"APPEND\",\"entities\":[{{\"id\": \"WaterStation:1\", \"type\":\"WaterStation\",\"Wait_{name_param}_Exit_Alert\":{{\"type\":\"Text\",\"value\":\"{alert_list[len(alert_list)-1]}\",\"metadata\":{{\"dateModified\":{{\"type\":\"DateTime\",\"value\":\"{dateModified}\"}}}}}}}}]}}"

								y=json.loads(payload)
								payload=json.dumps(y)
								headers = {'Content-Type': 'application/json'}
								response = requests.request("POST", url, headers=headers, data = payload)
								
								break
							
								
						
							
							
							
							
		
		for n in range(len(timesSent)):
			timesSent[n]=timesSent1[n]		
		
		#ritorno l'elenco di alert/wait che ho collezionato durante l'analisi
		return alert_list
	else:
		return("not ok")
########################################################################################

def create_wait_alert(header):
	wait_list=[]
	header1,threshold,limit,counter,counter_exit=reading_threshold_file()
	for name_param in header1:
		parametri=get_crate_param(name_param,header1,counter)
		dateModified=datetime.datetime.fromtimestamp(parametri[0][0]/1000)
		dateModified=str(dateModified).replace(' ','T')
	#Non è detto che l'inserimento di un valore sul sub di change non sia anche sul sub di threshold
		

		
		cont_right=0
		if int(parametri[0][1]) < int(threshold[header1.index(name_param)]):
			url=f"http://tirociniofiware_orion_1:1026/v2/entities/WaterStation:1/attrs/Alert{name_param}"
			response = requests.request("DELETE", url)
			for x in parametri:
				if int(x[1])<int(threshold[header1.index(name_param)]):
					cont_right+=1
					if cont_right==int(counter_exit[header.index(name_param)]):
						break
				elif int(x[1])>int(counter_exit[header.index(name_param)]):
					cont_right=-1
				
					wait_list.append(f"Waiting for the {name_param} to stabilize.")
					url = "http://tirociniofiware_orion_1:1026/v2/op/update"
					payload = f"{{\"actionType\":\"APPEND\",\"entities\":[{{\"id\": \"WaterStation:1\", \"type\":\"WaterStation\",\"Wait_{name_param}_Exit_Alert\":{{\"type\":\"Text\",\"value\":\"{wait_list[len(wait_list)-1]}\",\"metadata\":{{\"dateModified\":{{\"type\":\"DateTime\",\"value\":\"{dateModified}\"}}}}}}}}]}}"

					y=json.loads(payload)
					payload=json.dumps(y)
					headers = {'Content-Type': 'application/json'}
					response = requests.request("POST", url, headers=headers, data = payload)
					
					break
########################################################################################
#funzione per ottenere tutti i messaggi di alert/wait da comunicare successivamente al web server
def obtain_alert_wait():
	current_alert=[]
	
	url = "http://tirociniofiware_orion_1:1026/v2/entities/WaterStation:1"
	headers = {'header': 'Content-Type: application/json'}
	response = requests.request("GET", url, headers=headers, verify=False)
	data=json.loads(response.text.encode('utf-8'))
	
	#prendo dal data tutte le entità che iniziano con Alert
	array={k: v for k, v in data.items() if k.startswith('Alert')}
	for alert_id, alert_info in array.items():
		
		string=alert_info['value']
		date=alert_info['metadata']['dateModified']['value']
	
		current_alert.append(f"Alert: {alert_id}, What:  {string}. Last time notify: {date}. \n")
		
	#stesso procedimento svolto con le wait
	array={k: v for k, v in data.items() if k.startswith('Wait')}
	for wait_id, wait_info in array.items():
		
		string=wait_info['value']
		date=wait_info['metadata']['dateModified']['value']
		current_alert.append(f"Wait: {wait_id}. What: {string}. Last time notify: {date}  ")
	
	#nell'ipotesi in cui non ci siano alert e wait -> messaggio di ok
	if not current_alert:
		current_alert.append("NO PROBLEM")
	current_alert=[{"Notice": a} for a in zip(current_alert)]
	return current_alert
	


########################################################################################
#Funzione che mi calcola le varie variabili/condizioni per l'output dei parametri quali:
#media valori, valore max acquisito, condizione di allarme
def get_stat_param(name_param):
	#lettura dati di nostro interesse da "threshold_waterstation.csv"
	header1,threshold,limit,counter,counter_exit=reading_threshold_file()
	#dal db di crate ottengo gli utlimi n parametri, definiti sempre nel file di threshold
	parametri=get_crate_param(name_param,header1,counter)
	y=0
	#algoritmo di calcol val max e val avg
	for x in parametri:
		if int(x[1])>y:
			max_val=int(x[1])
		x[1]=int(x[1])+y
		y=int(x[1])
	avg_val=y/int(counter[header1.index(name_param)])
	url = f"http://tirociniofiware_orion_1:1026/v2/entities/WaterStation:1?attrs=Alert{name_param}"
	headers = {'header': 'Content-Type: application/json'}
	response = requests.request("GET", url, headers=headers)
	if "Alert" not in str(response.text.encode("utf-8")):
		url = f"http://tirociniofiware_orion_1:1026/v2/entities/WaterStation:1?attrs=Wait_{name_param}_Exit_Alert"
		headers = {'header': 'Content-Type: application/json'}
		response = requests.request("GET", url, headers=headers)
		if "Wait" not in str(response.text.encode("utf-8")):
			status="<p style=\"color:green;\">Sotto controllo</p>"
		else:
			status="<p style=\"color:yellow;\">Attesa uscita</p>"
	else:
		status="<p style=\"color:red;\">Alarm!</p>"
	return max_val,avg_val,status
		
		
		
	
####################################################################################################
#funzione utile ad acquisire i valori fondamentali dal db crate onde evitare ripetitività nel codice
def get_crate_param(name_param,header1,counter):
	connection=client.connect("http://tirociniofiware_crate_1:4200/#!/tables/doc/etwaterstation")
	cursor = connection.cursor()
	cursor.execute(f"SELECT \"time_index\",\"{name_param}\" FROM \"doc\".\"etwaterstation\" where \"{name_param}\">0 order by \"time_index\" desc limit {counter[header1.index(name_param)]};")
	parametri= cursor.fetchall()
	return parametri



####################################################################################################
#funzione che legga i dati di threshold dal file
def reading_threshold_file():
	with open("./Threshold_WaterStation.csv", newline="",encoding="ISO-8859-1") as filecsv1:
		lettore1=csv.reader(filecsv1,delimiter=",")
		header1=next(lettore1)
		dati1=[row1 for row1 in lettore1]
		threshold=dati1[0]
		limit=dati1[1]
		counter=dati1[2]
		counter_exit=dati1[3]
	return header1,threshold,limit,counter,counter_exit
	
	
	
	
####################################################################################################
#funzioni che leggono/scrivono su file json. Utili per la gestione delle mail di notifica
def reading_file():
	with open("./role settings.json", 'r') as json_file:
		elenco=json.load(json_file)
	return elenco
	
def writing_file(user,elenco):
	
	new_dict={}
	new_dict['users']=[]
	for old_user in elenco['users']:
		new_dict['users'].append({'account':old_user['account'], 'password':old_user['password'], 'role':old_user['role']})
	
	new_dict['users'].append({'account':user[0], 'password':user[1],"role":user[2]})
	with open("./role settings.json","w") as json_file1:
		json.dump(new_dict, json_file1)	

####################################################################################################




app=Flask(__name__)
cache=redis.Redis(host='redis', port=6379)
global admin


@app.route('/', methods=['GET','POST'])

def pre_app():
	#array che conterrà il numero totale di sub inviata per ciascuna 
	timesSent=[]
	#array che conterrà il nome dei parametri analizzati
	header=[]
	#array di ausilio per la pubblicazione all'utente degli alarm
	ok=[]
	#ottengo le sub di mio interesse
	data=get_sub(timesSent,header)
	#controllo dei threshold se stati modificati
	cont_head_sub,cont_val_sub=control_threshold(data,header)
	
	#creazione degli wait_exit
	create_wait_alert(header)
	
	
	while True:
		timesSent=[]
		header=[]
		data=get_sub(timesSent,header)
		
	
		if request.method == 'GET':
			header=[]
			ok=obtain_alert_wait()
			data=get_sub(timesSent,header)
			
			#quello che otteniamo in realtà è un array con all'interno tutti i nostri messaggi da pubblicare
			message_out=json.dumps(ok)
			ok=json.loads(message_out)
			#for n in range(len(ok)-1):
				
				#tentativo di formattazione, andato a male
				#message_out+="</li>"+ok[n+1]+"</li>"
			return jsonify(ok)
			
			
				
			
		elif request.method == 'POST':
			timesSent1=[]
			header=[]
			data=get_sub(timesSent1,header)
			
			message_out=case_post(timesSent,timesSent1,data)
			
			
			return str(message_out)
			
			
################################################################################

@app.route('/analysis', methods=['GET','POST'])
def analysis():
	#array che conterrà il numero totale di sub inviata per ciascuna 
	timesSent=[]
	#array che conterrà il nome dei parametri analizzati
	header=[]
	#ottengo le sub di mio interesse
	data=get_sub(timesSent,header)
	
	output="<!doctype html><html><head><title>Home</title><body><h1>Home page</h1><label>Scegli il parametro da analizzare<br><form method=\"POST\">" 
	for name in header:
		output+=f"<input type=\"radio\" name=\"parameter\" value=\"{name}\"/> {name} <br>"
	output+="<input type=\"submit\" value=\"Get stat\"></form><button onClick=\"window.location.reload();\">Reload</button>"
	if request.method == 'POST':
		param=request.form.get('parameter')
		max_val,avg_val,status=get_stat_param(param)
		final_str=f"<br>{param}<br><br>Media valori= {avg_val}<br> Val max = {max_val} <br> Status= {status}"
		output+=final_str
		output+="</body></head></html>"	
		outputHtml=Template(output).safe_substitute()
		
		with open("./templates/index.html","a") as output:
			output.write(outputHtml)
		return outputHtml
	elif request.method == "GET":
		output+="</body></head></html>"	
		outputHtml=Template(output).safe_substitute()
		with open("./templates/index.html","a") as output:
			output.write(outputHtml)
		return outputHtml


################################################################################

@app.route('/settings', methods=['GET','POST'])
def settings():
	output='''<!doctype html><html><head><title>Settings</title><body>
		<h1>Settings</h1><label>Cambia le tue impostazioni<br>
		<form method=\"POST\"><br>Mail-Transmitter:
		<input type=\"text\" name=\"account\">
		PASSWORD:<input type=\"text\" name=\"password\">
		<input type=\"submit\" name=\"sub\" value=\"Register admin\"></form>
		<form method=\"POST\"><br> Mail Receiver:
		<input type=\"text\" name=\"recepient\">
		<input type=\"submit\" name=\"sub\" value=\"Register slave\"></form></body></head></html>'''
		
	if request.method == 'POST':
		admin=1
		array_role=['0']
		i=0
		elenco=reading_file()
		user=[]
					
		if request.form['sub']=='Register admin':
			account=request.form.get('account')
			password=request.form.get('password')
			user.append(account)
			user.append(password)
			user.append("admin")
			writing_file(user,elenco)
				
		if request.form['sub']=='Register slave':		
			
			to=request.form.get('recepient')
			user.append(to)
			user.append("-")
			user.append("slave")
			writing_file(user,elenco)	
			
	return output
