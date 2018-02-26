import logging
import json
from aliyunsdkcore import client
from aliyunsdklive.request.v20161101 import DescribeLiveStreamsFrameRateAndBitRateDataRequest
from aliyunsdklive.request.v20161101 import SetLiveStreamsNotifyUrlConfigRequest

access_key_id = 'LTAI7D4S4kh8oGTu'
access_key_secret = 'GgX341eXilbN3iOefYFuuImwRl0zmV'
region_id = 'cn-shanghai'


class StreamServer(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.debug("StreamServer")

    def __repuest__(self, request):
        self.client = client.AcsClient(access_key_id, access_key_secret, region_id)
        result = self.client.do_action_with_exception(request)
        return result

    def set_live_streams_notify_url_config(self, domain=None, url=None):
        """
        set_live_streams_notify_url_config
        :param domain:
        :param url:
        :return:
        """
        request = SetLiveStreamsNotifyUrlConfigRequest.SetLiveStreamsNotifyUrlConfigRequest()
        request.set_DomainName(domain)
        request.set_NotifyUrl(url)
        result = self.__repuest__(request)
        self.logger.debug(str(result))

    def get_stream_framerate_and_bitRate(self, domain=None, app=None, stream=None, token=None):
        """
        get_stream_framerate_and_bitRate
        :param domain:
        :param app:
        :param stream:
        :param token:
        :return:
        """
        request = DescribeLiveStreamsFrameRateAndBitRateDataRequest.DescribeLiveStreamsFrameRateAndBitRateDataRequest()
        request.set_DomainName(domain)
        request.set_AppName(app)
        request.set_SecurityToken(token)
        request.set_StreamName(stream)
        result = self.__repuest__(request)
        x = json.loads(result)
        self.logger.debug(x['RequestId'])
        self.logger.debug(x['FrameRateAndBitRateInfos'])
