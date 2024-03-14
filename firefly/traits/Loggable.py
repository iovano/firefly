from time import localtime
from firefly.traits.Initializable import Initializable

class Loggable(Initializable):
    verbosity: int = 1
    def __init__(self, **attributes):
        Initializable.__init__(self, **attributes)
    def debug(self, message):
        if (self.verbosity > 1):
            self.log(message)

    def log(self, message):
        if (self.verbosity > 0):
            year, month, day, hour, mins, secs, weekday, yearday = localtime()
            prefix = "{:02d}:{:02d}:{:02d}".format(hour, mins, secs)+": "
            print(prefix+str(message))
