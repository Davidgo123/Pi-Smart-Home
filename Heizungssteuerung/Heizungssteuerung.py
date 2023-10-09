import time
import requests
import json
from datetime import datetime
from fritzconnection.lib.fritzhosts import FritzHosts

macs = [
    '12:5E:5E:87:E7:9A',  # David
    'E2:35:BD:07:7A:23',  # Lukas
    '16:D1:B3:39:7E:C4',  # Yannick
    '4A:77:8D:D0:6D:27'  # Mariella
]

# WIFI Settings
ADDRESS = '192.168.178.1'
PASSWORD = 'hirt3846'

# states for manuel control
r = requests.get('http://192.168.178.106/rpc/Shelly.GetInfoExt')
HeatingIsRunning = r.json()['components'][0]['state']
HeatingWasRunning = r.json()['components'][0]['state']

# saves last valid temp
lastTemp = 0.0

# min temp in celsius
minTempForHeating = 11

# HTTP data for shelly request-Post
jsonON = '{"id": 1, "type": 0, "state": {"state": true}}'
jsonOFF = '{"id": 1, "type": 0, "state": {"state": false}}'


# ---------------------------------------------------------------

def getCurrentDateTimeAsString():
    # dd/mm/YY H:M:S
    return datetime.now().strftime("%d-%m-%Y %H:%M:%S")


# ---------------------------------------------------------------

# return currentTemp
def getCurrentFeelsLikeTemp(lastTemp):
    try:
        # [lat=52,333][lon=9,7] - Wettbergen
        r = requests.get('https://api.openweathermap.org/data/2.5/weather?lat=52,333&lon=9,7&units=metric&appid=662e86ccdebdefe4deafe7379cd9113a')
        json_data = json.loads(r.text)
        print(getCurrentDateTimeAsString() + "  -  got Temp: " + str(json_data['main']['feels_like']))
        # return json_data['main']['temp']
        return json_data['main']['feels_like']

    except:
        print("An exception occurred (getCurrentTemp)")
        return lastTemp


# ---------------------------------------------------------------

# check if device is home
def checkIfDeviceIsHome(devices):
    try:
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
                    return True

        # return False if no Device is Online
        print(getCurrentDateTimeAsString() + "  -  no online device found")
        return False

    except:
        print("An exception occurred (deviceChecking)")
        return False


# ---------------------------------------------------------------

# check start heating (temp constraint)
def checkTempConstraint_ON(currentTemp):
    try:
        if currentTemp <= minTempForHeating:
            # check if heating is not already on
            r = requests.get('http://192.168.178.106/rpc/Shelly.GetInfoExt')
            if not r.json()['components'][0]['state']:
                print(getCurrentDateTimeAsString() + "  -  Temp goes under " + str(minTempForHeating) + " degrees!")
                return True
        return False

    except:
        print("An exception occurred (checkTempConstraint_ON)")
        return False


# ---------------------------------------------------------------

# check stop heating (temp constraint)
def checkTempConstraint_OFF(currentTemp):
    try:
        if currentTemp > minTempForHeating:
            # check if heating is not already off
            r = requests.get('http://192.168.178.106/rpc/Shelly.GetInfoExt')
            if r.json()['components'][0]['state']:
                print(getCurrentDateTimeAsString() + "  -  Temp goes over " + str(minTempForHeating) + " degrees!")
                return True
        return False

    except:
        print("An exception occurred (checkTempConstraint_OFF)")
        return False


# ---------------------------------------------------------------

def getState():
    try:
        r = requests.get('http://192.168.178.106/rpc/Shelly.GetInfoExt')
        return r.json()['components'][0]['state']
    except:
        print("An exception occurred (manuel control check)")
        return False


while True:

    print(getCurrentDateTimeAsString() + "  -  starting checking...")

    # checking manuel control
    try:
        HeatingIsRunning = getState()
        if HeatingIsRunning != HeatingWasRunning:
            print(getCurrentDateTimeAsString() + "  -  manual control detected: sleep for 2h")
            time.sleep(7200)
    except:
        print("An exception occurred (manuel control check)")

    # update temp and DeviceCheck
    currentTemp = getCurrentFeelsLikeTemp(lastTemp)
    DeviceIsHome = checkIfDeviceIsHome(macs)

    # checking constraints
    if checkTempConstraint_OFF(currentTemp) or (not DeviceIsHome):
        requests.post('http://192.168.178.106/rpc/Shelly.SetState', data=jsonOFF)
        print(getCurrentDateTimeAsString() + "  -  stopping heating!")
        HeatingIsRunning = getState()

    elif checkTempConstraint_ON(currentTemp) and DeviceIsHome:
        requests.post('http://192.168.178.106/rpc/Shelly.SetState', data=jsonON)
        print(getCurrentDateTimeAsString() + "  -  starting heating!")
        HeatingIsRunning = getState()

    else:
        print(getCurrentDateTimeAsString() + "  -  nothing to do! (running: " + str(HeatingIsRunning) + ")")

    # save current running state for manuel control
    HeatingWasRunning = HeatingIsRunning

    # 2min sleep
    print("sleep...\n")
    time.sleep(120)
