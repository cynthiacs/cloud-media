
class UserAdminProxy:
    def __init__(self):
        #logger.debug("UserAdminProxy init")
        print("UserAdminProxy init")

    def login(self, s):
        print("UserAdminProxy login(%s, %s)" % (s._account, s._password))
        # send http request
        # waiting for reply
        # signal the result


