class Observable:
    def __init__(self):
        self._observers = []
 
    def notify(self, payload):
        for observer in self._observers:
            observer.update(self, payload)
 
    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)
 
    def detach(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass