import network
import asyncio
import socket
from firefly.traits.Initializable import Initializable
import asyncio

class Server(Initializable):
    defaultResponse: str = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Pico Web Server</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
            </head>
            <body>
                <h1>Raspberry Pi Pico Web Server</h1>
                <p>It works!</p>
            </body>
            </html>
            """
    async def defaultRequestHandler(reader, writer):
        
        print("Client connected")
        request_line = await reader.readline()
        print('Request:', request_line)
        
        # Skip HTTP request headers
        while await reader.readline() != b"\r\n":
            pass
        
        request = str(request_line, 'utf-8').split()[1]
        print('Request:', request)
        
        # Process the request and update variables
        response = "hello world!"

        # Send the HTTP response and close the connection
        writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        writer.write(response)
        await writer.drain()
        await writer.wait_closed()
        print('Client Disconnected')        

    requestHandler: function = None
    def __init__(self, requestHandler:function = None, **attributes):
        Initializable.__init__(self, **attributes)     
        asyncio.run(self.run(requestHandler))

    async def run(self, requestHandler = None):
        if (requestHandler is not None):
            self.requestHandler = requestHandler
        if (self.requestHandler is None):
            def defaultRequestHandler():
                return str(self.defaultResponse)
            asyncio.start_server(defaultRequestHandler, "0.0.0.0", 80)
        else:
            asyncio.start_server(self.requestHandler, "0.0.0.0", 80)