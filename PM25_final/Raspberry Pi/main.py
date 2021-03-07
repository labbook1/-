# -*- coding: utf-8 -*-
import os
import sys
import imp
import thread
import threading
import time
import requests
import json
import RPi.GPIO as GPIO
from yeelinkFacade import postdata
from yeelinkFacade import acquiredata

DVK512 = False

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)

sensor_control_id=407107
sensor_status_id=407106
device_id=357749
sensor_fire_id=407108

sensors = []
datas = []
normal=None
control=None
status = None
threadLock = threading.Lock()

#参数
th_per_25=0.2 #下降多少时判定有效
th_times_fire=2 #上升几倍时认定火灾
th_fire=500 #认定火灾阈值
th_fire_abs=1500#到达时直接报警
checktime=60 #自动运行时 检查间隔
threshold=30

def shutdown(): #关闭净化器
    GPIO.output(11, GPIO.LOW)
    return 0;

def open(): #打开净化器
    GPIO.output(11, GPIO.HIGH)
    return 1;

def logout(str):
    print ("[%s]%s"%(time.strftime("%Y-%m-%d %H:%M:%S"), str))
    sys.stdout.flush()
def logout_nlf(str):
    print ("[%s]%s"%(time.strftime("%Y-%m-%d %H:%M:%S"), str)),
    sys.stdout.flush()

def load_sensors():
    sensor_path = os.path.abspath("Sensor") + "/"
    sensor_files = os.listdir(sensor_path)

    for filename in sensor_files:
        if filename[-3:] != ".py":
            continue
        try:
            sensor_name = filename[:-3]
            module = imp.load_source(sensor_name, sensor_path + filename)
            class_obj = getattr(module, sensor_name)
            instance = class_obj()
            sensors.append(instance)
        except Exception as e:
            logout("Sensor %s load error:%s"%(filename, e))

def fetchdata():
    while True:
        global datas
        global control
        global status
        global normal
        lst = []
        #收集传感器数据
        try:
            for sensor in sensors:
                try:
                    logout("Sensor %s fetching data..."%sensor.__class__.__name__)
                    result = sensor.GetData()
                    logout_nlf("Fetched:")
                    for data in result:
                        lst.append(data)
                        print ("\t%s\t%d;"%(data["name"],data["data"])),
                    print ("")
                    sys.stdout.flush()
                except Exception as e:
                    logout(str(e))

            #收集运行状态数据
            if status!=None:
                threadLock.acquire()
                status_buf=status
                threadLock.release()
                lst.append({
                    "name": "Status",
                    "symbol": "",
                    "device": device_id,
                    "sensor": sensor_status_id,
                    "data": status_buf
                })
            #将所收集数据放入全局变量中
            threadLock.acquire()
            datas = lst
            threadLock.release()
        except Exception as e:
            print e
        #logout( "Sleep")
        time.sleep(5)
def communicate():
    while True:
        global datas
        global control
        #发送所收集的数据
        threadLock.acquire()
        lst=datas
        threadLock.release()
        if lst!=[]:
            for data in lst:
                res, err = postdata(data["device"], data["sensor"], data["data"])
                logout("SensorID: %s w/ %d\tUploaed: %s"%(str(data["sensor"]),data["data"], "Success" if res else "Failed: %s"%err))
        #获取控制信号
        control_buf=acquiredata(device_id, sensor_control_id)
        logout("Control: %d @ %s"%(control_buf["value"],control_buf["timestamp"]))
        threadLock.acquire()
        control=control_buf
        threadLock.release()
######################################################
        time.sleep(11)

def raiseFireAlarm():
    res, err = postdata(device_id, sensor_fire_id, 1)
    while res!=True:
        res, err = postdata(device_id, sensor_fire_id, 1)
        time.sleep(11)
    print "\n\n\\nn\\n\n\n\nn\n\n\nn\n\n\n\\n\n\n\n\n"

def analyzeandcontrol():
    global control
    global datas
    global status #0(00)手动关闭 1(01)手动开启 2(10)自动关闭 3(11)自动开启
    global normal #1表示开机后空气指数有效下降

    list25=[]
    list10=[]
    for i in range(60):#假设每5秒一个数据 分析5分钟之内的数据
        list25=list25+[999]
        list10=list10+[999]
    t_=-1 #系统时间
    t__=-1 #距离收到新命令的时间
    stat=9999999
    prevalue=0
    while True:

        t_ =t_ + 1 #每5s加1 从0开始
        t__=t__+1
        threadLock.acquire()
        lst=datas
        ctrl=control
        threadLock.release()
        if datas==[] or ctrl==None:
            continue

        pm25data=0
        pm10data=0
        for data in lst:
            if data["name"]=="PM2.5": #读取数据
                pm25data=data["data"]
            elif data["name"]=="PM10":
                pm10data=data["data"]

        list25 = list25 + [pm25data] #删除5min前的数据
        del list25[0]
        list10 = list10 + [pm10data]
        del list10[0]

        #控制逻辑
	if ctrl["value"]!=prevalue:
            t__=0
        if ctrl["value"]==1: #收到打开信号就打开
            stat=open()
        elif ctrl["value"]==-1: #收到关闭信号
            stat=shutdown()
        elif ctrl["value"]==0: #收到自动控制信号 经过checktime检查一次，与threshold比较，决定开关
            if t__%checktime == 0:
                if pm25data < threshold:
                    stat = shutdown()+2 #2为关 3为开
                else:
                    stat = open()+2
        #print stat
        prevalue=ctrl["value"]

	#开机有效性分析
        avg_25_init = 0
        if t_==10 : #记录开机时空气质量
            for i in range(10):
                avg_25_init = avg_25_init + list25[50+i]
            avg_25_init = avg_25_init / 10.0
        avg_25_check = 0
        if t_ >=10 :
            for i in range(10):
                avg_25_check = avg_25_check + list25[50+i] #读取最新10个空气质量平均值
            avg_25_check = avg_25_check / 10.0
            if avg_25_check < avg_25_init * (1 - th_per_25):# 如果有效下降，则有效
                normal=1
            else:
                normal=0
	
	#火警
        avg_10_pre=0 #最新5组数据平均值
        avg_10_new=0 #前5组数据平均值
        for i in range(5):
            avg_10_pre = avg_10_pre + list10[50+i]
            avg_10_new = avg_10_new + list10[55+i]
        avg_10_pre = avg_10_pre / 10.0
        avg_10_new = avg_10_new / 10.0
	#pm10大于绝对限度或者上升过快且大于某个限度 则报警
        if pm10data>th_fire_abs or ((avg_10_new > avg_10_pre * th_times_fire) and (avg_10_new > th_fire)) :
            raiseFireAlarm() #报火警

        threadLock.acquire()
        status=stat
        threadLock.release()
        time.sleep(5) #每隔5s刷新一次数据


if __name__ == '__main__':
    load_sensors()

    thread.start_new_thread(fetchdata, ())
    thread.start_new_thread(communicate, ())
    analyzeandcontrol()