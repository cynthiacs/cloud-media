import logging.config
from enum import Enum
from user_admin_proxy import UserAdminProxy
from media_controller_proxy import MediaControllerProxy

logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)

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

    def set_node_tag(self, tag):
        self._node_tag = tag

    def set_status(self, status):
        self._status = status

    async def outer_commander(self, websocket, command):
        print('ws send %s' % (command, ))
        await websocket.send(command)
 

class MediaAdaptor:
    def __init__(self):
        logger.debug("MediaAdaptor init")
        self._uap = UserAdminProxy(logger)
        self._mcp = None 
        self._sessions = []

    def set_mqtt(self, mqtt):
        self._mcp = MediaControllerProxy(mqtt, logger=logger)

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

    def login(self, ws, account, password):
        s = Session(ws, account, password)
        self._sessions.append(s)

        self._uap.login(s) 

    def mcp_connect(self, ws, params):
        pass
        #self._mcp.connect(s, "{url:xxxx, expire_time:eeeee}")

    def mcp_start_push(self, ws, params):
        s = _find_session_by_ws(ws)
        self._mcp.start_push(s, "{url:xxxx, expire_time:eeeee}")

    def mcp_stop_push(self, params):
        pass

media_adaptor = MediaAdaptor()

