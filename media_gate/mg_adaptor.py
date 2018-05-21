from user_admin_proxy import UserAdminProxy
from media_controller_proxy import MediaControllerProxy
from enum import Enum

class SessionStatus(Enum):
    initial = 1
    running = 2
    waiting = 3


class Session(object):
    def __init__(self, ws=None, account=None, password=None, tag=None):
        self._ws = ws 
        self._account = account 
        self._password = password 
        self._node_tag = tag 
        self._status = SessionStatus.initial
        #self.input_queue = Queue()
        #self._nice = 0

    def set_node_tag(self, tag):
        self._node_tag = tag

    def set_status(self, status):
        self._status = status

    def ws_send(self, data):
        self._ws.send(data)

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
            if ws == s._ws:
                return s
        return None 

    def _find_session_by_tag(self, tag):
        """
        find the session whoes node tag is tag 
        """
        for s in self._sessions:
            if tag == s._node_tag:
                return s
        return None 

    def append_session(self, s):
        self._sessions.append(s)

    def login(self, ws, account, password):
        s = Session(ws, account, password)
        self._sessions.append(s)

        self.uap.login(s) 

    def uap_logout(self):
        pass

    def mcp_send_request(self, msg):
        self.mcp.send_request(msg)

    def wsp_send_reply(msg):
        print("debug: wsp send reply")
        # get the tag
        # get the session
        # send the reply to session.websocket
        pass


mg_adaptor = MgAdaptor()
