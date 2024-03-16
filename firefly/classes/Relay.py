from machine import Pin
from utime import sleep
import random
from firefly.traits.Loggable import Loggable

class Relay(Loggable):
    # (public) configuration parameters
    inertia: int            = 100   # specifies inertia (frames) before switching to idle mode
    fps: int                = 10    # specifies frames per second
    warmupDuration: int     = 3     # specifies warmup duration (to allow sensor leveling)
    onTrigger: function     = None  # callback on sensor trigger
    onIdle: function        = None  # callback on idle trigger
    verbosity: int          = 0     # toggle debug log
    autoRun: bool           = True  # autostart the detection
    on: bool                = 1     # specifies input sensor trigger value
    off: bool               = 0     # specifies input sensor idle value
    testMode: bool          = False # if set to "true", triggers will be fired randomly to simulate sensor activity

    input                   = 0     # specifies input GPIO (sensor/button source)
    output                  = 4     # specifies output GPIO (forwarding target)

    # internal variables
    led: Pin                       
    output: Pin
    input: Pin
    counter: int            = 0
    idleSince: int         = None

    def __new__(cls, *args, **kwargs):

        return super().__new__(cls)

    def __init__(self, **attributes):
        Loggable.__init__(self, **attributes)
        self.led  = Pin("LED", Pin.OUT)
        self.debug("Initializing Relay Module")
        self.log(attributes)
        self.output  = Pin(self.output, Pin.OUT)
        self.input  = Pin(self.input, Pin.IN, Pin.PULL_DOWN)
        self.warmup()
        if (self.autoRun):
            self.run()

    def _onTrigger(self):
        self.debug("trigger")
        self.output.high()
        self.led.on()
        if (self.onTrigger):
            self.onTrigger()

    def _onIdle(self):
        self.debug("idle")
        self.led.off()
        self.output.low()
        if (self.onIdle):
            self.onIdle()

    def warmup(self):
        self.debug("GPIO Relay Warmup")

        self.output.high()
        counter = 0
        while counter < self.warmupDuration * self.fps:
            try:
                self.led.toggle()
                counter += 1
                sleep(1/self.fps) # sleep 1sec
            except KeyboardInterrupt:
                break

        self.led.off()
        self.output.low()
        self.debug("Ready")
        sleep(0.5)

    def run(self):
        self.log("GPIO Relay start"+(" in TESTMODE" if self.testMode else ""))
        current = 0
        previous = None

        self.counter = 0
        self.idleSince = - self.inertia
        while True:
            self.counter += 1
            try:
                current = self.input.value()
                if (self.testMode and random.randint(0,30) == 0):
                    current = self.on if (current == self.off) else self.off
                    previous = not self.on
                    self.debug("TEST INCIDENCE CREATED")
                    self.idleSince = - self.inertia
                self.debug(str(current))
                blink = 0
                if (current == self.off):
                    togo = round((self.counter - self.idleSince) / (self.inertia) * 100)
                    if (togo <= 100): 
                        if (self.counter % self.fps >= togo * self.fps / 100 and self.counter % 2 == 0):
                            blink = 1
                    elif (previous != current):
                        previous = current
                        self._onIdle()
                    else:
                        blink = (self.counter % (self.fps * 4) == 0)
                elif (self.counter > self.idleSince + self.inertia + 5):
                    blink = 1
                    self.idleSince = self.counter
                    if (previous != current):
                        previous = current
                        self._onTrigger()
                sleep(1/self.fps) # sleep 1sec
                if (blink):
                    self.led.on()
                else:
                    self.led.off()
            except KeyboardInterrupt:
                self.led.off()
                self.output.low()
                break

        self.log("GPIO Relay termination")
        self.led.off() 