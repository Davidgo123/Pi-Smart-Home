import requests
import time

URL = 'http://192.168.178.20:80/YamahaRemoteControl/ctrl'
headers = {'Content-Type': 'text/xml'}

#Startet den Verstaerker
def turnOn():
        payload = '<YAMAHA_AV cmd="PUT"><Main_Zone><Power_Control><Power>On</Power></Power_Control></Main_Zone></YAMAHA_AV>';
        r = requests.post(URL, data=payload, headers=headers)


#Input auf Audio setzen
def setAudio():
        payload = '<YAMAHA_AV cmd="PUT"><Main_Zone><Input><Input_Sel>AUDIO</Input_Sel></Input></Main_Zone></YAMAHA_AV>';
        r = requests.post(URL, data=payload, headers=headers)


#Setzt Lautstaerke auf -30db (fuer Audio)
def volumeUp():
        payload = '<YAMAHA_AV cmd="PUT"><Main_Zone><Volume><Lvl><Val>-300</Val><Exp>1</Exp><Unit>dB</Unit></Lvl></Volume></Main_Zone></YAMAHA_AV>';
        r = requests.post(URL, data=payload, headers=headers)
        print("volumeUp(-30db)")


turnOn()
time.sleep(5)
setAudio()
time.sleep(1)
volumeUp()
