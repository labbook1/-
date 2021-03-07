
# -*- coding: utf-8 -*-
# filename: menu.py
# 本文件实现自定义菜单的生成
import urllib
from basic import Basic

class Menu(object):
    def __init__(self):
        pass

    #http接口调用请求

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

    #获取自定义菜单配置接口
    def get_current_selfmenu_info(self, accessToken):
        postUrl = "https://api.weixin.qq.com/cgi-bin/get_current_selfmenu_info?access_token=%s" % accessToken
        urlResp = urllib.urlopen(url=postUrl)
        print urlResp.read()

#类型按钮click：点击推事件用户点击click类型按钮后，微信服务器会通过消息接口推送消息类型为event的结构给开发者，并且带上按钮中开发者填写的key值，开发者可以通过自定义的key值与用户进行交互；
#类型按钮view：跳转URL。用户点击view类型按钮后，微信客户端将会打开开发者在按钮中填写的网页URL，可与网页授权获取用户基本信息接口结合，获得用户基本信息。
if __name__ == '__main__':
    myMenu = Menu()

    postJson = """
    {
        "button":
        [
            {
                "name": "空气数据",
                "sub_button":
                [
                    {
                        "type": "click",
                        "name": "pm2.5查询",
                        "key":  "pm25"
                    },

                    {
                        "type": "click",
                        "name": "pm10查询",
                        "key":  "pm10"
                    },
                   {
                        "type": "view",
                        "name": "图表信息",
                        "url": "http://www.yeelink.net/devices/357749"
                    }
                ]
            },

            {
                "name": "控制模块",
                "sub_button":
                [
                    {
                        "type": "click",
                        "name": "打开净化器",
                        "key":  "open"
                    },

                    {
                        "type": "click",
                        "name": "关闭净化器",
                        "key":  "close"
                    },

                    {
                        "type": "click",
                        "name": "自动模式",
                        "key":  "auto"
                    },

                    {
                        "type": "view",
                        "name": "网页控制",
                        "url":"http://39.108.14.221:2333/"
                    }
                ]
            }，
        ]
    }
    """

    accessToken = Basic().get_access_token()
    #myMenu.delete(accessToken)
    myMenu.create(postJson, accessToken)
