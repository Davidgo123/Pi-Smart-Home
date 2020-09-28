import requests
import time

URL = 'http://192.168.178.20:80/YamahaRemoteControl/ctrl'

#Setzt Lautstaerke auf -50db (fuer Spotify)
def volumeDown():
	payload = '<YAMAHA_AV cmd="PUT"><Main_Zone><Volume><Lvl><Val>-500</Val><Exp>1</Exp><Unit>dB</Unit></Lvl></Volume></Main_Zone></YAMAHA_AV>';
	headers = {'Content-Type': 'text/xml'}
	r = requests.post(URL, data=payload, headers=headers)
	print("volumeDown(-50db)")

#Setzt Lautstaerke auf -30db (fuer Audio)
def volumeUp():
	payload = '<YAMAHA_AV cmd="PUT"><Main_Zone><Volume><Lvl><Val>-300</Val><Exp>1</Exp><Unit>dB</Unit></Lvl></Volume></Main_Zone></YAMAHA_AV>';
	headers = {'Content-Type': 'text/xml'}
	r = requests.post(URL, data=payload, headers=headers)
	print("volumeUp(-30db)")

#Abfragen des Aktuellen Inputs
def getInput():
	payload = '<YAMAHA_AV cmd="GET"><Main_Zone><Input><Input_Sel>GetParam</Input_Sel></Input></Main_Zone></YAMAHA_AV>';
	headers = {'Content-Type': 'text/xml'}
	r = requests.post(URL, data=payload, headers=headers)
	#Grenzen fuer Input im String festlegen
	input_U = r.text.find("<Input_Sel>") + len("<Input_Sel>");
	input_O = r.text.find("</Input_Sel>");
	#input extraieren
	return  str(r.text[input_U:input_O])

global t0_input
global t1_input

while True:
	t0_input = getInput()
	time.sleep(2)
	t1_input = getInput()

	print("t0:" + t0_input)
	print("t1:" + t1_input)

	if (t0_input == "AUDIO" and t1_input == "AUDIO") or (t0_input == "Spotify" and t1_input == "Spotify"):
		print("No Changes on Volume")

	if t0_input == "AUDIO" and t1_input == "Spotify":
		volumeDown()
	if t0_input == "Spotify" and t1_input == "AUDIO":
		volumeUp()

	print("")
	time.sleep(0.2)

