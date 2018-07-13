import threading
import websockets
import asyncio
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
import base64
from config import config

from ws_tasks import ws_login, ws_logout, ws_error, ws_send_mqtt_request

class WsThread(threading.Thread):
    def __init__(self, main_loop, *args, **kwargs):
        self._main_loop = main_loop
        threading.Thread.__init__(self, *args, **kwargs)
        #self.daemon = True
        #self.loop = None
        with open('rsa_1024_priv.pem') as f:
            key = f.read()
            rsakey = RSA.importKey(key)
            self.cipher = Cipher_pkcs1_v1_5.new(rsakey)

    def _send_corutine(self, co):
        asyncio.run_coroutine_threadsafe(co, self._main_loop) 

    def _send_callable(self, ca, **kwargs):
        self._main_loop.call_soon_threadsafe(ca, kwargs)


    async def message_handler(self, websocket, path):
        async for message in websocket:
            print("got:", message)
            print(repr(websocket))
            #await websocket.send("echo: " + message)

            if config['media_gate']['encrypt']:
                if self.cipher != None:
                    text = self.cipher.decrypt(base64.b64decode(message), "ERROR")
                    print("decrypt message:")
                    print(text)
                    message = text
                else:
                    print("MG ERROR: cipher is None!")
                    return

            jrpc = eval(message)
            method = jrpc['method']

            if method == 'Login': 
                # note that ws.send must run as coroutine
                asyncio.run_coroutine_threadsafe(
                    ws_login(ws=websocket, msg=message), self._main_loop) 
            elif method == 'Logout': 
                asyncio.run_coroutine_threadsafe(
                    ws_logout(ws=websocket, msg=message), self._main_loop) 
            elif method == 'Online':
                self._send_callable(ws_send_mqtt_request, ws=websocket, msg=message)
            elif method == 'Offline':
                self._send_callable(ws_send_mqtt_request, ws=websocket, msg=message)
            elif method == 'StartPushMedia':
                self._send_callable(ws_send_mqtt_request, ws=websocket, msg=message)
            elif method == 'StopPushMedia':
                self._send_callable(ws_send_mqtt_request, ws=websocket, msg=message)
            else:
                print("unsupported command %s" % (method,))
                params = '{"method":"echo", "params":"unsupported command"}'
                self._send_callable(ws_error, websocket, params)
  
    def run(self):
        self.loop = asyncio.new_event_loop()
        #https://github.com/aaugustin/websockets/issues/60
        coro = websockets.serve(self.message_handler, '0.0.0.0', 9001, loop=self.loop)
        self.loop.run_until_complete(coro)
        self.loop.run_forever()
  
