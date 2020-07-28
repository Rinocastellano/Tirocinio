import csv

f=open("my_ip.txt","r")
my_ip=f.read()
f.close()




#modify new sub
payload = f"\"{my_ip}\""

print(payload)
