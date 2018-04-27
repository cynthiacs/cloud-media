#!/usr/bin/env python

import asyncio
import websockets

async def hello(uri):
    async with websockets.connect(uri) as ws:
        await ws.send("Hello world!")

    """
        while True:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=20)
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
                print("what's this case ??") 
    """

asyncio.get_event_loop().run_until_complete(
    hello('ws://localhost:9001'))
