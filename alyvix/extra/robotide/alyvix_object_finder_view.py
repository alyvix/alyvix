# Alyvix allows you to automate and monitor all types of applications
# Copyright (C) 2015 Alan Pipitone
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Developer: Alan Pipitone (Violet Atom) - http://www.violetatom.com/
# Supporter: Wuerth Phoenix - http://www.wuerth-phoenix.com/
# Official website: http://www.alyvix.com/

import sys
import os
import time
import datetime
import cv2
import copy
from ast import parse

from PyQt4.QtGui import QApplication, QWidget, QCursor, QImage, QPainter, QPainter, QPen, QColor, QPixmap, QBrush, QPainterPath, QDialog, QListWidgetItem , QTextEdit, QHBoxLayout, QTextCharFormat, QMessageBox, QFont, QFontMetrics, QTextCursor,QGridLayout, QPushButton, QIcon, QSpacerItem, QSizePolicy,  QTableWidgetItem, QDateTimeEdit, QHeaderView, QAbstractItemView
from PyQt4.QtCore import Qt, QThread, SIGNAL, QTimer, QUrl, QPoint, QRect, QModelIndex, SLOT, pyqtSlot, QString, QChar,  QDate,QDateTime, QSize
from PyQt4.Qt import QFrame

from PyQt4.QtWebKit import QWebSettings

from alyvix_rect_finder_view import AlyvixRectFinderView
from alyvix_rect_finder_view import AlyvixRectFinderPropertiesView
from alyvix_image_finder_view import AlyvixImageFinderView
from alyvix_image_finder_view import AlyvixImageFinderPropertiesView
from alyvix_text_finder_view import AlyvixTextFinderView
from alyvix_text_finder_view import AlyvixTextFinderPropertiesView
#from alyvix_object_selection_controller import AlyvixMainMenuController

from alyvix_object_finder_properties_view import Ui_Form
from alyvix_object_finder_obj_selection import Ui_Form as Ui_Form_2

from alyvix.tools.screen import ScreenManager

from stat import S_ISREG, ST_CTIME, ST_MODE

import shutil

import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET

import codecs

from distutils.sysconfig import get_python_lib

last_pos = None
last_row_selected = -1

old_order = Qt.AscendingOrder
old_section = 2


class dummy():
    def __init__(self):
        self.window = None
        self.full_file_name = None
        self.path = None
        self.robot_file_name = None
        self.action = ""
        self.xml_name = ""
        self.parent = None
        self.objectfinder_view = None
        self.scaling_factor = None
        self.build_objects = True
        
    def set_parent(self, parent):
        self.parent = parent
        
    def show(self):
        #self.parent._sub_objects_finder = []
        #self.parent._code_blocks = []
        #self.parent._main_object_finder = MainObjectForGui()
        #self.parent.build_objects()
        self.parent.show()
        
    def update_list(self):
        self.objectfinder_view.update_list()

