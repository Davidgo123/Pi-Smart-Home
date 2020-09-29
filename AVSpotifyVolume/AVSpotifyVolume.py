import requests
import time

URL = 'http://192.168.178.20:80/YamahaRemoteControl/ctrl'
headers = {'Content-Type': 'text/xml'}

#Setzt Lautstaerke auf -50db (fuer Spotify)
def volumeDown():
	payload = '<YAMAHA_AV cmd="PUT"><Main_Zone><Volume><Lvl><Val>-500</Val><Exp>1</Exp><Unit>dB</Unit></Lvl></Volume></Main_Zone></YAMAHA_AV>';
	r = requests.post(URL, data=payload, headers=headers)
	print("volumeDown(-50db)")

#Setzt Lautstaerke auf -30db (fuer Audio)
def volumeUp():
	payload = '<YAMAHA_AV cmd="PUT"><Main_Zone><Volume><Lvl><Val>-300</Val><Exp>1</Exp><Unit>dB</Unit></Lvl></Volume></Main_Zone></YAMAHA_AV>';
	r = requests.post(URL, data=payload, headers=headers)
	print("volumeUp(-30db)")

#Abfragen des Aktuellen Inputs
def getInput():
	payload = '<YAMAHA_AV cmd="GET"><Main_Zone><Input><Input_Sel>GetParam</Input_Sel></Input></Main_Zone></YAMAHA_AV>';
	r = requests.post(URL, data=payload, headers=headers)
	#Grenzen fuer Input im String festlegen
	input_U = r.text.find("<Input_Sel>") + len("<Input_Sel>");
	input_O = r.text.find("</Input_Sel>");
	#input extraieren
	return  str(r.text[input_U:input_O])

# Abfragen des Power Zustandes
def checkPower():
	payload = '<YAMAHA_AV cmd="GET"><Main_Zone><Power_Control><Power>GetParam</Power></Power_Control></Main_Zone></YAMAHA_AV>';
	r = requests.post(URL, data=payload, headers=headers)
	#Grenzen fuer Power im String festlegen
	power_U = r.text.find("<Power>") + len("<Power>");
	power_O = r.text.find("</Power>");
	# Power extraieren
	return str(r.text[power_U:power_O])

while True:
	t0_input = getInput()
	if checkPower() == "On":
		time.sleep(1)
		t1_input = getInput()

		if (t0_input == "AUDIO" and t1_input == "AUDIO") or (t0_input == "Spotify" and t1_input == "Spotify"):
			print("No Changes on Volume")

		if t0_input == "AUDIO" and t1_input == "Spotify":
			volumeDown()
		if t0_input == "Spotify" and t1_input == "AUDIO":
			volumeUp()

		time.sleep(0.1)

	else:
		time.sleep(3)
