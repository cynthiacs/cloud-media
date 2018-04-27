import asyncio
import websockets

async def hello(uri):
    async with websockets.connect(uri) as ws:

        while True:
            try:
                await ws.send("Hello world!")
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
