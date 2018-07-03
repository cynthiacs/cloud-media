from mg_adaptor import mg_adaptor 

async def wsp_unicast(topic, payload):
    print('wsp_unicast: topic:%s, payload:%s' % (topic,payload))
    await mg_adaptor.wsp_unicast(topic, payload)

async def wsp_broadcast(topic, payload):
    print('wsp_broadcast: topic:%s, payload:%s' % (topic,payload))
    await mg_adaptor.wsp_broadcast(topic, payload)

