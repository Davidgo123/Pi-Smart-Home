import json
import time
import requests
import datetime

bridge_ip = "192.168.178.45"
bridge_username = "J5RVHpoWwgviHQbnYdPaYHJTe63sHIRQxVs1ja6i"
headers = {'content-type': 'application/json'}

# ID der Hueplay
group_id_bars = 4
group_id_lights = 6

# Colors
chillColorX = 0.5200
chillColorY = 0.4100
workColorX = 0.3227
workColorY = 0.3290

def work(brightness):
	payload = {"on":True, "bri":brightness, "xy":[workColorX, workColorY]}
	r = requests.put("http://"+bridge_ip+"/api/"+bridge_username+"/groups/"+str(group_id_bars)+"/action", data=json.dumps(payload), headers=headers)
	r = requests.put("http://"+bridge_ip+"/api/"+bridge_username+"/groups/"+str(group_id_lights)+"/action", data=json.dumps(payload), headers=headers)

def chill(brightness):
	payload = {"on":True, "bri":brightness, "xy":[chillColorX, chillColorY]}
	r = requests.put("http://"+bridge_ip+"/api/"+bridge_username+"/groups/"+str(group_id_bars)+"/action", data=json.dumps(payload), headers=headers)
	r = requests.put("http://"+bridge_ip+"/api/"+bridge_username+"/groups/"+str(group_id_lights)+"/action", data=json.dumps(payload), headers=headers)

def checkOn():
	r = requests.get("http://"+bridge_ip+"/api/"+bridge_username+"/groups/"+str(group_id_bars))

	#Grenzen fuer Power im String festlegen
	power_U = r.text.find("all_on")+8
	power_O = r.text.find("all_on")+12
	#Power extraieren
	power = str(r.text[power_U:power_O])

	if (power == "true"):
		return True
	return False

def checkColor():
	r = requests.get("http://"+bridge_ip+"/api/"+bridge_username+"/groups/"+str(group_id_bars))

	#Grenzen vom brightness Wert festlegen
	bri_U = r.text.find("bri")+5
	bri_O = r.text.find("bri")+8
	#Brightness extraieren
	bri = int(r.text[bri_U:bri_O])

	#Grenzen fuer Color X Wert festlegen
	searchStart = r.text.find("action")
	colorX_U = r.text.find("[", searchStart)+1
	colorX_O = r.text.find("[", searchStart)+7
	#Color X Wert extraieren
	colorX = float(r.text[colorX_U:colorX_O])

	#Grenzen fuer Color Y Wert festlegen
	colorY_U = r.text.find("[", searchStart)+8
	colorY_O = r.text.find("[", searchStart)+14
	#Y Wert extraieren
	colorY = float(r.text[colorY_U:colorY_O])

	if ((chillColorX == colorX or workColorX == colorX) and (chillColorY == colorY or workColorY == colorY) and (bri == getBrightness(0) or bri == getBrightness(-1))):
		return True
	return False

# Passt Helligkeit an die Uhrzeit an
def getBrightness(last):
	hour = int(datetime.datetime.now().strftime('%H')) + last

	if (hour <= 4) or (hour >= 21):
		return 120
	if (hour == 5) or (hour == 20):
		return 150
	if (hour == 6) or (hour == 19):
		return 180
	if (hour == 7) or (hour == 18):
		return 210
	if (hour <= 8) or (hour >= 17):
		return 230
	return 250

# Main
work(getBrightness(0))
while(True):
	#3600s = 60min
	if (checkOn() and checkColor()):
		work(getBrightness(0))
		time.sleep(3600)
		#300s = 5min
		chill(getBrightness(0))
		time.sleep(300)
	#Falls Einstellungen geaendert werden, wird das Programm beendet
	else:
		break
