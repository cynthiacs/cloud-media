import asyncio
import websockets

def print_usage():
    print("command list:")
    print("help")
    print("login")
    print("online")
    print("offline")
    print("startpush")
    print("stoppush")
    print("exit")

print_usage()

async def send_request(jrpc):
    uri = 'ws://localhost:9001'
    async with websockets.connect(uri) as ws:
        try:
            await ws.send(jrpc)
        except asyncio.TimeoutError:
            # No data in 20 seconds, check the connection.
            try:
                pong_waiter = await ws.ping()
                await asyncio.wait_for(pong_waiter, timeout=10)
            except asyncio.TimeoutError:
                # No response to ping in 10 seconds, disconnect.
                pass
        else:
            # do something with msg
            print('OK ??') 

class Node(object):
    def __init__(self):
        pass
    def str(self):
        return ''

node_info = '{"id":"N1077746422140","nick":"PULLER0","role":"puller","device_name":"default","location":"Location Unknown","stream_status":"pulling_close","vendor_id":"V0001","vendor_nick":"Leadcore","group_id":"G00000","group_nick":"Default Group"}'
jrpc_id = 1000

while True:
    command = input('input a string:')
    if command == 'help':
        print_usage()
        continue
    elif command == 'login':
        params = '{"account":"yxd", "password":"123"}'
    elif command == 'online':
        method = 'Online'
        params = node_info
    elif command == 'offline':
        method = 'Offline'
        params = node_info
    elif command == 'startpush':
        method = 'StartPushMedia'
        params = '{"target-id":"V0001_G00000_N1369191308926","expire-time":"100s"}'
    elif command == 'stoppush':
        method = 'StopPushMedia'
        params = '{"target-id":"V0001_G00000_N1369191308926","expire-time":"100s"}'
    elif command == 'exit':
        break
    else:
        print("unknown method")
        continue

    jrpc_id = jrpc_id + 1 
    request = '{"jsonrpc":2.0, "method":"%s", "params":%s,"id":"%s"}'%(method, params, str(jrpc_id))
    print("the request is:")
    print(request)
    asyncio.get_event_loop().run_until_complete(
        send_request(request))


#async def hello(uri):
#    async with websockets.connect(uri) as ws:
#
#        while True:
#            try:
#                #send reqeust 
#                await ws.send(test_reqeust)
#
#                msg = await asyncio.wait_for(ws.recv(), timeout=20)
#                await asyncio.sleep(3)
#            except asyncio.TimeoutError:
#                # No data in 20 seconds, check the connection.
#                try:
#                    pong_waiter = await ws.ping()
#                    await asyncio.wait_for(pong_waiter, timeout=10)
#                except asyncio.TimeoutError:
#                    # No response to ping in 10 seconds, disconnect.
#                    break
#            else:
#                # do something with msg
#                print('msg:' + msg) 
#
#asyncio.get_event_loop().run_until_complete(
#    hello('ws://localhost:9001'))
#
