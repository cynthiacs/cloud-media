import requests
#http://docs.python-requests.org/en/master/


class UserAdminProxy:
    def __init__(self):
        print("UserAdminProxy init")
        self.login_url='http://139.224.128.15:8085/login_mg'

    def login(self, s):
        print("UserAdminProxy login(%s, %s)" % (s._account, s._password))
        data = {}
        data['method'] = 'login'
        data['params'] = {}
        data['params']['account'] = s._account
        data['params']['password'] = s._password

        response = requests.post(url=self.login_url, json=data)
        return response.text

    def logout(self, s):
        print("UserAdminProxy logout(%s, %s)" % (s._account, s._password))
        data = {}
        data['method'] = 'logout'
        data['params'] = {}
        data['params']['account'] = s._account
        data['params']['password'] = s._password

        response = requests.post(url=self.login_url, json=data)
        return response.text


