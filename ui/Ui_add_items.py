# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'e:\jd-assistant\ui\add_items.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_add_items(object):
    def setupUi(self, add_items):
        add_items.setObjectName("add_items")
        add_items.resize(432, 458)
        self.gridLayout = QtWidgets.QGridLayout(add_items)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushButton_get_items = QtWidgets.QPushButton(add_items)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(10)
        self.pushButton_get_items.setFont(font)
        self.pushButton_get_items.setObjectName("pushButton_get_items")
        self.horizontalLayout_2.addWidget(self.pushButton_get_items)
        self.pushButton_get_coupon = QtWidgets.QPushButton(add_items)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(10)
        self.pushButton_get_coupon.setFont(font)
        self.pushButton_get_coupon.setObjectName("pushButton_get_coupon")
        self.horizontalLayout_2.addWidget(self.pushButton_get_coupon)
        self.label_9 = QtWidgets.QLabel(add_items)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(10)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.horizontalLayout_2.addWidget(self.label_9)
        self.spinBox_interval = QtWidgets.QSpinBox(add_items)
        self.spinBox_interval.setMaximum(2000)
        self.spinBox_interval.setProperty("value", 1000)
        self.spinBox_interval.setObjectName("spinBox_interval")
        self.horizontalLayout_2.addWidget(self.spinBox_interval)
        self.label_19 = QtWidgets.QLabel(add_items)
        self.label_19.setObjectName("label_19")
        self.horizontalLayout_2.addWidget(self.label_19)
        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)
        self.textBrowser = QtWidgets.QTextBrowser(add_items)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.textBrowser.setFont(font)
        self.textBrowser.setObjectName("textBrowser")
        self.gridLayout.addWidget(self.textBrowser, 2, 0, 1, 1)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.spinBox_item_count1 = QtWidgets.QSpinBox(add_items)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.spinBox_item_count1.setFont(font)
        self.spinBox_item_count1.setObjectName("spinBox_item_count1")
        self.gridLayout_2.addWidget(self.spinBox_item_count1, 0, 5, 1, 1)
        self.label_5 = QtWidgets.QLabel(add_items)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(10)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.gridLayout_2.addWidget(self.label_5, 1, 4, 1, 1)
        self.lineEdit_item_name3 = QtWidgets.QLineEdit(add_items)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_item_name3.sizePolicy().hasHeightForWidth())
        self.lineEdit_item_name3.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.lineEdit_item_name3.setFont(font)
        self.lineEdit_item_name3.setInputMethodHints(QtCore.Qt.ImhNone)
        self.lineEdit_item_name3.setObjectName("lineEdit_item_name3")
        self.gridLayout_2.addWidget(self.lineEdit_item_name3, 2, 3, 1, 1)
        self.spinBox_item_count3 = QtWidgets.QSpinBox(add_items)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.spinBox_item_count3.setFont(font)
        self.spinBox_item_count3.setObjectName("spinBox_item_count3")
        self.gridLayout_2.addWidget(self.spinBox_item_count3, 2, 5, 1, 1)
        self.lineEdit_item_name1 = QtWidgets.QLineEdit(add_items)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_item_name1.sizePolicy().hasHeightForWidth())
        self.lineEdit_item_name1.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.lineEdit_item_name1.setFont(font)
        self.lineEdit_item_name1.setInputMethodHints(QtCore.Qt.ImhNone)
        self.lineEdit_item_name1.setObjectName("lineEdit_item_name1")
        self.gridLayout_2.addWidget(self.lineEdit_item_name1, 0, 3, 1, 1)
        self.t_1 = QtWidgets.QLabel(add_items)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(10)
        self.t_1.setFont(font)
        self.t_1.setObjectName("t_1")
        self.gridLayout_2.addWidget(self.t_1, 0, 0, 1, 1)
        self.lineEdit_item_name4 = QtWidgets.QLineEdit(add_items)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_item_name4.sizePolicy().hasHeightForWidth())
        self.lineEdit_item_name4.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.lineEdit_item_name4.setFont(font)
        self.lineEdit_item_name4.setInputMethodHints(QtCore.Qt.ImhNone)
        self.lineEdit_item_name4.setObjectName("lineEdit_item_name4")
        self.gridLayout_2.addWidget(self.lineEdit_item_name4, 3, 3, 1, 1)
        self.lineEdit_item_name2 = QtWidgets.QLineEdit(add_items)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_item_name2.sizePolicy().hasHeightForWidth())
        self.lineEdit_item_name2.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.lineEdit_item_name2.setFont(font)
        self.lineEdit_item_name2.setInputMethodHints(QtCore.Qt.ImhNone)
        self.lineEdit_item_name2.setObjectName("lineEdit_item_name2")
        self.gridLayout_2.addWidget(self.lineEdit_item_name2, 1, 3, 1, 1)
        self.spinBox_item_count2 = QtWidgets.QSpinBox(add_items)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.spinBox_item_count2.setFont(font)
        self.spinBox_item_count2.setObjectName("spinBox_item_count2")
        self.gridLayout_2.addWidget(self.spinBox_item_count2, 1, 5, 1, 1)
        self.label_2 = QtWidgets.QLabel(add_items)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.lineEdit_item_id1 = QtWidgets.QLineEdit(add_items)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_item_id1.sizePolicy().hasHeightForWidth())
        self.lineEdit_item_id1.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.lineEdit_item_id1.setFont(font)
        self.lineEdit_item_id1.setInputMethodHints(QtCore.Qt.ImhNone)
        self.lineEdit_item_id1.setObjectName("lineEdit_item_id1")
        self.gridLayout_2.addWidget(self.lineEdit_item_id1, 0, 1, 1, 1)
        self.label_15 = QtWidgets.QLabel(add_items)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(10)
        self.label_15.setFont(font)
        self.label_15.setObjectName("label_15")
        self.gridLayout_2.addWidget(self.label_15, 0, 2, 1, 1)
        self.label_7 = QtWidgets.QLabel(add_items)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(10)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.gridLayout_2.addWidget(self.label_7, 0, 4, 1, 1)
        self.label_3 = QtWidgets.QLabel(add_items)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(10)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 2, 0, 1, 1)
        self.label_8 = QtWidgets.QLabel(add_items)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(10)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.gridLayout_2.addWidget(self.label_8, 3, 4, 1, 1)
        self.label_18 = QtWidgets.QLabel(add_items)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(10)
        self.label_18.setFont(font)
        self.label_18.setObjectName("label_18")
        self.gridLayout_2.addWidget(self.label_18, 3, 2, 1, 1)
        self.label_17 = QtWidgets.QLabel(add_items)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(10)
        self.label_17.setFont(font)
        self.label_17.setObjectName("label_17")
        self.gridLayout_2.addWidget(self.label_17, 2, 2, 1, 1)
        self.lineEdit_item_id4 = QtWidgets.QLineEdit(add_items)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.lineEdit_item_id4.setFont(font)
        self.lineEdit_item_id4.setObjectName("lineEdit_item_id4")
        self.gridLayout_2.addWidget(self.lineEdit_item_id4, 3, 1, 1, 1)
        self.lineEdit_item_id2 = QtWidgets.QLineEdit(add_items)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.lineEdit_item_id2.setFont(font)
        self.lineEdit_item_id2.setObjectName("lineEdit_item_id2")
        self.gridLayout_2.addWidget(self.lineEdit_item_id2, 1, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(add_items)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(10)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 3, 0, 1, 1)
        self.lineEdit_item_id3 = QtWidgets.QLineEdit(add_items)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.lineEdit_item_id3.setFont(font)
        self.lineEdit_item_id3.setObjectName("lineEdit_item_id3")
        self.gridLayout_2.addWidget(self.lineEdit_item_id3, 2, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(add_items)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(10)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.gridLayout_2.addWidget(self.label_6, 2, 4, 1, 1)
        self.label_16 = QtWidgets.QLabel(add_items)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(10)
        self.label_16.setFont(font)
        self.label_16.setObjectName("label_16")
        self.gridLayout_2.addWidget(self.label_16, 1, 2, 1, 1)
        self.spinBox_item_count4 = QtWidgets.QSpinBox(add_items)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.spinBox_item_count4.setFont(font)
        self.spinBox_item_count4.setObjectName("spinBox_item_count4")
        self.gridLayout_2.addWidget(self.spinBox_item_count4, 3, 5, 1, 1)
        self.gridLayout_2.setColumnStretch(0, 2)
        self.gridLayout_2.setColumnStretch(1, 11)
        self.gridLayout_2.setColumnStretch(2, 1)
        self.gridLayout_2.setColumnStretch(3, 1)
        self.gridLayout_2.setColumnStretch(4, 1)
        self.gridLayout_2.setColumnStretch(5, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 1, 0, 1, 1)

        self.retranslateUi(add_items)
        QtCore.QMetaObject.connectSlotsByName(add_items)

    def retranslateUi(self, add_items):
        _translate = QtCore.QCoreApplication.translate
        add_items.setWindowTitle(_translate("add_items", "Form"))
        self.pushButton_get_items.setText(_translate("add_items", "获取商品"))
        self.pushButton_get_coupon.setText(_translate("add_items", "一键领券"))
        self.label_9.setText(_translate("add_items", "查询库存间隔"))
        self.label_19.setText(_translate("add_items", "毫秒"))
        self.label_5.setText(_translate("add_items", "购买数量"))
        self.t_1.setText(_translate("add_items", "商品编号"))
        self.label_2.setText(_translate("add_items", "商品编号"))
        self.label_15.setText(_translate("add_items", "简称"))
        self.label_7.setText(_translate("add_items", "购买数量"))
        self.label_3.setText(_translate("add_items", "商品编号"))
        self.label_8.setText(_translate("add_items", "购买数量"))
        self.label_18.setText(_translate("add_items", "简称"))
        self.label_17.setText(_translate("add_items", "简称"))
        self.label_4.setText(_translate("add_items", "商品编号"))
        self.label_6.setText(_translate("add_items", "购买数量"))
        self.label_16.setText(_translate("add_items", "简称"))
