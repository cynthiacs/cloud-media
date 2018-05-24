from mg_adaptor import mg_adaptor 

async def wsp_unicast(msg):
    print('mq_forward_reply')
    print(str(msg.payload))
    await mg_adaptor.wsp_unicast(msg)

async def wsp_broadcast(msg):
    print('mq_forward_reply')
    print(str(msg.payload))
    await mg_adaptor.wsp_broadcast(msg)

