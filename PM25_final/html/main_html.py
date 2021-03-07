#coding=utf-8
from flask import Flask, render_template , request
import time
import os
import sys
import imp
import thread
import threading
import time
import requests
import json
import httplib
#import wiringpi2 as wiringpi
app = Flask(__name__)
a = 'checked'
device_id=357749
sensor_pm25_id=406182
sensor_pm10_id=406183
sensor_status_id=407106
sensor_control_id=407107#控制信号对应的Yeelink ID
sensor_fire_id=407108#火警信号
api_url='http://api.yeelink.net/v1.0'
api_key='79a1d17cf69639d259c7df7b83735230'
api_headers={'U-ApiKey':api_key,'content-type': 'application/json'}

def acquiredata(device, sensor):#从Yeelink获取数据
    #http://api.yeelink.net/v1.0/device/<device_id>/sensor/<sensor_id>/datapoint/<key>
    try:
        url=r'%s/device/%s/sensor/%s/datapoints' % (api_url,device,sensor)
        conn = httplib.HTTPConnection("api.yeelink.net")
        conn.request(method="GET",url=url)
        response = conn.getresponse()
        #print response.status, response.reason
        res= response.read()
        data=json.loads(res);
    except Exception as e:
        data={"timestamp":"-","value":0}
    return data;
def postdata(device,sensor,data):#向Yeelink发送数据
    url=r'%s/device/%s/sensor/%s/datapoints' % (api_url,device,sensor)
    strftime=time.strftime("%Y-%m-%dT%H:%M:%S")
    data={"timestamp":strftime , "value": data}
    res=requests.post(url,headers=api_headers,data=json.dumps(data),timeout=30)
    if res.status_code != 200:
        return (False, res.status_code)
    else:
        return (True, None)

@app.route('/',methods=['GET','POST'])
def index():

    sensor_control_data=acquiredata(device_id,sensor_control_id)

    #控制传感器状态
    if request.method =='POST':
        control_str=request.form["turn_on"]
        if control_str==u'打开净化器':
            postdata(device_id,sensor_control_id,1)
            sensor_control_data["value"]=1
            print 'nowopen'
        elif control_str==u'关闭净化器':
            postdata(device_id,sensor_control_id,-1)
            sensor_control_data["value"]=-1
            print 'nowclose'
        elif control_str==u'自动控制模式':
            postdata(device_id,sensor_control_id,0)
            sensor_control_data["value"]=0
            print 'nowauto'
        else:
            print 'error'

    #获取空气净化器工作状况
    sensor_pm25_data=acquiredata(device_id,sensor_pm25_id) sensor_pm10_data=acquiredata(device_id,sensor_pm10_id)
sensor_status_data=acquiredata(device_id,sensor_status_id)
sensor_control_data=acquiredata(device_id,sensor_control_id)
sensor_fire_data=acquiredata(device_id,sensor_fire_id)

    #渲染网页并呈现
    return render_template('pm25.html',pm25= sensor_pm25_data["value"],pm10=sensor_pm10_data["value"],state=sensor_status_data["value"],control=sensor_control_data["value"],fire=sensor_fire_data["value"],lastupdate=sensor_pm25_data["timestamp"]);
    time.sleep(10)
    #return render_template('pm25.html',pm25= sensor_pm25_data);

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=2333, debug=True)
