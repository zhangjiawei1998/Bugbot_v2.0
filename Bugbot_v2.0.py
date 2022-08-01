from multiprocessing import Process, Manager, Lock
import psutil

import sys
from datetime import datetime
import json
import pickle
import re
import random
import time
from pathlib import Path

# html module
import requests
from bs4 import BeautifulSoup
# pyqt5 module
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
# ui module
from ui.Ui_add_items import Ui_add_items
from ui.Ui_login_qrcode import Ui_login_qrcode
from ui.Ui_oneUser import Ui_USER
# scripts module
from scripts.NotPusher import pusher
from scripts.config import global_config
from scripts.log import logger
from scripts.util import (
    random_USER_AGENTS,
    url_encode,
    add_url_params,
    deprecated,
    parse_json,
    save_image,
)


"""
    商品组信息
    seckill_group = [ {'10313203232':[2, '欧文42'], '2131321312':[1, '凑单']}, {...}, ...]
    if_seckill    = [  'yes','yes','no'....]
    
"""
# QRcode界面
class ui_loginQRcode(QWidget, Ui_login_qrcode):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

# 商品添加界面
class add_items(QWidget, Ui_add_items):
    getItemSignal = pyqtSignal(dict)
    def __init__(self) -> None:
        super().__init__()
        # 初始化
        self.setupUi(self)
        self.pushButton_get_items.clicked.connect(self.get_items_info)
        
    def _logger(self, msg:str):
        '''
            用于向gui界面输出日志信息
            
        Params
        ------
            msg: 日志信息str
        '''
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') # 含微秒的日期时间
        self.textBrowser.append(f'【{now[:-4]}】 : {msg}')
        
    def get_items_info(self):
        '''
            <获取商品>按钮
        '''
        # 获取 一组抢购商品
        lineEdit_items_id   = [self.lineEdit_item_id1,   self.lineEdit_item_id2,   self.lineEdit_item_id3,   self.lineEdit_item_id4]    # 商品编号输入
        lineEdit_items_name = [self.lineEdit_item_name1, self.lineEdit_item_name2, self.lineEdit_item_name3, self.lineEdit_item_name4]  # 商品简称输入
        spinBox_items_count = [self.spinBox_item_count1, self.spinBox_item_count2, self.spinBox_item_count3, self.spinBox_item_count4]  # 购买数量输入
        
        seckill_info = dict()
        for id, name, count in zip(lineEdit_items_id, lineEdit_items_name, spinBox_items_count):
            if id.text() != '':
                if id.text() in seckill_info.keys(): # 商品id不能重复 
                    self._logger('商品不能重复')
                    self.resetUi()
                    return
                if count.value() == 0: #数量不能为0
                    self._logger('商品数量不能为0')
                    self.resetUi()
                    return
                seckill_info[id.text()] = [count.value(), name.text()]
        
        # 获取库存查询间隔, 单位/秒
        #self.stock_interval = self.spinBox_interval.value() / 1000
        
        # 如果没有商品信息
        if not seckill_info:
            self.resetUi()
            self._logger('请输入你要抢购的商品')
            return
        self._logger('获取抢购商品:' + str(seckill_info))
        self.getItemSignal.emit(seckill_info)
   
    def resetUi(self):
        lineEdit_items_id    = [self.lineEdit_item_id1,   self.lineEdit_item_id2,   self.lineEdit_item_id3,   self.lineEdit_item_id4]    # 商品编号输入
        lineEdit_items_name  = [self.lineEdit_item_name1, self.lineEdit_item_name2, self.lineEdit_item_name3, self.lineEdit_item_name4]  # 商品简称输入
        spinBox_items_count  = [self.spinBox_item_count1, self.spinBox_item_count2, self.spinBox_item_count3, self.spinBox_item_count4]  # 购买数量输入
        for id, name, count in zip(lineEdit_items_id, lineEdit_items_name, spinBox_items_count):
            id.clear()
            name.clear()
            count.setValue(0)
            
    def get_coupon(self):
        '''
            <一键领券>按钮
            暂未实现
        '''

