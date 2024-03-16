import network
from machine import Pin
from time import sleep
from firefly.traits.Loggable import Loggable
import urequests
import asyncio
import ntptime
from firefly.classes.Server import Server
from firefly.traits.Initializable import Initializable


class Wlan(Loggable):
    hostname:   str = 'pico'
    country:    str = 'DE'
    ip:         str = None
    wlan:       network.WLAN = None
    timeout:    int = 3
    led:        Pin = None
    server: Server  = None
    autoConnect:bool= True
    def __init__(self, **attributes):
        Loggable.__init__(self, **attributes)
        self.setup()
        self.led  = Pin("LED", Pin.OUT)
        if (self.autoConnect):
            asyncio.run(self.connect())

    def setup(self):
        network.hostname(self.hostname)
        network.country(self.country)
        self.wlan = network.WLAN(network.STA_IF)

    async def connect(self):
        self.debug("Establishing Wifi-Connection...")
        self.wlan.active(True)
        for ssid, password in self.network.items():
            self.debug("Trying to connect with network '"+ssid+"'...")
            self.wlan.connect(ssid, password)
            counter = 0
            while not (self.wlan.isconnected() or counter > self.timeout):
                counter += 1
                self.led.toggle()
                sleep(1)
            if (self.wlan.isconnected() and self.wlan.status() >= 0):
                self.ip = self.wlan.ifconfig()[0]
                self.log("WIFI Connection active ("+self.ip+")")
                for i in range(8):
                    self.led.toggle()
                    sleep(0.05)
                self.led.off()
                self.log("Trying to synchronize local time (Internet Connection required)...")
                ntptime.settime()
                return self.wlan
            else:
                self.debug("Network Timeout")
        raise RuntimeError('NetworkTimeout')

    async def request(self, url): 
        if (not (self.wlan.isconnected() and self.wlan.status() >= 0)):
            if (self.autoConnect):
                self.debug("trying to reconnect...")
                asyncio.run(self.connect())
            else:
                raise RuntimeError('NetworkError')
        self.debug("calling url "+url)
        response = urequests.get(url)
        self.log(response.text)
        return True

    def close(self):
        wlan = network.WLAN()
        wlan.disconnect()
        sleep(1)
        wlan.active(False)
        sleep(1)
        wlan.deinit()
        self.log("wifi disconnected.")