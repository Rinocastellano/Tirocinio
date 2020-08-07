import csv
from crate import client
import requests
with open("./Threshold_WaterStation.csv", newline="",encoding="ISO-8859-1") as filecsv1:
		
	name_param="salinity"
	lettore1=csv.reader(filecsv1,delimiter=",")
	header1=next(lettore1)
	dati1=[row1 for row1 in lettore1]
	threshold=dati1[0]
	limit=dati1[1]
	counter=dati1[2]
	counter_exit=dati1[3]
	#dal db di crate ottengo gli utlimi n parametri, definiti sempre nel file di threshold
	connection=client.connect("http://localhost:4200/#!/tables/doc/etwaterstation")
	cursor = connection.cursor()
	cursor.execute(f"SELECT \"time_index\",\"{name_param}\" FROM \"doc\".\"etwaterstation\" where \"{name_param}\">0 order by \"time_index\" desc limit {counter[header1.index(name_param)]};")
	parametri= cursor.fetchall()
	y=0
	#algoritmo di calcol val max e val avg
	for x in parametri:
		if x[1]>y:
			max_val=x[1]
		x[1]+=y
		y=x[1]
	avg_val=y/int(counter[header1.index(name_param)])
	print(avg_val,max_val)
	url = f"http://localhost:1026/v2/entities/WaterStation:1?attrs=Alert{name_param}"
	headers = {'header': 'Content-Type: application/json'}
	response = requests.request("GET", url, headers=headers)
	if "Alert" not in str(response.text.encode("utf-8")):
		url = f"http://localhost:1026/v2/entities/WaterStation:1?attrs=Wait_alert_{name_param}"
		headers = {'header': 'Content-Type: application/json'}
		response = requests.request("GET", url, headers=headers)
		if "Wait" not in str(response.text.encode("utf-8")):
			status="Sotto controllo"
		else:
			status="Attesa uscita"
	else:
		status="Alarm!"
	print(status)
	print(response.text.encode("utf-8"))
	 
