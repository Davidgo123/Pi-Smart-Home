import time
import requests
import json
from pprint import pprint
from fritzconnection.lib.fritzhosts import FritzHosts

macs = ['12:5E:5E:87:E7:9A',  # David
        '1E:6A:E8:18:00:99',  # Lukas
        '16:D1:B3:39:7E:C4']  # Yannick

ADDRESS = '192.168.178.1'
PASSWORD = 'hirt3846'


# ---------------------------------------------------------------

def getCurrentWeatherAsJson():
    # [lat=52,333][lon=9,7] - Wettbergen
    r = requests.get(
        'https://api.openweathermap.org/data/2.5/weather?lat=52,333&lon=9,7&units=metric&appid=662e86ccdebdefe4deafe7379cd9113a')
    return json.loads(r.text)


def getCurrentTemp():
    json_data = getCurrentWeatherAsJson()
    return json_data['main']['temp']


# ---------------------------------------------------------------

# Abfragen des Power Zustandes
def isDeviceHome(devices):
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
                return True

    # return False if no Device is Online
    return False


# ---------------------------------------------------------------

# check parameters
while True:

    # Heizung an
    if isDeviceHome(macs) and getCurrentTemp() < 12:
        break

    # Heizung aus
    if not isDeviceHome(macs) or getCurrentTemp() > 12:
        break

    time.sleep(60)