# 用户 + 网页会话
class User(QThread):
    QRcodeSignal = pyqtSignal(str)
    loggerSignal = pyqtSignal(str)
    SuccessSignal = pyqtSignal()
    def __init__(self, username:str, is_new_user:bool=False) -> None:
        super(User, self).__init__()
        # 用户信息 类型都是str
        self.is_new_user = is_new_user # 是不是新用户
        self.username    = username
        self.nick_name   = ''                   if is_new_user else global_config.get(username, 'nick_name')  # 用户昵称
        self.cookie_path = ''                   if is_new_user else global_config.get(username, 'cookie_path')# cookie地址
        self.area_id     = '15_1213_3038_59931' if is_new_user else global_config.get(username, 'area_id')    # 默认地区西湖区，该参数只为查询库存
        self.eid         = ''                   if is_new_user else global_config.get(username, 'eid')        # 似乎不需要
        self.fp          = ''                   if is_new_user else global_config.get(username, 'fp')         # 似乎不需要
        # self.send_message = global_config.getboolean('messenger', 'enable')
        # self.messenger    = Messenger(global_config.get('messenger', 'sckey')) if self.send_message else None
        
        # 会话信息
        self.user_agent = random_USER_AGENTS
        self.sess = requests.session()
        # self.sess.proxies = {'https':'120.42.46.226:6666'}
        self.sess.keep_alive = False
        self.is_login = False

    def aotuLogin(self):
        with open(self.cookie_path, 'rb') as f:
            local_cookies = pickle.load(f)
        self.sess.cookies.update(local_cookies)
        
        # 验证cookies是否有效
        if self.validate_cookies():
            self.is_login = True
            return True
        else:
            self.loggerSignal.emit('cookie验证失败,大概率是过期了')

    def validate_cookies(self):
        """验证cookies是否有效(是否登陆)
            通过访问用户订单列表页进行判断：若未登录，将会重定向到登陆页面。
        
        Return
        ------
            True/False cookies是否有效
        """
        url = 'https://order.jd.com/center/list.action'
        payload = {
            'rid': str(int(time.time() * 1000)),
        }
        try:
            resp = self.sess.get(url=url, params=payload, allow_redirects=False)
            if resp.status_code == requests.codes.OK:
                return True
        except Exception as e:
            self.loggerSignal.emit(e)

        self.sess = requests.session()
        return False

    def save_cookies(self):
        self.cookie_path = f'./users_data/cookies/{self.nick_name}.cookies'
        if not Path(self.cookie_path).parent.exists():
            Path(self.cookie_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.cookie_path, 'wb') as f:
            pickle.dump(self.sess.cookies, f)

    def get_login_page(self):
        url = "https://passport.jd.com/new/login.aspx"
        headers={
            'User-Agent': self.user_agent
        }
        page = self.sess.get(url, headers=headers)
        return page

    def get_QRcode(self):
        url = 'https://qr.m.jd.com/show'
        payload = {
            'appid': 133, # 固定值
            'size': 147,  # 二维码尺寸
            't': str(int(time.time() * 1000)),
        }
        headers = {
            'User-Agent': self.user_agent,
            'Referer': 'https://passport.jd.com/new/login.aspx',
        }
        resp = self.sess.get(url=url, headers=headers, params=payload)
        
        if resp.status_code != requests.codes.OK: # OK = [200]
            self.loggerSignal.emit(f'Status: {resp.status_code}, Url: {resp.url}, 获取二维码失败')
            return False

        save_image(resp, './users_data/QRcode.png')
        self.loggerSignal.emit('二维码获取成功, 请打开京东APP扫描')
        return True

    def get_QRcode_ticket(self):
        url = 'https://qr.m.jd.com/check'
        payload = {
            'appid': '133',
            'callback': 'jQuery{}'.format(random.randint(1000000, 9999999)),
            'token': self.sess.cookies.get('wlfstk_smdl'),
            '_': str(int(time.time() * 1000)),
        }
        headers = {
            'User-Agent': self.user_agent,
            'Referer': 'https://passport.jd.com/new/login.aspx',
        }
        resp = self.sess.get(url=url, headers=headers, params=payload)

        if resp.status_code != requests.codes.OK: # OK = [200]
            self.loggerSignal.emit('Status: {0}, Url: {1}, 获取二维码扫描结果异常'.format(resp.status_code, resp.url))
            return False

        resp_json = parse_json(resp.text)
        if resp_json['code'] != 200:
            self.loggerSignal.emit('Code: {0}, Message: {1}'.format(resp_json['code'], resp_json['msg']))
            return None
        else:
            self.loggerSignal.emit('已完成手机客户端确认')
            return resp_json['ticket']

    def validate_QRcode_ticket(self, ticket):
        url = 'https://passport.jd.com/uc/qrCodeTicketValidation'
        headers = {
            'User-Agent': self.user_agent,
            'Referer': 'https://passport.jd.com/uc/login?ltype=logout',
        }
        payload = {
            't': ticket
        }
        resp = self.sess.get(url=url, headers=headers, params=payload)
        # 验证完一次ticket, 需要关闭连接, 避免报错: error[Max retries exceeded with url: /uc/qrCodeTicketValidation?t=AA...]
        if resp.status_code != requests.codes.OK: # OK = [200]
            self.loggerSignal.emit('Status: %u, Url: %s' % (resp.status_code, resp.url))
            resp.close() 
            return False

        resp_json = json.loads(resp.text)
        if resp_json['returnCode'] == 0:
            resp.close()
            return True
        else:
            self.loggerSignal.emit(resp_json)
            resp.close()
            return False

    def login_by_QRcode(self):
        """
            二维码登陆
        """
        self.get_login_page()
        
        # download QR code and show 
        if not self.get_QRcode():
            self.loggerSignal.emit('二维码下载失败')
            return False
        else:
            self.QRcodeSignal.emit('./users_data/QRcode.png') # 窗口显示登录二维码
        requests.Session
        # get QR code ticket
        ticket = None
        for _ in range(85): # 二维码有效时间大概3分钟
            ticket = self.get_QRcode_ticket()
            if ticket:
                break
            time.sleep(2)
        else:
            self.loggerSignal.emit('二维码过期，请重新获取扫描')
            return False

        # validate QR code ticket
        if not self.validate_QRcode_ticket(ticket):
            self.loggerSignal.emit('二维码信息校验失败')
            return False
        else:
            self.loggerSignal.emit('二维码登录成功')
            self.is_login = True
            return True

    def get_user_info(self):
        """
            获取用户信息
        
        Returns
        -------
            用户名
        """
        url = 'https://passport.jd.com/user/petName/getUserInfoForMiniJd.action'
        payload = {
            'callback': 'jQuery{}'.format(random.randint(1000000, 9999999)),
            '_': str(int(time.time() * 1000)),
        }
        headers = {
            'User-Agent': self.user_agent,
            'Referer': 'https://order.jd.com/center/list.action',
        }
        try:
            resp = self.sess.get(url=url, params=payload, headers=headers)
            resp_json = parse_json(resp.text)
            # many user info are included in response, now return nick name in it
            # jQuery2381773({"imgUrl":"//storage.360buyimg.com/i.imageUpload/xxx.jpg","lastLoginTime":"","nickName":"xxx","plusStatus":"0","realName":"xxx","userLevel":x,"userScoreVO":{"accountScore":xx,"activityScore":xx,"consumptionScore":xxxxx,"default":false,"financeScore":xxx,"pin":"xxx","riskScore":x,"totalScore":xxxxx}})
            return resp_json.get('nickName') or 'jd'
        except Exception:
            return 'jd'

    def login(self):
        '''
            用户登录
            
            if 存在用户cookie
                获取cookies自动登录
            else
                扫码登陆
        '''
        # 老用户尝试使用cookies自动登录
        try:
            if self.aotuLogin():
                self.loggerSignal.emit(f'用户:{self.nick_name} 自动登录成功')
                self.SuccessSignal.emit()
                return
        except Exception as e:
            pass
        # 老用户cookies失效 或者 新用户
        # 扫码登陆
        if self.login_by_QRcode():
            self.nick_name = self.get_user_info() 
            self.save_cookies()
            self.loggerSignal.emit(f'用户:{self.nick_name} 扫码登录成功')
            self.SuccessSignal.emit()
            
        # 已登录新用户 获取信息并添加到config.ini里
        if self.is_new_user and self.is_login:
            global_config.add_user(self.username, self.nick_name, self.cookie_path, self.area_id, self.eid, self.fp)

    def run(self):
        self.login()