class AlyvixObjectFinderView(QWidget, Ui_Form):
    def __init__(self, parent, main_object=None, sub_objects=[]):
        QWidget.__init__(self)
        
        #print "object init"
        
        global last_pos
        global last_row_selected
        last_row_selected = -1
        
        #print sub_objects
        
        self.setMouseTracking(True)
		
        self._main_deleted = False
        self._roi_restored_after_deleted_main = 0
        
        
        self._old_sub_roi = []
        self.text_finder_roi_modified = []

        # Set up the user interface from Designer.
        self.setupUi(self)
        
        self.parent = parent
        self.scaling_factor = self.parent.scaling_factor
        
        self.redraw_index_from_finder = None
        
        self.last_selected_index = 0
        
        self.scaling_factor = self.parent.scaling_factor
        
        #self.pushButtonRoiRedraw.setEnabled(False)
        #self.pushButtonRoiRedraw.hide()
        
        #self.pushButtonRemoveObj_2.setEnabled(False)
        #self.pushButtonRemoveObj_2.hide()
        
        
        #self.setFixedSize(self.size())
        self.setFixedSize(int(self.frameGeometry().width() * self.scaling_factor), int(self.frameGeometry().height() * self.scaling_factor))
        
        self.widget.setGeometry(QRect(int(self.widget.geometry().x() * self.scaling_factor), int(self.widget.geometry().y() * self.scaling_factor),
                                int(self.widget.geometry().width() * self.scaling_factor), int(self.widget.geometry().height() * self.scaling_factor)))
                                
        self.gridLayoutWidget.setGeometry(QRect(int(self.gridLayoutWidget.geometry().x() * self.scaling_factor), int(self.gridLayoutWidget.geometry().y() * self.scaling_factor),
                                          int(self.gridLayoutWidget.geometry().width() * self.scaling_factor), int(self.gridLayoutWidget.geometry().height() * self.scaling_factor)))
                                          
        self.pushButtonOk.setGeometry(QRect(int(self.pushButtonOk.geometry().x() * self.scaling_factor), int(self.pushButtonOk.geometry().y() * self.scaling_factor),
                                          int(self.pushButtonOk.geometry().width() * self.scaling_factor), int(self.pushButtonOk.geometry().height() * self.scaling_factor)))
                                          
        self.pushButtonCancel.setGeometry(QRect(int(self.pushButtonCancel.geometry().x() * self.scaling_factor), int(self.pushButtonCancel.geometry().y() * self.scaling_factor),
                                          int(self.pushButtonCancel.geometry().width() * self.scaling_factor), int(self.pushButtonCancel.geometry().height() * self.scaling_factor)))
                                          
        self.listWidget.setGeometry(QRect(int(self.listWidget.geometry().x() * self.scaling_factor), int(self.listWidget.geometry().y() * self.scaling_factor),
                                          int(self.listWidget.geometry().width() * self.scaling_factor), int(self.listWidget.geometry().height() * self.scaling_factor)))
                                
        
        self.widget_2.setGeometry(QRect(int(self.widget_2.geometry().x() * self.scaling_factor), int(self.widget_2.geometry().y() * self.scaling_factor),
                                        int(self.widget_2.geometry().width() * self.scaling_factor), int(self.widget_2.geometry().height() * self.scaling_factor)))
        
        
        self.pushButtonEditObj_2.setGeometry(QRect(int(self.pushButtonEditObj_2.geometry().x() * self.scaling_factor), int(self.pushButtonEditObj_2.geometry().y() * self.scaling_factor),
                                        int(self.pushButtonEditObj_2.geometry().width() * self.scaling_factor), int(self.pushButtonEditObj_2.geometry().height() * self.scaling_factor)))
              
              
        #self.gridLayoutWidget_2.setGeometry(QRect(int(self.gridLayoutWidget_2.geometry().x() * self.scaling_factor), int(self.gridLayoutWidget_2.geometry().y() * self.scaling_factor),
        #                                  int(self.gridLayoutWidget_2.geometry().width() * self.scaling_factor), int(self.gridLayoutWidget_2.geometry().height() * self.scaling_factor)))

        self.gridLayoutWidget_3.setGeometry(QRect(int(self.gridLayoutWidget_3.geometry().x() * self.scaling_factor), int(self.gridLayoutWidget_3.geometry().y() * self.scaling_factor),
                                          int(self.gridLayoutWidget_3.geometry().width() * self.scaling_factor), int(self.gridLayoutWidget_3.geometry().height() * self.scaling_factor)))
        
        self.gridLayoutWidget_4.setGeometry(QRect(int(self.gridLayoutWidget_4.geometry().x() * self.scaling_factor), int(self.gridLayoutWidget_4.geometry().y() * self.scaling_factor),
                                          int(self.gridLayoutWidget_4.geometry().width() * self.scaling_factor), int(self.gridLayoutWidget_4.geometry().height() * self.scaling_factor)))
                        
                        
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)
        
        #self.setAttribute(Qt.WA_DeleteOnClose)
        
        
        if last_pos is not None:
            self.move(last_pos[0],last_pos[1])

        self._path = self.parent.path
        self.action = self.parent.action
        self._xml_name = self.parent.xml_name
        
        self.find_radio.hide()
        #self.pushButtonRemoveObj.hide()
        
        self.is_object_finder_menu = True
        
        self._can_set_roi_unlim = False
        
        self.building_code = False
        
        self.button_selected = "set_main_object"
        
        self.esc_pressed = False
        self.ok_pressed = False
        
        self._main_object_finder = MainObjectForGui()
        self._sub_objects_finder = []
        self._last_sub_object = None
        self._deleted_sub_objects = []
        
        self._code_lines = []
        self._arg_index_processed = 0
        self._code_lines_for_object_finder = []
        
        self._code_blocks = []
        
        self.added_block = False
        self.textEdit = LineTextWidget()
        self.textEdit.setGeometry(QRect(8, 9, 520, 172))
        self.textEdit.setText(self.build_code_string())
        
        self._old_object_finder_config = None
        
        self._added_objects = []
        
        self.build_objects()
        #print self._old_object_finder_config
        #print self._added_objects
        #print self._main_object_finder.xml_path
        self._old_main_object = copy.deepcopy(self._main_object_finder)
        self._old_sub_objects = copy.deepcopy(self._sub_objects_finder)
        
        self.__old_code = self.get_old_code()
        #self._alyvix_proxy_path = os.getenv("ALYVIX_HOME") + os.sep + "robotproxy"
        self._alyvix_proxy_path = get_python_lib() + os.sep + "alyvix" + os.sep + "robotproxy"
        self._robot_file_name = self.parent.robot_file_name

        self._redraw_index = None
        
        if self.action == "edit":
            filename = self._main_object_finder.xml_path
            filename = filename.split(os.sep)[-1]
                        
            item = QListWidgetItem()
                
            if filename.endswith('_RectFinder.xml'):
                item.setText(filename[:-15] + " [RF]")
            elif filename.endswith('_ImageFinder.xml'):
                item.setText(filename[:-16] + " [IF]")
            elif filename.endswith('_TextFinder.xml'):
                item.setText(filename[:-15] + " [TF]")
                
            item.setData(Qt.UserRole, filename)
            
            self.listWidget.addItem(item)
            
            """
            if self._main_object_finder.show is True:
            
                self.listWidget.item(0).setCheckState(Qt.Checked)
            else:
                self.listWidget.item(0).setCheckState(Qt.Unchecked)
            """
        if self.action == "edit":
            self.namelineedit.setEnabled(False)
            
        if self._main_object_finder.find is True:
            self.find_radio.setChecked(True)
            self.timeout_label.setEnabled(False)
            self.timeout_spinbox.setEnabled(False)
            self.timeout_exception.setEnabled(False)
        
        if self._main_object_finder.wait is True:
            self.wait_radio.setChecked(True)
            self.timeout_label.setEnabled(True)
            self.timeout_spinbox.setEnabled(True)
            self.timeout_exception.setEnabled(True)
            
        if self._main_object_finder.wait_disapp is True:
            self.wait_disapp_radio.setChecked(True)
            self.timeout_label.setEnabled(True)
            self.timeout_spinbox.setEnabled(True)
            self.timeout_exception.setEnabled(True)
                    
        self.widget_2.hide()
        
        self.sub_object_index = 0
        
        cnt = 1
        for sub_object in self._sub_objects_finder:
        
            #item = QListWidgetItem()
            
            filename = sub_object.xml_path
            filename = filename.split(os.sep)[-1]
            
            scraper = False
            extra_path = get_python_lib() + os.sep + "alyvix" + os.sep + "robotproxy" + os.sep + self._path.split(os.sep)[-1] + "_extra"
            scraper_path = extra_path + os.sep + filename.replace("_TextFinder.xml","")
            scraper_file = scraper_path + os.sep + "scraper.txt"
            if os.path.exists(scraper_file):
                scraper = True
                        
            item = QListWidgetItem()
            
            if sub_object.show is True:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
                
            if filename.endswith('_RectFinder.xml'):
                item.setText(filename[:-15] + " [RF]")
            elif filename.endswith('_ImageFinder.xml'):
                item.setText(filename[:-16] + " [IF]")
            elif filename.endswith('_TextFinder.xml'):
                if scraper is True:
                    item.setText(filename[:-15] + " [TS]")
                else:
                    item.setText(filename[:-15] + " [TF]")
                
            item.setData(Qt.UserRole, filename)
            
            self.listWidget.addItem(item)
            cnt = cnt + 1
        
        #self.listWidget.setCurrentIndex(QModelIndex(self.listWidget.rootIndex()))
        #self.listWidget.item(0).setSelected(True)
        self.timeout_spinbox.setValue(self._main_object_finder.timeout)      
        
        #self.listWidget.setCurrentRow(0)
        
        try:
            if self._main_object_finder.show is True:
                self.listWidget.item(0).setCheckState(Qt.Checked)
            else:
                self.listWidget.item(0).setCheckState(Qt.Unchecked)
        except:
            pass
        
        if self._main_object_finder.timeout_exception is False:
            self.timeout_exception.setChecked(False)
        else:
            self.timeout_exception.setChecked(True)
        
        if self._main_object_finder.name == "":
            self.namelineedit.setText("Type the keyword name")
        else:
            self.namelineedit.setText(self._main_object_finder.name)      
            
        self.doubleSpinBoxWarning.setValue(self._main_object_finder.warning)
        self.doubleSpinBoxCritical.setValue(self._main_object_finder.critical)
            
        if self._main_object_finder.enable_performance is True:
            self.checkBoxEnablePerformance.setCheckState(Qt.Checked)
            self.doubleSpinBoxWarning.setEnabled(True)
            self.doubleSpinBoxCritical.setEnabled(True)
            self.labelWarning.setEnabled(True)
            self.labelCritical.setEnabled(True)
        else:
            self.checkBoxEnablePerformance.setCheckState(Qt.Unchecked)
            self.doubleSpinBoxWarning.setEnabled(False)
            self.doubleSpinBoxCritical.setEnabled(False)
            self.labelWarning.setEnabled(False)
            self.labelCritical.setEnabled(False)
                

                
        if main_object is not None:
        
            self.set_main_object_from_multiselection(self._path + os.sep + main_object)
        
            for sub_obj in sub_objects:
                self.add_sub_object_from_multiselection(self._path + os.sep + sub_obj)
        
        
        
        self.spinBoxArgs.setValue(self._main_object_finder.args_number)
        
        #print self._main_object_finder.args_number
        
        self.init_block_code()
                        
        self.pushButtonOk.setFocus()
        
        if self.namelineedit.text() == "Type the keyword name":
            self.namelineedit.setFocus()           
            self.namelineedit.setText("")  
        
        self.connect(self.listWidget, SIGNAL('itemSelectionChanged()'), self.listWidget_selection_changed)
        
        self.connect(self.pushButtonSelAll, SIGNAL('clicked()'), self.sel_all_event)
        self.connect(self.pushButtonDesAll, SIGNAL('clicked()'), self.des_all_event)
        self.connect(self.pushButtonDelete, SIGNAL('clicked()'), self.delete_event)
        
        
        self.connect(self.listWidget, SIGNAL('itemChanged(QListWidgetItem*)'), self, SLOT('listWidget_state_changed(QListWidgetItem*)'))
        
        self.connect(self.wait_radio, SIGNAL('toggled(bool)'), self.wait_radio_event)
        self.connect(self.wait_disapp_radio, SIGNAL('toggled(bool)'), self.wait_disapp_radio_event)
        self.connect(self.find_radio, SIGNAL('toggled(bool)'), self.find_radio_event)
        
        self.connect(self.timeout_spinbox, SIGNAL('valueChanged(int)'), self.timeout_spinbox_event)
        self.connect(self.timeout_exception, SIGNAL('stateChanged(int)'), self.timeout_exception_event)
        
        #self.connect(self.clickRadio, SIGNAL('toggled(bool)'), self.clickRadio_event)
        #self.connect(self.doubleclickRadio, SIGNAL('toggled(bool)'), self.doubleclickRadio_event)
        #self.connect(self.dontclickRadio, SIGNAL('toggled(bool)'), self.dontclickRadio_event)
        
        #self.connect(self.inserttext, SIGNAL("textChanged()"), self, SLOT("inserttext_event()"))
        self.connect(self.namelineedit, SIGNAL("textChanged(QString)"), self, SLOT("namelineedit_event(QString)"))
        self.connect(self.pushButtonAddBlock, SIGNAL('clicked()'), self.add_block_code)
        self.connect(self.pushButtonRemoveBlock, SIGNAL('clicked()'), self.remove_block_code)
        self.connect(self.listWidgetBlocks, SIGNAL('itemSelectionChanged()'), self.listWidgetBlocks_selection_changed)
        
        #self.inserttext.viewport().installEventFilter(self)
        #self.inserttext.installEventFilter(self)
        
        self.namelineedit.installEventFilter(self)
        
        #self.connect(self.tabWidget, SIGNAL('currentChanged(int)'), self.tab_changed_event)
        
        self.connect(self.checkBoxEnablePerformance, SIGNAL('stateChanged(int)'), self.enable_performance_event)
        self.connect(self.doubleSpinBoxWarning, SIGNAL('valueChanged(double)'), self.warning_event)
        self.connect(self.doubleSpinBoxCritical, SIGNAL('valueChanged(double)'), self.critical_event)
        
        self.connect(self.spinBoxArgs, SIGNAL('valueChanged(int)'), self.args_spinbox_change_event)
            
        self.connect(self.pushButtonSetMainObj, SIGNAL('clicked()'), self.open_select_obj_main)
        self.connect(self.pushButtonAddSubObj, SIGNAL('clicked()'), self.open_select_obj_sub)
        self.connect(self.pushButtonEditObj, SIGNAL('clicked()'), self.edit_obj)
        #self.connect(self.pushButtonRemoveObj, SIGNAL('clicked()'), self.remove_obj)
        
        self.connect(self.pushButtonOk, SIGNAL('clicked()'), self.pushButtonOk_event)
        self.connect(self.pushButtonCancel, SIGNAL('clicked()'), self.pushButtonCancel_event)
        
        ##################
        ##################
        
        self.connect(self.roi_x_spinbox, SIGNAL('valueChanged(int)'), self.roi_x_spinbox_event)
        self.connect(self.roi_y_spinbox, SIGNAL('valueChanged(int)'), self.roi_y_spinbox_event)
        self.connect(self.roi_height_spinbox, SIGNAL('valueChanged(int)'), self.roi_height_spinbox_event)
        self.connect(self.roi_width_spinbox, SIGNAL('valueChanged(int)'), self.roi_width_spinbox_event)
        
        #self.connect(self.clickRadio_2, SIGNAL('toggled(bool)'), self.clickRadio_event_2)
        #self.connect(self.doubleclickRadio_2, SIGNAL('toggled(bool)'), self.doubleclickRadio_event_2)
        #self.connect(self.dontclickRadio_2, SIGNAL('toggled(bool)'), self.dontclickRadio_event_2)
        
        #self.connect(self.inserttext_2, SIGNAL("textChanged()"), self, SLOT("inserttext_event_2()"))
        
        #self.inserttext_2.viewport().installEventFilter(self)
        #self.inserttext_2.installEventFilter(self)
        
        self.connect(self.pushButtonEditObj_2, SIGNAL('clicked()'), self.edit_obj_2)
        self.connect(self.pushButtonSetMainObj_2, SIGNAL('clicked()'), self.open_select_obj_main)
        self.connect(self.pushButtonAddSubObj_2, SIGNAL('clicked()'), self.open_select_obj_sub)
        #self.connect(self.pushButtonRoiRedraw, SIGNAL('clicked()'), self.redraw_roi_event)
        #self.connect(self.pushButtonRemoveObj_2, SIGNAL('clicked()'), self.remove_obj_2)
        
        self.textEditCustomLines.installEventFilter(self)
        self.roi_y_spinbox.installEventFilter(self)
        self.roi_height_spinbox.installEventFilter(self)
        self.roi_x_spinbox.installEventFilter(self)
        self.roi_width_spinbox.installEventFilter(self)
        
        if self.action == "edit":
            self.pv = PaintingView(self)
            #print self._main_object_finder.xml_path.replace("xml", "png")
            image = QImage(self._main_object_finder.xml_path.replace("xml", "png"))   
            self.pv.set_bg_pixmap(image)
            
            self.pv.showFullScreen()
        
        """
        if self.parent.last_view_index != 0:
            
            self.listWidget.setCurrentRow(self.parent.last_view_index)
        """
        
    def set_main_object_from_multiselection(self, xml_name):
        filename = xml_name
        filename = filename.split(os.sep)[-1]
        
        self._added_objects.append(((xml_name), open(xml_name).read()))
        
                    
        item = QListWidgetItem()
        
        path_main_xml = self._main_object_finder.xml_path
        main_obj = None           
        m_controller = dummy()
        m_controller.action = "new"
        m_controller.path = self.parent.path
        m_controller.scaling_factor = self.parent.scaling_factor
        m_controller.xml_name = filename
        m_controller.objectfinder_view = self
        
        if filename.endswith('_RectFinder.xml'):
            item.setText(filename[:-15] + " [RF]")
            main_obj = AlyvixRectFinderView(m_controller)
            main_obj.build_objects()
            main_obj = main_obj._main_rect_finder
        elif filename.endswith('_ImageFinder.xml'):
            item.setText(filename[:-16] + " [IF]")
            main_obj = AlyvixImageFinderView(m_controller)
            main_obj.build_objects()
            main_obj = main_obj._main_template
        elif filename.endswith('_TextFinder.xml'):
            item.setText(filename[:-15] + " [TF]")
            main_obj = AlyvixTextFinderView(m_controller)
            main_obj.build_objects()
            main_obj = main_obj._main_text
            
        item.setData(Qt.UserRole, filename)
        
        if self.listWidget.count() > 0:
            self.listWidget.takeItem(0)
            self.listWidget.insertItem(0, item)
        else:
            self.listWidget.addItem(item)
            
        #self._main_object_finder = MainObjectForGui()
        self._main_object_finder.xml_path = xml_name
        self._main_object_finder.x = main_obj.x
        self._main_object_finder.y = main_obj.y
        self._main_object_finder.height = main_obj.height
        self._main_object_finder.width = main_obj.width
        self._main_object_finder.mouse_or_key_is_set = main_obj.mouse_or_key_is_set
        
        #print self._main_object_finder.x
        #print self._main_object_finder.y
        #print self._main_object_finder.height
        #print self._main_object_finder.width
        
        #self.listWidget.addItem(item)
        #self.build_main_object()
        
        try:
            if self._main_object_finder.show is True:
                self.listWidget.item(0).setCheckState(Qt.Checked)
            else:
                self.listWidget.item(0).setCheckState(Qt.Unchecked)
        except:
            pass
        
        
        try:
            image = QImage(self._main_object_finder.xml_path.replace("xml", "png"))   
            self.pv.set_bg_pixmap(image)


        except:
            
            self.pv = PaintingView(self)
            #print self._main_object_finder.xml_path.replace("xml", "png")
            image = QImage(self._main_object_finder.xml_path.replace("xml", "png"))   
            self.pv.set_bg_pixmap(image)
            
        self.pv.showFullScreen()
        return True
            
    
    def add_sub_object_from_multiselection(self, xml_name):
    
        filename = xml_name
        filename = filename.split(os.sep)[-1]

        self._added_objects.append(((xml_name), open(xml_name).read()))
        
        scraper = False
        extra_path = get_python_lib() + os.sep + "alyvix" + os.sep + "robotproxy" + os.sep + self._path.split(os.sep)[-1] + "_extra"
        scraper_path = extra_path + os.sep + filename.replace("_TextFinder.xml","")
        scraper_file = scraper_path + os.sep + "scraper.txt"
        if os.path.exists(scraper_file):
            if self._main_object_finder.is_scraper is True:
                QMessageBox.critical(self, "Error", "You can add only one scraper object")
                return False
            else:
                self._main_object_finder.is_scraper = True
                scraper = True
        
        #self.update_lock_list(filename)
                    
        item = QListWidgetItem()
        
        main_obj = None           
        m_controller = dummy()
        m_controller.action = "new"
        m_controller.path = self._path
        m_controller.scaling_factor = self.scaling_factor
        m_controller.xml_name = filename
        m_controller.objectfinder_view = self

        if filename.endswith('_RectFinder.xml'):
            item.setText(filename[:-15] + " [RF]")
            main_obj = AlyvixRectFinderView(m_controller)
            main_obj.build_objects()
            main_obj = main_obj._main_rect_finder
        elif filename.endswith('_ImageFinder.xml'):
            item.setText(filename[:-16] + " [IF]")
            main_obj = AlyvixImageFinderView(m_controller)
            main_obj.build_objects()
            main_obj = main_obj._main_template
        elif filename.endswith('_TextFinder.xml'):
            if scraper is True:
                item.setText(filename[:-15] + " [TS]")
            else:
                item.setText(filename[:-15] + " [TF]")
            main_obj = AlyvixTextFinderView(m_controller)
            main_obj.build_objects()
            main_obj = main_obj._main_text

        item.setData(Qt.UserRole, filename)
        item.setCheckState(Qt.Checked)
        self.listWidget.addItem(item)
        
        sub_object = SubObjectForGui()
        sub_object.xml_path = xml_name
            
        sub_object.x = main_obj.x
        sub_object.y = main_obj.y
        sub_object.height = main_obj.height
        sub_object.width = main_obj.width
        
        if filename.endswith('_TextFinder.xml'):
            sub_object.roi_x = main_obj.roi_x - self._main_object_finder.x
            sub_object.roi_y = main_obj.roi_y - self._main_object_finder.y
            sub_object.roi_height = main_obj.roi_height
            sub_object.roi_width = main_obj.roi_width
            sub_object.is_textfinder = True
            
        else:
        
            hw_factor = 0
                                
            if sub_object.height < sub_object.width:
                hw_factor = sub_object.height
            else:
                hw_factor = sub_object.width
                
                
            sc_factor = 0
                                
            if self.pv._bg_pixmap.height() < self.pv._bg_pixmap.width():
                sc_factor = self.pv._bg_pixmap.height()
            else:
                sc_factor = self.pv._bg_pixmap.width()
                
            percentage_screen_w = int(0.0125 * sc_factor)
            percentage_screen_h = int(0.0125 * sc_factor)
            percentage_object_w = int(0.2 * hw_factor) #sub_object.width)
            percentage_object_h = int(0.2 * hw_factor) #sub_object.height)
            
            roi_height = percentage_screen_h + percentage_object_h + sub_object.height
            
            roi_width = percentage_screen_w + percentage_object_w + sub_object.width
            
            """
            hw_factor = 0

            if sub_object.height < sub_object.width:
                hw_factor = sub_object.height
            else:
                hw_factor = sub_object.width
                
            
            roi_height = int(0.95 * hw_factor) + sub_object.height

            roi_width = int(0.95 * hw_factor) + sub_object.width
            """

            roi_width_half = int((roi_width - sub_object.width)/2)

            roi_height_half = int((roi_height - sub_object.height)/2)


            sub_object.roi_x =  (sub_object.x - self._main_object_finder.x) - roi_width_half
            sub_object.roi_y =  (sub_object.y - self._main_object_finder.y) - roi_height_half
            sub_object.roi_height = sub_object.height + (roi_height_half*2)
            sub_object.roi_width = sub_object.width + (roi_width_half*2)

        
        sub_object.mouse_or_key_is_set = main_obj.mouse_or_key_is_set
        sub_object.scraper = scraper
        self._sub_objects_finder.append(sub_object)
        #self.build_sub_object(sub_object)
        
        self.pv.update()
        #image = QImage(self._main_object_finder.xml_path.replace("xml", "png"))   
        #self.pv.set_bg_pixmap(image)
        #self.pv.showFullScreen()
        #self.show()
        self._can_set_roi_unlim = True
        
        return True
    
    def saveUpdatedTextRoi(self):
        
        cnt = 0        
        for sub_obj in self._sub_objects_finder:
            if sub_obj.is_textfinder is True and cnt in self.text_finder_roi_modified:
                self.is_object_finder_menu = False
                s_controller = dummy()
                s_controller.set_parent(self)
                s_controller.action = "edit"
                s_controller.path = self.parent.path
                s_controller.robot_file_name =  self._robot_file_name
                s_controller.scaling_factor = self.parent.scaling_factor
                s_controller.xml_name = sub_obj.xml_path.split(os.sep)[-1]
                s_controller.objectfinder_view = self
                
                image = QImage(s_controller.path + os.sep + s_controller.xml_name.replace("xml", "png"))
                
                object = AlyvixTextFinderView(s_controller)
                    
                object.parent_is_objfinder = True
                
                object.set_bg_pixmap(image)
                
                object._main_text.roi_x = sub_obj.roi_x + self._main_object_finder.x
                object._main_text.roi_y = sub_obj.roi_y + self._main_object_finder.y
                object._main_text.roi_width = sub_obj.roi_width
                object._main_text.roi_height = sub_obj.roi_height
                
                object._main_text.roi_unlimited_up = sub_obj.roi_unlimited_up
                object._main_text.roi_unlimited_down = sub_obj.roi_unlimited_down
                object._main_text.roi_unlimited_left = sub_obj.roi_unlimited_left
                object._main_text.roi_unlimited_right = sub_obj.roi_unlimited_right
               
                
                object.save_all()
                #print "save_all"
                self.is_object_finder_menu = True
            cnt += 1
            
        self.text_finder_roi_modified = []
        self._old_main_object = copy.deepcopy(self._main_object_finder)
        self._old_sub_objects = copy.deepcopy(self._sub_objects_finder)
        
    def showEvent(self, event):
    
        #print self.parent.xx
        #print "object show event"
        global last_pos
        global last_row_selected
        if last_pos is not None:
            self.move(last_pos[0],last_pos[1])
            
        if self.listWidget.count() == 0:
            self.listWidget.setCurrentRow(0) 
            last_row_selected = 0             
        elif self.listWidget.count() > 0 and last_row_selected == -1:
            self.listWidget.setCurrentRow(0)  
            last_row_selected = 0
        elif last_row_selected != -1 and self.listWidget.count() > 0:
            self.listWidget.setCurrentRow(last_row_selected)

            
                
        
        
    def moveEvent(self, event):
        global last_pos
        last_pos = (self.frameGeometry().x(), self.frameGeometry().y())
        
    def save_all(self):
        #print self._old_object_finder_config
        #print self._added_objects
    
        if self._main_object_finder != None and self.ok_pressed is False:
            self.ok_pressed = True
            
            scraper_file_name = self._path + os.sep + self._main_object_finder.name + "_ObjectFinder.alyscraper"
            
            if self._main_object_finder.is_scraper is True:
                
                if not os.path.exists(scraper_file_name):
                    with open(scraper_file_name, 'w') as f:
                        
                        f.write("scraper=true")

                        f.close()
            else:
            
                if os.path.exists(scraper_file_name):
                    os.remove(scraper_file_name)
            
            self.build_code_array()
            self.update_lock_list()
            self.parent.update_list()
            self.build_xml()
            self.save_python_file()
            #self.build_perf_data_xml()
            #image_name = self._path + os.sep + self._main_object_finder.name + "_ImageFinder.png"
            #self._bg_pixmap.save(image_name,"PNG", -1)
            #self.save_template_images(image_name)
            #time.sleep(0.4)
            if self.action == "new":
                self.parent.add_new_item_on_list()
                
        try:
            if self.parent.is_AlyvixMainMenuController is True:
                self.parent.set_last_name(str(self._main_object_finder.name))
                self.parent.update_list()
        except:
            pass

        """
        self.parent.show()
        self.pv.close()
        try:
            self.pv.close()
        except:
            pass
        """
        self.close()
        
    def closeEvent(self, event):

        self.parent.show()
        
        try:
            self.pv.close()
        except:
            pass
        
        
    def cancel_all(self):
        #print "cancel"
        self._main_object_finder = copy.deepcopy(self._old_main_object)
        self._sub_objects_finder = copy.deepcopy(self._old_sub_objects)      
            
        self.is_object_finder_menu = False
         
        """
        if self._old_object_finder_config is not None:
            filename = self._old_object_finder_config[0]
            print "FILENAME", filename
            old_controller_config = self._old_object_finder_config[1]
            current_controller_config = open(filename, "r").read()

            
            if old_controller_config != current_controller_config:
                with open(filename, "w") as text_file:
                    text_file.write(old_controller_config)
        """
        
        for idx, added_obj in enumerate(self._added_objects):
            old_obj_config = added_obj[1]
            filename = added_obj[0]
            current_obj_config = open(filename, "r").read()
            
            if old_obj_config != current_obj_config:
            
                """
                with open(filename.replace(".xml", "_old.xml"), "w") as text_file:
                    text_file.write(old_obj_config)
                with open(filename.replace(".xml", "_curr.xml"), "w") as text_file:
                    text_file.write(current_obj_config)
                """                    
            
                m_controller = dummy()
                m_controller.set_parent(self)
                m_controller.action = "edit"
                m_controller.path = self.parent.path
                m_controller.robot_file_name =  self._robot_file_name
                m_controller.scaling_factor = self.parent.scaling_factor
                m_controller.xml_name = filename.split(os.sep)[-1]
                m_controller.objectfinder_view = self
                #m_controller.build_objects = False
                
                image = QImage(m_controller.path + os.sep + m_controller.xml_name.replace("xml", "png"))
                
                if filename.endswith('_RectFinder.xml'):
                    object = AlyvixRectFinderView(m_controller)
                    object._main_rect_finder = None
                    object._sub_rects_finder = []
                elif filename.endswith('_ImageFinder.xml'):
                    object = AlyvixImageFinderView(m_controller)
                    object._main_template = None
                    object._sub_templates_finder = []
                elif filename.endswith('_TextFinder.xml'):
                    object = AlyvixTextFinderView(m_controller)
                    object._main_text = None
                    object._sub_texts_finder = []
                    
                with open(filename, "w") as text_file:
                    text_file.write(old_obj_config)
                    
                object.build_objects()
                
                object.set_bg_pixmap(image)
                
                object.save_all()
                
        """
        if self.action == "edit":
            self.build_code_array()
            self.update_lock_list()
            self.parent.update_list()
            self.build_xml()
            self.save_python_file()   
        """
        if self._old_object_finder_config is not None:
            filename = self._old_object_finder_config[0]
            #print "FILENAME", filename
            old_controller_config = self._old_object_finder_config[1]
            current_controller_config = open(filename, "r").read()

            
            if old_controller_config != current_controller_config:
                with open(filename, "w") as text_file:
                    text_file.write(old_controller_config)
                    
            self._main_object_finder = MainObjectForGui()
            self._sub_objects_finder = []
            self.build_objects()
            self.update_lock_list()
            self.parent.update_list()
                    
            self.save_python_file() 
                    
        #print self._added_objects
        
                
        try:
            if self.parent.is_AlyvixMainMenuController is True:
                self.parent.update_list()
        except:
            pass
            
        """
        self.parent.show()
        try:
            self.pv.close()
        except:
            pass
        """
        self.close()
        
    def pushButtonCancel_event(self):
        #self.close()
        self.cancel_all()
        
    def is_valid_variable_name(self, name):
        try:
            parse('{} = None'.format(name))
            return True
        except (SyntaxError, ValueError, TypeError) as e:
            return False

    def pushButtonOk_event(self):
    
        if self._main_deleted is True:
        
            self.remove_code_from_py_file()
            
            deleted_obj_name = self.delete_lock_list()

            os.remove(self._path + os.sep + str(self._xml_name).replace("_ObjectFinder.xml","_old_code.txt"))
            

            if (os.path.exists(self._path + os.sep + str(self._xml_name).replace("_ObjectFinder.xml","_ObjectFinder.alyscraper"))):
                os.remove(self._path + os.sep + str(self._xml_name).replace("_ObjectFinder.xml","_ObjectFinder.alyscraper"))
                
            os.remove(self._path + os.sep + str(self._xml_name))
            
            #print "obj xml name", self._path + os.sep + str(self._xml_name)
                
            self.parent.update_list()
            self.parent.show()
            self.close()

            return
    
        answer = QMessageBox.Yes
        
        #print "name button", self._main_object_finder.name

        if self._main_object_finder.xml_path != "":
            filename = self._alyvix_proxy_path + os.sep + "AlyvixProxy" + self._robot_file_name + ".py"
                
            if self._main_object_finder.name == "":
                answer = QMessageBox.warning(self, "Warning", "The object name is empty. Do you want to create it automatically?", QMessageBox.Yes, QMessageBox.No)
            elif self.is_valid_variable_name(self.namelineedit.text()) is False or "#" in self.namelineedit.text():
                QMessageBox.critical(self, "Error", "Keyword name is invalid!")
                return
                
            elif os.path.isfile(filename) and self.action == "new":
                
                python_file = open(filename).read()
                
                #print filename
                
                obj_name = str(self._main_object_finder.name).lower()
                
                #print "obj_name:", obj_name
                
                if "def " + obj_name + "_mouse_keyboard(" in python_file or "def " + obj_name + "_build_object(" in python_file or "def " + obj_name + "(" in python_file:
                    QMessageBox.critical(self, "Error", "Keyword name already exists!")
                    return
            else:
                self.save_all()
                
            if answer == QMessageBox.Yes:
                self.close()
                self.save_all()
                
        else:
            QMessageBox.critical(self, "Error", "You have to set the main object before saving the object finder!")
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            if self._main_object_finder is None and self.esc_pressed is False:
                self.esc_pressed = True
                self.parent.show()
                self.close()
                try:
                    self.pv.close()
                except:
                    pass
            """
            self.parent.show()
            self.close()
            if self._main_object_finder != None and self.esc_pressed is False and self._main_object_finder.xml_path != "":
                self.esc_pressed = True
                self.build_code_array()
                self.build_xml()
                self.save_python_file()
                self.update_lock_list()
                self.build_perf_data_xml()
                #image_name = self._path + os.sep + self._main_object_finder.name + "_ImageFinder.png"
                #self._bg_pixmap.save(image_name,"PNG", -1)
                #self.save_template_images(image_name)
                #time.sleep(0.4)
                if self.action == "new":
                    self.parent.add_new_item_on_list()
                
            self.parent.show()
            self.close()
            """
    
    def delete_lock_list(self):
        filename = self._path + os.sep + "lock_list.xml"
        
        if os.path.exists(filename):
            doc = minidom.parse(filename)
            root_node = doc.getElementsByTagName("items")[0]
            
            items_node = doc.getElementsByTagName("item")
            
            main_name = None
            
            for item_node in items_node:
                
                owner = item_node.getElementsByTagName("owner")[0].firstChild.nodeValue
                name = item_node.getElementsByTagName("name")[0].firstChild.nodeValue.replace("_TextFinder.xml","").replace("_ImageFinder.xml","").replace("_RectFinder.xml","")
                
                if main_name == None:
                    main_name = name
                
                if owner == self._main_object_finder.name + "_ObjectFinder.xml":
                    root_node.removeChild(item_node)

            string = str(doc.toxml())
            python_file = open(filename, 'w')
            python_file.write(string)
            
        return main_name

    def update_lock_list(self):
    
        filename = self._path + os.sep + "lock_list.xml"
        
        if os.path.exists(filename):
            doc = minidom.parse(filename)
            root_node = doc.getElementsByTagName("items")[0]
            
            items_node = doc.getElementsByTagName("item")
            
            for item_node in items_node:
                owner = item_node.getElementsByTagName("owner")[0].firstChild.nodeValue
                if owner == self._main_object_finder.name + "_ObjectFinder.xml":
                    root_node.removeChild(item_node)
            
            item = doc.createElement("item")
            name = doc.createElement("name")
            txt = doc.createTextNode(self._main_object_finder.xml_path.split(os.sep)[-1])
            name.appendChild(txt)
            item.appendChild(name)

            owner = doc.createElement("owner")
            txt = doc.createTextNode(self._main_object_finder.name + "_ObjectFinder.xml")
            owner.appendChild(txt)
            item.appendChild(owner)
            root_node.appendChild(item)
            
            for sub_obj in self._sub_objects_finder:
                item = doc.createElement("item")
                name = doc.createElement("name")
                txt = doc.createTextNode(sub_obj.xml_path.split(os.sep)[-1])
                name.appendChild(txt)
                item.appendChild(name)

                owner = doc.createElement("owner")
                txt = doc.createTextNode(self._main_object_finder.name + "_ObjectFinder.xml")
                owner.appendChild(txt)
                item.appendChild(owner)
            
                root_node.appendChild(item)
            string = str(doc.toxml())
            python_file = open(filename, 'w')
            python_file.write(string)
            
        else:
            root = ET.Element("items")

            main_item_node = ET.SubElement(root, "item")
            
            name_node = ET.SubElement(main_item_node, "name")
            name_node.text = str(self._main_object_finder.xml_path.split(os.sep)[-1])
            
            name_node = ET.SubElement(main_item_node, "owner")
            name_node.text = str(self._main_object_finder.name + "_ObjectFinder.xml")
            
            for sub_obj in self._sub_objects_finder:
                main_item_node = ET.SubElement(root, "item")
            
                name_node = ET.SubElement(main_item_node, "name")
                name_node.text = str(sub_obj.xml_path.split(os.sep)[-1])

                name_node = ET.SubElement(main_item_node, "owner")
                name_node.text = str(self._main_object_finder.name + "_ObjectFinder.xml")
            
            #object_node = ET.SubElement(main_object_node, "object")
            #object_node.text = str(self._main_object_finder.click)
            
            tree = ET.ElementTree(root)
            python_file = open(filename, 'w')
            tree.write(python_file, encoding='utf-8', xml_declaration=True) 
            #python_file.write(rough_string)        
        python_file.close()
        
    def tiny_build_objects(self):
    
        #filename = open(self._path + os.sep + self._xml_name,"r")
        #print filename
        
        try:
            filehandler = open(self._path + os.sep + self._xml_name,"r")
        except:
            return

        doc = minidom.parse(filehandler)
        
        main_obj_xml_path = "xml_path"
        
        root_node = doc.getElementsByTagName("object_finder")[0]
        main_obj_node = doc.getElementsByTagName("main_object")[0]
        
        xml_name = main_obj_node.getElementsByTagName("xml_path")[0].firstChild.nodeValue
        
        main_obj = None           
        m_controller = dummy()
        m_controller.action = "new"
        m_controller.path = self.parent.path
        m_controller.scaling_factor = self.parent.scaling_factor
        m_controller.xml_name = xml_name.split(os.sep)[-1]
        m_controller.objectfinder_view = self
        
        if xml_name.endswith('_RectFinder.xml'):
            main_obj = AlyvixRectFinderView(m_controller)
            main_obj.build_objects()
            main_obj = main_obj._main_rect_finder
        elif xml_name.endswith('_ImageFinder.xml'):
            main_obj = AlyvixImageFinderView(m_controller)
            main_obj.build_objects()
            main_obj = main_obj._main_template
        elif xml_name.endswith('_TextFinder.xml'):
            main_obj = AlyvixTextFinderView(m_controller)
            main_obj.build_objects()
            main_obj = main_obj._main_text
            
        self._main_object_finder.x = main_obj.x
        self._main_object_finder.y = main_obj.y
        self._main_object_finder.height = main_obj.height
        self._main_object_finder.width = main_obj.width
        self._main_object_finder.mouse_or_key_is_set = main_obj.mouse_or_key_is_set
        
        sub_object_nodes = doc.getElementsByTagName("sub_object")
        
        cnt=0
        for sub_object_node in sub_object_nodes:
            filename = sub_object_node.getElementsByTagName("xml_path")[0].firstChild.nodeValue
                        
            item = QListWidgetItem()
            
            main_obj = None           
            m_controller = dummy()
            m_controller.action = "new"
            m_controller.path = self.parent.path
            m_controller.scaling_factor = self.parent.scaling_factor
            m_controller.xml_name = filename.split(os.sep)[-1]
            m_controller.objectfinder_view = self

            if filename.endswith('_RectFinder.xml'):
                main_obj = AlyvixRectFinderView(m_controller)
                main_obj.build_objects()
                main_obj = main_obj._main_rect_finder
            elif filename.endswith('_ImageFinder.xml'):
                main_obj = AlyvixImageFinderView(m_controller)
                main_obj.build_objects()
                main_obj = main_obj._main_template
            elif filename.endswith('_TextFinder.xml'):
                main_obj = AlyvixTextFinderView(m_controller)
                main_obj.build_objects()
                main_obj = main_obj._main_text
            
            self._sub_objects_finder[cnt].x = main_obj.x
            self._sub_objects_finder[cnt].y = main_obj.y
            self._sub_objects_finder[cnt].height = main_obj.height
            self._sub_objects_finder[cnt].width = main_obj.width
            if filename.endswith('_TextFinder.xml'):
                self._sub_objects_finder[cnt].is_textfinder = True
            else:
                self._sub_objects_finder[cnt].is_textfinder = False
            self._sub_objects_finder[cnt].mouse_or_key_is_set = main_obj.mouse_or_key_is_set
        
    
    def tiny_build_objects_2(self):
    
        #filename = open(self._path + os.sep + self._xml_name,"r")
        #print filename
        
        try:
            filehandler = open(self._path + os.sep + self._xml_name,"r")
        except:
            return

        doc = minidom.parse(filehandler)
        
        main_obj_xml_path = "xml_path"
        
        root_node = doc.getElementsByTagName("object_finder")[0]
        main_obj_node = doc.getElementsByTagName("main_object")[0]
        
        xml_name = main_obj_node.getElementsByTagName("xml_path")[0].firstChild.nodeValue
        
        main_obj = None           
        m_controller = dummy()
        m_controller.action = "new"
        m_controller.path = self.parent.path
        m_controller.scaling_factor = self.parent.scaling_factor
        m_controller.xml_name = xml_name.split(os.sep)[-1]
        m_controller.objectfinder_view = self
        
        if xml_name.endswith('_RectFinder.xml'):
            main_obj = AlyvixRectFinderView(m_controller)
            main_obj.build_objects()
            main_obj = main_obj._main_rect_finder
        elif xml_name.endswith('_ImageFinder.xml'):
            main_obj = AlyvixImageFinderView(m_controller)
            main_obj.build_objects()
            main_obj = main_obj._main_template
        elif xml_name.endswith('_TextFinder.xml'):
            main_obj = AlyvixTextFinderView(m_controller)
            main_obj.build_objects()
            main_obj = main_obj._main_text
            
        self._main_object_finder.x = main_obj.x
        self._main_object_finder.y = main_obj.y
        self._main_object_finder.height = main_obj.height
        self._main_object_finder.width = main_obj.width
        self._main_object_finder.mouse_or_key_is_set = main_obj.mouse_or_key_is_set
        
        sub_object_nodes = doc.getElementsByTagName("sub_object")
        
        cnt=0
        for sub_object_node in sub_object_nodes:
            filename = sub_object_node.getElementsByTagName("xml_path")[0].firstChild.nodeValue
                        
            item = QListWidgetItem()
            
            main_obj = None           
            m_controller = dummy()
            m_controller.action = "new"
            m_controller.path = self.parent.path
            m_controller.scaling_factor = self.parent.scaling_factor
            m_controller.xml_name = filename.split(os.sep)[-1]
            m_controller.objectfinder_view = self

            if filename.endswith('_RectFinder.xml'):
                main_obj = AlyvixRectFinderView(m_controller)
                main_obj.build_objects()
                main_obj = main_obj._main_rect_finder
            elif filename.endswith('_ImageFinder.xml'):
                main_obj = AlyvixImageFinderView(m_controller)
                main_obj.build_objects()
                main_obj = main_obj._main_template
            elif filename.endswith('_TextFinder.xml'):
                main_obj = AlyvixTextFinderView(m_controller)
                main_obj.build_objects()
                main_obj = main_obj._main_text
                main_obj.is_textfinder = True
            
            self._sub_objects_finder[cnt].x = main_obj.x
            self._sub_objects_finder[cnt].y = main_obj.y
            self._sub_objects_finder[cnt].height = main_obj.height
            self._sub_objects_finder[cnt].width = main_obj.width
            if filename.endswith('_TextFinder.xml'):
                self._sub_objects_finder[cnt].is_textfinder = True
            else:
                self._sub_objects_finder[cnt].is_textfinder = False
            self._sub_objects_finder[cnt].mouse_or_key_is_set = main_obj.mouse_or_key_is_set
        
    
    
    def build_objects(self):
        
        #filename = open(self._path + os.sep + self._xml_name,"r")
        #print filename
        #print "build_object"
        try:
            filehandler = open(self._path + os.sep + self._xml_name,"r")
        except:
            return
            
        self._old_object_finder_config = (self._path + os.sep + self._xml_name, open(self._path + os.sep + self._xml_name, "r").read())

        doc = minidom.parse(filehandler)
        
        main_obj_xml_path = "xml_path"
        
        root_node = doc.getElementsByTagName("object_finder")[0]
        main_obj_node = doc.getElementsByTagName("main_object")[0]

        xml_name = main_obj_node.getElementsByTagName("xml_path")[0].firstChild.nodeValue
        xml_name = self._path + os.sep + xml_name.split(os.sep)[-1]
        
        self._added_objects.append(((xml_name), open(xml_name).read()))
        
        main_obj = None           
        m_controller = dummy()
        m_controller.action = "new"
        m_controller.path = self.parent.path
        m_controller.scaling_factor = self.parent.scaling_factor
        m_controller.xml_name = xml_name.split(os.sep)[-1]
        m_controller.objectfinder_view = self
        
        if xml_name.endswith('_RectFinder.xml'):
            main_obj = AlyvixRectFinderView(m_controller)
            main_obj.build_objects()
            main_obj = main_obj._main_rect_finder
        elif xml_name.endswith('_ImageFinder.xml'):
            main_obj = AlyvixImageFinderView(m_controller)
            main_obj.build_objects()
            main_obj = main_obj._main_template
        elif xml_name.endswith('_TextFinder.xml'):
            main_obj = AlyvixTextFinderView(m_controller)
            main_obj.build_objects()
            main_obj = main_obj._main_text
            
        #print "objjjjj", xml_name
        self._main_object_finder = MainObjectForGui()
        self._main_object_finder.xml_path = self._path + os.sep + os.path.basename(xml_name) #xml_name
        #print "xml path:", self._main_object_finder.xml_path
        #print self._path + os.sep + os.path.basename(self._main_object_finder.xml_path)
        self._main_object_finder.x = main_obj.x
        self._main_object_finder.y = main_obj.y
        self._main_object_finder.height = main_obj.height
        self._main_object_finder.width = main_obj.width
        self._main_object_finder.mouse_or_key_is_set = main_obj.mouse_or_key_is_set
        
        self._main_object_finder.name = root_node.attributes["name"].value
        #self._main_object_finder.find = main_obj_node.attributes["find"].value
        #self._main_object_finder.wait = main_obj_node.attributes["wait"].value
        self._main_object_finder.timeout = int(root_node.attributes["timeout"].value)
        
        if root_node.attributes["timeout_exception"].value == "True":
            self._main_object_finder.timeout_exception = True
        else:
            self._main_object_finder.timeout_exception = False
        
        self._main_object_finder.args_number = int(root_node.attributes["args"].value)
        
        if "True" in root_node.attributes["find"].value: #main_obj_node.getElementsByTagName("find")[0].firstChild.nodeValue:
            self._main_object_finder.find = True
        else:
            self._main_object_finder.find = False    
            
        if "True" in root_node.attributes["wait"].value: #main_obj_node.getElementsByTagName("wait")[0].firstChild.nodeValue:
            self._main_object_finder.wait = True
        else:
            self._main_object_finder.wait = False    
            
        try:
            if "True" in root_node.attributes["wait_disapp"].value: #main_template_node.getElementsByTagName("wait")[0].firstChild.nodeValue:
                self._main_object_finder.wait_disapp = True
            else:
                self._main_object_finder.wait_disapp = False
        except:
            self._main_object_finder.wait_disapp = False
            
        if "True" in root_node.attributes["enable_performance"].value:
            self._main_object_finder.enable_performance = True
        else:
            self._main_object_finder.enable_performance = False
            
        try:
            if root_node.attributes["scraper"].value == "True":
                self._main_object_finder.is_scraper = True
            else:
                self._main_object_finder.is_scraper = False
        except:
            self._main_object_finder.is_scraper = False
            
        self._main_object_finder.warning = float(root_node.attributes["warning_value"].value)
            
        self._main_object_finder.critical = float(root_node.attributes["critical_value"].value)
        
        #self.__flag_capturing_main_rect = False
        #self.__flag_capturing_sub_rect_roi = True
                
        sub_object_nodes = doc.getElementsByTagName("sub_object")
        
        for sub_object_node in sub_object_nodes:
            filename = sub_object_node.getElementsByTagName("xml_path")[0].firstChild.nodeValue
            filename = self._path + os.sep + filename.split(os.sep)[-1]
            
            self._added_objects.append(((filename), open(filename).read()))
                        
            item = QListWidgetItem()
            
            main_obj = None           
            m_controller = dummy()
            m_controller.action = "new"
            m_controller.path = self.parent.path
            m_controller.scaling_factor = self.parent.scaling_factor
            m_controller.xml_name = filename.split(os.sep)[-1]
            m_controller.objectfinder_view = self

            if filename.endswith('_RectFinder.xml'):
                main_obj = AlyvixRectFinderView(m_controller)
                main_obj.build_objects()
                main_obj = main_obj._main_rect_finder
            elif filename.endswith('_ImageFinder.xml'):
                main_obj = AlyvixImageFinderView(m_controller)
                main_obj.build_objects()
                main_obj = main_obj._main_template
            elif filename.endswith('_TextFinder.xml'):
                main_obj = AlyvixTextFinderView(m_controller)
                main_obj.build_objects()
                main_obj = main_obj._main_text
            
            sub_object = SubObjectForGui()
            sub_object.xml_path = self._path + os.sep + os.path.basename(filename)
                
            if filename.endswith('_TextFinder.xml'):
                sub_object.is_textfinder = True
                
            sub_object.x = main_obj.x
            sub_object.y = main_obj.y
            sub_object.height = main_obj.height
            sub_object.width = main_obj.width
            sub_object.mouse_or_key_is_set = main_obj.mouse_or_key_is_set
            
            sub_object.roi_x = int(sub_object_node.getElementsByTagName("roi_x")[0].firstChild.nodeValue)
            sub_object.roi_y = int(sub_object_node.getElementsByTagName("roi_y")[0].firstChild.nodeValue)
            sub_object.roi_width = int(sub_object_node.getElementsByTagName("roi_width")[0].firstChild.nodeValue)
            sub_object.roi_height = int(sub_object_node.getElementsByTagName("roi_height")[0].firstChild.nodeValue)
            
            try:
                if "True" in sub_object_node.getElementsByTagName("roi_unlimited_up")[0].firstChild.nodeValue:
                    sub_object.roi_unlimited_up = True
                else:
                    sub_object.roi_unlimited_up = False
            except:
                sub_object.roi_unlimited_up = False
                
            try:
                if "True" in sub_object_node.getElementsByTagName("roi_unlimited_down")[0].firstChild.nodeValue:
                    sub_object.roi_unlimited_down = True
                else:
                    sub_object.roi_unlimited_down = False
            except:
                sub_object.roi_unlimited_down = False
                
            try:
                if "True" in sub_object_node.getElementsByTagName("roi_unlimited_left")[0].firstChild.nodeValue:
                    sub_object.roi_unlimited_left = True
                else:
                    sub_object.roi_unlimited_left = False
            except:
                sub_object.roi_unlimited_left = False
                
            try:
                if "True" in sub_object_node.getElementsByTagName("roi_unlimited_right")[0].firstChild.nodeValue:
                    sub_object.roi_unlimited_right = True
                else:
                    sub_object.roi_unlimited_right = False
            except:
                sub_object.roi_unlimited_right = False
            
            self._sub_objects_finder.append(sub_object)
            
        sub_block_nodes = doc.getElementsByTagName("code_block")
        
        #print len(sub_rect_nodes)

        for sub_block_node in sub_block_nodes:

            start_line = int(sub_block_node.getElementsByTagName("start_line")[0].firstChild.nodeValue)
            end_line = int(sub_block_node.getElementsByTagName("end_line")[0].firstChild.nodeValue)
            code = sub_block_node.getElementsByTagName("code")[0].toxml()
            
            code = code.replace("<code><!-- -->","")
            code = code.replace("<!-- --></code>","")
            code = code.replace("<![CDATA[","")
            code = code.replace("]]>","")

            #print code.encode('utf-8')
            self._code_blocks.append((start_line, code.encode('utf-8'), end_line))
            #print sub_block_node.childNodes[0].nodeValue #sub_block_node.toxml()
     
    def build_perf_data_xml(self):
    
        filename = self._path + os.sep + "perf_data.xml"
    
        if os.path.exists(filename):
            perf_is_present = False
            
            doc = minidom.parse(filename)
            root_node = doc.getElementsByTagName("performance")[0]
            
            items_node = doc.getElementsByTagName("perfdata")
            
            for item_node in items_node:
                name = item_node.getElementsByTagName("name")[0].firstChild.nodeValue
                if name == self._main_object_finder.name and self._main_object_finder.enable_performance is False:
                    root_node.removeChild(item_node)
                elif name == self._main_object_finder.name:
                    perf_is_present = True
                    
            if perf_is_present is False and self._main_object_finder.enable_performance is True:
                item = doc.createElement("perfdata")
                
                name = doc.createElement("name")
                txt = doc.createTextNode(self._main_object_finder.name)
                name.appendChild(txt)
                item.appendChild(name)

                warning = doc.createElement("warning")
                txt = doc.createTextNode(str(self._main_object_finder.warning))
                warning.appendChild(txt)
                item.appendChild(warning)
                
                critical = doc.createElement("critical")
                txt = doc.createTextNode(str(self._main_object_finder.critical))
                critical.appendChild(txt)
                item.appendChild(critical)
                
                root_node.appendChild(item)

            string = str(doc.toxml())
            python_file = open(filename, 'w')
            python_file.write(string)

        else:
            root = ET.Element("performance")

            main_item_node = ET.SubElement(root, "perfdata")
            
            name_node = ET.SubElement(main_item_node, "name")
            name_node.text = str(self._main_object_finder.name)
            
            warning_node = ET.SubElement(main_item_node, "warning")
            warning_node.text = str(self._main_object_finder.warning)
            
            critical_node = ET.SubElement(main_item_node, "critical")
            critical_node.text = str(self._main_object_finder.critical)
            
            tree = ET.ElementTree(root)
            python_file = open(filename, 'w')
            tree.write(python_file, encoding='utf-8', xml_declaration=True) 
            #python_file.write(rough_string)        
        python_file.close()  
    
    def build_code_string(self):
    
        last_block_line = 0
        lines = 0
        
        for block in self._code_blocks:
            start_line = block[0]
            end_line = block[2]
            lines = lines + (end_line - start_line) + 1
            
            if end_line > last_block_line:
                last_block_line = end_line
                
        #print "lines", lines
        #print "code lines", len(self._code_lines)
                
        while(len(self._code_lines) - 1 + lines < last_block_line):
            
            self._code_lines.append("")
            
    
        string = ""
        
        line_cnt = 1
        for element in self._code_lines:
            
            for block in self._code_blocks:
                code_line = block[0]
                code_text = unicode(block[1], 'utf-8')
                #print "code_text:", code_text
                
                if code_line == line_cnt:
                    
                    string = string + code_text + os.linesep
                    
                    line_cnt = line_cnt + len(str(code_text.encode('utf-8')).split("\n"))
                
            string = string + element + os.linesep
            line_cnt = line_cnt + 1

        #string = string[:-1]
        return string.encode('UTF-8')
        
    def build_code_array(self):
    
        mouse_or_key_is_set = False
        
        #print "self._main_object_finder.mouse_or_key_is_set:", self._main_object_finder.mouse_or_key_is_set
        
    
        total_args = 0 #self._main_object_finder.args_number
    
        self.building_code = True
    
        kmanager_declared = False
        mmanager_declared = False
       
        if self._main_object_finder is None:
            return
            
        self._code_lines = []
        self._code_lines_for_object_finder = []
            
        name = self._main_object_finder.name
        
        if name == "":
            name = time.strftime("object_finder_%d_%m_%y_%H_%M_%S")
            self._main_object_finder.name = name
            
        #self._code_lines.append("def " + name + "():")
        
        str_global_obj = ""
        str_build_obj = ""
        str_set_main_obj = ""
        main_obj_name = ""
        
        path_main_xml = self._main_object_finder.xml_path
        main_obj = None           
        m_controller = dummy()
        m_controller.action = "new"
        m_controller.path = self.parent.path
        m_controller.scaling_factor = self.parent.scaling_factor
        m_controller.xml_name = path_main_xml.split(os.sep)[-1]
        m_controller.objectfinder_view = self
        
        if m_controller.xml_name == "":
            return
            
        arg_main_component = 0
        if path_main_xml.endswith('_RectFinder.xml'):
            main_obj = AlyvixRectFinderView(m_controller)
            arg_main_component = main_obj.args_number
            main_obj_name = main_obj.object_name
        elif path_main_xml.endswith('_ImageFinder.xml'):
            main_obj = AlyvixImageFinderView(m_controller)
            arg_main_component = main_obj.args_number
            main_obj_name = main_obj.object_name
        elif path_main_xml.endswith('_TextFinder.xml'):
            main_obj = AlyvixTextFinderView(m_controller)
            arg_main_component = main_obj.args_number
            main_obj_name = main_obj.object_name
          
        #print "main_obj.mouse_or_key_is_set ", main_obj.mouse_or_key_is_set 
        if main_obj.mouse_or_key_is_set is True:
            mouse_or_key_is_set = True
        
        total_args = total_args + arg_main_component
        str_global_obj = "    global " + main_obj_name + "_object"
        
        string_function_args = "    " + main_obj_name + "_build_object("
        
        args_range = range(1, arg_main_component + 1)
        
        last_arg_num = 0
        for arg_num in args_range:
            string_function_args = string_function_args + "arg" + str(arg_num) + ", " 
            last_arg_num = arg_num
        
        self._arg_index_processed = self._arg_index_processed + last_arg_num
        
        if string_function_args.endswith(", "):
            string_function_args = string_function_args[:-2]
        string_function_args = string_function_args + ")"
        str_build_obj = string_function_args
        
        if last_arg_num != 0:
            obj_args_str2 = string_function_args.replace("    " + main_obj_name + "_build_object(", "")
            obj_args_str2 = obj_args_str2.replace(")","")
            self._main_object_finder.component_args = obj_args_str2
        else:
            self._main_object_finder.component_args = ""
        
        #str_build_obj = "    " + main_obj_name + "_build_object()"
        str_set_main_obj = "    object_finder.set_main_object(" + main_obj_name + "_object)"
        
        str_lines_sub_obj = []
        cnt = 1
        for sub_object in self._sub_objects_finder:
            if sub_object.height != 0 and sub_object.width !=0:
            
                #print "sub_object.mouse_or_key_is_set:", sub_object.mouse_or_key_is_set
            
                arg_sub_component = 0
                #roi_x = str(sub_object.roi_x - self._main_object_finder.x)
                roi_x = str(sub_object.roi_x)
                roi_y = str(sub_object.roi_y)
                
                roi_width = str(sub_object.roi_width)
                roi_height = str(sub_object.roi_height)
                
                roi_unlimited_up = str(sub_object.roi_unlimited_up)
                roi_unlimited_down = str(sub_object.roi_unlimited_down)
                roi_unlimited_left = str(sub_object.roi_unlimited_left)
                roi_unlimited_right = str(sub_object.roi_unlimited_right)
                
                path_sub_xml = sub_object.xml_path
                sub_obj = None           
                s_controller = dummy()
                s_controller.action = "new"
                s_controller.path = self.parent.path
                s_controller.scaling_factor = self.parent.scaling_factor
                s_controller.xml_name = path_sub_xml.split(os.sep)[-1]
                s_controller.objectfinder_view = self
        
                if path_sub_xml.endswith('_RectFinder.xml'):
                    sub_obj = AlyvixRectFinderView(s_controller)
                    sub_obj_name = sub_obj.object_name
                    arg_sub_component = sub_obj.args_number
                elif path_sub_xml.endswith('_ImageFinder.xml'):
                    sub_obj = AlyvixImageFinderView(s_controller)
                    sub_obj_name = sub_obj.object_name
                    arg_sub_component = sub_obj.args_number
                elif path_sub_xml.endswith('_TextFinder.xml'):
                    sub_obj = AlyvixTextFinderView(s_controller)
                    sub_obj_name = sub_obj.object_name
                    arg_sub_component = sub_obj.args_number
                
                total_args = total_args + arg_sub_component
                str_lines_sub_obj.append("    global " + sub_obj_name + "_object")
                
                #print "mss", sub_obj.mouse_or_key_is_set
                
                if sub_obj.mouse_or_key_is_set is True:
                    #print "sub_click_ok"
                    mouse_or_key_is_set = True
                
                
                string_function_args = "    " + sub_obj_name + "_build_object("
        
                args_range = range(last_arg_num + 1, last_arg_num + arg_sub_component + 1)
                
                last_arg_num = 0
                for arg_num in args_range:
                    string_function_args = string_function_args + "arg" + str(arg_num) + ", " 
                    last_arg_num = arg_num
                    
                self._arg_index_processed = self._arg_index_processed + last_arg_num
                
                if string_function_args.endswith(", "):
                    string_function_args = string_function_args[:-2]
                string_function_args = string_function_args + ")"
                
                str_lines_sub_obj.append(string_function_args)
                
                if last_arg_num != 0:
                    sub_obj_args_str2 = string_function_args.replace("    " + sub_obj_name + "_build_object(", "")
                    sub_obj_args_str2 = sub_obj_args_str2.replace(")","")
                    sub_object.component_args = sub_obj_args_str2
                else:
                    sub_object.component_args = ""
                
                
                
                
                
                str_lines_sub_obj.append("    object_finder.add_sub_object(" + sub_obj_name + "_object, {\"roi_x\": " + roi_x + ", \"roi_y\": " + roi_y + ", \"roi_width\": " + roi_width + ", \"roi_height\": " + roi_height + ", \"roi_unlimited_up\": " + roi_unlimited_up + ", \"roi_unlimited_down\": " + roi_unlimited_down + ", \"roi_unlimited_left\": " + roi_unlimited_left + ", \"roi_unlimited_right\": " + roi_unlimited_right + "})")

                #sub_obj.build_code_array()
                #str_lines_sub_obj.extend(sub_obj._code_lines_for_object_finder)
                #str_lines_sub_obj.append(strcode)
                #str_lines_sub_obj_for_object_finder.append(strcode)

                cnt = cnt + 1
        
        string_function_args = "def " + name + "("
        
        if self._main_object_finder.args_number == 0:
            args_range = range(1, total_args + 1)
        else:
            args_range = range(1, self._main_object_finder.args_number + 1)
        
        for arg_num in args_range:
            string_function_args = string_function_args + "arg" + str(arg_num) + ", " 
        
        if string_function_args.endswith(", "):
            string_function_args = string_function_args[:-2]
        string_function_args = string_function_args + "):"
        self._code_lines.append(string_function_args)
        
        #self._code_lines.append("\n")
        strcode = "    object_finder = ObjectFinder(\"" + name + "\")"
        self._code_lines.append(strcode)
        #self._code_lines_for_object_finder.append(strcode)
        #self._code_lines.append("\n")
        
        """
        path_main_xml = self._main_object_finder.xml_path
        main_obj = None           
        m_controller = dummy()
        m_controller.action = "new"
        m_controller.path = self.parent.path
        m_controller.xml_name = path_main_xml.split(os.sep)[-1]
        
        if m_controller.xml_name == "":
            return
 
        #print m_controller.path
        #print m_controller.xml_name
        
        
        if path_main_xml.endswith('_RectFinder.xml'):
            main_obj = AlyvixRectFinderView(m_controller)
            main_obj_name = main_obj._main_rect_finder.name
            self._code_lines.append("    global " + main_obj_name + "_object")
            self._code_lines.append("    " + main_obj_name + "_build_object()")
            strcode = "    object_finder.set_main_object(" + main_obj_name + "_object)"
        elif path_main_xml.endswith('_ImageFinder.xml'):
            main_obj = AlyvixImageFinderView(m_controller)
            main_obj_name = main_obj._main_template.name
            self._code_lines.append("    global " + main_obj_name + "_object")
            self._code_lines.append("    " + main_obj_name + "_build_object()")
            strcode = "    object_finder.set_main_object(" + main_obj_name + "_object)"
        elif path_main_xml.endswith('_TextFinder.xml'):
            main_obj = AlyvixTextFinderView(m_controller)
            main_obj_name = main_obj._main_text.name
            self._code_lines.append("    global " + main_obj_name + "_object")
            self._code_lines.append("    " + main_obj_name + "_build_object()")
            strcode = "    object_finder.set_main_object(" + main_obj_name + "_object)"
        """
        
        #main_obj.build_code_array()
            
        #self._code_lines.extend(main_obj._code_lines_for_object_finder)
        
        self._code_lines.append(str_global_obj)
        self._code_lines.append(str_build_obj)
        self._code_lines.append(str_set_main_obj)
        #self._code_lines_for_object_finder.append(strcode)
        
        #self._code_lines.append("\n")
        
        """
        cnt = 1
        for sub_object in self._sub_objects_finder:
            if sub_object.height != 0 and sub_object.width !=0:
            
                #roi_x = str(sub_object.roi_x - self._main_object_finder.x)
                roi_x = str(sub_object.roi_x)
                roi_y = str(sub_object.roi_y)
                
                roi_width = str(sub_object.roi_width)
                roi_height = str(sub_object.roi_height)
                
                path_sub_xml = sub_object.xml_path
                sub_obj = None           
                s_controller = dummy()
                s_controller.action = "new"
                s_controller.path = self.parent.path
                s_controller.xml_name = path_sub_xml.split(os.sep)[-1]
        
                if path_sub_xml.endswith('_RectFinder.xml'):
                    sub_obj = AlyvixRectFinderView(s_controller)
                    sub_obj_name = sub_obj._main_rect_finder.name
                    self._code_lines.append("    global " + sub_obj_name + "_object")
                    self._code_lines.append("    " + sub_obj_name + "_build_object()")
                    strcode = "    object_finder.add_sub_object(" + sub_obj_name + "_object, {\"roi_x\": " + roi_x + ", \"roi_y\": " + roi_y + ", \"roi_width\": " + roi_width + ", \"roi_height\": " + roi_height + "})"
                elif path_sub_xml.endswith('_ImageFinder.xml'):
                    sub_obj = AlyvixImageFinderView(s_controller)
                    sub_obj_name = sub_obj._main_template.name
                    self._code_lines.append("    global " + sub_obj_name + "_object")
                    self._code_lines.append("    " + sub_obj_name + "_build_object()")
                    strcode = "    object_finder.add_sub_object(" + sub_obj_name + "_object, {\"roi_x\": " + roi_x + ", \"roi_y\": " + roi_y + ", \"roi_width\": " + roi_width + ", \"roi_height\": " + roi_height + "})"
                elif path_sub_xml.endswith('_TextFinder.xml'):
                    sub_obj = AlyvixTextFinderView(s_controller)
                    sub_obj_name = sub_obj._main_text.name
                    self._code_lines.append("    global " + sub_obj_name + "_object")
                    self._code_lines.append("    " + sub_obj_name + "_build_object()")
                    strcode = "    object_finder.add_sub_object(" + sub_obj_name + "_object, {\"roi_x\": " + roi_x + ", \"roi_y\": " + roi_y + ", \"roi_width\": " + roi_width + ", \"roi_height\": " + roi_height + "})"

                sub_obj.build_code_array()
                #self._code_lines.extend(sub_obj._code_lines_for_object_finder)
                self._code_lines.append(strcode)
                self._code_lines_for_object_finder.append(strcode)

                cnt = cnt + 1
        """
        
        self._code_lines.extend(str_lines_sub_obj)
        
        if self._main_object_finder.timeout_exception is False:
        
            self._code_lines.append("    info_manager = InfoManager()")
            self._code_lines.append("    info_manager.set_info(\"DISABLE REPORTS\", True)")
        
                
        if self._main_object_finder.find is True:  
            self._code_lines.append("    object_finder.find()")
        elif self._main_object_finder.wait is True or mouse_or_key_is_set is True:
            self._code_lines.append("    timeout = " + str(self._main_object_finder.timeout))
            self._code_lines.append("    wait_time = object_finder.wait(timeout)")
        elif self._main_object_finder.wait_disapp is True:
            self._code_lines.append("    timeout = " + str(self._main_object_finder.timeout))
            self._code_lines.append("    wait_time = object_finder.wait_disappear(timeout)")

        if self._main_object_finder.enable_performance is True and self._main_object_finder.find is False:  
            self._code_lines.append("    if wait_time == -1:")
            if self._main_object_finder.timeout_exception is True:
                self._code_lines.append("        raise Exception(\"step " + str(self._main_object_finder.name) + " timed out, execution time: " + str(self._main_object_finder.timeout) + "\")")                
            else:
                self._code_lines.append("        print \"*WARN* step " + str(self._main_object_finder.name) + " timed out, execution time: " + str(self._main_object_finder.timeout) + "\"")
                self._code_lines.append("        return False")
            if self._main_object_finder.wait_disapp is True and mouse_or_key_is_set is True:
                pass
            else:    
                self._code_lines.append("    elif wait_time < " + repr(self._main_object_finder.warning) + ":")
                self._code_lines.append("        print \"step " + self._main_object_finder.name + " is ok, execution time:\", wait_time, \"sec.\"")
                self._code_lines.append("    elif wait_time < " + repr(self._main_object_finder.critical) + ":")
                self._code_lines.append("        print \"*WARN* step " + str(self._main_object_finder.name) + " has exceeded the performance warning threshold:\", wait_time, \"sec.\"")
                self._code_lines.append("    else:")
                self._code_lines.append("        print \"*WARN* step " + str(self._main_object_finder.name) + " has exceeded the performance critical threshold:\", wait_time, \"sec.\"")
                self._code_lines.append("    p = PerfManager()")
                self._code_lines.append("    p.add_perfdata(\"" + str(self._main_object_finder.name) + "\", wait_time, " + repr(self._main_object_finder.warning) + ", " + repr(self._main_object_finder.critical) + ")")
        elif self._main_object_finder.find is False:
            self._code_lines.append("    if wait_time == -1:")
            if self._main_object_finder.timeout_exception is True:
                self._code_lines.append("        raise Exception(\"step " + str(self._main_object_finder.name) + " timed out, execution time: " + str(self._main_object_finder.timeout) + "\")")             
            else:
                self._code_lines.append("        print \"*WARN* step " + str(self._main_object_finder.name) + " timed out, execution time: " + str(self._main_object_finder.timeout) + "\"")
                if self._main_object_finder.is_scraper is True:
                    self._code_lines.append("        return \"\"")
                else:
                    self._code_lines.append("        return False")
        
        #print "self._main_object_finder.mouse_or_key_is_set", self._main_object_finder.mouse_or_key_is_set
        if self._main_object_finder.mouse_or_key_is_set:
            self._code_lines.append("    " + main_obj_name + "_mouse_keyboard(" + self._main_object_finder.component_args + ")")
            
        cnt = 0
        for sub_object in self._sub_objects_finder:
            
            try:
                if sub_object.scraper is True:
                    continue
            except:
                pass
                
            if sub_object.height != 0 and sub_object.width !=0:
            
                sub_mouse_or_keyboard_is_set = False
                
                path_sub_xml = sub_object.xml_path
                sub_obj = None           
                s_controller = dummy()
                s_controller.action = "new"
                s_controller.path = self.parent.path
                s_controller.scaling_factor = self.parent.scaling_factor
                s_controller.xml_name = path_sub_xml.split(os.sep)[-1]
                s_controller.objectfinder_view = self
        
                if path_sub_xml.endswith('_RectFinder.xml'):
                    sub_obj = AlyvixRectFinderView(s_controller)
                elif path_sub_xml.endswith('_ImageFinder.xml'):
                    sub_obj = AlyvixImageFinderView(s_controller)
                elif path_sub_xml.endswith('_TextFinder.xml'):
                    sub_obj = AlyvixTextFinderView(s_controller)
                    
                    
                    
                sub_obj_name = sub_obj.object_name
                
                if sub_obj.mouse_or_key_is_set:
                    self._code_lines.append("    " + sub_obj_name + "_mouse_keyboard(" + sub_object.component_args + ")")

            cnt+=1
                    
        
        if self._main_object_finder.is_scraper is True:
            self._code_lines.append("    return object_finder.get_scraped_text()") 
        
        if self._main_object_finder.wait_disapp is True and mouse_or_key_is_set is True:   
            self._code_lines.append("    timeout = timeout - wait_time")
            self._code_lines.append("    wait_time_disappear = object_finder.wait_disappear(timeout)")  
            if self._main_object_finder.enable_performance is True and self._main_object_finder.find is False:  
                self._code_lines.append("    if wait_time_disappear == -1:")
                if self._main_object_finder.timeout_exception is True:
                    self._code_lines.append("        raise Exception(\"step " + str(self._main_object_finder.name) + " timed out, execution time: " + str(self._main_object_finder.timeout) + "\")")             
                else:
                    self._code_lines.append("        print \"*WARN* step " + str(self._main_object_finder.name) + " timed out, execution time: " + str(self._main_object_finder.timeout) + "\"")
                    self._code_lines.append("        return False")
                    
                self._code_lines.append("    elif wait_time + wait_time_disappear < " + repr(self._main_object_finder.warning) + ":")
                self._code_lines.append("        print \"step " + self._main_object_finder.name + " is ok, execution time:\", wait_time + wait_time_disappear, \"sec.\"")
                self._code_lines.append("    elif wait_time + wait_time_disappear < " + repr(self._main_object_finder.critical) + ":")
                self._code_lines.append("        print \"*WARN* step " + str(self._main_object_finder.name) + " has exceeded the performance warning threshold:\", wait_time + wait_time_disappear, \"sec.\"")
                self._code_lines.append("    else:")
                self._code_lines.append("        print \"*WARN* step " + str(self._main_object_finder.name) + " has exceeded the performance critical threshold:\", wait_time + wait_time_disappear, \"sec.\"")
                self._code_lines.append("    p = PerfManager()")
                self._code_lines.append("    p.add_perfdata(\"" + str(self._main_object_finder.name) + "\", wait_time + wait_time_disappear, " + repr(self._main_object_finder.warning) + ", " + repr(self._main_object_finder.critical) + ")")
            elif self._main_object_finder.find is False:
                self._code_lines.append("    if wait_time_disappear == -1:")
                if self._main_object_finder.timeout_exception is True:
                    self._code_lines.append("        raise Exception(\"step " + str(self._main_object_finder.name) + " timed out, execution time: " + str(self._main_object_finder.timeout) + "\")")             
                else:
                    self._code_lines.append("        print \"*WARN* step " + str(self._main_object_finder.name) + " timed out, execution time: " + str(self._main_object_finder.timeout) + "\"")
                    self._code_lines.append("        return False")
        
        if self._main_object_finder.timeout_exception is False:
            self._code_lines.append("    return True")
        self._code_lines.append("")
        self._code_lines.append("")
        if self._main_object_finder.args_number != 0:
            self.spinBoxArgs.setValue(self._main_object_finder.args_number)
        else:
            self.spinBoxArgs.setValue(total_args)
        self.building_code = False
        
    def get_old_code(self):
        file_code_string = ""
        filename = self._path + os.sep + self._main_object_finder.name + "_old_code.txt"
        
        if os.path.exists(filename):
            file = codecs.open(filename, encoding="utf-8")  
            lines = file.readlines()
            
            for line in lines:
                file_code_string = file_code_string + line   
                
        return file_code_string.encode('utf-8')
    
    def save_python_file(self):
    
        file_code_string = ""
        filename = self._alyvix_proxy_path + os.sep + "AlyvixProxy" + self._robot_file_name + ".py"
        
        if os.path.exists(filename):
            file = codecs.open(filename, encoding="utf-8")  
            lines = file.readlines()
            
            for line in lines:
                file_code_string = file_code_string + line   
                
        self.build_code_array()
        current_code_string = unicode(self.build_code_string(), 'utf-8')
        
        """
        if not os.path.exists(filename) and sel.action == "edit":
            sel.action = "new"
        """
        
        #print "old code:", self.__old_code
        
        if self.action == "new":
            file_code_string = file_code_string + current_code_string
        elif self.action == "edit":
            file_code_string = file_code_string.replace(unicode(self.__old_code, 'utf-8'), current_code_string)
            """
            print self.__old_code
            print "---"
            print current_code_string
            print "---"
            print file_code_string
            """

        string = file_code_string
        string = string.encode('utf-8')

        file = codecs.open(filename, 'w', 'utf-8')
        file.write(unicode(string, 'utf-8'))
        file.close()
        
        string = current_code_string
        string = string.encode('utf-8')
        
        filename = self._path + os.sep + self._main_object_finder.name + "_old_code.txt"
        file = codecs.open(filename, 'w', 'utf-8')
        file.write(unicode(string, 'utf-8'))
        file.close()

    
    def remove_code_from_py_file(self):
    
        file_code_string = ""
        filename = self._alyvix_proxy_path + os.sep + "AlyvixProxy" + self._robot_file_name + ".py"
        
        if os.path.exists(filename):
            file = codecs.open(filename, encoding="utf-8")  
            lines = file.readlines()
            
            for line in lines:
                file_code_string = file_code_string + line
            
        self.build_code_array()
        current_code_string = unicode(self.build_code_string(), 'utf-8')
        #current_code_string = current_code_string.replace(os.linesep + os.linesep, os.linesep)
        
        file_code_string = file_code_string.replace(unicode(self.__old_code, 'utf-8'), "")
        
        string = file_code_string
        string = string.encode('utf-8')

        file = codecs.open(filename, 'w', 'utf-8')
        file.write(unicode(string, 'utf-8'))
        file.close()    
    
    def open_select_obj_main(self):
    
        try:
            self.pv.close()
        except:
            pass

        self.button_selected = "set_main_object"
        self.open_select_obj_window()
        
    def open_select_obj_sub(self):
    
        try:
            self.pv.close()
        except:
            pass
        
        if self.listWidget.count() == 0:
            msgBox = QMessageBox()
            msgBox.setWindowTitle('Error')
            msgBox.setIcon (QMessageBox.Critical)
            msgBox.setText("You have to set the Main Object first")
            msgBox.setWindowFlags(Qt.WindowStaysOnTopHint)

            msgBox.exec_()
        else:
            
            self.button_selected = "add_sub_object"
            self.open_select_obj_window()
            
    def remove_obj(self):
    
        selected_index = self.listWidget.currentRow()
        
        if selected_index == -1:
            return True
    
        if selected_index == 0 and self._main_deleted is False:
            item = QListWidgetItem()
            item.setText("")
            self.listWidget.takeItem(0)
            self.listWidget.insertItem(0, item)
        
            self.button_selected = "set_main_object"
            
            self.delete_all_sub_roi()
            
            self._main_deleted = True
            self.open_select_obj_window()
        elif self._main_deleted is False:
            # print "selected_indexxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", selected_index
            item = self.listWidget.takeItem(selected_index)
            self.listWidget.removeItemWidget(item)
            del self._sub_objects_finder[selected_index - 1]
        self.parent.update_list()
        
        try:
            self.pv.update()
        except:
            pass
        
                
    def restore_all_sub_roi(self):
    
        self._sub_objects_finder = copy.deepcopy(self._old_sub_roi)
        
    def reset_all_sub_roi(self, old_pos):
    
        #self._old_sub_roi = copy.deepcopy(self._sub_objects_finder)
    
    
        cnt_sub = 1
        for sub_obj in self._sub_objects_finder:
            #print "cnt_sub", cnt_sub
            cnt_sub += 1
            
            if sub_obj.roi_height == 0 or sub_obj.roi_width == 0:
                return
            
            #print sub_obj.roi_x, sub_obj.roi_y, sub_obj.roi_height,sub_obj.roi_width
            
            #self.parent._deleted_sub_objects.append(copy.deepcopy(sub_obj))
            
            if sub_obj.is_textfinder is True:
                #print sub_obj.is_textfinder
                
                offset_main_x = old_pos[0] - self._main_object_finder.x
                offset_main_y = old_pos[1] - self._main_object_finder.y
                
                sub_obj.roi_x +=  offset_main_x
                sub_obj.roi_y += offset_main_y
                
                #print "exit"
            else:
                hw_factor = 0
                                
                if sub_obj.height < sub_obj.width:
                    hw_factor = sub_obj.height
                else:
                    hw_factor = sub_obj.width
                    
                    
                sc_factor = 0
                                    
                if self.pv._bg_pixmap.height() < self.pv._bg_pixmap.width():
                    sc_factor = self.pv._bg_pixmap.height()
                else:
                    sc_factor = self.pv._bg_pixmap.width()
                    
                percentage_screen_w = int(0.0125 * sc_factor)
                percentage_screen_h = int(0.0125 * sc_factor)
                percentage_object_w = int(0.2 * hw_factor) #sub_obj.width)
                percentage_object_h = int(0.2 * hw_factor) #sub_obj.height)
                
                roi_height = percentage_screen_h + percentage_object_h + sub_obj.height
                
                roi_width = percentage_screen_w + percentage_object_w + sub_obj.width
            
                """
                hw_factor = 0
                
                if sub_obj.height < sub_obj.width:
                    hw_factor = sub_obj.height
                else:
                    hw_factor = sub_obj.width
                
                roi_height = int(0.95 * hw_factor) + sub_obj.height

                roi_width = int(0.95 * hw_factor) + sub_obj.width
                """

                roi_width_half = int((roi_width - sub_obj.width)/2)

                roi_height_half = int((roi_height - sub_obj.height)/2)


                sub_obj.roi_x =  (sub_obj.x - self._main_object_finder.x) - roi_width_half
                sub_obj.roi_y =  (sub_obj.y - self._main_object_finder.y) - roi_height_half
                sub_obj.roi_height = sub_obj.height + (roi_height_half*2)
                sub_obj.roi_width = sub_obj.width + (roi_width_half*2)
                
                
                """
                roi_height = int(0.30*hw_factor*self.scaling_factor) + sub_obj.height

                roi_width = int(0.30*hw_factor*self.scaling_factor) + sub_obj.width
                

                roi_width_half = int((roi_width - sub_obj.width)/2)
                roi_height_half = int((roi_height - sub_obj.height)/2)

                sub_obj.roi_x =  (sub_obj.x - self._main_object_finder.x) - roi_width_half
                sub_obj.roi_y =  (sub_obj.y - self._main_object_finder.y) - roi_height_half
                sub_obj.roi_height = roi_height
                sub_obj.roi_width = roi_width
                """
             
            sub_obj.roi_unlimited_up = False
            sub_obj.roi_unlimited_down = False
            sub_obj.roi_unlimited_left = False
            sub_obj.roi_unlimited_right = False

        self._old_main_object = copy.deepcopy(self._main_object_finder)
        self._old_sub_objects = copy.deepcopy(self._sub_objects_finder)
        
        #print "update"
    
    def delete_all_sub_roi(self):
    
        self._old_sub_roi = copy.deepcopy(self._sub_objects_finder)
    
        for sub_obj in self._sub_objects_finder:
            
            if sub_obj.roi_height == 0 or sub_obj.roi_width == 0:
                return
            
            #print sub_obj.roi_x, sub_obj.roi_y, sub_obj.roi_height,sub_obj.roi_width
            
            #self.parent._deleted_sub_objects.append(copy.deepcopy(sub_obj))
            
            sub_obj.roi_x = 0
            sub_obj.roi_y = 0
            sub_obj.roi_height = 0
            sub_obj.roi_width = 0
            sub_obj.roi_unlimited_up = False
            sub_obj.roi_unlimited_down = False
            sub_obj.roi_unlimited_left = False
            sub_obj.roi_unlimited_right = False
            
        
    def edit_obj(self):
    
        self.last_selected_index = self.listWidget.currentRow()
    
        m_controller = dummy()
        m_controller.set_parent(self)
        m_controller.action = "edit"
        m_controller.path = self.parent.path
        m_controller.scaling_factor = self.parent.scaling_factor
        m_controller.robot_file_name =  self._robot_file_name
        m_controller.xml_name = str(self.listWidget.currentItem().data(Qt.UserRole).toString())
        m_controller.objectfinder_view = self
        
        
        image = QImage(m_controller.path + os.sep + m_controller.xml_name.replace("xml", "png"))
        
        if m_controller.xml_name.endswith('_RectFinder.xml'):
            self.object = AlyvixRectFinderView(m_controller)
        elif m_controller.xml_name.endswith('_ImageFinder.xml'):
            self.object = AlyvixImageFinderView(m_controller)
        elif m_controller.xml_name.endswith('_TextFinder.xml'):
            self.object = AlyvixTextFinderView(m_controller)
            
        self.object.parent_is_objfinder = True
        
        self.hide()
        
        self.object.set_bg_pixmap(image)
        self.object.showFullScreen()
        
        if m_controller.xml_name.endswith('_RectFinder.xml'):
            self.object.rect_view_properties = AlyvixRectFinderPropertiesView(self.object)
            self.object.rect_view_properties.show()
        elif m_controller.xml_name.endswith('_ImageFinder.xml'):
            self.object.image_view_properties = AlyvixImageFinderPropertiesView(self.object)
            self.object.image_view_properties.show()
        elif m_controller.xml_name.endswith('_TextFinder.xml'):
            self.object.image_view_properties = AlyvixTextFinderPropertiesView(self.object)
            self.object.image_view_properties.show()
    
    def open_select_obj_window(self):
        
        if self.button_selected == "set_main_object":
            self.select_main_object_view = AlyvixObjectsSelection(parent=self, is_main=True)
        elif self.button_selected == "add_sub_object":
            self.select_main_object_view = AlyvixObjectsSelection(parent=self, is_main=False)
          
        #print "objs",self


        self.select_main_object_view.show()
        
        self.hide()
        """
        try:
            self.close()
            self.parent.close()
        except: pass
        """
    def set_main_object(self, xml_name):
        filename = xml_name
        filename = filename.split(os.sep)[-1]
        
        self._added_objects.append(((xml_name), open(xml_name).read()))
        
        extra_path = get_python_lib() + os.sep + "alyvix" + os.sep + "robotproxy" + os.sep + self.parent.path.split(os.sep)[-1] + "_extra"
        scraper_path = extra_path + os.sep + filename.replace("_TextFinder.xml","")
        scraper_file = scraper_path + os.sep + "scraper.txt"
        
        
        if os.path.exists(scraper_file):
            QMessageBox.critical(self, "Error", "You cannot add a scraper object as main component!")
            self.restore_all_sub_roi()
            self.parent._main_deleted = False
            #self.listWidget.insertItem(0, self._old_main_list_item)
            return False

        elif "_TextFinder.xml" in filename:
            QMessageBox.critical(self, "Error", "You cannot add a Text Finder object as main component!")
            self.restore_all_sub_roi()
            self.parent._main_deleted = False
            #self.listWidget.insertItem(0, self._old_main_list_item)
            return False
            
        #self.update_lock_list(filename)
        
        #self._finders_to_exclude.append(xml_name)
                    
        item = QListWidgetItem()
        
        path_main_xml = self._main_object_finder.xml_path
        main_obj = None           
        m_controller = dummy()
        m_controller.action = "new"
        m_controller.path = self.parent.path
        m_controller.scaling_factor = self.parent.scaling_factor
        m_controller.xml_name = filename
        m_controller.objectfinder_view = self
        
        if filename.endswith('_RectFinder.xml'):
            item.setText(filename[:-15] + " [RF]")
            main_obj = AlyvixRectFinderView(m_controller)
            main_obj.build_objects()
            main_obj = main_obj._main_rect_finder
        elif filename.endswith('_ImageFinder.xml'):
            item.setText(filename[:-16] + " [IF]")
            main_obj = AlyvixImageFinderView(m_controller)
            main_obj.build_objects()
            main_obj = main_obj._main_template
        elif filename.endswith('_TextFinder.xml'):
            item.setText(filename[:-15] + " [TF]")
            main_obj = AlyvixTextFinderView(m_controller)
            main_obj.build_objects()
            main_obj = main_obj._main_text
            
        item.setData(Qt.UserRole, filename)
        
        if self.listWidget.count() > 0:
            self.listWidget.takeItem(0)
            self.listWidget.insertItem(0, item)
        else:
            self.listWidget.addItem(item)
            
        #self._main_object_finder = MainObjectForGui()
        self._main_object_finder.xml_path = xml_name
        self._main_object_finder.x = main_obj.x
        self._main_object_finder.y = main_obj.y
        self._main_object_finder.height = main_obj.height
        self._main_object_finder.width = main_obj.width
        self._main_object_finder.mouse_or_key_is_set = main_obj.mouse_or_key_is_set
        
        #print self._main_object_finder.x
        #print self._main_object_finder.y
        #print self._main_object_finder.height
        #print self._main_object_finder.width
        
        #self.listWidget.addItem(item)
        #self.build_main_object()
        
        try:
            if self._main_object_finder.show is True:
                self.listWidget.item(0).setCheckState(Qt.Checked)
            else:
                self.listWidget.item(0).setCheckState(Qt.Unchecked)
        except:
            pass
        
        
        try:
            image = QImage(self._main_object_finder.xml_path.replace("xml", "png"))   
            self.pv.set_bg_pixmap(image)


        except:
            
            self.pv = PaintingView(self)
            #print self._main_object_finder.xml_path.replace("xml", "png")
            image = QImage(self._main_object_finder.xml_path.replace("xml", "png"))   
            self.pv.set_bg_pixmap(image)
            
        self.pv.showFullScreen()
        return True
        
    def add_sub_object(self, xml_name):
    
        filename = xml_name
        filename = filename.split(os.sep)[-1]
        
        self._added_objects.append(((xml_name), open(xml_name).read()))
        
        scraper = False
        extra_path = get_python_lib() + os.sep + "alyvix" + os.sep + "robotproxy" + os.sep + self.parent.path.split(os.sep)[-1] + "_extra"
        scraper_path = extra_path + os.sep + filename.replace("_TextFinder.xml","")
        scraper_file = scraper_path + os.sep + "scraper.txt"
        if os.path.exists(scraper_file):
            if self._main_object_finder.is_scraper is True:
                QMessageBox.critical(self, "Error", "You can add only one scraper object")
                return False
            else:
                self._main_object_finder.is_scraper = True
                scraper = True
        
        #self.update_lock_list(filename)
                    
        item = QListWidgetItem()
        
        main_obj = None           
        m_controller = dummy()
        m_controller.action = "new"
        m_controller.path = self.parent.path
        m_controller.scaling_factor = self.parent.scaling_factor
        m_controller.xml_name = filename
        m_controller.objectfinder_view = self

        if filename.endswith('_RectFinder.xml'):
            item.setText(filename[:-15] + " [RF]")
            main_obj = AlyvixRectFinderView(m_controller)
            main_obj.build_objects()
            main_obj = main_obj._main_rect_finder
        elif filename.endswith('_ImageFinder.xml'):
            item.setText(filename[:-16] + " [IF]")
            main_obj = AlyvixImageFinderView(m_controller)
            main_obj.build_objects()
            main_obj = main_obj._main_template
        elif filename.endswith('_TextFinder.xml'):
            if scraper is True:
                item.setText(filename[:-15] + " [TS]")
            else:
                item.setText(filename[:-15] + " [TF]")
            main_obj = AlyvixTextFinderView(m_controller)
            main_obj.build_objects()
            main_obj = main_obj._main_text

        item.setData(Qt.UserRole, filename)
        item.setCheckState(Qt.Checked)
        self.listWidget.addItem(item)
        
        sub_object = SubObjectForGui()
        sub_object.xml_path = xml_name
            
        sub_object.x = main_obj.x
        sub_object.y = main_obj.y
        sub_object.height = main_obj.height
        sub_object.width = main_obj.width
        
        if filename.endswith('_TextFinder.xml'):
            sub_object.roi_x = main_obj.roi_x - self._main_object_finder.x
            sub_object.roi_y = main_obj.roi_y - self._main_object_finder.y
            sub_object.roi_height = main_obj.roi_height
            sub_object.roi_width = main_obj.roi_width
            sub_object.is_textfinder = True
            
        else:
            hw_factor = 0
                                
            if sub_object.height < sub_object.width:
                hw_factor = sub_object.height
            else:
                hw_factor = sub_object.width
                
                
            sc_factor = 0
                                
            if self.pv._bg_pixmap.height() < self.pv._bg_pixmap.width():
                sc_factor = self.pv._bg_pixmap.height()
            else:
                sc_factor = self.pv._bg_pixmap.width()
                
            percentage_screen_w = int(0.0125 * sc_factor)
            percentage_screen_h = int(0.0125 * sc_factor)
            percentage_object_w = int(0.2 * hw_factor) #image_finder.width)
            percentage_object_h = int(0.2 * hw_factor) #image_finder.height)
            
            roi_height = percentage_screen_h + percentage_object_h + sub_object.height
            
            roi_width = percentage_screen_w + percentage_object_w + sub_object.width


            roi_width_half = int((roi_width - sub_object.width)/2)

            roi_height_half = int((roi_height - sub_object.height)/2)


            sub_object.roi_x =  (sub_object.x - self._main_object_finder.x) - roi_width_half
            sub_object.roi_y =  (sub_object.y - self._main_object_finder.y) - roi_height_half
            sub_object.roi_height = sub_object.height + (roi_height_half*2)
            sub_object.roi_width = sub_object.width + (roi_width_half*2)

            """
            roi_height = int(0.30*hw_factor*self.scaling_factor) + sub_object.height #int(10*self.scaling_factor) + sub_object.height

            roi_width = int(0.30*hw_factor*self.scaling_factor) + sub_object.width #int(10*self.scaling_factor) + sub_object.width


            roi_width_half = int((roi_width - sub_object.width)/2)
            roi_height_half = int((roi_height - sub_object.height)/2)

            sub_object.roi_x =  (sub_object.x - self._main_object_finder.x) - roi_width_half
            sub_object.roi_y =  (sub_object.y - self._main_object_finder.y) - roi_height_half
            sub_object.roi_height = roi_height
            sub_object.roi_width = roi_width
            """
        
        sub_object.mouse_or_key_is_set = main_obj.mouse_or_key_is_set
        sub_object.scraper = scraper
        self._sub_objects_finder.append(sub_object)
        #self.build_sub_object(sub_object)
        
        #self.pv = PaintingView(self)
        
        #image = QImage(self._main_object_finder.xml_path.replace("xml", "png"))   
        #self.pv.set_bg_pixmap(image)
        #self.pv.showFullScreen()
        #self.show()
        self._can_set_roi_unlim = True
        
        return True
                
    def add_new_item_on_list(self): 
        dirpath = self._path

        # get all entries in the directory w/ stats
        entries = (os.path.join(dirpath, fn) for fn in os.listdir(dirpath))
        entries = ((os.stat(path), path) for path in entries)

        # leave only regular files, insert creation date
        entries = ((stat[ST_CTIME], path)
                   for stat, path in entries if S_ISREG(stat[ST_MODE]))
        #NOTE: on Windows `ST_CTIME` is a creation date 
        #  but on Unix it could be something else
        #NOTE: use `ST_MTIME` to sort by a modification date
        
        cdate, path = sorted(entries)[-1]
        
        filename = os.path.basename(path)
        
        item = QListWidgetItem()

        if filename.endswith('_RectFinder.xml'):
            item.setText(filename[:-15] + " [RF]")
        elif filename.endswith('_ImageFinder.xml'):
            item.setText(filename[:-16] + " [IF]")
        elif filename.endswith('_TextFinder.xml'):
            item.setText(filename[:-15] + " [TF]")
                    
        item.setData(Qt.UserRole, filename)
        self.listWidget.addItem(item)
        
    def build_xml(self):
        
        if self._main_object_finder is None:
            return

        name = str(self._main_object_finder.name)
        
        if name == "":
            name = time.strftime("object_finder_%d_%m_%y_%H_%M_%S")
            self._main_object_finder.name = name
        
        root = ET.Element("object_finder")
        root.set("name", name)
        root.set("find", str(self._main_object_finder.find))
        root.set("wait", str(self._main_object_finder.wait))
        root.set("wait_disapp", str(self._main_object_finder.wait_disapp))
        root.set("timeout", str(self._main_object_finder.timeout))
        root.set("timeout_exception", str(self._main_object_finder.timeout_exception))
        root.set("enable_performance", str(self._main_object_finder.enable_performance))
        root.set("warning_value", repr(self._main_object_finder.warning))
        root.set("critical_value", repr(self._main_object_finder.critical))
        root.set("args", str(self._main_object_finder.args_number))
        root.set("scraper", str(self._main_object_finder.is_scraper))

        main_object_node = ET.SubElement(root, "main_object")
        
        path_node = ET.SubElement(main_object_node, "xml_path")
        path_node.text = str(self._main_object_finder.xml_path)
        
        sub_objects_root = ET.SubElement(root, "sub_objects")
        
        cnt = 1
        for sub_object in self._sub_objects_finder:
            if sub_object.height != 0 and sub_object.width !=0:
            
                sub_object_node = ET.SubElement(sub_objects_root, "sub_object") #ET.SubElement(sub_objects_root, "sub_object_" + str(cnt))
                sub_object_node.set("id", str(cnt))
                     
                path_node = ET.SubElement(sub_object_node, "xml_path")
                #path_node.text = str(self._path + os.sep + self._main_object_finder.name + os.sep + "sub_object_" + str(cnt) + ".png")
                path_node.text = str(sub_object.xml_path)
                
                roi_x_node = ET.SubElement(sub_object_node, "roi_x")
                roi_x_node.text = str(sub_object.roi_x)
                
                roi_y_node = ET.SubElement(sub_object_node, "roi_y")
                roi_y_node.text = str(sub_object.roi_y)
                
                roi_width_node = ET.SubElement(sub_object_node, "roi_width")
                roi_width_node.text = str(sub_object.roi_width)
                
                roi_height_node = ET.SubElement(sub_object_node, "roi_height")
                roi_height_node.text = str(sub_object.roi_height)
                
                roi_unlimited_up_node = ET.SubElement(sub_object_node, "roi_unlimited_up")
                roi_unlimited_up_node.text = str(sub_object.roi_unlimited_up)
                
                roi_unlimited_down_node = ET.SubElement(sub_object_node, "roi_unlimited_down")
                roi_unlimited_down_node.text = str(sub_object.roi_unlimited_down)
                
                roi_unlimited_left_node = ET.SubElement(sub_object_node, "roi_unlimited_left")
                roi_unlimited_left_node.text = str(sub_object.roi_unlimited_left)
                
                roi_unlimited_right_node = ET.SubElement(sub_object_node, "roi_unlimited_right")
                roi_unlimited_right_node.text = str(sub_object.roi_unlimited_right)
                
                cnt = cnt + 1
        
        code_blocks_root = ET.SubElement(root, "code_blocks")
        for block in self._code_blocks:
            block_start_line = block[0]
            block_text = block[1]
            block_end_line = block[2]
           # block_text = unicode(block_text, "utf-8")
            code_block = ET.SubElement(code_blocks_root, "code_block") #ET.SubElement(sub_objects_root, "sub_object_" + str(cnt))
            #code_block.set("id", str(block_start_line) + "_" + str(block_end_line))
            
            start_line_node = ET.SubElement(code_block, "start_line")
            start_line_node.text = str(block_start_line)
         
            end_line_node = ET.SubElement(code_block, "end_line")
            end_line_node.text = str(block_end_line)
            
            code_node = ET.SubElement(code_block, "code")
            code_node.append(ET.Comment(' --><![CDATA[' + unicode(block_text.replace(']]>', ']]]]><![CDATA[>'), 'utf-8') + ']]><!-- '))
            #code_node.text = str(block_start_line)
            
        tree = ET.ElementTree(root)
        
        python_file = open(self._path + os.sep + self._main_object_finder.name + "_ObjectFinder.xml", 'w')
        tree.write(python_file, encoding='utf-8', xml_declaration=True) 
        #python_file.write(rough_string)        
        python_file.close()
    
    @pyqtSlot()
    def inserttext_event(self):
        if self.inserttext.toPlainText() == "Type here the Keyboard macro" or self.inserttext.toPlainText() == "#k.send('Type here the key')":
            self._main_object_finder.sendkeys = "".encode('utf-8')
        else:
            self._main_object_finder.sendkeys = str(self.inserttext.toPlainText().toUtf8())
    
    @pyqtSlot(QString)
    def namelineedit_event(self, text):
        if text == "Type the keyword name":
            self._main_object_finder.name = "".encode('utf-8')
        else:
            self._main_object_finder.name = str(text.toUtf8()).replace(" ", "_")
            
        #print "name", self._main_object_finder.name
  
    def args_spinbox_change_event(self, event):

        if self.building_code is False:
            #print "spinbox"
            self._main_object_finder.args_number = self.spinBoxArgs.value()
            self.build_code_array()
            self.textEdit.setText(unicode(self.build_code_string(), 'utf-8'))
  
    def warning_event(self, event):
        self._main_object_finder.warning = self.doubleSpinBoxWarning.value()
        
    def critical_event(self, event):
        self._main_object_finder.critical = self.doubleSpinBoxCritical.value()
        
    def tab_changed_event(self, tab_index):
        if tab_index is 1:
            self.build_code_array()
            self.textEdit.setText(unicode(self.build_code_string(), 'utf-8'))
        elif tab_index is 3:
            self.doubleSpinBoxWarning.setValue(self._main_object_finder.warning)
            self.doubleSpinBoxCritical.setValue(self._main_object_finder.critical)
            
            if self._main_object_finder.enable_performance is True:
                self.checkBoxEnablePerformance.setCheckState(Qt.Checked)
                self.doubleSpinBoxWarning.setEnabled(True)
                self.doubleSpinBoxCritical.setEnabled(True)
                self.labelWarning.setEnabled(True)
                self.labelCritical.setEnabled(True)
            else:
                self.checkBoxEnablePerformance.setCheckState(Qt.Unchecked)
                self.doubleSpinBoxWarning.setEnabled(False)
                self.doubleSpinBoxCritical.setEnabled(False)
                self.labelWarning.setEnabled(False)
                self.labelCritical.setEnabled(False)
                
    def enable_performance_event(self, event):
        if self.checkBoxEnablePerformance.isChecked() is True:
            self._main_object_finder.enable_performance = True
            self.doubleSpinBoxWarning.setEnabled(True)
            self.doubleSpinBoxCritical.setEnabled(True)
            self.labelWarning.setEnabled(True)
            self.labelCritical.setEnabled(True)
        else:
            self._main_object_finder.enable_performance = False
            self.doubleSpinBoxWarning.setEnabled(False)
            self.doubleSpinBoxCritical.setEnabled(False)
            self.labelWarning.setEnabled(False)
            self.labelCritical.setEnabled(False)
    
    def wait_radio_event(self, event):
        
        if event is True:
            self.timeout_spinbox.setEnabled(True)
            self.timeout_label.setEnabled(True)
            self.timeout_exception.setEnabled(True)
            self._main_object_finder.wait_disapp = False
            self._main_object_finder.wait = True
            self._main_object_finder.find = False
        
    def wait_disapp_radio_event(self, event):
        
        if event is True:
            self.timeout_spinbox.setEnabled(True)
            self.timeout_label.setEnabled(True)
            self.timeout_exception.setEnabled(True)
            self._main_object_finder.wait_disapp = True
            self._main_object_finder.wait = False
            self._main_object_finder.find = False
            
    def find_radio_event(self, event):
        
        if event is True:
            self.timeout_spinbox.setEnabled(False)
            self.timeout_exception.setEnabled(False)
            self.timeout_label.setEnabled(False)
            self._main_object_finder.wait_disapp = False
            self._main_object_finder.wait = False
            self._main_object_finder.find = True
            
    def timeout_spinbox_event(self, event):
        self._main_object_finder.timeout = self.timeout_spinbox.value()
        
    def timeout_exception_event(self, event):
        if self.timeout_exception.isChecked() is True:
            self._main_object_finder.timeout_exception = True
        else:
            self._main_object_finder.timeout_exception = False
    
    def sel_all_event(self):
  
        #print "count",self.listWidget.count()
        for row_index in range(self.listWidget.count()):
        
            self.listWidget.item(row_index).setCheckState(Qt.Checked)
            
       
    def des_all_event(self):

        for row_index in range(self.listWidget.count()):
        
            self.listWidget.item(row_index).setCheckState(Qt.Unchecked)
        
    def delete_event(self):
    
        index_to_remove = []
        #print self._sub_objects_finder
        delete_main = False
        for row_index in range(self.listWidget.count()):
                if row_index == 0 and self.listWidget.item(row_index).checkState() == 2: 
                    delete_main = True
                if row_index != 0 and self.listWidget.item(row_index).checkState() == 2:
                    #print row_index - 1
                    #del self._sub_objects_finder[row_index-1]
                    index_to_remove.append(row_index-1)
                    
        if len(index_to_remove):
            answer = QMessageBox.No
        
            answer = QMessageBox.warning(self, "Warning", "Are you sure you want to delete selected items?", QMessageBox.Yes, QMessageBox.No)
              
            if answer == QMessageBox.No:
                return
        
        self._sub_objects_finder = [i for j, i in enumerate(self._sub_objects_finder) if j not in index_to_remove]
        
        item0_text =  self.listWidget.item(0).text()
        item0_data =  self.listWidget.item(0).data(Qt.UserRole).toString()
        self.listWidget.clear()
        
        item = QListWidgetItem()
        item.setText(item0_text)
        item.setData(Qt.UserRole, item0_data)
        self.listWidget.addItem(item)
        
        is_main_scraper = False
        
        cnt = 1
        for sub_object in self._sub_objects_finder:
        
            #item = QListWidgetItem()
            
            filename = sub_object.xml_path
            filename = filename.split(os.sep)[-1]
            
            scraper = False
            extra_path = get_python_lib() + os.sep + "alyvix" + os.sep + "robotproxy" + os.sep + self._path.split(os.sep)[-1] + "_extra"
            scraper_path = extra_path + os.sep + filename.replace("_TextFinder.xml","")
            scraper_file = scraper_path + os.sep + "scraper.txt"
            if os.path.exists(scraper_file):
                scraper = True
                is_main_scraper = True
                        
            item = QListWidgetItem()
            
            if sub_object.show is True:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
                
            if filename.endswith('_RectFinder.xml'):
                item.setText(filename[:-15] + " [RF]")
            elif filename.endswith('_ImageFinder.xml'):
                item.setText(filename[:-16] + " [IF]")
            elif filename.endswith('_TextFinder.xml'):
                if scraper is True:
                    item.setText(filename[:-15] + " [TS]")
                else:
                    item.setText(filename[:-15] + " [TF]")
                
            item.setData(Qt.UserRole, filename)
            
            self.listWidget.addItem(item)
            cnt = cnt + 1
            
        if self._main_object_finder.show is True:
            self.listWidget.item(0).setCheckState(Qt.Checked)
        else:
            self.listWidget.item(0).setCheckState(Qt.Unchecked)
        self.listWidget.item(0).setSelected(True)  
        
        
        if is_main_scraper is False:

            self._main_object_finder.is_scraper = False
                
        if delete_main is True and len(self._sub_objects_finder) == 0:
            self.listWidget.clear()
            
            self._main_deleted = True

            self.update_list()
            
            self.pv.close()
            
        self.widget_2.hide()
        self.widget.show()
        #self.widget.setGeometry(QRect(168, 9, 413, 433))
        self.widget.setGeometry(QRect(self.widget.geometry().x(), self.widget.geometry().y(),
                                self.widget.geometry().width(), self.widget.geometry().height()))
             
                                    
        self.pv.update()
        
    @pyqtSlot(QListWidgetItem)
    def listWidget_state_changed(self, item):
        #selected_index = self.listWidget.currentRow()
        #print "asasascdferfgref"
        #print self.listWidget.findItems(item.text(), Qt.MatchExactly)
        
        show = True
        
        if item.checkState() == 0:
            show = False
        elif item.checkState() == 2:
            show = True
        else:
            show = False
        
        for row_index in range(self.listWidget.count()):
            if item == self.listWidget.item(row_index):
                if row_index == 0:
                    self._main_object_finder.show = show
                else:
                    self._sub_objects_finder[row_index-1].show = show
                    
        self.pv.update()
        
    def listWidget_selection_changed(self):
        global last_row_selected
        selected_index = self.listWidget.currentRow()
        
        last_row_selected = selected_index   
        
        if selected_index == 0:
            self.widget_2.hide()
            self.widget.show()
            #self.widget.setGeometry(QRect(168, 9, 413, 433))
            self.widget.setGeometry(QRect(self.widget.geometry().x(), self.widget.geometry().y(),
                                    self.widget.geometry().width(), self.widget.geometry().height()))

        else:
            self.widget.hide()
            self.widget_2.show()
            #self.widget_2.setGeometry(QRect(168, 9, 414, 434))
            self.widget_2.setGeometry(QRect(self.widget.geometry().x(), self.widget.geometry().y(),
                                        self.widget_2.geometry().width(), self.widget_2.geometry().height()))
            self.sub_object_index = selected_index - 1
            self.update_sub_object_view()
    
            
    def eventFilter(self, obj, event):
        if event.type() == event.MouseButtonPress:
        
            if self.namelineedit.text() == "Type the keyword name" and obj.objectName() == "namelineedit":
                self.namelineedit.setText("")
                return True
                
        if event.type()== event.FocusOut:
            if obj.objectName() == "roi_y_spinbox":

                absolute_sub_roi_y = self._main_object_finder.y + self._sub_objects_finder[self.sub_object_index].roi_y
                absolute_sub_rect_y = self._sub_objects_finder[self.sub_object_index].y
        
                if absolute_sub_roi_y > absolute_sub_rect_y:
                    self._sub_objects_finder[self.sub_object_index].roi_y = self._sub_objects_finder[self.sub_object_index].y - self._main_object_finder.y
                    self.roi_y_spinbox.setValue(self._sub_objects_finder[self.sub_object_index].roi_y)
                    self.update()
                    return True
                    
                if absolute_sub_roi_y + self._sub_objects_finder[self.sub_object_index].roi_height < absolute_sub_rect_y + self._sub_objects_finder[self.sub_object_index].height:
                    self._sub_objects_finder[self.sub_object_index].roi_y = self._sub_objects_finder[self.sub_object_index].y - self._main_object_finder.y
                    self.roi_y_spinbox.setValue(self._sub_objects_finder[self.sub_object_index].roi_y)
                    self.update()
                    return True
                    
            elif obj.objectName() == "roi_height_spinbox":
                
                absolute_sub_roi_y = self._main_object_finder.y + self._sub_objects_finder[self.sub_object_index].roi_y
                absolute_sub_rect_y = self._sub_objects_finder[self.sub_object_index].y
                if absolute_sub_roi_y + self._sub_objects_finder[self.sub_object_index].roi_height < absolute_sub_rect_y + self._sub_objects_finder[self.sub_object_index].height:
                    px_to_add = (absolute_sub_rect_y + self._sub_objects_finder[self.sub_object_index].height) - (absolute_sub_roi_y + self._sub_objects_finder[self.sub_object_index].roi_height)
                    height = absolute_sub_roi_y - px_to_add
                    self._sub_objects_finder[self.sub_object_index].roi_height = self._sub_objects_finder[self.sub_object_index].roi_height  + px_to_add
                    self.roi_height_spinbox.setValue(self._sub_objects_finder[self.sub_object_index].roi_height)
                    self.update()
                    return True
                    
            elif obj.objectName() == "roi_x_spinbox":

                absolute_sub_roi_x = self._main_object_finder.x + self._sub_objects_finder[self.sub_object_index].roi_x
                absolute_sub_rect_x = self._sub_objects_finder[self.sub_object_index].x
        
                if absolute_sub_roi_x > absolute_sub_rect_x:
                    self._sub_objects_finder[self.sub_object_index].roi_x = self._sub_objects_finder[self.sub_object_index].x - self._main_object_finder.x
                    self.roi_x_spinbox.setValue(self._sub_objects_finder[self.sub_object_index].roi_x)
                    self.update()
                    return True
                    
                if absolute_sub_roi_x + self._sub_objects_finder[self.sub_object_index].roi_width < absolute_sub_rect_x + self._sub_objects_finder[self.sub_object_index].width:
                    self._sub_objects_finder[self.sub_object_index].roi_x = self._sub_objects_finder[self.sub_object_index].x - self._main_object_finder.x
                    self.roi_x_spinbox.setValue(self._sub_objects_finder[self.sub_object_index].roi_x)
                    self.update()
                    return True
                    
            elif obj.objectName() == "roi_width_spinbox":
                
                absolute_sub_roi_x = self._main_object_finder.x + self._sub_objects_finder[self.sub_object_index].roi_x
                absolute_sub_rect_x = self._sub_objects_finder[self.sub_object_index].x
                if absolute_sub_roi_x + self._sub_objects_finder[self.sub_object_index].roi_width < absolute_sub_rect_x + self._sub_objects_finder[self.sub_object_index].width:
                    px_to_add = (absolute_sub_rect_x + self._sub_objects_finder[self.sub_object_index].width) - (absolute_sub_roi_x + self._sub_objects_finder[self.sub_object_index].roi_width)
                    height = absolute_sub_roi_x - px_to_add
                    self._sub_objects_finder[self.sub_object_index].roi_width = self._sub_objects_finder[self.sub_object_index].roi_width  + px_to_add
                    self.roi_width_spinbox.setValue(self._sub_objects_finder[self.sub_object_index].roi_width)
                    self.update()
                    return True
            elif self.namelineedit.text() == "" and obj.objectName() == "namelineedit":
                self.namelineedit.setText("Type the keyword name")
                return True
            elif obj.objectName() == "namelineedit":
                self.namelineedit.setText(self._main_object_finder.name)
                return True
                
            if obj.objectName() == "textEditCustomLines" and self.added_block is False:
                self.update_code_block_array()
                return True
            elif obj.objectName() == "textEditCustomLines" and self.added_block is True:
                self.added_block = False
                return True
                
        if event.type() == event.KeyPress and obj.objectName() == "namelineedit" and (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter):
            self.pushButtonOk_event()
        if event.type() == event.KeyPress and obj.objectName() == "textEditCustomLines" and event.key() == Qt.Key_Tab:
            
            select_start = self.textEditCustomLines.textCursor().selectionStart()
            
            new_text = self.textEditCustomLines.textCursor().selection().toPlainText()
            
            if new_text == "":
                self.textEditCustomLines.insertPlainText("    ")
            else:
                new_text = "    " + new_text.replace("\n", "\n    ")
                self.textEditCustomLines.textCursor().insertText(new_text)
                            
                select_end = self.textEditCustomLines.textCursor().position()

                c = self.textEditCustomLines.textCursor()
                c.setPosition(select_start)
                c.setPosition(select_end, QTextCursor.KeepAnchor)
                self.textEditCustomLines.setTextCursor(c)

            return True
            
        if event.type() == event.KeyPress and obj.objectName() == "textEditCustomLines" and event.key() == Qt.Key_Backtab:
            
            cursors_pos = self.textEditCustomLines.textCursor().position()
            new_pos = 0
            select_start = self.textEditCustomLines.textCursor().selectionStart()
            
            new_text = str(self.textEditCustomLines.textCursor().selection().toPlainText().toUtf8())
            
            if new_text == "":
                #self.textEditCustomLines.insertPlainText("    ")
                #print self.textEditCustomLines.textCursor().block().text().toAscii()

                textedit_string = str(self.textEditCustomLines.toPlainText().toUtf8())
                textedit_strings = textedit_string.split("\n")
                
                cursor_line_number = self.textEditCustomLines.textCursor().blockNumber()
                
                cnt = 0
                for string in textedit_strings:
                    if cnt == cursor_line_number:
                        #current_line = str(self.textEditCustomLines.textCursor().block().text().toAscii())
                        #print current_line
                        if string.startswith("    "):
                            string_trimmed = string[4:]
                            #new_text = new_text.replace(first_line, firt_line_trimmed, 1)
                            #self.textEditCustomLines.textCursor().insertText(current_line_trimmed)
                            textedit_strings[cnt] = string_trimmed
                            new_pos = cursors_pos -4
                            
                            new_string = ""
                            
                            for string in textedit_strings:
                                new_string = new_string + string + "\n"
                            new_string = new_string[:-1]

                            self.textEditCustomLines.setPlainText(unicode(new_string, 'utf-8'))
                            
                            if new_pos < 0:
                                new_pos = 0
                            
                            c = self.textEditCustomLines.textCursor()
                            c.setPosition(new_pos)
                            self.textEditCustomLines.setTextCursor(c)
                            
                            
                            
                            #print string_trimmed
                    cnt = cnt + 1
                    
            else:
                first_line = new_text.split("\n")[0]
                #firt_line_trimmed = str(first_line).lstrip('    ')
                if first_line.startswith("    "):
                    firt_line_trimmed = first_line[4:]
                    new_text = new_text.replace(first_line, firt_line_trimmed, 1)
                new_text = new_text.replace("\n    ", "\n")

                self.textEditCustomLines.textCursor().insertText(unicode(new_text,'utf-8'))
                
                select_end = self.textEditCustomLines.textCursor().position()
                
                c = self.textEditCustomLines.textCursor()
                c.setPosition(select_start)
                c.setPosition(select_end, QTextCursor.KeepAnchor)
                self.textEditCustomLines.setTextCursor(c)
                
            return True
            
        return False  
    
    def init_block_code(self):
                
        for block in self._code_blocks:
            block_index_start_line = block[0]
            block_index_end_line = block[2]

            item = QListWidgetItem()
            item.setText(str(block_index_start_line) + ":" + str(block_index_end_line))
            self.listWidgetBlocks.addItem(item)
                
    def add_block_code(self):
    
        if self.pushButtonAddBlock.text() == "Unselect":
            self.listWidgetBlocks.item(self.listWidgetBlocks.currentRow()).setSelected(False)
            self.listWidgetBlocks.setCurrentItem(None)
            self.pushButtonAddBlock.setText("Add Block")
            self.textEditCustomLines.setPlainText("")
        elif self.textEditCustomLines.toPlainText() != "":
            
            index = self.spinBoxLine.value()

            is_present = False
                            
            block_index_start_line = None
            block_index_end_line = None
                
            for block in self._code_blocks:
                block_index_start_line = block[0]
                block_index_end_line = block[2]

                if index >= block_index_start_line and index <= block_index_end_line:
                    is_present = True
                    break

            if is_present is False:

                end_line = index + len(self.textEditCustomLines.toPlainText().split("\n")) -1
                item = QListWidgetItem()
                #item.setCheckState(Qt.Checked)
                item.setText(str(index) + ":" + str(end_line))
                #print str(index) + ":" + str(end_line)
                self.listWidgetBlocks.addItem(item)
                
                self._code_blocks.append((index, str(self.textEditCustomLines.toPlainText().toUtf8()), end_line))
                #print self._code_blocks
                self.textEditCustomLines.setPlainText("")
                self.added_block = True
            else:
                msgBox = QMessageBox()
                msgBox.setWindowTitle('Error')
                msgBox.setIcon (QMessageBox.Critical)
                msgBox.setText("You cannot add block of code into another block.\nLines from " + str(block_index_start_line) + " to " + str(block_index_end_line) + " belongs to block " + str(block_index_start_line) + ":" + str(block_index_end_line))
                msgBox.setWindowFlags(Qt.WindowStaysOnTopHint)

                msgBox.exec_()

    def remove_block_code(self):
        selected_index = self.listWidgetBlocks.currentRow()
        
        if selected_index == -1:
            return
        
        del self._code_blocks[selected_index]
        
        item = self.listWidgetBlocks.takeItem(selected_index)
        self.listWidgetBlocks.removeItemWidget(item)
        self.textEditCustomLines.setPlainText("")
        
        if len(self._code_blocks) == 1:
            block = self._code_blocks[0]
            code_text = block[1]
            self.textEditCustomLines.setPlainText(code_text)
            
    def listWidgetBlocks_selection_changed(self):
        
        selected_index = self.listWidgetBlocks.currentRow()
        
        if len(self._code_blocks) > 0:
            block = self._code_blocks[selected_index]
            code_text = block[1]
            self.textEditCustomLines.setPlainText(unicode(code_text, 'utf-8'))
            self.pushButtonAddBlock.setText("Unselect")

    def update_code_block_array(self):
        
        list_current_item = self.listWidgetBlocks.currentItem()
        
        if list_current_item is None:
            return
        
        selected_index = self.listWidgetBlocks.currentRow()
        
        if len(self._code_blocks) > 0:
            text = str(self.textEditCustomLines.toPlainText().toUtf8())
            end_line = self._code_blocks[selected_index][0] + len(self.textEditCustomLines.toPlainText().split("\n")) -1
            new_tuple = (self._code_blocks[selected_index][0], text, end_line)
            self._code_blocks[selected_index] = new_tuple
            self.listWidgetBlocks.currentItem().setText(str(self._code_blocks[selected_index][0]) + ":" + str(end_line))
        
    
    def update_sub_object_view(self):
    
        index = self.sub_object_index 
                    
        if index < 0:
            return
            
        self.roi_x_spinbox.setValue(self._sub_objects_finder[self.sub_object_index].roi_x)
        self.roi_y_spinbox.setValue(self._sub_objects_finder[self.sub_object_index].roi_y)
        self.roi_width_spinbox.setValue(self._sub_objects_finder[self.sub_object_index].roi_width)
        self.roi_height_spinbox.setValue(self._sub_objects_finder[self.sub_object_index].roi_height)
            
    #################
    #################
            
    def roi_x_spinbox_event(self, event):
        self._sub_objects_finder[self.sub_object_index].roi_x = self.roi_x_spinbox.value()
        self.update()
        
    def roi_y_spinbox_event(self, event):
        self._sub_objects_finder[self.sub_object_index].roi_y = self.roi_y_spinbox.value()
        self.update()
        
    def roi_width_spinbox_event(self, event):
        self._sub_objects_finder[self.sub_object_index].roi_width = self.roi_width_spinbox.value()
        self.update()
        
    def roi_height_spinbox_event(self, event):
        self._sub_objects_finder[self.sub_object_index].roi_height = self.roi_height_spinbox.value()
        
    def remove_obj_2(self):
    
        #print "rrrrr"
    
        selected_index = self.listWidget.currentRow()
    
        if selected_index == -1:
            return True
    
        if selected_index == 0:
            item = QListWidgetItem()
            item.setText("")
            self.listWidget.takeItem(0)
            self.listWidget.insertItem(0, item)
        
            self.button_selected = "set_main_object"
            self.open_select_obj_window()
        else:
        
            item = self.listWidget.takeItem(selected_index)
            #item_path = self.parent.path + os.sep + item.data(Qt.UserRole).toString()
            
            scraper_file_name = self._path + os.sep + self._main_object_finder.name + "_ObjectFinder.alyscraper"

            if os.path.exists(scraper_file_name):
                self._main_object_finder.is_scraper = False
                #print "scraper is false"
            
            #print selected_index
            self.listWidget.removeItemWidget(item)
            #print "rrrrr"
            del self._sub_objects_finder[selected_index - 1]
            
        try:
            self.pv.update()
        except:
            pass
        
    def edit_obj_2(self):
    
        self.last_selected_index = self.listWidget.currentRow()
    
        s_controller = dummy()
        s_controller.set_parent(self)
        s_controller.action = "edit"
        s_controller.path = self.parent.path
        s_controller.robot_file_name =  self._robot_file_name
        s_controller.scaling_factor = self.parent.scaling_factor
        s_controller.xml_name = str(self.listWidget.currentItem().data(Qt.UserRole).toString())
        s_controller.objectfinder_view = self
        
        image = QImage(s_controller.path + os.sep + s_controller.xml_name.replace("xml", "png"))
        
        if s_controller.xml_name.endswith('_RectFinder.xml'):
            self.object = AlyvixRectFinderView(s_controller)
        elif s_controller.xml_name.endswith('_ImageFinder.xml'):
            self.object = AlyvixImageFinderView(s_controller)
        elif s_controller.xml_name.endswith('_TextFinder.xml'):
            self.object = AlyvixTextFinderView(s_controller)
            
        self.object.parent_is_objfinder = True
        
        self.hide()
        
        self.object.set_bg_pixmap(image)
        self.object.showFullScreen()
        
        if s_controller.xml_name.endswith('_RectFinder.xml'):
            self.object.rect_view_properties = AlyvixRectFinderPropertiesView(self.object)
            self.object.rect_view_properties.show()
        elif s_controller.xml_name.endswith('_ImageFinder.xml'):
            self.object.image_view_properties = AlyvixImageFinderPropertiesView(self.object)
            self.object.image_view_properties.show()
        elif s_controller.xml_name.endswith('_TextFinder.xml'):
            self.object.image_view_properties = AlyvixTextFinderPropertiesView(self.object)
            self.object.image_view_properties.show()
            
        self.update()
        
    def redraw_roi_event(self):
    
        #self.tiny_build_objects()
        
        self._last_sub_object = copy.deepcopy(self._sub_objects_finder[self.sub_object_index])
    
        self._sub_objects_finder[self.sub_object_index].roi_x = 0
        self._sub_objects_finder[self.sub_object_index].roi_y = 0
        self._sub_objects_finder[self.sub_object_index].roi_width = 0
        self._sub_objects_finder[self.sub_object_index].roi_height = 0
        self._sub_objects_finder[self.sub_object_index].roi_unlimited_up = False
        self._sub_objects_finder[self.sub_object_index].roi_unlimited_down = False
        self._sub_objects_finder[self.sub_object_index].roi_unlimited_left = False
        self._sub_objects_finder[self.sub_object_index].roi_unlimited_right = False
        
        self._redraw_index = self.sub_object_index
        
        try:
            image = QImage(self._main_object_finder.xml_path.replace("xml", "png"))   
            self.pv.set_bg_pixmap(image)


        except:
            
            self.pv = PaintingView(self)
            #print self._main_object_finder.xml_path.replace("xml", "png")
            image = QImage(self._main_object_finder.xml_path.replace("xml", "png"))   
            self.pv.set_bg_pixmap(image)
            
        self.pv.showFullScreen()
        self._can_set_roi_unlim = True
        #self.update()
    
        """
    
        s_controller = dummy()
        s_controller.set_parent(self)
        s_controller.action = "edit"
        s_controller.path = self.parent.path
        s_controller.robot_file_name =  self._robot_file_name
        s_controller.xml_name = str(self.listWidget.currentItem().data(Qt.UserRole).toString())
        
        image = QImage(s_controller.path + os.sep + s_controller.xml_name.replace("xml", "png"))
        
        if s_controller.xml_name.endswith('_RectFinder.xml'):
            self.object = AlyvixRectFinderView(s_controller)
        elif s_controller.xml_name.endswith('_ImageFinder.xml'):
            self.object = AlyvixImageFinderView(s_controller)
        elif s_controller.xml_name.endswith('_TextFinder.xml'):
            self.object = AlyvixTextFinderView(s_controller)
        
        self.hide()
        
        self.object.set_bg_pixmap(image)
        self.object.showFullScreen()
        self.update()
        """
        
    def update_list(self):
    
        pass
    
        """
        items = []
        for index in xrange(self.listWidget.count()):
            item = self.listWidget.item(index)
                         
            if "[TF]" in item.text():

                extra_path = get_python_lib() + os.sep + "alyvix" + os.sep + "robotproxy" + os.sep + self._path.split(os.sep)[-1] + "_extra"


                xml_file = item.data(Qt.UserRole).toString()

                #print self.parent.path + os.sep + xml_file

                scraper_path = extra_path + os.sep + xml_file.replace("_TextFinder.xml","")
                scraper_file = scraper_path + os.sep + "scraper.txt"

                if os.path.exists(scraper_file):
                    item.setText(xml_file[:-15] + " [TS]")
                    
                    self._main_object_finder.is_scraper = True
                    
                    scraper_file_name = self._path + os.sep + self._main_object_finder.name + "_ObjectFinder.alyscraper"
            
                            
                    if not os.path.exists(scraper_file_name):
                        with open(scraper_file_name, 'w') as f:
                            
                            f.write("scraper=true")

                            f.close()
                            
                            
                    with open(self._path + os.sep + self._xml_name, 'r') as content_file:
                        content = content_file.read()
                        
                        
                    if not "scraper=\"False\"" in content and not "scraper=\"True\"" in content:
                        content = content.replace("<object_finder", "<object_finder scraper=\"True\"")

                                    
                    content = content.replace("scraper=\"False\"", "scraper=\"True\"")

                    
                    with open(self._path + os.sep + self._xml_name, "w") as text_file:
                        text_file.write(content)

        """
        
        """
        # get all entries in the directory w/ stats
        entries = (os.path.join(dirpath, fn) for fn in os.listdir(dirpath))
        entries = ((os.stat(path), path) for path in entries)

        # leave only regular files, insert creation date
        entries = ((stat[ST_CTIME], path)
        for stat, path in entries if S_ISREG(stat[ST_MODE]))
        #NOTE: on Windows `ST_CTIME` is a creation date 
        #  but on Unix it could be something else
        #NOTE: use `ST_MTIME` to sort by a modification date

        cdate, path = sorted(entries)[-1]

        filename = os.path.basename(path)

        item = QListWidgetItem()

        if filename.endswith('_RectFinder.xml'):
        item.setText(filename[:-15] + " [RF]")
        elif filename.endswith('_ImageFinder.xml'):
        item.setText(filename[:-16] + " [IF]")
        elif filename.endswith('_TextFinder.xml'):
        item.setText(filename[:-15] + " [TF]")

        item.setData(Qt.UserRole, filename)
        self.listWidget.addItem(item)
        """
        
            
