import time
import requests
import json
from datetime import datetime
from fritzconnection.lib.fritzhosts import FritzHosts

macs = ['12:5E:5E:87:E7:9A',  # David
        'E2:35:BD:07:7A:23',  # Lukas
        '16:D1:B3:39:7E:C4',  # Yannick
        '4A:77:8D:D0:6D:27'   # Mariella
        ]

# WIFI Settings
ADDRESS = '192.168.178.1'
PASSWORD = 'hirt3846'

# state for last Check if one Device is home
DeviceWasHomeState = False
DeviceIsHomeState = False

r = requests.get('http://192.168.178.106/rpc/Shelly.GetInfoExt')
HeatingIsRunning = r.json()['components'][0]['state']
HeatingWasRunning = r.json()['components'][0]['state']

# HTTP data for shelly request-Post
jsonON = '{"id": 1, "type": 0, "state": {"state": true}}'
jsonOFF = '{"id": 1, "type": 0, "state": {"state": false}}'

# ---------------------------------------------------------------

def getCurrentDateTimeAsString():
    # dd/mm/YY H:M:S
    return datetime.now().strftime("%d-%m-%Y %H:%M:%S")

# ---------------------------------------------------------------

# return currentTemp
def getCurrentTemp():
    try:
        # [lat=52,333][lon=9,7] - Wettbergen
        r = requests.get(
            'https://api.openweathermap.org/data/2.5/weather?lat=52,333&lon=9,7&units=metric&appid=662e86ccdebdefe4deafe7379cd9113a')
        json_data = json.loads(r.text)
        print(getCurrentDateTimeAsString() + "  -  got Temp: " + str(json_data['main']['temp']))
        return json_data['main']['temp']

    except:
        print("An exception occurred (getCurrentTemp)")
        return 0.0

def getCurrentFeelsLikeTemp():
    try:
        # [lat=52,333][lon=9,7] - Wettbergen
        r = requests.get(
            'https://api.openweathermap.org/data/2.5/weather?lat=52,333&lon=9,7&units=metric&appid=662e86ccdebdefe4deafe7379cd9113a')
        json_data = json.loads(r.text)
        print(getCurrentDateTimeAsString() + "  -  got Temp: " + str(json_data['main']['feels_like']))
        return json_data['main']['feels_like']

    except:
        print("An exception occurred (getCurrentTemp)")
        return 0.0

# ---------------------------------------------------------------

# check if device is home
def checkIfDeviceIsHome(devices):
    global DeviceIsHomeState

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
                    DeviceIsHomeState = True
                    return

        # return False if no Device is Online
        print(getCurrentDateTimeAsString() + "  -  no online device found")
        DeviceIsHomeState = False

    except:
        print("An exception occurred (deviceChecking)")
        DeviceIsHomeState = False

# ---------------------------------------------------------------

def checkDeviceConstraint():
    global DeviceIsHomeState
    global DeviceWasHomeState

    checkIfDeviceIsHome(macs)

    try:
        # check if no one is home
        if not DeviceIsHomeState:
            # check if heating is not already off
            r = requests.get('http://192.168.178.106/rpc/Shelly.GetInfoExt')
            if r.json()['components'][0]['state']:
                # stop heating
                time.sleep(1)
                requests.post('http://192.168.178.106/rpc/Shelly.SetState', data=jsonOFF)
                print(getCurrentDateTimeAsString() + "  -  stop heating (no device online)")
                return

        # check temp if someone comes home
        if DeviceIsHomeState and (not DeviceWasHomeState):
            if checkTempConstraint_ON():
                time.sleep(1)
                requests.post('http://192.168.178.106/rpc/Shelly.SetState', data=jsonON)
                print(getCurrentDateTimeAsString() + "  -  start heating (device online)")
                return
    except:
        print("An exception occurred (checkDeviceConstraint)")

# ---------------------------------------------------------------

# check start heating (temp constraint)
def checkTempConstraint_ON():
    global currentTemp

    try:
        if currentTemp <= 12:
            # check if heating is not already on
            r = requests.get('http://192.168.178.106/rpc/Shelly.GetInfoExt')
            if not r.json()['components'][0]['state']:
                print(getCurrentDateTimeAsString() + "  -  Temp goes under 12 degrees!")
                return True
        return False

    except:
        print("An exception occurred (checkTempConstraint_ON)")

# ---------------------------------------------------------------

# check stop heating (temp constraint)
def checkTempConstraint_OFF():
    global currentTemp

    try:
        if currentTemp > 12:
            # check if heating is not already off
            r = requests.get('http://192.168.178.106/rpc/Shelly.GetInfoExt')
            if r.json()['components'][0]['state']:
                print(getCurrentDateTimeAsString() + "  -  Temp goes over 12 degrees!")
                return True
        return False

    except:
        print("An exception occurred (checkTempConstraint_OFF)")


# ---------------------------------------------------------------

while True:

    try:
        r = requests.get('http://192.168.178.106/rpc/Shelly.GetInfoExt')
        HeatingIsRunning = r.json()['components'][0]['state']

        if HeatingIsRunning != HeatingWasRunning:
            print(getCurrentDateTimeAsString() + "  -  manual control detected: sleep for 1h")
            time.sleep(3600)

        # get current temp
        currentTemp = getCurrentFeelsLikeTemp()

        # check 30 times device constraint (one time per minute)
        print(getCurrentDateTimeAsString() + "  -  device checking...")
        checkDeviceConstraint()

        print(getCurrentDateTimeAsString() + "  -  temp checking...")
        if checkTempConstraint_OFF():
            time.sleep(1)
            requests.post('http://192.168.178.106/rpc/Shelly.SetState', data=jsonOFF)
            print(getCurrentDateTimeAsString() + "  -  stop heating (temp)")

        if checkTempConstraint_ON() and DeviceIsHomeState:
            time.sleep(1)
            requests.post('http://192.168.178.106/rpc/Shelly.SetState', data=jsonON)
            print(getCurrentDateTimeAsString() + "  -  start heating (temp)")

        print("sleep...\n")

        # save temp from now
        DeviceWasHomeState = DeviceIsHomeState
        r = requests.get('http://192.168.178.106/rpc/Shelly.GetInfoExt')
        HeatingWasRunning = r.json()['components'][0]['state']

    except:
        print("An exception occurred (main)")

    # wait one minute
    time.sleep(60)
