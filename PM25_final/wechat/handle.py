
# -*- coding: utf-8 -*-
# filename: handle.py
# ���ļ�ͨ��receive.py�ķ���ֵʵ���ı���Ϣ�Ͱ�ť�Ļظ�
import hashlib
import reply
import receive
import web
import httplib
import json
import time
import requests

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
    res=requests.post(url,headers=api_headers,data=json.dumps(data),timeout=30)
    if res.status_code != 200:
        return (False, res.status_code)
    else:
        return (True, None)

class Handle(object):
    def POST(self):
        try:
            webData = web.data()
            print "Handle Post webdata is ", webData   #��̨����־
            recMsg = receive.parse_xml(webData)
            

            pm25_data=acquiredata(device_id,sensor_pm25_id)
            pm10_data=acquiredata(device_id,sensor_pm10_id)

            toUser = recMsg.FromUserName
            fromUser = recMsg.ToUserName 
           
	    #����ϢΪ�ı���Ϊ����ѯ��
            if isinstance(recMsg, receive.Msg) and recMsg.MsgType == 'text' and recMsg.Content == '��ѯ':


                content = "pm2.5: %s\npm10:  %s"%(pm25_data["value"],pm10_data["value"])
                replyMsg = reply.TextMsg(toUser, fromUser, content)
                return replyMsg.send()
            #����ϢΪ�ı��Ҳ�Ϊ����ѯ��
 	    elif isinstance(recMsg, receive.Msg) and recMsg.MsgType == 'text' :
                toUser = recMsg.FromUserName
                fromUser = recMsg.ToUserName
                content = "���롰��ѯ����ȡ������������"
                replyMsg = reply.TextMsg(toUser, fromUser, content)
                return replyMsg.send()
                    

            #����ϢΪ���ı�ʱ
            if isinstance(recMsg, receive.EventMsg):
		#�ǰ�ť�����ÿ����ť��keyֵʵʩ��Ӧ����
                if recMsg.Event == 'CLICK':
                    if recMsg.Eventkey == 'pm25':
                        content = "pm2.5: %s"%(pm25_data["value"])
                        replyMsg = reply.TextMsg(toUser, fromUser, content)
                        return replyMsg.send()
                    elif recMsg.Eventkey == 'pm10':
                        content = "pm10: %s"%(pm10_data["value"])
                        replyMsg = reply.TextMsg(toUser, fromUser, content)
                        return replyMsg.send()
                    elif recMsg.Eventkey == 'open':
                        postdata(device_id,sensor_control_id,1)
                        content = u"������...".encode('utf-8')
                        replyMsg = reply.TextMsg(toUser, fromUser, content)
                        return replyMsg.send()
                    elif recMsg.Eventkey == 'close':
                        postdata(device_id,sensor_control_id,-1)
                        content = u"�ر���...".encode('utf-8')
                        replyMsg = reply.TextMsg(toUser, fromUser, content)
                        return replyMsg.send()
                    elif recMsg.Eventkey == 'auto':
                        postdata(device_id,sensor_control_id,0)
                        content = u"�Զ�ģʽת����...".encode('utf-8')
                        replyMsg = reply.TextMsg(toUser, fromUser, content)
                        return replyMsg.send()
            #���������������ʱ
            print "���Ҳ�����"
            return "success"
        except Exception, Argment:
            return Argment
