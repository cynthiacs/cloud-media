import requests
#http://docs.python-requests.org/en/master/
from config import config


class UserAdminProxy:
    def __init__(self):
        print("UserAdminProxy init")
        self.login_url=config['user_admin']['login_url']

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


