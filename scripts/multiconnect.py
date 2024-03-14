# SPDX-FileCopyrightText: 2022 Liz Clark for Adafruit Industries
#
# SPDX-License-Identifier: MIT

##This method loops through several SSID / Password matches in the settings.toml file

import os
import wifi
import socketpool

import time

#Add your possible WiFi networks here:
wifiNetworks = {'Poldi und Dieter' : '6393406464831291', 'Lutz und Mo': '6393406464831291'}

print()
print("Attempting to connect to WiFi...")
print()

wifiConnect = False #flag to see if we are already connected

for ssid, password in wifiNetworks.items():
    ##Try next SSID
    if not wifiConnect:
        print("Trying to connect to: " + ssid)
        time.sleep(.1)
        try:
            wifi.radio.connect(ssid,password)
            print("Success! Connected to WiFi network: " + ssid)
            wifiConnect = True #Mark flag so we can stop trying to connect
            pool = socketpool.SocketPool(wifi.radio)
            #  prints MAC address to REPL
            print("My MAC addr:", [hex(i) for i in wifi.radio.mac_address])
            #  prints IP address to REPL
            print("My IP address is", wifi.radio.ipv4_address)
        except:
            print("Failed to connect to: " + ssid)

#Pause if still not connected:
if not wifiConnect:
    print("=============================================")
    print("Failed to connect to all known WiFi networks!")
    print("=============================================")
    time.sleep(60)