import time
import json
import requests
import datetime

# Hue wichtige Konstanten (IP, Username, Header, Payload)
bridge_ip = "192.168.178.45"
bridge_username = "J5RVHpoWwgviHQbnYdPaYHJTe63sHIRQxVs1ja6i"
headers = {'content-type': 'application/json'}

# ID der Hueplay
lamp_id_Terasse_1 = 20
lamp_id_Terasse_2 = 21
lamp_id_Wintergarten = 12

# Control Variable fuer einmaliges Schalten
Control_aktiv = True

def checkOn(lamp_id):
	r = requests.get("http://"+bridge_ip+"/api/"+bridge_username+"/lights/"+str(lamp_id))
	#Grenzen fuer Power im String festlegen
	power_U = r.text.find("all_on")+16
	power_O = r.text.find("all_on")+21
	#Power extraieren
	return str(r.text[power_U:power_O])


# Gibt die aktuelle Stunde zurueck
def getHour():
	return  int(datetime.datetime.now().strftime('%H'))+2
# Gibt den aktuellen Tag zurueck
def getDay():
	return str(datetime.datetime.now().strftime('%a'))


# Startet die Chill Scene auf Hueplay
def Wintergarten_on():
	on = {"on":True, "bri":180, "xy":[0.5762,0.3949]}
	while (checkOn(lamp_id_Wintergarten) == "false"):
		r = requests.put("http://"+bridge_ip+"/api/"+bridge_username+"/lights/"+str(lamp_id_Wintergarten)+"/state", data=json.dumps(on), headers=headers)

# Startet die Chill Scene auf Hueplay
def Terasse_on():
	on = {"on":True, "bri":150, "xy":[0.5762,0.3949]}
	while (checkOn(lamp_id_Terasse_1) == "false") or (checkOn(lamp_id_Terasse_2) == "false"):
		r = requests.put("http://"+bridge_ip+"/api/"+bridge_username+"/lights/"+str(lamp_id_Terasse_1)+"/state", data=json.dumps(on), headers=headers)
		time.sleep(2)
		r = requests.put("http://"+bridge_ip+"/api/"+bridge_username+"/lights/"+str(lamp_id_Terasse_2)+"/state", data=json.dumps(on), headers=headers)

# Startet die Chill Scene auf Hueplay
def Wintergarten_off():
	off = {"on":False}
	while (checkOn(lamp_id_Wintergarten) != "false"):
		r = requests.put("http://"+bridge_ip+"/api/"+bridge_username+"/lights/"+str(lamp_id_Wintergarten)+"/state", data=json.dumps(off), headers=headers)

# Startet die Chill Scene auf Hueplay
def Terasse_off():
	off = {"on":False}
	while (checkOn(lamp_id_Terasse_1) != "false") or (checkOn(lamp_id_Terasse_2) != "false"):
		r = requests.put("http://"+bridge_ip+"/api/"+bridge_username+"/lights/"+str(lamp_id_Terasse_1)+"/state", data=json.dumps(off), headers=headers)
		r = requests.put("http://"+bridge_ip+"/api/"+bridge_username+"/lights/"+str(lamp_id_Terasse_2)+"/state", data=json.dumps(off), headers=headers)

while(True):
	time.sleep(5)

	# Ausschalten am Wochenende
	if ((getHour() == 3) and (getDay() == "Fri" or getDay() == "Sat")):
		Control_aktiv = False
		Wintergarten_off()
		time.sleep(2)
		Terasse_off()

	if ((getHour() == 4) and (getDay() == "Fri" or getDay() == "Sat")):
		Control_aktiv = True

	# Ausschalten in der Woche
	if ((getHour() == 8) and (getDay() != "Fri" and getDay() != "Sat")):
		Control_aktiv = False
		Wintergarten_off()
		time.sleep(2)
		Terasse_off()

	if ((getHour() == 9) and (getDay() != "Fri" and getDay() != "Sat")):
		Control_aktiv = True

	# Einschalten um 18 Uhr
	if ((getHour() == 17) and (Control_aktiv == True)):
		Control_aktiv = False
		Wintergarten_on()
		time.sleep(2)
		Terasse_on()

	if (getHour() == 18):
		Control_aktiv = True


