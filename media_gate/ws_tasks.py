from mg_adaptor import mg_adaptor 

def ws_login(kwargs):
    """
    kwargs['ws']: websocket
    kwargs['account']:account 
    kwargs['password']:password
    """
    print('ws_login ...')
    mg_adaptor.login(kwargs['ws'], kwargs['account'], kwargs['password'])
 
def ws_logout(kwargs):
    pass

def ws_error(kwargs):
    print('this is an error task')
    # send error notify reply through the ws

def ws_send_mqtt_request(kwargs):
    msg = kwargs['msg']
    mg_adaptor.mcp_send_request(msg)

