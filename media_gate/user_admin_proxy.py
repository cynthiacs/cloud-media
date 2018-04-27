
class UserAdminProxy:
    def __init__(self, logger):
        logger.debug("UserAdminProxy init")
        self.logger = logger

    def login(self, s):
        self.logger.debug("UserAdminProxy login(%s, %s)" % (s._account, s._password))
        # send http request
        # waiting for reply
        # signal the result