# 主界面 ui
class Bugbot(QWidget, Ui_USER):
    loggerSignal = pyqtSignal(str)
    statusSignal = pyqtSignal(str, int)
    def __init__(self, username, is_new_user:bool=False) -> None:
        super().__init__()
        # 初始化ui
        self.setupUi(self)                # 主界面
        self.ui_add_items = add_items()   # 商品添加界面
        self.ui_QRcode = ui_loginQRcode() # QRcode界面

        # 创建一个QThread User(), 用于和Jd服务器建立session
        self.user = User(username, is_new_user)
        self.user.start() # 开启用户登录线程
        
        # 优先抢购记录
        self.priority_record = 0
        
        self.seckill_process = ''
        self.monitor_process = ''
        # 创建一个Bugbot_logic, 用于多进程抢购
        self.Bugbot_logic = ''
        self.read_log = ''
        # 初始化抢购信息
        self.seckill_group = ''
        self.if_seckill    = ''
        # 日志信息
        self.loginfo       = ''

        self.connect()
        
    #---------------------登录模块-----------------------------
    def login_success(self):
        self.label_nickname.setText(self.user.nick_name)
        self.ui_QRcode.close()
        self.Btn_login.setEnabled(False)
        try:
            self.init_bugbot_logic()
        except Exception as e:
            self.loggerSignal.emit(f'Bugbot初始化错误, error: {e}')
        else:
            self.loggerSignal.emit('Bugbot初始化完毕')
        
    def show_QRcode(self, filename: str):
        '''创建ui显示QRcode'''
        self.ui_QRcode.label_qrcode.setPixmap(QPixmap(filename))
        self.ui_QRcode.label_qrcode.setScaledContents (True) # 自适应大小
        self.ui_QRcode.show()

    #---------------------功能模块-----------------------------
    def connect(self):
        self.dateEdit.setDate(QDate.currentDate())
        # 允许tableWidget弹出菜单
        self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableWidget.customContextMenuRequested.connect(self.generateMenu)
        # 禁止编辑
        # self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # Bugbot()信号
        self.Btn_login.clicked.connect(self.user.start)
        self.Btn_addSeckillInfo.clicked.connect(self.ui_add_items.show) # 添加按钮 --> 打开添加商品界面
        self.Btn_startSeckill.clicked.connect(self.process_start) # 执行抢购按钮
        self.Btn_stopSeckill.clicked.connect(self.process_suspend_or_resume)
        self.Btn_importSeckillInfo.clicked.connect(self.import_or_export_seckill_info)
        self.Btn_exportSeckillInfo.clicked.connect(self.import_or_export_seckill_info)
        self.loggerSignal.connect(self._logger)
        self.statusSignal.connect(self._logger)
        # add_items()信号
        self.ui_add_items.getItemSignal.connect(self.add_seckill_info)# getItemSignal信号 --> 添加一组秒杀信息
        # User() 信号
        self.user.QRcodeSignal.connect(self.show_QRcode)
        self.user.loggerSignal.connect(self._logger)
        self.user.SuccessSignal.connect(self.login_success)
    
    def _logger(self, msg: str, group_id: int=None):
        '''
            用于向gui界面输出日志信息
        '''
        sender = self.sender()
        if sender == self.read_log:
            self.textBrowser.append(msg)
        else:
            if group_id == None:
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') # 含微秒的日期时间
                self.textBrowser.append(f'【{now[:-4]}】 : {msg}')
            else:
                self.tableWidget.setItem(group_id, 4, QTableWidgetItem(msg))
        
    def generateMenu(self, pos):
        """
            QTableWidget 右键菜单

            Params:
                pos (int): 传入的鼠标postion
        """
        # 通过迭代器获取当前选中的行数的索引
        for i in self.tableWidget.selectionModel().selection().indexes():
            rowNum = i.row()
            
        print(len(self.seckill_group), rowNum)
        if len(self.seckill_group) <= rowNum:
            return

        menu = QMenu()
        item1 = menu.addAction("删除该组商品")
        item2 = menu.addAction('取消屏蔽') if self.if_seckill[rowNum] == 'no' else menu.addAction('屏蔽该组商品')
        item3 = menu.addAction('优先抢购')
        item4 = menu.addAction('↑ ↑ ↑')
        item5 = menu.addAction('↓ ↓ ↓')
        # 坐标转换(将主窗口坐标系中的坐标映射到屏幕坐标系)
        screenPos = self.tableWidget.mapToGlobal(pos)
        # 阻塞, 等待选择
        action = menu.exec_(screenPos) 
        if action == item1:
            self.seckill_group.pop(rowNum)
            self.if_seckill.pop(rowNum)
            self.update_tableWidget()
        if action == item2:
            self.if_seckill[rowNum] = 'no' if self.if_seckill[rowNum]=='yes' else 'yes'
            self.update_tableWidget()
        if action == item3:
            try:
                if rowNum < self.priority_record:
                    # 重置 self.priority_record
                    self.loggerSignal.emit(f'抢购优先级已经重置')
                    self.priority_record = 0
                self.seckill_group.insert(self.priority_record, self.seckill_group.pop(rowNum))
                self.if_seckill.insert(self.priority_record, self.if_seckill.pop(rowNum))
                self.priority_record += 1
                self.update_tableWidget()
            except Exception as e:
                self.loggerSignal.emit(f'抢购优先级改变失败, error: {e}')
            
        if action == item4 and rowNum != 0:# 不为第一行
            self.seckill_group[rowNum-1], self.seckill_group[rowNum] = self.seckill_group[rowNum], self.seckill_group[rowNum-1]
            self.if_seckill[rowNum-1], self.if_seckill[rowNum] = self.if_seckill[rowNum], self.if_seckill[rowNum-1]
            self.update_tableWidget()
        
        if action == item5 and rowNum != (len(self.seckill_group)-1):# 不为最后一行
            self.seckill_group[rowNum], self.seckill_group[rowNum+1] = self.seckill_group[rowNum+1], self.seckill_group[rowNum]
            self.if_seckill[rowNum], self.if_seckill[rowNum+1] = self.if_seckill[rowNum+1], self.if_seckill[rowNum]
            self.update_tableWidget()

    def add_seckill_info(self, seckill_info):
        """向Bugbot添加一组秒杀信息 并在tablewidget中显示信息

        Args:
            seckill_info (dict): 一组秒杀信息
        """
        self.seckill_group.append(seckill_info)
        self.if_seckill.append('yes')
        self.update_tableWidget()
     
    def update_tableWidget(self):
        """
            根据self.seckill_group和self.if_seckill来更新tableWidget
        """
        self.tableWidget.clearContents()
        for group_id, seckill_info in enumerate(self.seckill_group):
            names = ''
            ids   = ''
            numbers = ''
            for id, info in seckill_info.items():
                ids += id + '\n'
                names += info[1] + '\n'
                numbers += 'x' + str(info[0]) + '\n'
            
            # 抢购优先级
            if group_id < self.priority_record:
                newItem = QTableWidgetItem(str(group_id))
                newItem.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter|Qt.AlignCenter)
                self.tableWidget.setItem(group_id, 5, newItem)
            # ① 正常抢购
            list_row = [str(group_id), names.rstrip('\n'), ids.rstrip('\n'), numbers.rstrip('\n'), '正常抢购']
            qcolor = QColor(255,255,255,255)# 白色
            # ② 屏蔽, 暂时不想抢购
            if self.if_seckill[group_id] == 'no':
                list_row = [str(group_id), names.rstrip('\n'), ids.rstrip('\n'), numbers.rstrip('\n'), '已屏蔽']
                qcolor = QColor(152,153,115,255)# 深褐色
            # 填充一行tableWidght
            for i, content in enumerate(list_row):
                newItem = QTableWidgetItem(content)
                newItem.setBackground(qcolor)
                newItem.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter|Qt.AlignCenter)
                self.tableWidget.setItem(group_id, i, newItem)
            
            self.tableWidget.resizeColumnsToContents()# 自适应内容大小
            self.tableWidget.resizeRowsToContents()   # 自适应内容大小
            self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # 自适应列宽大小
        
    def import_or_export_seckill_info(self):
        sender = self.sender()
        if sender == self.Btn_importSeckillInfo:
            text, ok = QInputDialog.getMultiLineText(self, 'import Seckill info', '请输入')
            if ok:
                try:
                    text = text.replace('\'','\"')  # str替换 '0': -> "0":
                    match = re.match(r'(.*)___(.*)___(.*)', text)
                    for _ in range(len(self.seckill_group)):
                        self.seckill_group.pop(0)
                        self.if_seckill.pop(0)
                    # 信息1
                    for x in json.loads(match.group(1)):
                        self.seckill_group.append(x)
                    # 信息2
                    for x in json.loads(match.group(2)):
                        self.if_seckill.append(x)
                    # 信息3
                    self.priority_record = int(match.group(3))
                except Exception as e:
                    self.loggerSignal.emit(f'商品信息导入失败, 商品简称中请不要携带 \' _ \" 等字符, error:{e}')
                else:
                    self.update_tableWidget()
                    self.loggerSignal.emit('商品信息导入成功')
                    
        if sender == self.Btn_exportSeckillInfo:
            text, ok = QInputDialog.getMultiLineText(self, 'export Seckill info', '请复制', str(self.seckill_group) + '___' + str(self.if_seckill) + '___' + str(self.priority_record))

    def get_buy_time(self):
        # 获取下单时间
        buy_time = ''
        buy_date = self.dateEdit.date().toString("yyyy-MM-dd")
        year, month, day = int(buy_date[0:4]), int(buy_date[5:7]), int(buy_date[8:10])
        hour, minute, second, ahead_milsec = self.spinBox_hour.value(), self.spinBox_min.value(), self.spinBox_sec.value(), self.spinBox_milsec.value()
        if ahead_milsec > 0:
            if second > 0:   # 找秒借         20:30:05 提前200毫秒 -> 20:30:04.800
                buy_time = f'{year}-{month}-{day} {hour}:{minute}:{second-1}.{1000-ahead_milsec}'
            elif minute > 0: # 秒不够，找分借  20:30:00 提前200毫秒 -> 20:29:59.800
                buy_time = f'{year}-{month}-{day} {hour}:{minute-1}:{59}.{1000-ahead_milsec}'
            elif hour > 0:   # 分不够，找时借  20:00:00 提前200毫秒 -> 19:59:59.800
                buy_time = f'{year}-{month}-{day} {hour-1}:{59}:{59}.{1000-ahead_milsec}'
            elif day > 1 :    # 时不够，找天借             2021-08-16 00:00:00 提前200毫秒 -> 2021-08-15 23:59:59.800
                buy_time = f'{year}-{month}-{day-1} {23}:{59}:{59}.{1000-ahead_milsec}'
            # 年和月先不管了
            else:
                buy_time = f'{year}-{month}-{day} {hour}:{minute}:{second}.000000'
        else:
            buy_time = f'{year}-{month}-{day} {hour}:{minute}:{second}.000000'

        return buy_time # <str> 2021-08-15 23:59:59.800

    def init_bugbot_logic(self):
        # 初始化bugbot_logic， 大概需要3秒
        self.Bugbot_logic = Bugbot_logic(session=self.user.sess,
                                         username= self.user.username,
                                         user_agent=self.user.user_agent,
                                         area_id=self.user.area_id,
                                         eid = self.user.eid,
                                         fp = self.user.fp)
        
        # 初始化log读取线程: 从共享堆内存self.Bugbot_logic.loginfo中读取
        self.read_log = read_loginfo(self.Bugbot_logic.loginfo)
        self.read_log.loggerSignal.connect(self._logger)

        # 共享内存
        self.seckill_group  = self.Bugbot_logic.seckill_group
        self.if_seckill     = self.Bugbot_logic.if_seckill
        self.loginfo        = self.Bugbot_logic.loginfo
        
    def process_start(self):
        """
            开启抢购线程
        """
        # 购买时间赋值
        self.Bugbot_logic.buy_time = self.get_buy_time()
        
        # 开启log读取线程
        self.read_log.start()
        
        # 普通抢购模式
        if self.radioButton.isChecked() == False:
            seckill_process = Process(target=self.Bugbot_logic.seckill)
            monitor_process = Process(target=self.Bugbot_logic.monitor)
            seckill_process.start()
            monitor_process.start()
            self.seckill_process = psutil.Process(seckill_process.pid)
            self.monitor_process = psutil.Process(monitor_process.pid)
        # 预约抢购模式
        else:
            seckill_process = Process(target=self.seckill_reserve)
            seckill_process.start()
            
            self.seckill_process = psutil.Process(seckill_process.pid)
            
        # 抢购按钮禁止，防止多次创建进程，导致内存泄露
        self.Btn_startSeckill.setEnabled(False)
            
    def process_suspend_or_resume(self):
        """
            暂停或恢复抢购进程
        """
        if self.Btn_stopSeckill.text() == '停止抢购':
            try:
                if self.radioButton.isChecked() == False: # 普通抢购
                    self.seckill_process.suspend()
                    self.seckill_process.suspend()
                    self.loggerSignal.emit('已暂停抢购')
                else:
                    self.seckill_process.suspend()
                    self.loggerSignal.emit('已暂停预约抢购')
            except Exception as e:
                self.loggerSignal.emit(f'暂停抢购失败, error:{e}')
            finally:
                self.Btn_stopSeckill.setText('恢复抢购')
                
        elif self.Btn_stopSeckill.text() == '恢复抢购':
            try:
                if self.radioButton.isChecked() == False: # 普通抢购
                    self.seckill_process.resume()
                    self.seckill_process.resume()
                    self.loggerSignal.emit('已恢复抢购')
                else:
                    self.seckill_process.resume()
                    self.loggerSignal.emit('已恢复预约抢购')
            except Exception as e:
                self.loggerSignal.emit(f'恢复抢购失败, error:{e}')
            finally:
                self.Btn_stopSeckill.setText('停止抢购')

