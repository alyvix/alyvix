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
import cv2
import copy
import codecs
import ast

import time

from PyQt4.QtGui import QApplication, QWidget, QCursor, QImage, QPainter, QPainter, QPen, QColor, QPixmap, QBrush, QPainterPath, QDialog, QListWidgetItem , QTextEdit, QHBoxLayout, QTextCharFormat, QMessageBox, QFont, QFontMetrics, QTextCursor
from PyQt4.QtCore import Qt, QThread, SIGNAL, QTimer, QUrl, QPoint, QRect, QModelIndex, SLOT, pyqtSlot, QString, QChar
from PyQt4.Qt import QFrame

from PyQt4.QtWebKit import QWebSettings

#from alyvix.tools.screen import ScreenCapture
#from alyvix.finders.rectfinder import RectFinder
from alyvix_text_finder_properties_view import Ui_Form
from alyvix_text_check import Ui_Form as Ui_Form_Text
#from alyvix_text_finder_properties_view_2 import Ui_Form
#from alyvix_text_finder_properties_view_3 import Ui_Form as Ui_Form_2
from alyvix.finders.cv.textfinder import TextFinder

import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET

from distutils.sysconfig import get_python_lib


class AlyvixTextFinderView(QWidget):

    def __init__(self, parent):
        QWidget.__init__(self)
        #self.setupUi(self)
        
        self.object_name = ""
        self.wait = True
        self.find = False
        self.wait_disapp = False
        self.args_number = 0
        self.timeout = 60
        self.timeout_exception = True
        self.enable_performance = True
        self.warning = 15.00
        self.critical = 40.00
        
        self.mouse_or_key_is_set = False
        
        self.setMouseTracking(True)
        
        self._bg_pixmap = QPixmap()
        self.__capturing = False
        
        self.__click_position = QPoint(0,0)
        
        self._main_text = None
        
        self._sub_texts_finder = []
        
        self.__deleted_texts = []
        
        #flags
        #self.__flag_mouse_left_button_is_pressed = False
        self.__flag_mouse_is_inside_rect = False
        self.__flag_capturing_main_text_rect_roi = True
        self.__flag_capturing_main_text_rect = False
        self.__flag_capturing_sub_text_rect_roi = False
        self.__flag_capturing_sub_text = False
        self.set_xy_offset = None  #-1 for main, other int for sub index
        self.__flag_need_to_delete_main_roi = False
        self.__flag_need_to_restore_main_roi = False
        self.__flag_need_to_restore_main_text_rect = False
        self.__flag_need_to_delete_roi = False
        self.__flag_need_to_restore_roi = False
        self._flag_show_min_max = False
        self._self_show_tolerance = False

        self.__index_deleted_rect_inside_roi = -1
        self.__restored_rect_roi = False
    
        self.parent = parent

        self._xml_name = self.parent.xml_name
        self._path = self.parent.path
        self._robot_file_name = self.parent.robot_file_name
        #self._alyvix_proxy_path = os.getenv("ALYVIX_HOME") + os.sep + "robotproxy"
        self._alyvix_proxy_path = get_python_lib() + os.sep + "alyvix" + os.sep + "robotproxy"
        self.action = self.parent.action
        
        if self.action == "edit":
            self.__flag_capturing_main_text_rect_roi = False
            self.__flag_capturing_main_text_rect = False
            self.__flag_capturing_sub_text_rect_roi = True
            self.__flag_capturing_sub_text = False
        
        self._code_lines = []
        self._code_lines_for_object_finder = []
        self._code_blocks = []
        
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        #self.update_path_and_name(path)
        
        self.build_objects()
        self.__old_code_v220 = self.get_old_code_v220()
        self.__old_code = self.get_old_code()
        #print self.__old_code
        
        self._old_main_text = copy.deepcopy(self._main_text)
        self._old_sub_text = copy.deepcopy(self._sub_texts_finder)
        
        self.esc_pressed = False
        self.ok_pressed = False
        
    def set_bg_pixmap(self, image):
        self._bg_pixmap = QPixmap.fromImage(image)
        
    def save_all(self):
    
        if self._main_text != None and self.ok_pressed is False:
            self.ok_pressed = True
            #print "dummy"
            #self.build_xml()
            self.build_code_array()
            self.build_xml()
            self.save_python_file()
            #self.build_perf_data_xml()
            image_name = self._path + os.sep + self.object_name + "_TextFinder.png"
            self._bg_pixmap.save(image_name,"PNG", -1)
            #self.save_template_images(image_name)
            if self.action == "new":
                self.parent.add_new_item_on_list()
                
        try:
            if self.parent.parent.is_object_finder_menu:
                if self.mouse_or_key_is_set is True:
                    
                    self.parent.parent._main_object_finder.mouse_or_key_is_set = True
                    #print "build_objjjjjjjjjjjjjjjjjjjjj"
        except:
            pass
            
        self.parent.show()
        self.close()
        
    def cancel_all(self):
        self._main_text = copy.deepcopy(self._old_main_text)
        self._sub_texts_finder = copy.deepcopy(self._old_sub_text)
        self.parent.show()
        self.close()
        
    def keyPressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Z: 
            self.delete_rect()
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Y:
            self.restore_rect()
        if event.key() == Qt.Key_Escape:
            if self._main_text is None and self.esc_pressed is False:
                self.esc_pressed = True
                self.parent.show()
                self.close()
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_O and self.set_xy_offset is None:
            self.image_view_properties = AlyvixTextFinderPropertiesView(self)
            self.image_view_properties.show()
            """
            self.parent.show()
            self.close()
            if self._main_text != None and self.esc_pressed is False:
                self.esc_pressed = True
                #print "dummy"
                #self.build_xml()
                self.build_code_array()
                self.build_xml()
                self.save_python_file()
                self.build_perf_data_xml()
                image_name = self._path + os.sep + self.object_name + "_TextFinder.png"
                self._bg_pixmap.save(image_name,"PNG", -1)
                #self.save_template_images(image_name)
                if self.action == "new":
                    self.parent.add_new_item_on_list()
            self.parent.show()
            self.close()
            """
    
    """
    def save_template_images(self, image_name):
    
        template_text_path = self._path + os.sep + self.object_name
        
        if not os.path.exists(template_text_path):
            os.makedirs(template_text_path)
    
        image = cv2.imread(image_name)
        x1 = self._main_text.x
        x2 = x1 + self._main_text.width
        y1 = self._main_text.y
        y2 = y1 + self._main_text.height
        image2 = image[y1:y2,x1:x2]
        cv2.imwrite(template_text_path + os.sep + "main_template.png", image2)
        
        cnt = 1
        for sub_text in self._sub_texts_finder:
            x1 = sub_text.x
            x2 = x1 + sub_text.width
            y1 = sub_text.y
            y2 = y1 + sub_text.height
            image2 = image[y1:y2,x1:x2]
            cv2.imwrite(template_text_path + os.sep + "sub_text_" + str(cnt) + ".png", image2)
            cnt = cnt + 1
    """
    
    def closeEvent(self, event):
        self.close
        
    def mouseMoveEvent(self, event):
        self.update()
        
    def mouseDoubleClickEvent(self, event):
        if False is True:
            #self.BringWindowToFront()
            return
        if self.is_mouse_inside_rect(self._main_text) and self.set_xy_offset is None:
            self.image_view_properties = AlyvixTextFinderPropertiesView(self)
            self.image_view_properties.show()
        
    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
        
            self.__click_position = QPoint(QCursor.pos())
            
            if self.set_xy_offset is not None:
                if self.set_xy_offset == -1:
                    self._main_text.x_offset = self.__click_position.x() - self._main_text.x
                    self._main_text.y_offset = self.__click_position.y() - self._main_text.y
                else:
                    self._sub_texts_finder[self.set_xy_offset].x_offset = self.__click_position.x() - self._sub_texts_finder[self.set_xy_offset].x
                    self._sub_texts_finder[self.set_xy_offset].y_offset = self.__click_position.y() - self._sub_texts_finder[self.set_xy_offset].y
            else:
                self.__capturing = True
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.__capturing = False
            
            if self.set_xy_offset is not None:
                self.set_xy_offset = None
            
            elif self.__flag_capturing_main_text_rect_roi is True:
                self.__flag_capturing_main_text_rect_roi = False
                self.__flag_capturing_main_text_rect = True
                self.__flag_need_to_delete_main_roi = True
                #if len(self.__deleted_texts) > 0:
                #    del self.__deleted_texts[-1]
                self.add_main_text_roi()
                
            elif self.__flag_capturing_main_text_rect is True:
                #self.__flag_capturing_main_text_rect_roi = False
                self.__flag_capturing_main_text_rect = False
                self.__flag_capturing_sub_text_rect_roi = True
                self.__flag_need_to_delete_main_roi = False
                self.add_main_rect()
            elif self.__flag_capturing_sub_text_rect_roi is True:
                self.__flag_capturing_sub_text_rect_roi = False
                self.__flag_capturing_sub_text = True
                self.__flag_need_to_delete_roi = True
                if len(self.__deleted_texts) > 0:
                    del self.__deleted_texts[-1]
                self.add_sub_text_roi()
            elif self.__flag_capturing_sub_text is True:
                self.__flag_capturing_sub_text = False
                self.__flag_capturing_sub_text_rect_roi = True
                self.__flag_need_to_delete_roi = False
                self.add_sub_text_attributes()
            
        self.update()
        

        
    def paintEvent(self, event):
    
        qp = QPainter()
        qp.begin(self)
        qp.drawPixmap(0, 0, self._bg_pixmap)
        
        self.__flag_mouse_is_inside_rect = False
        self.__index_of_rectangle_with_mouse_inside = -2
        
        if self._main_text is not None:
            
            self.draw_main_text_rect(qp)
            
            if self.is_mouse_inside_rect(self._main_text):
                self.__flag_mouse_is_inside_rect = True
        
        rect_index = 0
        #self.__sub_text_color_index = 0
        for sub_text_finder in self._sub_texts_finder:
        
            self.draw_sub_textangle(qp, sub_text_finder)
            
            if self.is_mouse_inside_rect(sub_text_finder):
                self.__flag_mouse_is_inside_rect = True
 
        if self.set_xy_offset is None:
            if self.__capturing is False:
                self.draw_cross_lines(qp)
            elif self.__flag_capturing_main_text_rect_roi is True:
                self.draw_capturing_roi_lines(qp)  
            elif self.__flag_capturing_main_text_rect is True:
                self.draw_capturing_rectangle_lines(qp)
            elif self.__flag_capturing_sub_text_rect_roi is True:
                self.draw_capturing_roi_lines(qp)
            elif self.__flag_capturing_sub_text is True:
                self.draw_capturing_rectangle_lines(qp)
        qp.end()
        
    def is_mouse_inside_rect(self, rect):
    
        mouse_position = QPoint(QCursor.pos())
        
        if (mouse_position.x() > rect.x and
                mouse_position.x() < rect.width + rect.x and
                mouse_position.y() > rect.y and
                mouse_position.y() < rect.height + rect.y):
            return True
        else:
            return False
 
    def draw_main_text_rect(self, qp):
    
            if self._main_text.show is False:
                return
                
            pen = QPen()
            pen.setWidth(1)
            pen.setStyle(Qt.SolidLine)
            pen.setBrush(QBrush(QColor(255, 0, 0, 255)))
            qp.setPen(pen)
            
            """
            pen = QPen()
            pen.setBrush(QColor(255, 0, 0, 255))
            pen.setWidth(1)
            qp.setPen(pen)
            """
            
            OuterPath_roi = QPainterPath()
            OuterPath_roi.setFillRule(Qt.WindingFill)
            
            OuterPath_roi.addRect(self._main_text.roi_x,
                self._main_text.roi_y,
                self._main_text.roi_width,
                self._main_text.roi_height)
                
            if self._main_text.x != 0 and self._main_text.y != 0:
            
                InnerPath_roi = QPainterPath()
                
                """
                InnerPath_roi.addRect(self._main_text.x,
                    self._main_text.y,
                    self._main_text.width,
                    self._main_text.height)
                """
                

                InnerPath_roi.addRect(self._main_text.x,
                    self._main_text.y,
                    self._main_text.width,
                    self._main_text.height)
                    
                                            
                FillPath_roi = OuterPath_roi.subtracted(InnerPath_roi)
                qp.fillPath(FillPath_roi, QBrush(QColor(255, 0, 255, 180), Qt.BDiagPattern))
                
                qp.drawRect(QRect(self._main_text.roi_x,
                    self._main_text.roi_y,
                    self._main_text.roi_width,
                    self._main_text.roi_height))  
                    
                qp.fillRect(self._main_text.x,
                    self._main_text.y,
                    self._main_text.width,
                    self._main_text.height,
                    QBrush(QColor(255, 0, 255, 130)))
                
                    
                qp.drawRect(QRect(self._main_text.x,
                    self._main_text.y,
                    self._main_text.width,
                    self._main_text.height))
                    
                if self._main_text.click is True or self._main_text.rightclick is True or self._main_text.mousemove is True or self._main_text.doubleclick is True:
                    
                    if self._main_text.x_offset is None and self._main_text.y_offset is None:
                        click_pos = QPoint(self._main_text.x + (self._main_text.width/2), self._main_text.y + (self._main_text.height/2))
                    else:
                        click_pos = QPoint(self._main_text.x + self._main_text.x_offset, self._main_text.y + self._main_text.y_offset)
                        
                    old_brush = qp.brush()
                        
                    qp.setBrush(QColor(255, 0, 255, 130))
                    qp.drawLine(self._main_text.x + (self._main_text.width/2), self._main_text.y + (self._main_text.height/2), click_pos.x(), click_pos.y())
                    qp.drawEllipse(click_pos, 10, 10)
                    qp.setBrush(old_brush)
            
            else:
                qp.fillRect(self._main_text.roi_x + self._main_text.x,
                    self._main_text.roi_y + self._main_text.y,
                    self._main_text.roi_width,
                    self._main_text.roi_height,
                    QBrush(QColor(255, 0, 255, 180), Qt.BDiagPattern))
                    
                qp.drawRect(QRect(self._main_text.roi_x + self._main_text.x,
                    self._main_text.roi_y + self._main_text.y,
                    self._main_text.roi_width,
                    self._main_text.roi_height))  
                
            #####################################
                
            """
            pen = QPen()
            pen.setBrush(QColor(255, 0, 0, 255))
            pen.setWidth(1)
            qp.setPen(pen)
            
            qp.fillRect(self._main_text.x,
                self._main_text.y,
                self._main_text.width,
                self._main_text.height,
                QBrush(QColor(255, 0, 255, 130)))
                
            qp.drawRect(QRect(self._main_text.x,
                self._main_text.y,
                self._main_text.width,
                self._main_text.height))  
            """
        
     
    def draw_sub_textangle(self, qp, text_finder):
    
            if text_finder.show is False:
                return
    
            pen = QPen()
            pen.setWidth(1)
            pen.setStyle(Qt.SolidLine)
            pen.setBrush(QBrush(QColor(255, 0, 198, 255)))
            qp.setPen(pen)
            
            OuterPath_roi = QPainterPath()
            OuterPath_roi.setFillRule(Qt.WindingFill)
            
            OuterPath_roi.addRect(text_finder.roi_x + self._main_text.x,
                text_finder.roi_y + self._main_text.y,
                text_finder.roi_width,
                text_finder.roi_height)
                
            if text_finder.x != 0 and text_finder.y != 0:
            
                InnerPath_roi = QPainterPath()
                
                """
                InnerPath_roi.addRect(text_finder.x,
                    text_finder.y,
                    text_finder.width,
                    text_finder.height)
                """
                

                InnerPath_roi.addRect(text_finder.x,
                    text_finder.y,
                    text_finder.width,
                    text_finder.height)
                    
                                            
                FillPath_roi = OuterPath_roi.subtracted(InnerPath_roi)
                qp.fillPath(FillPath_roi, QBrush(QColor(172, 96, 246, 180), Qt.BDiagPattern))
                
                qp.drawRect(QRect(text_finder.roi_x + self._main_text.x,
                    text_finder.roi_y + self._main_text.y,
                    text_finder.roi_width,
                    text_finder.roi_height))  
                    
                qp.fillRect(text_finder.x,
                    text_finder.y,
                    text_finder.width,
                    text_finder.height,
                    QBrush(QColor(172, 96, 246, 130)))
                
                    
                qp.drawRect(QRect(text_finder.x,
                    text_finder.y,
                    text_finder.width,
                    text_finder.height))
                    
                if text_finder.click is True or text_finder.rightclick is True or text_finder.mousemove is True or text_finder.doubleclick is True:
                        
                    
                    if text_finder.x_offset is None and text_finder.y_offset is None:
                        click_pos = QPoint(text_finder.x + (text_finder.width/2), text_finder.y + (text_finder.height/2))
                    else:
                        click_pos = QPoint(text_finder.x + text_finder.x_offset, text_finder.y + text_finder.y_offset)
                        
                    old_brush = qp.brush()
                        
                    qp.setBrush(QColor(172, 96, 246, 130))
                    qp.drawLine(text_finder.x + (text_finder.width/2), text_finder.y + (text_finder.height/2), click_pos.x(), click_pos.y())
                    qp.drawEllipse(click_pos, 10, 10)
                    qp.setBrush(old_brush)
            
            else:
                qp.fillRect(text_finder.roi_x + self._main_text.x,
                    text_finder.roi_y + self._main_text.y,
                    text_finder.roi_width,
                    text_finder.roi_height,
                    QBrush(QColor(172, 96, 246, 180), Qt.BDiagPattern))
                    
                qp.drawRect(QRect(text_finder.roi_x + self._main_text.x,
                    text_finder.roi_y + self._main_text.y,
                    text_finder.roi_width,
                    text_finder.roi_height))  
                
            """
            qp.fillRect(text_finder.x,
                text_finder.y,
                text_finder.width,
                text_finder.height,
                QBrush(QColor(172, 96, 246, 130)))
            
                
            qp.drawRect(QRect(text_finder.x,
                text_finder.y,
                text_finder.width,
                text_finder.height))
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
    
    def add_main_rect(self):
    
        rect_attributes = self.convert_mouse_position_into_rect()
        
        if rect_attributes is not None:
        
            x, y, width, height = rect_attributes
            
            if (x + width > self._main_text.roi_x + self._main_text.x + self._main_text.roi_width) or (x < self._main_text.roi_x + self._main_text.x) or \
                (y + height > self._main_text.roi_y + self._main_text.y + self._main_text.roi_height) or (y < self._main_text.roi_y + self._main_text.y):
                self.__flag_capturing_main_text_rect = True
                self.__flag_capturing_main_text_rect_roi = False
                return
        
            #text_finder = MainTextForGui()
            self._main_text.x = x
            self._main_text.y = y
            self._main_text.height = height
            self._main_text.width = width
            
        else:
            self.__flag_capturing_main_text_rect = True
            self.__flag_capturing_sub_text_rect_roi = False
            
    def add_main_text_roi(self):
        rect_attributes = self.convert_mouse_position_into_rect()
        
        if rect_attributes is not None:
        
            x, y, width, height = rect_attributes

            text_finder = MainTextForGui()
            text_finder.roi_x = x
            text_finder.roi_y = y
            text_finder.roi_height = height
            text_finder.roi_width = width
            
            self._main_text = text_finder
        else:
            self.__flag_capturing_main_text_rect = False
            self.__flag_capturing_main_text_rect_roi = True
            
    def add_sub_text_roi(self):
    
        rect_attributes = self.convert_mouse_position_into_rect()
        
        if rect_attributes is not None:
        
            x, y, width, height = rect_attributes

            text_finder = SubTextForGui()                
            text_finder.roi_x = x - self._main_text.x
            text_finder.roi_y = y - self._main_text.y
            text_finder.roi_height = height
            text_finder.roi_width = width
            
            self._sub_texts_finder.append(text_finder)
            
        else:
            self.__flag_capturing_sub_text = False
            self.__flag_capturing_sub_text_rect_roi = True
            
    def add_sub_text_attributes(self):
    
        rect_attributes = self.convert_mouse_position_into_rect()
        
        if rect_attributes is not None:
        
            x, y, width, height = rect_attributes

            text_finder = self._sub_texts_finder[-1]
            
            if (x + width > text_finder.roi_x + self._main_text.x + text_finder.roi_width) or (x < text_finder.roi_x + self._main_text.x) or \
                (y + height > text_finder.roi_y + self._main_text.y + text_finder.roi_height) or (y < text_finder.roi_y + self._main_text.y):
                self.__flag_capturing_sub_text = True
                self.__flag_capturing_sub_text_rect_roi = False
                return
            
            text_finder.x = x
            text_finder.y = y
            text_finder.height = height
            text_finder.width = width
            text_finder.min_height = height/2
            text_finder.max_height = height*2
            text_finder.min_width = width/2
            text_finder.max_width = width*2
        else:
            self.__flag_capturing_sub_text = True
            self.__flag_capturing_sub_text_rect_roi = False
    
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
            
        
    def move_main_rect(self):
        mouse_pos = QPoint(QCursor.pos())
        self._main_text.x = mouse_pos.x() - self.__moving_rect_mouse_offset_x
        self._main_text.y = mouse_pos.y() - self.__moving_rect_mouse_offset_y
        #self.update()
        
    def delete_rect(self):
        
        if len(self._sub_texts_finder) > 0:
            
            index = -1 #self.__index_deleted_rect_inside_roi
            if  self.__flag_need_to_delete_roi is False and self._sub_texts_finder[index].x != 0 and self._sub_texts_finder[index].y != 0 \
                and self._sub_texts_finder[index].width != 0 and self._sub_texts_finder[index].height != 0:
                
                self._sub_texts_finder[index].deleted_x = self._sub_texts_finder[index].x
                self._sub_texts_finder[index].deleted_y = self._sub_texts_finder[index].y
                self._sub_texts_finder[index].deleted_width = self._sub_texts_finder[index].width
                self._sub_texts_finder[index].deleted_height = self._sub_texts_finder[index].height
                
                self._sub_texts_finder[index].x = 0
                self._sub_texts_finder[index].y = 0
                self._sub_texts_finder[index].width = 0
                self._sub_texts_finder[index].height = 0
                
                self.__flag_need_to_delete_roi = True
                self.__flag_need_to_restore_roi = False
                self.__flag_capturing_sub_text_rect_roi = False
                self.__flag_capturing_sub_text = True
               
            else: #self.__flag_need_to_delete_roi:
                
                self.__deleted_texts.append(self._sub_texts_finder[-1])
                del self._sub_texts_finder[-1]
                self.__flag_need_to_delete_roi = False
                self.__flag_need_to_restore_roi = True
                self.__flag_capturing_sub_text_rect_roi = True
                self.__flag_capturing_sub_text = False
            
        elif self._main_text is not None and self.__flag_need_to_delete_main_roi is False:
            #self.__deleted_texts.append(self._main_text)
            #self._main_text = None
            #self.__flag_capturing_main_text_rect = True
            #self.__flag_capturing_sub_text_rect_roi = False

            self._main_text.deleted_x = self._main_text.x
            self._main_text.deleted_y = self._main_text.y
            self._main_text.deleted_width = self._main_text.width
            self._main_text.deleted_height = self._main_text.height
            
            self._main_text.x = 0
            self._main_text.y = 0
            self._main_text.width = 0
            self._main_text.height = 0
            
            self.__flag_need_to_delete_main_roi = True
            self.__flag_need_to_restore_main_roi = False
            self.__flag_capturing_main_text_rect_roi = False
            self.__flag_capturing_main_text_rect = True
            self.__flag_need_to_restore_main_text_rect = True
               
        elif self._main_text is not None: #self.__flag_need_to_delete_roi:
        
            self.__deleted_texts.append(self._main_text)
            self._main_text = None
            print "deleted main"
            self.__flag_need_to_delete_main_roi = False
            self.__flag_need_to_restore_main_roi = True
            self.__flag_capturing_main_text_rect_roi = True
            self.__flag_capturing_sub_text_rect_roi = False
            #self.__flag_need_to_restore_main_text_rect = False
            """
            self.__deleted_texts.append(self._sub_texts_finder[-1])
            del self._sub_texts_finder[-1]
            self.__flag_need_to_delete_roi = False
            self.__flag_need_to_restore_roi = True
            self.__flag_capturing_sub_text_rect_roi = True
            self.__flag_capturing_sub_text = False
            """
        self.update()
        
    def restore_rect(self):
    
        if self._main_text is not None and self.__flag_need_to_restore_main_text_rect is True:
            
            if  self._main_text.deleted_x is not None and \
                self._main_text.deleted_y is not None and self._main_text.deleted_height is not None \
                and self._main_text.deleted_width is not None:
                
                self._main_text.x = self._main_text.deleted_x
                self._main_text.y = self._main_text.deleted_y
                self._main_text.width = self._main_text.deleted_width
                self._main_text.height = self._main_text.deleted_height
                
                self._main_text.deleted_x = None
                self._main_text.deleted_y = None
                self._main_text.deleted_width = None
                self._main_text.deleted_height = None
                
                
                self.__flag_capturing_sub_text_rect_roi = True
                self.__flag_capturing_sub_text = False
                self.__flag_need_to_restore_main_text_rect = False
                
            self.__flag_need_to_restore_main_roi = False
            
            self.__flag_capturing_main_text_rect = False
            self.__flag_capturing_main_text_rect_roi = False

        elif len(self.__deleted_texts) > 0 and self.__flag_need_to_restore_main_roi is True:
            self._main_text = copy.deepcopy(self.__deleted_texts[-1])
            del self.__deleted_texts[-1]
            self.__flag_need_to_restore_main_roi = False
            
            self.__flag_capturing_main_text_rect_roi = False
            self.__flag_capturing_main_text_rect = True
            
        elif len(self.__deleted_texts) > 0 and self.__flag_need_to_restore_roi is True:
            self._sub_texts_finder.append(self.__deleted_texts[-1])
            del self.__deleted_texts[-1]
            self.__flag_need_to_restore_roi = False
            
            self.__flag_capturing_sub_text_rect_roi = False
            self.__flag_capturing_sub_text = True
                
        elif self.__flag_need_to_restore_roi is False:
        
            index = -1
            
            if  self._sub_texts_finder[index].deleted_x is not None and \
                self._sub_texts_finder[index].deleted_y is not None and self._sub_texts_finder[index].deleted_height is not None \
                and self._sub_texts_finder[index].deleted_width is not None:
                
                self._sub_texts_finder[index].x = self._sub_texts_finder[index].deleted_x
                self._sub_texts_finder[index].y = self._sub_texts_finder[index].deleted_y
                self._sub_texts_finder[index].width = self._sub_texts_finder[index].deleted_width
                self._sub_texts_finder[index].height = self._sub_texts_finder[index].deleted_height
                
                self._sub_texts_finder[index].deleted_x = None
                self._sub_texts_finder[index].deleted_y = None
                self._sub_texts_finder[index].deleted_width = None
                self._sub_texts_finder[index].deleted_height = None
                
                self.__flag_capturing_sub_text_rect_roi = True
                self.__flag_capturing_sub_text = False
                
            self.__flag_need_to_restore_roi = True

        """
        if len(self.__deleted_texts) == 0:
            self.__index_of_deleted_rect_inside_roi = 0
        """
            
        self.update()
        
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
        
        file_code_string = file_code_string.replace(unicode(self.__old_code_v220, 'utf-8'), "")
        file_code_string = file_code_string.replace(unicode(self.__old_code, 'utf-8'), "")
        
        string = file_code_string
        string = string.encode('utf-8')

        file = codecs.open(filename, 'w', 'utf-8')
        file.write(unicode(string, 'utf-8'))
        file.close()    

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
        
        if self.action == "new" and file_code_string == "":
            file_code_string = file_code_string + "# -*- coding: utf-8 -*-" + os.linesep
            file_code_string = file_code_string + "from alyvixcommon import *" + os.linesep
            file_code_string = file_code_string + os.linesep
            file_code_string = file_code_string + os.linesep
            file_code_string = file_code_string + "os.environ[\"alyvix_test_case_name\"] = os.path.basename(__file__).split('.')[0]" + os.linesep
            file_code_string = file_code_string + os.linesep
            file_code_string = file_code_string + current_code_string
        elif self.action == "new":
            file_code_string = file_code_string + current_code_string
        elif self.action == "edit":
            file_code_string = file_code_string.replace(unicode(self.__old_code_v220, 'utf-8'), current_code_string)
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
    
    def get_old_code_v220(self):
        if self._main_text is None:
            return "".encode('utf-8')
        
        self.build_code_array_v220()
        return self.build_code_string()
    
    def get_old_code(self):
        if self._main_text is None:
            return "".encode('utf-8')
        
        self.build_code_array()
        return self.build_code_string()
    
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
        
    def build_code_array_v220(self):
    
        kmanager_declared = False
        mmanager_declared = False
       
        if self._main_text is None:
            return
            
        self._code_lines = []
        self._code_lines_for_object_finder = []
            
        name = self.object_name
        
        if name == "":
            name = time.strftime("text_finder_%d_%m_%y_%H_%M_%S")
            self.object_name = name
            
        #self._code_lines.append("def " + name + "():")
        
        strcode = name + "_object = None" #TextFinder(\"" + name + "\")"
        self._code_lines.append(strcode)
        self._code_lines_for_object_finder.append(strcode)
        
        self._code_lines.append("")
        
        string_function_args = "def " + name + "_build_object("
        
        args_range = range(1, self.args_number + 1)
        
        for arg_num in args_range:
            string_function_args = string_function_args + "arg" + str(arg_num) + ", " 
        
        if string_function_args.endswith(", "):
            string_function_args = string_function_args[:-2]
        string_function_args = string_function_args + "):"
        self._code_lines.append(string_function_args)
        
            
        
        #strcode = "    text_finder = TextFinder(\"" + name + "\")"
        #self._code_lines.append(strcode)
        #self._code_lines_for_object_finder.append(strcode)
        
        roi_x = str(self._main_text.roi_x)
        roi_y = str(self._main_text.roi_y)
        roi_width = str(self._main_text.roi_width)
        roi_height = str(self._main_text.roi_height)
        
        self._code_lines.append("    global " + name + "_object")  
        self._code_lines.append("    " + name + "_object = TextFinder(\"" + name + "\")")
        
        text_to_find = ""
        
        if self._main_text.quotes_ocr is True:
            text_to_find = "\"" + unicode(self._main_text.text, "utf8") + "\""
        else:
            text_to_find = self._main_text.text + ".encode('utf8')"
        
        if self._main_text.whitelist == "'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ&:/-_\,+()*.=[]<>@":
            str1 = "    " + name + "_object.set_main_component({\"text\": " + text_to_find + ", \"lang\": \""  + self._main_text.lang + "\"},"
        else:
            str1 = "    " + name + "_object.set_main_component({\"text\": " + text_to_find + ", \"lang\": \""  + self._main_text.lang + "\"" + ", \"whitelist\": \"" + unicode(self._main_text.whitelist, "utf8") + "\"},"
            
        str2 ="                                   {\"roi_x\": " + roi_x + ", \"roi_y\": " + roi_y + ", \"roi_width\": " + roi_width + ", \"roi_height\": " + roi_height + "})"
            
        self._code_lines.append(str1)
        self._code_lines.append(str2)
        self._code_lines_for_object_finder.append(str1)
        self._code_lines_for_object_finder.append(str2)
        
        #self._code_lines.append("\n")
        
        cnt = 1
        for sub_text in self._sub_texts_finder:
            if sub_text.height != 0 and sub_text.width !=0:
            
                #sub_text.path = template_text_path + os.sep + "sub_text_" + str(cnt) + ".png"
                #sub_text.path = sub_text.path.replace("\\","\\\\")
            
                #roi_x = str(sub_text.roi_x - self._main_text.x)
                roi_x = str(sub_text.roi_x)
                roi_y = str(sub_text.roi_y)
                
                roi_width = str(sub_text.roi_width)
                roi_height = str(sub_text.roi_height)
                    
                text_to_find = ""
                if sub_text.quotes_ocr is True:
                    text_to_find = "\"" + unicode(sub_text.text, "utf8") + "\""
                else:
                    text_to_find = sub_text.text + ".encode('utf8')"
            
                #str1 = "    text_finder.add_sub_component({\"path\": \"" + sub_text.path + "\", \"threshold\":" + repr(sub_text.threshold) + "},"
                if sub_text.whitelist == "'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ&:/-_\,+()*.=[]<>@":
                    str1 = "    " + name + "_object.add_sub_component({\"text\": " + text_to_find + ", \"lang\": \"" + sub_text.lang + "\"},"
                else:
                    str1 = "    " + name + "_object.add_sub_component({\"text\": " + text_to_find + ", \"lang\": \"" + sub_text.lang + "\", \"whitelist\": \"" + unicode(sub_text.whitelist, "utf8") + "\"},"
                    
                
                str2 = "                                  {\"roi_x\": " + roi_x + ", \"roi_y\": " + roi_y + ", \"roi_width\": " + roi_width + ", \"roi_height\": " + roi_height + "})"
    
                self._code_lines.append(str1)
                self._code_lines.append(str2)
                self._code_lines_for_object_finder.append(str1)
                self._code_lines_for_object_finder.append(str2)
    
                #self._code_lines.append("\n")
                cnt = cnt + 1
        
        self._code_lines.append("")
        
        string_function_args = "def " + name + "_mouse_keyboard("
        
        args_range = range(1, self.args_number + 1)
        
        for arg_num in args_range:
            string_function_args = string_function_args + "arg" + str(arg_num) + ", " 
        
        if string_function_args.endswith(", "):
            string_function_args = string_function_args[:-2]
        string_function_args = string_function_args + "):"
        self._code_lines.append(string_function_args)
        
        self._code_lines.append("    global " + name + "_object")
        
        if self._main_text.click == True or self._main_text.doubleclick == True or self._main_text.rightclick == True or self._main_text.mousemove == True:
        
            self._code_lines.append("    main_text_pos = " + name + "_object.get_result(0)")  
        
            if mmanager_declared is False:
                self._code_lines.append("    m = MouseManager()")
                mmanager_declared = True
                
            self._code_lines.append("    time.sleep(2)")
                                
            if self._main_text.click == True:
                self._code_lines.append("    m.click(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2), 1)")
            elif self._main_text.doubleclick == True:
                self._code_lines.append("    m.click(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2), 1, 2)")
            elif self._main_text.rightclick == True:
                self._code_lines.append("    m.click(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2), 2)")
            elif self._main_text.mousemove == True:
                self._code_lines.append("    m.move(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2))")

                
        if self._main_text.sendkeys != "":
            if kmanager_declared is False:
                self._code_lines.append("    k  = KeyboardManager()")
                kmanager_declared = True
            keys = unicode(self._main_text.sendkeys, 'utf-8')
            self._code_lines.append("    time.sleep(2)")
            
            if self._main_text.sendkeys_quotes is True:
                self._code_lines.append("    k.send(\"" + keys + "\", encrypted=" + str(self._main_text.text_encrypted) + ")")
            else:
                self._code_lines.append("    k.send(" + keys + ", encrypted=" + str(self._main_text.text_encrypted) + ")")
            
        cnt = 0
        for sub_text in self._sub_texts_finder:
        
            if sub_text.height != 0 and sub_text.width !=0:
                if sub_text.click == True or sub_text.doubleclick == True or sub_text.rightclick == True or sub_text.mousemove == True:
            
                    self._code_lines.append("    sub_text_" + str(cnt) + "_pos = " + name + "_object.get_result(0, " + str(cnt) + ")")  
                
                    if mmanager_declared is False:
                        self._code_lines.append("    m = MouseManager()")
                        mmanager_declared = True
                    self._code_lines.append("    time.sleep(2)")
                                        
                    if sub_text.click == True:
                        self._code_lines.append("    m.click(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2), 1)")
                    elif sub_text.doubleclick == True:
                        self._code_lines.append("    m.click(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2), 1, 2)")
                    elif sub_text.rightclick == True:
                        self._code_lines.append("    m.click(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2), 2)")
                    elif sub_text.mousemove == True:
                        self._code_lines.append("    m.move(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2))")
                        
                if sub_text.sendkeys != "":
                    if kmanager_declared is False:
                        self._code_lines.append("    k  = KeyboardManager()")
                        kmanager_declared = True
                    keys = unicode(sub_text.sendkeys, 'utf-8')
                    self._code_lines.append("    time.sleep(2)")
                    
                    if sub_text.sendkeys_quotes is True:
                        self._code_lines.append("    k.send(\"" + keys + "\", encrypted=" + str(sub_text.text_encrypted) + ")")
                    else:
                        self._code_lines.append("    k.send(" + keys + ", encrypted=" + str(sub_text.text_encrypted) + ")")
                              
                                    
                cnt = cnt + 1
                
        #if kmanager_declared is False and mmanager_declared is False:
        #    self._code_lines.append("    pass")
        
        self._code_lines.append("")
        
        string_function_args = "def " + name + "("
        
        args_range = range(1, self.args_number + 1)
        
        for arg_num in args_range:
            string_function_args = string_function_args + "arg" + str(arg_num) + ", " 
        
        if string_function_args.endswith(", "):
            string_function_args = string_function_args[:-2]
        string_function_args = string_function_args + "):"
        self._code_lines.append(string_function_args)
        
        self._code_lines.append("    global " + name + "_object")  

        string_function_args = "    " + name + "_build_object("
        
        args_range = range(1, self.args_number + 1)
        
        for arg_num in args_range:
            string_function_args = string_function_args + "arg" + str(arg_num) + ", " 
        
        if string_function_args.endswith(", "):
            string_function_args = string_function_args[:-2]
        string_function_args = string_function_args + ")"
        self._code_lines.append(string_function_args)

        if self.find is True:  
            self._code_lines.append("    " + name + "_object.find()")
        else:
            self._code_lines.append("    wait_time = " + name + "_object.wait(" + str(self.timeout) + ")")
           
        if self.enable_performance is True and self.find is False:
            self._code_lines.append("    if wait_time == -1:")
            if self.timeout_exception is True:
                self._code_lines.append("        raise Exception(\"step " + str(self.object_name) + " timed out, execution time: " + str(self.timeout) + "\")")             
            else:
                self._code_lines.append("        print \"*WARN* step " + str(self.object_name) + " timed out, execution time: " + str(self.timeout) + "\"")
                self._code_lines.append("        return False")
            self._code_lines.append("    elif wait_time < " + repr(self.warning) + ":")
            self._code_lines.append("        print \"step " + self.object_name + " is ok, execution time:\", wait_time, \"sec.\"")
            self._code_lines.append("    elif wait_time < " + repr(self.critical) + ":")
            self._code_lines.append("        print \"*WARN* step " + str(self.object_name) + " has exceeded the performance warning threshold:\", wait_time, \"sec.\"")
            self._code_lines.append("    else:")
            self._code_lines.append("        print \"*WARN* step " + str(self.object_name) + " has exceeded the performance critical threshold:\", wait_time, \"sec.\"")
            self._code_lines.append("    p = PerfManager()")
            self._code_lines.append("    p.add_perfdata(\"" + str(self.object_name) + "\", wait_time, " + repr(self.warning) + ", " + repr(self.critical) + ")")
        elif self.find is False:
            self._code_lines.append("    if wait_time == -1:")
            if self.timeout_exception is True:
                self._code_lines.append("        raise Exception(\"step " + str(self.object_name) + " timed out, execution time: " + str(self.timeout) + "\")")             
            else:
                self._code_lines.append("        print \"*WARN* step " + str(self.object_name) + " timed out, execution time: " + str(self.timeout) + "\"")
                self._code_lines.append("        return False")  
            #self._code_lines.append("        raise Exception(\"step " + str(self.object_name) + " timed out, execution time: " + str(self.timeout) + "\")")
 
        string_function_args = "    " + name + "_mouse_keyboard("
        
        args_range = range(1, self.args_number + 1)
        
        for arg_num in args_range:
            string_function_args = string_function_args + "arg" + str(arg_num) + ", " 
        
        if string_function_args.endswith(", "):
            string_function_args = string_function_args[:-2]
        string_function_args = string_function_args + ")"
        self._code_lines.append(string_function_args)
 
        """
        if self._main_text.click == True or self._main_text.doubleclick == True or self._main_text.rightclick == True or self._main_text.mousemove == True:
        
            self._code_lines.append("    main_text_pos = " + name + "_object.get_result(0)")  
        
            if mmanager_declared is False:
                self._code_lines.append("    m = MouseManager()")
                mmanager_declared = True
                
            self._code_lines.append("    time.sleep(2)")
                                
            if self._main_text.click == True:
                self._code_lines.append("    m.click(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2), 1)")
            elif self._main_text.doubleclick == True:
                self._code_lines.append("    m.click(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2), 1, 2)")
            elif self._main_text.rightclick == True:
                self._code_lines.append("    m.click(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2), 2)")
            elif self._main_text.mousemove == True:
                self._code_lines.append("    m.move(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2))")

                
        if self._main_text.sendkeys != "":
            if kmanager_declared is False:
                self._code_lines.append("    k  = KeyboardManager()")
                kmanager_declared = True
            keys = unicode(self._main_text.sendkeys, 'utf-8')
            self._code_lines.append("    time.sleep(2)")
            
            if self._main_text.sendkeys_quotes is True:
                self._code_lines.append("    k.send(\"" + keys + "\", encrypted=" + str(self._main_text.text_encrypted) + ")")
            else:
                self._code_lines.append("    k.send(" + keys + ", encrypted=" + str(self._main_text.text_encrypted) + ")")
            
        cnt = 0
        for sub_text in self._sub_texts_finder:
        
            if sub_text.height != 0 and sub_text.width !=0:
                if sub_text.click == True or sub_text.doubleclick == True or sub_text.rightclick == True or sub_text.mousemove == True:
            
                    self._code_lines.append("    sub_text_" + str(cnt) + "_pos = " + name + "_object.get_result(0, " + str(cnt) + ")")  
                
                    if mmanager_declared is False:
                        self._code_lines.append("    mouse = MouseManager()")
                        mmanager_declared = True
                    self._code_lines.append("    time.sleep(2)")
                                        
                    if sub_text.click == True:
                        self._code_lines.append("    m.click(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2), 1)")
                    elif sub_text.doubleclick == True:
                        self._code_lines.append("    m.click(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2), 1, 2)")
                    elif sub_text.rightclick == True:
                        self._code_lines.append("    m.click(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2), 2)")
                    elif sub_text.mousemove == True:
                        self._code_lines.append("    m.move(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2))")
                        
                if sub_text.sendkeys != "":
                    if kmanager_declared is False:
                        self._code_lines.append("    k  = KeyboardManager()")
                        kmanager_declared = True
                    keys = unicode(sub_text.sendkeys, 'utf-8')
                    self._code_lines.append("    time.sleep(2)")
                    
                    if sub_text.sendkeys_quotes is True:
                        self._code_lines.append("    k.send(\"" + keys + "\", encrypted=" + str(sub_text.text_encrypted) + ")")
                    else:
                        self._code_lines.append("    k.send(" + keys + ", encrypted=" + str(sub_text.text_encrypted) + ")")
                              
                                    
                cnt = cnt + 1
        """
        
        if self.timeout_exception is False:
            self._code_lines.append("    return True")
        self._code_lines.append("")
        self._code_lines.append("")

        #x = 2
        
        #tmp_array =  self._code_lines[:x] + ["aaaaaaaaa"] +  self._code_lines[x:]
        
        #self._code_lines = tmp_array

        """
        for element in self._code_lines:
            print element
        """ 
        
    def build_code_array(self):
    
        self.mouse_or_key_is_set = False
    
        kmanager_declared = False
        mmanager_declared = False
       
        if self._main_text is None:
            return
            
        self._code_lines = []
        self._code_lines_for_object_finder = []
            
        name = self.object_name
        
        if name == "":
            name = time.strftime("text_finder_%d_%m_%y_%H_%M_%S")
            self.object_name = name
            
        #self._code_lines.append("def " + name + "():")
        
        strcode = name + "_object = None" #TextFinder(\"" + name + "\")"
        self._code_lines.append(strcode)
        self._code_lines_for_object_finder.append(strcode)
        
        self._code_lines.append("")
        
        string_function_args = "def " + name + "_build_object("
        
        args_range = range(1, self.args_number + 1)
        
        for arg_num in args_range:
            string_function_args = string_function_args + "arg" + str(arg_num) + ", " 
        
        if string_function_args.endswith(", "):
            string_function_args = string_function_args[:-2]
        string_function_args = string_function_args + "):"
        self._code_lines.append(string_function_args)
        
            
        
        #strcode = "    text_finder = TextFinder(\"" + name + "\")"
        #self._code_lines.append(strcode)
        #self._code_lines_for_object_finder.append(strcode)
        
        roi_x = str(self._main_text.roi_x)
        roi_y = str(self._main_text.roi_y)
        roi_width = str(self._main_text.roi_width)
        roi_height = str(self._main_text.roi_height)
        
        self._code_lines.append("    global " + name + "_object")  
        self._code_lines.append("    " + name + "_object = TextFinder(\"" + name + "\")")
        
        text_to_find = ""
        
        if self._main_text.quotes_ocr is True:
            text_to_find = "\"" + unicode(self._main_text.text, "utf8") + "\""
        else:
            text_to_find = self._main_text.text + ".encode('utf8')"
        
        if self._main_text.whitelist == "'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ&:/-_\,+()*.=[]<>@":
            str1 = "    " + name + "_object.set_main_component({\"text\": " + text_to_find + ", \"lang\": \""  + self._main_text.lang + "\"},"
        else:
            str1 = "    " + name + "_object.set_main_component({\"text\": " + text_to_find + ", \"lang\": \""  + self._main_text.lang + "\"" + ", \"whitelist\": \"" + unicode(self._main_text.whitelist, "utf8") + "\"},"
            
        str2 ="                                   {\"roi_x\": " + roi_x + ", \"roi_y\": " + roi_y + ", \"roi_width\": " + roi_width + ", \"roi_height\": " + roi_height + "})"
            
        self._code_lines.append(str1)
        self._code_lines.append(str2)
        self._code_lines_for_object_finder.append(str1)
        self._code_lines_for_object_finder.append(str2)
        
        #self._code_lines.append("\n")
        
        cnt = 1
        for sub_text in self._sub_texts_finder:
            if sub_text.height != 0 and sub_text.width !=0:
            
                #sub_text.path = template_text_path + os.sep + "sub_text_" + str(cnt) + ".png"
                #sub_text.path = sub_text.path.replace("\\","\\\\")
            
                #roi_x = str(sub_text.roi_x - self._main_text.x)
                roi_x = str(sub_text.roi_x)
                roi_y = str(sub_text.roi_y)
                
                roi_width = str(sub_text.roi_width)
                roi_height = str(sub_text.roi_height)
                    
                text_to_find = ""
                if sub_text.quotes_ocr is True:
                    text_to_find = "\"" + unicode(sub_text.text, "utf8") + "\""
                else:
                    text_to_find = sub_text.text + ".encode('utf8')"
            
                #str1 = "    text_finder.add_sub_component({\"path\": \"" + sub_text.path + "\", \"threshold\":" + repr(sub_text.threshold) + "},"
                if sub_text.whitelist == "'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ&:/-_\,+()*.=[]<>@":
                    str1 = "    " + name + "_object.add_sub_component({\"text\": " + text_to_find + ", \"lang\": \"" + sub_text.lang + "\"},"
                else:
                    str1 = "    " + name + "_object.add_sub_component({\"text\": " + text_to_find + ", \"lang\": \"" + sub_text.lang + "\", \"whitelist\": \"" + unicode(sub_text.whitelist, "utf8") + "\"},"
                    
                
                str2 = "                                  {\"roi_x\": " + roi_x + ", \"roi_y\": " + roi_y + ", \"roi_width\": " + roi_width + ", \"roi_height\": " + roi_height + "})"
    
                self._code_lines.append(str1)
                self._code_lines.append(str2)
                self._code_lines_for_object_finder.append(str1)
                self._code_lines_for_object_finder.append(str2)
    
                #self._code_lines.append("\n")
                cnt = cnt + 1
        
        self._code_lines.append("")
        
        string_function_args = "def " + name + "_mouse_keyboard("
        
        args_range = range(1, self.args_number + 1)
        
        for arg_num in args_range:
            string_function_args = string_function_args + "arg" + str(arg_num) + ", " 
        
        if string_function_args.endswith(", "):
            string_function_args = string_function_args[:-2]
        string_function_args = string_function_args + "):"
        self._code_lines.append(string_function_args)
        
        self._code_lines.append("    global " + name + "_object")
        self._code_lines.append("    info_manager = InfoManager()")
        self._code_lines.append("    sleep_factor = info_manager.get_info(\"ACTIONS DELAY\")")  
        
        if self._main_text.click == True or self._main_text.doubleclick == True or self._main_text.rightclick == True or self._main_text.mousemove == True:
        
            self.mouse_or_key_is_set = True
        
            self._code_lines.append("    main_text_pos = " + name + "_object.get_result(0)")  
        
            if mmanager_declared is False:
                self._code_lines.append("    m = MouseManager()")
                mmanager_declared = True
                
            self._code_lines.append("    time.sleep(sleep_factor)")
            
            if self._main_text.x_offset is None and self._main_text.y_offset is None:             
                if self._main_text.click == True:
                    self._code_lines.append("    m.click(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2), 1)")
                elif self._main_text.doubleclick == True:
                    self._code_lines.append("    m.click(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2), 1, 2)")
                elif self._main_text.rightclick == True:
                    self._code_lines.append("    m.click(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2), 2)")
                elif self._main_text.mousemove == True:
                    self._code_lines.append("    m.move(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2))")
            else:
                if self._main_text.click == True:
                    self._code_lines.append("    m.click(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + "), 1)")
                elif self._main_text.doubleclick == True:
                    self._code_lines.append("    m.click(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + "), 1, 2)")
                elif self._main_text.rightclick == True:
                    self._code_lines.append("    m.click(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + "), 2)")
                elif self._main_text.mousemove == True:
                    self._code_lines.append("    m.move(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + "))")

                
        if self._main_text.sendkeys != "":
        
            self.mouse_or_key_is_set = True
        
            if kmanager_declared is False:
                self._code_lines.append("    k  = KeyboardManager()")
                kmanager_declared = True
            keys = unicode(self._main_text.sendkeys, 'utf-8')
            self._code_lines.append("    time.sleep(sleep_factor)")
            
            if self._main_text.sendkeys_quotes is True:
                self._code_lines.append("    k.send(\"" + keys + "\", encrypted=" + str(self._main_text.text_encrypted) + ")")
            else:
                self._code_lines.append("    k.send(" + keys + ", encrypted=" + str(self._main_text.text_encrypted) + ")")
            
        cnt = 0
        for sub_text in self._sub_texts_finder:
        
            if sub_text.height != 0 and sub_text.width !=0:
                if sub_text.click == True or sub_text.doubleclick == True or sub_text.rightclick == True or sub_text.mousemove == True:
                
                    self.mouse_or_key_is_set = True
            
                    self._code_lines.append("    sub_text_" + str(cnt) + "_pos = " + name + "_object.get_result(0, " + str(cnt) + ")")  
                
                    if mmanager_declared is False:
                        self._code_lines.append("    m = MouseManager()")
                        mmanager_declared = True
                    self._code_lines.append("    time.sleep(sleep_factor)")
                                      
                    if sub_text.x_offset is None and sub_text.y_offset is None:     
                        if sub_text.click == True:
                            self._code_lines.append("    m.click(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2), 1)")
                        elif sub_text.doubleclick == True:
                            self._code_lines.append("    m.click(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2), 1, 2)")
                        elif sub_text.rightclick == True:
                            self._code_lines.append("    m.click(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2), 2)")
                        elif sub_text.mousemove == True:
                            self._code_lines.append("    m.move(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2))")
                    else:
                        if sub_text.click == True:
                            self._code_lines.append("    m.click(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "), 1)")
                        elif sub_text.doubleclick == True:
                            self._code_lines.append("    m.click(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "), 1, 2)")
                        elif sub_text.rightclick == True:
                            self._code_lines.append("    m.click(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "), 2)")
                        elif sub_text.mousemove == True:
                            self._code_lines.append("    m.move(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "))")
                        
                         
                if sub_text.sendkeys != "":
                
                    self.mouse_or_key_is_set = True
                
                    if kmanager_declared is False:
                        self._code_lines.append("    k  = KeyboardManager()")
                        kmanager_declared = True
                    keys = unicode(sub_text.sendkeys, 'utf-8')
                    self._code_lines.append("    time.sleep(sleep_factor)")
                    
                    if sub_text.sendkeys_quotes is True:
                        self._code_lines.append("    k.send(\"" + keys + "\", encrypted=" + str(sub_text.text_encrypted) + ")")
                    else:
                        self._code_lines.append("    k.send(" + keys + ", encrypted=" + str(sub_text.text_encrypted) + ")")
                              
                                    
                cnt = cnt + 1
                
        #if kmanager_declared is False and mmanager_declared is False:
        #    self._code_lines.append("    pass")
        
        self._code_lines.append("")
        
        string_function_args = "def " + name + "("
        
        args_range = range(1, self.args_number + 1)
        
        for arg_num in args_range:
            string_function_args = string_function_args + "arg" + str(arg_num) + ", " 
        
        if string_function_args.endswith(", "):
            string_function_args = string_function_args[:-2]
        string_function_args = string_function_args + "):"
        self._code_lines.append(string_function_args)
        
        self._code_lines.append("    global " + name + "_object")  

        string_function_args = "    " + name + "_build_object("
        
        args_range = range(1, self.args_number + 1)
        
        for arg_num in args_range:
            string_function_args = string_function_args + "arg" + str(arg_num) + ", " 
        
        if string_function_args.endswith(", "):
            string_function_args = string_function_args[:-2]
        string_function_args = string_function_args + ")"
        self._code_lines.append(string_function_args)

        if self.find is True:  
            self._code_lines.append("    " + name + "_object.find()")
        elif self.wait is True or self.mouse_or_key_is_set is True:
            self._code_lines.append("    timeout = " + str(self.timeout))
            self._code_lines.append("    wait_time = " + name + "_object.wait(timeout)")
        elif self.wait_disapp is True:
            self._code_lines.append("    timeout = " + str(self.timeout))
            self._code_lines.append("    wait_time = " + name + "_object.wait_disappear(timeout)")
           
           
        if self.enable_performance is True and self.find is False:
            self._code_lines.append("    if wait_time == -1:")
            if self.timeout_exception is True:
                self._code_lines.append("        raise Exception(\"step " + str(self.object_name) + " timed out, execution time: " + str(self.timeout) + "\")")              
            else:
                self._code_lines.append("        print \"*WARN* step " + str(self.object_name) + " timed out, execution time: " + str(self.timeout) + "\"")
                self._code_lines.append("        return False")
            if self.wait_disapp is True and self.mouse_or_key_is_set is True:
                pass
            else:
                self._code_lines.append("    elif wait_time < " + repr(self.warning) + ":")
                self._code_lines.append("        print \"step " + self.object_name + " is ok, execution time:\", wait_time, \"sec.\"")
                self._code_lines.append("    elif wait_time < " + repr(self.critical) + ":")
                self._code_lines.append("        print \"*WARN* step " + str(self.object_name) + " has exceeded the performance warning threshold:\", wait_time, \"sec.\"")
                self._code_lines.append("    else:")
                self._code_lines.append("        print \"*WARN* step " + str(self.object_name) + " has exceeded the performance critical threshold:\", wait_time, \"sec.\"")

                self._code_lines.append("    p = PerfManager()")
                self._code_lines.append("    p.add_perfdata(\"" + str(self.object_name) + "\", wait_time, " + repr(self.warning) + ", " + repr(self.critical) + ")")
        elif self.find is False:
            self._code_lines.append("    if wait_time == -1:")
            if self.timeout_exception is True:
                self._code_lines.append("        raise Exception(\"step " + str(self.object_name) + " timed out, execution time: " + str(self.timeout) + "\")")             
            else:
                self._code_lines.append("        print \"*WARN* step " + str(self.object_name) + " timed out, execution time: " + str(self.timeout) + "\"")
                self._code_lines.append("        return False")  
            #self._code_lines.append("        raise Exception(\"step " + str(self.object_name) + " timed out, execution time: " + str(self.timeout) + "\")")
 
        string_function_args = "    " + name + "_mouse_keyboard("
        
        args_range = range(1, self.args_number + 1)
        
        for arg_num in args_range:
            string_function_args = string_function_args + "arg" + str(arg_num) + ", " 
        
        if string_function_args.endswith(", "):
            string_function_args = string_function_args[:-2]
        string_function_args = string_function_args + ")"
        self._code_lines.append(string_function_args)
 
        """
        if self._main_text.click == True or self._main_text.doubleclick == True or self._main_text.rightclick == True or self._main_text.mousemove == True:
        
            self._code_lines.append("    main_text_pos = " + name + "_object.get_result(0)")  
        
            if mmanager_declared is False:
                self._code_lines.append("    m = MouseManager()")
                mmanager_declared = True
                
            self._code_lines.append("    time.sleep(2)")
                                
            if self._main_text.click == True:
                self._code_lines.append("    m.click(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2), 1)")
            elif self._main_text.doubleclick == True:
                self._code_lines.append("    m.click(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2), 1, 2)")
            elif self._main_text.rightclick == True:
                self._code_lines.append("    m.click(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2), 2)")
            elif self._main_text.mousemove == True:
                self._code_lines.append("    m.move(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2))")

                
        if self._main_text.sendkeys != "":
            if kmanager_declared is False:
                self._code_lines.append("    k  = KeyboardManager()")
                kmanager_declared = True
            keys = unicode(self._main_text.sendkeys, 'utf-8')
            self._code_lines.append("    time.sleep(2)")
            
            if self._main_text.sendkeys_quotes is True:
                self._code_lines.append("    k.send(\"" + keys + "\", encrypted=" + str(self._main_text.text_encrypted) + ")")
            else:
                self._code_lines.append("    k.send(" + keys + ", encrypted=" + str(self._main_text.text_encrypted) + ")")
            
        cnt = 0
        for sub_text in self._sub_texts_finder:
        
            if sub_text.height != 0 and sub_text.width !=0:
                if sub_text.click == True or sub_text.doubleclick == True or sub_text.rightclick == True or sub_text.mousemove == True:
            
                    self._code_lines.append("    sub_text_" + str(cnt) + "_pos = " + name + "_object.get_result(0, " + str(cnt) + ")")  
                
                    if mmanager_declared is False:
                        self._code_lines.append("    mouse = MouseManager()")
                        mmanager_declared = True
                    self._code_lines.append("    time.sleep(2)")
                                        
                    if sub_text.click == True:
                        self._code_lines.append("    m.click(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2), 1)")
                    elif sub_text.doubleclick == True:
                        self._code_lines.append("    m.click(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2), 1, 2)")
                    elif sub_text.rightclick == True:
                        self._code_lines.append("    m.click(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2), 2)")
                    elif sub_text.mousemove == True:
                        self._code_lines.append("    m.move(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2))")
                        
                if sub_text.sendkeys != "":
                    if kmanager_declared is False:
                        self._code_lines.append("    k  = KeyboardManager()")
                        kmanager_declared = True
                    keys = unicode(sub_text.sendkeys, 'utf-8')
                    self._code_lines.append("    time.sleep(2)")
                    
                    if sub_text.sendkeys_quotes is True:
                        self._code_lines.append("    k.send(\"" + keys + "\", encrypted=" + str(sub_text.text_encrypted) + ")")
                    else:
                        self._code_lines.append("    k.send(" + keys + ", encrypted=" + str(sub_text.text_encrypted) + ")")
                              
                                    
                cnt = cnt + 1
        """
        
        if self.wait_disapp is True and self.mouse_or_key_is_set is True:
            self._code_lines.append("    timeout = timeout - wait_time")
            self._code_lines.append("    wait_time_disappear = " + name + "_object.wait_disappear(timeout)")
            if self.enable_performance is True and self.find is False:
                self._code_lines.append("    if wait_time_disappear == -1:")
                if self.timeout_exception is True:
                    self._code_lines.append("        raise Exception(\"step " + str(self.object_name) + " timed out, execution time: " + str(self.timeout) + "\")")             
                else:
                    self._code_lines.append("        print \"*WARN* step " + str(self.object_name) + " timed out, execution time: " + str(self.timeout) + "\"")
                    self._code_lines.append("        return False")
                self._code_lines.append("    elif wait_time + wait_time_disappear < " + repr(self.warning) + ":")
                self._code_lines.append("        print \"step " + self.object_name + " is ok, execution time:\", wait_time + wait_time_disappear, \"sec.\"")
                self._code_lines.append("    elif  wait_time + wait_time_disappear < " + repr(self.critical) + ":")
                self._code_lines.append("        print \"*WARN* step " + str(self.object_name) + " has exceeded the performance warning threshold:\", wait_time + wait_time_disappear, \"sec.\"")
                self._code_lines.append("    else:")
                self._code_lines.append("        print \"*WARN* step " + str(self.object_name) + " has exceeded the performance critical threshold:\", wait_time + wait_time_disappear, \"sec.\"")
                self._code_lines.append("    p = PerfManager()")
                self._code_lines.append("    p.add_perfdata(\"" + str(self.object_name) + "\", wait_time + wait_time_disappear, " + repr(self.warning) + ", " + repr(self.critical) + ")")
            elif self.find is False:
                self._code_lines.append("    if wait_time_disappear == -1:")
                if self.timeout_exception is True:
                    self._code_lines.append("        raise Exception(\"step " + str(self.object_name) + " timed out, execution time: " + str(self.timeout) + "\")")             
                else:
                    self._code_lines.append("        print \"*WARN* step " + str(self.object_name) + " timed out, execution time: " + str(self.timeout) + "\"")
                    self._code_lines.append("        return False")  
                #self._code_lines.append("        raise Exception(\"step " + str(self.object_name) + " timed out, execution time: " + str(self.timeout) + "\")")
            
            
        
        if self.timeout_exception is False:
            self._code_lines.append("    return True")
        self._code_lines.append("")
        self._code_lines.append("")

        #x = 2
        
        #tmp_array =  self._code_lines[:x] + ["aaaaaaaaa"] +  self._code_lines[x:]
        
        #self._code_lines = tmp_array

        """
        for element in self._code_lines:
            print element
        """ 
  
    def build_xml(self):
        
        if self._main_text is None:
            return

        name = str(self.object_name)
        
        if name == "":
            name = time.strftime("text_finder_%d_%m_%y_%H_%M_%S")
            self.object_name = name
        
        root = ET.Element("text_finder")
        root.set("name", name)
        root.set("find", str(self.find))
        root.set("wait", str(self.wait))
        root.set("wait_disapp", str(self.wait_disapp))
        root.set("timeout", str(self.timeout))
        root.set("timeout_exception", str(self.timeout_exception))
        root.set("enable_performance", str(self.enable_performance))
        root.set("warning_value", repr(self.warning))
        root.set("critical_value", repr(self.critical))
        root.set("args", str(self.args_number))

        main_text_node = ET.SubElement(root, "main_text")

        x_node = ET.SubElement(main_text_node, "x")
        #x_node.set("name", "blah")
        x_node.text = str(self._main_text.x)
        
        y_node = ET.SubElement(main_text_node, "y")
        y_node.text = str(self._main_text.y)
        
        width_node = ET.SubElement(main_text_node, "width")
        width_node.text = str(self._main_text.width)
        
        height_node = ET.SubElement(main_text_node, "height")
        height_node.text = str(self._main_text.height)
        
        text_node = ET.SubElement(main_text_node, "text")
        text_node.set("quotes", str(self._main_text.quotes_ocr))
        text_node.append(ET.Comment(' --><![CDATA[' + unicode(self._main_text.text.replace(']]>', ']]]]><![CDATA[>'), 'utf-8') + ']]><!-- '))
        #text_node.text = str(self._main_text.text)
        
        lang_node = ET.SubElement(main_text_node, "lang")
        lang_node.text = str(self._main_text.lang)
        
        whitelist_node = ET.SubElement(main_text_node, "whitelist")
        whitelist_node.append(ET.Comment(' --><![CDATA[' + unicode(self._main_text.whitelist.replace(']]>', ']]]]><![CDATA[>'), 'utf-8') + ']]><!-- '))
        #whitelist_node.text = str(self._main_text.whitelist)
        
        roi_x_node = ET.SubElement(main_text_node, "roi_x")
        roi_x_node.text = str(self._main_text.roi_x)

        roi_y_node = ET.SubElement(main_text_node, "roi_y")
        roi_y_node.text = str(self._main_text.roi_y)

        roi_width_node = ET.SubElement(main_text_node, "roi_width")
        roi_width_node.text = str(self._main_text.roi_width)

        roi_height_node = ET.SubElement(main_text_node, "roi_height")
        roi_height_node.text = str(self._main_text.roi_height)
        
        """
        find_node = ET.SubElement(main_text_node, "find")
        find_node.text = str(self.find)
        
        wait_node = ET.SubElement(main_text_node, "wait")
        wait_node.text = str(self.wait)
        
        timeout_node = ET.SubElement(main_text_node, "timeout")
        timeout_node.text = str(self.timeout)
        """
        
        click_node = ET.SubElement(main_text_node, "click")
        click_node.text = str(self._main_text.click)

        doubleclick_node = ET.SubElement(main_text_node, "doubleclick")
        doubleclick_node.text = str(self._main_text.doubleclick)
        
        rightclick_node = ET.SubElement(main_text_node, "rightclick")
        rightclick_node.text = str(self._main_text.rightclick)
        
        mousemove_node = ET.SubElement(main_text_node, "mousemove")
        mousemove_node.text = str(self._main_text.mousemove)
        
        x_offset_node = ET.SubElement(main_text_node, "x_offset")
        x_offset_node.text = str(self._main_text.x_offset)
        
        y_offset_node = ET.SubElement(main_text_node, "y_offset")
        y_offset_node.text = str(self._main_text.y_offset)

        sendkeys_node = ET.SubElement(main_text_node, "sendkeys")
        
        sendkeys_node.set("encrypted", str(self._main_text.text_encrypted))
        sendkeys_node.set("quotes", str(self._main_text.sendkeys_quotes))
        
        #print self._main_text.sendkeys
        
        sendkey_text = unicode(self._main_text.sendkeys, 'utf-8')
        
        #print
        
        sendkeys_node.append(ET.Comment(' --><![CDATA[' + sendkey_text.replace(']]>', ']]]]><![CDATA[>') + ']]><!-- '))
        #sendkeys_node.text = unicode(self._main_text.sendkeys, 'utf-8')

    
        #tree.write("filename.xml")

        height = str(self._main_text.height)
        width = str(self._main_text.width)
        
        sub_texts_root = ET.SubElement(root, "sub_texts")
        
        cnt = 1
        for sub_text in self._sub_texts_finder:
            if sub_text.height != 0 and sub_text.width !=0:
            
                sub_text_node = ET.SubElement(sub_texts_root, "sub_text") #ET.SubElement(sub_texts_root, "sub_text_" + str(cnt))
                sub_text_node.set("id", str(cnt))
            
                x_node = ET.SubElement(sub_text_node, "x")
                #x_node.set("name", "blah")
                x_node.text = str(sub_text.x)
                
                y_node = ET.SubElement(sub_text_node, "y")
                y_node.text = str(sub_text.y)
                
                width_node = ET.SubElement(sub_text_node, "width")
                width_node.text = str(sub_text.width)
                
                height_node = ET.SubElement(sub_text_node, "height")
                height_node.text = str(sub_text.height)
                
                #threshold_node = ET.SubElement(sub_text_node, "threshold")
                #threshold_node.text = repr(sub_text.threshold)
                
                text_node = ET.SubElement(sub_text_node, "text")
                text_node.set("quotes", str(sub_text.quotes_ocr))
                
                text_node.append(ET.Comment(' --><![CDATA[' + unicode(sub_text.text.replace(']]>', ']]]]><![CDATA[>'), 'utf-8') + ']]><!-- '))
                #text_node.text = str(sub_text.text)

                lang_node = ET.SubElement(sub_text_node, "lang")
                lang_node.text = str(sub_text.lang)

                whitelist_node = ET.SubElement(sub_text_node, "whitelist")
                whitelist_node.append(ET.Comment(' --><![CDATA[' + unicode(sub_text.whitelist.replace(']]>', ']]]]><![CDATA[>'), 'utf-8') + ']]><!-- '))
                
                #whitelist_node.text = str(sub_text.whitelist)
                
                roi_x_node = ET.SubElement(sub_text_node, "roi_x")
                roi_x_node.text = str(sub_text.roi_x)
                
                roi_y_node = ET.SubElement(sub_text_node, "roi_y")
                roi_y_node.text = str(sub_text.roi_y)
                
                roi_width_node = ET.SubElement(sub_text_node, "roi_width")
                roi_width_node.text = str(sub_text.roi_width)
                
                roi_height_node = ET.SubElement(sub_text_node, "roi_height")
                roi_height_node.text = str(sub_text.roi_height)
                
                click_node = ET.SubElement(sub_text_node, "click")
                click_node.text = str(sub_text.click)
                
                doubleclick_node = ET.SubElement(sub_text_node, "doubleclick")
                doubleclick_node.text = str(sub_text.doubleclick)
                
                rightclick_node = ET.SubElement(sub_text_node, "rightclick")
                rightclick_node.text = str(sub_text.rightclick)

                mousemove_node = ET.SubElement(sub_text_node, "mousemove")
                mousemove_node.text = str(sub_text.mousemove)
                
                x_offset_node = ET.SubElement(sub_text_node, "x_offset")
                x_offset_node.text = str(sub_text.x_offset)

                y_offset_node = ET.SubElement(sub_text_node, "y_offset")
                y_offset_node.text = str(sub_text.y_offset)
                
                sendkeys_node = ET.SubElement(sub_text_node, "sendkeys")
                sendkeys_node.set("encrypted", str(sub_text.text_encrypted))
                sendkeys_node.set("quotes", str(sub_text.sendkeys_quotes))
                #sendkeys_node.text = unicode(sub_text.sendkeys, 'utf-8')
                sendkeys_node.append(ET.Comment(' --><![CDATA[' + unicode(sub_text.sendkeys.replace(']]>', ']]]]><![CDATA[>'), 'utf-8') + ']]><!-- '))
                
                cnt = cnt + 1
        
        code_blocks_root = ET.SubElement(root, "code_blocks")
        for block in self._code_blocks:
            block_start_line = block[0]
            block_text = block[1]
            block_end_line = block[2]
           # block_text = unicode(block_text, "utf-8")
            code_block = ET.SubElement(code_blocks_root, "code_block") #ET.SubElement(sub_texts_root, "sub_text_" + str(cnt))
            #code_block.set("id", str(block_start_line) + "_" + str(block_end_line))
            
            start_line_node = ET.SubElement(code_block, "start_line")
            start_line_node.text = str(block_start_line)
            
            
            """
            #cdata = CDATA("<<<<<sender")
            data = block_text
            code_block.append(ET.Comment(' --><![CDATA[' + unicode(data.replace(']]>', ']]]]><![CDATA[>'), 'utf-8') + ']]><!-- '))
            #print unicode(data, 'utf-8')
            #text_node = ET.SubElement(code_block, "file")
            block_file_name = self._path + "\\code_blocks\\" + str(block_start_line) + "_" + str(block_end_line) + ".txt"
            """
            
            end_line_node = ET.SubElement(code_block, "end_line")
            end_line_node.text = str(block_end_line)
            
            code_node = ET.SubElement(code_block, "code")
            code_node.append(ET.Comment(' --><![CDATA[' + unicode(block_text.replace(']]>', ']]]]><![CDATA[>'), 'utf-8') + ']]><!-- '))
            #code_node.text = str(block_start_line)
            
            """
            if not os.path.exists(self._path + "\\code_blocks\\"):
                os.makedirs(self._path + "\\code_blocks\\")
            #text_node.text = block_file_name
            block_text = unicode(block_text, 'utf-8')
            block_file = codecs.open(block_file_name, 'w', 'utf-8')
            block_file.write(block_text)
            block_file.close()            
            """
            
        tree = ET.ElementTree(root)
        
        #rough_string = ET.tostring(root, 'utf-8')
        #reparsed = minidom.parseString(rough_string)
        #str_xml = reparsed.toprettyxml(indent="\t")
        
        if not os.path.exists(self._path):
            os.makedirs(self._path)
            
        python_file = open(self._path + os.sep + self.object_name + "_TextFinder.xml", 'w')
        tree.write(python_file, encoding='utf-8', xml_declaration=True) 
        #python_file.write(rough_string)        
        python_file.close()
        
        
        """
        python_file.write("def search_on_google():" + "\n")
        python_file.write("    rect = RectFinder(\"test\")" + "\n")
        python_file.write("    rect.set_main_rect({\"height\": " + height + ", \"width\": " + width + ", \"height_tolerance\": 15, \"width_tolerance\": 15}," + "\n")
        
        for sub_text in self._sub_texts_finder:
            if sub_text.height != 0 and sub_text.width !=0:
            
                x = str(sub_text.x - self._main_text.x)
                y = str(sub_text.y - self._main_text.y)
                height = str(sub_text.height)
                width = str(sub_text.width)
                
                python_file.write("    rect.add_sub_text({\"height\": " + height + ", \"width\": " + width + ", \"height_tolerance\": 15, \"width_tolerance\": 15}," + "\n")
                python_file.write("                      {\"roi_x\": " + x + ", \"roi_y\": " + y + ", \"roi_width\": " + width + ", \"roi_height\": " + height + "})" + "\n")
        
        """
        python_file.close()
        
    def build_code_blocks(self):
        for block in self.parent._code_blocks:
            python_file = open('c:\\alan\\code.txt', 'w')

    def build_objects(self):
        
        #print self._path + "\\text_finder.xml"
        
        try:
            filehandler = open(self._path + os.sep + self._xml_name,"r")
        except:
            return
            
        doc = minidom.parse(filehandler)
        #data_root = raw_data.getroot()
        
        root_node = doc.getElementsByTagName("text_finder")[0]
        
        self._main_text = MainTextForGui()
        
        main_text_node = doc.getElementsByTagName("main_text")[0]
        #self.object_name = main_text_node.getElementsByTagName("name")[0].firstChild.nodeValue
        
        self.object_name = root_node.attributes["name"].value
        #self.find = main_text_node.attributes["find"].value
        #self.wait = main_text_node.attributes["wait"].value
        self.timeout = int(root_node.attributes["timeout"].value)
        self.args_number = int(root_node.attributes["args"].value)
        
        if root_node.attributes["timeout_exception"].value == "True":
            self.timeout_exception = True
        else:
            self.timeout_exception = False
        
        self._main_text.x = int(main_text_node.getElementsByTagName("x")[0].firstChild.nodeValue)
        self._main_text.y = int(main_text_node.getElementsByTagName("y")[0].firstChild.nodeValue)
        self._main_text.height = int(main_text_node.getElementsByTagName("height")[0].firstChild.nodeValue)
        self._main_text.width = int(main_text_node.getElementsByTagName("width")[0].firstChild.nodeValue)
        self._main_text.height = int(main_text_node.getElementsByTagName("height")[0].firstChild.nodeValue)
        
        #self._main_text.text = main_text_node.getElementsByTagName("text")[0].firstChild.nodeValue
        
        try:
            #self._main_text.text = main_text_node.getElementsByTagName("text")[0].toxml()
            
            if main_text_node.getElementsByTagName("text")[0].attributes["quotes"].value == "True":
                self._main_text.quotes_ocr = True
            else:
                self._main_text.quotes_ocr = False
            
            self._main_text.text = main_text_node.getElementsByTagName("text")[0].toxml()
            self._main_text.text = self._main_text.text.replace("<text quotes=\"False\"><!-- -->","")
            self._main_text.text = self._main_text.text.replace("<text quotes=\"True\"><!-- -->","")
            self._main_text.text = self._main_text.text.replace("<!-- --></text>","")
            self._main_text.text = self._main_text.text.replace("<![CDATA[","")
            self._main_text.text = self._main_text.text.replace("]]>","")
            self._main_text.text = self._main_text.text.encode('utf-8')
        except AttributeError:
            self._main_text.text = ''.encode('utf-8')
        
        self._main_text.lang = main_text_node.getElementsByTagName("lang")[0].firstChild.nodeValue
        #self._main_text.whitelist = main_text_node.getElementsByTagName("whitelist")[0].firstChild.nodeValue
        
        try:
            self._main_text.whitelist = main_text_node.getElementsByTagName("whitelist")[0].toxml()
            self._main_text.whitelist = self._main_text.whitelist.replace("<whitelist><!-- -->","")
            self._main_text.whitelist = self._main_text.whitelist.replace("<!-- --></whitelist>","")
            self._main_text.whitelist = self._main_text.whitelist.replace("<![CDATA[","")
            self._main_text.whitelist = self._main_text.whitelist.replace("]]>","")
            self._main_text.whitelist = self._main_text.whitelist.encode('utf-8')
        except AttributeError:
            self._main_text.whitelist = ''.encode('utf-8')
        
        self._main_text.roi_x = int(main_text_node.getElementsByTagName("roi_x")[0].firstChild.nodeValue)
        self._main_text.roi_y = int(main_text_node.getElementsByTagName("roi_y")[0].firstChild.nodeValue)
        self._main_text.roi_width = int(main_text_node.getElementsByTagName("roi_width")[0].firstChild.nodeValue)
        self._main_text.roi_height = int(main_text_node.getElementsByTagName("roi_height")[0].firstChild.nodeValue)
        
        if "True" in root_node.attributes["find"].value: #main_text_node.getElementsByTagName("find")[0].firstChild.nodeValue:
            self.find = True
        else:
            self.find = False    
            
        if "True" in root_node.attributes["wait"].value: #main_text_node.getElementsByTagName("wait")[0].firstChild.nodeValue:
            self.wait = True
        else:
            self.wait = False    
            
        try:
            if "True" in root_node.attributes["wait_disapp"].value: #main_template_node.getElementsByTagName("wait")[0].firstChild.nodeValue:
                self.wait_disapp = True
            else:
                self.wait_disapp = False
        except:
            self.wait_disapp = False
            
        if "True" in main_text_node.getElementsByTagName("click")[0].firstChild.nodeValue:
            self._main_text.click = True
            self.mouse_or_key_is_set = True
        else:
            self._main_text.click = False
            
        if "True" in main_text_node.getElementsByTagName("doubleclick")[0].firstChild.nodeValue:
            self._main_text.doubleclick = True
            self.mouse_or_key_is_set = True
        else:
            self._main_text.doubleclick = False
            
        if "True" in main_text_node.getElementsByTagName("rightclick")[0].firstChild.nodeValue:
            self._main_text.rightclick = True
            self.mouse_or_key_is_set = True
        else:
            self._main_text.rightclick = False
            
        if "True" in main_text_node.getElementsByTagName("mousemove")[0].firstChild.nodeValue:
            self._main_text.mousemove = True
            self.mouse_or_key_is_set = True
        else:
            self._main_text.mousemove = False
            
        try:
            if "None" in main_text_node.getElementsByTagName("x_offset")[0].firstChild.nodeValue:
                self._main_text.x_offset = None
            else:
                self._main_text.x_offset = int(main_text_node.getElementsByTagName("x_offset")[0].firstChild.nodeValue)
        except:
            pass
            
        try:
            if "None" in main_text_node.getElementsByTagName("y_offset")[0].firstChild.nodeValue:
                self._main_text.y_offset = None
            else:
                self._main_text.y_offset = int(main_text_node.getElementsByTagName("y_offset")[0].firstChild.nodeValue)
        except:
            pass
            
        if "True" in root_node.attributes["enable_performance"].value:
            self.enable_performance = True
        else:
            self.enable_performance = False
            
        self.warning = float(root_node.attributes["warning_value"].value)
            
        self.critical = float(root_node.attributes["critical_value"].value)
        
        if main_text_node.getElementsByTagName("sendkeys")[0].attributes["encrypted"].value == "True":
            self._main_text.text_encrypted = True
        else:
            self._main_text.text_encrypted = False
            
        if main_text_node.getElementsByTagName("sendkeys")[0].attributes["quotes"].value == "True":
            self._main_text.sendkeys_quotes = True
        else:
            self._main_text.sendkeys_quotes = False
        
        try:
            self._main_text.sendkeys = main_text_node.getElementsByTagName("sendkeys")[0].toxml()
            self._main_text.sendkeys = self._main_text.sendkeys.replace("<sendkeys encrypted=\"False\" quotes=\"False\"><!-- -->","")
            self._main_text.sendkeys = self._main_text.sendkeys.replace("<sendkeys encrypted=\"True\" quotes=\"True\"><!-- -->","")
            self._main_text.sendkeys = self._main_text.sendkeys.replace("<sendkeys encrypted=\"True\" quotes=\"False\"><!-- -->","")
            self._main_text.sendkeys = self._main_text.sendkeys.replace("<sendkeys encrypted=\"False\" quotes=\"True\"><!-- -->","")
            self._main_text.sendkeys = self._main_text.sendkeys.replace("<!-- --></sendkeys>","")
            self._main_text.sendkeys = self._main_text.sendkeys.replace("<![CDATA[","")
            self._main_text.sendkeys = self._main_text.sendkeys.replace("]]>","")
            self._main_text.sendkeys = self._main_text.sendkeys.encode('utf-8')
            
            if self._main_text.sendkeys != "":
                self.mouse_or_key_is_set = True
        except AttributeError:
            self._main_text.sendkeys = ''.encode('utf-8')
        
        self.__flag_capturing_main_text_rect = False
        self.__flag_capturing_sub_text_rect_roi = True
                
        sub_text_nodes = doc.getElementsByTagName("sub_text")
        
        #print len(sub_text_nodes)

        for sub_text_node in sub_text_nodes:

            sub_text_obj = SubTextForGui()
            
            #print int(sub_text_node.getElementsByTagName("x")[0].firstChild.nodeValue)
        
            #sub_text_node = doc.getElementsByTagName("main_rect")[0]
            #sub_text_obj.name = sub_text_node.getElementsByTagName("name")[0].firstChild.nodeValue
            sub_text_obj.x = int(sub_text_node.getElementsByTagName("x")[0].firstChild.nodeValue)
            sub_text_obj.y = int(sub_text_node.getElementsByTagName("y")[0].firstChild.nodeValue)
            sub_text_obj.height = int(sub_text_node.getElementsByTagName("height")[0].firstChild.nodeValue)
            sub_text_obj.width = int(sub_text_node.getElementsByTagName("width")[0].firstChild.nodeValue)

            #sub_text_obj.text = sub_text_node.getElementsByTagName("text")[0].firstChild.nodeValue
            
            try:
                #self._main_text.text = main_text_node.getElementsByTagName("text")[0].toxml()
            
                if sub_text_node.getElementsByTagName("text")[0].attributes["quotes"].value == "True":
                    sub_text_obj.quotes_ocr = True
                else:
                    sub_text_obj.quotes_ocr = False
                
                sub_text_obj.text = sub_text_node.getElementsByTagName("text")[0].toxml()
                sub_text_obj.text = sub_text_obj.text.replace("<text quotes=\"False\"><!-- -->","")
                sub_text_obj.text = sub_text_obj.text.replace("<text quotes=\"True\"><!-- -->","")
                sub_text_obj.text = sub_text_obj.text.replace("<!-- --></text>","")
                sub_text_obj.text = sub_text_obj.text.replace("<![CDATA[","")
                sub_text_obj.text = sub_text_obj.text.replace("]]>","")
                sub_text_obj.text = sub_text_obj.text.encode('utf-8')
            except AttributeError:
                sub_text_obj.text = ''.encode('utf-8')
            
            sub_text_obj.lang = sub_text_node.getElementsByTagName("lang")[0].firstChild.nodeValue
            #sub_text_obj.whitelist = sub_text_node.getElementsByTagName("whitelist")[0].firstChild.nodeValue
            
            try:
                sub_text_obj.whitelist = sub_text_node.getElementsByTagName("whitelist")[0].toxml()                
                sub_text_obj.whitelist = sub_text_obj.whitelist.replace("<whitelist><!-- -->","")
                sub_text_obj.whitelist = sub_text_obj.whitelist.replace("<!-- --></whitelist>","")
                sub_text_obj.whitelist = sub_text_obj.whitelist.replace("<![CDATA[","")
                sub_text_obj.whitelist = sub_text_obj.whitelist.replace("]]>","")
                sub_text_obj.whitelist = sub_text_obj.whitelist.encode('utf-8')
            except AttributeError:
                sub_text_obj.whitelist = ''.encode('utf-8')
                
            sub_text_obj.roi_x = int(sub_text_node.getElementsByTagName("roi_x")[0].firstChild.nodeValue)
            sub_text_obj.roi_y = int(sub_text_node.getElementsByTagName("roi_y")[0].firstChild.nodeValue)
            sub_text_obj.roi_width = int(sub_text_node.getElementsByTagName("roi_width")[0].firstChild.nodeValue)
            sub_text_obj.roi_height = int(sub_text_node.getElementsByTagName("roi_height")[0].firstChild.nodeValue)
                
            if "True" in sub_text_node.getElementsByTagName("click")[0].firstChild.nodeValue:
                sub_text_obj.click = True
                self.mouse_or_key_is_set = True
            else:
                sub_text_obj.click = False
                
            if "True" in sub_text_node.getElementsByTagName("doubleclick")[0].firstChild.nodeValue:
                sub_text_obj.doubleclick = True
                self.mouse_or_key_is_set = True
            else:
                sub_text_obj.doubleclick = False
                
            if "True" in sub_text_node.getElementsByTagName("rightclick")[0].firstChild.nodeValue:
                sub_text_obj.rightclick = True
                self.mouse_or_key_is_set = True
            else:
                sub_text_obj.rightclick = False
                
            if "True" in sub_text_node.getElementsByTagName("mousemove")[0].firstChild.nodeValue:
                sub_text_obj.mousemove = True
                self.mouse_or_key_is_set = True
            else:
                sub_text_obj.mousemove = False
            
            try:
                if "None" in sub_text_node.getElementsByTagName("x_offset")[0].firstChild.nodeValue:
                    sub_text_obj.x_offset = None
                else:
                    sub_text_obj.x_offset = int(sub_text_node.getElementsByTagName("x_offset")[0].firstChild.nodeValue)
            except:
                pass
                    
            try:
                if "None" in sub_text_node.getElementsByTagName("y_offset")[0].firstChild.nodeValue:
                    sub_text_obj.y_offset = None
                else:
                    sub_text_obj.y_offset = int(sub_text_node.getElementsByTagName("y_offset")[0].firstChild.nodeValue)
            except:
                pass
                
                
            if sub_text_node.getElementsByTagName("sendkeys")[0].attributes["encrypted"].value == "True":
                sub_text_obj.text_encrypted = True
            else:
                sub_text_obj.text_encrypted = False
                
            if sub_text_node.getElementsByTagName("sendkeys")[0].attributes["quotes"].value == "True":
                sub_text_obj.sendkeys_quotes = True
            else:
                sub_text_obj.sendkeys_quotes = False
            
            try:
                sub_text_obj.sendkeys = sub_text_node.getElementsByTagName("sendkeys")[0].toxml()                
                sub_text_obj.sendkeys = sub_text_obj.sendkeys.replace("<sendkeys encrypted=\"False\" quotes=\"False\"><!-- -->","")
                sub_text_obj.sendkeys = sub_text_obj.sendkeys.replace("<sendkeys encrypted=\"True\" quotes=\"True\"><!-- -->","")
                sub_text_obj.sendkeys = sub_text_obj.sendkeys.replace("<sendkeys encrypted=\"True\" quotes=\"False\"><!-- -->","")
                sub_text_obj.sendkeys = sub_text_obj.sendkeys.replace("<sendkeys encrypted=\"False\" quotes=\"True\"><!-- -->","")
                sub_text_obj.sendkeys = sub_text_obj.sendkeys.replace("<!-- --></sendkeys>","")
                sub_text_obj.sendkeys = sub_text_obj.sendkeys.replace("<![CDATA[","")
                sub_text_obj.sendkeys = sub_text_obj.sendkeys.replace("]]>","")
                sub_text_obj.sendkeys = sub_text_obj.sendkeys.encode('utf-8')
                
                if sub_text_obj.sendkeys != "":
                    self.mouse_or_key_is_set = True
            except AttributeError:
                sub_text_obj.sendkeys = ''.encode('utf-8')
                
            self._sub_texts_finder.append(sub_text_obj)
            
        sub_block_nodes = doc.getElementsByTagName("code_block")
        
        #print len(sub_text_nodes)

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
            
        self._main_text.mouse_or_key_is_set = self.mouse_or_key_is_set

    def build_perf_data_xml(self):
    
        filename = self._path + os.sep + "perf_data.xml"

        if os.path.exists(filename):
            perf_is_present = False
            
            doc = minidom.parse(filename)
            root_node = doc.getElementsByTagName("performance")[0]
            
            items_node = doc.getElementsByTagName("perfdata")
            
            for item_node in items_node:
                name = item_node.getElementsByTagName("name")[0].firstChild.nodeValue
                if name == self.object_name and self.enable_performance is False:
                    root_node.removeChild(item_node)
                elif name == self.object_name:
                    perf_is_present = True
                    
            if perf_is_present is False and self.enable_performance is True:
                item = doc.createElement("perfdata")
                
                name = doc.createElement("name")
                txt = doc.createTextNode(self.object_name)
                name.appendChild(txt)
                item.appendChild(name)

                warning = doc.createElement("warning")
                txt = doc.createTextNode(str(self.warning))
                warning.appendChild(txt)
                item.appendChild(warning)
                
                critical = doc.createElement("critical")
                txt = doc.createTextNode(str(self.critical))
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
            name_node.text = str(self.object_name)
            
            warning_node = ET.SubElement(main_item_node, "warning")
            warning_node.text = str(self.warning)
            
            critical_node = ET.SubElement(main_item_node, "critical")
            critical_node.text = str(self.critical)
            
            tree = ET.ElementTree(root)
            python_file = open(filename, 'w')
            tree.write(python_file, encoding='utf-8', xml_declaration=True) 
            #python_file.write(rough_string)        
        python_file.close()  
            
class MainTextForGui:
    
    def __init__(self):
        self.name = ""
        self.x = 0
        self.y = 0
        self.height = 0
        self.width = 0
        self.show = True
        #self.threshold = 0.7
        self.text = ""
        self.quotes_ocr = True
        self.whitelist = "'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ&:/-_\,+()*.=[]<>@"
        self.lang = "eng"
        self.path = ""
        self.roi_x = 0
        self.roi_y = 0
        self.roi_height = 0
        self.roi_width = 0
        self.deleted_x = None
        self.deleted_y = None
        self.deleted_height = None
        self.deleted_width = None
        self.click = False
        self.rightclick = False
        self.mousemove = False
        self.doubleclick = False
        self.xy_offset = None
        self.x_offset = None
        self.y_offset = None
        self.wait = True
        self.wait_disapp = False
        self.find = False
        self.args_number = 0
        self.timeout = 60
        self.timeout_exception = True
        self.sendkeys = ""
        self.mouse_or_key_is_set = False
        self.sendkeys_quotes = True
        self.text_encrypted = False
        self.enable_performance = True
        self.warning = 15.00
        self.critical = 40.00
        
class SubTextForGui:
    
    def __init__(self):
        self.x = 0
        self.y = 0
        self.height = 0
        self.width = 0
        #self.threshold = 0.7
        self.text = ""
        self.quotes_ocr = True
        self.whitelist = "'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ&:/-_\,+()*.=[]<>@"
        self.lang = "eng"
        self.path = ""
        self.roi_x = 0
        self.roi_y = 0
        self.roi_height = 0
        self.roi_width = 0
        self.deleted_x = None
        self.deleted_y = None
        self.deleted_height = None
        self.deleted_width = None
        self.args_number = 0
        self.show = True
        self.click = False
        self.rightclick = False
        self.mousemove = False
        self.xy_offset = None
        self.x_offset = None
        self.y_offset = None
        self.doubleclick = False
        self.sendkeys = ""
        self.sendkeys_quotes = True
        self.text_encrypted = False
        
class AlyvixTextFinderPropertiesView(QDialog, Ui_Form):
    def __init__(self, parent):
        QDialog.__init__(self)

        # Set up the user interface from Designer.
        self.setupUi(self)
                        
        self.parent = parent
        self.added_block = False
        
        """
        self.number_bar = NumberBar(self.tab_code)
        self.number_bar.setTextEdit(self.textEdit)
        self.textEdit.installEventFilter(self)
        self.textEdit.viewport().installEventFilter(self)
        self.textEdit.setFrameStyle(QFrame.NoFrame)
        self.textEdit.setAcceptRichText(False)
        """
        
        self.textEdit = LineTextWidget(self.tab_code)
        self.textEdit.setGeometry(QRect(8, 9, 535, 255))
        self.textEdit.setText(self.parent.build_code_string())
        #self.textEdit.setStyleSheet("font-family: Currier New;")
        
        """
        font = QFont()
        font.setFamily("Courier New")
        font.setStyleHint(QFont.Monospace)
        font.setFixedPitch(True)
        font.setPointSize(8)
        """

        #metrics = QFontMetrics(font)
                
        tabStop = 4  #4 characters
        #self.textEditCustomLines.setTabStopWidth(tabStop * self.textEditCustomLines.fontMetrics().width(' '))
        
        #charFormat = QTextCharFormat()
        
        self.textEditCustomLines.setLineWrapMode(QTextEdit.NoWrap)

        self.setFixedSize(self.size())

        #self.setWindowTitle('Application Object Properties')
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)
        
        #self.lineEditText.setText(self.parent._main_text.text)
        self.lineEditLang.setText(self.parent._main_text.lang)
        self.lineEditWhiteList.setText(unicode(self.parent._main_text.whitelist, 'utf-8'))
        
        if self.parent.action == "edit":
            self.namelineedit.setEnabled(False)
            
        if self.parent.timeout_exception is False:
            self.timeout_exception.setChecked(False)
        else:
            self.timeout_exception.setChecked(True)
            
        if self.parent.find is True:
            self.find_radio.setChecked(True)
            self.timeout_label.setEnabled(False)
            self.timeout_spinbox.setEnabled(False)
            self.timeout_exception.setEnabled(False)

        if self.parent.wait is True:
            self.wait_radio.setChecked(True)
            self.timeout_label.setEnabled(True)
            self.timeout_spinbox.setEnabled(True)
            self.timeout_exception.setEnabled(True)
            
        if self.parent.wait_disapp is True:
            self.wait_disapp_radio.setChecked(True)
            self.timeout_label.setEnabled(True)
            self.timeout_spinbox.setEnabled(True)
            self.timeout_exception.setEnabled(True)
            
        """
        if self.parent.wait is True:
            self.wait_radio.setChecked(True)
        else:
            self.wait_radio.setChecked(False)
        """

        if self.parent._main_text.click is True:
            self.clickRadio.setChecked(True)
            self.pushButtonXYoffset.setEnabled(True)
        else:
            self.clickRadio.setChecked(False)
            
        if self.parent._main_text.doubleclick is True:
            self.doubleclickRadio.setChecked(True)
            self.pushButtonXYoffset.setEnabled(True)
        else:
            self.doubleclickRadio.setChecked(False)
            
        if self.parent._main_text.rightclick is True:
            self.rightclickRadio.setChecked(True)
            self.pushButtonXYoffset.setEnabled(True)
        else:
            self.rightclickRadio.setChecked(False)
            
        if self.parent._main_text.mousemove is True:
            self.movemouseRadio.setChecked(True)
            self.pushButtonXYoffset.setEnabled(True)
        else:
            self.movemouseRadio.setChecked(False)
            
        if self.parent._main_text.click is False \
            and self.parent._main_text.doubleclick is False \
            and self.parent._main_text.mousemove is False\
            and self.parent._main_text.rightclick is False:
            self.dontclickRadio.setChecked(True)
            self.pushButtonXYoffset.setEnabled(False)
        else:
            self.dontclickRadio.setChecked(False)
            
        if self.parent._main_text.text_encrypted is False:
            self.text_encrypted.setChecked(False)
        else:
            self.text_encrypted.setChecked(True)
            
        if self.parent._main_text.sendkeys_quotes is False:
            self.add_quotes.setChecked(False)
        else:
            self.add_quotes.setChecked(True)
            
        if self.parent._main_text.quotes_ocr is False:
            self.add_quotes_ocr.setChecked(False)
        else:
            self.add_quotes_ocr.setChecked(True)
                    
        self.widget_2.hide()
        
        self.sub_text_index = 0
        
        cnt = 1
        for sub_text in self.parent._sub_texts_finder:
        
            if sub_text.x == 0 and sub_text.y == 0:
                continue
            item = QListWidgetItem()
            item.setCheckState(Qt.Checked)
            item.setText("sub_component_" + str(cnt))
            self.listWidget.addItem(item)
            cnt = cnt + 1
            
        #self.listWidget.setCurrentIndex(QModelIndex(self.listWidget.rootIndex()))
        self.listWidget.item(0).setSelected(True)
        
        self.timeout_spinbox.setValue(self.parent.timeout)      
        self.inserttext.setText(self.parent._main_text.sendkeys)       

        if self.parent._main_text.sendkeys == "":
            self.inserttext.setText("Insert here the Keystroke to send")
        else:
            self.inserttext.setText(unicode(self.parent._main_text.sendkeys, 'utf-8'))       
            
        if self.parent._main_text.text == "":
            self.lineEditText.setText("Type here the Text to find")
        else:
            self.lineEditText.setText(unicode(self.parent._main_text.text, 'utf-8'))      

        if self.parent.object_name == "":
            self.namelineedit.setText("Type here the name of the object")
        else:
            self.namelineedit.setText(self.parent.object_name)      

        
        self.spinBoxArgs.setValue(self.parent.args_number)
        
        self.init_block_code()            
           
        self.connect(self.listWidget, SIGNAL('itemSelectionChanged()'), self.listWidget_selection_changed)
        self.connect(self.listWidget, SIGNAL('itemChanged(QListWidgetItem*)'), self, SLOT('listWidget_state_changed(QListWidgetItem*)'))
        
        self.connect(self.wait_radio, SIGNAL('toggled(bool)'), self.wait_radio_event)
        self.connect(self.wait_disapp_radio, SIGNAL('toggled(bool)'), self.wait_disapp_radio_event)
        self.connect(self.find_radio, SIGNAL('toggled(bool)'), self.find_radio_event)
        
        self.connect(self.timeout_spinbox, SIGNAL('valueChanged(int)'), self.timeout_spinbox_event)
        self.connect(self.timeout_exception, SIGNAL('stateChanged(int)'), self.timeout_exception_event)
        
        self.connect(self.add_quotes_ocr, SIGNAL('stateChanged(int)'), self.add_quotes_ocr_event)
        
        self.connect(self.clickRadio, SIGNAL('toggled(bool)'), self.clickRadio_event)
        self.connect(self.doubleclickRadio, SIGNAL('toggled(bool)'), self.doubleclickRadio_event)
        self.connect(self.rightclickRadio, SIGNAL('toggled(bool)'), self.rightclickRadio_event)
        self.connect(self.movemouseRadio, SIGNAL('toggled(bool)'), self.movemouseRadio_event)
        self.connect(self.dontclickRadio, SIGNAL('toggled(bool)'), self.dontclickRadio_event)
        
        self.connect(self.pushButtonXYoffset, SIGNAL('clicked()'), self.pushButtonXYoffset_event)
        
        self.connect(self.pushButtonCheck, SIGNAL('clicked()'), self.check_text)
        
        self.connect(self.inserttext, SIGNAL("textChanged(QString)"), self, SLOT("inserttext_event(QString)"))
        self.connect(self.namelineedit, SIGNAL("textChanged(QString)"), self, SLOT("namelineedit_event(QString)"))
        #self.connect(self.inserttext, SIGNAL('cursorPositionChanged ( int, int)'), self.inserttext_textchanged_event)
        self.connect(self.pushButtonAddBlock, SIGNAL('clicked()'), self.add_block_code)
        self.connect(self.pushButtonRemoveBlock, SIGNAL('clicked()'), self.remove_block_code)
        self.connect(self.listWidgetBlocks, SIGNAL('itemSelectionChanged()'), self.listWidgetBlocks_selection_changed)
        #self.connect(self.textEditCustomLines, SIGNAL("textChanged(QString)"), self, SLOT("custom_lines_text_changed(QString)"))
        self.connect(self.lineEditText, SIGNAL("textChanged(QString)"), self, SLOT("lineEditText_event(QString)"))
        self.connect(self.lineEditLang, SIGNAL("textChanged(QString)"), self, SLOT("lineEditLang_event(QString)"))
        self.connect(self.lineEditWhiteList, SIGNAL("textChanged(QString)"), self, SLOT("lineEditWhiteList_event(QString)"))
        
        
        #self.inserttext.viewport().installEventFilter(self)
        self.inserttext.installEventFilter(self)
        
        self.connect(self.add_quotes, SIGNAL('stateChanged(int)'), self.add_quotes_event)
        self.connect(self.text_encrypted, SIGNAL('stateChanged(int)'), self.text_encrypted_event)
        
        self.namelineedit.installEventFilter(self)
        
        self.connect(self.tabWidget, SIGNAL('currentChanged(int)'), self.tab_changed_event)
        
        self.connect(self.checkBoxEnablePerformance, SIGNAL('stateChanged(int)'), self.enable_performance_event)
        self.connect(self.doubleSpinBoxWarning, SIGNAL('valueChanged(double)'), self.warning_event)
        self.connect(self.doubleSpinBoxCritical, SIGNAL('valueChanged(double)'), self.critical_event)
        
        self.connect(self.spinBoxArgs, SIGNAL('valueChanged(int)'), self.args_spinbox_change_event)
        self.lineEditText.installEventFilter(self)
        
        self.connect(self.pushButtonOk, SIGNAL('clicked()'), self.pushButtonOk_event)
        self.connect(self.pushButtonCancel, SIGNAL('clicked()'), self.pushButtonCancel_event)
        
        ###########
        ###########
        
        self.connect(self.add_quotes_ocr_2, SIGNAL('stateChanged(int)'), self.add_quotes_ocr_event_2)
        
        self.connect(self.roi_x_spinbox, SIGNAL('valueChanged(int)'), self.roi_x_spinbox_event)
        self.connect(self.roi_y_spinbox, SIGNAL('valueChanged(int)'), self.roi_y_spinbox_event)
        self.connect(self.roi_height_spinbox, SIGNAL('valueChanged(int)'), self.roi_height_spinbox_event)
        self.connect(self.roi_width_spinbox, SIGNAL('valueChanged(int)'), self.roi_width_spinbox_event)
        
        self.connect(self.pushButtonCheck_2, SIGNAL('clicked()'), self.check_text_2)
        
        self.connect(self.clickRadio_2, SIGNAL('toggled(bool)'), self.clickRadio_event_2)
        self.connect(self.doubleclickRadio_2, SIGNAL('toggled(bool)'), self.doubleclickRadio_event_2)
        self.connect(self.movemouseRadio_2, SIGNAL('toggled(bool)'), self.movemouseRadio_event_2)
        self.connect(self.rightclickRadio_2, SIGNAL('toggled(bool)'), self.rightclickRadio_event_2)
        self.connect(self.dontclickRadio_2, SIGNAL('toggled(bool)'), self.dontclickRadio_event_2)
        
        self.connect(self.pushButtonXYoffset_2, SIGNAL('clicked()'), self.pushButtonXYoffset_event_2)
        
        self.connect(self.inserttext_2, SIGNAL("textChanged(QString)"), self, SLOT("inserttext_event_2(QString)"))
        #self.connect(self.inserttext, SIGNAL('cursorPositionChanged ( int, int)'), self.inserttext_textchanged_event)
        self.connect(self.lineEditText_2, SIGNAL("textChanged(QString)"), self, SLOT("lineEditText_2_event(QString)"))
        self.connect(self.lineEditLang_2, SIGNAL("textChanged(QString)"), self, SLOT("lineEditLang2_event(QString)"))
        self.connect(self.lineEditWhiteList_2, SIGNAL("textChanged(QString)"), self, SLOT("lineEditWhiteList2_event(QString)"))
        
        #self.inserttext_2.viewport().installEventFilter(self)
        self.inserttext_2.installEventFilter(self)
        
        self.connect(self.text_encrypted_2, SIGNAL('stateChanged(int)'), self.text_encrypted_event_2)
        self.connect(self.add_quotes_2, SIGNAL('stateChanged(int)'), self.add_quotes_event_2)
        
        self.textEditCustomLines.installEventFilter(self)
        self.lineEditText_2.installEventFilter(self)
        self.roi_y_spinbox.installEventFilter(self)
        self.roi_height_spinbox.installEventFilter(self)
        self.roi_x_spinbox.installEventFilter(self)
        self.roi_width_spinbox.installEventFilter(self)
        
    def pushButtonCancel_event(self):
        self.close()
        self.parent.cancel_all()

    def pushButtonOk_event(self):
    
        answer = QMessageBox.Yes
        filename = self.parent._alyvix_proxy_path + os.sep + "AlyvixProxy" + self.parent._robot_file_name + ".py"
        
        arg_list = []       
        args_range = range(1, self.parent.args_number + 1)
        
        for arg_num in args_range:
            arg_list.append("arg" + str(arg_num))
        
        if self.parent._main_text.sendkeys_quotes is False:
            try:
            
                node = ast.parse(self.parent._main_text.sendkeys)
                
                checksyntax = CheckSyntax()
                var = checksyntax.check(node, arg_list)
                
                #print "varr
                
                if var is not None and "," in var:
                    msgbox_str = "The variables " + var + " are not arguments of the keyword. Do you want to save the keyword?"
                    
                elif var is not None:
                    msgbox_str = "The variable " + var + " is not an argument of the keyword. Do you want to save the keyword?"
                
                if var is not None:
                    #QMessageBox.warning(self, "Warning on main conponent", "The variable " + var + " is not an argument of the Keyword")
                    answer = QMessageBox.warning(self, "Warning on main conponent", msgbox_str, QMessageBox.Yes, QMessageBox.No)
                    #return True
                    if answer == QMessageBox.No:
                        return True
                
            except SyntaxError:
                QMessageBox.critical(self, "Error", "Invalid Keystroke syntax on main conponent")
                return True
                
        if self.parent._main_text.quotes_ocr is False:
            try:
            
                node = ast.parse(self.parent._main_text.text)
                
                checksyntax = CheckSyntax()
                var = checksyntax.check(node, arg_list)
                
                #print "varr
                
                if var is not None and "," in var:
                    msgbox_str = "The variables " + var + " are not arguments of the keyword. Do you want to save the keyword?"
                    
                elif var is not None:
                    msgbox_str = "The variable " + var + " is not an argument of the keyword. Do you want to save the keyword?"
                
                if var is not None:
                    #QMessageBox.warning(self, "Warning on main conponent", "The variable " + var + " is not an argument of the Keyword")
                    answer = QMessageBox.warning(self, "Warning on main conponent", msgbox_str, QMessageBox.Yes, QMessageBox.No)
                    #return True
                    if answer == QMessageBox.No:
                        return True
                
            except SyntaxError:
                QMessageBox.critical(self, "Error", "Invalid text syntax on main conponent")
                return True
                
        cnt = 1
        for sub_text in self.parent._sub_texts_finder:
            if sub_text.sendkeys_quotes is False:
                try:
                    node = ast.parse(sub_text.sendkeys)
                    
                    checksyntax = CheckSyntax()
                    var = checksyntax.check(node, arg_list)
                    
                    if var is not None and "," in var:
                        msgbox_str = "The variables " + var + " are not arguments of the keyword. Do you want to save the keyword?"
                        
                    elif var is not None:
                        msgbox_str = "The variable " + var + " is not an argument of the keyword. Do you want to save the keyword?"
                    
                    #print "varrr"
                
                    if var is not None:
                        answer = QMessageBox.warning(self, "Warning on sub component " + str(cnt), msgbox_str, QMessageBox.Yes, QMessageBox.No)
                        #return True
                        if answer == QMessageBox.No:
                            return True
                    
                except SyntaxError:
                    QMessageBox.critical(self, "Error", "Invalid Keystroke syntax on sub component " + str(cnt))
                    return True
                    
            if sub_text.quotes_ocr is False:
                try:
                    node = ast.parse(sub_text.text)
                    
                    checksyntax = CheckSyntax()
                    var = checksyntax.check(node, arg_list)
                    
                    if var is not None and "," in var:
                        msgbox_str = "The variables " + var + " are not arguments of the keyword. Do you want to save the keyword?"
                        
                    elif var is not None:
                        msgbox_str = "The variable " + var + " is not an argument of the keyword. Do you want to save the keyword?"
                    
                    #print "varrr"
                
                    if var is not None:
                        answer = QMessageBox.warning(self, "Warning on sub component " + str(cnt), msgbox_str, QMessageBox.Yes, QMessageBox.No)
                        #return True
                        if answer == QMessageBox.No:
                            return True
                    
                except SyntaxError:
                    QMessageBox.critical(self, "Error", "Invalid text syntax on sub component " + str(cnt))
                    return True
            cnt += 1
            
        
        if str(self.namelineedit.text().toUtf8()) == "" or str(self.namelineedit.text().toUtf8()) == "Type here the name of the object":
            answer = QMessageBox.warning(self, "Warning", "The object name is empty. Do you want to create it automatically?", QMessageBox.Yes, QMessageBox.No)
        elif os.path.isfile(filename) and self.parent.action == "new":
            
            python_file = open(filename).read()
            
            #print filename
            
            obj_name = str(self.parent.object_name).lower()
            
            #print "obj_name:", obj_name
            
            if "def " + obj_name + "_mouse_keyboard(" in python_file or "def " + obj_name + "_build_object(" in python_file or "def " + obj_name + "(" in python_file:
                QMessageBox.critical(self, "Error", "Keyword name already exists!")
                return
        
        if answer == QMessageBox.Yes:
            self.close()
            self.parent.save_all()
  
    def check_text(self):
        if not os.path.exists(self.parent._path):
            os.makedirs(self.parent._path)
        image_name = self.parent._path + os.sep + time.strftime("text_finder_%d_%m_%y_%H_%M_%S_temp_img.png")
        self.parent._bg_pixmap.save(image_name,"PNG", -1)
        time.sleep(0.05)
        cv_image = cv2.imread(image_name)
        #print cv_image
        #time.sleep(0.1)
        os.remove(image_name)
        text_finder = TextFinder()
        text_finder.set_source_image_color(cv_image)
        
        roi_x = self.parent._main_text.roi_x
        roi_y = self.parent._main_text.roi_y
        roi_width = self.parent._main_text.roi_width
        roi_height = self.parent._main_text.roi_height
        
        text_finder.set_main_component({"text":str(self.parent._main_text.text), "lang":str(self.parent._main_text.lang), "whitelist":self.parent._main_text.whitelist},
                                       {"roi_x":roi_x, "roi_y":roi_y, "roi_width":roi_width, "roi_height":roi_height})
                                       
        text_finder.find()
        text = text_finder.get_last_read()
        
        result = text_finder.get_result(0)
        
        result_flag = False
        if result != None:
            result_flag = True
        
        self.check_window = AlyvixTextCheck(text, result_flag)
        self.check_window.show()
  
    def args_spinbox_change_event(self, event):
        self.parent.args_number = self.spinBoxArgs.value()
        self.parent.build_code_array()
        self.textEdit.setText(unicode(self.parent.build_code_string(), 'utf-8'))
  
    def warning_event(self, event):
        self.parent.warning = self.doubleSpinBoxWarning.value()
        
    def critical_event(self, event):
        self.parent.critical = self.doubleSpinBoxCritical.value()
        
    def enable_performance_event(self, event):
        if self.checkBoxEnablePerformance.isChecked() is True:
            self.parent.enable_performance = True
            self.doubleSpinBoxWarning.setEnabled(True)
            self.doubleSpinBoxCritical.setEnabled(True)
            self.labelWarning.setEnabled(True)
            self.labelCritical.setEnabled(True)
        else:
            self.parent.enable_performance = False
            self.doubleSpinBoxWarning.setEnabled(False)
            self.doubleSpinBoxCritical.setEnabled(False)
            self.labelWarning.setEnabled(False)
            self.labelCritical.setEnabled(False)
        
    def tab_changed_event(self, tab_index):
        if tab_index is 1:
            self.parent.build_code_array()
            self.textEdit.setText(unicode(self.parent.build_code_string(), 'utf-8'))
        elif tab_index is 3:
            self.doubleSpinBoxWarning.setValue(self.parent.warning)
            self.doubleSpinBoxCritical.setValue(self.parent.critical)
            
            if self.parent.enable_performance is True:
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
            
        
    def min_width_spinbox_change_event(self, event):
        self.parent._main_text.min_width = self.min_width_spinbox.value()
        
        if self.parent._main_text.min_width > self.parent._main_text.max_width:
            self.parent._main_text.min_width = self.parent._main_text.max_width
            self.min_width_spinbox.setValue(self.parent._main_text.min_width)
            
        self.parent.update()
        
    def max_width_spinbox_change_event(self, event):
    
        if self.max_width_spinbox.value() < self.min_width_spinbox.value():
            self.max_width_spinbox.setValue(self.parent._main_text.min_width)
            return
            
        self.parent._main_text.max_width = self.max_width_spinbox.value()
        self.parent.update()
        
    def min_height_spinbox_change_event(self, event):
        self.parent._main_text.min_height = self.min_height_spinbox.value()
        
        if self.parent._main_text.min_height > self.parent._main_text.max_height:
            self.parent._main_text.min_height = self.parent._main_text.max_height
            self.min_height_spinbox.setValue(self.parent._main_text.min_height)
            
        self.parent.update()
        
    def max_height_spinbox_change_event(self, event):
    
        if self.max_height_spinbox.value() < self.min_height_spinbox.value():
            self.max_height_spinbox.setValue(self.parent._main_text.min_height)
            return
        
        self.parent._main_text.max_height = self.max_height_spinbox.value()
        self.parent.update()
        
    def show_min_max_event(self, event):
        if self.show_min_max.isChecked() is True:
            self.parent._main_text.show_min_max = True
            self.show_tolerance.setChecked(False)
        else:
            self.parent._main_text.show_min_max = False
        self.parent.update()
        
    def show_tolerance_event(self, event):
        if self.show_tolerance.isChecked() is True:
            self.parent._main_text.show_tolerance = True
            self.show_min_max.setChecked(False)
        else:
            self.parent._main_text.show_tolerance = False
        self.parent.update()
        
    def height_tolerance_spinbox_event(self, event):
        self.parent._main_text.height_tolerance = self.height_tolerance_spinbox.value()
        self.parent.update()
        
    def width_tolerance_spinbox_event(self, event):
        self.parent._main_text.width_tolerance = self.width_tolerance_spinbox.value()
        self.parent.update()
     
    def use_tolerance_event(self, event):
        pass

        
    def use_min_max_event(self, event):
        if event is False:
            self.height_tolerance_spinbox.setEnabled(True)
            self.width_tolerance_spinbox.setEnabled(True)
            self.height_tolerance_label.setEnabled(True)
            self.width_tolerance_label.setEnabled(True)
            
            self.min_height_label.setEnabled(False)
            self.max_height_label.setEnabled(False)
            self.min_width_label.setEnabled(False)
            self.max_width_label.setEnabled(False)
            self.min_height_spinbox.setEnabled(False)
            self.max_height_spinbox.setEnabled(False)
            self.min_width_spinbox.setEnabled(False)
            self.max_width_spinbox.setEnabled(False)
            
            self.parent._main_text.use_min_max = False
            self.parent._main_text.use_tolerance = True
            
            
        else:
            self.height_tolerance_spinbox.setEnabled(False)
            self.width_tolerance_spinbox.setEnabled(False)
            self.height_tolerance_label.setEnabled(False)
            self.width_tolerance_label.setEnabled(False)
            
            self.min_height_label.setEnabled(True)
            self.max_height_label.setEnabled(True)
            self.min_width_label.setEnabled(True)
            self.max_width_label.setEnabled(True)
            self.min_height_spinbox.setEnabled(True)
            self.max_height_spinbox.setEnabled(True)
            self.min_width_spinbox.setEnabled(True)
            self.max_width_spinbox.setEnabled(True)
            
            self.parent._main_text.use_min_max = True
            self.parent._main_text.use_tolerance = False
        
    def listWidget_selection_changed(self):
    
        selected_index = self.listWidget.currentRow()
        
        if selected_index == 0:
            self.widget_2.hide()
            self.widget.show()
            self.widget.setGeometry(QRect(173, 9, 381, 306))

        else:
            self.widget.hide()
            self.widget_2.show()
            self.widget_2.setGeometry(QRect(173, 9, 381, 283))
            self.sub_text_index = selected_index - 1
            self.update_sub_text_view()

        #print self.listWidget.currentItem().text()
        
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
                    self.parent._main_text.show = show
                else:
                    self.parent._sub_texts_finder[row_index-1].show = show
                    
        self.parent.update()
        
    def wait_radio_event(self, event):
        
        if event is True:
            self.timeout_spinbox.setEnabled(True)
            self.timeout_label.setEnabled(True)
            self.timeout_exception.setEnabled(True)
            self.parent.wait_disapp = False
            self.parent.wait = True
            self.parent.find = False
        
    def wait_disapp_radio_event(self, event):
        
        if event is True:
            self.timeout_spinbox.setEnabled(True)
            self.timeout_label.setEnabled(True)
            self.timeout_exception.setEnabled(True)
            self.parent.wait_disapp = True
            self.parent.wait = False
            self.parent.find = False
            
    def find_radio_event(self, event):
        
        if event is True:
            self.timeout_spinbox.setEnabled(False)
            self.timeout_exception.setEnabled(False)
            self.timeout_label.setEnabled(False)
            self.parent.wait_disapp = False
            self.parent.wait = False
            self.parent.find = True
            
    def timeout_spinbox_event(self, event):
        self.parent.timeout = self.timeout_spinbox.value()
        
    def timeout_exception_event(self, event):
        if self.timeout_exception.isChecked() is True:
            self.parent.timeout_exception = True
        else:
            self.parent.timeout_exception = False

    def update_sub_text_view(self):
        index = self.sub_text_index
        
        if self.parent._sub_texts_finder[index].sendkeys == "":
            self.inserttext_2.setText("Insert here the Keystroke to send")
        else:
            self.inserttext_2.setText(unicode(self.parent._sub_texts_finder[index].sendkeys, 'utf-8'))
            
        if self.parent._sub_texts_finder[index].text_encrypted is False:
            self.text_encrypted_2.setChecked(False)
        else:
            self.text_encrypted_2.setChecked(True)
            
        if self.parent._sub_texts_finder[index].sendkeys_quotes is False:
            self.add_quotes_2.setChecked(False)
        else:
            self.add_quotes_2.setChecked(True)
            
        if self.parent._sub_texts_finder[index].quotes_ocr is False:
            self.add_quotes_ocr_2.setChecked(False)
        else:
            self.add_quotes_ocr_2.setChecked(True)
            
        if self.parent._sub_texts_finder[index].text == "":
            self.lineEditText_2.setText("Type here the Text to find")
        else:
            self.lineEditText_2.setText(unicode(self.parent._sub_texts_finder[index].text, 'utf-8'))
        
        #self.lineEditText_2.setText(self.parent._sub_texts_finder[self.sub_text_index].text)
        self.lineEditLang_2.setText(self.parent._sub_texts_finder[self.sub_text_index].lang)
        self.lineEditWhiteList_2.setText(unicode(self.parent._sub_texts_finder[self.sub_text_index].whitelist, 'utf-8'))
            
        self.roi_x_spinbox.setValue(self.parent._sub_texts_finder[self.sub_text_index].roi_x)
        self.roi_y_spinbox.setValue(self.parent._sub_texts_finder[self.sub_text_index].roi_y)
        self.roi_width_spinbox.setValue(self.parent._sub_texts_finder[self.sub_text_index].roi_width)
        self.roi_height_spinbox.setValue(self.parent._sub_texts_finder[self.sub_text_index].roi_height)
            
        if self.parent._sub_texts_finder[self.sub_text_index].click is True:
            self.clickRadio_2.setChecked(True)
            self.pushButtonXYoffset_2.setEnabled(True)
        else:
            self.clickRadio_2.setChecked(False)
            
        if self.parent._sub_texts_finder[self.sub_text_index].doubleclick is True:
            self.doubleclickRadio_2.setChecked(True)
            self.pushButtonXYoffset_2.setEnabled(True)
        else:
            self.doubleclickRadio_2.setChecked(False)
            
        if self.parent._sub_texts_finder[self.sub_text_index].rightclick is True:
            self.rightclickRadio_2.setChecked(True)
            self.pushButtonXYoffset_2.setEnabled(True)
        else:
            self.rightclickRadio_2.setChecked(False)
            
        if self.parent._sub_texts_finder[self.sub_text_index].mousemove is True:
            self.movemouseRadio_2.setChecked(True)
            self.pushButtonXYoffset_2.setEnabled(True)
        else:
            self.movemouseRadio_2.setChecked(False)
            
        if self.parent._sub_texts_finder[self.sub_text_index].click is False \
            and self.parent._sub_texts_finder[self.sub_text_index].doubleclick is False \
            and self.parent._sub_texts_finder[self.sub_text_index].rightclick is False \
            and self.parent._sub_texts_finder[self.sub_text_index].mousemove is False:
            self.dontclickRadio_2.setChecked(True)
            self.pushButtonXYoffset_2.setEnabled(False)
        else:
            self.dontclickRadio_2.setChecked(False)
            
    def clickRadio_event(self, event):
        if event is False:
            self.parent._main_text.click = False
        else:
            self.parent._main_text.click = True
            self.pushButtonXYoffset.setEnabled(True) 
            
        self.parent.update()
        
    def doubleclickRadio_event(self, event):
        if event is False:
            self.parent._main_text.doubleclick = False
        else:
            self.parent._main_text.doubleclick = True 
            self.pushButtonXYoffset.setEnabled(True) 
            
        self.parent.update()
            
                        
    def rightclickRadio_event(self, event):
        if event is False:
            self.parent._main_text.rightclick = False
        else:
            self.parent._main_text.rightclick = True 
            self.pushButtonXYoffset.setEnabled(True) 
            
        self.parent.update()
            
    def movemouseRadio_event(self, event):
        if event is False:
            self.parent._main_text.mousemove = False
        else:
            self.parent._main_text.mousemove = True 
            self.pushButtonXYoffset.setEnabled(True) 
            
        self.parent.update()
             
    def dontclickRadio_event(self, event):
        if event is True:
            self.parent._main_text.click = False
            self.parent._main_text.doubleclick = False
            self.parent._main_text.rightclick = False
            self.parent._main_text.mousemove = False
            self.pushButtonXYoffset.setEnabled(False) 
            
        self.parent.update()
            
    def pushButtonXYoffset_event(self):
        self.parent.set_xy_offset = -1  #-1 for main, other int for sub index
        self.hide()
    
            
    @pyqtSlot(QString)
    def inserttext_event(self, text):
        if self.inserttext.text() == "Insert here the Keystroke to send": #or self.inserttext.text() == "#k.send('Type here the key')":
            self.parent._main_text.sendkeys = "".encode('utf-8')
        else:
            self.parent._main_text.sendkeys = str(text.toUtf8()) #str(self.inserttext.text().toUtf8())
            
    def text_encrypted_event(self, event):
        if self.text_encrypted.isChecked() is True:
            self.parent._main_text.text_encrypted = True
        else:
            self.parent._main_text.text_encrypted = False
    
    def add_quotes_event(self, event):
        if self.add_quotes.isChecked() is True:
            self.parent._main_text.sendkeys_quotes = True
        else:
            self.parent._main_text.sendkeys_quotes = False
            
    def add_quotes_ocr_event(self, event):
        if self.add_quotes_ocr.isChecked() is True:
            self.parent._main_text.quotes_ocr = True
        else:
            self.parent._main_text.quotes_ocr = False
    
    @pyqtSlot(QString)    
    def lineEditText_event(self, text):
        if text == "Type here the Text to find":
            self.parent._main_text.text = "".encode('utf-8')
        else:
            self.parent._main_text.text = str(text.toUtf8())
            
    @pyqtSlot(QString)    
    def lineEditLang_event(self, text):
        if text == "Type here the Text to find":
            self.parent._main_text.lang = "".encode('utf-8')
        else:
            self.parent._main_text.lang = str(text.toUtf8())
            
    @pyqtSlot(QString)    
    def lineEditWhiteList_event(self, text):
        if text == "Type here the Text to find":
            self.parent._main_text.whitelist = "".encode('utf-8')
        else:
            self.parent._main_text.whitelist = str(text.toUtf8())
            #print "type:", type(self.parent._main_text.whitelist), "value:", unicode(self.parent._main_text.whitelist, "utf8")
        
    @pyqtSlot(QString)
    def namelineedit_event(self, text):
        if text == "Type here the name of the object":
            self.parent.object_name = "".encode('utf-8')
        else:
            self.parent.object_name = str(text.toUtf8()).replace(" ", "_")
        
    def eventFilter(self, obj, event):
        if event.type() == event.MouseButtonPress:
        
            if self.namelineedit.text() == "Type here the name of the object" and obj.objectName() == "namelineedit":
                self.namelineedit.setText("")
                return True
        

            if self.inserttext.text() == "Insert here the Keystroke to send" and obj.objectName() == "inserttext":
                self.inserttext.setText("")
                return True
                    
            if self.inserttext_2.text() == "Insert here the Keystroke to send" and obj.objectName() == "inserttext_2":
                self.inserttext_2.setText("")
                return True
                
            if self.lineEditText.text() == "Type here the Text to find" and obj.objectName() == "lineEditText":
                self.lineEditText.setText("")
                return True
                
            if self.lineEditText_2.text() == "Type here the Text to find" and obj.objectName() == "lineEditText_2":
                self.lineEditText_2.setText("")
                return True
                
        if event.type()== event.FocusOut:
            #print "event"
            if obj.objectName() == "roi_y_spinbox":

                absolute_sub_roi_y = self.parent._main_text.y + self.parent._sub_texts_finder[self.sub_text_index].roi_y
                absolute_sub_rect_y = self.parent._sub_texts_finder[self.sub_text_index].y
        
                if absolute_sub_roi_y > absolute_sub_rect_y:
                    self.parent._sub_texts_finder[self.sub_text_index].roi_y = self.parent._sub_texts_finder[self.sub_text_index].y - self.parent._main_text.y
                    self.roi_y_spinbox.setValue(self.parent._sub_texts_finder[self.sub_text_index].roi_y)
                    self.parent.update()
                    return True
                    
                if absolute_sub_roi_y + self.parent._sub_texts_finder[self.sub_text_index].roi_height < absolute_sub_rect_y + self.parent._sub_texts_finder[self.sub_text_index].height:
                    self.parent._sub_texts_finder[self.sub_text_index].roi_y = self.parent._sub_texts_finder[self.sub_text_index].y - self.parent._main_text.y
                    self.roi_y_spinbox.setValue(self.parent._sub_texts_finder[self.sub_text_index].roi_y)
                    self.parent.update()
                    return True
                    
            elif obj.objectName() == "roi_height_spinbox":
                
                absolute_sub_roi_y = self.parent._main_text.y + self.parent._sub_texts_finder[self.sub_text_index].roi_y
                absolute_sub_rect_y = self.parent._sub_texts_finder[self.sub_text_index].y
                if absolute_sub_roi_y + self.parent._sub_texts_finder[self.sub_text_index].roi_height < absolute_sub_rect_y + self.parent._sub_texts_finder[self.sub_text_index].height:
                    px_to_add = (absolute_sub_rect_y + self.parent._sub_texts_finder[self.sub_text_index].height) - (absolute_sub_roi_y + self.parent._sub_texts_finder[self.sub_text_index].roi_height)
                    height = absolute_sub_roi_y - px_to_add
                    self.parent._sub_texts_finder[self.sub_text_index].roi_height = self.parent._sub_texts_finder[self.sub_text_index].roi_height  + px_to_add
                    self.roi_height_spinbox.setValue(self.parent._sub_texts_finder[self.sub_text_index].roi_height)
                    self.parent.update()
                    return True
                    
            elif obj.objectName() == "roi_x_spinbox":

                absolute_sub_roi_x = self.parent._main_text.x + self.parent._sub_texts_finder[self.sub_text_index].roi_x
                absolute_sub_rect_x = self.parent._sub_texts_finder[self.sub_text_index].x
        
                if absolute_sub_roi_x > absolute_sub_rect_x:
                    self.parent._sub_texts_finder[self.sub_text_index].roi_x = self.parent._sub_texts_finder[self.sub_text_index].x - self.parent._main_text.x
                    self.roi_x_spinbox.setValue(self.parent._sub_texts_finder[self.sub_text_index].roi_x)
                    self.parent.update()
                    return True
                    
                if absolute_sub_roi_x + self.parent._sub_texts_finder[self.sub_text_index].roi_width < absolute_sub_rect_x + self.parent._sub_texts_finder[self.sub_text_index].width:
                    self.parent._sub_texts_finder[self.sub_text_index].roi_x = self.parent._sub_texts_finder[self.sub_text_index].x - self.parent._main_text.x
                    self.roi_x_spinbox.setValue(self.parent._sub_texts_finder[self.sub_text_index].roi_x)
                    self.parent.update()
                    return True
                    
            elif obj.objectName() == "roi_width_spinbox":
                
                absolute_sub_roi_x = self.parent._main_text.x + self.parent._sub_texts_finder[self.sub_text_index].roi_x
                absolute_sub_rect_x = self.parent._sub_texts_finder[self.sub_text_index].x
                if absolute_sub_roi_x + self.parent._sub_texts_finder[self.sub_text_index].roi_width < absolute_sub_rect_x + self.parent._sub_texts_finder[self.sub_text_index].width:
                    px_to_add = (absolute_sub_rect_x + self.parent._sub_texts_finder[self.sub_text_index].width) - (absolute_sub_roi_x + self.parent._sub_texts_finder[self.sub_text_index].roi_width)
                    height = absolute_sub_roi_x - px_to_add
                    self.parent._sub_texts_finder[self.sub_text_index].roi_width = self.parent._sub_texts_finder[self.sub_text_index].roi_width  + px_to_add
                    self.roi_width_spinbox.setValue(self.parent._sub_texts_finder[self.sub_text_index].roi_width)
                    self.parent.update()
                    return True
                
            elif self.namelineedit.text() == "" and obj.objectName() == "namelineedit":
                self.namelineedit.setText("Type here the name of the object")
                return True
            elif obj.objectName() == "namelineedit":
                self.namelineedit.setText(self.parent.object_name)
                return True
        
            if self.inserttext.text() == "" and obj.objectName() == "inserttext":
                self.inserttext.setText("Insert here the Keystroke to send")
                return True
                
            if self.inserttext_2.text() == "" and obj.objectName() == "inserttext_2":
                self.inserttext_2.setText("Insert here the Keystroke to send")
                return True
                
            if self.lineEditText.text() == "" and obj.objectName() == "lineEditText":
                self.lineEditText.setText("Type here the Text to find")
                return True
                
            if self.lineEditText_2.text() == "" and obj.objectName() == "lineEditText_2":
                self.lineEditText_2.setText("Type here the Text to find")
                return True
                
            if obj.objectName() == "textEditCustomLines" and self.added_block is False:
                self.update_code_block_array()
                return True
            elif obj.objectName() == "textEditCustomLines" and self.added_block is True:
                self.added_block = False
                return True
                
        if event.type() == event.KeyPress and obj.objectName() == "textEditCustomLines" and event.key() == Qt.Key_Tab:
            #event.ignore()
            #self.textEditCustomLines.append("    ")
            #print event.Key()
            #self.textEditCustomLines.setPlainText(self.textEditCustomLines.toPlainText().replace("\t","    "))
            
            #self.textEditCustomLines.moveCursor(QTextCursor.End)
            #string =  self.textEditCustomLines.textCursor().selectedText().split("\n")
            #print self.textEditCustomLines.textCursor().selectedText().replace("\n","    ").toUtf8()
            
            """
            selected_lines = self.textEditCustomLines.textCursor().selection().toPlainText().split("\n")
            print len(selected_lines)
            for line in selected_lines:
                print line.toUtf8()
            """
            
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
            
            # str(string.toUtf8()) #unicode(string, "utf-8")
            
            """
            cnt = 0
            for str in string:
                str = "    " + str
                cnt = cnt + 1
            """
                
            #print self.textEditCustomLines.toPlainText()
                        
            #self.textEditCustomLines.insertPlainText("    ")

            #self.textEditCustomLines.moveCursor(QTextCursor.End)

            #self.update_code_block_array()

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
            
                                
            #self.update_code_block_array()
                
            return True
            
        return False
        # regardless, just do the default
        #return super(Widget, self).eventFilter(obj, event)
    
    def init_block_code(self):
                
        for block in self.parent._code_blocks:
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
                
            for block in self.parent._code_blocks:
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
                self.listWidgetBlocks.addItem(item)
                
                self.parent._code_blocks.append((index, str(self.textEditCustomLines.toPlainText().toUtf8()), end_line))
                self.added_block = True
                self.textEditCustomLines.setPlainText("")
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
        
        del self.parent._code_blocks[selected_index]
        
        item = self.listWidgetBlocks.takeItem(selected_index)
        self.listWidgetBlocks.removeItemWidget(item)
        self.textEditCustomLines.setPlainText("")
        
        if len(self.parent._code_blocks) == 1:
            block = self.parent._code_blocks[0]
            code_text = block[1]
            self.textEditCustomLines.setPlainText(code_text)
            
    def listWidgetBlocks_selection_changed(self):
        
        selected_index = self.listWidgetBlocks.currentRow()
        
        if len(self.parent._code_blocks) > 0:
            block = self.parent._code_blocks[selected_index]
            code_text = block[1]
            self.textEditCustomLines.setPlainText(unicode(code_text, 'utf-8'))
            self.pushButtonAddBlock.setText("Unselect")

    def update_code_block_array(self):
        
        list_current_item = self.listWidgetBlocks.currentItem()
        
        if list_current_item is None:
            return
            
        selected_index = self.listWidgetBlocks.currentRow()
        
        if len(self.parent._code_blocks) > 0:
            text = str(self.textEditCustomLines.toPlainText().toUtf8())
            end_line = self.parent._code_blocks[selected_index][0] + len(self.textEditCustomLines.toPlainText().split("\n")) -1
            new_tuple = (self.parent._code_blocks[selected_index][0], text, end_line)
            self.parent._code_blocks[selected_index] = new_tuple
            self.listWidgetBlocks.currentItem().setText(str(self.parent._code_blocks[selected_index][0]) + ":" + str(end_line))
        
############
############

    def text_encrypted_event_2(self, event):
        if self.text_encrypted_2.isChecked() is True:
            self.parent._sub_texts_finder[self.sub_text_index].text_encrypted = True
        else:
            self.parent._sub_texts_finder[self.sub_text_index].text_encrypted = False
    
    def add_quotes_event_2(self, event):
        if self.add_quotes_2.isChecked() is True:
            self.parent._sub_texts_finder[self.sub_text_index].sendkeys_quotes = True
        else:
            self.parent._sub_texts_finder[self.sub_text_index].sendkeys_quotes = False
            
    def add_quotes_ocr_event_2(self, event):
        if self.add_quotes_ocr_2.isChecked() is True:
            self.parent._sub_texts_finder[self.sub_text_index].quotes_ocr = True
        else:
            self.parent._sub_texts_finder[self.sub_text_index].quotes_ocr = False
        
    def check_text_2(self):
        if not os.path.exists(self.parent._path):
            os.makedirs(self.parent._path)
        image_name = self.parent._path + os.sep + time.strftime("text_finder_%d_%m_%y_%H_%M_%S_temp_img.png")
        self.parent._bg_pixmap.save(image_name,"PNG", -1)
        time.sleep(0.05)
        cv_image = cv2.imread(image_name)
        #print cv_image
        #time.sleep(0.1)
        os.remove(image_name)
        text_finder = TextFinder()
        text_finder.set_source_image_color(cv_image)
            
        roi_x = self.parent._main_text.x + self.parent._sub_texts_finder[self.sub_text_index].roi_x #self.parent._sub_texts_finder[self.sub_text_index].roi_x # - self.parent._main_text.x
        roi_y = absolute_sub_roi_y = self.parent._main_text.y + self.parent._sub_texts_finder[self.sub_text_index].roi_y #self.parent._sub_texts_finder[self.sub_text_index].roi_y #- self.parent._main_text.x
        roi_width = self.parent._sub_texts_finder[self.sub_text_index].roi_width
        roi_height = self.parent._sub_texts_finder[self.sub_text_index].roi_height
        
        text_finder.set_main_component({"text":str(self.parent._sub_texts_finder[self.sub_text_index].text), "lang":str(self.parent._sub_texts_finder[self.sub_text_index].lang), "whitelist":self.parent._sub_texts_finder[self.sub_text_index].whitelist},
                                       {"roi_x":roi_x, "roi_y":roi_y, "roi_width":roi_width, "roi_height":roi_height})
                                       
        text_finder.find()
        text = text_finder.get_last_read()
        
        result = text_finder.get_result(0)
        
        result_flag = False
        if result != None:
            result_flag = True
        
        self.check_window = AlyvixTextCheck(text, result_flag)
        self.check_window.show()
        
    @pyqtSlot(QString)
    def inserttext_event_2(self, text):
        if self.inserttext_2.text() == "Insert here the Keystroke to send":
            self.parent._sub_texts_finder[self.sub_text_index].sendkeys = "".encode('utf-8')
        else:
            self.parent._sub_texts_finder[self.sub_text_index].sendkeys = str(text.toUtf8())

            
    @pyqtSlot(QString)    
    def lineEditText_2_event(self, text):
        if text == "Type here the Text to find":
            self.parent._sub_texts_finder[self.sub_text_index].text = "".encode('utf-8')
        else:
            self.parent._sub_texts_finder[self.sub_text_index].text = str(text.toUtf8())
            
    @pyqtSlot(QString)    
    def lineEditLang2_event(self, text):
        if text == "Type here the Text to find":
            self.parent._sub_texts_finder[self.sub_text_index].lang = "".encode('utf-8')
        else:
            self.parent._sub_texts_finder[self.sub_text_index].lang = str(text.toUtf8())
            
    @pyqtSlot(QString)    
    def lineEditWhiteList2_event(self, text):
        if text == "Type here the Text to find":
            self.parent._sub_texts_finder[self.sub_text_index].whitelist = "".encode('utf-8')
        else:
            self.parent._sub_texts_finder[self.sub_text_index].whitelist = str(text.toUtf8())
            
    def min_width_spinbox_change_event_2(self, event):
        self.parent._sub_texts_finder[self.sub_text_index].min_width = self.min_width_spinbox_2.value()
        
        if self.parent._sub_texts_finder[self.sub_text_index].min_width > self.parent._sub_texts_finder[self.sub_text_index].max_width:
            self.parent._sub_texts_finder[self.sub_text_index].min_width = self.parent._sub_texts_finder[self.sub_text_index].max_width   
            self.min_width_spinbox_2.setValue(self.parent._sub_texts_finder[self.sub_text_index].min_width)
        
        self.parent.update()
        
    def max_width_spinbox_change_event_2(self, event):
        
        if self.max_width_spinbox_2.value() < self.min_width_spinbox_2.value():
            self.max_width_spinbox_2.setValue(self.parent._sub_texts_finder[self.sub_text_index].min_width)
            return
            
        self.parent._sub_texts_finder[self.sub_text_index].max_width = self.max_width_spinbox_2.value()
        self.parent.update()
        
    def min_height_spinbox_change_event_2(self, event):
        self.parent._sub_texts_finder[self.sub_text_index].min_height = self.min_height_spinbox_2.value()
        
        if self.parent._sub_texts_finder[self.sub_text_index].min_height > self.parent._sub_texts_finder[self.sub_text_index].max_height:
            self.parent._sub_texts_finder[self.sub_text_index].min_height = self.parent._sub_texts_finder[self.sub_text_index].max_height
            self.min_height_spinbox_2.setValue(self.parent._sub_texts_finder[self.sub_text_index].min_height)

        self.parent.update()
        
    def max_height_spinbox_change_event_2(self, event):
        
        if self.max_height_spinbox_2.value() < self.min_height_spinbox_2.value():
            self.max_height_spinbox_2.setValue(self.parent._sub_texts_finder[self.sub_text_index].min_height)
            return
            
        self.parent._sub_texts_finder[self.sub_text_index].max_height = self.max_height_spinbox_2.value()
        self.parent.update()
        
    def show_min_max_event_2(self, event):
        if self.show_min_max_2.isChecked() is True:
            self.parent._sub_texts_finder[self.sub_text_index].show_min_max = True
            self.show_tolerance_2.setChecked(False)
        else:
            self.parent._sub_texts_finder[self.sub_text_index].show_min_max  = False
        self.parent.update()
        
    def show_tolerance_event_2(self, event):
        if self.show_tolerance_2.isChecked() is True:
            self.parent._sub_texts_finder[self.sub_text_index].show_tolerance = True
            self.show_min_max_2.setChecked(False)
        else:
            self.parent._sub_texts_finder[self.sub_text_index].show_tolerance = False
        self.parent.update()
        
    def height_tolerance_spinbox_event_2(self, event):
        self.parent._sub_texts_finder[self.sub_text_index].height_tolerance = self.height_tolerance_spinbox_2.value()
        self.parent.update()
        
    def width_tolerance_spinbox_event_2(self, event):
        self.parent._sub_texts_finder[self.sub_text_index].width_tolerance = self.width_tolerance_spinbox_2.value()
        self.parent.update()
        
    def use_tolerance_event_2(self, event):
        pass   
            
    def roi_x_spinbox_event(self, event):
        """
        if self.roi_x_spinbox.value() > self.parent._sub_texts_finder[self.sub_text_index].x:
            self.roi_x_spinbox.setValue(self.parent._sub_texts_finder[self.sub_text_index].roi_x)
            return
            
        if self.roi_x_spinbox.value() + self.roi_width_spinbox.value() < self.parent._sub_texts_finder[self.sub_text_index].x + self.parent._sub_texts_finder[self.sub_text_index].width:
            self.roi_x_spinbox.setValue(self.parent._sub_texts_finder[self.sub_text_index].roi_x)
            return
        """
        
        self.parent._sub_texts_finder[self.sub_text_index].roi_x = self.roi_x_spinbox.value()
        self.parent.update()
        
    def roi_y_spinbox_event(self, event):            
        self.parent._sub_texts_finder[self.sub_text_index].roi_y = self.roi_y_spinbox.value()
        self.parent.update()
        
    def roi_width_spinbox_event(self, event):
        """
        if self.roi_x_spinbox.value() + self.roi_width_spinbox.value() < self.parent._sub_texts_finder[self.sub_text_index].x + self.parent._sub_texts_finder[self.sub_text_index].width:
            self.roi_width_spinbox.setValue(self.parent._sub_texts_finder[self.sub_text_index].roi_width)
            return
        """
        self.parent._sub_texts_finder[self.sub_text_index].roi_width = self.roi_width_spinbox.value()
        self.parent.update()
        
    def roi_height_spinbox_event(self, event):
        self.parent._sub_texts_finder[self.sub_text_index].roi_height = self.roi_height_spinbox.value()
        self.parent.update()
        
    def use_min_max_event_2(self, event):
        if event is False:
            self.height_tolerance_spinbox_2.setEnabled(True)
            self.width_tolerance_spinbox_2.setEnabled(True)
            self.height_tolerance_label_2.setEnabled(True)
            self.width_tolerance_label_2.setEnabled(True)
            
            self.min_height_label_2.setEnabled(False)
            self.max_height_label_2.setEnabled(False)
            self.min_width_label_2.setEnabled(False)
            self.max_width_label_2.setEnabled(False)
            self.min_height_spinbox_2.setEnabled(False)
            self.max_height_spinbox_2.setEnabled(False)
            self.min_width_spinbox_2.setEnabled(False)
            self.max_width_spinbox_2.setEnabled(False)
            
            self.parent._sub_texts_finder[self.sub_text_index].use_min_max = False
            self.parent._sub_texts_finder[self.sub_text_index].use_tolerance = True
            
            
        else:
            self.height_tolerance_spinbox_2.setEnabled(False)
            self.width_tolerance_spinbox_2.setEnabled(False)
            self.height_tolerance_label_2.setEnabled(False)
            self.width_tolerance_label_2.setEnabled(False)
            
            self.min_height_label_2.setEnabled(True)
            self.max_height_label_2.setEnabled(True)
            self.min_width_label_2.setEnabled(True)
            self.max_width_label_2.setEnabled(True)
            self.min_height_spinbox_2.setEnabled(True)
            self.max_height_spinbox_2.setEnabled(True)
            self.min_width_spinbox_2.setEnabled(True)
            self.max_width_spinbox_2.setEnabled(True)
            
            self.parent._sub_texts_finder[self.sub_text_index].use_min_max = True
            self.parent._sub_texts_finder[self.sub_text_index].use_tolerance = False
            
    def clickRadio_event_2(self, event):
        if event is False:
            self.parent._sub_texts_finder[self.sub_text_index].click = False
        else:
            self.parent._sub_texts_finder[self.sub_text_index].click = True
            self.pushButtonXYoffset_2.setEnabled(True)
            
        self.parent.update()
        
    def doubleclickRadio_event_2(self, event):
        if event is False:
            self.parent._sub_texts_finder[self.sub_text_index].doubleclick = False
        else:
            self.parent._sub_texts_finder[self.sub_text_index].doubleclick = True 
            self.pushButtonXYoffset_2.setEnabled(True)
            
        self.parent.update()
            
                        
    def movemouseRadio_event_2(self, event):
        if event is False:
            self.parent._sub_texts_finder[self.sub_text_index].mousemove = False
        else:
            self.parent._sub_texts_finder[self.sub_text_index].mousemove = True 
            self.pushButtonXYoffset_2.setEnabled(True)
            
        self.parent.update()
            
    def rightclickRadio_event_2(self, event):
        if event is False:
            self.parent._sub_texts_finder[self.sub_text_index].rightclick = False
        else:
            self.parent._sub_texts_finder[self.sub_text_index].rightclick = True 
            self.pushButtonXYoffset_2.setEnabled(True)
            
        self.parent.update()
             
    def dontclickRadio_event_2(self, event):
        if event is True:
            self.parent._sub_texts_finder[self.sub_text_index].click = False
            self.parent._sub_texts_finder[self.sub_text_index].doubleclick = False
            self.parent._sub_texts_finder[self.sub_text_index].rightclick = False
            self.parent._sub_texts_finder[self.sub_text_index].mousemove = False
            self.pushButtonXYoffset_2.setEnabled(False)
            
        self.parent.update()
            
    def pushButtonXYoffset_event_2(self):
        self.parent.set_xy_offset = self.sub_text_index  #-1 for main, other int for sub index
        self.hide()
            

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
        
class AlyvixTextCheck(QDialog, Ui_Form_Text):
    def __init__(self, text, check_result):
        QDialog.__init__(self)

        # Set up the user interface from Designer.
        self.setupUi(self)
                        
        #self.text = text
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        if check_result is False:
            self.labelCheckResult.setText("CRITICAL:  Your regular expression doesn't match with text found!")
        
        self.plainTextEdit.setPlainText(text)
        self.plainTextEdit.setReadOnly(True)
        
        self.connect(self.pushButtonOk, SIGNAL("clicked()"), self.button_ok_event)
        
    def button_ok_event(self):
        self.close()
     
     
class CheckSyntax(ast.NodeVisitor):

    def __init__(self):
        self.var_list = []

    def generic_visit(self, node):
        #print type(node).__name__
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Name(self, node):
        #print 'Name:', node.id
        self.var_list.append(node.id)
        
    def check(self, node, arg_list):
        self.visit(node)
        
        var_not_in_arg = []
        
        for var in self.var_list:
        
            if var not in arg_list:
                var_not_in_arg.append(var)
                
        str = ""
        for var in var_not_in_arg:
            str = str + var + ", "
            
        if str != "":
            return str[:-2]
        else:
            return None