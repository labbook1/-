
# -*- coding: utf-8 -*-
# filename: menu.py
# ���ļ�ʵ���Զ���˵�������
import urllib
from basic import Basic

class Menu(object):
    def __init__(self):
        pass

    #http�ӿڵ�������

    def create(self, postData, accessToken):
        postUrl = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token=%s" % accessToken
        if isinstance(postData, unicode):
            postData = postData.encode('utf-8')
        urlResp = urllib.urlopen(url=postUrl, data=postData)
        print urlResp.read()

    def query(self, accessToken):
        postUrl = "https://api.weixin.qq.com/cgi-bin/menu/get?access_token=%s" % accessToken
        urlResp = urllib.urlopen(url=postUrl)
        print urlResp.read()

    def delete(self, accessToken):
        postUrl = "https://api.weixin.qq.com/cgi-bin/menu/delete?access_token=%s" % accessToken
        urlResp = urllib.urlopen(url=postUrl)
        print urlResp.read()

    #��ȡ�Զ���˵����ýӿ�
    def get_current_selfmenu_info(self, accessToken):
        postUrl = "https://api.weixin.qq.com/cgi-bin/get_current_selfmenu_info?access_token=%s" % accessToken
        urlResp = urllib.urlopen(url=postUrl)
        print urlResp.read()

#���Ͱ�ťclick��������¼��û����click���Ͱ�ť��΢�ŷ�������ͨ����Ϣ�ӿ�������Ϣ����Ϊevent�Ľṹ�������ߣ����Ҵ��ϰ�ť�п�������д��keyֵ�������߿���ͨ���Զ����keyֵ���û����н�����
#���Ͱ�ťview����תURL���û����view���Ͱ�ť��΢�ſͻ��˽���򿪿������ڰ�ť����д����ҳURL��������ҳ��Ȩ��ȡ�û�������Ϣ�ӿڽ�ϣ�����û�������Ϣ��
if __name__ == '__main__':
    myMenu = Menu()

    postJson = """
    {
        "button":
        [
            {
                "name": "��������",
                "sub_button":
                [
                    {
                        "type": "click",
                        "name": "pm2.5��ѯ",
                        "key":  "pm25"
                    },

                    {
                        "type": "click",
                        "name": "pm10��ѯ",
                        "key":  "pm10"
                    },
                   {
                        "type": "view",
                        "name": "ͼ����Ϣ",
                        "url": "http://www.yeelink.net/devices/357749"
                    }
                ]
            },

            {
                "name": "����ģ��",
                "sub_button":
                [
                    {
                        "type": "click",
                        "name": "�򿪾�����",
                        "key":  "open"
                    },

                    {
                        "type": "click",
                        "name": "�رվ�����",
                        "key":  "close"
                    },

                    {
                        "type": "click",
                        "name": "�Զ�ģʽ",
                        "key":  "auto"
                    },

                    {
                        "type": "view",
                        "name": "��ҳ����",
                        "url":"http://39.108.14.221:2333/"
                    }
                ]
            }��
        ]
    }
    """

    accessToken = Basic().get_access_token()
    #myMenu.delete(accessToken)
    myMenu.create(postJson, accessToken)
