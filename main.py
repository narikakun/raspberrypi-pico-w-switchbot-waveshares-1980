import gc

from nanoguilib.color_setup import ssd
from nanoguilib.nanogui import refresh
from nanoguilib.label import Label
from nanoguilib.writer import CWriter
import nanoguilib.freesans20 as freesans20
from nanoguilib.colors import *

gc.collect()

CWriter.set_textpos(ssd, 0, 0)
wri = CWriter(ssd, freesans20, GREEN, BLACK, verbose=False)
wri.set_clip(True, True, False)
ssd.fill(0)
Label(wri, 2, 2, 'Starting...')
refresh(ssd)

gc.collect()

import hashlib
import hmac
import base64
import cmath
import ntptime
import urequests
import utime
import network

gc.collect()

JST_OFFSET = 9 * 60 * 60
base_url = 'https://api.switch-bot.com/v1.1/'

device_map = {
    "Device ID 1": "Device Name 1",
    "Device ID 2": "Device Name 2",
    "Device ID 3": "Device Name 3"
}

def make_sign(token, secret):
    nonce = 'raspberryPiPicoWH'
    t = int(round(utime.time() * 1000))
    string_to_sign = bytes(f'{token}{t}{nonce}', 'utf-8')
    secret = bytes(secret, 'utf-8')
    sign = base64.b64encode(hmac.new(secret, msg=string_to_sign, digestmod=hashlib.sha256).digest())
    return sign, str(t), nonce

def make_request_header(token, secret):
    sign, t, nonce = make_sign(token, secret)
    headers = {
        "Authorization": token,
        "sign": sign,
        "t": str(t),
        "nonce": nonce
    }
    return headers

def get_temperature_humidity(device_id):
    token = "SwitchBot API Token"
    secret = "SwitchBot API Secret"
    devices_url = base_url + "devices/{}/status"
    headers = make_request_header(token, secret)
    url = devices_url.format(device_id)
    response = urequests.get(url, headers=headers)
    gc.collect()
    if response.status_code == 200:
        data = response.json()
        temperature = data["body"]["temperature"]
        humidity = data["body"]["humidity"]
        return temperature, humidity
    else:
        print("デバイス {} のAPIエラー:".format(device_map[device_id]), response.status_code)
        Label(wri, 170, 2, f"Err: {}".format(response.status_code), fgcolor = RED)
        refresh(ssd)
        return None, None

ssd.fill(0)
Label(wri, 2, 2, 'WiFi Connecting...')
refresh(ssd)

WIFI_SSID = "WiFi SSID"
WIFI_PASSWORD = "WiFi Password"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.config(pm = 0xa11140)  # Disable power-save mode
if not wlan.isconnected():
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while not wlan.isconnected():
        pass
print("WiFiに接続しました")
print("IPアドレス:", wlan.ifconfig()[0])
wifiIp = wlan.ifconfig()[0]

ssd.fill(0)
Label(wri, 2, 2, 'WiFi Success')
Label(wri, 40, 2, wifiIp)
refresh(ssd)

utime.sleep(2)
ssd.fill(0)
Label(wri, 2, 2, 'NTP Setting...')
refresh(ssd)
try:
    ntptime.settime()
    ssd.fill(0)
    Label(wri, 2, 2, 'NTP Success')
    refresh(ssd)
except OSError:
    ssd.fill(0)
    Label(wri, 2, 2, 'NTP Error')
    refresh(ssd)
    print("NTP Error")

ssd.fill(0)
Label(wri, 2, 2, 'Ok...')
refresh(ssd)

gc.collect()

Label(wri, 170, 2, 'GC OK', fgcolor = RED)
refresh(ssd)
        
while True:
    counter = 0
    for device_id in device_map:
        gc.collect()
        Label(wri, 170, 2, 'Req Now', fgcolor = RED)
        Label(wri, 170, 80, str(wlan.status()), fgcolor = RED)
        refresh(ssd)
        temperature, humidity = get_temperature_humidity(device_id)
        (year, month, day, hour, min, sec, wd, yd) = utime.localtime(utime.time() + JST_OFFSET)
        room_name = device_map[device_id]
        Label(wri, 170, 2, 'Req OK    ', fgcolor = RED)
        refresh(ssd)
        if temperature is not None and humidity is not None:
            ssd.fill_rect(0, counter * 49, 240, 49, BLACK)
            Label(wri, 2 + (counter * 49), 2, f"{room_name} ({hour:02d}:{min:02d}:{sec:02d})")
            Label(wri, 25 + (counter * 49), 10, f"{temperature:2.1f}", fgcolor = YELLOW)
            Label(wri, 25 + (counter * 49), 55, f"[deg] / ")
            Label(wri, 25 + (counter * 49), 120, f"{humidity:02d}", fgcolor = YELLOW)
            Label(wri, 25 + (counter * 49), 153, f"[%]")
            refresh(ssd)
            counter += 1
            if counter >= 3:
                counter = 0
        utime.sleep(1)
    utime.sleep(5)


