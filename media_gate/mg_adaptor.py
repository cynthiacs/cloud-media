from user_admin_proxy import UserAdminProxy
from media_controller_proxy import MediaControllerProxy
from enum import Enum
import datetime

class SessionStatus(Enum):
    initial = 1
    running = 2
    waiting = 3


class Session(object):
    def __init__(self, ws=None, account=None, password=None, tag=None):
        self.ws = ws
        self._account = account 
        self._password = password 
        self.node_tag = tag
        self.node_info = {}
        self._status = SessionStatus.initial
        #self.input_queue = Queue()
        #self._nice = 0

    def set_status(self, status):
        self._status = status

    def ws_send(self, data):
        self.ws.send(data)

    async def outer_commander(self, websocket, command):
        print('ws send %s' % (command, ))
        await websocket.send(command)


class MgAdaptor(object):
    def __init__(self):
        self.uap = UserAdminProxy()
        self.mcp = None 
        self._sessions = []
 
    def set_mqtt(self, mqtt):
        self.mcp = MediaControllerProxy(mqtt)

    def _find_session_by_ws(self, ws):
        """
        find the session whoes websocket is ws
        """
        for s in self._sessions:
            if ws == s.ws:
                return s
        return None 

    def _find_session_by_tag(self, tag):
        """
        find the session whoes node tag is tag 
        """
        for s in self._sessions:
            if tag == s.node_tag:
                return s
        return None 

    def append_session(self, s):
        self._sessions.append(s)

    async def login(self, ws, msg):
        print("debug: mg_adaptor login ")
        jrpc = eval(msg)
        params = jrpc['params']
        rpc_id = jrpc['id']

        account=params['account']
        password=params['password']

        s = Session(ws, account, password)
        self._sessions.append(s)

        resp = self.uap.login(s)

        print(repr(resp))
        resp = eval(resp)
        reply = {}
        reply['jsonrpc'] = '2.0'
        #todo: check the response at first
        if resp['result'] == 'OK':
            """nid = "N%s" % (datetime.datetime.now().microsecond, )"""
            node_tag = "%s_%s_%s" % (resp['vendor_id'], resp['group_id'], resp['node_id'])
            s.node_tag = node_tag 
            del resp['result']
            print(repr(resp))
            print("node_tag: " + node_tag)
            #self._sessions.node_info = resp

            topic = "%s/%s/reply"%(s.node_tag, "media_controller")
            self.mcp.sub(topic)
            reply['result'] = resp
        else:
            reply['error'] = resp['result']

        reply['id'] = rpc_id
        print(repr(reply))
        await ws.send(str(reply).replace('\'', '\"'))

    async def logout(self, ws, msg):
        print("debug: mg_adaptor logout ")
        jrpc = eval(msg)
        params = jrpc['params']
        rpc_id = jrpc['id']

        account=params['account']

        reply = {}
        reply['jsonrpc'] = '2.0'
        s = self._find_session_by_ws(ws)
        if s is not None:
            resp = self.uap.logout(s)
            print(repr(resp))
            resp = eval(resp)

            #todo: check the response at first
            if resp['result'] == 'OK':
                topic = "%s/%s/reply"%(s.node_tag, "media_controller")
                self.mcp.unsub(topic)
                self._sessions.remove(s)
                reply['result'] = resp['result']
                print("unsubscribe topic and removed session")
            else:
                reply['error'] = resp['result']
        else:
            reply['error'] = "ERROR:INVALID"

        reply['id'] = rpc_id
        print(repr(reply))
        await ws.send(str(reply).replace('\'', '\"'))

    def mcp_send_request(self, msg):
        self.mcp.send_request(msg)

    async def wsp_unicast(self, msg):
        print("debug: wsp send one msg")
        topic = msg.topic.split('/')

        ntag = topic[0]
        print('the tag is:' + ntag)
        s = self._find_session_by_tag(ntag)
        if s is None:
            print('no sesion for this node: ' + ntag)
            return

        await s.ws.send(str(msg.payload))

    async def wsp_broadcast(self, msg):
        print("debug: wsp send one msg")
        topic = msg.topic.split('/')

        ntag = topic[0]
        print('the tag is:' + ntag)
        sntag = ntag.split('_')
        if len(sntag) != 3:
            return

        vid,gid,nid = sntag[0],sntag[1],sntag[2]

        for s in self._sessions:
            t = s.node_tag.split('_')
            if vid == '*' or \
                t[0] == vid and gid == '*' or \
                t[0] == vid and t[1] == gid and nid == '*' or \
                t[0] == vid and t[1] == gid and t[2] == nid:
                await s.ws.send(str(msg.payload))


mg_adaptor = MgAdaptor()
