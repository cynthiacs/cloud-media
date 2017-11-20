from pymongo import MongoClient
from p2p_mqtt.p2p_mqtt import P2PMqtt
from p2p_mqtt.p2p_mqtt import enable_p2p_mqtt_logger

_REQUEST_ONLINE = 'online'
_REQUEST_OFFLINE = 'offline'
_TOPIC_NODES_WILL = 'nodes_will/#'
_TOPIC_NODES_ON_LINE = 'nodes_online'

p2pc = None


class CollectionOnLine(object):
    def __init__(self, url='mongodb://139.224.128.15'):
        self._db_client = MongoClient(url)
        self._db = self._db_client.extmqtt_nodes
        self._db_col_nodes_online = self._db.nodes_online

    def remove(self, whoami):
        if self._db_col_nodes_online.find_one({'whoami': whoami}) is not None:
            print("already in online, so i remove it and re-Online")
            self._db_col_nodes_online.remove({'whoami': whoami})

    def insert(self, params):
        self._db_col_nodes_online.insert_one(params)

    def find(self):
        nodes_online = self._db_col_nodes_online.find()
        # update retain topic
        # NOTE: this works!, but str(list(car_online)) wont
        l_nodes_online = list(nodes_online)
        return str(l_nodes_online)

    def publish(self, p2p_client):
        p2p_client.mqtt_publish(_TOPIC_NODES_ON_LINE, self.find(), qos=2, retain=True)

    def online(self, p2p_client, whoami, params):
        self.remove(whoami)
        self.insert(params=params)
        self.publish(p2p_client)

    def offline(self, p2p_client, whoami):
        if p2p_client is None:
            raise ValueError("p2p client should not be None")
        self.remove(whoami)
        self.publish(p2p_client)


_online_col = CollectionOnLine()


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

    _online_col.online(p2pc, whoami, params)
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
    params = jrpc['params']
    whoami = params['whoami']
    _online_col.offline(p2pc, whoami)
    return "OK"


def handle_nodes_will(msg):
    print(repr(msg))
    whoami = msg.paylaod
    _online_col.offline(p2pc, whoami)
    pass


if __name__ == '__main__':
    enable_p2p_mqtt_logger()
    p2pc = P2PMqtt(broker_url="139.224.128.15", whoami='controller')
    p2pc.register_request_handler(_REQUEST_ONLINE, handle_online)
    p2pc.register_request_handler(_REQUEST_OFFLINE, handle_offline)
    p2pc.register_topic_handler(_TOPIC_NODES_WILL, handle_nodes_will)
    p2pc.loop()


