# -*- coding: utf-8 -*-
from pathlib import Path
import configparser
import pickle

CONFIG_PATH = Path('./users_data/config.ini')

class Config(object):

    def __init__(self, config_path):
        self.config = configparser.ConfigParser()
        self.config_path = config_path
        # 第一次创建user_data
        if not self.config_path.exists():
            if not config_path.parent.exists():
                config_path.parent.mkdir(parents=True,exist_ok=False)
                (config_path.parent / 'cookies').mkdir(parents=True,exist_ok=False)
            self.config.write(open(self.config_path,'w',encoding='utf-8'))
        else:
            self.config.read(self.config_path, encoding='utf-8')

    def get(self, section, option):
        if self.config.has_section(section): # 老用户
            s = self.config.get(section, option)
            s = s.strip() # 剥离空白字符
            s = s.strip('"').strip("'")# 剥离'' ""
            return s
        else: # 新用户，赋初值
            return ''

    def getboolean(self, section, name):
        return self.config.getboolean(section, name)

    def add_user(self, section, nick_name:str='', cookie_path:str='', area_id:str='', eid:str='', fp:str=''):
        if self.config.has_section(section):
            return False # 添加用户失败
        self.config.add_section(section)
        self.config.set(section, 'nick_name', nick_name)
        self.config.set(section, 'cookie_path', cookie_path)
        self.config.set(section, 'area_id', area_id)
        self.config.set(section, 'eid', eid)
        self.config.set(section, 'fp', fp)
        self.config.write(open(self.config_path,'w',encoding='utf-8'))
        return True

global_config = Config(CONFIG_PATH)

if __name__ == "__main__":
    cookie_path = global_config.get('张佳伟大号', 'cookie_path')
    with open(cookie_path, 'rb') as f:
        local_cookies = pickle.load(f)
        print(local_cookies)
        for k,v in local_cookies.items():
            print(k, v)

