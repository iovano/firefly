# Bibliotheken laden
from machine import Pin
from time import sleep

# Initialisierung des PIR-Moduls
pir = Pin(22, Pin.IN, Pin.PULL_DOWN)

# Initialisierung der Onboard-LED
led = Pin(25, Pin.OUT, value=0)

# Initialisierung für Buzzer
buz = Pin(16, Pin.OUT, value=0)

# PIR-Ruhezustand abwarten
print('Warten')
print()
sleep(3)
print('Bereit')
print()

# Funktion bei Bewerbungserkennung
def pir_handler(pin):
    # PIR-Sensor-Zustand lesen
    pir_value = pir.value()
    if pir_value == 1:
        # Alarm auslösen
        alarm()
        # Warten, bis sich der Bewegungssensor beruhigt hat
        sleep(6)
        print('Ruhezustand')
        print()

def alarm():
    # Text-Ausgabe
    print('Bewegung erkannt')
    print()
    # Buzzer ein
    buz.on()
    # LED blinken lassen
    for i in range(10):
        led.toggle()
        sleep(0.2)
    # Buzzer aus
    buz.off()

# Initialisierung Interrupt für die Bewegungserkennung
pir.irq(trigger=Pin.IRQ_RISING, handler=pir_handler)
sleep(20)