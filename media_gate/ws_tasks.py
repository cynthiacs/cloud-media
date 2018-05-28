from mg_adaptor import mg_adaptor 

async def ws_login(ws, account, password):
    print('ws_login ...')
    await mg_adaptor.login(ws, account, password)
 
def ws_logout(kwargs):
    pass

def ws_error(kwargs):
    print('this is an error task')
    # send error notify reply through the ws

def ws_send_mqtt_request(kwargs):
    msg = kwargs['msg']
    mg_adaptor.mcp_send_request(msg)

