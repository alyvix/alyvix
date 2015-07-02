# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'alyvix_object_finder_obj_selection.ui'
#
# Created: Sat Jan 17 19:01:14 2015
#      by: PyQt4 UI code generator 4.11
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(235, 252)
        self.listWidgetAlyObj = QtGui.QListWidget(Form)
        self.listWidgetAlyObj.setGeometry(QtCore.QRect(8, 28, 218, 181))
        self.listWidgetAlyObj.setObjectName(_fromUtf8("listWidgetAlyObj"))
        self.pushButtonSelect = QtGui.QPushButton(Form)
        self.pushButtonSelect.setGeometry(QtCore.QRect(19, 219, 90, 23))
        self.pushButtonSelect.setObjectName(_fromUtf8("pushButtonSelect"))
        self.pushButtonCancel = QtGui.QPushButton(Form)
        self.pushButtonCancel.setGeometry(QtCore.QRect(124, 219, 90, 23))
        self.pushButtonCancel.setObjectName(_fromUtf8("pushButtonCancel"))
        self.label = QtGui.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(8, 7, 211, 16))
        self.label.setObjectName(_fromUtf8("label"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.pushButtonSelect.setText(_translate("Form", "Select", None))
        self.pushButtonCancel.setText(_translate("Form", "Cancel", None))
        self.label.setText(_translate("Form", "Alyvix Objects:", None))

