# -*- coding: utf-8 -*-

import os
import sys
import imp
import thread
import threading
import time
import requests
import json
import httplib

DVK512 = False

api_url='http://api.yeelink.net/v1.0'
api_key='79a1d17cf69639d259c7df7b83735230'
api_headers={'U-ApiKey':api_key,'content-type': 'application/json'}

def acquiredata(device, sensor):
    try:
    #http://api.yeelink.net/v1.0/device/<device_id>/sensor/<sensor_id>/datapoint/<key>
        url=r'%s/device/%s/sensor/%s/datapoints' % (api_url,device,sensor)
        conn = httplib.HTTPConnection("api.yeelink.net")
        conn.request(method="GET",url=url)
        response = conn.getresponse()
        res= response.read()
        data=json.loads(res)
    except Exception as e:
        print e
        print url
        data={"timestamp" : "-", "value" : 0}
    return data

def postdata(device, sensor, data):
    try:
        url=r'%s/device/%s/sensor/%s/datapoints' % (api_url,device,sensor)
        strftime=time.strftime("%Y-%m-%dT%H:%M:%S")
        data={"timestamp":strftime , "value": data}
        res=requests.post(url,headers=api_headers,data=json.dumps(data),timeout=30)
        if res.status_code != 200:
            return (False, res.status_code)
        else:
            return (True, None)
    except Exception as e:
        print e
        return (False, 1111)