# 逻辑
class Bugbot_logic(object):
    def __init__(self, session, username:str, user_agent:str, area_id:str, eid:str, fp:str) -> None:
        self.sess = session
        self.user_agent = user_agent
        self.area_id = area_id
        self.eid = eid
        self.fp = fp
    
        self.username = username
        self.buy_time = ''
        
        self.lock = Lock() # 抢购进程和监控进程的lock
        m = Manager()
        # 秒杀信息列表
        self.seckill_group = m.list()
        self.if_seckill    = m.list()
        # 监视库存列表
        self.monitor_items = m.list()
        # 日志信息
        self.loginfo       = m.list()
        # 购物车信息 
        self.cart_info = dict()
        
    def log(self, msg:str):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') # 含微秒的日期时间
        self.loginfo.append(f'【{now[:-4]}】 : {msg}')

    def wait_for_time(self, buy_time: str, time_sleep: float=0.01):
        # buy_time: '2018-09-28 22:45:50.000'
        try:
            buy_time = datetime.strptime(buy_time, "%Y-%m-%d %H:%M:%S.%f")
            self.log(f'正在等待到达设定时间:{buy_time}')
            while True:
                if datetime.now() >= buy_time:
                    self.log('时间到达，开始抢购......')
                    return
                else:
                    time.sleep(time_sleep)
        except:
            pass

    def seckill(self):
        # 等待抢购的到来
        self.wait_for_time(self.buy_time, time_sleep=0.5)
        
        # 开始抢购
        while True:
            self.cart_info = self.cancel_select_all_cart_item()
            group_id = self.if_can_ordered()# 哪一组可以下单
            if group_id != -1:
                self.lock.acquire() # 嗦住! 防止内存混乱
                if self.change_cart_item(group_id): # 成功勾选商品
                    self.get_order_info(group_id)# 获取订单信息
                    self.submit_order(group_id) # 提交订单
                self.lock.release()
            time.sleep(2)
            
    def cancel_select_all_cart_item(self):
        """
            取消勾选购物车中的所有商品
            并且返回购物车信息
        Returns
        -------
            cart_info 购物车信息
        """
        url =  'https://api.m.jd.com/api'
        header = {
            'Host':       'api.m.jd.com',
            'Accept':     'application/json, text/plain, */*',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': self.user_agent,
            'Origin': 'https://cart.jd.com',
            'Referer':   'https://cart.jd.com/'
            
        }
        body = dict(
            serInfo = {
                'area':self.area_id,
                'user-key':' '
            }
        )
        payload = dict(
            functionId= 'pcCart_jc_cartUnCheckAll',
            appid     ='JDC_mall_cart',
            loginType = 3,
            body      = url_encode(body)
        )
        url_with_params = add_url_params(url, payload)
        resp_json = self.sess.post(url=url_with_params, headers=header).json()
        
        cart_info = dict()
        try:
            for vendor in resp_json['resultData']['cartInfo']['vendors']: # for every vendor in cart
                for item_info in vendor['sorted']: # for every item in vendor
                    try:
                        item = item_info['item']
                        # 另外一种购物车信息格式
                        if 'skuUuid' not in item:
                            item = item['items'][0]['item']
                            
                        cart_info[item['Id']] = {
                            'verder_id':    vendor['vendorId'],            # str 商家id
                            'name':         item['unitedText'],            # str 商品 货号+尺码 "EG4958/偏大半码，39"
                            'skuUuid':      item['skuUuid'],               # 用于购物车勾选操作
                            'useUuid':      item['useUuid'],               # 用于购物车勾选操作
                            'num':          item['Num'],                   # int 数量
                            'stockStateId': item['stock']['stockStateId'], # int 商品库存状态：33 -- 现货  0,34 -- 无货  36 -- 采购中  40 -- 可配货
                            'stockCode':    item['stock']['stockCode'],    # int 商品是否上架 猜测：0有货， 1无货
                            'price':        item['Price'],                 # int 原价   799
                            'priceShow':    item['PriceShow'],             # str 现价  "￥574.00" 
                            'checkType':    item['CheckType'],             # int 商品是否被勾选   1:已被勾选，0:未被勾选
                            'isNoCheck':    item['isNoCheck'],             # int 商品是否能被勾选  1:不能，   0:能
                            'targetId':     item['targetId'],              # int ?
                            'promo_id':     item['targetId']               # int ?
                        }
                    
                    except Exception as e:
                        logger.info(f"购物车信息解析错误 error={e} item={item}")
        except Exception as e:
            self.log(f"购物车返回信息错误({resp_json})")
        return cart_info

    def if_can_ordered(self): 
        '''
            主要有2个功能:
            1. 比较cart_info和seckill_group, 满足以下条件即可下单:
                  一组商品的 isNoCheck == 0(商品可勾选), 即有库存
            2. 如果有一个商品不在购物车里, 则将其加入self.monitor_items列表, 进行库存监控(另外一个进程实现)
            
            Return
            ------
                可以下单: group_id in [0, n]
                不能下单: -1
        '''
        
        for group_id, seckill_info in enumerate(self.seckill_group): # for one group in groups
            if self.if_seckill[group_id] == 'no': # 该组被屏蔽
                break
            flag = True 
            for item_id in seckill_info.keys(): # for item in one group
                # 购物车里没有抢购商品, 将该组商品加入self.monitor_items列表, 进行库存监控
                if item_id not in self.cart_info.keys():
                    flag = False
                    if item_id not in self.monitor_items:  # 防止重复库存监控
                        self.monitor_items.append(item_id)
                    continue
                # 一组中有一个商品不能勾选, 则判断下一个
                if self.cart_info[item_id]['isNoCheck'] != 0: 
                    flag = False
            # 符合下单条件
            if flag:
                self.log(f'第{group_id}组商品尝试下单')
                return group_id # 第几组可以下单`
    
        return -1
    
    def change_cart_item(self, group_id: int):
        """根据group_id更改购物车中商品数量,更改完的商品会自动勾选

        Args:
            group_id (int): 商品组别

        Returns:
            Ture/False: 是否勾选成功
        """
        url =  'https://api.m.jd.com/api'
        headers = {
            'Host':         'api.m.jd.com',
            'Accept':       'application/json, text/plain, */*',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent':   self.user_agent,
            'Origin':       'https://cart.jd.com',
            'Referer':      'https://cart.jd.com/'
            
        }
        body = dict(
            operations= [{
                "ThePacks": [],
                "TheSkus":  [],
                "carttype": "5"
            }],
            serInfo = {
                'area':     self.area_id,
                'user-key': ' '
            }
        )
        # 根据group_id从self.seckill_group获得需要勾选的商品信息, 放到body里
        total_num = 0 
        for item_id, item_info in self.seckill_group[group_id].items():
            TheSku = dict(
                Id=item_id,
                num=item_info[0],
                skuUuid=self.cart_info[item_id]['skuUuid'],
                useUuid=self.cart_info[item_id]['useUuid']
            )
            total_num += item_info[0]
            body['operations'][0]['TheSkus'].append(TheSku)
            
        payload = dict(
            functionId= 'pcCart_jc_changeSkuNum',
            appid     = 'JDC_mall_cart',
            loginType = 3,
            body      = url_encode(body)
        )
        url_with_params = add_url_params(url, payload)
        resp_json = self.sess.post(url=url_with_params, headers=headers).json()
       
        # 普通抢购模式: 是否更改成功, 比较total_num和购物车已勾选的商品数量 [maybe]
        if resp_json['resultData']['cartInfo']['checkedWareNum'] == total_num:
            self.log(f'第{group_id}组勾选成功')
            return True
        else:
            self.log(f'第{group_id}组勾选失败')
            return False
            
    def get_order_info(self, group_id: int):
        """
            请求订单页面信息, 可以理解成点击 购物车<去结算> 按钮,
            这会将session的cookies 替换/增加三个参数:
            1. 替换 Name=JSESSIONID; Value=34D5B13F2A12CFFED82A941E936C8575.s1; 
            2. 增加 Name=ipLoc-djd;  Value=15-1213-3411-59340.3773897606; 
            3. 增加 Name=ipLocation; Value=%u6d59%u6c5f; 
            
            Return
            ------
                order_info: dict订单信息, 
                >>> {'name': ['【速干凉爽】李宁短袖T恤男子速干吸湿排汗运动服训练系列圆领上衣健身服官方旗舰网ATSR369 【速干凉爽】-标准黑(369)-1 XL/175-182', 
                              '安德玛官方UA RUSH女子瑜伽训练运动内衣-低强度1361027 黑色001 L'], 
                     'num': ['x4', 'x4'],
                     'state': ['有货', '有货'], 
                     'address': '浙江 杭州市 西湖区 留下街道  浙江工业大学屏峰校区288号', 
                     'receiver': '张佳伟 178****3304', 
                     'sum_price': '1828.04'}
            
        """
        url = 'https://trade.jd.com/shopping/order/getOrderInfo.action'
        headers = {
            'Host':             'trade.jd.com',
            'User-Agent':       self.user_agent,
            'Referer':          'https://cart.jd.com'
        }
        payload = dict(
             rid = str(int(time.time() * 1000))
        )
        
        try:
            resp = self.sess.get(url=url, headers=headers, params=payload)
            if resp.status_code != requests.codes.OK:
                self.log(f'第{group_id}组商品获取订单结算页面失败, Status_Code: {resp.status_code}')
            
            # 节省时间， 不解析订单信息了
            # soup = BeautifulSoup(resp.content, 'html5lib')
            
            # order_info = dict(
            #     name =      [],
            #     num =       [],
            #     state =     [],
            #     address =   soup.find('span', attrs=dict(id='sendAddr')).text[5:],    # 地址
            #     receiver =  soup.find('span', attrs=dict(id='sendMobile')).text[4:],  # 电话   
            #     sum_price = soup.find('span', attrs=dict(id='sumPayPriceId')).text[1:]# 总价
            # )
            # a = soup.find_all('div',  attrs={'class':'p-name'})
            # b = soup.find_all('span', attrs={'class':'p-num'})
            # c = soup.find_all('span', attrs={'id':'pre-state', 'class':'p-state'})
            # for name, num, state in zip(a, b, c):
            #     order_info['name'].append(name.a.text.replace('  ','').replace('\n',''))# 去除空格 换行
            #     order_info['num'].append(num.text.replace('  ','').replace('\n',''))
            #     order_info['state'].append(state.text.replace('  ','').replace('\n',''))

            # self.log(f'尝试提交订单'+str(order_info))
            self.log(f'第{group_id}组商品尝试提交订单')
            return
        except Exception as e:
            self.log(f'订单结算页面数据解析异常，报错信息：{e}')
         
    def submit_order(self, group_id: int):
        """
            第{group_id}组商品尝试提交订单

            重要：
            1.该方法只适用于普通商品的提交订单（即可以加入购物车，然后结算提交订单的商品）
            2.提交订单时，会对购物车中勾选✓的商品进行结算（如果勾选了多个商品，将会提交成一个订单）

            Returns
            -------
                True/False 订单提交结果
        """
        url = 'https://trade.jd.com/shopping/order/submitOrder.action?presaleStockSign=1'
        headers = {
            'Host':             'trade.jd.com',
            'Accept':           'application/json, text/javascript, */*; q=0.01',
            'Content-Type':     'application/x-www-form-urlencoded',
            'User-Agent':       self.user_agent,
            'Origin':           'https://cart.jd.com',
            'Referer':          'https://trade.jd.com/shopping/order/getOrderInfo.action'
            
        } 
        data = {
            'overseaPurchaseCookies' : '',
            'vendorRemarks': [],
            'submitOrderParam.sopNotPutInvoice' :'false',
            'submitOrderParam.trackID': 'TestTrackId',
            'presaleStockSign': 1,
            'submitOrderParam.ignorePriceChange': '0',
            'submitOrderParam.btSupport': '0',
            'submitOrderParam.eid':self.eid,
            'submitOrderParam.fp': self.fp,
            'submitOrderParam.jxj': 1  #可以代替下面三个参数
            # 'submitOrderParam.skuDetailInfo': 
            #     [{"firstCategory":"1318","secondCategory":"12102","discount":0,"skuName":"【速干凉爽】李宁短袖T恤男子速干吸湿排汗运动服训练系列圆领上衣健身服官方旗舰网ATSR369 【速干凉爽】-标准黑(369)-1 XL/175-182","skuId":"10026215807526","price":9900,"num":1,"thirdCategory":"9765"},
            #      {"firstCategory":"1318","secondCategory":"12102","discount":0,"skuName":"安德玛官方UA RUSH女子瑜伽训练运动内衣-低强度1361027 黑色001 L","skuId":"10034941592352","price":39900,"num":4,"thirdCategory":"15099"}],
            # 'submitOrderParam.amount': 1664.01, # 总付款金额
            # 'submitOrderParam.needCheck': 1,
        }
        
        try:
            resp_json = self.sess.post(url=url, headers=headers,data=data).json()
            if resp_json.get('success'):
                order_id = resp_json.get('orderId')
                self.log(f'第{group_id}组商品订单提交成功, 订单号: {order_id}')
                # 推送消息到企业微信应用
                items = ''
                for itemInfo in self.seckill_group[group_id].values():
                    items += f'{itemInfo[1]}x{itemInfo[0]} ' 
                msg = f'用户[{self.username}]商品下单成功\n商品名称[ {items}]\n订单号[{order_id}]]'
                pusher.send_text('Bugbot_v2.0', 'ZhangJiaWei', msg)
            else:
                message, result_code = resp_json.get('message'), resp_json.get('resultCode')
                if result_code == 0:
                    pass
                elif result_code == 60077:
                    message = message + '(可能是购物车为空 或 未勾选购物车中商品)'
                elif result_code == 60123:
                    message = message + '(需要在config.ini文件中配置支付密码)'
                self.log(f'第{group_id}组商品订单提交失败, resultCode: {result_code}, message: {message}')
        except Exception as e:
            self.log(f'[Error]{e}, when submit order group {group_id}')

    #------------------线程2: 监视库存---------------------
    def monitor(self):
        """
            监控self.monitor_items列表里的商品是否有库存, 如果有, 尝试加入购物车
        """
        while True:
            if self.monitor_items:
                item_have_stock = self.get_multi_item_stock(self.monitor_items) # return list
                if item_have_stock:
                    self.lock.acquire() # 嗦住！ 防止内存混乱
                    self.add_item_to_cart(item_have_stock)
                    self.lock.release()
            time.sleep(2)
            
    def get_multi_item_stock(self, items: list):
        """
            获取多个商品库存状态
            
            1. 访问网库存url
                https://c0.3.cn/stocks?callback=jQuery9141851&type=getstocks&skuIds=10022336426185%2C10043579996077&area=15_1213_3038_59931&_=1650195775323
            2. 获取返回的resp.text
                jQuery9141851({
                    "10022336426185":{
                        "StockState":34, 商品库存状态: 33 -- 现货  0,34 -- 无货  36 -- 采购中  40 -- 可配货
                        "ab":"-1","ac":"-1","ad":"-1","ae":"-1",
                        "skuState":1,     商品是否上架
                        "PopType":0,"af":"-1","ag":"-1","sidDely":"-1","channel":1,"StockStateName":"无货","m":"0","sid":"-1","rfg":0,"dcId":"-1","ArrivalDate":"","v":"0","IsPurchase":false,"rn":-1,"eb":"99","ec":"-1"
                    }
                }
                )
                                                
            Params
            ------ 
                items (list): ['item_id1', 'item_id2', ...] 需要查询的商品编号列表

            Return
            ------
                items_have_stock (list): 有库存的商品编号列表
            
        """
        url = 'https://c0.3.cn/stocks' # https://c0.3.cn/stocks?callback=jQuery9141851&type=getstocks&skuIds=10022336426185%2C10043579996077&area=15_1213_3038_59931&_=1650195775323
        payload = {
            'callback': 'jQuery{}'.format(random.randint(1000000, 9999999)),
            'type': 'getstocks',
            'skuIds': ','.join(items),
            'area': self.area_id,
            '_': str(int(time.time() * 1000))
        }
        headers = {
            'User-Agent': self.user_agent
        }
        resp_text = ''
        items_have_stock = list()
        try:
            resp_text = requests.get(url=url, params=payload, headers=headers, timeout=10).text
            for item_id, stock_info in parse_json(resp_text).items(): # for stock_info in all_stock_info
                sku_state =   stock_info.get('skuState')    # 商品是否上架: 1 -- 上架  
                stock_state = stock_info.get('StockState')  # 商品库存状态：33 -- 现货  0,34 -- 无货  36 -- 采购中  40 -- 可配货
                if sku_state == 1 and stock_state in (33, 40):
                    items_have_stock.append(item_id)
            return items_have_stock
        except requests.exceptions.Timeout:
            self.log(f'查询库存信息超时(10秒)')
            return False
        except requests.exceptions.RequestException as request_exception:
            self.log(f'查询库存信息发生网络请求异常：{request_exception}')
            return False
        except Exception as e:  
            self.log(f'查询库存信息发生异常 库存信息: {resp_text}, Exception: {e}')
            return False

    def add_item_to_cart(self, items: list):
        """
            添加商品到购物车
            1.商品添加到购物车后将会自动被勾选✓中。
            2.部分商品（如预售、下架等）无法添加到购物车
            京东购物车可容纳的最大商品种数约为118-120种,超过数量会加入购物车失败。

            Params
            ------
                items (list): 商品id列表
        """
        url = 'https://cart.jd.com/gate.action'
        headers = {
            'User-Agent': self.user_agent,
        }

        for item_id in items:
            payload = {
                'pid': item_id,
                'pcount': 1,
                'ptype': 1,
            }
            resp = self.sess.get(url=url, params=payload, headers=headers)
            
            # 套装商品加入购物车后直接跳转到购物车页面
            if 'https://cart.jd.com/cart.action' in resp.url:
                self.monitor_items.remove(item_id) # 从监视库存名单里去除
                self.log(f'{item_id} 已成功加入购物车')
            
            # 普通商品成功加入购物车后会跳转到提示 "商品已成功加入购物车！" 页面
            else:  
                soup = BeautifulSoup(resp.text, "html5lib")
                if bool(soup.select('h3.ftx-02')): # [<h3 class="ftx-02">商品已成功加入购物车！</h3>]
                    self.monitor_items.remove(item_id) # 从监视库存名单里去除
                    self.log(f'{item_id} 已成功加入购物车')
                else:
                    self.log(f'{item_id} 添加到购物车失败')
    
      #-------------------预约抢购功能---------------------
    def seckill_reserve(self):
        """
            主程序, 速度至上
        """
        # 预约
        for seckill_info in self.seckill_group:
            for item_id in list(seckill_info.keys()):
                self.make_reserve(item_id)
                
        # 一些request信息
        self.cart_info = self.cancel_select_all_cart_item()
        url1, headers1        = self.get_requset_check_cart()
        url2, headers2, data2 = self.get_requset_submit_order()
        
        # 等待抢购的到来
        self.wait_for_buy_time()
        # 抢购
        while True:
            # 勾选购物车
            resp_json = self.user.sess.post(url=url1, headers=headers1).json() # 大约150ms
            if resp_json.get('success'):
                if resp_json['resultData']['cartInfo']['checkedWareNum'] > 0:
                    # 获取订单信息 300ms
                    self.user.sess.get(
                        url='https://trade.jd.com/shopping/order/getOrderInfo.action', 
                        headers={
                            'Host':             'trade.jd.com',
                            'User-Agent':       self.user.user_agent,
                            'Referer':          'https://cart.jd.com'
                        }, 
                        params=dict(rid = str(int(time.time() * 1000)))
                    )
                    
                    # 提交订单 200ms
                    resp_json = self.user.sess.post(url=url2, headers=headers2,data=data2).json()
                    if resp_json.get('success'):
                        order_id = resp_json.get('orderId')
                        self.loggerSignal.emit(f'商品订单提交成功, 订单号: {order_id}')
                    else:
                        message, result_code = resp_json.get('message'), resp_json.get('resultCode')
                        self.loggerSignal.emit(f'商品订单提交失败, resultCode: {result_code}, message: {message}') 
            
            time.sleep(0.01)

    def make_reserve(self, item_id: str):
        try:
            reserve_url = self.get_reserve_url(item_id)
            if not reserve_url:
                self.loggerSignal.emit(f'{item_id}非预约商品')
                return
            headers = {
                'User-Agent': self.user.user_agent,
                'Referer': 'https://item.jd.com/{}.html'.format(item_id),
            }
            resp = self.user.sess.get(url=reserve_url, headers=headers)
            soup = BeautifulSoup(resp.text, "html5lib")
            reserve_result = soup.find('p', {'class': 'bd-right-result'}).text.strip(' \t\r\n')
        except Exception as e:
            self.loggerSignal.emit(f'商品({item_id})预约失败, error:{e}')
            return False
        else:
            # 预约成功，已获得抢购资格 / 您已成功预约过了，无需重复预约
            self.loggerSignal.emit(f'商品({item_id}){reserve_result}')
            return True
    
    def get_reserve_url(self, item_id: str):
        url = 'https://yushou.jd.com/youshouinfo.action'
        payload = {
            'callback': 'fetchJSON',
            'sku': item_id,
        }
        headers = {
            'User-Agent': self.user.user_agent,
            'Referer': 'https://item.jd.com/{}.html'.format(item_id),
        }
        resp = self.user.sess.get(url=url, params=payload, headers=headers)
        resp_json = parse_json(resp.text)
        # {"type":"1","hasAddress":false,"riskCheck":"0","flag":false,"num":941723,"stime":"2018-10-12 12:40:00","plusEtime":"","qiangEtime":"","showPromoPrice":"0","qiangStime":"","state":2,"sku":100000287121,"info":"\u9884\u7ea6\u8fdb\u884c\u4e2d","isJ":0,"address":"","d":48824,"hidePrice":"0","yueEtime":"2018-10-19 15:01:00","plusStime":"","isBefore":0,"url":"//yushou.jd.com/toYuyue.action?sku=100000287121&key=237af0174f1cffffd227a2f98481a338","etime":"2018-10-19 15:01:00","plusD":48824,"category":"4","plusType":0,"yueStime":"2018-10-12 12:40:00"};
        reserve_url = resp_json.get('url')
        return 'https:' + reserve_url if reserve_url else None
    
    def get_requset_check_cart(self):
        url =  'https://api.m.jd.com/api'
        headers = {
            'Host':         'api.m.jd.com',
            'Accept':       'application/json, text/plain, */*',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent':   self.user.user_agent,
            'Origin':       'https://cart.jd.com',
            'Referer':      'https://cart.jd.com/'
            
        }
        self.loggerSignal.emit('将定时抢购商品: ')
        # 从self.seckill_group获得需要勾选的商品信息, 放到body里
        TheSkus = []
        for seckill_info in self.seckill_group:
            for item_id, item_info in seckill_info.items():
                if self.cart_info.get(item_id):
                    TheSku = dict(
                        Id=item_id,
                        num=item_info[0],
                        skuUuid=self.cart_info[item_id]['skuUuid'],
                        useUuid=self.cart_info[item_id]['useUuid']
                    )
                    self.loggerSignal.emit(item_id + ' '+ item_info[1] + ' x' + str(item_info[0]))
                    TheSkus.append(TheSku)

        body = dict(
            operations= [{
                "ThePacks": [],
                "TheSkus":  TheSkus,
                "carttype": "5"
            }],
            serInfo = {
                'area': self.user.area_id,
                'user-key': ' '
            }
        )
        
        payload = dict(
            functionId= 'pcCart_jc_changeSkuNum',
            appid     = 'JDC_mall_cart',
            loginType = 3,
            body      = url_encode(body)
        )
        
        url_with_params = add_url_params(url, payload)
        
        return url_with_params, headers
    
    def get_requset_submit_order(self):
        url = 'https://trade.jd.com/shopping/order/submitOrder.action?presaleStockSign=1'
        headers = {
            'Host':             'trade.jd.com',
            'Accept':           'application/json, text/javascript, */*; q=0.01',
            'Content-Type':     'application/x-www-form-urlencoded',
            'User-Agent':       self.user.user_agent,
            'Origin':           'https://cart.jd.com',
            'Referer':          'https://trade.jd.com/shopping/order/getOrderInfo.action'
            
        } 
        data = {
            'overseaPurchaseCookies' : '',
            'vendorRemarks': [],
            'submitOrderParam.sopNotPutInvoice' :'false',
            'submitOrderParam.trackID': 'TestTrackId',
            'presaleStockSign': 1,
            'submitOrderParam.ignorePriceChange': '0',
            'submitOrderParam.btSupport': '0',
            'submitOrderParam.eid':self.user.eid,
            'submitOrderParam.fp': self.user.fp,
            'submitOrderParam.jxj': 1  # 可以代替下面三个参数
            # 'submitOrderParam.skuDetailInfo':
            #     [{"firstCategory":"1318","secondCategory":"12102","discount":0,"skuName":"【速干凉爽】李宁短袖T恤男子速干吸湿排汗运动服训练系列圆领上衣健身服官方旗舰网ATSR369 【速干凉爽】-标准黑(369)-1 XL/175-182","skuId":"10026215807526","price":9900,"num":1,"thirdCategory":"9765"},
            #      {"firstCategory":"1318","secondCategory":"12102","discount":0,"skuName":"安德玛官方UA RUSH女子瑜伽训练运动内衣-低强度1361027 黑色001 L","skuId":"10034941592352","price":39900,"num":4,"thirdCategory":"15099"}],
            # 'submitOrderParam.amount': 1664.01, # 总付款金额
            # 'submitOrderParam.needCheck': 1,
        }
        
        return url, headers, data

    #----------------------弃用---------------------------
    @deprecated
    def get_cart_info(self):
        '''
            获取购物车信息
            Return
            ------
                { item_id: item_info, ... }
        '''
        url =  'https://api.m.jd.com/api'
        header = {
            'Host':       'api.m.jd.com',
            'Accept':     'application/json, text/plain, */*',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': self.user.user_agent,
            'Origin': 'https://cart.jd.com',
            'Referer':   'https://cart.jd.com/'
            
        }
        body = {
            'serInfo':{
                'area':     self.user.area_id,
                'user-key': ' ' # 暂时不知道什么东西,但是似乎不需要
            },
            'cartExt':{
                'specialId': 1  # 暂时不知道什么东西
            }
        }
        payload  = {
            'functionId': 'pcCart_jc_getCurrentCart',
            'appid':      'JDC_mall_cart',
            'loginType':  3,
            'body':       url_encode(body)
        }
        url_with_params = add_url_params(url, payload)#request默认会把params编码后加到url, 因此手动加params参数
        
        resp_json = self.user.sess.post(url_with_params, headers=header).json()
        cart_info = dict()
        
        for vendor in resp_json['resultData']['cartInfo']['vendors']: # for every vendor in cart
            for item_info in vendor['sorted']: # for every item in vendor
                try:
                    item = item_info['item']
                    cart_info[item['Id']] = {
                        'verder_id':    vendor['vendorId'],            # str 商家id
                        'name':         item['unitedText'] if item.get('unitedText') else ' ',# str 商品 货号+尺码 "EG4958/偏大半码，39"
                        'skuUuid':      item['skuUuid'],               # 用于购物车勾选操作
                        'useUuid':      item['useUuid'],               # 用于购物车勾选操作
                        'num':          item['Num'],                   # int 数量
                        'stockStateId': item['stock']['stockStateId'], # int 商品库存状态：33 -- 现货  0,34 -- 无货  36 -- 采购中  40 -- 可配货
                        'stockCode':    item['stock']['stockCode'],    # int 商品是否上架 猜测：0有货， 1无货
                        'price':        item['Price'],                 # int 原价（一双
                        'priceShow':    item['PriceShow'],             # str 现价  "￥574.00" 
                        'checkType':    item['CheckType'],             # int 商品是否被勾选   1:已被勾选，0:未被勾选
                        'isNoCheck':    item['isNoCheck'],             # int 商品是否能被勾选  1:不能，   0:能
                        'targetId':     item['targetId'],              # int ?
                        'promo_id':     item['targetId']               # int ?
                    }
                except Exception as e:
                    self.loggerSignal.emit(f"购物车信息解析错误, 报错信息：{e}, 忽略商品:{item['Num']}")
        return cart_info
    
    def cart_Check_Single(self, item_id: str, cart_info: dict):
        """勾选单个商品

        Args:
            item_id (int): 商品组别

        Returns:
            Ture/False: 是否勾选成功
        """
        url =  'https://api.m.jd.com/api'
        headers = {
            'Host':         'api.m.jd.com',
            'Accept':       'application/json, text/plain, */*',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent':   self.user.user_agent,
            'Origin':       'https://cart.jd.com',
            'Referer':      'https://cart.jd.com/'
            
        }
        body = dict(
            operations= [{
                "TheSkus":[{
                    "Id":item_id,
                    "num":1,
                    "skuUuid":cart_info[item_id]['skuUuid'],
                    "useUuid":False
                    }]
            }],
            serInfo = {
                'area':     self.user.area_id,
                'user-key': ' '
            }
        )
            
        payload = dict(
            functionId= 'pcCart_jc_cartCheckSingle',
            appid     = 'JDC_mall_cart',
            loginType = 3,
            body      = url_encode(body)
        )
        url_with_params = add_url_params(url, payload)
        try:
            resp_json = self.user.sess.post(url=url_with_params, headers=headers).json()
            # 是否更改成功：比较total_num和购物车已勾选的商品数量 [maybe]
            if resp_json['resultData']['cartInfo']['checkedWareNum'] >= 1:
                self.loggerSignal.emit(f'勾选成功')
                return True
            else:
                self.loggerSignal.emit(f'勾选失败')
                return False
        except Exception as e:
            return False

