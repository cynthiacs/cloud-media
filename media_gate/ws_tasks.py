from task import Task
from mg_adaptor import Session

class WsLoginTask(Task):
    def __init__(self, adaptor, ws, params):
        Task.__init__(self)
        self._adaptor = adaptor
        p = params
        self._session = Session(ws, p['account'], p['password'])
        self._adaptor.append_session(self._session)

    def run(self):
        ret = self._adaptor.uap.login(self._session) 
        # send ret to js client
        # self._session.ws_send('OK')


class WsErrorTask(Task):
    def __init__(self, adaptor, ws, params):
        Task.__init__(self)
        print('WsErrorTask')

    def run(self):
        print('this is an error task')


