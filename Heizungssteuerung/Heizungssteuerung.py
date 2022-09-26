import time
import requests
import json
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

def getCurrentWeatherAsJson():
    # [lat=52,333][lon=9,7] - Wettbergen
    r = requests.get('https://api.openweathermap.org/data/2.5/weather?lat=52,333&lon=9,7&units=metric&appid=662e86ccdebdefe4deafe7379cd9113a')
    return json.loads(r.text)


# round down currentTemp and return
def getCurrentTemp():
    json_data = getCurrentWeatherAsJson()
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
            if device == mac:
                DeviceIsHomeState = True
                return

    # return False if no Device is Online
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
            requests.post('http://192.168.178.106/relay/0?turn=off')

    # check temp if someone comes home
    if DeviceIsHomeState and not DeviceWasHomeState:
        if checkTempConstraint_ON():
            requests.post('http://192.168.178.106/relay/0?turn=on')


# ---------------------------------------------------------------

# check start heating (temp constraint)
def checkTempConstraint_ON():
    global currentTemp
    global oldTemp

    if currentTemp <= 12 and oldTemp > 12:
        print("Temp goes under 13°, check devices!")
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

try:

    # main loop
    while True:
        # get current temp
        currentTemp = getCurrentTemp()
        checkIfDeviceIsHome(macs)

        # check 30 times device constraint (one time per minute)
        for x in range(30):
            checkDeviceConstraint()
            time.sleep(60)

        if checkTempConstraint_OFF():
            requests.post('http://192.168.178.106/relay/0?turn=off')

        if checkTempConstraint_ON() and DeviceIsHomeState:
            requests.post('http://192.168.178.106/relay/0?turn=on')

        # save temp from now
        oldTemp = currentTemp
        DeviceWasHomeState = DeviceIsHomeState

        # wait one minute
        time.sleep(60)

except:
    print("An exception occurred")
