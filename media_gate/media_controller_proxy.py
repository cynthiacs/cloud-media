
class MediaControllerProxy:
    def __init__(self, mqtt, logger):
        logger.debug("MediaControllerProxy init")
        self._mqtt = mqtt
        self._logger = logger

    def online(self, s):
        self._logger.debug("MediaControllerProxy.online(%s)" % (s.tag,))
        # lock: some interface is exposed to other thread,
        # send request
        # waiting for reply
        # signal the result

    def start_push(self, s, params):
        self._logger.debug("MediaControllerProxy.start_push(%s)" % (params,))
        # send request
        # waiting for reply
        # signal the result


