
class StreamCookie(object):
    def __init__(self, logger):
        self._streams = {}
        self.logger = logger

    def __getitem__(self, item):
        return self._streams[item]

    def __str__(self):
        return str(self._streams)

    def keys(self):
        return self._streams.keys()

    def join_stream(self, stream_tag, puller_tag):
        """ when a new puller start to pull the stream
        """
        print("%s join stream %s" % (puller_tag, stream_tag))
        stream_info = self._streams.setdefault(stream_tag,
                                               {"pullers": [], "expire-time": 0})
        stream_info["pullers"].append(puller_tag)

    def quit_stream(self, stream_tag, puller_tag):
        """ when the puller stop to pull the stream
        """
        print("%s quit stream %s" % (puller_tag, stream_tag))
        stream_info = self._streams.setdefault(stream_tag,
                                               {"pullers": [], "expire-time": 0})
        if puller_tag in stream_info["pullers"]:
            stream_info["pullers"].remove(puller_tag)

    def del_stream(self, stream_tag):
        """when the stream is done
        """
        print("delete stream %s" % stream_tag)
        if stream_tag in self._streams:
            del self._streams[stream_tag]

    def clean_puller(self, puller_tag):
        """ when the puller die, do this
        """
        print("clean puller %s" % puller_tag)
        for k, v in self._streams.items():
            if puller_tag in v["pullers"]:
                v["pullers"].remove(puller_tag)

    def clean_pusher(self, pusher_tag):
        """ when the pusher die, do this
        """
        print("clean pusher %s" % pusher_tag)
        stream_tag = None
        for k, v in self._streams.items():
            app, stream = k.split('/')
            if app == pusher_tag:
                stream_tag = k
                break
        # dictionary should not change size during iteration
        if stream_tag is not None:
            del self._streams[stream_tag]

    def count_puller(self, stream_tag):
        """ count how many puller is attached on the stream
        """
        print("stream %s count puller" % stream_tag)
        stream_info = self._streams.setdefault(stream_tag,
                                               {"pullers": [], "expire-time": 0})
        return len(stream_info["pullers"])
