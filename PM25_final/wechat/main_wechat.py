
# -*- coding: utf-8 -*-
# filename: test.py
import web
import thread
import threading
import httplib
import json
import time
import requests
import urllib
from basic import Basic
from handle import Handle

threadLock = threading.Lock()

urls = (
    '/wx', 'Handle',
)
device_id=357749
sensor_pm25_id=406182
sensor_pm10_id=406183
sensor_status_id=407106
sensor_control_id=407107
sensor_fire_id=407108
api_url='http://api.yeelink.net/v1.0'
api_key='79a1d17cf69639d259c7df7b83735230'
api_headers={'U-ApiKey':api_key,'content-type': 'application/json'}


def acquiredata(device, sensor):
    #http://api.yeelink.net/v1.0/device/<device_id>/sensor/<sensor_id>/datapoint/<key>
    #http://api.yeelink.net/v1.0/device/357749/sensor/406182/datapoint/
    url=r'%s/device/%s/sensor/%s/datapoints' % (api_url,device,sensor)
    conn = httplib.HTTPConnection("api.yeelink.net")
    conn.request(method="GET",url=url)
    response = conn.getresponse()
    res= response.read()
    data=json.loads(res)
    return data

def postdata(device,sensor,data):
    url=r'%s/device/%s/sensor/%s/datapoints' % (api_url,device,sensor)
    strftime=time.strftime("%Y-%m-%dT%H:%M:%S")
    data={"timestamp":strftime , "value": data}
res=requests.post(url,headers=api_headers,data =json.dumps(data),timeout=30)
    if res.status_code != 200:
        return (False, res.status_code)
    else:
        return (True, None)

#监视火警情况，每一分钟更新一次数据。
def moniterFireStatus():
    alarm_status=0
    while True:
        try:
            if alarm_status>0:
                alarm_status=alarm_status-1
                continue
fire_data=acquiredata(device_id, sensor_fire_id)
            if fire_data["value"]==1 and alarm_status==0:
                alarm_status=5
                wxurl='https://api.weixin.qq.com/cgi-bin/message/mass/sendall?access_token=%s'%Basic().get_access_token()
                strftime=time.strftime("%Y-%m-%dT%H:%M:%S")
                #content_dec=content.encode('utf_8')
      			  wxMsg="""{"filter":{"is_to_all": true},"text":{"content":"""+"\"%s:\n检测到空气状况异常变化，请确认安全\""%strftime+"""}, "msgtype": "text"}"""
                #print content
                #print content_dec
                #print json.dumps(wxMsg).encode('utf-8')
                print wxMsg
                res=requests.post(wxurl,data=wxMsg,timeout=30)
                print res.text
                postdata(device_id,sensor_fire_id,0)
        except Exception as e:
            print e
        time.sleep(60)

if __name__ == '__main__':
    app = web.application(urls, globals())
    thread.start_new_thread(moniterFireStatus, ())
app.run()
