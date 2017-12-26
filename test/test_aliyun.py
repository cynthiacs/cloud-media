#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import os
import shutil
import oss2
import time

from aliyunsdkcore import client

from aliyunsdklive.request.v20161101 import SetLiveStreamsNotifyUrlConfigRequest
from aliyunsdklive.request.v20161101 import AddLiveDetectNotifyConfigRequest

from aliyunsdklive.request.v20161101 import DescribeLiveStreamsPublishListRequest
#from aliyunsdklive.request.v20161101 import DescribeLiveRecordConfigRequest
#from aliyunsdklive.request.v20161101 import DescribeLiveStreamRecordContentRequest
#from aliyunsdklive.request.v20161101 import CreateLiveStreamRecordIndexFilesRequest
#from aliyunsdklive.request.v20161101 import DescribeLiveStreamsOnlineListRequest


access_key_id = 'LTAI7D4S4kh8oGTu'
access_key_secret = 'GgX341eXilbN3iOefYFuuImwRl0zmV'

def utc_time(t):
    UTC_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    #time.

def send_request(r):
    clt = client.AcsClient(access_key_id, access_key_secret, 'cn-shanghai')
    result = clt.do_action_with_exception(r)
    print(result)
    return result

def set_live_steams_notify_url_config():
    r = SetLiveStreamsNotifyUrlConfigRequest.SetLiveStreamsNotifyUrlConfigRequest()
    r.set_DomainName("push.yangxudong.com")
    r.set_NotifyUrl("http://www.yangxudong.com:8085/cm_live_steams_notify")
    send_request(r)

set_live_steams_notify_url_config()

def add_live_detect_notify_config():
    r = AddLiveDetectNotifyConfigRequest.AddLiveDetectNotifyConfigRequest()
    r.set_DomainName("push.yangxudong.com")
    r.set_NotifyUrl("http://www.yangxudong.com:8085/cm_add_live_detect_notify")
    #r.set_SecurityToken
    #r.set_OwnerId
    send_request(r)

def describe_live_streams_publish_list():
    """
    get all the streams info of the domain
    :return:
    """
    r = DescribeLiveStreamsPublishListRequest.DescribeLiveStreamsPublishListRequest()
    r.set_DomainName("push.yangxudong.com")
    r.set_AppName("live")
    r.set_StreamName('livestream5')
    r.set_StartTime('2017-07-27T17:36:00Z')
    r.set_EndTime('2017-12-27T17:36:00Z')
    send_request(r)


def get_url():
    a = DescribeLiveRecordConfigRequest.DescribeLiveRecordConfigRequest()
    a.set_DomainName("push.yangxudong.com")
    a.set_AppName("myapp1")
    a.set_accept_format("JSON")
    # a.set_accept_format("XML")   #default is None, which is XML
    regionId = "cn-shanghai"
    ak = "LTAI7D4S4kh8oGTu"
    secret = "GgX341eXilbN3iOefYFuuImwRl0zmV"
    s = a.get_url(regionId, ak, secret)
    return "http://live.aliyuncs.com" + s

def url_RecordContent():
    a = DescribeLiveStreamRecordContentRequest.DescribeLiveStreamRecordContentRequest()
    a.set_DomainName("push.yangxudong.com")
    a.set_AppName('record-transcode')
    a.set_StreamName('video1')
    #a.set_accept_format("JSON")
    #a.set_accept_format("XML")   #default is None, which is XML
    a.set_StartTime('2017-07-27T17:36:00Z')
    a.set_EndTime('2017-07-29T17:36:00Z')
    regionId = "cn-shanghai"
    ak = "LTAI7D4S4kh8oGTu"
    secret = "GgX341eXilbN3iOefYFuuImwRl0zmV"
    s = a.get_url(regionId, ak, secret)
    return "http://live.aliyuncs.com" + s


def url_CreateIndexFiles():
    a = CreateLiveStreamRecordIndexFilesRequest.CreateLiveStreamRecordIndexFilesRequest()
    #a.set_accept_format("JSON")
    #a.set_accept_format("XML")   #default is None, which is XML
 
    a.set_DomainName("push.yangxudong.com")
    a.set_AppName('record-transcode')
    a.set_StreamName('video1')
    a.set_OssEndpoint('oss-cn-shanghai.aliyuncs.com')
    a.set_OssBucket('bucket-transcode-in')
    a.set_OssObject('2017-07-28-11:03:52_2017-07-28-11:18:52.mp4')
    #a.set_StartTime('2017-07-27T17:36:00Z')
    #a.set_EndTime('2017-07-29T17:36:00Z')
    a.set_StartTime('2017-07-28T11:03:52Z')
    a.set_EndTime('2017-07-28T11:18:52Z')
 
    regionId = "cn-shanghai"
    ak = "LTAI7D4S4kh8oGTu"
    secret = "GgX341eXilbN3iOefYFuuImwRl0zmV"
    s = a.get_url(regionId, ak, secret)
    return "http://live.aliyuncs.com" + s


def get_online_stream():
    r = DescribeLiveStreamsOnlineListRequest.DescribeLiveStreamsOnlineListRequest()
    r.set_DomainName("push.yangxudong.com")
    r.set_AppName('live')
    r.set_accept_format('json')

    clt = client.AcsClient(access_key_id, access_key_secret, 'cn-shanghai')
    result = clt.do_action_with_exception(r)
    print("online:\n", result)
 

#describe_live_streams_publish_list()

#s = get_url()
#s = url_RecordContent()
#s = url_CreateIndexFiles()
#print(s)

#get_online_stream()

