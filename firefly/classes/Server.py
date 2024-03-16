import asyncio
import socket
from firefly.traits.Initializable import Initializable
import asyncio
from time import sleep
from machine import Pin

class Server(Initializable):
    led: Pin = None
    s: socket = None
    autoStart: bool = False
    def __init__(self, requestHandler:function = None, **attributes):
        Initializable.__init__(self, **attributes)
        self.warmup()
        self.led  = Pin("LED", Pin.OUT)
        if (self.autoStart):
            asyncio.gather(self.run(requestHandler))

    def webpage(self, state = None):
        html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Pico Web Server</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
            </head>
            <body>
                <h1>Raspberry Pi Pico Web Server</h1>
                <h2>Led Control</h2>
                <form action="./lighton">
                    <input type="submit" value="Light on" />
                </form>
                <br>
                <form action="./lightoff">
                    <input type="submit" value="Light off" />
                </form>
                <p>LED state: {state}</p>
                <h2>Fetch New Value</h2>
                <form action="./value">
                    <input type="submit" value="Fetch value" />
                </form>
            </body>
            </html>
            """
        return str(html)

    def warmup(self):
        print('Starting server...')
        addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
        self.s = socket.socket()
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind(addr)
        self.s.listen()
        print('Server is istening on', addr)

    def run(self, requestHandler = None):
        while True:
            try:
                conn, addr = self.s.accept()
                print('Got a connection from', addr)
                
                # Receive and parse the request
                request = conn.recv(1024)
                request = str(request)
                print('Request content = %s' % request)

                try:
                    request = request.split()[1]
                    print('Request:', request)
                except IndexError:
                    pass
                
                # Process the request and update variables
                if request == '/lighton?':
                    print("LED on")
                    self.led.value(1)
                    state = "ON"
                elif request == '/lightoff?':
                    self.led.value(0)
                    state = 'OFF'
                
                # Generate HTML response
                response = self.webpage(self.led.value())  

                # Send the HTTP response and close the connection
                conn.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
                conn.send(response)
                conn.close()

            except OSError as e:
                conn.close()
                print('Connection closed')

            sleep(0.1)