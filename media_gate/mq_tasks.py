from mg_adaptor import mg_adaptor 

def mq_forward_reply(msg):
    print('mq_forward_reply')
    print(str(msg.payload))
    mg_adaptor.wsp_send_reply(msg)