class MainObjectForGui:
    
    def __init__(self):
        self.name = ""
        self.x = 0
        self.y = 0
        self.height = 0
        self.width = 0
        self.show = True
        self.xml_path = ""
        self.click = False
        self.doubleclick = False
        self.wait = True
        self.wait_disapp = False
        self.find = False
        self.args_number = 0
        self.component_args = ""
        self.timeout = 20
        self.is_scraper = False
        self.is_textfinder = False
        self.timeout_exception = True
        self.sendkeys = ""
        self.enable_performance = True
        self.mouse_or_key_is_set = False
        self.warning = 10.00
        self.critical = 15.00
        self.x_offset = None
        self.y_offset = None
        
class SubObjectForGui:
    
    def __init__(self):
        self.x = 0
        self.y = 0
        self.height = 0
        self.width = 0
        self.roi_x = 0
        self.roi_y = 0
        self.roi_height = 0
        self.roi_width = 0
        self.roi_unlimited_up = False
        self.roi_unlimited_down = False
        self.roi_unlimited_left = False
        self.roi_unlimited_right = False
        self.show = True
        self.xml_path = ""
        self.click = False
        self.doubleclick = False
        self.sendkeys = ""
        self.component_args = ""
        self.mouse_or_key_is_set = False
        self.scraper = False
        self.is_textfinder = False
        self.x_offset = None
        self.y_offset = None
        
