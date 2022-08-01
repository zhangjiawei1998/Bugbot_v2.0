# -*- coding:utf-8 -*-
import time
import requests
from datetime import datetime, timedelta

class Timer(object):
    def __init__(self):
        super().__init__()
        
    def get_jd_time(self):
        """返回京东服务器时间

        Returns:
            <class 'datetime.datetime'> : 2022-05-08 15:31:18.030000
        """
        resp = requests.get(url='https://api.m.jd.com/client.action?functionId=queryMaterialProducts&client=wh5',
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'})
        resp_json = resp.json()
        timeStamp = float(resp_json['currentTime2']) / 1000
        jd_time = datetime.utcfromtimestamp(timeStamp) + timedelta(hours=8)
        return jd_time 
    
    def get_local_time(self):
        """ 返回本机时间

        Returns:
            <class 'datetime.datetime'> : 2022-05-08 15:31:18.030000
        """
        return datetime.now()
    
    def get_time_diff(self):
        """ 计算本地与京东服务器时间差
            这个时间差包含了 一次请求时间 + 时间戳差
        Returns:
            <class 'datetime.timedelta'> : 0:00:00.129237
        """
        a = self.get_local_time()
        b = self.get_jd_time()
        time_diff = a - b
        if time_diff < timedelta(0):
            pass #self.loggerSignal.emit(f'提前{b-a}下单')
        else:
            pass #self.loggerSignal.emit(f'延后{time_diff}下单')
            
        return time_diff
    
    def wait_for_time(self, buy_time: str, time_sleep: float=0.01):
        # '2018-09-28 22:45:50.000'
        # time_diff = self.get_time_diff()
        buy_time = datetime.strptime(buy_time, "%Y-%m-%d %H:%M:%S.%f")
        #s elf.loggerSignal.emit(f'正在等待到达设定时间:{buy_time}')
        while True:
            # self.loggerSignal.emit('等待ing')
            if datetime.now() >= buy_time:
                # self.loggerSignal.emit('时间到达，开始执行……')
                break
            else:
                time.sleep(time_sleep)