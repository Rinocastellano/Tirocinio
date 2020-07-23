import csv
import json


with open("./DataWaterStation.csv", newline="",encoding="ISO-8859-1") as filecsv:
	lettore=csv.reader(filecsv,delimiter=",")
	header=next(lettore)
	print(header)
	dati=[row for row in lettore]
	for valori in dati:
		import requests
		print(len(valori))
		url = "http://localhost:1026/v2/op/update"
		payload = f"{{\"actionType\":\"APPEND\",\"entities\":[{{\"id\": \"WaterStation:1\", \"type\":\"WaterStation\",\"conductance\":{{\"value\":{valori[1]},\"type\":\"Integer\"}},\"conductivity\":{{\"value\":{valori[2]},\"type\":\"Integer\"}},\"orp\":{{\"value\":{valori[3]},\"type\":\"Integer\"}},\"ph\":{{\"value\":{valori[4]},\"type\":\"Integer\"}},\"salinity\":{{\"value\":{valori[5]},\"type\":\"Integer\"}},\"temperature\":{{\"value\":{valori[6]},\"type\":\"Integer\"}},\"tds\":{{\"value\":{valori[7]},\"type\":\"Integer\"}},\"tss\":{{\"value\":{valori[8]},\"type\":\"Integer\"}},\"turbidity\":{{\"value\":{valori[9]},\"type\":\"Integer\"}},\"dateModified\":{{\"value\":\"{valori[0]}\",\"type\":\"DateTime\"}}}}]}}"

		y=json.loads(payload)
		payload=json.dumps(y)
		headers = {'Content-Type': 'application/json'}

		response = requests.request("POST", url, headers=headers, data = payload)

		print(response.text.encode('utf8'))


