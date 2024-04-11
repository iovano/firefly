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
from firefly.functions.dictMerge import dictMerge

cycle = 0
configRoot = 'firefly/config/'
configFile = 'config.json'
uriCursor: int = 0

def getUri(cursor, cycle, cfg):
    # get current uri
    uris = list(cfg.get('trigger',{}).get('uri'))
    configs = [cfg.get('trigger')]
    sections = [len(uris)]
    periods = cfg.get('trigger',{}).get('period')

    for period in periods:
        configDataBuffer = periods[period]
        if (DateHelper.isInRange(period)):
            uris += configDataBuffer.get('uri')
            sections.append(len(configDataBuffer.get('uri')))
            configs.append(configs[0] | configDataBuffer)

    cursor = cursor % len(uris)
    pos = -1
    limit = 0
    for l in sections:
        pos += 1
        limit += l
        if (cursor <= limit):
            actualConfig = dict(configs[pos])

    if ((cycle) % actualConfig.get('tact', 1) != 0):
        return False

    if (actualConfig.get('shuffle') == True):
        uri = choice(uris)
    else:
        uri = uris[cursor]
    
    uri = actualConfig.get('prefix','' ) + uri + actualConfig.get('suffix', '')

    return uri


def main():
    f = open(configRoot + configFile)
    config = json.loads(f.read())
    if (config.get('include')):
        for fname in config.get('include'):
            fa = open(configRoot + fname)
            aconfig = json.loads(fa.read())
            config = dictMerge(config, aconfig)
            fa.close()
    f.close()

    sensor = Relay(**config.get('gpio'), verbosity = config.get('verbosity'), autoRun = False, writer = config.get('writer'))

    def onIdle(self):
        self.log("idle handler evoked")
    def onTrigger(self):
        try:
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
                        wifi.warn("an error occurred while calling url "+uri)
                        wifi.warn(str(e))

            cycle += 1
        except Exception as e:
            wifi.error("an error occurred during onTrigger handler")
            wifi.error(str(e))
    
    if (not config.get('wifi') or config.get('wifi',{}).get('active') == False):
        wifi = Wlan(
            verbosity = config.get('verbosity'), 
            writer = config.get('writer'),
            autoConnect = False
        )
        wifi.close()
    else:
        wifi = Wlan(
            **config.get('wifi'), 
            writer = config.get('writer'),
            verbosity = config.get('verbosity'), 
            autoConnect = False
        )
        wifi.autoConnect = True
        try:
            asyncio.run(wifi.connect())
        except Exception as e:
            wifi.error(e)

        uri = config.get('wifi',{}).get('onSuccess')
        try:
            asyncio.run(wifi.request(uri))
        except Exception as e:
            wifi.warn("an error occurred while calling url "+uri)
            wifi.warn(str(e))

    Relay.onIdle = onIdle
    Relay.onTrigger = onTrigger

    #server = Server()
    #_thread.start_new_thread(server.run, ())

    sensor.run()
main()