class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('BugBot')
        self.resize(650,780)

        self.tabWidget = QTabWidget()
        hbox = QHBoxLayout()
        hbox.addWidget(self.tabWidget)
        self.setLayout(hbox)

        # 添加用户 '按钮'
        Tab_addUser = QWidget()
        self.tabWidget.addTab(Tab_addUser, '添加用户')
        self.tabWidget.currentChanged.connect(self.tabChanged)

        # 用户列表
        self.currentUserList = list()
        self.userList = global_config.config.sections()
        self.userList.append('【创建新用户】')
        self.choose_user = QListWidget()
        self.choose_user.itemClicked.connect(self.add_user)
        self.choose_user.addItems(self.userList)

    def tabChanged(self):
        """如果选中了最后一个tab,则触发choose_user窗口
        """
        if self.tabWidget.currentIndex() == len(self.currentUserList):
            self.choose_user.show()

    def add_user(self, username):
        if username.text() == '【创建新用户】':
            text, ok = QInputDialog.getText(self, 'q.q', '请输入您的用户名')
            if ok:
                self.add_one_user(text, True)
            else:
                return
        else:
            self.add_one_user(username.text(), False)
    
        self.choose_user.close()

    def add_one_user(self, username, is_new_user):
        # bugbot
        BugBot = Bugbot(username=username, is_new_user=is_new_user)
        self.tabWidget.insertTab(len(self.currentUserList), BugBot, username)
        # tabWidget 索引变化
        self.tabWidget.setCurrentIndex(len(self.currentUserList))
        self.currentUserList.append(username)

