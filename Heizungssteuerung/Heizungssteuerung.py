import time
import requests
import json
from datetime import datetime
from fritzconnection.lib.fritzhosts import FritzHosts

macs = ['12:5E:5E:87:E7:9A',  # David
        '1E:6A:E8:18:00:99',  # Lukas
        '16:D1:B3:39:7E:C4'  # Yannick
        ]

ADDRESS = '192.168.178.1'
PASSWORD = 'hirt3846'

currentTemp = 0
oldTemp = 0

# state for last Check if one Device is home
DeviceWasHomeState = False
DeviceIsHomeState = False

# ---------------------------------------------------------------

def getCurrentDateTimeAsString():
    # dd/mm/YY H:M:S
    return datetime.now().strftime("%d-%m-%Y %H:%M:%S")

# ---------------------------------------------------------------

def getCurrentWeatherAsJson():
    # [lat=52,333][lon=9,7] - Wettbergen
    r = requests.get('https://api.openweathermap.org/data/2.5/weather?lat=52,333&lon=9,7&units=metric&appid=662e86ccdebdefe4deafe7379cd9113a')
    return json.loads(r.text)


# round down currentTemp and return
def getCurrentTemp():
    json_data = getCurrentWeatherAsJson()
    print(getCurrentDateTimeAsString() + "  -  got Temp: " + str(json_data['main']['temp'] // 1))
    return json_data['main']['temp'] // 1


# ---------------------------------------------------------------

def checkIfDeviceIsHome(devices):
    global DeviceIsHomeState

    # Get connected devices in network
    fh = FritzHosts(address='192.168.178.1', password='hirt3846')
    hosts = fh.get_hosts_info()

    # iterate over all connected devices
    for index, host in enumerate(hosts, start=1):
        status = 'active' if host['status'] else 'inactive'
        mac = host['mac'] if host['mac'] else '-'
        # Check Online Status
        for device in devices:
            if device == mac and status == 'active':
                print(getCurrentDateTimeAsString() + "  -  online device found")
                DeviceIsHomeState = True
                return

    # return False if no Device is Online
    print(getCurrentDateTimeAsString() + "  -  no online device found")
    DeviceIsHomeState = False
    return


# ---------------------------------------------------------------

def checkDeviceConstraint():
    global DeviceIsHomeState
    global DeviceWasHomeState

    # check if no one is home
    if not DeviceIsHomeState:
        # check if heating is not already off
        r = requests.get('http://192.168.178.106/relay/0?')
        if not r.json()['ison']:
            # stop heating
            print(getCurrentDateTimeAsString() + "  -  stop heating (no device now online)")
            requests.post('http://192.168.178.106/relay/0?turn=off')

    # check temp if someone comes home
    if DeviceIsHomeState and not DeviceWasHomeState:
        if checkTempConstraint_ON():
            print(getCurrentDateTimeAsString() + "  -  start heating (device now online)")
            requests.post('http://192.168.178.106/relay/0?turn=on')


# ---------------------------------------------------------------

# check start heating (temp constraint)
def checkTempConstraint_ON():
    global currentTemp
    global oldTemp

    if currentTemp <= 12 and oldTemp > 12:
        # check if heating is not already on
        r = requests.get('http://192.168.178.106/relay/0?')
        if r.json()['ison']:
            return True
    return False


# check stop heating (temp constraint)
def checkTempConstraint_OFF():
    global currentTemp
    global oldTemp

    if currentTemp > 12 and oldTemp <= 12:
        print("Temp goes over 12°, heating stopped!")
        # check if heating is not already off
        r = requests.get('http://192.168.178.106/relay/0?')
        if not r.json()['ison']:
            return True
    return False


# ---------------------------------------------------------------
print("start program:")

while True:
    # get current temp
    currentTemp = getCurrentTemp()
    checkIfDeviceIsHome(macs)

    # check 30 times device constraint (one time per minute)
    print(getCurrentDateTimeAsString() + "  -  start 30 times device checking")
    for x in range(30):
        checkDeviceConstraint()
        time.sleep(60)

    print(getCurrentDateTimeAsString() + "  -  start temp checking")
    if checkTempConstraint_OFF():
        print(getCurrentDateTimeAsString() + "  -  stop heating (temp)")
        requests.post('http://192.168.178.106/relay/0?turn=off')

    if checkTempConstraint_ON() and DeviceIsHomeState:
        print(getCurrentDateTimeAsString() + "  -  start heating (temp)")
        requests.post('http://192.168.178.106/relay/0?turn=on')

    # save temp from now
    oldTemp = currentTemp
    DeviceWasHomeState = DeviceIsHomeState

    # wait one minute
    time.sleep(60)


