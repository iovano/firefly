from firefly.classes.Relay import Relay
from firefly.classes.Wlan import Wlan
import asyncio
from random import choice
from time import localtime
from firefly.classes.Server import Server
import machine
import json
import _thread
from array import array
from firefly.classes.DateHelper import DateHelper

cycle = 0
uriCursor: int = 0

def getUri(cursor, cycle, config):
    # get current uri
    uris = config.get('trigger',{}).get('uri')
    configs = [config.get('trigger')]
#    configs[0]['period'] = None
    sections = [len(uris)]
    periods = config.get('trigger',{}).get('period')

    for period in periods:
        configDataBuffer = periods[period]
        if (DateHelper.isInRange(period)):
            uris += configDataBuffer.get('uri')
            sections.append(len(configDataBuffer.get('uri')))
            configs.append(configs[0] | configDataBuffer)

    
    cursor = cursor % len(uris)
    pos = -1
    for limit in sections:
        pos += 1
        if (cursor < limit):
            actualConfig = configs[pos]
    
    actualConfig['period'] = None
    actualConfig['uri'] = None

    if ((cycle) % actualConfig.get('tact', 1) != 0):
        return False

    if (actualConfig.get('shuffle') == True):
        uri = choice(uris)
    else:
        uri = uris[cursor]
    
    uri = actualConfig.get('prefix','' ) + uri + actualConfig.get('suffix', '')

    return uri


def main():
    f = open('firefly/config.json')
    config = json.loads(f.read())
    print(config['gpio'])
    f.close()

    sensor = Relay(**config.get('gpio'), verbosity = config.get('verbosity'), autoRun = False)

    def onIdle(self):
        self.log("idle handler evoked")
    def onTrigger(self):
        global uriCursor
        global cycle
        if (not config.get('wifi')):
            return False
        uri = getUri(uriCursor, cycle, config)
        if (uri):
            uriCursor += 1
            self.log("#"+str(cycle)+" trigger handler evoked ("+uri+")")
            if (config['wifi'] and not config.get('wifi',{}).get('active') == False):
                try:
                    asyncio.run(wifi.request(uri))
                except Exception as e:
                    wifi.log("an error occurred while calling url "+uri)
                    wifi.log(str(e))

        cycle += 1
    
    if (not config.get('wifi') or config.get('wifi',{}).get('active') == False):
        wifi = Wlan(verbosity = config.get('verbosity'), 
        autoConnect = False)
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

    #server = Server()
    #_thread.start_new_thread(server.run, ())

    sensor.run()
main()