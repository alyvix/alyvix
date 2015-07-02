# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'alyvix_text_check.ui'
#
# Created: Fri Mar 27 17:39:15 2015
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
        Form.resize(452, 269)
        self.plainTextEdit = QtGui.QPlainTextEdit(Form)
        self.plainTextEdit.setGeometry(QtCore.QRect(10, 48, 432, 137))
        self.plainTextEdit.setObjectName(_fromUtf8("plainTextEdit"))
        self.labelHeader = QtGui.QLabel(Form)
        self.labelHeader.setGeometry(QtCore.QRect(11, 14, 428, 16))
        self.labelHeader.setObjectName(_fromUtf8("labelHeader"))
        self.labelCheckResult = QtGui.QLabel(Form)
        self.labelCheckResult.setGeometry(QtCore.QRect(11, 204, 429, 16))
        self.labelCheckResult.setObjectName(_fromUtf8("labelCheckResult"))
        self.pushButtonOk = QtGui.QPushButton(Form)
        self.pushButtonOk.setGeometry(QtCore.QRect(11, 236, 75, 23))
        self.pushButtonOk.setObjectName(_fromUtf8("pushButtonOk"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.labelHeader.setText(_translate("Form", "Text found inside ROI:", None))
        self.labelCheckResult.setText(_translate("Form", "EXCELLENT: Your regular expression match with text found!", None))
        self.pushButtonOk.setText(_translate("Form", "Ok", None))

