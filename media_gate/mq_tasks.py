
def mq_forward_reply(msg):
    print('mq_forward_reply')
    print(str(msg.payload))
    # get the tag
    # get the session
    # send the reply to session.websocket

