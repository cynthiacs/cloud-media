import threading
from media_gate import media_adaptor
import websockets
import asyncio


class WsThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.daemon = True
        self.loop = None
 
    async def message_handler(self, websocket, path):
        async for message in websocket:
            print("got:", message)
            print(repr(websocket))
            await websocket.send("echo: " + message)
            if message == "login":
                media_adaptor.login(websocket, "yangxudong", "123456")
  
    def run(self):
        self.loop = asyncio.new_event_loop()
        #https://github.com/aaugustin/websockets/issues/60
        coro = websockets.serve(self.message_handler, '0.0.0.0', 9001, loop=self.loop)
        self.loop.run_until_complete(coro)
        self.loop.run_forever()
  
