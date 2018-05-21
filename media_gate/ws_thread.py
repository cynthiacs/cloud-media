import threading
import websockets
import asyncio
from ws_tasks import ws_login, ws_error, ws_send_mqtt_request 

class WsThread(threading.Thread):
    def __init__(self, main_loop, *args, **kwargs):
        self._main_loop = main_loop
        threading.Thread.__init__(self, *args, **kwargs)
        #self.daemon = True
        #self.loop = None

    def _send_corutine(self, co):
        asyncio.run_coroutine_threadsafe(co, self._main_loop) 

    def _send_callable(self, ca, **kwargs):
        self._main_loop.call_soon_threadsafe(ca, kwargs)


    async def message_handler(self, websocket, path):
        async for message in websocket:
            print("got:", message)
            print(repr(websocket))
            #await websocket.send("echo: " + message)

            jrpc = eval(message)
            method = jrpc['method']
            params = jrpc['params']

            if method == 'login': 
                self._send_callable(ws_login, 
                    ws=websocket, account=params['account'], password=params['password'])
            elif method == 'logout': 
                pass
            elif method == 'Online':
                self._send_callable(ws_send_mqtt_request, msg=message)
            elif method == 'Offline':
                self._send_callable(ws_send_mqtt_request, msg=message)
            elif method == 'Start_push':
                self._send_callable(ws_send_mqtt_request, msg=message)
            elif method == 'Stop_push':
                self._send_callable(ws_send_mqtt_request, msg=message)
            else:
                print("unsupported command %s" % (method,))
                params = '{"method":"echo", "params":"unsupported command"}'
                self.send_callable(ws_error, websocket, params)
  
    def run(self):
        self.loop = asyncio.new_event_loop()
        #https://github.com/aaugustin/websockets/issues/60
        coro = websockets.serve(self.message_handler, '0.0.0.0', 9001, loop=self.loop)
        self.loop.run_until_complete(coro)
        self.loop.run_forever()
  
