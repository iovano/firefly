import time
class DateHelper:
    
    @staticmethod
    def createTimeFromString(timeStamp):
        now = list(time.localtime())
        tokens = timeStamp.split(":")
        for i in range(3):
            now[i+3] = int(tokens[i]) if len(tokens) > i else 0
        return time.mktime(tuple(now))
    
    # checks whether a given time is within one or more given time ranges 
    # (e.g. "19:00-20:30:10" or "20:15" or "14:30-15:00,16:30-17:00")
    @staticmethod
    def isInRange(range, current = None):
        if (current is None):
            current = time.time()

        periods = range.split(",")
        for period in periods:
            times = period.split("-")
            if len(times) == 1: # we are dealing with a moment (e.g. 20:15)
                t = DateHelper.createTimeFromString(times[0])
                if current>=t and current<=t+60:
                    return True
            else: # we are dealing with a time range (e.g. 20:15-21:45)
                t1 = DateHelper.createTimeFromString(times[0])
                t2 = DateHelper.createTimeFromString(times[1])
                if current>=t1 and current<=t2:
                    print("Date ("+period+") is in range ("+str(t1)+"<"+str(current)+"<"+str(t2)+")")
                    return True
        return False