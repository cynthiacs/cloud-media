import http.client


class UserAdminProxy:
    def __init__(self):
        #logger.debug("UserAdminProxy init")
        print("UserAdminProxy init")
        self._host = '127.0.0.1:8085'

    def login(self, s):
        print("UserAdminProxy login(%s, %s)" % (s._account, s._password))
        conn = http.client.HTTPConnection(self._host)
        conn.request("GET","/login_mg")
        r = conn.getresponse()
        ret = r.read()
        print(ret)
        return ret 