class AlyvixObjectsSelection(QWidget, Ui_Form_2):

    
    def __init__(self, parent=None, is_main=False):

                    
        global old_order
        global old_section
        
        QWidget.__init__(self)
        
        self.setupUi(self)
        
        #self.setWindowTitle("Alyvix - Select Component")
        
                
        self.parent = parent
        
        self.is_main = is_main
        
        self.scaling_factor = self.parent.parent.scaling_factor
        
        icon_path = get_python_lib() + os.sep + "alyvix" + os.sep + "extra" + os.sep + "robotide" + os.sep +"images"
             
        old_order = Qt.AscendingOrder
        old_section = 2
        
        if self.scaling_factor <= 1.3:
            
            icon = QIcon()
            icon.addPixmap(QPixmap(icon_path + "/16x16/window-close.png"), QIcon.Normal, QIcon.Off)
            self.toolButtonCancelText.setIcon(icon)
            
            icon = QIcon()
            icon.addPixmap(QPixmap(icon_path + "/32x32/dialog-ok-3.png"), QIcon.Normal, QIcon.Off)
            self.toolButtonOk.setIcon(icon)
            #self.toolButtonImageFinder.setIconSize(QSize(64, 64))
            
            icon = QIcon()
            icon.addPixmap(QPixmap(icon_path + "/32x32/window-close-2.png"), QIcon.Normal, QIcon.Off)
            self.toolButtonCancel.setIcon(icon)
            
        else:
            icon = QIcon()
            icon.addPixmap(QPixmap(icon_path + "/32x32/window-close.png"), QIcon.Normal, QIcon.Off)
            self.toolButtonCancelText.setIcon(icon)
            
            icon = QIcon()
            icon.addPixmap(QPixmap(icon_path + "/64x64/dialog-ok-3.png"), QIcon.Normal, QIcon.Off)
            self.toolButtonOk.setIcon(icon)
            
            icon = QIcon()
            icon.addPixmap(QPixmap(icon_path + "/64x64/window-close-2.png"), QIcon.Normal, QIcon.Off)
            self.toolButtonCancel.setIcon(icon)
        
        #self.setFixedSize(self.size())
        #self.setFixedSize(int(self.frameGeometry().width() * self.scaling_factor), int(self.frameGeometry().height() * self.scaling_factor))
        
        #self.listWidgetAlyObj.setGeometry(QRect(int(self.listWidgetAlyObj.geometry().x() * self.scaling_factor), int(self.listWidgetAlyObj.geometry().y() * self.scaling_factor),
        #                        int(self.listWidgetAlyObj.geometry().width() * self.scaling_factor), int(self.listWidgetAlyObj.geometry().height() * self.scaling_factor)))
            
        #self.resize(int(self.width() * self.scaling_factor),
        #         int(425 * self.scaling_factor))
        
        self.toolButtonOk.setMinimumSize(QSize(int(self.toolButtonOk.minimumSize().width() * self.scaling_factor), 0))
        self.toolButtonOk.setIconSize(QSize(int(32* self.scaling_factor), int(32* self.scaling_factor)))
        
        self.toolButtonCancel.setMinimumSize(QSize(int(self.toolButtonCancel.minimumSize().width() * self.scaling_factor), 0))
        self.toolButtonCancel.setIconSize(QSize(int(32* self.scaling_factor), int(32* self.scaling_factor)))

        self.widget.setGeometry(int(self.widget.x() * self.scaling_factor), int(self.widget.y()*self.scaling_factor),
                                            int(self.widget.width()*self.scaling_factor), int(self.widget.height()*self.scaling_factor))

                                            
        self.gridLayoutWidget.setGeometry(QRect(int(self.gridLayoutWidget.geometry().x() * self.scaling_factor), int(self.gridLayoutWidget.geometry().y() * self.scaling_factor),
                                          int(self.gridLayoutWidget.geometry().width() * self.scaling_factor), int(self.gridLayoutWidget.geometry().height() * self.scaling_factor)))
                               
        self.gridLayoutWidget_2.setGeometry(QRect(int(self.gridLayoutWidget_2.geometry().x() * self.scaling_factor), int(self.gridLayoutWidget_2.geometry().y() * self.scaling_factor),
                                          int(self.gridLayoutWidget_2.geometry().width() * self.scaling_factor), int(self.gridLayoutWidget_2.geometry().height() * self.scaling_factor)))
           
        
        self._old_main_list_item = None
        
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        self.update_list()
        
        self.connect(self.toolButtonOk, SIGNAL('clicked()'), self.push_button_select_event)   
        self.connect(self.toolButtonCancel, SIGNAL('clicked()'), self.push_button_cancel_event)   
        self.connect(self.lineEditSearch, SIGNAL("textChanged(QString)"), self, SLOT("search_event(QString)"))
        self.connect(self.toolButtonCancelText, SIGNAL("clicked()"), self.clear_text)
        
        self.lineEditSearch.installEventFilter(self)
        
        self.setMinimumWidth(int(325 * self.scaling_factor))
        
        """
        if self.scaling_factor <= 1.3:
            self.setMinimumHeight(int(427 * self.scaling_factor))
        else:
            self.setMinimumHeight(int(427 * self.scaling_factor))
            
        """
        
        self.resize(int(self.width() * self.scaling_factor),
                         int(425 * self.scaling_factor))
                         
        self.setMinimumHeight(int(350 * self.scaling_factor))
        
        header = self.tableWidget.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignLeft)
        

        header.setDefaultSectionSize(int(370*self.scaling_factor))
        
        header.setSortIndicator(2, Qt.AscendingOrder)
        
        header.setResizeMode(0, QHeaderView.Interactive)
        header.setResizeMode(1, QHeaderView.ResizeToContents)
        
        self.tableWidget.resizeRowsToContents()
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:

            self.close()
        
    def eventFilter(self, object, event):
        #print event
        #if event.type() == QEvent.KeyPress:

        
        try:
            if event.type() == event.MouseButtonPress:
            
                if self.lineEditSearch.text() == "search..." and object.objectName() == "lineEditSearch":
                    self.lineEditSearch.setText("")
                    return True
                    
            if event.type() == event.KeyPress:
            
                if self.lineEditSearch.text() == "search..." and object.objectName() == "lineEditSearch":
                    self.lineEditSearch.setText("")

                    
            if event.type()== event.FocusOut:
                if self.lineEditSearch.text() == "" and object.objectName() == "lineEditSearch":
                    self.lineEditSearch.setText("search...")
                    return True
        except:
            pass
        return super(AlyvixObjectsSelection, self).eventFilter(object, event)
        
    def clear_text(self):
        #if text == "search...":
        #    self.update_list_for_search()
        self.lineEditSearch.setText("search...")
        
    def resizeEvent(self, event):
    
        self.resize_all()
        
        
    def resize_all(self):

        #340 310
        
        #if resize_factor_h >= 1 and resize_factor_w >= 1:
        
        
        self.widget.setGeometry(QRect(self.widget.x(), self.widget.y(),
                                            int(self.frameGeometry().width()), int(self.frameGeometry().height())))
                                            
        self.gridLayoutWidget_2.setGeometry(QRect(self.gridLayoutWidget_2.x(), self.gridLayoutWidget_2.y(),
                                            int(self.frameGeometry().width() - (30*self.scaling_factor)), int(self.frameGeometry().height() - (100*self.scaling_factor))))
                                            
        self.gridLayoutWidget.setGeometry(QRect(self.gridLayoutWidget.x(), self.gridLayoutWidget_2.y() + self.gridLayoutWidget_2.height() + (3*self.scaling_factor),
                                            int(self.gridLayoutWidget.width()), int(self.gridLayoutWidget.height())))
        
        header = self.tableWidget.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignLeft)
        
        header.setDefaultSectionSize(int(self.gridLayoutWidget_2.width()*0.64))
        
        
        header.setResizeMode(0, QHeaderView.Interactive)
        header.setResizeMode(1, QHeaderView.ResizeToContents)
        
        self.tableWidget.resizeRowsToContents()
        
        
    def closeEvent(self, event):
        
        #print "self close"

        if self.parent._main_object_finder.xml_path != "":
            try:
                image = QImage(self.parent._main_object_finder.xml_path.replace("xml", "png"))   
                self.parent.pv.set_bg_pixmap(image)


            except:
                
                pass
        
        try:
            self.parent.pv.showFullScreen()
        except:
            pass #no image if we dont have selected a main
            
        #self.parent.obj_Selection_open = False

        #print self.parent.parent.xx
        self.parent.show()
        
        
    @pyqtSlot(QString)
    def search_event(self, text):
        if text == "search...":
            self.update_list_for_search()
        elif text == "":
            self.update_list_for_search()
        else:
            self.update_list_for_search(str(text.toUtf8()))
            
    def update_list_for_search(self, text_to_search=None):
        allRows = self.tableWidget.rowCount()
        for row_index in xrange(0,allRows):              
            
            name = self.tableWidget.item(row_index, 0).data(Qt.EditRole).toString()
            
            if text_to_search is not None and text_to_search not in name:
                self.tableWidget.setRowHidden(row_index, True)
            else:
                self.tableWidget.setRowHidden(row_index, False)
            #print name
            #type = self.tableWidget.item(row_index, 1).data(Qt.EditRole).toString()
            #date = self.tableWidget.item(row_index, 2).data(Qt.EditRole).toString()
        
    def update_list(self):
        #dirs = os.listdir(self.full_file_name)
        #dirs = [d for d in os.listdir(self.path) if os.path.isdir(os.path.join(self.path, d))]
        
        global old_order
        global old_section
        
        icon_path = get_python_lib() + os.sep + "alyvix" + os.sep + "extra" + os.sep + "robotide" + os.sep +"images"
        
        header = self.tableWidget.horizontalHeader()
        
        if header.sortIndicatorOrder() == Qt.AscendingOrder:
            old_order = Qt.AscendingOrder
            #print "AscendingOrder"
        else:
            old_order = Qt.DescendingOrder
            #print "DescendingOrder"
        
        #clear sorting filter
        header.setSortIndicator(3, Qt.DescendingOrder)
        
        #self.listWidgetAlyObj.clear()
        self.tableWidget.setRowCount(0)
        
        extra_path = get_python_lib() + os.sep + "alyvix" + os.sep + "robotproxy" + os.sep + self.parent._path.split(os.sep)[-1] + "_extra"
        
        obj_to_exclude = []

        for parent_item_index in range(self.parent.listWidget.count()):
            parent_item = self.parent.listWidget.item(parent_item_index).data(Qt.UserRole).toString()
            obj_to_exclude.append(parent_item)
        
        # path to the directory (relative or absolute)
        dirpath = self.parent._path

        # get all entries in the directory w/ stats
        entries = (os.path.join(dirpath, fn) for fn in os.listdir(dirpath))
        entries = ((os.stat(path), path) for path in entries)

        # leave only regular files, insert creation date
        entries = ((stat[ST_CTIME], path)
                   for stat, path in entries if S_ISREG(stat[ST_MODE]))
        #NOTE: on Windows `ST_CTIME` is a creation date 
        #  but on Unix it could be something else
        #NOTE: use `ST_MTIME` to sort by a modification date
        
        icon_prefix_sf = "16x16"
        if self.scaling_factor > 1.3:
            icon_prefix_sf = "32x32"

        lock_list_name = self.parent._path + os.sep + "lock_list.xml"
        
        doc = None
        if os.path.exists(lock_list_name):
            doc = minidom.parse(lock_list_name)
            root_node = doc.getElementsByTagName("items")[0]
            
            items_node = doc.getElementsByTagName("item")
            
        for cdate, path in sorted(entries):
            filename = os.path.basename(path)
            #print filename
            
            continue_the_loop = False
            
            item_type = QTableWidgetItem()
            item_date = QTableWidgetItem()
            item_name = QTableWidgetItem()
            
            if doc is not None:

                for item_node in items_node:
                    owner = item_node.getElementsByTagName("owner")[0].firstChild.nodeValue
                    file_name = item_node.getElementsByTagName("name")[0].firstChild.nodeValue
                    if owner != self.parent._main_object_finder.name + "_ObjectFinder.xml" and file_name == filename:
                        continue_the_loop = True
                        
                                
            for name_to_exclude in obj_to_exclude:
                if filename == name_to_exclude:
                    continue_the_loop = True
                    
            if filename.endswith('.xml'):
                if filename.endswith('_ObjectFinder.xml') or filename.endswith('list.xml') or filename.endswith('data.xml') or (filename.endswith('_TextFinder.xml') is True and self.is_main is True) or continue_the_loop is True:
                    continue_the_loop = False
                    continue
                    
                item = QListWidgetItem()
                if filename.endswith('_RectFinder.xml'):                    
                    item_name.setData(Qt.EditRole, filename[:-15]);#item.setText(filename[:-15] + " [RF]")
                    item_type.setData(Qt.EditRole, "RF")
                    
                    icon = QIcon()
                    icon.addPixmap(QPixmap(icon_path + os.sep + icon_prefix_sf + "/preferences-desktop-theme.png"), QIcon.Normal, QIcon.Off)
                    item_type.setIcon(icon)
                    
                elif filename.endswith('_ImageFinder.xml'):
                    item_name.setData(Qt.EditRole, filename[:-16]);#item.setText(filename[:-15] + " [RF]")
                    item_type.setData(Qt.EditRole, "IF")
                    
                    icon = QIcon()
                    icon.addPixmap(QPixmap(icon_path + os.sep + icon_prefix_sf + "/user-desktop.png"), QIcon.Normal, QIcon.Off)
                    item_type.setIcon(icon)
                    
                elif filename.endswith("_TextFinder.xml"):
                
                    scraper_path = extra_path + os.sep + filename.replace("_TextFinder.xml","")
                    scraper_file = scraper_path + os.sep + "scraper.txt"
                    if os.path.exists(scraper_file):
                        #item.setText(filename[:-15] + " [TS]")
                        item_name.setData(Qt.EditRole, filename[:-15]);#item.setText(filename[:-15] + " [RF]")
                        item_type.setData(Qt.EditRole, "TS")
                    else:
                        item_name.setData(Qt.EditRole, filename[:-15]);#item.setText(filename[:-15] + " [RF]")
                        item_type.setData(Qt.EditRole, "TF")
                        
                    icon = QIcon()
                    icon.addPixmap(QPixmap(icon_path + os.sep + icon_prefix_sf + "/texteffect.png"), QIcon.Normal, QIcon.Off)
                    item_type.setIcon(icon)

                date = datetime.datetime.fromtimestamp(cdate)
                #print date.strftime("%Y-%m-%d %H:%M:%S")

                some_date =  QDateTime.fromString (date.strftime("%Y-%m-%d %H:%M:%S"), "yyyy-MM-dd HH:mm:ss")
                #print some_date.toString("yyyy-MM-dd HH:mm:ss")
                #myDTE = QDateTimeEdit()
                #myDTE.setDateTime(some_date)
                item_date.setData(Qt.EditRole, some_date)
                    
                item_type.setData(Qt.UserRole, filename)
                
                self.tableWidget.insertRow ( self.tableWidget.rowCount() );
                self.tableWidget.setItem   ( self.tableWidget.rowCount()-1, 
                         0, 
                         item_name);
                         
                self.tableWidget.setItem   ( self.tableWidget.rowCount()-1, 
                         1, 
                         item_type)
                self.tableWidget.setItem   ( self.tableWidget.rowCount()-1, 
                         2, 
                         item_date);
                         
                         
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        if self.lineEditSearch.text() != "" and self.lineEditSearch.text() != "search...":
            self.update_list_for_search(self.lineEditSearch.text())
            
        header.setSortIndicator(old_section, old_order)
            
                
    def push_button_select_event(self):
            
        if self.tableWidget.rowCount() == 0:
            return
                
        if self.tableWidget.currentRow() < 0:
            return
            
        if self.parent.button_selected == "set_main_object":
            #print "set_main_object"
            if len(self.parent._sub_objects_finder) != 0:

                item = QListWidgetItem()
                item.setText("")
                self._old_main_list_item = self.parent.listWidget.takeItem(0)
                self.parent.listWidget.insertItem(0, item)
                
                #self.parent.delete_all_sub_roi()
                
                self.parent._main_deleted = True

            self.set_main_object()
        elif self.parent.button_selected == "add_sub_object":
            self.add_sub_object()
            
    def push_button_cancel_event(self):

        self.close()
                
    def set_main_object(self):
            

        indexes = self.tableWidget.selectionModel().selectedRows()
        last_index = -1
        for index in sorted(indexes):
            #print('Row %d is selected' % index.row())
            last_index = index.row()
            
        last_selected_index = last_index
        
        xml_name = str(self.tableWidget.item(last_index, 1).data(Qt.UserRole).toString())
        
        xml_name = self.parent._path + os.sep + xml_name
        
        #self.parent._main_object_finder.xml_path = xml_name
        
        old_main_pos = (self.parent._main_object_finder.x, self.parent._main_object_finder.y)
        
        if self.parent.set_main_object(xml_name) is False:
            if self._old_main_list_item is not None:
                self.parent.listWidget.takeItem(0)
                self.parent.listWidget.insertItem(0,self._old_main_list_item)
                self._old_main_list_item = None
            #self.parent.show()
            self.close()
            return
        
        """
        if self.parent._main_deleted is True and len(self.parent._sub_objects_finder) > 0:
            self.parent.pv = PaintingView(self.parent)
            image = QImage(self.parent._main_object_finder.xml_path.replace("xml", "png"))   
            self.parent.pv.set_bg_pixmap(image)
            self.parent.pv.showFullScreen()
        elif self.parent._main_deleted is True:
            self.parent._main_deleted = False
            self.parent.show()
        else:
            self.parent.show()
        """
        
        self.parent._main_deleted = False
        self.parent.reset_all_sub_roi(old_main_pos)
        #self.parent.show()
        self.close()
        
    def add_sub_object(self):
            
        #print self.listWidgetAlyObj.currentRow()
        
        indexes = self.tableWidget.selectionModel().selectedRows()
        #print indexes

        for index in indexes:
            #print('Row %d is selected' % index.row())
        
            xml_name = str(self.tableWidget.item(index.row(), 1).data(Qt.UserRole).toString())
            
            xml_name = self.parent._path + os.sep + xml_name
            
            if self.parent.add_sub_object(xml_name) is False:
            
                pass #self.parent.show()
        
        self.close()
        
            

