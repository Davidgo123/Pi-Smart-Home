from flask import Flask
import subprocess

import time
import json
import requests

# Hue wichtige Konstanten (IP, Username, Header, Payload)
bridge_ip = "192.168.178.45"
bridge_username = "J5RVHpoWwgviHQbnYdPaYHJTe63sHIRQxVs1ja6i"
headers = {'content-type': 'application/json'}
# ID der Hueplay
group_id_bars = 4
group_id_lights = 6
lamp_id_nachttisch = 14
# Variable fuer Aktive Konzentrationspausen
work_light = False
cozy_light = False
process_work = None
process_chill = None

# Webserver
model = Flask(__name__)

# Toggle Arbeits-Skript | Chill-Skript
@model.route("/work")
def work():
	global work_light
	global process_work
	global process_chill
	global cozy_light

	cozy_light = False
	work_light = change_bool(work_light)

	if work_light:
		if process_chill:
			process_chill.terminate()
		feedbackStartWork()
		process_work = subprocess.Popen(['python', 'model/HueWorkSkript.py'])
		time.sleep(0.5)
		process_av = subprocess.Popen(['python', 'model/AV-Control.py'])

	elif not work_light:
		if process_work:
			process_work.terminate()
		feedbackEndWork()
		process_chill = subprocess.Popen(['python', 'model/HueChillSkript.py'])
		turn_lamps_off()
	return str(work_light)

# Toggle Cozy-Skript | Cozy-Skript-eat
@model.route("/cozy")
def cozy():
	global work_light
	global process_work
	global process_chill
	global cozy_light

	work_light = False

	if process_chill:
		process_chill.terminate()

	if process_work:
		process_work.terminate()

	cozy_bars = {"on":True, "bri":125, "xy":[0.58,0.4]}
	cozy_lights = {"on":True, "bri":10, "xy":[0.58,0.4]}
	r = requests.put("http://"+bridge_ip+"/api/"+bridge_username+"/groups/"+str(group_id_bars)+"/action", data=json.dumps(cozy_bars), headers=headers)
	time.sleep(0.2)
	r = requests.put("http://"+bridge_ip+"/api/"+bridge_username+"/groups/"+str(group_id_lights)+"/action", data=json.dumps(cozy_lights), headers=headers)
	time.sleep(0.2)

	if cozy_light:
		eat_nachttisch = {"on":True, "bri":120, "xy":[0.58,0.4]}
		r = requests.put("http://"+bridge_ip+"/api/"+bridge_username+"/lights/"+str(lamp_id_nachttisch)+"/state", data=json.dumps(eat_nachttisch), headers=headers)

	elif not cozy_light:
		r = requests.put("http://"+bridge_ip+"/api/"+bridge_username+"/lights/"+str(lamp_id_nachttisch)+"/state", data=json.dumps(cozy_lights), headers=headers)

	cozy_light = change_bool(cozy_light)
	return str(cozy_light)

# invertieren eines boolischen Wertes
def change_bool(var):
	return not var

# Feedback beim starten des Arbeitsskriptes
def feedbackStartWork():
	green = {"on":True, "bri": 100, "xy":[0.17,0.7]}
	r = requests.put("http://"+bridge_ip+"/api/"+bridge_username+"/groups/"+str(group_id_bars)+"/action", data=json.dumps(green), headers=headers)
	time.sleep(0.5)

# Feedback beim beenden des Arbeitsskriptes
def feedbackEndWork():
	red = {"on":True, "bri": 100, "xy":[0.7,0.3]}
	r = requests.put("http://"+bridge_ip+"/api/"+bridge_username+"/groups/"+str(group_id_bars)+"/action", data=json.dumps(red), headers=headers)
	time.sleep(0.5)

# Ausschalten der Decken und Nachttischlampe
def turn_lamps_off():
	off = {"on":False}
	r = requests.put("http://"+bridge_ip+"/api/"+bridge_username+"/groups/"+str(group_id_lights)+"/action", data=json.dumps(off), headers=headers)

# Webserver aufruf
if __name__ == "__main__":
        model.run(host='0.0.0.0',port=1337,debug=False)

