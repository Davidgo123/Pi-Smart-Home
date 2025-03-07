import json
import requests
import time
import os
from fritzconnection.lib.fritzhosts import FritzHosts

bridge_ip = "192.168.178.45"
bridge_username = os.environ['bridge_username']
headers = {'content-type': 'application/json'}

URL = 'http://192.168.178.20:80/YamahaRemoteControl/ctrl'
headers = {'Content-Type': 'text/xml'}

pc_mac = '70:85:C2:28:1E:D1'

# ---------------------------------------------------------------

pc_power_now = ''
pc_power_last = ''

av_Input_now = ''
av_Input_last = ''


# ---------------------------------------------------------------

# Abfragen des Power Zustandes
def checkPower_AV():
    r = requests.get("http://" + bridge_ip + "/api/" + bridge_username + "/groups/" + str(6), headers=headers)
    # Grenzen fuer Power im String festlegen
    power_U = r.text.find("all_on") + 8
    power_O = r.text.find("all_on") + 12

    if str(r.text[power_U:power_O]) == "true":
        payload = '<YAMAHA_AV cmd="GET"><Main_Zone><Power_Control><Power>GetParam</Power></Power_Control></Main_Zone></YAMAHA_AV>'
        r = requests.post(URL, data=payload, headers=headers)
        # Grenzen fuer Power im String festlegen
        power_U = r.text.find("<Power>") + len("<Power>")
        power_O = r.text.find("</Power>")
        # Power extraieren
        return str(r.text[power_U:power_O])


# Abfragen des Power Zustandes
def checkPower_PC():
    fh = FritzHosts(address='192.168.178.1', password=os.environ['router_pw'])
    hosts = fh.get_hosts_info()
    # iterate over all connected devices
    for index, host in enumerate(hosts, start=1):
        status = 'active' if host['status'] else 'inactive'
        mac = host['mac'] if host['mac'] else '-'
        name = host['name']
        # save PC status
        if mac == pc_mac:
            return status


def switchPower_AV(state):
    # turn off
    if state == 'off':
        payload = {"on": False}
        r = requests.put("http://" + bridge_ip + "/api/" + bridge_username + "/groups/" + str(6) + "/action", data=json.dumps(payload), headers=headers)

    # turn on
    if state == 'on':
        payload = {"on": True}
        r = requests.put("http://" + bridge_ip + "/api/" + bridge_username + "/groups/" + str(6) + "/action", data=json.dumps(payload), headers=headers)
        time.sleep(5)
        payload = '<YAMAHA_AV cmd="PUT"><Main_Zone><Power_Control><Power>On</Power></Power_Control></Main_Zone></YAMAHA_AV>'
        r = requests.post(URL, data=payload, headers=headers)


# ---------------------------------------------------------------

# Setzt Lautstaerke auf -30db (fuer Audio)
def volumeUp_AV():
    payload = '<YAMAHA_AV cmd="PUT"><Main_Zone><Volume><Lvl><Val>-300</Val><Exp>1</Exp><Unit>dB</Unit></Lvl></Volume></Main_Zone></YAMAHA_AV>'
    r = requests.post(URL, data=payload, headers=headers)


# Setzt Lautstaerke auf -65db (fuer Spotify)
def volumeDown_AV():
    payload = '<YAMAHA_AV cmd="PUT"><Main_Zone><Volume><Lvl><Val>-650</Val><Exp>1</Exp><Unit>dB</Unit></Lvl></Volume></Main_Zone></YAMAHA_AV>'
    r = requests.post(URL, data=payload, headers=headers)


# ---------------------------------------------------------------
def SetInput_AV(input):
    payload = '<YAMAHA_AV cmd="PUT"><Main_Zone><Input><Input_Sel>' + input + '</Input_Sel></Input></Main_Zone></YAMAHA_AV>'
    r = requests.post(URL, data=payload, headers=headers)

# Abfragen des Aktuellen Inputs
def getInput_AV():
    payload = '<YAMAHA_AV cmd="GET"><Main_Zone><Input><Input_Sel>GetParam</Input_Sel></Input></Main_Zone></YAMAHA_AV>'
    r = requests.post(URL, data=payload, headers=headers)
    # Grenzen fuer Input im String festlegen
    input_U = r.text.find("<Input_Sel>") + len("<Input_Sel>")
    input_O = r.text.find("</Input_Sel>")
    # input extraieren
    return str(r.text[input_U:input_O])


# ---------------------------------------------------------------
print("start program:")

checkPower_AV()
while True:
    try:
        # Change powerstate from receiver if pc change powerstate
        pc_power_now = checkPower_PC()

        if pc_power_last == "active" and pc_power_now == "inactive":
            print('off')
            switchPower_AV('off')

        if pc_power_last == "inactive" and pc_power_now == "active":
            print('on')
            switchPower_AV('on')
            time.sleep(3)
            SetInput_AV('AUDIO')
            time.sleep(3)
            volumeUp_AV()

        time.sleep(1)

        # Check powerstate and input from AV and change volume on change
        if checkPower_AV() == "On":

            av_Input_now = getInput_AV()

            if av_Input_last != "Spotify" and av_Input_now == "Spotify":
                volumeDown_AV()

            if av_Input_last != "AUDIO" and av_Input_now == "AUDIO":
                volumeUp_AV()

        # save last state
        pc_power_last = pc_power_now
        av_Input_last = av_Input_now

    except:
        print("An exception occurred")

    # wait 2 seconds
    time.sleep(2)
