import logging
from aliyunsdkcore import client
from aliyunsdklive.request.v20161101 import DescribeLiveStreamsFrameRateAndBitRateDataRequest

_AK_ = 'LTAI7D4S4kh8oGTu'
_Secret_ = 'GgX341eXilbN3iOefYFuuImwRl0zmV'
_region_id_ = 'cn-shanghai'


class StreamInfo(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.debug("StreamInfo")
        self.clint = client.AcsClient(_AK_, _Secret_, _region_id_)

    def stream_framerate_and_bitRate(self, domain=None, app=None, stream=None):
        """
        fetch the stream frame rate and bit rate
        :param domain:
        :param app:
        :param stream:
        :return:
        """
        self.logger.debug(str(domain) + '/' + str(app) + '/' + str(stream))
        request = DescribeLiveStreamsFrameRateAndBitRateDataRequest.DescribeLiveStreamsFrameRateAndBitRateDataRequest()
        request.set_DomainName(domain)
        request.set_AppName(app)
        request.set_StreamName(stream)
        result = self.clint.do_action_with_exception(request)
        self.logger.debug(str(result))
        return result