class read_loginfo(QThread):
    loggerSignal = pyqtSignal(str)
    def __init__(self, loginfo, timesleep:int=1, timeout:int=5) -> None:
        super().__init__()
        """传入loginfo列表的引用, 读取存在堆内存中的日志信息
            如果日志信息>5条  ->  输出日志信息到ui
            如果timeout超时  ->  输出日志信息到ui
            
            Params
            ------
                loginfo  (list): 日志信息引用
                timesleep (int): 每隔多少时间查询一次日志信息
                timeout   (int): 每隔多少秒输出一次日志信息
        """
        self.loginfo = loginfo
        self.loopcount = 0
        self.countout = timeout / timesleep 
        
    def reading(self):
        while True:
            if len(self.loginfo) > 5 or (self.loopcount > self.countout and self.loginfo):
                for _ in range(len(self.loginfo)):
                    self.loggerSignal.emit(self.loginfo.pop(0))
                self.loopcount = 0
            else:
                self.loopcount += 1
            time.sleep(1)
            
    def run(self):
        self.reading()

# 弃用，从文件中读取log
class read_log(QThread):
    loggerSignal = pyqtSignal(str)
    def __init__(self, log_path:str) -> None:
        super().__init__()
        self.log_path = log_path
        self.line_count = 0 # 读到第几行
        
    def reading(self):
        """从self.log_path路径中读取.log日志文件
           一行一行输出
        """
        with open(self.log_path, mode='r', encoding='utf-8') as log:    
            while True:
                infos = log.readlines()
                for i in range(self.line_count, len(infos)):
                    self.line_count += 1
                    self.loggerSignal.emit(infos[i])
    def run(self):
        self.reading()


if __name__ == '__main__':
    
    # app = QApplication(sys.argv)
    # w = Bugbot('胯下运球人', False) 
    # w.show()
    # sys.exit(app.exec_())
    
    app = QApplication(sys.argv)
    bugbot = MainWindow()
    bugbot.show()
    bugbot.choose_user.show()
    sys.exit(app.exec_())
    
