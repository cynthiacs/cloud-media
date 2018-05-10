
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

    def show_cookie(self):
        self.logger.debug('*** show_cookie')
        for (k,v) in self._streams.items(): 
            self.logger.debug("*** %s, %s" % (k, str(v["pullers"]) ))
            self.logger.debug("*** stream %s count puller: %d" % (k, len(v["pullers"])))

    def join_stream(self, stream_tag, puller_tag):
        """ when a new puller start to pull the stream
        """
        self.show_cookie()
        self.logger.debug("%s join stream %s" % (puller_tag, stream_tag))

        stream_info = self._streams.setdefault(stream_tag,
                                               {"pullers": [], "expire-time": 0})
        if puller_tag not in stream_info["pullers"]:
            stream_info["pullers"].append(puller_tag)

    def quit_stream(self, stream_tag, puller_tag):
        """ when the puller stop to pull the stream
        """
        self.show_cookie()
        self.logger.debug("%s quit stream %s" % (puller_tag, stream_tag))

        stream_info = self._streams.setdefault(stream_tag,
                                               {"pullers": [], "expire-time": 0})
        if puller_tag in stream_info["pullers"]:
            stream_info["pullers"].remove(puller_tag)

    def del_stream(self, stream_tag):
        """when the stream is done
        """
        self.show_cookie()
        self.logger.debug("delete stream %s" % stream_tag)

        if stream_tag in self._streams:
            del self._streams[stream_tag]

    def clean_puller(self, puller_tag):
        """ when the puller die, do this
        """
        self.show_cookie()
        self.logger.debug("clean puller %s" % puller_tag)

        for k, v in self._streams.items():
            if puller_tag in v["pullers"]:
                v["pullers"].remove(puller_tag)

    def clean_pusher(self, pusher_tag):
        """ when the pusher die, do this
        """
        self.show_cookie()
        self.logger.debug("clean pusher %s" % pusher_tag)

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
        stream_info = self._streams.setdefault(stream_tag,
                                               {"pullers": [], "expire-time": 0})
        self.show_cookie()

        return len(stream_info["pullers"])

    def get_pullers(self, pusher_tag):
        for k, v in self._streams.items():
            app, stream = k.split('/')
            if app == pusher_tag:
                return self._streams[k]["pullers"]

        return []
