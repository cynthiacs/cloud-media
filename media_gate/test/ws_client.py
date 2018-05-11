import asyncio
import websockets

login_reqeust = '{"jsonrpc":2.0, "method":"login", "params":{"account":"yxd", "password":"123"}}'
connect_reqeust = '{"jsonrpc":2.0, "method":"connect", "params":{"tag":"V0001_G0001_N0001", "token":"123456"}}'
start_push_reqeust = ''
stop_push_reqeust = ''


test_reqeust = login_reqeust
#test_reqeust = connect_reqeust

async def hello(uri):
    async with websockets.connect(uri) as ws:

        while True:
            try:
                #send reqeust 
                await ws.send(test_reqeust)

                msg = await asyncio.wait_for(ws.recv(), timeout=20)
                await asyncio.sleep(3)
            except asyncio.TimeoutError:
                # No data in 20 seconds, check the connection.
                try:
                    pong_waiter = await ws.ping()
                    await asyncio.wait_for(pong_waiter, timeout=10)
                except asyncio.TimeoutError:
                    # No response to ping in 10 seconds, disconnect.
                    break
            else:
                # do something with msg
                print('msg:' + msg) 

asyncio.get_event_loop().run_until_complete(
    hello('ws://localhost:9001'))