class LineTextWidget(QFrame):
 
    class NumberBar(QWidget):
 
        def __init__(self, *args):
            QWidget.__init__(self, *args)
            self.edit = None
            # This is used to update the width of the control.
            # It is the highest line that is currently visibile.
            self.highest_line = 0
 
        def setTextEdit(self, edit):
            self.edit = edit
 
        def update(self, *args):
            '''
            Updates the number bar to display the current set of numbers.
            Also, adjusts the width of the number bar if necessary.
            '''
            # The + 4 is used to compensate for the current line being bold.
            width = self.fontMetrics().width(str(self.highest_line)) + 4
            if self.width() != width:
                self.setFixedWidth(width)
            QWidget.update(self, *args)
 
        def paintEvent(self, event):
            contents_y = self.edit.verticalScrollBar().value()
            page_bottom = contents_y + self.edit.viewport().height()
            font_metrics = self.fontMetrics()
            current_block = self.edit.document().findBlock(self.edit.textCursor().position())
 
            painter = QPainter(self)
 
            line_count = 0
            # Iterate over all text blocks in the document.
            block = self.edit.document().begin()
            while block.isValid():
                line_count += 1
 
                # The top left position of the block in the document
                position = self.edit.document().documentLayout().blockBoundingRect(block).topLeft()
 
                # Check if the position of the block is out side of the visible
                # area.
                if position.y() > page_bottom:
                    break
 
                # We want the line number for the selected line to be bold.
                bold = False
                if block == current_block:
                    bold = True
                    font = painter.font()
                    font.setBold(True)
                    painter.setFont(font)
 
                # Draw the line number right justified at the y position of the
                # line. 3 is a magic padding number. drawText(x, y, text).
                painter.drawText(self.width() - font_metrics.width(str(line_count)) - 3, round(position.y()) - contents_y + font_metrics.ascent(), str(line_count))
 
                # Remove the bold style if it was set previously.
                if bold:
                    font = painter.font()
                    font.setBold(False)
                    painter.setFont(font)
 
                block = block.next()
 
            self.highest_line = line_count
            painter.end()
 
            QWidget.paintEvent(self, event)
 
 
    def __init__(self, *args):
        QFrame.__init__(self, *args)
 
        #self.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
 
        self.edit = QTextEdit(*args)
        #self.edit.setFrameStyle(QFrame.NoFrame)
        self.edit.setLineWrapMode(QTextEdit.NoWrap)
        self.edit.setAcceptRichText(False)
        self.edit.setReadOnly(True)
 
        self.number_bar = self.NumberBar()
        self.number_bar.setTextEdit(self.edit)
 
        hbox = QHBoxLayout(self)
        hbox.setSpacing(0)
        hbox.setMargin(0)
        hbox.addWidget(self.number_bar)
        hbox.addWidget(self.edit)

        self.edit.installEventFilter(self)
        self.edit.viewport().installEventFilter(self)
        
                    
    def setText(self, text):
        self.edit.setText(text)
 
    def eventFilter(self, object, event):
        # Update the line numbers for all events on the text edit and the viewport.
        # This is easier than connecting all necessary singals.
        if object in (self.edit, self.edit.viewport()):
            self.number_bar.update()
            return False
        return QFrame.eventFilter(object, event)

 
    def getTextEdit(self):
        return self.edit
        
    
