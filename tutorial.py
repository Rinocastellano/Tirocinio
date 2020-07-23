import json
import csv
import requests
import time
from crate import client
import datetime
import os
import subprocess
import docker
#Questa funzione ha lo scopo di ottenere l'indirizzo IP di "docker_web_1", il mio container dove sarà salvato il web_server. 
#tale funzione è utile al fine di tenere il mio web server sempre aggiornato sulle possibil variazioni dell'indirizzo IP

command=json.load(os.popen('sudo docker inspect docker_web_1'))
print(command)

docker_network=command[0]['HostConfig']['NetworkMode']
print(docker_network)
command=f'sudo docker inspect {docker_network}'
#command=os.popen(command).read() 
command=json.load(os.popen(command))
dict_container=command[0]['Containers']
for container in dict_container:
	
	name_container=container
	act_cont=dict_container.get(name_container)
	if "docker_web_1" in act_cont["Name"]:
		#print(act_cont["IPv4Address"])
		limit=act_cont["IPv4Address"].find('/')
		string_use=act_cont["IPv4Address"]
		new_string="http://"+string_use[:limit]+":5000"
		print(new_string)
f=open("my_ip.txt","w+")
f.write(new_string)
f.close

