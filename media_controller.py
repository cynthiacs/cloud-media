from pymongo import MongoClient
from p2p_mqtt.p2p_mqtt import P2PMqtt
from p2p_mqtt.p2p_mqtt import enable_p2p_mqtt_logger

_REQUEST_ONLINE = 'online'
_REQUEST_OFFLINE = 'offline'

p2pc = None

_db_client = MongoClient('mongodb://139.224.128.15')
_db = _db_client.extmqtt_nodes
_db_col_nodes_online = _db.nodes_online


def handle_online(jrpc):
    """
    mehtod: online
    params: {
        whoami: my id
        time: the time to send online request
        location: longi and lati tude
    }
    """
    print(repr(jrpc))
    params = jrpc['params']
    whoami = params['whoami']
    print("----whoami", whoami)
    if _db_col_nodes_online.find_one({'whoami': whoami}) is not None:
        print("already in online, so i remove it and re-Online")
        _db_col_nodes_online.remove({'whoami': whoami})

    _db_col_nodes_online.insert_one(params)
    nodes_online = _db_col_nodes_online.find()
    # update retain topic
    # NOTE: this works!, but str(list(car_online)) wont
    l_nodes_online = list(nodes_online)
    if p2pc is not None:
        print("new ondes online declare!!!!")
        p2pc.mqtt_publish('nodes_online', str(l_nodes_online), 0, True)  # Qos 0, retain

    return "OK"


def handle_offline(jrpc):
    """
    mehtod: offline
    params: {
        whoami: my id
        time: the time to send online request
        location: longi and lati tude
    }
    """
    print(repr(jrpc))
    pass


if __name__ == '__main__':
    enable_p2p_mqtt_logger()
    p2pc = P2PMqtt(broker_url="139.224.128.15", whoami='controller')
    p2pc.register_request_handler(_REQUEST_ONLINE, handle_online)
    p2pc.register_request_handler(_REQUEST_ONLINE, handle_offline)
    p2pc.loop()


