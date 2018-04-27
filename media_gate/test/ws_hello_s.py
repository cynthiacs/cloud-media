import asyncio
import websockets

async def echo(websocket, path):
    async for message in websocket:
        print("got:", message)
        await websocket.send("echo: " + message)

asyncio.get_event_loop().run_until_complete(
    websockets.serve(echo, '0.0.0.0', 9001))
    # the follwing expresses are wrong?
    #websockets.serve(echo, 'www.yangxudong.com', 9001))
    #websockets.serve(echo, '139.224.128.15', 9001))

asyncio.get_event_loop().run_forever()
