# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'e:\jd-assistant\ui\login_qrcode.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_login_qrcode(object):
    def setupUi(self, login_qrcode):
        login_qrcode.setObjectName("login_qrcode")
        login_qrcode.resize(300, 300)
        self.label_qrcode = QtWidgets.QLabel(login_qrcode)
        self.label_qrcode.setGeometry(QtCore.QRect(25, 25, 250, 250))
        self.label_qrcode.setText("")
        self.label_qrcode.setObjectName("label_qrcode")

        self.retranslateUi(login_qrcode)
        QtCore.QMetaObject.connectSlotsByName(login_qrcode)

    def retranslateUi(self, login_qrcode):
        _translate = QtCore.QCoreApplication.translate
        login_qrcode.setWindowTitle(_translate("login_qrcode", "京东APP扫描二维码登录"))
