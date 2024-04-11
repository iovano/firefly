from time import localtime
from firefly.traits.Initializable import Initializable

class Loggable(Initializable):
    verbosity: int = 1
    levels: dict = {0: "[ERROR] ", 1: "[WARN]  ", 2: "[NOTICE]", 3: "[DEBUG] "}
    writer: list = None
    def __init__(self, **attributes):
        Initializable.__init__(self, **attributes)
        self.initFiles()
    
    def initFiles(self, writer = None):
        writer = writer if writer else self.writer
        if (writer):
              for w in writer:
                  if (w.get('overwrite')):
                      with open(w.get('file'), "w"):
                          pass
    
    def write(self, message, level = 1):
        if (level > self.verbosity):
            return
        year, month, day, hour, mins, secs, weekday, yearday = localtime()
        prefix = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(year, month, day, hour, mins, secs)+" "
        message = prefix + self.levels.get(level, '') + " " + str(message)
        print(message)
        if (self.writer):
              for w in self.writer:
                   if (w.get('level') == None or (type(w.get('level')) == list and level in w.get('level')) or w.get('level') == level):
                     fname = w.get('file')
                     limit:int = int(w.get('limit'))
                     if (limit):
                        try:
                            with open(fname, "r") as f:
                                lines = f.read().split('\n')
                        except:
                            with open(fname, "w") as f:
                                pass
                            lines = list()
                        lines.append(message)
                        lines = list(filter(None, lines[(-limit):]))
                        with open(fname, "w") as f:
                            f.write('\n'.join(lines))
                     else:
                        with open(fname, 'a+') as f: 
                            f = open(fname, 'a+')
                            f.write(message+"\n")


    def debug(self, message):
        self.log(message, 3)

    def warn(self, message):
        self.log(message, 1)

    def log(self, message, level = 2):
        self.write(str(message), level)

    def error(self, message):
        self.write(str(message), 0)
