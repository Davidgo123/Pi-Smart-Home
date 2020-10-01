import json
import time
import requests
import datetime

bridge_ip = "192.168.178.31"
bridge_username = "J5RVHpoWwgviHQbnYdPaYHJTe63sHIRQxVs1ja6i"
headers = {'content-type': 'application/json'}

# ID der Hueplay
group_id_bars = 4

# Startet die Chill Scene auf Hueplay
def chill(brightness):
	chill = {"on":True, "bri":brightness, "xy":[0.48,0.42]}
	r = requests.put("http://"+bridge_ip+"/api/"+bridge_username+"/groups/"+str(group_id_bars)+"/action", data=json.dumps(chill), headers=headers)

# Passt Helligkeit an Lautsärke an
def getBrightness():
	hour = int(datetime.datetime.now().strftime('%H'))
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


while True:
        #300s = 5min
        chill(getBrightness())
        time.sleep(300)