class PaintingView(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self)
        
        self.parent = parent
        
        self.scaling_factor = self.parent.scaling_factor
        
        self.ignore_release = False
        
        self._bg_pixmap = QPixmap()
        self.__capturing = False
        
        self.__click_position = QPoint(0,0)
        
        self._sub_rects_finder = []
        
        
        self.__move_index = None
        self.__flag_moving_rect = False
        self.__drag_border = False
        
        self.__flag_mouse_is_on_left_border = False
        self.__flag_mouse_is_on_right_border = False
        self.__flag_mouse_is_on_top_border = False
        self.__flag_mouse_is_on_bottom_border = False
        self.__flag_mouse_is_on_border = None
        
        self.__flag_mouse_is_on_left_up_corner = False
        self.__flag_mouse_is_on_right_up_corner = False
        self.__flag_mouse_is_on_right_bottom_corner = False
        self.__flag_mouse_is_on_left_bottom_corner = False
        
        self.__border_index = None
        
        
        
        self.__flag_mouse_is_on_left_border_roi = False
        self.__flag_mouse_is_on_right_border_roi = False
        self.__flag_mouse_is_on_top_border_roi = False
        self.__flag_mouse_is_on_bottom_border_roi = False
        
        self.__flag_mouse_is_on_left_up_corner_roi = False
        self.__flag_mouse_is_on_right_up_corner_roi = False
        self.__flag_mouse_is_on_right_bottom_corner_roi = False
        self.__flag_mouse_is_on_left_bottom_corner_roi = False
        
        
        self._old_width_rect = 0
        self._old_height_rect = 0
        self._old_x_rect = 0
        self._old_y_rect = 0
        self._old_roi_width_rect = 0
        self._old_roi_height_rect = 0
        self._old_roi_x_rect = 0
        self._old_roi_y_rect = 0
        
        
        #flags
        #self.__flag_mouse_left_button_is_pressed = False
        self.__flag_mouse_is_inside_rect = False
        self.__flag_capturing_sub_rect_roi = False
        self.__flag_capturing_sub_rect = False
        self.__flag_need_to_delete_roi = False
        self.__flag_need_to_restore_roi = False
        self._flag_show_min_max = False
        self._self_show_tolerance = False

        self.__index_deleted_rect_inside_roi = -1
        self.__restored_rect_roi = False
        
        self.setMouseTracking(True)
        
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        #self.setAttribute(Qt.WA_DeleteOnClose)
        
    def closeEvent(self, event):

        pass #self.deleteLater()
        
            
    def keyPressEvent(self, event):
        global last_pos
        if event.modifiers() == Qt.ControlModifier:
            self.ignore_release = True
        
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Z: 
            pass #self.delete_sub_roi()
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Y:
            pass #self.restore_sub_roi()    
        if (event.key() == Qt.Key_Escape) or (event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_O):
            
            if (event.key() == Qt.Key_O and self.parent._last_sub_object != None and self.parent._sub_objects_finder[self.parent.sub_object_index].roi_height != 0 and self.parent._sub_objects_finder[self.parent.sub_object_index].roi_width != 0):
                self.parent._last_sub_object = None    
                self.parent.saveUpdatedTextRoi()
                self.ignore_release = False
                self.update()
                self.parent.show()
                self.parent.activateWindow()
                if last_pos is not None:
                    self.parent.move(last_pos[0],last_pos[1])
                self.parent._redraw_index = None
                self.parent._can_set_roi_unlim = False
            elif (event.key() == Qt.Key_O and self.parent._last_sub_object != None and self.parent._last_sub_object.roi_x == 0 and self.parent._last_sub_object.roi_y == 0 and self.parent._last_sub_object.roi_width == 0 and self.parent._last_sub_object.roi_width == 0):
                event.ignore()
            elif (event.key() == Qt.Key_Escape and self.parent._last_sub_object != None and self.parent._last_sub_object.roi_width != 0 and self.parent._last_sub_object.roi_width != 0):
                self.parent._sub_objects_finder[self.parent.sub_object_index] = copy.deepcopy(self.parent._last_sub_object)
                self.parent._last_sub_object = None    
                self.parent.saveUpdatedTextRoi()
                self.ignore_release = False
                self.update()
                self.parent.show()
                self.parent.activateWindow()
                if last_pos is not None:
                    self.parent.move(last_pos[0],last_pos[1])
                self.parent._redraw_index = None
                self.parent._can_set_roi_unlim = False
            elif (event.key() == Qt.Key_Escape and self.parent._last_sub_object != None and self.parent._sub_objects_finder[self.parent.sub_object_index].roi_height != 0 and self.parent._sub_objects_finder[self.parent.sub_object_index].roi_width != 0):
                self.parent._last_sub_object = None  
                self.ignore_release = False                
                self.parent.saveUpdatedTextRoi()
                self.update()
                self.parent.show()
                self.parent.activateWindow()
                if last_pos is not None:
                    self.parent.move(last_pos[0],last_pos[1])
                self.parent._redraw_index = None
                self.parent._can_set_roi_unlim = False
            elif (event.key() == Qt.Key_Escape and self.parent._last_sub_object != None and self.parent._last_sub_object.roi_x == 0 and self.parent._last_sub_object.roi_y == 0 and self.parent._last_sub_object.roi_width == 0 and self.parent._last_sub_object.roi_width == 0):
                event.ignore()
            elif (len(self.parent._sub_objects_finder) >0 and self.parent._sub_objects_finder[-1].roi_height != 0 and self.parent._sub_objects_finder[-1].roi_width != 0 and self.parent._main_deleted is False):
                #self.parent.raise_()
                self.parent.saveUpdatedTextRoi()
                self.ignore_release = False
                self.parent.show()
                self.parent.activateWindow()
                if last_pos is not None:
                    self.parent.move(last_pos[0],last_pos[1])
                self.parent._redraw_index = None
                self.parent._can_set_roi_unlim = False
                #self.close()
            elif (event.key() == Qt.Key_Escape and len(self.parent._sub_objects_finder) >0 and self.parent._sub_objects_finder[-1].roi_height == 0 and self.parent._sub_objects_finder[-1].roi_width == 0 and self.parent._main_deleted is False):
                item = self.parent.listWidget.takeItem(0 + len(self.parent._sub_objects_finder))
                self.parent.listWidget.removeItemWidget(item)
                del self.parent._sub_objects_finder[-1]
                self.parent.saveUpdatedTextRoi()
                self.ignore_release = False
                self.parent.show()
                self.parent.activateWindow()
                if last_pos is not None:
                    self.parent.move(last_pos[0],last_pos[1])
                self.parent._can_set_roi_unlim = False

            elif len(self.parent._sub_objects_finder) == 0:
                self.parent.saveUpdatedTextRoi()
                self.ignore_release = False
                self.parent.show()
                self.parent.activateWindow()
                if last_pos is not None:
                    self.parent.move(last_pos[0],last_pos[1])
                self.parent._can_set_roi_unlim = False
            #self.parent._can_set_roi_unlim == True
        
        
        if self.parent._can_set_roi_unlim == True:
        
            _index_roi = self.parent._redraw_index 
            
            if _index_roi == None and self.parent._main_deleted is True:
                _index_roi = self.parent._roi_restored_after_deleted_main -1
                
            if _index_roi == None:
                _index_roi = -1
                
            if self.parent._sub_objects_finder[_index_roi].roi_height != 0 and self.parent._sub_objects_finder[_index_roi].roi_width != 0:
            
                if event.key() == Qt.Key_Down:
                
                    if self.__capturing == False:
                        self.parent._sub_objects_finder[_index_roi].roi_unlimited_down = True
                        self.update()
                        
                if event.key() == Qt.Key_Up:
                
                    if self.__capturing == False:
                        self.parent._sub_objects_finder[_index_roi].roi_unlimited_up = True
                        self.update()
                        
                if event.key() == Qt.Key_Left:
                
                    if self.__capturing == False:
                        self.parent._sub_objects_finder[_index_roi].roi_unlimited_left = True
                        self.update()
                        
                if event.key() == Qt.Key_Right:
                
                    if self.__capturing == False:
                        self.parent._sub_objects_finder[_index_roi].roi_unlimited_right = True
                        self.update()
                        
    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Control:
            self.ignore_release = False
            #print "self.ignore_release", self.ignore_release
        
    def set_bg_pixmap(self, image):
        self._bg_pixmap = QPixmap.fromImage(image)
        
    def mouseMoveEvent(self, event):
        self.update()  
            
    def mouseDoubleClickEvent(self, event):
        pass
        """
        if False is True:
            #self.BringWindowToFront()
            return
        if self.is_mouse_inside_rect(self._main_rect_finder):
            self.rect_view_properties = AlyvixRectFinderPropertiesView(self)
            self.rect_view_properties.show()
        """
        
    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
        
            if event.modifiers() == Qt.ControlModifier:
            
                if self.__flag_mouse_is_inside_rect is not None and self.__flag_mouse_is_inside_rect != 0:
                    index = self.__flag_mouse_is_inside_rect -1
                    
                    #print self.__flag_mouse_is_inside_rect
                    
                    """
                    
                    percentage_screen_w = int(0.1 * self._bg_pixmap.width())
                    percentage_screen_h = int(0.1 * self._bg_pixmap.height())
                    percentage_object_w = int(0.5 * self.parent._sub_objects_finder[index].width)
                    percentage_object_h = int(0.5 * self.parent._sub_objects_finder[index].height)
                    
                    roi_height = percentage_screen_h + percentage_object_h + self.parent._sub_objects_finder[index].height
                    
                    roi_width = percentage_screen_w + percentage_object_w + self.parent._sub_objects_finder[index].width
                    
                    roi_width_half = int((roi_width - self.parent._sub_objects_finder[index].width)/2)
                    roi_height_half = int((roi_height - self.parent._sub_objects_finder[index].height)/2)
                    
                    self.parent._sub_objects_finder[index].roi_x =  (self.parent._sub_objects_finder[index].x - self.parent._main_object_finder.x) - roi_width_half
                    self.parent._sub_objects_finder[index].roi_y =  (self.parent._sub_objects_finder[index].y - self.parent._main_object_finder.y) - roi_height_half
                    self.parent._sub_objects_finder[index].roi_height = roi_height
                    self.parent._sub_objects_finder[index].roi_width = roi_width
                    """
                    

                    hw_factor = 0
                                        
                    if self.parent._sub_objects_finder[index].height < self.parent._sub_objects_finder[index].width:
                        hw_factor = self.parent._sub_objects_finder[index].height
                    else:
                        hw_factor = self.parent._sub_objects_finder[index].width
                        
                        
                    sc_factor = 0
                                
                    if self._bg_pixmap.height() < self._bg_pixmap.width():
                        sc_factor = self._bg_pixmap.height()
                    else:
                        sc_factor = self._bg_pixmap.width()
                        
                    percentage_screen_w = int(0.0125 * sc_factor)
                    percentage_screen_h = int(0.0125 * sc_factor)
                    percentage_object_w = int(0.2 * hw_factor) #image_finder.width)
                    percentage_object_h = int(0.2 * hw_factor) #image_finder.height)
                    
                    roi_height = percentage_screen_h + percentage_object_h + self.parent._sub_objects_finder[index].height
                    
                    roi_width = percentage_screen_w + percentage_object_w + self.parent._sub_objects_finder[index].width
                    
                    """
                    hw_factor = 0

                    if self.parent._sub_objects_finder[index].height < self.parent._sub_objects_finder[index].width:
                        hw_factor = self.parent._sub_objects_finder[index].height
                    else:
                        hw_factor = self.parent._sub_objects_finder[index].width

                    roi_height = int(0.95 * hw_factor) + self.parent._sub_objects_finder[index].height

                    roi_width = int(0.95 * hw_factor) + self.parent._sub_objects_finder[index].width
                    """

                    roi_width_half = int((roi_width - self.parent._sub_objects_finder[index].width)/2)

                    roi_height_half = int((roi_height - self.parent._sub_objects_finder[index].height)/2)


                    self.parent._sub_objects_finder[index].roi_x =  (self.parent._sub_objects_finder[index].x - self.parent._main_object_finder.x) - roi_width_half
                    self.parent._sub_objects_finder[index].roi_y =  (self.parent._sub_objects_finder[index].y - self.parent._main_object_finder.y) - roi_height_half
                    self.parent._sub_objects_finder[index].roi_height = self.parent._sub_objects_finder[index].height + (roi_height_half*2)
                    self.parent._sub_objects_finder[index].roi_width = self.parent._sub_objects_finder[index].width + (roi_width_half*2)
                    
                    """
                    roi_height = int(0.30*hw_factor*self.scaling_factor) + self.parent._sub_objects_finder[index].height #int(10*self.scaling_factor) + self.parent._sub_objects_finder[index].height

                    roi_width = int(0.30*hw_factor*self.scaling_factor) + self.parent._sub_objects_finder[index].width #int(10*self.scaling_factor) + self.parent._sub_objects_finder[index].width


                    roi_width_half = int((roi_width - self.parent._sub_objects_finder[index].width)/2)
                    roi_height_half = int((roi_height - self.parent._sub_objects_finder[index].height)/2)

                    self.parent._sub_objects_finder[index].roi_x =  (self.parent._sub_objects_finder[index].x - self.parent._main_object_finder.x) - roi_width_half
                    self.parent._sub_objects_finder[index].roi_y =  (self.parent._sub_objects_finder[index].y - self.parent._main_object_finder.y) - roi_height_half
                    self.parent._sub_objects_finder[index].roi_height = roi_height
                    self.parent._sub_objects_finder[index].roi_width = roi_width
                    """
                    
                    
                    if self.parent._main_object_finder.y + self.parent._sub_objects_finder[index].roi_y < 0:
                    
                        under_zero = abs(self.parent._main_object_finder.y + self.parent._sub_objects_finder[index].roi_y)
                        self.parent._sub_objects_finder[index].roi_y = self.parent._sub_objects_finder[index].roi_y + under_zero
                        self.parent._sub_objects_finder[index].roi_height = self.parent._sub_objects_finder[index].roi_height - under_zero
                        
                    
                    if self.parent._main_object_finder.y + self.parent._sub_objects_finder[index].roi_y + self.parent._sub_objects_finder[index].roi_height > self._bg_pixmap.height():
                    
                        diff = (self.parent._main_object_finder.y + self.parent._sub_objects_finder[index].roi_y + self.parent._sub_objects_finder[index].roi_height) - self._bg_pixmap.height()

                        self.parent._sub_objects_finder[index].roi_height = self.parent._sub_objects_finder[index].roi_height - diff - 1
                        
                    if self.parent._main_object_finder.x + self.parent._sub_objects_finder[index].roi_x < 0:
                    
                        under_zero = abs(self.parent._main_object_finder.x + self.parent._sub_objects_finder[index].roi_x)
                        self.parent._sub_objects_finder[index].roi_x = self.parent._sub_objects_finder[index].roi_x + under_zero
                        self.parent._sub_objects_finder[index].roi_width = self.parent._sub_objects_finder[index].roi_width - under_zero
                        
                    
                    if self.parent._main_object_finder.x + self.parent._sub_objects_finder[index].roi_x + self.parent._sub_objects_finder[index].roi_width > self._bg_pixmap.width():
                    
                        diff = (self.parent._main_object_finder.x + self.parent._sub_objects_finder[index].roi_x + self.parent._sub_objects_finder[index].roi_width) - self._bg_pixmap.width()

                        self.parent._sub_objects_finder[index].roi_width = self.parent._sub_objects_finder[index].roi_width - diff - 1
                    
                    
                    
                    self.parent._sub_objects_finder[index].roi_unlimited_left = False
                    
                    self.parent._sub_objects_finder[index].roi_unlimited_right = False
                    
                    self.parent._sub_objects_finder[index].roi_unlimited_up = False
                    
                    self.parent._sub_objects_finder[index].roi_unlimited_down = False
                    
                    if self.parent._sub_objects_finder[index].is_textfinder:
                        self.parent.text_finder_roi_modified.append(index)                   
            
            else:
        
                self.__click_position = QPoint(QCursor.pos())
                #self.__capturing = True
                
                if self.__flag_mouse_is_on_border is not None:
                    self.__border_index = self.__flag_mouse_is_on_border
                    self.__drag_border = True
                    if self.__border_index == 0:
                        self._old_height_rect = self.parent._main_object_finder.height
                        self._old_width_rect = self.parent._main_object_finder.width
                        self._old_x_rect = self.parent._main_object_finder.x
                        self._old_y_rect = self.parent._main_object_finder.y
                    else:
                        self._old_height_rect = self.parent._sub_objects_finder[self.__border_index-1].height
                        self._old_width_rect = self.parent._sub_objects_finder[self.__border_index-1].width
                        self._old_x_rect = self.parent._sub_objects_finder[self.__border_index-1].x
                        self._old_y_rect = self.parent._sub_objects_finder[self.__border_index-1].y
                        
                        self._old_roi_height_rect = self.parent._sub_objects_finder[self.__border_index-1].roi_height
                        self._old_roi_width_rect = self.parent._sub_objects_finder[self.__border_index-1].roi_width
                        self._old_roi_x_rect = self.parent._sub_objects_finder[self.__border_index-1].roi_x
                        self._old_roi_y_rect = self.parent._sub_objects_finder[self.__border_index-1].roi_y
                        
                        if not self.__border_index in self.parent.text_finder_roi_modified:
                            self.parent.text_finder_roi_modified.append(self.__border_index-1)
                        
                elif self.__flag_mouse_is_inside_rect is not None:
                    self.__move_index = self.__flag_mouse_is_inside_rect
                    
            
                    if self.__move_index == 0:
                        rect = self.parent._main_object_finder
                    else:
                        rect = self.parent._sub_objects_finder[self.__move_index - 1]
                    
                    self.__position_offset_x = self.__click_position.x() - rect.x
                    self.__position_offset_y =  self.__click_position.y() - rect.y

                elif self.__drag_border is False:  #and self.__move_rect is False:
                    self.__capturing = True
                
        elif event.buttons() == Qt.RightButton:
        
            if event.modifiers() == Qt.ControlModifier:
                index = 0
                delete_sub = False
                delete_main = False
                
                if self.__flag_mouse_is_inside_rect is not None and self.__flag_mouse_is_inside_rect == 0 and len(self.parent._sub_objects_finder) == 0:
                    index = 0
                    delete_main = True
                
                if self.__flag_mouse_is_on_border == 0 and self.__flag_mouse_is_on_border is not None and len(self.parent._sub_objects_finder) == 0:
                    index = 0
                    delete_main = True
                
                
                if self.__flag_mouse_is_inside_rect is not None and self.__flag_mouse_is_inside_rect != 0 and len(self.parent._sub_objects_finder) > 0 and self.parent._main_deleted is False:
                    index = self.__flag_mouse_is_inside_rect -1
                    delete_sub = True
                
                if self.__flag_mouse_is_on_border != 0 and self.__flag_mouse_is_on_border is not None and len(self.parent._sub_objects_finder) > 0 and self.parent._main_deleted is False:
                    index = self.__flag_mouse_is_on_border -1
                    delete_sub = True
                    
                if delete_sub is True:
                    if self.parent._sub_objects_finder[-1].x != 0 and self.parent._sub_objects_finder[-1].y != 0 \
                    and self.parent._sub_objects_finder[-1].width != 0 and self.parent._sub_objects_finder[-1].height != 0:

                        """
                        if selected_index == 0:
                            item = QListWidgetItem()
                            item.setText("")
                            self.listWidget.takeItem(0)
                            self.listWidget.insertItem(0, item)
                        
                            self.button_selected = "set_main_object"
                            self.open_select_obj_window()
                        else:
                        """

                        
                        item = self.parent.listWidget.takeItem(index + 1)
                        
                        filename = self.parent._sub_objects_finder[index].xml_path
                        filename = filename.split(os.sep)[-1]
                        

                        extra_path = get_python_lib() + os.sep + "alyvix" + os.sep + "robotproxy" + os.sep + self.parent._path.split(os.sep)[-1] + "_extra"
                        scraper_path = extra_path + os.sep + filename.replace("_TextFinder.xml","")
                        scraper_file = scraper_path + os.sep + "scraper.txt"
                        #print scraper_file
                        if os.path.exists(scraper_file):
                            self.parent._main_object_finder.is_scraper = False

                        
                        #print selected_index
                        self.parent.listWidget.removeItemWidget(item)
                        #print "rrrrr"
                        del self.parent._sub_objects_finder[index]


                elif delete_main is True:
                    try:
                        self.parent.pv.close()
                    except:
                        pass

                    #item = QListWidgetItem()
                    #item.setText("")
                    self.parent.listWidget.clear()
                    #self.parent.listWidget.insertItem(0, item)
                
                    #self.parent.button_selected = "set_main_object"
                    
                    #self.parent.delete_all_sub_roi()
                    
                    self.parent._main_deleted = True

                    self.parent.update_list()
                    self.parent.widget.show()
                    self.parent.widget_2.hide()
                    self.parent.show()
                    #self.parent.button_selected = "set_main_object"
                    #self.parent.open_select_obj_window()
                    
                                            
                try:
                    self.parent.pv.update()
                except:
                    pass
            else:

        
                if self.__flag_mouse_is_on_border != 0 and self.__flag_mouse_is_on_border is not None:

                    index = self.__flag_mouse_is_on_border-1
                    
                    
                    if self.__flag_mouse_is_on_left_border_roi is True:
                        self.parent._sub_objects_finder[index].roi_unlimited_left = True
                        
                    if self.__flag_mouse_is_on_right_border_roi is True:
                        self.parent._sub_objects_finder[index].roi_unlimited_right = True
                        
                    if self.__flag_mouse_is_on_top_border_roi is True:
                        self.parent._sub_objects_finder[index].roi_unlimited_up = True
                        
                    if self.__flag_mouse_is_on_bottom_border_roi is True:
                        self.parent._sub_objects_finder[index].roi_unlimited_down = True

                    if self.parent._sub_objects_finder[index].is_textfinder is True:
                        self.parent.text_finder_roi_modified.append(index)
                
            self.update()
            
    def mouseReleaseEvent(self, event):
        if self.ignore_release is True:
            event.ignore()
            self.update()
            #print "event ignore"
            return
        if event.button() == Qt.LeftButton:
            self.__capturing = False

            if len(self.parent._deleted_sub_objects) > 0:
                del self.parent._deleted_sub_objects[-1]
                
            if self.__move_index is not None:
                self.__move_index = None
                
            elif self.__drag_border is True:
                self.__drag_border = False
                self.__flag_mouse_is_on_left_border = False
                self.__flag_mouse_is_on_right_border = False
                self.__flag_mouse_is_on_top_border = False
                self.__flag_mouse_is_on_bottom_border = False
                self.__flag_mouse_is_on_border = None
                self.__border_index = None
            else:
                #print "add sub rect roi"
                self.add_sub_rect_roi()
            
        self.update()
        
    def delete_sub_roi(self):
    
        sub_obj = self.parent._sub_objects_finder[-1]    
        
        if sub_obj.roi_height == 0 or sub_obj.roi_width == 0:
            return
        
        #print sub_obj.roi_x, sub_obj.roi_y, sub_obj.roi_height,sub_obj.roi_width
        
        self.parent._deleted_sub_objects.append(copy.deepcopy(sub_obj))
        
        sub_obj.roi_x = 0
        sub_obj.roi_y = 0
        sub_obj.roi_height = 0
        sub_obj.roi_width = 0
        sub_obj.roi_unlimited_up = False
        sub_obj.roi_unlimited_down = False
        sub_obj.roi_unlimited_left = False
        sub_obj.roi_unlimited_right = False
        
        self.update()
        
        
    def restore_sub_roi(self):
    
        if len(self.parent._deleted_sub_objects) > 0:
            sub_obj_deleted = self.parent._deleted_sub_objects[-1]    
            
            sub_obj = self.parent._sub_objects_finder[-1] 
            
            sub_obj.roi_x = sub_obj_deleted.roi_x
            sub_obj.roi_y = sub_obj_deleted.roi_y
            sub_obj.roi_height = sub_obj_deleted.roi_height
            sub_obj.roi_width = sub_obj_deleted.roi_width
            sub_obj.roi_unlimited_up = sub_obj_deleted.roi_unlimited_up
            sub_obj.roi_unlimited_down = sub_obj_deleted.roi_unlimited_down
            sub_obj.roi_unlimited_left = sub_obj_deleted.roi_unlimited_left
            sub_obj.roi_unlimited_right = sub_obj_deleted.roi_unlimited_right
            
            del self.parent._deleted_sub_objects[-1]
            
        self.update()
        
    def add_sub_rect_roi(self):
    
        rect_attributes = self.convert_mouse_position_into_rect()
        
        ori_sub = copy.deepcopy(self.parent._sub_objects_finder[-1])
        
        if rect_attributes is not None:
        
                    
            x, y, width, height = rect_attributes
            

        
            for idx, sub_obj in enumerate(self.parent._sub_objects_finder):
            
                if x < sub_obj.x and y < sub_obj.y and x + width > sub_obj.x + sub_obj.width and y + height > sub_obj.y + sub_obj.height:    

                
                    sub_obj.roi_x = x - self.parent._main_object_finder.x
                    sub_obj.roi_y = y - self.parent._main_object_finder.y
                    sub_obj.roi_height = height
                    sub_obj.roi_width = width
                    
                    self.parent._roi_restored_after_deleted_main = self.parent._roi_restored_after_deleted_main + 1
                    
                    if self.parent._roi_restored_after_deleted_main == len(self.parent._sub_objects_finder):
                        self.parent._roi_restored_after_deleted_main = 0
                        self.parent._main_deleted = False
                        
                    
                    if sub_obj.is_textfinder is True:
                        self.parent.text_finder_roi_modified.append(idx)
                    
                    break
                
    def convert_mouse_position_into_rect(self):
            
        #self.__click_position
        
        mouse_position = QPoint(QCursor.pos())
        
        width = mouse_position.x() - self.__click_position.x()
        height = mouse_position.y() - self.__click_position.y()

        rect = QRect(self.__click_position.x(), self.__click_position.y(), width, height)

        if (rect.width() >= 3 or rect.width() <= -3) and (rect.height() >= 3 or rect.height() <= -3):

            if (rect.width() < 0 and rect.height() < 0):

                x = rect.x() + rect.width()
                y = rect.y() + rect.height()
                w = -rect.width()
                h = -rect.height()
                ##rect = QRect(x, y, w, h)

            elif (rect.width() < 0 and rect.height() > 0):

                x = rect.x() + rect.width()
                y = rect.y()
                w = -rect.width()
                h = rect.height()
                ##rect = QRect(x, y, w, h)

            elif (rect.width() > 0 and rect.height() < 0):

                x = rect.x()
                y = rect.y() + rect.height()
                w = rect.width()
                h = -rect.height()
                ##rect = QRect(x, y, w, h)
            else:
                x = rect.x()
                y = rect.y()
                w = rect.width()
                h = rect.height()
                ##rect = QRect(x, y, w, h)

            if width < 0:
                width = width * -1
            if height < 0:
                height = height * -1
        
            return (x, y, width, height)
            
        else:
            return None
            
    def paintEvent(self, event):
    
        mouse_on_border = False
    
        qp = QPainter()
        qp.begin(self)
        qp.drawPixmap(0, 0, self._bg_pixmap)
        
        self.__flag_mouse_is_inside_rect = None
        self.__index_of_rectangle_with_mouse_inside = -2
        
        if self.__drag_border is False:
            self.__flag_mouse_is_on_left_border = False
            self.__flag_mouse_is_on_right_border = False
            self.__flag_mouse_is_on_top_border = False
            self.__flag_mouse_is_on_bottom_border = False
            
            self.__flag_mouse_is_on_left_up_corner = False
            self.__flag_mouse_is_on_right_up_corner = False
            self.__flag_mouse_is_on_right_bottom_corner = False
            self.__flag_mouse_is_on_left_bottom_corner = False
            
            self.__flag_mouse_is_on_left_border_roi = False
            self.__flag_mouse_is_on_right_border_roi = False
            self.__flag_mouse_is_on_top_border_roi = False
            self.__flag_mouse_is_on_bottom_border_roi = False
            
            self.__flag_mouse_is_on_left_up_corner_roi = False
            self.__flag_mouse_is_on_right_up_corner_roi = False
            self.__flag_mouse_is_on_right_bottom_corner_roi = False
            self.__flag_mouse_is_on_left_bottom_corner_roi = False
            
        #if self.__flag_mouse_is_on_border is None:
        #    self.setCursor(QCursor(Qt.CrossCursor))

        
        if self.parent._main_object_finder is not None:
        
            if self.__drag_border is False and self.__move_index is None and self.__capturing is False and self.parent._main_object_finder.show is True:
                if self.is_mouse_inside_rect(self.parent._main_object_finder):
                    self.__flag_mouse_is_inside_rect = 0
                    #self.setCursor(QCursor(Qt.SizeAllCursor))

                """
                elif self.is_mouse_on_left_border(self.parent._main_object_finder) and self.is_mouse_on_top_border(self.parent._main_object_finder):
                    self.__flag_mouse_is_on_left_up_corner = True
                    self.__flag_mouse_is_on_border = 0
                    mouse_on_border = True
                    #self.setCursor(QCursor(Qt.SizeFDiagCursor))
                    #self.setCursor(Qt.SizeFDiagCursor)
                    
                elif self.is_mouse_on_right_border(self.parent._main_object_finder) and self.is_mouse_on_top_border(self.parent._main_object_finder):
                    self.__flag_mouse_is_on_right_up_corner = True
                    self.__flag_mouse_is_on_border = 0
                    mouse_on_border = True
                    #self.setCursor(QCursor(Qt.SizeBDiagCursor))
                    #QApplication.setOverrideCursor(Qt.SizeBDiagCursor)
                    
                elif self.is_mouse_on_right_border(self.parent._main_object_finder) and self.is_mouse_on_bottom_border(self.parent._main_object_finder):
                    self.__flag_mouse_is_on_right_bottom_corner = True
                    self.__flag_mouse_is_on_border = 0
                    mouse_on_border = True
                    #self.setCursor(QCursor(Qt.SizeFDiagCursor))
                    #QApplication.setOverrideCursor(Qt.SizeFDiagCursor)
                    
                elif self.is_mouse_on_left_border(self.parent._main_object_finder) and self.is_mouse_on_bottom_border(self.parent._main_object_finder):
                    self.__flag_mouse_is_on_left_bottom_corner = True
                    self.__flag_mouse_is_on_border = 0
                    mouse_on_border = True
                    #self.setCursor(QCursor(Qt.SizeBDiagCursor))
                    #QApplication.setOverrideCursor(Qt.SizeBDiagCursor)
                    
                elif self.is_mouse_on_left_border(self.parent._main_object_finder):
                    self.__flag_mouse_is_on_left_border = True
                    self.__flag_mouse_is_on_border = 0
                    mouse_on_border = True
                    #self.setCursor(QCursor(Qt.SizeHorCursor))
                    #QApplication.setOverrideCursor(Qt.SizeHorCursor)
                                        
                elif self.is_mouse_on_top_border(self.parent._main_object_finder):
                    self.__flag_mouse_is_on_top_border = True
                    self.__flag_mouse_is_on_border = 0
                    mouse_on_border = True
                    #self.setCursor(QCursor(Qt.SizeVerCursor))
                    #QApplication.setOverrideCursor(Qt.SizeVerCursor)
                    
                elif self.is_mouse_on_right_border(self.parent._main_object_finder):
                    self.__flag_mouse_is_on_right_border = True
                    self.__flag_mouse_is_on_border = 0
                    mouse_on_border = True
                    #self.setCursor(QCursor(Qt.SizeHorCursor))
                    #QApplication.setOverrideCursor(Qt.SizeHorCursor)

                    
                elif self.is_mouse_on_bottom_border(self.parent._main_object_finder):
                    self.__flag_mouse_is_on_bottom_border = True
                    self.__flag_mouse_is_on_border = 0
                    mouse_on_border = True
                    #self.setCursor(QCursor(Qt.SizeVerCursor))
                    #QApplication.setOverrideCursor(Qt.SizeVerCursor)
                    
                """

            elif self.__drag_border is True:
                pass #self.update_border()
            #elif self.__move_index is not None:
            #    self.update_position()
            
            self.draw_main_object_rect(qp)
            
            #if self.is_mouse_inside_rect(self.parent._main_object_finder):
            #    self.__flag_mouse_is_inside_rect = True
        
        rect_index = 0
        #self.__sub_template_color_index = 0
        cnt_sub = 1
        cnt_sub_text = 1
        for sub_object_finder in self.parent._sub_objects_finder:
        
            #print "__drag_border", self.__drag_border 
            #print "__move_index", self.__move_index
            #print "__capturing", self.__capturing
            #print "sub_object_finder show", sub_object_finder.show
        
            if self.__drag_border is False and self.__move_index is None and self.__capturing is False and sub_object_finder.show is True:
                                        
                if self.is_mouse_inside_rect(sub_object_finder):
                    self.__flag_mouse_is_inside_rect = cnt_sub
                    #self.setCursor(QCursor(Qt.SizeAllCursor))
                    
        
                elif self.is_mouse_on_left_border_roi(sub_object_finder) and self.is_mouse_on_top_border_roi(sub_object_finder):
                    self.__flag_mouse_is_on_left_up_corner_roi = True
                    self.__flag_mouse_is_on_border = cnt_sub
                    mouse_on_border = True
                    self.setCursor(QCursor(Qt.SizeFDiagCursor))
                    #self.setCursor(Qt.SizeFDiagCursor)
                    
                elif self.is_mouse_on_right_border_roi(sub_object_finder) and self.is_mouse_on_top_border_roi(sub_object_finder):
                    self.__flag_mouse_is_on_right_up_corner_roi = True
                    self.__flag_mouse_is_on_border = cnt_sub
                    mouse_on_border = True
                    self.setCursor(QCursor(Qt.SizeBDiagCursor))
                    #QApplication.setOverrideCursor(Qt.SizeBDiagCursor)
                    
                elif self.is_mouse_on_right_border_roi(sub_object_finder) and self.is_mouse_on_bottom_border_roi(sub_object_finder):
                    self.__flag_mouse_is_on_right_bottom_corner_roi = True
                    self.__flag_mouse_is_on_border = cnt_sub
                    mouse_on_border = True
                    self.setCursor(QCursor(Qt.SizeFDiagCursor))
                    #QApplication.setOverrideCursor(Qt.SizeFDiagCursor)
                    
                elif self.is_mouse_on_left_border_roi(sub_object_finder) and self.is_mouse_on_bottom_border_roi(sub_object_finder):
                    self.__flag_mouse_is_on_left_bottom_corner_roi = True
                    self.__flag_mouse_is_on_border = cnt_sub
                    mouse_on_border = True
                    self.setCursor(QCursor(Qt.SizeBDiagCursor))
                    #QApplication.setOverrideCursor(Qt.SizeBDiagCursor)
                    
                elif self.is_mouse_on_left_border_roi(sub_object_finder):
                    self.__flag_mouse_is_on_left_border_roi = True
                    self.__flag_mouse_is_on_border = cnt_sub
                    mouse_on_border = True
                    self.setCursor(QCursor(Qt.SizeHorCursor))
                    #QApplication.setOverrideCursor(Qt.SizeHorCursor)
                                        
                elif self.is_mouse_on_top_border_roi(sub_object_finder):
                    self.__flag_mouse_is_on_top_border_roi = True
                    self.__flag_mouse_is_on_border = cnt_sub
                    mouse_on_border = True
                    self.setCursor(QCursor(Qt.SizeVerCursor))
                    #QApplication.setOverrideCursor(Qt.SizeVerCursor)
                    
                elif self.is_mouse_on_right_border_roi(sub_object_finder):
                    self.__flag_mouse_is_on_right_border_roi = True
                    self.__flag_mouse_is_on_border = cnt_sub
                    mouse_on_border = True
                    self.setCursor(QCursor(Qt.SizeHorCursor))
                    #QApplication.setOverrideCursor(Qt.SizeHorCursor)

                    
                elif self.is_mouse_on_bottom_border_roi(sub_object_finder):
                    self.__flag_mouse_is_on_bottom_border_roi = True
                    self.__flag_mouse_is_on_border = cnt_sub
                    mouse_on_border = True
                    self.setCursor(QCursor(Qt.SizeVerCursor))

                """
                elif self.is_mouse_on_left_border(sub_object_finder) and self.is_mouse_on_top_border(sub_object_finder):
                    self.__flag_mouse_is_on_left_up_corner = True
                    self.__flag_mouse_is_on_border = cnt_sub
                    mouse_on_border = True
                    self.setCursor(QCursor(Qt.SizeFDiagCursor))
                    #self.setCursor(Qt.SizeFDiagCursor)
                    
                elif self.is_mouse_on_right_border(sub_object_finder) and self.is_mouse_on_top_border(sub_object_finder):
                    self.__flag_mouse_is_on_right_up_corner = True
                    self.__flag_mouse_is_on_border = cnt_sub
                    mouse_on_border = True
                    self.setCursor(QCursor(Qt.SizeBDiagCursor))
                    #QApplication.setOverrideCursor(Qt.SizeBDiagCursor)
  
                elif self.is_mouse_on_right_border(sub_object_finder) and self.is_mouse_on_bottom_border(sub_object_finder):
                    self.__flag_mouse_is_on_right_bottom_corner = True
                    self.__flag_mouse_is_on_border = cnt_sub
                    mouse_on_border = True
                    self.setCursor(QCursor(Qt.SizeFDiagCursor))
                    #QApplication.setOverrideCursor(Qt.SizeFDiagCursor)
                    
                elif self.is_mouse_on_left_border(sub_object_finder) and self.is_mouse_on_bottom_border(sub_object_finder):
                    self.__flag_mouse_is_on_left_bottom_corner = True
                    self.__flag_mouse_is_on_border = cnt_sub
                    mouse_on_border = True
                    self.setCursor(QCursor(Qt.SizeBDiagCursor))
                    #QApplication.setOverrideCursor(Qt.SizeBDiagCursor)
                    
                elif self.is_mouse_on_left_border(sub_object_finder):
                    self.__flag_mouse_is_on_left_border = True
                    self.__flag_mouse_is_on_border = cnt_sub
                    mouse_on_border = True
                    self.setCursor(QCursor(Qt.SizeHorCursor))
                    #QApplication.setOverrideCursor(Qt.SizeHorCursor)
                                        
                elif self.is_mouse_on_top_border(sub_object_finder):
                    self.__flag_mouse_is_on_top_border = True
                    self.__flag_mouse_is_on_border = cnt_sub
                    mouse_on_border = True
                    self.setCursor(QCursor(Qt.SizeVerCursor))
                    #QApplication.setOverrideCursor(Qt.SizeVerCursor)
                    
                elif self.is_mouse_on_right_border(sub_object_finder):
                    self.__flag_mouse_is_on_right_border = True
                    self.__flag_mouse_is_on_border = cnt_sub
                    mouse_on_border = True
                    self.setCursor(QCursor(Qt.SizeHorCursor))
                    #QApplication.setOverrideCursor(Qt.SizeHorCursor)

                    
                elif self.is_mouse_on_bottom_border(sub_object_finder):
                    self.__flag_mouse_is_on_bottom_border = True
                    self.__flag_mouse_is_on_border = cnt_sub
                    mouse_on_border = True
                    self.setCursor(QCursor(Qt.SizeVerCursor))
                    #QApplication.setOverrideCursor(Qt.SizeVerCursor)
                """    
                cnt_sub = cnt_sub + 1

            elif self.__drag_border is True:
                self.update_border()
            #elif self.__move_index is not None:
            #    self.update_position()
        
            self.draw_sub_templateangle(qp, sub_object_finder, cnt_sub_text)
            cnt_sub_text += 1
            
        if mouse_on_border is False:
            self.__flag_mouse_is_on_border = None
 
        if self.__flag_mouse_is_on_border is None and self.__flag_mouse_is_inside_rect is None and len(self.parent._sub_objects_finder) > 0:
            if self.__capturing is False:
                
                self.draw_cross_lines(qp)
            else:    
                self.draw_capturing_roi_lines(qp)
        elif self.__flag_mouse_is_inside_rect is not None and self.__flag_mouse_is_on_border is None:
            self.setCursor(QCursor(Qt.ArrowCursor))
        elif len(self.parent._sub_objects_finder) == 0:
            self.setCursor(QCursor(Qt.ArrowCursor))
        qp.end()   
        
        
    def calc_threshold_inside(self, rect):
    

        if rect.height > 16 * self.scaling_factor and rect.width > 16 * self.scaling_factor:
            return int((6 *self.scaling_factor))
        elif rect.height > 12 * self.scaling_factor and rect.width > 12 * self.scaling_factor:
            return int((4 *self.scaling_factor))
        elif rect.height > 8 * self.scaling_factor and rect.width > 8 * self.scaling_factor:
            return int((2 *self.scaling_factor))
        elif rect.height > 4 * self.scaling_factor and rect.width > 4 * self.scaling_factor:
            return int((1 *self.scaling_factor))
        else:
            return 0
       
    def is_mouse_inside_rect(self, rect):
    
        mouse_position = QPoint(QCursor.pos())
        
        threshold = self.calc_threshold_inside(rect)

        if (mouse_position.x() > rect.x and
                mouse_position.x() < rect.width + rect.x and
                mouse_position.y() > rect.y and
                mouse_position.y() < rect.height + rect.y):
            return True
        else:
            return False
        
        """
        if (mouse_position.x() > rect.x + threshold and
                mouse_position.x() < rect.width + rect.x - threshold and
                mouse_position.y() > rect.y + threshold and
                mouse_position.y() < rect.height + rect.y - threshold):
            return True
        else:
            return False
        """
        
    def update_position(self):
    
        rect = None
        
        if self.__move_index is None:
            return
        
        if self.__move_index == 0:
            rect = self.parent._main_object_finder
        else:
            rect = self.parent._sub_objects_finder[self.__move_index - 1]
    
        old_x = rect.x
        old_width = rect.width 
        old_y = rect.y
        old_height = rect.height 
        
        mouse_position = QPoint(QCursor.pos())
        #print mouse_position
        

        rect.x = mouse_position.x() - self.__position_offset_x 
        rect.y =  mouse_position.y() - self.__position_offset_y
        
        if  rect.x + rect.width > self._bg_pixmap.width():
            rect.x =  (self._bg_pixmap.width()-1) - rect.width
            
        if rect.x < 0:
            rect.x = 1
 
        if  rect.y + rect.height > self._bg_pixmap.height():
            rect.y = (self._bg_pixmap.height()-1) - rect.height
            
        if rect.y < 0:
            rect.y = 1 
            
        if self.__move_index != 0:
            if self.parent._main_object_finder.x + rect.roi_x + rect.roi_width > self._bg_pixmap.width():
                rect.roi_width = self._bg_pixmap.width() - (self.parent._main_object_finder.x + rect.roi_x)
                
            if self.parent._main_object_finder.y + rect.roi_y + rect.roi_height > self._bg_pixmap.height():
                rect.roi_height = self._bg_pixmap.height() - (self.parent._main_object_finder.y + rect.roi_y)
         
               
            if self.parent._main_object_finder.x + rect.roi_x < 0:
                old_roi_x = rect.roi_x
                rect.roi_x = -self.parent._main_object_finder.x
                
                width_diff = rect.roi_x - old_roi_x
                rect.roi_width = rect.roi_width - width_diff
                
            if self.parent._main_object_finder.y + rect.roi_y < 0:
                old_roi_y = rect.roi_y
                rect.roi_y = -self.parent._main_object_finder.y
                
                height_diff = rect.roi_y - old_roi_y
                rect.roi_height = rect.roi_height - height_diff
                
        
        x_offset =  old_x - rect.x
        y_offset =  old_y - rect.y

        if rect.x_offset is not None and rect.y_offset is not None:
            rect.y_offset = rect.y_offset + y_offset
            rect.x_offset = rect.x_offset + x_offset
            
        if self.__move_index == 0:
            for sub_image_finder in self.parent._sub_objects_finder:
                sub_image_finder.roi_x = sub_image_finder.roi_x + x_offset
                sub_image_finder.roi_y = sub_image_finder.roi_y + y_offset
        else:
            rect.roi_x = rect.roi_x - x_offset
            rect.roi_y = rect.roi_y - y_offset
            


    def calc_threshold_border(self, rect):
        if rect.roi_height > 16 * self.scaling_factor and rect.roi_width > 16 * self.scaling_factor:
            return int((8 *self.scaling_factor))
        elif rect.roi_height > 12 * self.scaling_factor and rect.roi_width > 12 * self.scaling_factor:
            return int((6 *self.scaling_factor))
        elif rect.roi_height > 8 * self.scaling_factor and rect.roi_width > 8 * self.scaling_factor:
            return int((4 *self.scaling_factor))
        elif rect.roi_height > 4 * self.scaling_factor and rect.roi_width > 4 * self.scaling_factor:
            return int((2 *self.scaling_factor))
        else:
            return int(self.scaling_factor)
            
        
        
            
    def update_border(self):
    
        rect = None
        
        if self.__border_index is None:
            return
        
        if self.__border_index == 0:
            rect = self.parent._main_object_finder
        else:
            rect = self.parent._sub_objects_finder[self.__border_index - 1]
            
            
            
            
            
            
            
            
            
        if  self.__flag_mouse_is_on_left_up_corner_roi is True:
            
            mouse_position = QPoint(QCursor.pos())
        
            old_x = rect.roi_x
            old_width = rect.roi_width 
            
            
            rect.roi_x = mouse_position.x() - self.parent._main_object_finder.x
            rect.roi_width = self._old_roi_width_rect + ((self._old_roi_x_rect + self.parent._main_object_finder.x) - mouse_position.x()) #rect.roi_width + (rect.roi_x + self.parent._main_object_finder.x - mouse_position.x())

            
            
            if rect.x < rect.roi_x + self.parent._main_object_finder.x:
                rect.roi_x = rect.x - self.parent._main_object_finder.x - 1 #rect.roi_x +  self.parent._main_object_finder.x
                rect.roi_width = self._old_roi_width_rect - (rect.x - (self._old_roi_x_rect + self.parent._main_object_finder.x))
                
                
             
                    
            old_y = rect.roi_y
            old_height = rect.roi_height 
            
            
            rect.roi_y = mouse_position.y() - self.parent._main_object_finder.y
            rect.roi_height = self._old_roi_height_rect + ((self._old_roi_y_rect + self.parent._main_object_finder.y) - mouse_position.y()) #rect.roi_height + (rect.roi_y + self.parent._main_object_finder.y - mouse_position.y())

            
            
            if rect.y < rect.roi_y + self.parent._main_object_finder.y:
                rect.roi_y = rect.y - self.parent._main_object_finder.y -1#rect.roi_y +  self.parent._main_object_finder.y
                rect.roi_height = self._old_roi_height_rect - (rect.y - (self._old_roi_y_rect + self.parent._main_object_finder.y))
                
                
                
        elif  self.__flag_mouse_is_on_right_up_corner_roi == True:
        
            mouse_position = QPoint(QCursor.pos())

            mouse_position = QPoint(QCursor.pos())

            old_width = rect.roi_width 
            
            #rect.width = mouse_position.x() - rect.x
            
            rect.roi_width = mouse_position.x() - (rect.roi_x + self.parent._main_object_finder.x)
            #rect.roi_width = self._old_roi_width_rect + ((self._old_roi_x_rect + self.parent._main_object_finder.x) - mouse_position.x()) #rect.roi_width + (rect.roi_x + self.parent._main_object_finder.x - mouse_position.x())


            if rect.x + rect.width > rect.roi_x + self.parent._main_object_finder.x + rect.roi_width:
                #rect.y = old_y #rect.roi_x +  self.parent._main_object_finder.x
                rect.roi_width = (rect.x - (self._old_roi_x_rect + self.parent._main_object_finder.x)) + rect.width + 1
               
            old_y = rect.roi_y
            old_height = rect.roi_height 
            
            
            rect.roi_y = mouse_position.y() - self.parent._main_object_finder.y
            rect.roi_height = self._old_roi_height_rect + ((self._old_roi_y_rect + self.parent._main_object_finder.y) - mouse_position.y()) #rect.roi_height + (rect.roi_y + self.parent._main_object_finder.y - mouse_position.y())

            
            
            if rect.y < rect.roi_y + self.parent._main_object_finder.y:
                rect.roi_y = rect.y - self.parent._main_object_finder.y -1#rect.roi_y +  self.parent._main_object_finder.y
                rect.roi_height = self._old_roi_height_rect - (rect.y - (self._old_roi_y_rect + self.parent._main_object_finder.y))
                
                
        elif  self.__flag_mouse_is_on_right_bottom_corner_roi == True:
        
            mouse_position = QPoint(QCursor.pos())

            
            old_width = rect.roi_width 
            
            #rect.width = mouse_position.x() - rect.x
            
            rect.roi_width = mouse_position.x() - (rect.roi_x + self.parent._main_object_finder.x)
            #rect.roi_width = self._old_roi_width_rect + ((self._old_roi_x_rect + self.parent._main_object_finder.x) - mouse_position.x()) #rect.roi_width + (rect.roi_x + self.parent._main_object_finder.x - mouse_position.x())


            if rect.x + rect.width > rect.roi_x + self.parent._main_object_finder.x + rect.roi_width:
                #rect.y = old_y #rect.roi_x +  self.parent._main_object_finder.x
                rect.roi_width = (rect.x - (self._old_roi_x_rect + self.parent._main_object_finder.x)) + rect.width + 1
            
            old_height = rect.roi_height 
            
            #rect.height = mouse_position.y() - rect.y
            
            rect.roi_height = mouse_position.y() - (rect.roi_y + self.parent._main_object_finder.y)
            #rect.roi_height = self._old_roi_height_rect + ((self._old_roi_y_rect + self.parent._main_object_finder.y) - mouse_position.y()) #rect.roi_height + (rect.roi_y + self.parent._main_object_finder.y - mouse_position.y())


            if rect.y + rect.height > rect.roi_y + self.parent._main_object_finder.y + rect.roi_height:
                #rect.y = old_y #rect.roi_y +  self.parent._main_object_finder.y
                rect.roi_height = (rect.y - (self._old_roi_y_rect + self.parent._main_object_finder.y)) + rect.height + 1
            
                
                
        elif  self.__flag_mouse_is_on_left_bottom_corner_roi == True:
            mouse_position = QPoint(QCursor.pos())

            old_x = rect.roi_x
            old_width = rect.roi_width 
            
            
            rect.roi_x = mouse_position.x() - self.parent._main_object_finder.x
            rect.roi_width = self._old_roi_width_rect + ((self._old_roi_x_rect + self.parent._main_object_finder.x) - mouse_position.x()) #rect.roi_width + (rect.roi_x + self.parent._main_object_finder.x - mouse_position.x())

            
            
            if rect.x < rect.roi_x + self.parent._main_object_finder.x:
                rect.roi_x = rect.x - self.parent._main_object_finder.x - 1 #rect.roi_x +  self.parent._main_object_finder.x
                rect.roi_width = self._old_roi_width_rect - (rect.x - (self._old_roi_x_rect + self.parent._main_object_finder.x))
                
                    
                
            old_height = rect.roi_height 
            
            #rect.height = mouse_position.y() - rect.y
            
            rect.roi_height = mouse_position.y() - (rect.roi_y + self.parent._main_object_finder.y)
            #rect.roi_height = self._old_roi_height_rect + ((self._old_roi_y_rect + self.parent._main_object_finder.y) - mouse_position.y()) #rect.roi_height + (rect.roi_y + self.parent._main_object_finder.y - mouse_position.y())


            if rect.y + rect.height > rect.roi_y + self.parent._main_object_finder.y + rect.roi_height:
                #rect.y = old_y #rect.roi_y +  self.parent._main_object_finder.y
                rect.roi_height = (rect.y - (self._old_roi_y_rect + self.parent._main_object_finder.y)) + rect.height + 1
            
            
        
        elif self.__flag_mouse_is_on_left_border_roi is True:
        
            mouse_position = QPoint(QCursor.pos())

            old_x = rect.roi_x
            old_width = rect.roi_width 
            
            
            rect.roi_x = mouse_position.x() - self.parent._main_object_finder.x
            rect.roi_width = self._old_roi_width_rect + ((self._old_roi_x_rect + self.parent._main_object_finder.x) - mouse_position.x()) #rect.roi_width + (rect.roi_x + self.parent._main_object_finder.x - mouse_position.x())

            
            
            if rect.x < rect.roi_x + self.parent._main_object_finder.x:
                rect.roi_x = rect.x - self.parent._main_object_finder.x - 1 #rect.roi_x +  self.parent._main_object_finder.x
                rect.roi_width = self._old_roi_width_rect - (rect.x - (self._old_roi_x_rect + self.parent._main_object_finder.x))
                
            """
            if rect.roi_width < int(4 * self.scaling_factor):
                rect.roi_width = old_width
                rect.roi_x = old_x
            """    
        elif self.__flag_mouse_is_on_top_border_roi is True:
        
            mouse_position = QPoint(QCursor.pos())

            old_y = rect.roi_y
            old_height = rect.roi_height 
            
            
            rect.roi_y = mouse_position.y() - self.parent._main_object_finder.y
            rect.roi_height = self._old_roi_height_rect + ((self._old_roi_y_rect + self.parent._main_object_finder.y) - mouse_position.y()) #rect.roi_height + (rect.roi_y + self.parent._main_object_finder.y - mouse_position.y())

            
            
            if rect.y < rect.roi_y + self.parent._main_object_finder.y:
                rect.roi_y = rect.y - self.parent._main_object_finder.y -1#rect.roi_y +  self.parent._main_object_finder.y
                rect.roi_height = self._old_roi_height_rect - (rect.y - (self._old_roi_y_rect + self.parent._main_object_finder.y))
                
        elif self.__flag_mouse_is_on_bottom_border_roi is True:
        
            mouse_position = QPoint(QCursor.pos())

            old_height = rect.roi_height 
            
            #rect.height = mouse_position.y() - rect.y
            
            rect.roi_height = mouse_position.y() - (rect.roi_y + self.parent._main_object_finder.y)
            #rect.roi_height = self._old_roi_height_rect + ((self._old_roi_y_rect + self.parent._main_object_finder.y) - mouse_position.y()) #rect.roi_height + (rect.roi_y + self.parent._main_object_finder.y - mouse_position.y())


            if rect.y + rect.height > rect.roi_y + self.parent._main_object_finder.y + rect.roi_height:
                #rect.y = old_y #rect.roi_y +  self.parent._main_object_finder.y
                rect.roi_height = (rect.y - (self._old_roi_y_rect + self.parent._main_object_finder.y)) + rect.height + 1
            
                

            #print rect.x
        elif self.__flag_mouse_is_on_right_border_roi is True:
        
            mouse_position = QPoint(QCursor.pos())

            old_width = rect.roi_width 
            
            #rect.width = mouse_position.x() - rect.x
            
            rect.roi_width = mouse_position.x() - (rect.roi_x + self.parent._main_object_finder.x)
            #rect.roi_width = self._old_roi_width_rect + ((self._old_roi_x_rect + self.parent._main_object_finder.x) - mouse_position.x()) #rect.roi_width + (rect.roi_x + self.parent._main_object_finder.x - mouse_position.x())


            if rect.x + rect.width > rect.roi_x + self.parent._main_object_finder.x + rect.roi_width:
                #rect.y = old_y #rect.roi_x +  self.parent._main_object_finder.x
                rect.roi_width = (rect.x - (self._old_roi_x_rect + self.parent._main_object_finder.x)) + rect.width + 1


        elif  self.__flag_mouse_is_on_left_up_corner is True:
            
            mouse_position = QPoint(QCursor.pos())
        
            old_x = rect.x

                                    
            rect.x = mouse_position.x()
            rect.width = self._old_width_rect + (self._old_x_rect - mouse_position.x()) 
            
      
            
            if rect.x < 1:
                rect.x = 1
            
            if self.__border_index != 0:
                if  mouse_position.x() < (rect.roi_x +  self.parent._main_object_finder.x):
                
                    if rect.roi_unlimited_left:
                        rect.roi_width = rect.roi_width + ((rect.roi_x + self.parent._main_object_finder.x) - rect.x)
                        rect.roi_x = rect.roi_x - ((rect.roi_x + self.parent._main_object_finder.x) - rect.x)
                    else:
                        rect.x = rect.roi_x +  self.parent._main_object_finder.x + 1
                        rect.width = self._old_width_rect + (self._old_x_rect - (rect.roi_x +  self.parent._main_object_finder.x)) 
                        
                        #rect.roi_width = rect.roi_width + ((rect.roi_x + self.parent._main_object_finder.x) - rect.x)
                        #rect.roi_x = rect.roi_x - ((rect.roi_x + self.parent._main_object_finder.x) - rect.x)
                        
            
            if rect.width < int(4 * self.scaling_factor):
                rect.width = int(4 * self.scaling_factor)
                rect.x = self._old_x_rect + self._old_width_rect - int(4 * self.scaling_factor)
                 
            x_offset =  old_x - rect.x

                                    
            if rect.x_offset is not None and rect.y_offset is not None:
                rect.x_offset = rect.x_offset + x_offset
            
            #print x_offset
                        
            if self.__border_index == 0:
                for sub_image_finder in self.parent._sub_objects_finder:
                    sub_image_finder.roi_x = sub_image_finder.roi_x + x_offset
                    
            old_y = rect.y
            
            rect.y = mouse_position.y()
            rect.height = self._old_height_rect + (self._old_y_rect - mouse_position.y()) 
            
            if rect.y < 1:
                rect.y = 1
                
            if self.__border_index != 0:
                if  mouse_position.y() < (rect.roi_y +  self.parent._main_object_finder.y):
            
                    if rect.roi_unlimited_up:
                        rect.roi_height = rect.roi_height + ((rect.roi_y + self.parent._main_object_finder.y) - rect.y)
                        rect.roi_y = rect.roi_y - ((rect.roi_y + self.parent._main_object_finder.y) - rect.y)
                    else:
                        rect.y = rect.roi_y +  self.parent._main_object_finder.y + 1
                        rect.height = self._old_height_rect + (self._old_y_rect - (rect.roi_y +  self.parent._main_object_finder.y)) 
                        
                        #rect.roi_height = rect.roi_height + ((rect.roi_y + self.parent._main_object_finder.y) - rect.y)
                        #rect.roi_y = rect.roi_y - ((rect.roi_y + self.parent._main_object_finder.y) - rect.y)

            
            if rect.height < int(4 * self.scaling_factor):
                rect.height = int(4 * self.scaling_factor)
                rect.y = self._old_y_rect + self._old_height_rect - int(4 * self.scaling_factor)
                
                 
            y_offset =  old_y - rect.y
            
            if rect.x_offset is not None and rect.y_offset is not None:
                rect.y_offset = rect.y_offset + y_offset
                
            #print x_offset
            if self.__border_index == 0:
                for sub_image_finder in self.parent._sub_objects_finder:
                    sub_image_finder.roi_y = sub_image_finder.roi_y + y_offset
                
        elif  self.__flag_mouse_is_on_right_up_corner == True:
        
            mouse_position = QPoint(QCursor.pos())

            old_width = rect.width 
            
            rect.width = mouse_position.x() - rect.x
            
            if rect.x + rect.width > self._bg_pixmap.width() + 1:
                rect.width = self._bg_pixmap.width() - rect.x - 1
            
            
            if self.__border_index != 0:
                if  rect.x + rect.width > rect.roi_x + self.parent._main_object_finder.x + rect.roi_width:
                
                    if rect.roi_unlimited_right:
                        rect.roi_width = rect.roi_width + ((rect.x + rect.width) - (rect.roi_x + self.parent._main_object_finder.x + rect.roi_width))
                        #rect.roi_x = rect.roi_x - ((rect.roi_x + self.parent._main_object_finder.x) - rect.x)
                    else:
                        # -- rect.x = rect.roi_x +  self.parent._main_object_finder.x
                        rect.width = self._old_width_rect + ((rect.roi_x + rect.roi_width + self.parent._main_object_finder.x) - (self._old_x_rect + self._old_width_rect)) - 1

                        #rect.roi_width = rect.roi_width + ((rect.x + rect.width) - (rect.roi_x + self.parent._main_object_finder.x + rect.roi_width))
                        

            
            if rect.width < int(4 * self.scaling_factor):
                rect.width = int(4 * self.scaling_factor)
                #rect.x = self._old_x_rect + self._old_width_rect + 4
                
                 
            old_y = rect.y
            
            rect.y = mouse_position.y()
            rect.height = self._old_height_rect + (self._old_y_rect - mouse_position.y()) 
            
            if rect.y < 1:
                rect.y = 1
                
            if self.__border_index != 0:
                if  mouse_position.y() < (rect.roi_y +  self.parent._main_object_finder.y):
            
                    if rect.roi_unlimited_up:
                        rect.roi_height = rect.roi_height + ((rect.roi_y + self.parent._main_object_finder.y) - rect.y)
                        rect.roi_y = rect.roi_y - ((rect.roi_y + self.parent._main_object_finder.y) - rect.y)
                    else:
                        rect.y = rect.roi_y +  self.parent._main_object_finder.y + 1
                        rect.height = self._old_height_rect + (self._old_y_rect - (rect.roi_y +  self.parent._main_object_finder.y)) 
                        
                        #rect.roi_height = rect.roi_height + ((rect.roi_y + self.parent._main_object_finder.y) - rect.y)
                        #rect.roi_y = rect.roi_y - ((rect.roi_y + self.parent._main_object_finder.y) - rect.y)

            
            if rect.height < int(4 * self.scaling_factor):
                rect.height = int(4 * self.scaling_factor)
                rect.y = self._old_y_rect + self._old_height_rect - int(4 * self.scaling_factor)
                
                 
            y_offset =  old_y - rect.y
            
            if rect.x_offset is not None and rect.y_offset is not None:
                rect.y_offset = rect.y_offset + y_offset
                
            #print x_offset
            if self.__border_index == 0:
                for sub_image_finder in self.parent._sub_objects_finder:
                    sub_image_finder.roi_y = sub_image_finder.roi_y + y_offset
                
        elif  self.__flag_mouse_is_on_right_bottom_corner == True:
        
            mouse_position = QPoint(QCursor.pos())

            old_width = rect.width 
            
            rect.width = mouse_position.x() - rect.x
            
            if rect.x + rect.width > self._bg_pixmap.width() + 1:
                rect.width = self._bg_pixmap.width() - rect.x - 1
            
            
            if self.__border_index != 0:
                if  rect.x + rect.width > rect.roi_x + self.parent._main_object_finder.x + rect.roi_width:
                
                    if rect.roi_unlimited_right:
                        rect.roi_width = rect.roi_width + ((rect.x + rect.width) - (rect.roi_x + self.parent._main_object_finder.x + rect.roi_width))
                        #rect.roi_x = rect.roi_x - ((rect.roi_x + self.parent._main_object_finder.x) - rect.x)
                    else:
                        # -- rect.x = rect.roi_x +  self.parent._main_object_finder.x
                        rect.width = self._old_width_rect + ((rect.roi_x + rect.roi_width + self.parent._main_object_finder.x) - (self._old_x_rect + self._old_width_rect)) -1 

                        #rect.roi_width = rect.roi_width + ((rect.x + rect.width) - (rect.roi_x + self.parent._main_object_finder.x + rect.roi_width))
                        #rect.roi_x = rect.roi_x - ((rect.roi_x + self.parent._main_object_finder.x) - rect.x)


            
            if rect.width < int(4 * self.scaling_factor):
                rect.width = int(4 * self.scaling_factor)
                #rect.x = self._old_x_rect + self._old_width_rect + 4

            old_height = rect.height 
            
            rect.height = mouse_position.y() - rect.y
       
            if rect.y + rect.height > self._bg_pixmap.height() + 1:
                rect.height = self._bg_pixmap.height() - rect.y - 1
            
            
            if self.__border_index != 0:
                if  rect.y + rect.height > rect.roi_y + self.parent._main_object_finder.y + rect.roi_height:
                
                    if rect.roi_unlimited_down:
                        rect.roi_height = rect.roi_height + ((rect.y + rect.height) - (rect.roi_y + self.parent._main_object_finder.y + rect.roi_height))
                        #rect.roi_y = rect.roi_y - ((rect.roi_y + self.parent._main_object_finder.y) - rect.y)
                    else:
                        # -- rect.y = rect.roi_y +  self.parent._main_object_finder.y
                        rect.height = self._old_height_rect + ((rect.roi_y + rect.roi_height + self.parent._main_object_finder.y) - (self._old_y_rect + self._old_height_rect)) -1

                        #rect.roi_height = rect.roi_height + ((rect.y + rect.height) - (rect.roi_y + self.parent._main_object_finder.y + rect.roi_height))
                        #rect.roi_y = rect.roi_y - ((rect.roi_y + self.parent._main_object_finder.y) - rect.y)

            
            if rect.height < int(4 * self.scaling_factor):
                rect.height = int(4 * self.scaling_factor)
                #rect.y = self._old_y_rect + self._old_height_rect + 4
                
        elif  self.__flag_mouse_is_on_left_bottom_corner == True:
            mouse_position = QPoint(QCursor.pos())

            mouse_position = QPoint(QCursor.pos())

            old_x = rect.x
            
            #rect.width = rect.width + (rect.x - mouse_position.x())
            #rect.x = mouse_position.x()

                                    
            rect.x = mouse_position.x()
            rect.width = self._old_width_rect + (self._old_x_rect - mouse_position.x()) 
          
            
            if rect.x < 1:
                rect.x = 1
            
            if self.__border_index != 0:
                if  mouse_position.x() < (rect.roi_x +  self.parent._main_object_finder.x):
                
                    if rect.roi_unlimited_left:
                        rect.roi_width = rect.roi_width + ((rect.roi_x + self.parent._main_object_finder.x) - rect.x)
                        rect.roi_x = rect.roi_x - ((rect.roi_x + self.parent._main_object_finder.x) - rect.x)
                    else:
                        rect.x = rect.roi_x +  self.parent._main_object_finder.x + 1
                        rect.width = self._old_width_rect + (self._old_x_rect - (rect.roi_x +  self.parent._main_object_finder.x)) 
                        
                        #rect.roi_width = rect.roi_width + ((rect.roi_x + self.parent._main_object_finder.x) - rect.x)
                        #rect.roi_x = rect.roi_x - ((rect.roi_x + self.parent._main_object_finder.x) - rect.x)
                        
            
            if rect.width < int(4 * self.scaling_factor):
                rect.width = int(4 * self.scaling_factor)
                rect.x = self._old_x_rect + self._old_width_rect - int(4 * self.scaling_factor)
                 
            x_offset =  old_x - rect.x

                                    
            if rect.x_offset is not None and rect.y_offset is not None:
                rect.x_offset = rect.x_offset + x_offset
            
            #print x_offset
                        
            if self.__border_index == 0:
                for sub_image_finder in self.parent._sub_objects_finder:
                    sub_image_finder.roi_x = sub_image_finder.roi_x + x_offset
                    
                
            old_height = rect.height 
            
            rect.height = mouse_position.y() - rect.y
       
            if rect.y + rect.height > self._bg_pixmap.height() + 1:
                rect.height = self._bg_pixmap.height() - rect.y - 1
            
            
            if self.__border_index != 0:
                if  rect.y + rect.height > rect.roi_y + self.parent._main_object_finder.y + rect.roi_height:
                
                    if rect.roi_unlimited_down:
                        rect.roi_height = rect.roi_height + ((rect.y + rect.height) - (rect.roi_y + self.parent._main_object_finder.y + rect.roi_height))
                        #rect.roi_y = rect.roi_y - ((rect.roi_y + self.parent._main_object_finder.y) - rect.y)
                    else:
                        # -- rect.y = rect.roi_y +  self.parent._main_object_finder.y
                        rect.height = self._old_height_rect + ((rect.roi_y + rect.roi_height + self.parent._main_object_finder.y) - (self._old_y_rect + self._old_height_rect)) -1

                        #rect.roi_height = rect.roi_height + ((rect.y + rect.height) - (rect.roi_y + self.parent._main_object_finder.y + rect.roi_height))
                        #rect.roi_y = rect.roi_y - ((rect.roi_y + self.parent._main_object_finder.y) - rect.y)

            
            if rect.height < int(4 * self.scaling_factor):
                rect.height = int(4 * self.scaling_factor)
                #rect.y = self._old_y_rect + self._old_height_rect + 4
        
        elif self.__flag_mouse_is_on_left_border is True:
        
            mouse_position = QPoint(QCursor.pos())

            old_x = rect.x
            
            #rect.width = rect.width + (rect.x - mouse_position.x())
            #rect.x = mouse_position.x()

                                    
            rect.x = mouse_position.x()
            rect.width = self._old_width_rect + (self._old_x_rect - mouse_position.x()) 
            
            """
                            
            if self.__border_index != 0:
                
                if rect.roi_unlimited_left:
                    if  mouse_position.x() < rect.roi_x +  self.parent._main_object_finder.x:
                        rect.roi_width = rect.roi_width + ((rect.roi_x + self.parent._main_object_finder.x) - rect.x)
                        rect.roi_x = rect.roi_x - ((rect.roi_x + self.parent._main_object_finder.x) - rect.x)
                else:
                    if  mouse_position.x() < (rect.roi_x +  self.parent._main_object_finder.x):

                        rect.x = rect.roi_x +  self.parent._main_object_finder.x
                        rect.width = ((rect.roi_x + self.parent._main_object_finder.x) - rect.x)
                        
                        #rect.roi_width = rect.roi_width + ((rect.roi_x + self.parent._main_object_finder.x) - rect.x)
                        #rect.roi_x = rect.roi_x - ((rect.roi_x + self.parent._main_object_finder.x) - rect.x)
            """
            
            if rect.x < 1:
                rect.x = 1
            
            if self.__border_index != 0:
                if  mouse_position.x() < (rect.roi_x +  self.parent._main_object_finder.x):
                
                    if rect.roi_unlimited_left:
                        rect.roi_width = rect.roi_width + ((rect.roi_x + self.parent._main_object_finder.x) - rect.x)
                        rect.roi_x = rect.roi_x - ((rect.roi_x + self.parent._main_object_finder.x) - rect.x)
                    else:
                        rect.x = rect.roi_x +  self.parent._main_object_finder.x + 1
                        rect.width = self._old_width_rect + (self._old_x_rect - (rect.roi_x +  self.parent._main_object_finder.x)) 
                        
                        #rect.roi_width = rect.roi_width + ((rect.roi_x + self.parent._main_object_finder.x) - rect.x)
                        #rect.roi_x = rect.roi_x - ((rect.roi_x + self.parent._main_object_finder.x) - rect.x)
                        
            
            if rect.width < int(4 * self.scaling_factor):
                rect.width = int(4 * self.scaling_factor)
                rect.x = self._old_x_rect + self._old_width_rect - int(4 * self.scaling_factor)
                 
            x_offset =  old_x - rect.x

                                    
            if rect.x_offset is not None and rect.y_offset is not None:
                rect.x_offset = rect.x_offset + x_offset
            
            #print x_offset
                        
            if self.__border_index == 0:
                for sub_image_finder in self.parent._sub_objects_finder:
                    sub_image_finder.roi_x = sub_image_finder.roi_x + x_offset
                
        elif self.__flag_mouse_is_on_top_border is True:
        
            mouse_position = QPoint(QCursor.pos())

            old_y = rect.y
            
            rect.y = mouse_position.y()
            rect.height = self._old_height_rect + (self._old_y_rect - mouse_position.y()) 
            
            if rect.y < 1:
                rect.y = 1
                
            if self.__border_index != 0:
                if  mouse_position.y() < (rect.roi_y +  self.parent._main_object_finder.y):
            
                    if rect.roi_unlimited_up:
                        rect.roi_height = rect.roi_height + ((rect.roi_y + self.parent._main_object_finder.y) - rect.y)
                        rect.roi_y = rect.roi_y - ((rect.roi_y + self.parent._main_object_finder.y) - rect.y)
                    else:
                        rect.y = rect.roi_y +  self.parent._main_object_finder.y + 1
                        rect.height = self._old_height_rect + (self._old_y_rect - (rect.roi_y +  self.parent._main_object_finder.y)) 
                        
                        #rect.roi_height = rect.roi_height + ((rect.roi_y + self.parent._main_object_finder.y) - rect.y)
                        #rect.roi_y = rect.roi_y - ((rect.roi_y + self.parent._main_object_finder.y) - rect.y)

            
            if rect.height < int(4 * self.scaling_factor):
                rect.height = int(4 * self.scaling_factor)
                rect.y = self._old_y_rect + self._old_height_rect - int(4 * self.scaling_factor)
                
                 
            y_offset =  old_y - rect.y
            
            if rect.x_offset is not None and rect.y_offset is not None:
                rect.y_offset = rect.y_offset + y_offset
                
            #print x_offset
            if self.__border_index == 0:
                for sub_image_finder in self.parent._sub_objects_finder:
                    sub_image_finder.roi_y = sub_image_finder.roi_y + y_offset
                
        elif self.__flag_mouse_is_on_bottom_border is True:
        
            mouse_position = QPoint(QCursor.pos())

            old_height = rect.height 
            
            rect.height = mouse_position.y() - rect.y
       
            if rect.y + rect.height > self._bg_pixmap.height() + 1:
                rect.height = self._bg_pixmap.height() - rect.y - 1
            
            
            if self.__border_index != 0:
                if  rect.y + rect.height > rect.roi_y + self.parent._main_object_finder.y + rect.roi_height:
                
                    if rect.roi_unlimited_down:
                        rect.roi_height = rect.roi_height + ((rect.y + rect.height) - (rect.roi_y + self.parent._main_object_finder.y + rect.roi_height))
                        #rect.roi_y = rect.roi_y - ((rect.roi_y + self.parent._main_object_finder.y) - rect.y)
                    else:
                        # -- rect.y = rect.roi_y +  self.parent._main_object_finder.y
                        rect.height = self._old_height_rect + ((rect.roi_y + rect.roi_height + self.parent._main_object_finder.y) - (self._old_y_rect + self._old_height_rect)) -1

                        #rect.roi_height = rect.roi_height + ((rect.y + rect.height) - (rect.roi_y + self.parent._main_object_finder.y + rect.roi_height))
                        #rect.roi_y = rect.roi_y - ((rect.roi_y + self.parent._main_object_finder.y) - rect.y)

            
            if rect.height < int(4 * self.scaling_factor):
                rect.height = int(4 * self.scaling_factor)
                #rect.y = self._old_y_rect + self._old_height_rect + 4
                

            #print rect.x
        elif self.__flag_mouse_is_on_right_border is True:
        
            mouse_position = QPoint(QCursor.pos())

            old_width = rect.width 
            
            rect.width = mouse_position.x() - rect.x
            
            if rect.x + rect.width > self._bg_pixmap.width() + 1:
                rect.width = self._bg_pixmap.width() - rect.x - 1
            
            
            if self.__border_index != 0:
                if  rect.x + rect.width > rect.roi_x + self.parent._main_object_finder.x + rect.roi_width:
                
                    if rect.roi_unlimited_right:
                        rect.roi_width = rect.roi_width + ((rect.x + rect.width) - (rect.roi_x + self.parent._main_object_finder.x + rect.roi_width))
                        #rect.roi_x = rect.roi_x - ((rect.roi_x + self.parent._main_object_finder.x) - rect.x)
                    else:
                        # -- rect.x = rect.roi_x +  self.parent._main_object_finder.x
                        rect.width = self._old_width_rect + ((rect.roi_x + rect.roi_width + self.parent._main_object_finder.x) - (self._old_x_rect + self._old_width_rect)) -1

                        #rect.roi_width = rect.roi_width + ((rect.x + rect.width) - (rect.roi_x + self.parent._main_object_finder.x + rect.roi_width))
                        #rect.roi_x = rect.roi_x - ((rect.roi_x + self.parent._main_object_finder.x) - rect.x)


            
            if rect.width < int(4 * self.scaling_factor):
                rect.width = int(4 * self.scaling_factor)
                #rect.x = self._old_x_rect + self._old_width_rect + 4


        
     
    def is_mouse_on_left_border(self, rect):
        mouse_position = QPoint(QCursor.pos())
        
        if (mouse_position.x() > rect.x - int((8 *self.scaling_factor)) and
                mouse_position.x() < rect.x + int((8 *self.scaling_factor)) and
                mouse_position.y() > rect.y and
                mouse_position.y() < rect.height + rect.y):
            return True
        else:
            return False
            
    def is_mouse_on_left_border_roi(self, rect):
    
        threshold = self.calc_threshold_border(rect)
    
        if rect.x == 0 and rect.width == 0 and rect.y == 0 and rect.height == 0:
            return False
        mouse_position = QPoint(QCursor.pos())
        
        if (rect.roi_unlimited_left is True ):
            return False
        elif (mouse_position.x() > rect.roi_x + self.parent._main_object_finder.x - threshold and
                mouse_position.x() < rect.roi_x + self.parent._main_object_finder.x + threshold and
                mouse_position.y() > rect.roi_y + self.parent._main_object_finder.y - threshold and
                mouse_position.y() < rect.roi_height + rect.roi_y + self.parent._main_object_finder.y + threshold):
            return True
        elif ((rect.roi_unlimited_up is True or rect.roi_unlimited_down is True) and
                mouse_position.x() > rect.roi_x + self.parent._main_object_finder.x - threshold and
                mouse_position.x() < rect.roi_x + self.parent._main_object_finder.x + threshold): #and
                #mouse_position.y() > rect.roi_y + self.parent._main_object_finder.y - int((8 *self.scaling_factor)) and
                #mouse_position.y() < rect.roi_y + self.parent._main_object_finder.y + int((8 *self.scaling_factor))):
            return True
        else:
            return False
            
    def is_mouse_on_right_border(self, rect):
        mouse_position = QPoint(QCursor.pos())
        
        if (mouse_position.x() > rect.x + rect.width - int((8 *self.scaling_factor)) and
                mouse_position.x() < rect.x + rect.width + int((8 *self.scaling_factor)) and
                mouse_position.y() > rect.y and
                mouse_position.y() < rect.height + rect.y):
            return True
        else:
            return False
            
    def is_mouse_on_right_border_roi(self, rect):
        if rect.x == 0 and rect.width == 0 and rect.y == 0 and rect.height == 0:
            return False
            
        mouse_position = QPoint(QCursor.pos())
        
        threshold = self.calc_threshold_border(rect)
        
        if (rect.roi_unlimited_right is True ):
            return False
        elif (mouse_position.x() > rect.roi_x + self.parent._main_object_finder.x + rect.roi_width - threshold and
                mouse_position.x() < rect.roi_x + self.parent._main_object_finder.x + rect.roi_width + threshold and
                mouse_position.y() > rect.roi_y + self.parent._main_object_finder.y - threshold and
                mouse_position.y() < rect.roi_height + rect.roi_y + self.parent._main_object_finder.y + threshold):
            return True
        elif ((rect.roi_unlimited_up is True or rect.roi_unlimited_down is True) and
                mouse_position.x() > rect.roi_x + self.parent._main_object_finder.x + rect.roi_width - threshold and
                mouse_position.x() < rect.roi_x + self.parent._main_object_finder.x + rect.roi_width + threshold):
            return True
        else:
            return False
            
    def is_mouse_on_top_border(self, rect):
        mouse_position = QPoint(QCursor.pos())
        
        if (mouse_position.x() > rect.x and
                mouse_position.x() < rect.x + rect.width and
                mouse_position.y() > rect.y - int((8 *self.scaling_factor)) and
                mouse_position.y() < rect.y + int((8 *self.scaling_factor))):
            return True
        else:
            return False
            
    def is_mouse_on_top_border_roi(self, rect):
        if rect.x == 0 and rect.width == 0 and rect.y == 0 and rect.height == 0:
            return False
            
        mouse_position = QPoint(QCursor.pos())
        
        threshold = self.calc_threshold_border(rect)
        
        if (rect.roi_unlimited_up is True ):
            return False
        elif (mouse_position.x() > rect.roi_x + self.parent._main_object_finder.x - threshold and
                mouse_position.x() < rect.roi_x + self.parent._main_object_finder.x + rect.roi_width + threshold and
                mouse_position.y() > rect.roi_y + self.parent._main_object_finder.y - threshold and
                mouse_position.y() < rect.roi_y + self.parent._main_object_finder.y + threshold):
            return True
        elif ((rect.roi_unlimited_left is True or rect.roi_unlimited_right is True) and
                mouse_position.y() > rect.roi_y + self.parent._main_object_finder.y - threshold and
                mouse_position.y() < rect.roi_y + self.parent._main_object_finder.y + threshold):
            return True

        else:
            return False
            
    def is_mouse_on_bottom_border(self, rect):
        mouse_position = QPoint(QCursor.pos())
        
        if (mouse_position.x() > rect.x and
                mouse_position.x() < rect.x + rect.width and
                mouse_position.y() > rect.y + rect.height - int((8 *self.scaling_factor)) and
                mouse_position.y() < rect.y + rect.height + int((8 *self.scaling_factor))):
            return True
        else:
            return False
            
    def is_mouse_on_bottom_border_roi(self, rect):
        if rect.x == 0 and rect.width == 0 and rect.y == 0 and rect.height == 0:
            return False
            
        mouse_position = QPoint(QCursor.pos())
        
        threshold = self.calc_threshold_border(rect)
        
        if (rect.roi_unlimited_down is True ):
            return False
        elif (mouse_position.x() > rect.roi_x + self.parent._main_object_finder.x - threshold and
                mouse_position.x() < rect.roi_x + self.parent._main_object_finder.x + rect.roi_width + threshold and
                mouse_position.y() > rect.roi_y + self.parent._main_object_finder.y + rect.roi_height - threshold and
                mouse_position.y() < rect.roi_y + self.parent._main_object_finder.y + rect.roi_height + threshold):
            return True
        elif ((rect.roi_unlimited_left is True or rect.roi_unlimited_right is True) and
                mouse_position.y() > rect.roi_y + self.parent._main_object_finder.y + rect.roi_height - threshold and
                mouse_position.y() < rect.roi_y + self.parent._main_object_finder.y + rect.roi_height + threshold):
            return True
        else:
            return False
 
    def draw_main_object_rect(self, qp):
    
            if self.parent._main_object_finder.show is False:
                return
                
            pen = QPen()
            pen.setBrush(QColor(255, 0, 0, 255))
            pen.setWidth(1)
            qp.setPen(pen)
            
            font = qp.font()
            font.setPixelSize(11 * self.scaling_factor);

            qp.setFont(font)
            qp.drawText( QPoint(self.parent._main_object_finder.x -1, self.parent._main_object_finder.y -(6*self.scaling_factor)), "M" )

            
            qp.fillRect(self.parent._main_object_finder.x,
                self.parent._main_object_finder.y,
                self.parent._main_object_finder.width,
                self.parent._main_object_finder.height,
                QBrush(QColor(255, 0, 255, 130)))
                
            qp.drawRect(QRect(self.parent._main_object_finder.x,
                self.parent._main_object_finder.y,
                self.parent._main_object_finder.width,
                self.parent._main_object_finder.height))  
        
     
    def draw_sub_templateangle(self, qp, image_finder, cnt):
    
            if image_finder.show is False:
                return
    
            pen = QPen()
            pen.setWidth(1)
            pen.setStyle(Qt.SolidLine)
            pen.setBrush(QBrush(QColor(255, 0, 198, 255)))
            qp.setPen(pen)
            
            OuterPath_roi = QPainterPath()
            OuterPath_roi.setFillRule(Qt.WindingFill)
            
            roi_x = image_finder.roi_x + self.parent._main_object_finder.x
            roi_y = image_finder.roi_y + self.parent._main_object_finder.y
            roi_width = image_finder.roi_width
            roi_height = image_finder.roi_height
            
            if image_finder.roi_unlimited_up is True and self.parent._main_deleted is False:
                roi_y = 0
                roi_height = image_finder.roi_y + self.parent._main_object_finder.y + roi_height

            if image_finder.roi_unlimited_down is True and self.parent._main_deleted is False:
                if image_finder.roi_unlimited_up is True:
                    roi_height = self._bg_pixmap.height()-1
                else:
                    roi_height = self._bg_pixmap.height() - (image_finder.roi_y + self.parent._main_object_finder.y + 1)
                    
                    #print self._bg_pixmap.width(), (image_finder.roi_x + self.parent._main_object_finder.x)

            if image_finder.roi_unlimited_left is True and self.parent._main_deleted is False:
                roi_x = 0
                roi_width = image_finder.roi_x + self.parent._main_object_finder.x + roi_width

            if image_finder.roi_unlimited_right is True and self.parent._main_deleted is False:
                if image_finder.roi_unlimited_left is True:
                    roi_width = self._bg_pixmap.width() -1
                else:
                    roi_width = self._bg_pixmap.width() - (image_finder.roi_x + self.parent._main_object_finder.x + 1)
            
            OuterPath_roi.addRect(roi_x,
                    roi_y,
                    roi_width,
                    roi_height)
                
            if image_finder.x != 0 and image_finder.y != 0:
            
                font = qp.font()
                font.setPixelSize(11 * self.scaling_factor);

                qp.setFont(font)
                qp.drawText( QPoint(image_finder.x -1, image_finder.y -(6*self.scaling_factor)), str(cnt) )


            
                InnerPath_roi = QPainterPath()
                
                """
                InnerPath_roi.addRect(image_finder.x,
                    image_finder.y,
                    image_finder.width,
                    image_finder.height)
                """
                

                InnerPath_roi.addRect(image_finder.x,
                    image_finder.y,
                    image_finder.width,
                    image_finder.height)
                    
                                            
                FillPath_roi = OuterPath_roi.subtracted(InnerPath_roi)
                qp.fillPath(FillPath_roi, QBrush(QColor(172, 96, 246, 180), Qt.BDiagPattern))
                
                qp.drawRect(QRect(roi_x,
                    roi_y,
                    roi_width,
                    roi_height))  
                    
                qp.fillRect(image_finder.x,
                    image_finder.y,
                    image_finder.width,
                    image_finder.height,
                    QBrush(QColor(172, 96, 246, 130)))
                
                    
                qp.drawRect(QRect(image_finder.x,
                    image_finder.y,
                    image_finder.width,
                    image_finder.height))
            
            else:
                qp.fillRect(roi_x,
                    roi_y,
                    roi_width,
                    roi_height,
                    QBrush(QColor(172, 96, 246, 180), Qt.BDiagPattern))
                    
                qp.drawRect(QRect(roi_x,
                    roi_y,
                    roi_width,
                    roi_height))  
                
            """
            qp.fillRect(image_finder.x,
                image_finder.y,
                image_finder.width,
                image_finder.height,
                QBrush(QColor(172, 96, 246, 130)))
            
                
            qp.drawRect(QRect(image_finder.x,
                image_finder.y,
                image_finder.width,
                image_finder.height))
            """
     
    def draw_cross_lines(self, qp):
    
        self.setCursor(QCursor(Qt.CrossCursor))
                
        center = QPoint(QCursor.pos())
        
        pen = QPen()
        pen.setDashPattern([1, 1])
        pen.setWidth(1)
        pen.setBrush(QColor(32, 178, 170, 255))
        
        qp.setPen(pen)

        qp.drawLine(center.x(), center.y(), center.x(), 0)
        qp.drawLine(center.x(), center.y(), center.x(), self.height())
        qp.drawLine(center.x(), center.y(), 0, center.y())
        qp.drawLine(center.x(), center.y(), self.width(), center.y())

    def draw_capturing_roi_lines(self, qp):
           
        self.draw_capturing_rectangle_lines(qp)
        """
        mouse_position = QPoint(QCursor.pos())
        
        pen = QPen()
        pen.setWidth(1)
        pen.setStyle(Qt.DashLine)
        pen.setBrush(QBrush(QColor(0, 255, 0, 255)))
        
        qp.setPen(pen)
            
        rect = QRect(self.__click_position.x(), self.__click_position.y(),
            mouse_position.x() - self.__click_position.x(), mouse_position.y() - self.__click_position.y())
            
        qp.drawRect(rect)
        """
        
    def draw_capturing_rectangle_lines(self, qp):
            
        mouse_position = QPoint(QCursor.pos())
        
        pen = QPen()
        pen.setWidth(1)
        pen.setStyle(Qt.SolidLine)
        pen.setBrush(QBrush(QColor(0, 255, 0, 255)))
        
        qp.setPen(pen)
        
        qp.fillRect(self.__click_position.x() + 1,
            self.__click_position.y() + 1,
            mouse_position.x() - self.__click_position.x() - 1,
            mouse_position.y() - self.__click_position.y() - 1,
            QBrush(QColor(32, 178, 170, 100)))
            
        rect = QRect(self.__click_position.x(), self.__click_position.y(),
            mouse_position.x() - self.__click_position.x(), mouse_position.y() - self.__click_position.y())
            
        qp.drawRect(rect)