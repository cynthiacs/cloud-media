
class MediaControllerProxy:
    def __init__(self, mqtt):
        print("MediaControllerProxy init")
        self._mqtt = mqtt

    def online(self, s):
        print("MediaControllerProxy.online(%s)" % (s.tag,))
        # lock: some interface is exposed to other thread,
        # send request
        # waiting for reply
        # signal the result

    def start_push(self, s, params):
        print("MediaControllerProxy.start_push(%s)" % (params,))
        # send request
        # waiting for reply
        # signal the result


