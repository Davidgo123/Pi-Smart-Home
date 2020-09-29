import json
import time
import requests

bridge_ip = "192.168.178.31"
bridge_username = "J5RVHpoWwgviHQbnYdPaYHJTe63sHIRQxVs1ja6i"
headers = {'content-type': 'application/json'}

# ID der Hueplay
group_id_bars = 4


def work():
        payload = {"on":True, "bri": 250, "xy":[0.3227,0.329]}
        r = requests.put("http://"+bridge_ip+"/api/"+bridge_username+"/groups/"+str(group_id_bars)+"/action", data=json.dumps(payload), headers=headers)

def chill():
        payload = {"on":True, "bri":200, "xy":[0.5,0.35]}
        r = requests.put("http://"+bridge_ip+"/api/"+bridge_username+"/groups/"+str(group_id_bars)+"/action", data=json.dumps(payload), headers=headers)


while True:
	#3600s = 60min
	work()
	time.sleep(3600)
	#300s = 5min
	chill()
	time.sleep(300)
