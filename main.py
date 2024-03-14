from firefly.classes.Relay import Relay
from firefly.classes.Wlan import Wlan
import asyncio
from random import choice
from time import localtime
from firefly.classes.Server import Server
import machine
import json

cycle = 0
currentSound = -1


def main():
    f = open('firefly/config.json')
    config = json.loads(f.read())
    print(config['gpio'])
    f.close()

    sensor = Relay(**config.get('gpio'), verbosity = config.get('verbosity'), autoRun = False)

    def onIdle(self):
        self.log("idle handler evoked")
    def onTrigger(self):
        global currentSound
        global cycle
        cycle += 1
        sounds = config.get('trigger',{}).get('uri')
        if (currentSound is None or (cycle-1) % config['trigger']['tact'] != 0):
            return False
        if (not config.get('wifi')):
            return False
        if (config.get('trigger',{}).get('shuffle') == True):
            file = choice(sounds)
        else:
            if (currentSound >= len(sounds)):
                currentSound = 0
            else:
                currentSound += 1
            file = sounds[currentSound]
        year, month, day, hour, minute, second, weekday, yearday = localtime()
        uri = config['trigger']['uriPrefix'] + file
        if (22 >= hour >= 8): 
            uri += config.get('trigger',{}).get('uriSuffix',{}).get('day')
        else:
            uri += config.get('trigger',{}).get('uriSuffix',{}).get('night')
        self.log("#"+str(cycle)+" trigger handler evoked ("+uri+")")
        if (config['wifi'] and not config.get('wifi',{}).get('active') == False):
            try:
                asyncio.run(wifi.request(uri))
            except Exception as e:
                wifi.log("an error occurred while calling url "+uri)
                wifi.log(str(e))
    
    if (not config.get('wifi') or config.get('wifi',{}).get('active') == False):
        wifi = Wlan(verbosity = config.get('verbosity'), autoConnect = False)
        wifi.close()
    else:
        wifi = Wlan(**config.get('wifi'), verbosity = config.get('verbosity'), autoConnect = False)
        wifi.autoConnect = True
        try:
            asyncio.run(wifi.connect())
        except Exception as e:
            wifi.log(e)

        uri = config.get('wifi',{}).get('onSuccess')
        try:
            asyncio.run(wifi.request(uri))
        except Exception as e:
            wifi.log("an error occurred while calling url "+uri)
            wifi.log(str(e))

    Relay.onIdle = onIdle
    Relay.onTrigger = onTrigger

    server = Server()
    asyncio.create_task(server.run())    

    sensor.run()

main()