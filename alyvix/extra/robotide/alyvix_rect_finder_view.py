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
import ast
import time
import cv2
import copy
import codecs
import re

import time

from PyQt4.QtGui import QApplication, QWidget, QCursor, QImage, QPainter, QPainter, QPen, QColor, QPixmap, QBrush, QPainterPath, QDialog, QListWidgetItem , QTextEdit, QHBoxLayout, QTextCharFormat, QMessageBox, QFont, QFontMetrics, QTextCursor
from PyQt4.QtCore import Qt, QThread, SIGNAL, QTimer, QUrl, QPoint, QRect, QModelIndex, SLOT, pyqtSlot, QString, QChar
from PyQt4.Qt import QFrame

from PyQt4.QtWebKit import QWebSettings

#from alyvix.tools.screen import ScreenCapture
#from alyvix.finders.rectfinder import RectFinder
from alyvix_rect_finder_properties_view import Ui_Form
#from alyvix_rect_finder_properties_view_2 import Ui_Form
#from alyvix_rect_finder_properties_view_3 import Ui_Form as Ui_Form_2

import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET

from distutils.sysconfig import get_python_lib


class AlyvixRectFinderView(QWidget):

    def __init__(self, parent):
        QWidget.__init__(self)
        #self.setupUi(self)
        
        self.parent = parent
        
        self.object_name = ""
        self.wait = True
        self.find = False
        self.wait_disapp = False
        self.args_number = 0
        self.timeout = 20
        self.timeout_exception = True
        self.enable_performance = True
        self.warning = 10.00
        self.critical = 15.00
        
        self.parent_is_objfinder = False
        
        self.mouse_or_key_is_set = False
        
        self.setMouseTracking(True)
        
        self._bg_pixmap = QPixmap()
        self.__capturing = False
        
        self.__click_position = QPoint(0,0)
        
        self._main_rect_finder = None
        
        self._sub_rects_finder = []
        
        self.__deleted_rects = []
        
        self.last_view_index = 0
        
        #flags
        #self.__flag_mouse_left_button_is_pressed = False
        self.__flag_mouse_is_inside_rect = False
        self.__flag_capturing_main_rect = True
        self.__flag_capturing_sub_rect_roi = False
        self.__flag_capturing_sub_rect = False
        self.__flag_need_to_delete_roi = False
        self.__flag_need_to_restore_roi = False
        self._flag_show_min_max = False
        self.set_xy_offset = None  #-1 for main, other int for sub index
        self.last_xy_offset_index = None
        self._old_min_width = None
        self._old_min_height = None
        self._self_show_tolerance = False

        self.__index_deleted_rect_inside_roi = -1
        self.__restored_rect_roi = False
        
                
        self._xml_name = self.parent.xml_name
        self._path = self.parent.path
        self._robot_file_name = self.parent.robot_file_name
        #self._alyvix_proxy_path = os.getenv("ALYVIX_HOME") + os.sep + "robotproxy"
        self._alyvix_proxy_path = get_python_lib() + os.sep + "alyvix" + os.sep + "robotproxy"
        self.action = self.parent.action
        
        self._code_lines = []
        self._code_lines_for_object_finder = []
        self._code_blocks = []
        
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        #self.update_path_and_name(path)
        
        self.build_objects()
        self.old_mouse_or_key_is_set = self.mouse_or_key_is_set
        self.__old_code_v220 = self.get_old_code_v220()
        self.__old_code_v230 = self.get_old_code_v230()
        self.__old_code_v250 = self.get_old_code_v250()
        #text_file = open("Output.txt", "w")
        #text_file.write(self.__old_code_v250)
        #text_file.close()
        self.__old_code = self.get_old_code()
        self.mouse_or_key_is_set = self.old_mouse_or_key_is_set
        #print self.__old_code
        
        self._old_main_rect = copy.deepcopy(self._main_rect_finder)
        self._old_sub_rects = copy.deepcopy(self._sub_rects_finder)
        
        self.esc_pressed = False
        self.ok_pressed = False

    """
    def update_path_and_name(self, path):
        lines = path.split(os.sep)
        self._path = ""
        
        cnt = 0
        for line in lines:
        
            if cnt == len(lines) - 1:
                break
            self._path = self._path + line + os.sep
            cnt = cnt + 1
        
        self._robot_file_name = lines[len(lines) - 1]
        self._robot_file_name = self._robot_file_name.split('.')[0]
        self._robot_file_name = "AlyvixProxy" + self._robot_file_name
        
        self._path = self._path[:-1] + os.sep + "Alyvix" + lines[len(lines) - 1].split('.')[0] + "Objects"
        if not os.path.exists(self._path):
            os.makedirs(self._path)
        
        #print self._path
        #print self._robot_file_name
        #print self._test_case_path
    """
        
    def set_bg_pixmap(self, image):
        self._bg_pixmap = QPixmap.fromImage(image)
        
    def save_all(self):
        if self._main_rect_finder != None and self.ok_pressed is False:
            self.ok_pressed = True
            #print "dummy"
            self.build_xml()
            #self.build_code()
            self.build_code_array()
            self.save_python_file()
            #self.build_perf_data_xml()
            self._bg_pixmap.save(self._path + os.sep + self.object_name + "_RectFinder.png","PNG", -1)
            if self.action == "new":
                #print "add_new"
                self.parent.add_new_item_on_list()
                
        try:
            if self.parent.parent.is_object_finder_menu:
            
                sel_index = self.parent.parent.last_selected_index
                
                obj_main_redraw = False
                obj_sub_redraw = False
                
                if sel_index == 0:
                    if self.parent.parent._main_object_finder.x != self._main_rect_finder.x or self.parent.parent._main_object_finder.y != self._main_rect_finder.y or self.parent.parent._main_object_finder.height != self._main_rect_finder.height or self.parent.parent._main_object_finder.width != self._main_rect_finder.width:
                        obj_main_redraw = True
                    self.parent.parent._main_object_finder.x = self._main_rect_finder.x
                    self.parent.parent._main_object_finder.y = self._main_rect_finder.y
                    self.parent.parent._main_object_finder.height = self._main_rect_finder.height
                    self.parent.parent._main_object_finder.width = self._main_rect_finder.width
                else:
                    if self.parent.parent._sub_objects_finder[sel_index-1].x != self._main_rect_finder.x or self.parent.parent._sub_objects_finder[sel_index-1].y != self._main_rect_finder.y or self.parent.parent._sub_objects_finder[sel_index-1].height != self._main_rect_finder.height or self.parent.parent._sub_objects_finder[sel_index-1].width != self._main_rect_finder.width:
                        obj_sub_redraw = True
                    self.parent.parent._sub_objects_finder[sel_index-1].x = self._main_rect_finder.x
                    self.parent.parent._sub_objects_finder[sel_index-1].y = self._main_rect_finder.y
                    self.parent.parent._sub_objects_finder[sel_index-1].height = self._main_rect_finder.height
                    self.parent.parent._sub_objects_finder[sel_index-1].width = self._main_rect_finder.width
                    
                    self.parent.parent._sub_objects_finder[sel_index-1].roi_x = 0
                    self.parent.parent._sub_objects_finder[sel_index-1].roi_y = 0
                    self.parent.parent._sub_objects_finder[sel_index-1].roi_height = 0
                    self.parent.parent._sub_objects_finder[sel_index-1].roi_width = 0
                    self.parent.parent._sub_objects_finder[sel_index-1].roi_unlimited_up = False
                    self.parent.parent._sub_objects_finder[sel_index-1].roi_unlimited_down = False
                    self.parent.parent._sub_objects_finder[sel_index-1].roi_unlimited_left = False
                    self.parent.parent._sub_objects_finder[sel_index-1].roi_unlimited_right = False
                    
                    self.parent.parent.redraw_index_from_finder = sel_index-1
                
                try:
                    #self.parent.parent.pv.showFullScreen()
                    if obj_main_redraw is True:
                        self.parent.parent.delete_all_sub_roi()
                        #self.parent.parent.pv = PaintingView(self.parent.parent)
                        #image = QImage(self.parent.parent._main_object_finder.xml_path.replace("xml", "png"))   
                        #self.parent.parent.pv.set_bg_pixmap(image)
                        self.parent.parent._main_deleted = True
                        self.parent.parent.pv.showFullScreen()
                    elif obj_sub_redraw is True:
                        self.parent.parent.sub_object_index = sel_index-1
                        self.parent.parent.redraw_roi_event()
                    else:
                        self.parent.parent.pv.update()
                    sel_index = None
                except:
                    pass
            
                if self.mouse_or_key_is_set is True:
                    
                    self.parent.parent._main_object_finder.mouse_or_key_is_set = True
                    #print "build_objjjjjjjjjjjjjjjjjjjjj"
        except:
            pass
            
        self.parent.show()
        self.close()
        
    def cancel_all(self):
        self._main_rect_finder = copy.deepcopy(self._old_main_rect)
        self._sub_rects_finder = copy.deepcopy(self._old_sub_rects)
        self.parent.show()
        self.close()
        
    def keyPressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Z: 
            if self.set_xy_offset is None:
                self.delete_rect()

        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Y:
            self.restore_rect()
        if event.key() == Qt.Key_Escape:
            #print len(self._sub_rects_finder)
            #print self._main_rect_finder
            if len(self._sub_rects_finder) == 0 and self._main_rect_finder is None:
                try:
                    self.rect_view_properties.close()
                except:
                    pass
                self.parent.show()
                self.close()
            else:
                if len(self._sub_rects_finder) > 0:
            
                    index = -1 #self.__index_deleted_rect_inside_roi
                    if self._sub_rects_finder[index].x == 0 and self._sub_rects_finder[index].y == 0 \
                        and self._sub_rects_finder[index].width == 0 and self._sub_rects_finder[index].height == 0:

                        del self._sub_rects_finder[-1]
                        self.__flag_need_to_delete_roi = False
                        self.__flag_need_to_restore_roi = True
                        self.__flag_capturing_sub_rect_roi = True
                        self.__flag_capturing_sub_rect = False
                self.set_xy_offset = None
                self.rect_view_properties = AlyvixRectFinderPropertiesView(self)
                self.rect_view_properties.show()
            """
            if self._main_rect_finder is None and self.esc_pressed is False:
                self.esc_pressed = True
                try:
                    self.rect_view_properties.close()
                except:
                    pass
                self.parent.show()
                self.close()
            elif self.set_xy_offset is not None:
                if self.set_xy_offset == -1:
                    self._main_rect_finder.x_offset = None
                    self._main_rect_finder.y_offset = None
                else:
                    self._sub_rects_finder[self.set_xy_offset].x_offset = None
                    self._sub_rects_finder[self.set_xy_offset].y_offset = None
                self.set_xy_offset = None
                self.last_xy_offset_index = None
                self.update()
                self.rect_view_properties = AlyvixRectFinderPropertiesView(self)
                self.rect_view_properties.show()
            """
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_O: #and self.set_xy_offset is None:
            #print len(self._sub_rects_finder)
            #print self._main_rect_finder
            if len(self._sub_rects_finder) == 0 and self._main_rect_finder is None:
                try:
                    self.rect_view_properties.close()
                except:
                    pass
                self.parent.show()
                self.close()
            else:
                if len(self._sub_rects_finder) > 0:
            
                    index = -1 #self.__index_deleted_rect_inside_roi
                    if self._sub_rects_finder[index].x == 0 and self._sub_rects_finder[index].y == 0 \
                        and self._sub_rects_finder[index].width == 0 and self._sub_rects_finder[index].height == 0:

                        del self._sub_rects_finder[-1]
                        self.__flag_need_to_delete_roi = False
                        self.__flag_need_to_restore_roi = True
                        self.__flag_capturing_sub_rect_roi = True
                        self.__flag_capturing_sub_rect = False
                self.set_xy_offset = None
                self.rect_view_properties = AlyvixRectFinderPropertiesView(self)
                self.rect_view_properties.show()
                
        if event.key() == Qt.Key_Down:
        
            if self.__flag_capturing_sub_rect == True:
                self._sub_rects_finder[-1].roi_unlimited_down = True
                self.update()
                
        if event.key() == Qt.Key_Up:
        
            if self.__flag_capturing_sub_rect == True:
                self._sub_rects_finder[-1].roi_unlimited_up = True
                self.update()
                
        if event.key() == Qt.Key_Left:
        
            if self.__flag_capturing_sub_rect == True:
                self._sub_rects_finder[-1].roi_unlimited_left = True
                self.update()
                
        if event.key() == Qt.Key_Right:
        
            if self.__flag_capturing_sub_rect == True:
                self._sub_rects_finder[-1].roi_unlimited_right = True
                self.update()
                
            """
            self.parent.show()
            self.close()
            
            if self._main_rect_finder != None and self.esc_pressed is False:
                self.esc_pressed = True
                #print "dummy"
                self.build_xml()
                #self.build_code()
                self.build_code_array()
                self.save_python_file()
                self.build_perf_data_xml()
                self._bg_pixmap.save(self._path + os.sep + self.object_name + "_RectFinder.png","PNG", -1)
                if self.action == "new":
                    self.parent.add_new_item_on_list()
            self.parent.show()
            self.close()
            """
            
            
    def closeEvent(self, event):
        self.close
        
    def mouseMoveEvent(self, event):
        self.update()
        
    def mouseDoubleClickEvent(self, event):
        if False is True:
            #self.BringWindowToFront()
            return
        if self.is_mouse_inside_rect(self._main_rect_finder) and self.set_xy_offset is None:
            if len(self._sub_rects_finder) > 0:

                index = -1 #self.__index_deleted_rect_inside_roi
                if self._sub_rects_finder[index].x == 0 and self._sub_rects_finder[index].y == 0 \
                    and self._sub_rects_finder[index].width == 0 and self._sub_rects_finder[index].height == 0:

                    del self._sub_rects_finder[-1]
                    self.__flag_need_to_delete_roi = False
                    self.__flag_need_to_restore_roi = True
                    self.__flag_capturing_sub_rect_roi = True
                    self.__flag_capturing_sub_rect = False
            self.rect_view_properties = AlyvixRectFinderPropertiesView(self)
            self.rect_view_properties.show()
        
    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
        
            self.__click_position = QPoint(QCursor.pos())
            
            if self.set_xy_offset is not None:
                if self.set_xy_offset == -1:
                    self._main_rect_finder.x_offset = self.__click_position.x() - self._main_rect_finder.x
                    self._main_rect_finder.y_offset = self.__click_position.y() - self._main_rect_finder.y
                else:
                    self._sub_rects_finder[self.set_xy_offset].x_offset = self.__click_position.x() - self._sub_rects_finder[self.set_xy_offset].x
                    self._sub_rects_finder[self.set_xy_offset].y_offset = self.__click_position.y() - self._sub_rects_finder[self.set_xy_offset].y
            else:
                self.__capturing = True
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.__capturing = False
            
            if self.set_xy_offset is not None:
                self.last_xy_offset_index = self.set_xy_offset
                #self.set_xy_offset = None
                
            elif self.__flag_capturing_main_rect is True:
                self.last_xy_offset_index = None
                self.__flag_capturing_main_rect = False
                self.__flag_capturing_sub_rect_roi = True
                self.add_main_rect()
            elif self.__flag_capturing_sub_rect_roi is True:
                self.last_xy_offset_index = None
                self.__flag_capturing_sub_rect_roi = False
                self.__flag_capturing_sub_rect = True
                self.__flag_need_to_delete_roi = True
                if len(self.__deleted_rects) > 0:
                    del self.__deleted_rects[-1]
                self.add_sub_rect_roi()
            elif self.__flag_capturing_sub_rect is True:
                self.last_xy_offset_index = None
                self.__flag_capturing_sub_rect = False
                self.__flag_capturing_sub_rect_roi = True
                self.__flag_need_to_delete_roi = False
                self.add_sub_rect_attributes()
            
        self.update()
        

        
    def paintEvent(self, event):
    
        qp = QPainter()
        qp.begin(self)
        qp.drawPixmap(0, 0, self._bg_pixmap)
        
        self.__flag_mouse_is_inside_rect = False
        self.__index_of_rectangle_with_mouse_inside = -2
        
        if self._main_rect_finder is not None:
            
            self.draw_main_rectangle(qp)
            
            if self.is_mouse_inside_rect(self._main_rect_finder):
                self.__flag_mouse_is_inside_rect = True
        
        rect_index = 0
        #self.__sub_rect_color_index = 0
        for sub_rect_finder in self._sub_rects_finder:
        
            self.draw_sub_rectangle(qp, sub_rect_finder)
            
            if self.is_mouse_inside_rect(sub_rect_finder):
                self.__flag_mouse_is_inside_rect = True
 
        
        if self.set_xy_offset is None:
            if self.__capturing is False:
                self.draw_cross_lines(qp)
            elif self.set_xy_offset is not None:
                pass
            elif self.__flag_capturing_main_rect is True:
                self.draw_capturing_rectangle_lines(qp)
            elif self.__flag_capturing_sub_rect_roi is True:
                self.draw_capturing_roi_lines(qp)
            elif self.__flag_capturing_sub_rect is True:
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
 
    def draw_main_rectangle(self, qp):
    
            if self._main_rect_finder.show is False:
                return
    
            if self._main_rect_finder.show_min_max is False and self._main_rect_finder.show_tolerance is False:
                pen = QPen()
                pen.setBrush(QColor(255, 0, 0, 255))
                pen.setWidth(1)
                qp.setPen(pen)
                
                qp.fillRect(self._main_rect_finder.x,
                    self._main_rect_finder.y,
                    self._main_rect_finder.width,
                    self._main_rect_finder.height,
                    QBrush(QColor(255, 0, 255, 130)))
                    
                qp.drawRect(QRect(self._main_rect_finder.x,
                    self._main_rect_finder.y,
                    self._main_rect_finder.width,
                    self._main_rect_finder.height))  
                    
                if self._main_rect_finder.click is True or self._main_rect_finder.rightclick is True or self._main_rect_finder.mousemove is True or self._main_rect_finder.hold_and_release is not None:
                    if self._main_rect_finder.x_offset is None and self._main_rect_finder.y_offset is None:
                        click_pos = QPoint(self._main_rect_finder.x + (self._main_rect_finder.width/2), self._main_rect_finder.y + (self._main_rect_finder.height/2))
                    else:
                        click_pos = QPoint(self._main_rect_finder.x + self._main_rect_finder.x_offset, self._main_rect_finder.y + self._main_rect_finder.y_offset)
                        
                    old_brush = qp.brush()
                        
                    qp.setBrush(QColor(255, 0, 255, 130))
                    qp.drawLine(self._main_rect_finder.x + (self._main_rect_finder.width/2), self._main_rect_finder.y + (self._main_rect_finder.height/2), click_pos.x(), click_pos.y())
                    qp.drawEllipse(click_pos, 10, 10)
                    qp.setBrush(old_brush)
            
            elif self._main_rect_finder.show_min_max is True:
                pen = QPen()
                pen.setBrush(QColor(108, 0, 255, 255))
                pen.setWidth(1)
                qp.setPen(pen)
                
                OuterPath = QPainterPath()
                OuterPath.setFillRule(Qt.WindingFill)
                
                min_width = self._main_rect_finder.min_width
                min_height = self._main_rect_finder.min_height
                    
                if self._main_rect_finder.min_width > self._main_rect_finder.max_width:
                
                    #self._main_rect_finder.min_width = self._main_rect_finder.max_width
                    min_width = self._main_rect_finder.max_width
                    #self.rect_view_properties.min_width_spinbox.setValue(min_width)

            
                if self._main_rect_finder.min_height > self._main_rect_finder.max_height:
                                        
                    #self._main_rect_finder.min_height = self._main_rect_finder.max_height
                    min_height  = self._main_rect_finder.max_height
                    #self.rect_view_properties.min_height_spinbox.setValue(min_height)
                    
                
                """
                    if self._old_min_height is None:
                        self._old_min_height = self._main_rect_finder.min_height
                        
                    self._main_rect_finder.min_height = self._main_rect_finder.max_height
                    min_height  = self._main_rect_finder.min_height
                    
                else:
                    if self._old_min_height is not None:
                        self._main_rect_finder.min_height = self._old_min_height
                        min_height = self._main_rect_finder.min_height 
                        self._old_min_height  = None
                """
                
                OuterPath.addRect(self._main_rect_finder.x,
                    self._main_rect_finder.y,
                    self._main_rect_finder.max_width,
                    self._main_rect_finder.max_height)
                
                InnerPath = QPainterPath()
                InnerPath.addRect(self._main_rect_finder.x,
                self._main_rect_finder.y,
                min_width,
                min_height)
                
                FillPath = OuterPath.subtracted(InnerPath)
                #qp.fillPath(FillPath, QBrush(QColor(255, 0, 0, 255), Qt.DiagCrossPattern))
                
                
                qp.drawRect(QRect(self._main_rect_finder.x,
                    self._main_rect_finder.y,
                    min_width,
                    min_height))  
                    
                qp.drawRect(QRect(self._main_rect_finder.x,
                    self._main_rect_finder.y,
                    self._main_rect_finder.max_width,
                    self._main_rect_finder.max_height))  
                    
                qp.fillPath(FillPath, QBrush(QColor(118, 21, 227, 130)))
                  
                """
                qp.fillRect(rect_finder.x,
                    rect_finder.y,
                    rect_finder.width,
                    rect_finder.height,
                    QBrush(QColor(172, 96, 246, 130)))
                    
                qp.drawRect(QRect(rect_finder.x,
                    rect_finder.y,
                    rect_finder.width,
                    rect_finder.height))
                """
                """
                qp.fillRect(self._main_rect_finder.x,
                    self._main_rect_finder.y,
                    self._main_rect_finder.min_width,
                    self._main_rect_finder.min_height,
                    QBrush(QColor(255, 0, 255, 130)))
                    
                qp.drawRect(QRect(self._main_rect_finder.x,
                    self._main_rect_finder.y,
                    self._main_rect_finder.min_width,
                    self._main_rect_finder.min_height))  
                    
                qp.fillRect(self._main_rect_finder.x,
                    self._main_rect_finder.y,
                    self._main_rect_finder.max_width,
                    self._main_rect_finder.max_height,
                    QBrush(QColor(255, 0, 255, 130)))
                    
                qp.drawRect(QRect(self._main_rect_finder.x,
                    self._main_rect_finder.y,
                    self._main_rect_finder.max_width,
                    self._main_rect_finder.max_height))  
                """
            elif self._main_rect_finder.show_tolerance is True: 
                
                pen = QPen()
                pen.setBrush(QColor(108, 0, 255, 255))
                pen.setWidth(1)
                qp.setPen(pen)

                OuterPath_tolerance = QPainterPath()
                OuterPath_tolerance.setFillRule(Qt.WindingFill)

                OuterPath_tolerance.addRect(self._main_rect_finder.x - self._main_rect_finder.width_tolerance,
                    self._main_rect_finder.y - self._main_rect_finder.height_tolerance,
                    self._main_rect_finder.width + (self._main_rect_finder.width_tolerance * 2),
                    self._main_rect_finder.height + (self._main_rect_finder.height_tolerance * 2))

                if self._main_rect_finder.width >= (self._main_rect_finder.width_tolerance * 2) and self._main_rect_finder.height >= (self._main_rect_finder.height_tolerance * 2):
                    InnerPath_tolerance = QPainterPath()

                    InnerPath_tolerance.addRect(self._main_rect_finder.x + self._main_rect_finder.width_tolerance,
                        self._main_rect_finder.y + self._main_rect_finder.height_tolerance,
                        self._main_rect_finder.width - (self._main_rect_finder.width_tolerance * 2),
                        self._main_rect_finder.height - (self._main_rect_finder.height_tolerance * 2))

                    FillPath = OuterPath_tolerance.subtracted(InnerPath_tolerance)
                    qp.fillPath(FillPath, QColor(118, 21, 227, 130))
                else:
                    qp.fillPath(OuterPath_tolerance, QColor(118, 21, 227, 130))
                    
                pen.setWidth(1)
                #pen.setStyle(Qt.DashLine)
                qp.setPen(pen)

                qp.drawRect(self._main_rect_finder.x - self._main_rect_finder.width_tolerance,
                    self._main_rect_finder.y - self._main_rect_finder.height_tolerance,
                    self._main_rect_finder.width + (self._main_rect_finder.width_tolerance * 2),
                    self._main_rect_finder.height + (self._main_rect_finder.height_tolerance * 2))

                if self._main_rect_finder.width >= (self._main_rect_finder.width_tolerance * 2) and self._main_rect_finder.height >= (self._main_rect_finder.height_tolerance * 2):
                    qp.drawRect(self._main_rect_finder.x + self._main_rect_finder.width_tolerance,
                        self._main_rect_finder.y + self._main_rect_finder.height_tolerance,
                        self._main_rect_finder.width - (self._main_rect_finder.width_tolerance * 2),
                        self._main_rect_finder.height - (self._main_rect_finder.height_tolerance * 2))
                elif self._main_rect_finder.width >= (self._main_rect_finder.width_tolerance * 2):
                    qp.drawLine(self._main_rect_finder.x + self._main_rect_finder.width_tolerance,
                        self._main_rect_finder.y + (self._main_rect_finder.height / 2),
                        self._main_rect_finder.x + self._main_rect_finder.width - self._main_rect_finder.width_tolerance,
                        self._main_rect_finder.y + (self._main_rect_finder.height / 2))
                    #qp.drawLine(self._main_rect_finder.x + 8, self._main_rect_finder.y + (h/2), self._main_rect_finder.x + 8 + 1, self._main_rect_finder.y + (h/2))
                    #qp.drawLine(self._main_rect_finder.x + w - 8, self._main_rect_finder.y + (h/2), self._main_rect_finder.x + w - 8, self._main_rect_finder.y + (h/2))
                    #pen.setStyle(Qt.SolidLine)
                    #qp.setPen(pen)
                    #qp.drawLine(self._main_rect_finder.x + 8, y, self._main_rect_finder.x + 8, self._main_rect_finder.y + h)
                elif self._main_rect_finder.height >= (self._main_rect_finder.height_tolerance * 2):
                    qp.drawLine(self._main_rect_finder.x + (self._main_rect_finder.width / 2),
                        self._main_rect_finder.y + self._main_rect_finder.height_tolerance,
                        self._main_rect_finder.x + (self._main_rect_finder.width / 2),
                        self._main_rect_finder.y + self._main_rect_finder.height - self._main_rect_finder.height_tolerance)
                else:
                    qp.drawLine(self._main_rect_finder.x + (self._main_rect_finder.width / 2),
                        self._main_rect_finder.y + (self._main_rect_finder.height / 2),
                        self._main_rect_finder.x + (self._main_rect_finder.width / 2),
                        self._main_rect_finder.y + (self._main_rect_finder.height / 2))
     
    def draw_sub_rectangle(self, qp, rect_finder):
    
            if rect_finder.show is False:
                return
    
            pen = QPen()
            pen.setWidth(1)
            pen.setStyle(Qt.SolidLine)
            pen.setBrush(QBrush(QColor(255, 0, 198, 255)))
            qp.setPen(pen)
            
            OuterPath_roi = QPainterPath()
            OuterPath_roi.setFillRule(Qt.WindingFill)
            
            roi_x = rect_finder.roi_x + self._main_rect_finder.x
            roi_y = rect_finder.roi_y + self._main_rect_finder.y
            roi_width = rect_finder.roi_width
            roi_height = rect_finder.roi_height

            if rect_finder.roi_unlimited_up is True:
                roi_y = 0
                roi_height = rect_finder.roi_y + self._main_rect_finder.y + roi_height

            if rect_finder.roi_unlimited_down is True:
                if rect_finder.roi_unlimited_up is True:
                    roi_height = self._bg_pixmap.height()-1
                else:
                    roi_height = self._bg_pixmap.height() - (rect_finder.roi_y + self._main_rect_finder.y + 1)
                    
                    print self._bg_pixmap.width(), (rect_finder.roi_x + self._main_rect_finder.x)

            if rect_finder.roi_unlimited_left is True:
                roi_x = 0
                roi_width = rect_finder.roi_x + self._main_rect_finder.x + roi_width

            if rect_finder.roi_unlimited_right is True:
                if rect_finder.roi_unlimited_left is True:
                    roi_width = self._bg_pixmap.width() -1
                else:
                    roi_width = self._bg_pixmap.width() - (rect_finder.roi_x + self._main_rect_finder.x + 1)
            
            OuterPath_roi.addRect(roi_x,
                    roi_y,
                    roi_width,
                    roi_height)
                
            if rect_finder.x != 0 and rect_finder.y != 0:
            
                InnerPath_roi = QPainterPath()
                
                """
                InnerPath_roi.addRect(rect_finder.x,
                    rect_finder.y,
                    rect_finder.width,
                    rect_finder.height)
                """
                
                #FillPath_roi = OuterPath_roi.subtracted(InnerPath_roi)
                #qp.fillPath(FillPath_roi, QBrush(QColor(172, 96, 246, 180), Qt.BDiagPattern))
                    
                if rect_finder.show_min_max is False and rect_finder.show_tolerance is False:

                    InnerPath_roi.addRect(rect_finder.x,
                        rect_finder.y,
                        rect_finder.width,
                        rect_finder.height)
                        
                                                
                    FillPath_roi = OuterPath_roi.subtracted(InnerPath_roi)
                    qp.fillPath(FillPath_roi, QBrush(QColor(172, 96, 246, 180), Qt.BDiagPattern))
                    
                    qp.drawRect(QRect(roi_x,
                        roi_y,
                        roi_width,
                        roi_height))  
                        
                    qp.fillRect(rect_finder.x,
                        rect_finder.y,
                        rect_finder.width,
                        rect_finder.height,
                        QBrush(QColor(172, 96, 246, 130)))
                    
                        
                    qp.drawRect(QRect(rect_finder.x,
                        rect_finder.y,
                        rect_finder.width,
                        rect_finder.height))
                        
                    if rect_finder.click is True or rect_finder.rightclick is True or rect_finder.mousemove is True or rect_finder.hold_and_release is not None:
                        
                        if rect_finder.x_offset is None and rect_finder.y_offset is None:
                            click_pos = QPoint(rect_finder.x + (rect_finder.width/2), rect_finder.y + (rect_finder.height/2))
                        else:
                            click_pos = QPoint(rect_finder.x + rect_finder.x_offset, rect_finder.y + rect_finder.y_offset)
                            
                        old_brush = qp.brush()
                            
                        qp.setBrush(QColor(172, 96, 246, 130))
                        qp.drawLine(rect_finder.x + (rect_finder.width/2), rect_finder.y + (rect_finder.height/2), click_pos.x(), click_pos.y())
                        qp.drawEllipse(click_pos, 10, 10)
                        qp.setBrush(old_brush)
                    
                elif rect_finder.show_min_max is True: 
                                  
                    min_width = rect_finder.min_width
                    min_height = rect_finder.min_height
                    
                    max_width = rect_finder.max_width
                    max_height = rect_finder.max_height
                    
                    if rect_finder.x + rect_finder.max_width > roi_x + roi_width:
                        max_width = roi_width - (rect_finder.x  - roi_x)
                        
                    if rect_finder.y + rect_finder.max_height > roi_y + roi_height:
                        max_height = roi_height - (rect_finder.y  - roi_y)
                    
                    if rect_finder.min_width > max_width:
                        #rect_finder.min_width = max_width
                        min_width = max_width
                        #self.rect_view_properties.min_width_spinbox_2.setValue(min_width)
                        
                    if rect_finder.min_height > max_height:
                        #rect_finder.min_height = max_height
                        #self.rect_view_properties.min_height_spinbox_2.setValue(max_height)
                        min_height = max_height
                        
                    
                    InnerPath_roi.addRect(rect_finder.x,
                        rect_finder.y,
                        max_width,
                        max_height)
                        
                                                
                    FillPath_roi = OuterPath_roi.subtracted(InnerPath_roi)
                    qp.fillPath(FillPath_roi, QBrush(QColor(172, 96, 246, 180), Qt.BDiagPattern))
                    
                    pen = QPen()
                    pen.setBrush(QColor(108, 0, 255, 255))
                    pen.setWidth(1)
                    qp.setPen(pen)
                    
                    OuterPath = QPainterPath()
                    OuterPath.setFillRule(Qt.WindingFill)
                    
                    OuterPath.addRect(rect_finder.x,
                        rect_finder.y,
                        max_width,
                        max_height)
                    
                    InnerPath = QPainterPath()
                    InnerPath.addRect(rect_finder.x,
                    rect_finder.y,
                    min_width,
                    min_height)
                    
                    FillPath = OuterPath.subtracted(InnerPath)
                    
                    qp.drawRect(QRect(rect_finder.x,
                        rect_finder.y,
                        min_width,
                        min_height))  
                        
                    qp.drawRect(QRect(rect_finder.x,
                        rect_finder.y,
                        max_width,
                        max_height))  
                        
                    qp.fillPath(FillPath, QBrush(QColor(118, 21, 227, 130)))
                    
                    qp.drawRect(QRect(roi_x,
                        roi_y,
                        roi_width,
                        roi_height))  

                elif rect_finder.show_tolerance is True: 
                
                    outer_height_tolerance = rect_finder.height + (rect_finder.height_tolerance * 2)
                    outer_width_tolerance = rect_finder.width + (rect_finder.width_tolerance * 2)
                    
                    fill_path_x = rect_finder.x - rect_finder.width_tolerance
                    fill_path_y = rect_finder.y - rect_finder.height_tolerance
                    
                    
                    if fill_path_x < roi_x or fill_path_y < roi_y:
                        if fill_path_x < roi_x:
                            fill_path_x = roi_x
                            
                            if fill_path_x + rect_finder.width + (rect_finder.width_tolerance*2) >= roi_x + roi_width:
                                outer_width_tolerance = roi_width + (roi_x - fill_path_x) 
                            
                        if fill_path_y < roi_y:
                            fill_path_y = roi_y
                            
                            if fill_path_y + rect_finder.height + (rect_finder.height_tolerance*2) >= roi_y + roi_height:
                                outer_height_tolerance = roi_height + (roi_y - fill_path_y) 
                                
                        if rect_finder.x + rect_finder.width + rect_finder.width_tolerance >= roi_x + roi_width:
                            outer_width_tolerance = (roi_width) + (roi_x - fill_path_x) 
                        
                        if rect_finder.y + rect_finder.height + rect_finder.height_tolerance >= roi_y + roi_height:
                            outer_height_tolerance = (roi_height) + (roi_y - fill_path_y) 
                        
                    
                    else:
                        if rect_finder.x + rect_finder.width + rect_finder.width_tolerance >= roi_x + roi_width:
                            outer_width_tolerance = (roi_width) + (roi_x - fill_path_x) 
                        
                        if rect_finder.y + rect_finder.height + rect_finder.height_tolerance >= roi_y + roi_height:
                            outer_height_tolerance = (roi_height) + (roi_y - fill_path_y) 
                    
                
                    FillPath_roi = OuterPath_roi.subtracted(InnerPath_roi)
                    qp.fillPath(FillPath_roi, QBrush(QColor(172, 96, 246, 180), Qt.BDiagPattern))
                    
                    pen = QPen()
                    pen.setBrush(QColor(108, 0, 255, 255))
                    pen.setWidth(1)
                    qp.setPen(pen)

                    OuterPath_tolerance = QPainterPath()
                    OuterPath_tolerance.setFillRule(Qt.WindingFill)

                    OuterPath_tolerance.addRect(fill_path_x,
                        fill_path_y,
                        outer_width_tolerance,
                        outer_height_tolerance)

                    if rect_finder.width >= (rect_finder.width_tolerance * 2) and rect_finder.height >= (rect_finder.height_tolerance * 2):
                        InnerPath_tolerance = QPainterPath()

                        InnerPath_tolerance.addRect(rect_finder.x + rect_finder.width_tolerance,
                            rect_finder.y + rect_finder.height_tolerance,
                            rect_finder.width - (rect_finder.width_tolerance * 2),
                            rect_finder.height - (rect_finder.height_tolerance * 2))

                        FillPath = OuterPath_tolerance.subtracted(InnerPath_tolerance)
                        qp.fillPath(FillPath, QColor(118, 21, 227, 130))
                    else:
                        qp.fillPath(OuterPath_tolerance, QColor(118, 21, 227, 130))
                        
                    pen.setWidth(1)
                    #pen.setStyle(Qt.DashLine)
                    qp.setPen(pen)

                    qp.drawRect(fill_path_x,
                        fill_path_y,
                        outer_width_tolerance,
                        outer_height_tolerance)

                    if rect_finder.width >= (rect_finder.width_tolerance * 2) and rect_finder.height >= (rect_finder.height_tolerance * 2):
                        qp.drawRect(rect_finder.x + rect_finder.width_tolerance,
                            rect_finder.y + rect_finder.height_tolerance,
                            rect_finder.width - (rect_finder.width_tolerance * 2),
                            rect_finder.height - (rect_finder.height_tolerance * 2))
                    elif rect_finder.width >= (rect_finder.width_tolerance * 2):
                        qp.drawLine(rect_finder.x + rect_finder.width_tolerance,
                            rect_finder.y + (rect_finder.height / 2),
                            rect_finder.x + rect_finder.width - rect_finder.width_tolerance,
                            rect_finder.y + (rect_finder.height / 2))
                        #qp.drawLine(rect_finder.x + 8, rect_finder.y + (h/2), rect_finder.x + 8 + 1, rect_finder.y + (h/2))
                        #qp.drawLine(rect_finder.x + w - 8, rect_finder.y + (h/2), rect_finder.x + w - 8, rect_finder.y + (h/2))
                        #pen.setStyle(Qt.SolidLine)
                        #qp.setPen(pen)
                        #qp.drawLine(rect_finder.x + 8, y, rect_finder.x + 8, rect_finder.y + h)
                    elif rect_finder.height >= (rect_finder.height_tolerance * 2):
                        qp.drawLine(rect_finder.x + (rect_finder.width / 2),
                            rect_finder.y + rect_finder.height_tolerance,
                            rect_finder.x + (rect_finder.width / 2),
                            rect_finder.y + rect_finder.height - rect_finder.height_tolerance)
                    else:
                        qp.drawLine(rect_finder.x + (rect_finder.width / 2),
                            rect_finder.y + (rect_finder.height / 2),
                            rect_finder.x + (rect_finder.width / 2),
                            rect_finder.y + (rect_finder.height / 2))
                        
                    qp.drawRect(QRect(roi_x,
                        roi_y,
                        roi_width,
                        roi_height))  
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
            qp.fillRect(rect_finder.x,
                rect_finder.y,
                rect_finder.width,
                rect_finder.height,
                QBrush(QColor(172, 96, 246, 130)))
            
                
            qp.drawRect(QRect(rect_finder.x,
                rect_finder.y,
                rect_finder.width,
                rect_finder.height))
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
        
            rect_finder = MainRectForGui()
            rect_finder.x = x
            rect_finder.y = y
            rect_finder.height = height
            rect_finder.width = width
            rect_finder.min_height = int(height/1.5)
            rect_finder.max_height = int(height*1.5)
            rect_finder.min_width = int(width/1.5)
            rect_finder.max_width = int(width*1.5)
            
            self._main_rect_finder = rect_finder
            
        else:
            self.__flag_capturing_main_rect = True
            self.__flag_capturing_sub_rect_roi = False
            
    def add_sub_rect_roi(self):
    
        rect_attributes = self.convert_mouse_position_into_rect()
        
        if rect_attributes is not None:
        
            x, y, width, height = rect_attributes

            rect_finder = SubRectForGui()                
            rect_finder.roi_x = x - self._main_rect_finder.x
            rect_finder.roi_y = y -self._main_rect_finder.y
            rect_finder.roi_height = height
            rect_finder.roi_width = width
            
            self._sub_rects_finder.append(rect_finder)
            
        else:
            self.__flag_capturing_sub_rect = False
            self.__flag_capturing_sub_rect_roi = True
            
    def add_sub_rect_attributes(self):
    
        rect_attributes = self.convert_mouse_position_into_rect()
        
        if rect_attributes is not None:
        
            x, y, width, height = rect_attributes

            rect_finder = self._sub_rects_finder[-1]
            
       
        if rect_attributes is not None:
        
            x, y, width, height = rect_attributes

            rect_finder = self._sub_rects_finder[-1]
            
            roi_x = rect_finder.roi_x + self._main_rect_finder.x
            roi_y = rect_finder.roi_y + self._main_rect_finder.y
            roi_width = rect_finder.roi_width
            roi_height = rect_finder.roi_height
            
            if rect_finder.roi_unlimited_up is True:
                roi_y = 0
                roi_height = rect_finder.roi_y + self._main_rect_finder.y + roi_height

            if rect_finder.roi_unlimited_down is True:
                if rect_finder.roi_unlimited_up is True:
                    roi_height = self._bg_pixmap.height()-1
                else:
                    roi_height = self._bg_pixmap.height() - (rect_finder.roi_y + self._main_rect_finder.y + 1)
                    
                    print self._bg_pixmap.width(), (rect_finder.roi_x + self._main_rect_finder.x)

            if rect_finder.roi_unlimited_left is True:
                roi_x = 0
                roi_width = rect_finder.roi_x + self._main_rect_finder.x + roi_width

            if rect_finder.roi_unlimited_right is True:
                if rect_finder.roi_unlimited_left is True:
                    roi_width = self._bg_pixmap.width() -1
                else:
                    roi_width = self._bg_pixmap.width() - (rect_finder.roi_x + self._main_rect_finder.x + 1)
            
            
            if (x + width > roi_x + roi_width) or (x < roi_x) or \
                (y + height > roi_y + roi_height) or (y < roi_y):
                self.__flag_capturing_sub_rect = True
                self.__flag_capturing_sub_rect_roi = False
                return
            
            rect_finder.x = x
            rect_finder.y = y
            rect_finder.height = height
            rect_finder.width = width
            rect_finder.min_height = int(height/1.5)
            rect_finder.max_height = int(height*1.5)
            rect_finder.min_width = int(width/1.5)
            rect_finder.max_width = int(width*1.5)
        else:
            self.__flag_capturing_sub_rect = True
            self.__flag_capturing_sub_rect_roi = False
    
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
        self._main_rect_finder.x = mouse_pos.x() - self.__moving_rect_mouse_offset_x
        self._main_rect_finder.y = mouse_pos.y() - self.__moving_rect_mouse_offset_y
        #self.update()
        
    def delete_rect(self):
        
        if len(self._sub_rects_finder) > 0:
            
            index = -1 #self.__index_deleted_rect_inside_roi
            if self._sub_rects_finder[index].x != 0 and self._sub_rects_finder[index].y != 0 \
                and self._sub_rects_finder[index].width != 0 and self._sub_rects_finder[index].height != 0:
                
                self._sub_rects_finder[index].deleted_x = self._sub_rects_finder[index].x
                self._sub_rects_finder[index].deleted_y = self._sub_rects_finder[index].y
                self._sub_rects_finder[index].deleted_width = self._sub_rects_finder[index].width
                self._sub_rects_finder[index].deleted_height = self._sub_rects_finder[index].height
                
                self._sub_rects_finder[index].x = 0
                self._sub_rects_finder[index].y = 0
                self._sub_rects_finder[index].width = 0
                self._sub_rects_finder[index].height = 0
                
                self.__flag_need_to_delete_roi = True
                self.__flag_need_to_restore_roi = False
                self.__flag_capturing_sub_rect_roi = False
                self.__flag_capturing_sub_rect = True
               
            else: #self.__flag_need_to_delete_roi:
                
                self.__deleted_rects.append(self._sub_rects_finder[-1])
                del self._sub_rects_finder[-1]
                self.__flag_need_to_delete_roi = False
                self.__flag_need_to_restore_roi = True
                self.__flag_capturing_sub_rect_roi = True
                self.__flag_capturing_sub_rect = False
            
        elif self._main_rect_finder is not None:
            self.__deleted_rects.append(self._main_rect_finder)
            self._main_rect_finder = None
            self.__flag_capturing_main_rect = True
            self.__flag_capturing_sub_rect_roi = False
        self.update()
        
    def restore_rect(self):
    
        if self._main_rect_finder is None:
            self._main_rect_finder = copy.deepcopy(self.__deleted_rects[-1])
            self.__flag_capturing_main_rect = False
            self.__flag_capturing_sub_rect_roi = True
            del self.__deleted_rects[-1]
            
        elif len(self.__deleted_rects) > 0 and self.__flag_need_to_restore_roi is True:
            self._sub_rects_finder.append(self.__deleted_rects[-1])
            del self.__deleted_rects[-1]
            self.__flag_need_to_restore_roi = False
            
            self.__flag_capturing_sub_rect_roi = False
            self.__flag_capturing_sub_rect = True
                
        elif self.__flag_need_to_restore_roi is False:
        
            index = -1
            
            if  self._sub_rects_finder[index].deleted_x is not None and \
                self._sub_rects_finder[index].deleted_y is not None and self._sub_rects_finder[index].deleted_height is not None \
                and self._sub_rects_finder[index].deleted_width is not None:
                
                self._sub_rects_finder[index].x = self._sub_rects_finder[index].deleted_x
                self._sub_rects_finder[index].y = self._sub_rects_finder[index].deleted_y
                self._sub_rects_finder[index].width = self._sub_rects_finder[index].deleted_width
                self._sub_rects_finder[index].height = self._sub_rects_finder[index].deleted_height
                
                self._sub_rects_finder[index].deleted_x = None
                self._sub_rects_finder[index].deleted_y = None
                self._sub_rects_finder[index].deleted_width = None
                self._sub_rects_finder[index].deleted_height = None
                
                self.__flag_capturing_sub_rect_roi = True
                self.__flag_capturing_sub_rect = False
                
            self.__flag_need_to_restore_roi = True

        """
        if len(self.__deleted_rects) == 0:
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
        file_code_string = file_code_string.replace(unicode(self.__old_code_v230, 'utf-8'), "")
        file_code_string = file_code_string.replace(unicode(self.__old_code_v250, 'utf-8'), "")
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
        #current_code_string = current_code_string.replace(os.linesep + os.linesep, os.linesep)
        
        """
        if not os.path.exists(filename) and self.action == "edit":
            self.action = "new"
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
            #print "replaced"
            file_code_string = file_code_string.replace(unicode(self.__old_code_v220, 'utf-8'), current_code_string)
            file_code_string = file_code_string.replace(unicode(self.__old_code_v230, 'utf-8'), current_code_string)
            file_code_string = file_code_string.replace(unicode(self.__old_code_v250, 'utf-8'), current_code_string)
            file_code_string = file_code_string.replace(unicode(self.__old_code, 'utf-8'), current_code_string)

        string = file_code_string
        string = string.encode('utf-8')

        file = codecs.open(filename, 'w', 'utf-8')
        file.write(unicode(string, 'utf-8'))
        file.close()    
        #print unicode(self.__old_code, 'utf-8'), current_code_string, file_code_string
    
    def get_old_code_v220(self):
        if self._main_rect_finder is None:
            return "".encode('utf-8')
        
        self.build_code_array_v220()
        return self.build_code_string()
        
    def get_old_code_v230(self):
        if self._main_rect_finder is None:
            return "".encode('utf-8')
        
        self.build_code_array_v230()
        return self.build_code_string()
    
    def get_old_code_v250(self):
        if self._main_rect_finder is None:
            return "".encode('utf-8')
        
        self.build_code_array_v250()
        return self.build_code_string()

    def get_old_code(self):
        if self._main_rect_finder is None:
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
       
        if self._main_rect_finder is None:
            return
            
        self._code_lines = []
        self._code_lines_for_object_finder = []
            
        name = self.object_name
        
        if name == "":
            name = time.strftime("rect_finder_%d_%m_%y_%H_%M_%S")
            self.object_name = name
            
        strcode = name + "_object = None" #RectFinder(\"" + name + "\")"
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
        
        self._code_lines.append("    global " + name + "_object")
        self._code_lines.append("    " + name + "_object = RectFinder(\"" + name + "\")")
        
        if self._main_rect_finder.use_min_max is False:                  
            height = str(self._main_rect_finder.height)
            width = str(self._main_rect_finder.width)
            width_tolerance = str(self._main_rect_finder.width_tolerance)
            height_tolerance = str(self._main_rect_finder.height_tolerance)
            strcode = "    " + name + "_object.set_main_component({\"height\": " + height + ", \"width\": " + width + ", \"height_tolerance\": " + height_tolerance + ", \"width_tolerance\": " + width_tolerance + "})"
            #self._code_lines.append("    rect_finder.set_main_rect({\"height\": " + height + ", \"width\": " + width + ", \"height_tolerance\": " + height_tolerance + ", \"width_tolerance\": " + width_tolerance + "})")
        else:
            min_width = str(self._main_rect_finder.min_width)
            max_width = str(self._main_rect_finder.max_width)
            min_height = str(self._main_rect_finder.min_height)
            max_height = str(self._main_rect_finder.max_height)
            strcode = "    " + name + "_object.set_main_component({\"min_width\": " + min_width + ", \"max_width\": " + max_width + ", \"min_height\": " + min_height + ", \"max_height\": " + max_height + "})"
            #self._code_lines.append("    rect_finder.set_main_rect({\"min_width\": " + min_width + ", \"max_width\": " + max_width + ", \"min_height\": " + min_height + ", \"max_height\": " + max_height + "})")
            
        self._code_lines.append(strcode)
        self._code_lines_for_object_finder.append(strcode)
            
        #self._code_lines.append("\n")
        
        for sub_rect in self._sub_rects_finder:
            if sub_rect.height != 0 and sub_rect.width !=0:
            
                #roi_x = str(sub_rect.roi_x - self._main_rect_finder.x)
                roi_x = str(sub_rect.roi_x)
                roi_y = str(sub_rect.roi_y)
                
                roi_width = str(sub_rect.roi_width)
                roi_height = str(sub_rect.roi_height)

                
                if sub_rect.use_min_max is False:  
                    
                    height = str(sub_rect.height)
                    width = str(sub_rect.width)
                    width_tolerance = str(sub_rect.width_tolerance)
                    height_tolerance = str(sub_rect.height_tolerance)
                
                    str1 = "    " + name + "_object.add_sub_component({\"height\": " + height + ", \"width\": " + width + ", \"height_tolerance\": " + height_tolerance + ", \"width_tolerance\": " + width_tolerance + "},"
                    str2 = "                             {\"roi_x\": " + roi_x + ", \"roi_y\": " + roi_y + ", \"roi_width\": " + roi_width + ", \"roi_height\": " + roi_height + "})"
                    #self._code_lines.append("    rect_finder.add_sub_rect({\"height\": " + height + ", \"width\": " + width + ", \"height_tolerance\": " + height_tolerance + ", \"width_tolerance\": " + width_tolerance + "},")
                    #self._code_lines.append("                             {\"roi_x\": " + roi_x + ", \"roi_y\": " + roi_y + ", \"roi_width\": " + roi_width + ", \"roi_height\": " + roi_height + "})")
                    
                else:
                    min_width = str(sub_rect.min_width)
                    max_width = str(sub_rect.max_width)
                    min_height = str(sub_rect.min_height)
                    max_height = str(sub_rect.max_height)
                    
                    str1 = "    " + name + "_object.add_sub_component({\"min_height\": " + min_height + ", \"max_height\": " + max_height + ", \"min_width\": " + min_width + ", \"max_width\": " + max_width + "},"
                    str2 = "                             {\"roi_x\": " + roi_x + ", \"roi_y\": " + roi_y + ", \"roi_width\": " + roi_width + ", \"roi_height\": " + roi_height + "})"
                    #self._code_lines.append("    rect_finder.add_sub_rect({\"min_height\": " + min_height + ", \"max_height\": " + max_height + ", \"min_width\": " + min_width + ", \"max_width\": " + max_width + "},")
                    #self._code_lines.append("                             {\"roi_x\": " + roi_x + ", \"roi_y\": " + roi_y + ", \"roi_width\": " + roi_width + ", \"roi_height\": " + roi_height + "})")
        
                #self._code_lines.append("\n")
                self._code_lines.append(str1)
                self._code_lines.append(str2)
                self._code_lines_for_object_finder.append(str1)
                self._code_lines_for_object_finder.append(str2)

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
        
        if self._main_rect_finder.click == True or self._main_rect_finder.doubleclick == True or self._main_rect_finder.rightclick == True or self._main_rect_finder.mousemove == True:
        
            self._code_lines.append("    main_rect_pos = " + name + "_object.get_result(0)")  
        
            if mmanager_declared is False:
                self._code_lines.append("    m = MouseManager()")
                mmanager_declared = True
                
            self._code_lines.append("    time.sleep(2)")
                                
            if self._main_rect_finder.click == True and self._main_rect_finder.number_of_clicks == 1:
                self._code_lines.append("    m.click(main_rect_pos.x + (main_rect_pos.width/2), main_rect_pos.y + (main_rect_pos.height/2), 1)")
            elif self._main_rect_finder.click == True and self._main_rect_finder.number_of_clicks == 2:
                self._code_lines.append("    m.click(main_rect_pos.x + (main_rect_pos.width/2), main_rect_pos.y + (main_rect_pos.height/2), 1, 2)")
            elif self._main_rect_finder.rightclick == True:
                self._code_lines.append("    m.click(main_rect_pos.x + (main_rect_pos.width/2), main_rect_pos.y + (main_rect_pos.height/2), 2)")
            elif self._main_rect_finder.mousemove == True:
                self._code_lines.append("    m.move(main_rect_pos.x + (main_rect_pos.width/2), main_rect_pos.y + (main_rect_pos.height/2))")
                
        if self._main_rect_finder.sendkeys != "":
            if kmanager_declared is False:
                self._code_lines.append("    k  = KeyboardManager()")
                kmanager_declared = True
            keys = unicode(self._main_rect_finder.sendkeys, 'utf-8')
            self._code_lines.append("    time.sleep(2)")
            
            if self._main_rect_finder.sendkeys_quotes is True:
                self._code_lines.append("    k.send(\"" + keys + "\", encrypted=" + str(self._main_rect_finder.text_encrypted) + ")")
            else:
                self._code_lines.append("    k.send(" + keys + ", encrypted=" + str(self._main_rect_finder.text_encrypted) + ")")
            
        cnt = 0
        for sub_rect in self._sub_rects_finder:
        
            if sub_rect.height != 0 and sub_rect.width !=0:
                if sub_rect.click == True or sub_rect.doubleclick == True or sub_rect.rightclick == True or sub_rect.mousemove == True:
            
                    self._code_lines.append("    sub_rect_" + str(cnt) + "_pos = " + name + "_object.get_result(0, " + str(cnt) + ")")  
                
                    if mmanager_declared is False:
                        self._code_lines.append("    m = MouseManager()")
                        mmanager_declared = True
                    self._code_lines.append("    time.sleep(2)")
                                        
                    if sub_rect.click == True and sub_rect.number_of_clicks == 1:
                        self._code_lines.append("    m.click(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2), sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2), 1)")
                    elif sub_rect.click == True and sub_rect.number_of_clicks == 2:
                        self._code_lines.append("    m.click(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2), sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2), 1, 2)")
                    elif sub_rect.rightclick == True:
                        self._code_lines.append("    m.click(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2), sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2), 2)")
                    elif sub_rect.mousemove == True:
                        self._code_lines.append("    m.move(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2), sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2))")
                    
                if sub_rect.sendkeys != "":
                    if kmanager_declared is False:
                        self._code_lines.append("    k  = KeyboardManager()")
                        kmanager_declared = True
                    keys = unicode(sub_rect.sendkeys, 'utf-8')
                    self._code_lines.append("    time.sleep(2)")
                    
                    if sub_rect.sendkeys_quotes is True:
                        self._code_lines.append("    k.send(\"" + keys + "\", encrypted=" + str(sub_rect.text_encrypted) + ")")
                    else:
                        self._code_lines.append("    k.send(" + keys + ", encrypted=" + str(sub_rect.text_encrypted) + ")")
                       
                    
                cnt = cnt + 1
        self._code_lines.append("")
        
        
        #self._code_lines.append("def " + name + "():")
        
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
            self._code_lines.append("    elif wait_time < " + repr(self._main_rect_finder.critical) + ":")
            self._code_lines.append("        print \"*WARN* step " + str(self.object_name) + " has exceeded the performance warning threshold:\", wait_time, \"sec.\"")
            self._code_lines.append("    else:")
            self._code_lines.append("        print \"*WARN* step " + str(self.object_name) + " has exceeded the performance critical threshold:\", wait_time, \"sec.\"")
            self._code_lines.append("    p = PerfManager()")
            self._code_lines.append("    p.add_perfdata(\"" + str(self.object_name) + "\", wait_time, " + repr(self.warning) + ", " + repr(self._main_rect_finder.critical) + ")")
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
           
    def build_code_array_v230(self):
    
        self.mouse_or_key_is_set = False
    
        kmanager_declared = False
        mmanager_declared = False
       
        if self._main_rect_finder is None:
            return
            
        self._code_lines = []
        self._code_lines_for_object_finder = []
            
        name = self.object_name
        
        if name == "":
            name = time.strftime("rect_finder_%d_%m_%y_%H_%M_%S")
            self.object_name = name
            
        strcode = name + "_object = None" #RectFinder(\"" + name + "\")"
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
        
        self._code_lines.append("    global " + name + "_object")
        self._code_lines.append("    " + name + "_object = RectFinder(\"" + name + "\")")
        
        if self._main_rect_finder.use_min_max is False:                  
            height = str(self._main_rect_finder.height)
            width = str(self._main_rect_finder.width)
            width_tolerance = str(self._main_rect_finder.width_tolerance)
            height_tolerance = str(self._main_rect_finder.height_tolerance)
            strcode = "    " + name + "_object.set_main_component({\"height\": " + height + ", \"width\": " + width + ", \"height_tolerance\": " + height_tolerance + ", \"width_tolerance\": " + width_tolerance + "})"
            #self._code_lines.append("    rect_finder.set_main_rect({\"height\": " + height + ", \"width\": " + width + ", \"height_tolerance\": " + height_tolerance + ", \"width_tolerance\": " + width_tolerance + "})")
        else:
            min_width = str(self._main_rect_finder.min_width)
            max_width = str(self._main_rect_finder.max_width)
            min_height = str(self._main_rect_finder.min_height)
            max_height = str(self._main_rect_finder.max_height)
            strcode = "    " + name + "_object.set_main_component({\"min_width\": " + min_width + ", \"max_width\": " + max_width + ", \"min_height\": " + min_height + ", \"max_height\": " + max_height + "})"
            #self._code_lines.append("    rect_finder.set_main_rect({\"min_width\": " + min_width + ", \"max_width\": " + max_width + ", \"min_height\": " + min_height + ", \"max_height\": " + max_height + "})")
            
        self._code_lines.append(strcode)
        self._code_lines_for_object_finder.append(strcode)
            
        #self._code_lines.append("\n")
        
        for sub_rect in self._sub_rects_finder:
            if sub_rect.height != 0 and sub_rect.width !=0:
            
                #roi_x = str(sub_rect.roi_x - self._main_rect_finder.x)
                roi_x = str(sub_rect.roi_x)
                roi_y = str(sub_rect.roi_y)
                
                roi_width = str(sub_rect.roi_width)
                roi_height = str(sub_rect.roi_height)

                
                if sub_rect.use_min_max is False:  
                    
                    height = str(sub_rect.height)
                    width = str(sub_rect.width)
                    width_tolerance = str(sub_rect.width_tolerance)
                    height_tolerance = str(sub_rect.height_tolerance)
                
                    str1 = "    " + name + "_object.add_sub_component({\"height\": " + height + ", \"width\": " + width + ", \"height_tolerance\": " + height_tolerance + ", \"width_tolerance\": " + width_tolerance + "},"
                    str2 = "                             {\"roi_x\": " + roi_x + ", \"roi_y\": " + roi_y + ", \"roi_width\": " + roi_width + ", \"roi_height\": " + roi_height + "})"
                    #self._code_lines.append("    rect_finder.add_sub_rect({\"height\": " + height + ", \"width\": " + width + ", \"height_tolerance\": " + height_tolerance + ", \"width_tolerance\": " + width_tolerance + "},")
                    #self._code_lines.append("                             {\"roi_x\": " + roi_x + ", \"roi_y\": " + roi_y + ", \"roi_width\": " + roi_width + ", \"roi_height\": " + roi_height + "})")
                    
                else:
                    min_width = str(sub_rect.min_width)
                    max_width = str(sub_rect.max_width)
                    min_height = str(sub_rect.min_height)
                    max_height = str(sub_rect.max_height)
                    
                    str1 = "    " + name + "_object.add_sub_component({\"min_height\": " + min_height + ", \"max_height\": " + max_height + ", \"min_width\": " + min_width + ", \"max_width\": " + max_width + "},"
                    str2 = "                             {\"roi_x\": " + roi_x + ", \"roi_y\": " + roi_y + ", \"roi_width\": " + roi_width + ", \"roi_height\": " + roi_height + "})"
                    #self._code_lines.append("    rect_finder.add_sub_rect({\"min_height\": " + min_height + ", \"max_height\": " + max_height + ", \"min_width\": " + min_width + ", \"max_width\": " + max_width + "},")
                    #self._code_lines.append("                             {\"roi_x\": " + roi_x + ", \"roi_y\": " + roi_y + ", \"roi_width\": " + roi_width + ", \"roi_height\": " + roi_height + "})")
        
                #self._code_lines.append("\n")
                self._code_lines.append(str1)
                self._code_lines.append(str2)
                self._code_lines_for_object_finder.append(str1)
                self._code_lines_for_object_finder.append(str2)

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
        
        if self._main_rect_finder.click == True or self._main_rect_finder.doubleclick == True or self._main_rect_finder.rightclick == True or self._main_rect_finder.mousemove == True:
        
            self.mouse_or_key_is_set = True
        
            self._code_lines.append("    main_rect_pos = " + name + "_object.get_result(0)")  
        
            if mmanager_declared is False:
                self._code_lines.append("    m = MouseManager()")
                mmanager_declared = True
                
            self._code_lines.append("    time.sleep(sleep_factor)")
                                
            if self._main_rect_finder.click == True and self._main_rect_finder.number_of_clicks == 1:
                self._code_lines.append("    m.click(main_rect_pos.x + (main_rect_pos.width/2), main_rect_pos.y + (main_rect_pos.height/2), 1)")
            elif self._main_rect_finder.click == True and self._main_rect_finder.number_of_clicks == 2:
                self._code_lines.append("    m.click(main_rect_pos.x + (main_rect_pos.width/2), main_rect_pos.y + (main_rect_pos.height/2), 1, 2)")
            elif self._main_rect_finder.rightclick == True:
                self._code_lines.append("    m.click(main_rect_pos.x + (main_rect_pos.width/2), main_rect_pos.y + (main_rect_pos.height/2), 2)")
            elif self._main_rect_finder.mousemove == True:
                self._code_lines.append("    m.move(main_rect_pos.x + (main_rect_pos.width/2), main_rect_pos.y + (main_rect_pos.height/2))")
                
        if self._main_rect_finder.sendkeys != "":
            self.mouse_or_key_is_set = True
        
            if kmanager_declared is False:
                self._code_lines.append("    k  = KeyboardManager()")
                kmanager_declared = True
            keys = unicode(self._main_rect_finder.sendkeys, 'utf-8')
            self._code_lines.append("    time.sleep(sleep_factor)")
            
            if self._main_rect_finder.sendkeys_quotes is True:
                self._code_lines.append("    k.send(\"" + keys + "\", encrypted=" + str(self._main_rect_finder.text_encrypted) + ")")
            else:
                self._code_lines.append("    k.send(" + keys + ", encrypted=" + str(self._main_rect_finder.text_encrypted) + ")")
            
        cnt = 0
        for sub_rect in self._sub_rects_finder:
        
            if sub_rect.height != 0 and sub_rect.width !=0:
                if sub_rect.click == True or sub_rect.doubleclick == True or sub_rect.rightclick == True or sub_rect.mousemove == True:
                
                    self.mouse_or_key_is_set = True
            
                    self._code_lines.append("    sub_rect_" + str(cnt) + "_pos = " + name + "_object.get_result(0, " + str(cnt) + ")")  
                
                    if mmanager_declared is False:
                        self._code_lines.append("    m = MouseManager()")
                        mmanager_declared = True
                    self._code_lines.append("    time.sleep(sleep_factor)")
                                        
                    if sub_rect.click == True and sub_rect.number_of_clicks == 1:
                        self._code_lines.append("    m.click(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2), sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2), 1)")
                    elif sub_rect.click == True and sub_rect.number_of_clicks == 2:
                        self._code_lines.append("    m.click(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2), sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2), 1, 2)")
                    elif sub_rect.rightclick == True:
                        self._code_lines.append("    m.click(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2), sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2), 2)")
                    elif sub_rect.mousemove == True:
                        self._code_lines.append("    m.move(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2), sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2))")
                    
                if sub_rect.sendkeys != "":
                
                    self.mouse_or_key_is_set = True
                
                    if kmanager_declared is False:
                        self._code_lines.append("    k  = KeyboardManager()")
                        kmanager_declared = True
                    keys = unicode(sub_rect.sendkeys, 'utf-8')
                    self._code_lines.append("    time.sleep(sleep_factor)")
                    
                    if sub_rect.sendkeys_quotes is True:
                        self._code_lines.append("    k.send(\"" + keys + "\", encrypted=" + str(sub_rect.text_encrypted) + ")")
                    else:
                        self._code_lines.append("    k.send(" + keys + ", encrypted=" + str(sub_rect.text_encrypted) + ")")
                       
                    
                cnt = cnt + 1
        self._code_lines.append("")
        
        
        #self._code_lines.append("def " + name + "():")
        
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
                self._code_lines.append("    elif wait_time + wait_time_disappear < " + repr(self.critical) + ":")
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

    def build_code_array_v250(self):
    
        self.mouse_or_key_is_set = False
    
        kmanager_declared = False
        mmanager_declared = False
       
        if self._main_rect_finder is None:
            return
            
        self._code_lines = []
        self._code_lines_for_object_finder = []
            
        name = self.object_name
        
        if name == "" and self.ok_pressed is True:
            name = time.strftime("rect_finder_%d_%m_%y_%H_%M_%S")
            self.object_name = name
            
        strcode = name + "_object = None" #RectFinder(\"" + name + "\")"
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
        
        self._code_lines.append("    global " + name + "_object")
        self._code_lines.append("    " + name + "_object = RectFinder(\"" + name + "\")")
        
        if self._main_rect_finder.use_min_max is False:                  
            height = str(self._main_rect_finder.height)
            width = str(self._main_rect_finder.width)
            width_tolerance = str(self._main_rect_finder.width_tolerance)
            height_tolerance = str(self._main_rect_finder.height_tolerance)
            strcode = "    " + name + "_object.set_main_component({\"height\": " + height + ", \"width\": " + width + ", \"height_tolerance\": " + height_tolerance + ", \"width_tolerance\": " + width_tolerance + "})"
            #self._code_lines.append("    rect_finder.set_main_rect({\"height\": " + height + ", \"width\": " + width + ", \"height_tolerance\": " + height_tolerance + ", \"width_tolerance\": " + width_tolerance + "})")
        else:
            min_width = str(self._main_rect_finder.min_width)
            max_width = str(self._main_rect_finder.max_width)
            min_height = str(self._main_rect_finder.min_height)
            max_height = str(self._main_rect_finder.max_height)
            strcode = "    " + name + "_object.set_main_component({\"min_width\": " + min_width + ", \"max_width\": " + max_width + ", \"min_height\": " + min_height + ", \"max_height\": " + max_height + "})"
            #self._code_lines.append("    rect_finder.set_main_rect({\"min_width\": " + min_width + ", \"max_width\": " + max_width + ", \"min_height\": " + min_height + ", \"max_height\": " + max_height + "})")
            
        self._code_lines.append(strcode)
        self._code_lines_for_object_finder.append(strcode)
        
                
        if self._main_rect_finder.click == True or self._main_rect_finder.rightclick == True or self._main_rect_finder.mousemove == True or self._main_rect_finder.hold_and_release is not None:
            if self._main_rect_finder.x_offset is None and self._main_rect_finder.y_offset is None: 
                if self._main_rect_finder.hold_and_release is not None:
                    if self._main_rect_finder.hold_and_release == 0:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
                    elif self._main_rect_finder.hold_and_release == 1:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
                    elif self._main_rect_finder.hold_and_release == 2:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0, 0 - " + str(self._main_rect_finder.release_pixel) + ", False)")
                    elif self._main_rect_finder.hold_and_release == 3:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0, 0 + " + str(self._main_rect_finder.release_pixel) + ", False)")
                    elif self._main_rect_finder.hold_and_release == 4:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0 - " + str(self._main_rect_finder.release_pixel) + ", 0, False)")
                    elif self._main_rect_finder.hold_and_release == 5:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0 + " + str(self._main_rect_finder.release_pixel) + ", 0, False)")
                else:
                    self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                    self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
            else:
                if self._main_rect_finder.hold_and_release is not None:
                    if self._main_rect_finder.hold_and_release == 0:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_rect_finder.x_offset) + "), 0 + (" + str(self._main_rect_finder.y_offset) + "), True)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
                    elif self._main_rect_finder.hold_and_release == 1:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_rect_finder.x_offset) + "), 0 + (" + str(self._main_rect_finder.y_offset) + "), True)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
                    elif self._main_rect_finder.hold_and_release == 2:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_rect_finder.x_offset) + "), 0 + (" + str(self._main_rect_finder.y_offset) + "), True)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0 + (" + str(self._main_rect_finder.x_offset) + "), 0 + (" + str(self._main_rect_finder.y_offset) + ") - " + str(self._main_rect_finder.release_pixel) + ", True)")
                    elif self._main_rect_finder.hold_and_release == 3:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_rect_finder.x_offset) + "), 0 + (" + str(self._main_rect_finder.y_offset) + "), True)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0 + (" + str(self._main_rect_finder.x_offset) + "), 0 + (" + str(self._main_rect_finder.y_offset) + ") + " + str(self._main_rect_finder.release_pixel) + ", True)")
                    elif self._main_rect_finder.hold_and_release == 4:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_rect_finder.x_offset) + "), 0 + (" + str(self._main_rect_finder.y_offset) + "), True)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0 + (" + str(self._main_rect_finder.x_offset) + ") - " + str(self._main_rect_finder.release_pixel) + ",  0 + (" + str(self._main_rect_finder.y_offset) + "), True)")
                    elif self._main_rect_finder.hold_and_release == 5:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_rect_finder.x_offset) + "), 0 + (" + str(self._main_rect_finder.y_offset) + "), True)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0 + (" + str(self._main_rect_finder.x_offset) + ") + " + str(self._main_rect_finder.release_pixel) + ",  0 + (" + str(self._main_rect_finder.y_offset) + "), True)")
                else:
                    self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_rect_finder.x_offset) + "), 0 + (" + str(self._main_rect_finder.y_offset) + "), True)")
                    self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
        else:
            self._code_lines.append("    "  + name + "_object.main_xy_coordinates = None")
            self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
            
        #self._code_lines.append("\n")
        
        for sub_rect in self._sub_rects_finder:
            if sub_rect.height != 0 and sub_rect.width !=0:
            
                #roi_x = str(sub_rect.roi_x - self._main_rect_finder.x)
                roi_x = str(sub_rect.roi_x)
                roi_y = str(sub_rect.roi_y)
                
                roi_width = str(sub_rect.roi_width)
                roi_height = str(sub_rect.roi_height)

                
                if sub_rect.use_min_max is False:  
                    
                    height = str(sub_rect.height)
                    width = str(sub_rect.width)
                    width_tolerance = str(sub_rect.width_tolerance)
                    height_tolerance = str(sub_rect.height_tolerance)
                
                    str1 = "    " + name + "_object.add_sub_component({\"height\": " + height + ", \"width\": " + width + ", \"height_tolerance\": " + height_tolerance + ", \"width_tolerance\": " + width_tolerance + "},"
                    str2 = "                             {\"roi_x\": " + roi_x + ", \"roi_y\": " + roi_y + ", \"roi_width\": " + roi_width + ", \"roi_height\": " + roi_height + "})"
                    #self._code_lines.append("    rect_finder.add_sub_rect({\"height\": " + height + ", \"width\": " + width + ", \"height_tolerance\": " + height_tolerance + ", \"width_tolerance\": " + width_tolerance + "},")
                    #self._code_lines.append("                             {\"roi_x\": " + roi_x + ", \"roi_y\": " + roi_y + ", \"roi_width\": " + roi_width + ", \"roi_height\": " + roi_height + "})")
                    
                else:
                    min_width = str(sub_rect.min_width)
                    max_width = str(sub_rect.max_width)
                    min_height = str(sub_rect.min_height)
                    max_height = str(sub_rect.max_height)
                    
                    str1 = "    " + name + "_object.add_sub_component({\"min_height\": " + min_height + ", \"max_height\": " + max_height + ", \"min_width\": " + min_width + ", \"max_width\": " + max_width + "},"
                    str2 = "                             {\"roi_x\": " + roi_x + ", \"roi_y\": " + roi_y + ", \"roi_width\": " + roi_width + ", \"roi_height\": " + roi_height + "})"
                    #self._code_lines.append("    rect_finder.add_sub_rect({\"min_height\": " + min_height + ", \"max_height\": " + max_height + ", \"min_width\": " + min_width + ", \"max_width\": " + max_width + "},")
                    #self._code_lines.append("                             {\"roi_x\": " + roi_x + ", \"roi_y\": " + roi_y + ", \"roi_width\": " + roi_width + ", \"roi_height\": " + roi_height + "})")
        
                #self._code_lines.append("\n")
                self._code_lines.append(str1)
                self._code_lines.append(str2)
                self._code_lines_for_object_finder.append(str1)
                self._code_lines_for_object_finder.append(str2)
                
                if sub_rect.click == True or sub_rect.rightclick == True or sub_rect.mousemove == True or sub_rect.hold_and_release is not None:
                    if sub_rect.x_offset is None and sub_rect.y_offset is None: 
                        if sub_rect.hold_and_release is not None:
                            if sub_rect.hold_and_release == 0:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0, False))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")
                            elif sub_rect.hold_and_release == 1:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0, False))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")
                            elif sub_rect.hold_and_release == 2:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0, False))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0, 0 - " + str(sub_rect.release_pixel) + ", False))")
                            elif sub_rect.hold_and_release == 3:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0, 0 + " + str(sub_rect.release_pixel) + ", False))")
                            elif sub_rect.hold_and_release == 4:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0 - " + str(sub_rect.release_pixel) + ", 0, False))")
                            elif sub_rect.hold_and_release == 5:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0 + " + str(sub_rect.release_pixel) + ", 0, False))")
                        else:
                            self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0, False))")
                            self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")
                    else:
                        if sub_rect.hold_and_release is not None:
                            if sub_rect.hold_and_release == 0:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_rect.x_offset) + "), 0 + (" + str(sub_rect.y_offset) + "), True))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")
                            elif sub_rect.hold_and_release == 1:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_rect.x_offset) + "), 0 + (" + str(sub_rect.y_offset) + "), True))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")
                            elif sub_rect.hold_and_release == 2:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_rect.x_offset) + "), 0 + (" + str(sub_rect.y_offset) + "), True))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0 + (" + str(sub_rect.x_offset) + "), 0 + (" + str(sub_rect.y_offset) + ") - " + str(sub_rect.release_pixel) + ", True))")
                            elif sub_rect.hold_and_release == 3:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_rect.x_offset) + "), 0 + (" + str(sub_rect.y_offset) + ")))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0 + (" + str(sub_rect.x_offset) + "), 0 + (" + str(sub_rect.y_offset) + ") + " + str(sub_rect.release_pixel) + ", True))")
                            elif sub_rect.hold_and_release == 4:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_rect.x_offset) + "), 0 + (" + str(sub_rect.y_offset) + ")))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0 + (" + str(sub_rect.x_offset) + ") - " + str(sub_rect.release_pixel) + ",  0 + (" + str(sub_rect.y_offset) + "), True))")
                            elif sub_rect.hold_and_release == 5:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_rect.x_offset) + "), 0 + (" + str(sub_rect.y_offset) + ")))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0 + (" + str(sub_rect.x_offset) + ") + " + str(sub_rect.release_pixel) + ",  0 + (" + str(sub_rect.y_offset) + "), True))")
                        else:
                            self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_rect.x_offset) + "), 0 + (" + str(sub_rect.y_offset) + "), True))")
                            self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")
                else:
                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append(None)")
                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")

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
        
        if self._main_rect_finder.click == True or self._main_rect_finder.rightclick == True or self._main_rect_finder.mousemove == True or self._main_rect_finder.hold_and_release is not None:
        
            self.mouse_or_key_is_set = True
        
            self._code_lines.append("    main_rect_pos = " + name + "_object.get_result(0)")  
        
            if mmanager_declared is False:
                self._code_lines.append("    m = MouseManager()")
                mmanager_declared = True
                
            self._code_lines.append("    time.sleep(sleep_factor)")
            
            if self._main_rect_finder.x_offset is None and self._main_rect_finder.y_offset is None: 
                if self._main_rect_finder.click == True:
                    self._code_lines.append("    m.click_2(main_rect_pos.x + (main_rect_pos.width/2), main_rect_pos.y + (main_rect_pos.height/2), 1, " + str(self._main_rect_finder.number_of_clicks) + ", " + str(self._main_rect_finder.click_delay) + ")")
                elif self._main_rect_finder.rightclick == True:
                    self._code_lines.append("    m.click(main_rect_pos.x + (main_rect_pos.width/2), main_rect_pos.y + (main_rect_pos.height/2), 2)")
                elif self._main_rect_finder.mousemove == True:
                    self._code_lines.append("    m.move(main_rect_pos.x + (main_rect_pos.width/2), main_rect_pos.y + (main_rect_pos.height/2))")
                elif self._main_rect_finder.hold_and_release is not None:
                    if self._main_rect_finder.hold_and_release == 0:
                        self._code_lines.append("    m.hold(main_rect_pos.x + (main_rect_pos.width/2), main_rect_pos.y + (main_rect_pos.height/2))")
                    elif self._main_rect_finder.hold_and_release == 1:
                        self._code_lines.append("    m.release(main_rect_pos.x + (main_rect_pos.width/2), main_rect_pos.y + (main_rect_pos.height/2))")
                    elif self._main_rect_finder.hold_and_release == 2:
                        self._code_lines.append("    m.hold(main_rect_pos.x + (main_rect_pos.width/2), main_rect_pos.y + (main_rect_pos.height/2))")
                        self._code_lines.append("    time.sleep(sleep_factor)")
                        self._code_lines.append("    m.release(main_rect_pos.x + (main_rect_pos.width/2), main_rect_pos.y + (main_rect_pos.height/2) - " + str(self._main_rect_finder.release_pixel) + ")")
                    elif self._main_rect_finder.hold_and_release == 3:
                        self._code_lines.append("    m.hold(main_rect_pos.x + (main_rect_pos.width/2), main_rect_pos.y + (main_rect_pos.height/2))")
                        self._code_lines.append("    time.sleep(sleep_factor)")
                        self._code_lines.append("    m.release(main_rect_pos.x + (main_rect_pos.width/2), main_rect_pos.y + (main_rect_pos.height/2) + " + str(self._main_rect_finder.release_pixel) + ")")
                    elif self._main_rect_finder.hold_and_release == 4:
                        self._code_lines.append("    m.hold(main_rect_pos.x + (main_rect_pos.width/2), main_rect_pos.y + (main_rect_pos.height/2))")
                        self._code_lines.append("    time.sleep(sleep_factor)")
                        self._code_lines.append("    m.release(main_rect_pos.x + (main_rect_pos.width/2) - " + str(self._main_rect_finder.release_pixel) + ", main_rect_pos.y + (main_rect_pos.height/2))")
                    elif self._main_rect_finder.hold_and_release == 5:
                        self._code_lines.append("    m.hold(main_rect_pos.x + (main_rect_pos.width/2), main_rect_pos.y + (main_rect_pos.height/2))")
                        self._code_lines.append("    time.sleep(sleep_factor)")
                        self._code_lines.append("    m.release(main_rect_pos.x + (main_rect_pos.width/2) + " + str(self._main_rect_finder.release_pixel) + ", main_rect_pos.y + (main_rect_pos.height/2))")
            else:
                if self._main_rect_finder.click == True:
                    self._code_lines.append("    m.click_2(main_rect_pos.x + (" + str(self._main_rect_finder.x_offset) + "), main_rect_pos.y + (" + str(self._main_rect_finder.y_offset) + "), 1, " + str(self._main_rect_finder.number_of_clicks) + ", " + str(self._main_rect_finder.click_delay) + ")")
                elif self._main_rect_finder.rightclick == True:
                    self._code_lines.append("    m.click(main_rect_pos.x + (" + str(self._main_rect_finder.x_offset) + "), main_rect_pos.y + (" + str(self._main_rect_finder.y_offset) + "), 2)")
                elif self._main_rect_finder.mousemove == True:
                    self._code_lines.append("    m.move(main_rect_pos.x + (" + str(self._main_rect_finder.x_offset) + "), main_rect_pos.y + (" + str(self._main_rect_finder.y_offset) + "))")
                elif self._main_rect_finder.hold_and_release is not None:
                    if self._main_rect_finder.hold_and_release == 0:
                        self._code_lines.append("    m.hold(main_rect_pos.x + (" + str(self._main_rect_finder.x_offset) + "), main_rect_pos.y + (" + str(self._main_rect_finder.y_offset) + "))")
                    elif self._main_rect_finder.hold_and_release == 1:
                        self._code_lines.append("    m.release(main_rect_pos.x + (" + str(self._main_rect_finder.x_offset) + "), main_rect_pos.y + (" + str(self._main_rect_finder.y_offset) + "))")
                    elif self._main_rect_finder.hold_and_release == 2:
                        self._code_lines.append("    m.hold(main_rect_pos.x + (" + str(self._main_rect_finder.x_offset) + "), main_rect_pos.y + (" + str(self._main_rect_finder.y_offset) + "))")
                        self._code_lines.append("    time.sleep(sleep_factor)")
                        self._code_lines.append("    m.release(main_rect_pos.x + (" + str(self._main_rect_finder.x_offset) + "), main_rect_pos.y + (" + str(self._main_rect_finder.y_offset) + ") - " + str(self._main_rect_finder.release_pixel) + ")")
                    elif self._main_rect_finder.hold_and_release == 3:
                        self._code_lines.append("    m.hold(main_rect_pos.x + (" + str(self._main_rect_finder.x_offset) + "), main_rect_pos.y + (" + str(self._main_rect_finder.y_offset) + "))")
                        self._code_lines.append("    time.sleep(sleep_factor)")
                        self._code_lines.append("    m.release(main_rect_pos.x + (" + str(self._main_rect_finder.x_offset) + "), main_rect_pos.y + (" + str(self._main_rect_finder.y_offset) + ") + " + str(self._main_rect_finder.release_pixel) + ")")
                    elif self._main_rect_finder.hold_and_release == 4:
                        self._code_lines.append("    m.hold(main_rect_pos.x + (" + str(self._main_rect_finder.x_offset) + "), main_rect_pos.y + (" + str(self._main_rect_finder.y_offset) + "))")
                        self._code_lines.append("    time.sleep(sleep_factor)")
                        self._code_lines.append("    m.release(main_rect_pos.x + (" + str(self._main_rect_finder.x_offset) + ") - " + str(self._main_rect_finder.release_pixel) + ",  main_rect_pos.y + (" + str(self._main_rect_finder.y_offset) + "))")
                    elif self._main_rect_finder.hold_and_release == 5:
                        self._code_lines.append("    m.hold(main_rect_pos.x + (" + str(self._main_rect_finder.x_offset) + "), main_rect_pos.y + (" + str(self._main_rect_finder.y_offset) + "))")
                        self._code_lines.append("    time.sleep(sleep_factor)")
                        self._code_lines.append("    m.release(main_rect_pos.x + (" + str(self._main_rect_finder.x_offset) + ") + " + str(self._main_rect_finder.release_pixel) + ",  main_rect_pos.y + (" + str(self._main_rect_finder.y_offset) + "))")
        if self._main_rect_finder.sendkeys != "":
            self.mouse_or_key_is_set = True
        
            if kmanager_declared is False:
                self._code_lines.append("    k  = KeyboardManager()")
                kmanager_declared = True
            keys = unicode(self._main_rect_finder.sendkeys, 'utf-8')
            self._code_lines.append("    time.sleep(sleep_factor)")
            
            if self._main_rect_finder.sendkeys_quotes is True:
                self._code_lines.append("    k.send(\"" + keys + "\", encrypted=" + str(self._main_rect_finder.text_encrypted) + ")")
            else:
                self._code_lines.append("    k.send(" + keys + ", encrypted=" + str(self._main_rect_finder.text_encrypted) + ")")
            
        cnt = 0
        for sub_rect in self._sub_rects_finder:
        
            if sub_rect.height != 0 and sub_rect.width !=0:
                if sub_rect.click == True or sub_rect.rightclick == True or sub_rect.mousemove == True or sub_rect.hold_and_release is not None:
                
                    self.mouse_or_key_is_set = True
            
                    self._code_lines.append("    sub_rect_" + str(cnt) + "_pos = " + name + "_object.get_result(0, " + str(cnt) + ")")  
                
                    if mmanager_declared is False:
                        self._code_lines.append("    m = MouseManager()")
                        mmanager_declared = True
                    self._code_lines.append("    time.sleep(sleep_factor)")
                    

                    if sub_rect.x_offset is None and sub_rect.y_offset is None:    
                        if sub_rect.click == True:
                            self._code_lines.append("    m.click_2(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2), sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2), 1, " + str(sub_rect.number_of_clicks) + ", " + str(sub_rect.click_delay) + ")")
                        elif sub_rect.rightclick == True:
                            self._code_lines.append("    m.click(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2), sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2), 2)")
                        elif sub_rect.mousemove == True:
                            self._code_lines.append("    m.move(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2), sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2))")
                        elif sub_rect.hold_and_release is not None:
                            if sub_rect.hold_and_release == 0:
                                self._code_lines.append("    m.hold(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2), sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2))")
                            elif sub_rect.hold_and_release == 1:
                                self._code_lines.append("    m.release(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2), sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2))")
                            elif sub_rect.hold_and_release == 2:
                                self._code_lines.append("    m.hold(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2), sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2))")
                                self._code_lines.append("    time.sleep(sleep_factor)")
                                self._code_lines.append("    m.release(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2), sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2) - " + str(sub_rect.release_pixel) + ")")
                            elif sub_rect.hold_and_release == 3:
                                self._code_lines.append("    m.hold(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2), sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2))")
                                self._code_lines.append("    time.sleep(sleep_factor)")
                                self._code_lines.append("    m.release(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2), sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2) + " + str(sub_rect.release_pixel) + ")")
                            elif sub_rect.hold_and_release == 4:
                                self._code_lines.append("    m.hold(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2), sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2))")
                                self._code_lines.append("    time.sleep(sleep_factor)")
                                self._code_lines.append("    m.release(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2) - " + str(sub_rect.release_pixel) + ", sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2))")
                            elif sub_rect.hold_and_release == 5:
                                self._code_lines.append("    m.hold(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2), sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2))")
                                self._code_lines.append("    time.sleep(sleep_factor)")
                                self._code_lines.append("    m.release(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2) + " + str(sub_rect.release_pixel) + ", sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2))")
                    else:
                        if sub_rect.click == True:
                            self._code_lines.append("    m.click_2(sub_rect_" + str(cnt) + "_pos.x + (" + str(sub_rect.x_offset) + "), sub_rect_" + str(cnt) + "_pos.y + (" + str(sub_rect.y_offset) + "), 1, " + str(sub_rect.number_of_clicks) + ", " + str(sub_rect.click_delay) + ")")
                        elif sub_rect.rightclick == True:
                            self._code_lines.append("    m.click(sub_rect_" + str(cnt) + "_pos.x + (" + str(sub_rect.x_offset) + "), sub_rect_" + str(cnt) + "_pos.y + (" + str(sub_rect.y_offset) + "), 2)")
                        elif sub_rect.mousemove == True:
                            self._code_lines.append("    m.move(sub_rect_" + str(cnt) + "_pos.x + (" + str(sub_rect.x_offset) + "), sub_rect_" + str(cnt) + "_pos.y + (" + str(sub_rect.y_offset) + "))")
                        elif sub_rect.hold_and_release is not None:
                            if sub_rect.hold_and_release == 0:
                                self._code_lines.append("    m.hold(sub_rect_" + str(cnt) + "_pos.x + (" + str(sub_rect.x_offset) + "), sub_rect_" + str(cnt) + "_pos.y + (" + str(sub_rect.y_offset) + "))")
                            elif sub_rect.hold_and_release == 1:
                                self._code_lines.append("    m.release(sub_rect_" + str(cnt) + "_pos.x + (" + str(sub_rect.x_offset) + "), sub_rect_" + str(cnt) + "_pos.y + (" + str(sub_rect.y_offset) + "))")
                            elif sub_rect.hold_and_release == 2:
                                self._code_lines.append("    m.hold(sub_rect_" + str(cnt) + "_pos.x + (" + str(sub_rect.x_offset) + "), sub_rect_" + str(cnt) + "_pos.y + (" + str(sub_rect.y_offset) + "))")
                                self._code_lines.append("    time.sleep(sleep_factor)")
                                self._code_lines.append("    m.release(sub_rect_" + str(cnt) + "_pos.x + (" + str(sub_rect.x_offset) + "), sub_rect_" + str(cnt) + "_pos.y + (" + str(sub_rect.y_offset) + ") - " + str(sub_rect.release_pixel) + ")")
                            elif sub_rect.hold_and_release == 3:
                                self._code_lines.append("    m.hold(sub_rect_" + str(cnt) + "_pos.x + (" + str(sub_rect.x_offset) + "), sub_rect_" + str(cnt) + "_pos.y + (" + str(sub_rect.y_offset) + "))")
                                self._code_lines.append("    time.sleep(sleep_factor)")
                                self._code_lines.append("    m.release(sub_rect_" + str(cnt) + "_pos.x + (" + str(sub_rect.x_offset) + "), sub_rect_" + str(cnt) + "_pos.y + (" + str(sub_rect.y_offset) + ") + " + str(sub_rect.release_pixel) + ")")
                            elif sub_rect.hold_and_release == 4:
                                self._code_lines.append("    m.hold(sub_rect_" + str(cnt) + "_pos.x + (" + str(sub_rect.x_offset) + "), sub_rect_" + str(cnt) + "_pos.y + (" + str(sub_rect.y_offset) + "))")
                                self._code_lines.append("    time.sleep(sleep_factor)")
                                self._code_lines.append("    m.release(sub_rect_" + str(cnt) + "_pos.x + (" + str(sub_rect.x_offset) + ") - " + str(sub_rect.release_pixel) + ",  sub_rect_" + str(cnt) + "_pos.y + (" + str(sub_rect.y_offset) + "))")
                            elif sub_rect.hold_and_release == 5:
                                self._code_lines.append("    m.hold(sub_rect_" + str(cnt) + "_pos.x + (" + str(sub_rect.x_offset) + "), sub_rect_" + str(cnt) + "_pos.y + (" + str(sub_rect.y_offset) + "))")
                                self._code_lines.append("    time.sleep(sleep_factor)")
                                self._code_lines.append("    m.release(sub_rect_" + str(cnt) + "_pos.x + (" + str(sub_rect.x_offset) + ") + " + str(sub_rect.release_pixel) + ",  sub_rect_" + str(cnt) + "_pos.y + (" + str(sub_rect.y_offset) + "))")
                        
                if sub_rect.sendkeys != "":
                
                    self.mouse_or_key_is_set = True
                
                    if kmanager_declared is False:
                        self._code_lines.append("    k  = KeyboardManager()")
                        kmanager_declared = True
                    keys = unicode(sub_rect.sendkeys, 'utf-8')
                    self._code_lines.append("    time.sleep(sleep_factor)")
                    
                    if sub_rect.sendkeys_quotes is True:
                        self._code_lines.append("    k.send(\"" + keys + "\", encrypted=" + str(sub_rect.text_encrypted) + ")")
                    else:
                        self._code_lines.append("    k.send(" + keys + ", encrypted=" + str(sub_rect.text_encrypted) + ")")
                       
                    
                cnt = cnt + 1
        self._code_lines.append("")
        
        
        #self._code_lines.append("def " + name + "():")
        
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
                self._code_lines.append("    elif wait_time + wait_time_disappear < " + repr(self.critical) + ":")
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
        
    def build_code_array(self):
    
        self.mouse_or_key_is_set = False
    
        kmanager_declared = False
        mmanager_declared = False
       
        if self._main_rect_finder is None:
            return
            
        self._code_lines = []
        self._code_lines_for_object_finder = []
            
        name = self.object_name
        
        if name == "" and self.ok_pressed is True:
            name = time.strftime("rect_finder_%d_%m_%y_%H_%M_%S")
            self.object_name = name
            
        strcode = name + "_object = None" #RectFinder(\"" + name + "\")"
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
        
        self._code_lines.append("    global " + name + "_object")
        self._code_lines.append("    " + name + "_object = RectFinder(\"" + name + "\")")
        
        if self._main_rect_finder.use_min_max is False:                  
            height = str(self._main_rect_finder.height)
            width = str(self._main_rect_finder.width)
            width_tolerance = str(self._main_rect_finder.width_tolerance)
            height_tolerance = str(self._main_rect_finder.height_tolerance)
            strcode = "    " + name + "_object.set_main_component({\"height\": " + height + ", \"width\": " + width + ", \"height_tolerance\": " + height_tolerance + ", \"width_tolerance\": " + width_tolerance + "})"
            #self._code_lines.append("    rect_finder.set_main_rect({\"height\": " + height + ", \"width\": " + width + ", \"height_tolerance\": " + height_tolerance + ", \"width_tolerance\": " + width_tolerance + "})")
        else:
            min_width = str(self._main_rect_finder.min_width)
            max_width = str(self._main_rect_finder.max_width)
            min_height = str(self._main_rect_finder.min_height)
            max_height = str(self._main_rect_finder.max_height)
            strcode = "    " + name + "_object.set_main_component({\"min_width\": " + min_width + ", \"max_width\": " + max_width + ", \"min_height\": " + min_height + ", \"max_height\": " + max_height + "})"
            #self._code_lines.append("    rect_finder.set_main_rect({\"min_width\": " + min_width + ", \"max_width\": " + max_width + ", \"min_height\": " + min_height + ", \"max_height\": " + max_height + "})")
            
        self._code_lines.append(strcode)
        self._code_lines_for_object_finder.append(strcode)
        
                
        if self._main_rect_finder.click == True or self._main_rect_finder.rightclick == True or self._main_rect_finder.mousemove == True or self._main_rect_finder.hold_and_release is not None:
            if self._main_rect_finder.x_offset is None and self._main_rect_finder.y_offset is None: 
                if self._main_rect_finder.hold_and_release is not None:
                    if self._main_rect_finder.hold_and_release == 0:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
                    elif self._main_rect_finder.hold_and_release == 1:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
                    elif self._main_rect_finder.hold_and_release == 2:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0, 0 - " + str(self._main_rect_finder.release_pixel) + ", False)")
                    elif self._main_rect_finder.hold_and_release == 3:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0, 0 + " + str(self._main_rect_finder.release_pixel) + ", False)")
                    elif self._main_rect_finder.hold_and_release == 4:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0 - " + str(self._main_rect_finder.release_pixel) + ", 0, False)")
                    elif self._main_rect_finder.hold_and_release == 5:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0 + " + str(self._main_rect_finder.release_pixel) + ", 0, False)")
                else:
                    self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                    self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
            else:
                if self._main_rect_finder.hold_and_release is not None:
                    if self._main_rect_finder.hold_and_release == 0:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_rect_finder.x_offset) + "), 0 + (" + str(self._main_rect_finder.y_offset) + "), True)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
                    elif self._main_rect_finder.hold_and_release == 1:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_rect_finder.x_offset) + "), 0 + (" + str(self._main_rect_finder.y_offset) + "), True)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
                    elif self._main_rect_finder.hold_and_release == 2:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_rect_finder.x_offset) + "), 0 + (" + str(self._main_rect_finder.y_offset) + "), True)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0 + (" + str(self._main_rect_finder.x_offset) + "), 0 + (" + str(self._main_rect_finder.y_offset) + ") - " + str(self._main_rect_finder.release_pixel) + ", True)")
                    elif self._main_rect_finder.hold_and_release == 3:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_rect_finder.x_offset) + "), 0 + (" + str(self._main_rect_finder.y_offset) + "), True)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0 + (" + str(self._main_rect_finder.x_offset) + "), 0 + (" + str(self._main_rect_finder.y_offset) + ") + " + str(self._main_rect_finder.release_pixel) + ", True)")
                    elif self._main_rect_finder.hold_and_release == 4:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_rect_finder.x_offset) + "), 0 + (" + str(self._main_rect_finder.y_offset) + "), True)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0 + (" + str(self._main_rect_finder.x_offset) + ") - " + str(self._main_rect_finder.release_pixel) + ",  0 + (" + str(self._main_rect_finder.y_offset) + "), True)")
                    elif self._main_rect_finder.hold_and_release == 5:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_rect_finder.x_offset) + "), 0 + (" + str(self._main_rect_finder.y_offset) + "), True)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0 + (" + str(self._main_rect_finder.x_offset) + ") + " + str(self._main_rect_finder.release_pixel) + ",  0 + (" + str(self._main_rect_finder.y_offset) + "), True)")
                else:
                    self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_rect_finder.x_offset) + "), 0 + (" + str(self._main_rect_finder.y_offset) + "), True)")
                    self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
        else:
            self._code_lines.append("    "  + name + "_object.main_xy_coordinates = None")
            self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
            
        #self._code_lines.append("\n")
        
        for sub_rect in self._sub_rects_finder:
            if sub_rect.height != 0 and sub_rect.width !=0:
            
                #roi_x = str(sub_rect.roi_x - self._main_rect_finder.x)
                roi_x = str(sub_rect.roi_x)
                roi_y = str(sub_rect.roi_y)
                
                roi_width = str(sub_rect.roi_width)
                roi_height = str(sub_rect.roi_height)
                
                roi_unlimited_up = str(sub_rect.roi_unlimited_up)
                roi_unlimited_down = str(sub_rect.roi_unlimited_down)
                roi_unlimited_left = str(sub_rect.roi_unlimited_left)
                roi_unlimited_right = str(sub_rect.roi_unlimited_right)
                
                if sub_rect.use_min_max is False:  
                    
                    height = str(sub_rect.height)
                    width = str(sub_rect.width)
                    width_tolerance = str(sub_rect.width_tolerance)
                    height_tolerance = str(sub_rect.height_tolerance)
                
                    str1 = "    " + name + "_object.add_sub_component({\"height\": " + height + ", \"width\": " + width + ", \"height_tolerance\": " + height_tolerance + ", \"width_tolerance\": " + width_tolerance + "},"
                    str2 = "                             {\"roi_x\": " + roi_x + ", \"roi_y\": " + roi_y + ", \"roi_width\": " + roi_width + ", \"roi_height\": " + roi_height + ", \"roi_unlimited_up\": " + roi_unlimited_up + ", \"roi_unlimited_down\": " + roi_unlimited_down + ", \"roi_unlimited_left\": " + roi_unlimited_left + ", \"roi_unlimited_right\": " + roi_unlimited_right + "})"
                    #self._code_lines.append("    rect_finder.add_sub_rect({\"height\": " + height + ", \"width\": " + width + ", \"height_tolerance\": " + height_tolerance + ", \"width_tolerance\": " + width_tolerance + "},")
                    #self._code_lines.append("                             {\"roi_x\": " + roi_x + ", \"roi_y\": " + roi_y + ", \"roi_width\": " + roi_width + ", \"roi_height\": " + roi_height + "})")
                    
                else:
                    min_width = str(sub_rect.min_width)
                    max_width = str(sub_rect.max_width)
                    min_height = str(sub_rect.min_height)
                    max_height = str(sub_rect.max_height)
                    
                    str1 = "    " + name + "_object.add_sub_component({\"min_height\": " + min_height + ", \"max_height\": " + max_height + ", \"min_width\": " + min_width + ", \"max_width\": " + max_width + "},"
                    str2 = "                             {\"roi_x\": " + roi_x + ", \"roi_y\": " + roi_y + ", \"roi_width\": " + roi_width + ", \"roi_height\": " + roi_height + ", \"roi_unlimited_up\": " + roi_unlimited_up + ", \"roi_unlimited_down\": " + roi_unlimited_down + ", \"roi_unlimited_left\": " + roi_unlimited_left + ", \"roi_unlimited_right\": " + roi_unlimited_right + "})"
                    #self._code_lines.append("    rect_finder.add_sub_rect({\"min_height\": " + min_height + ", \"max_height\": " + max_height + ", \"min_width\": " + min_width + ", \"max_width\": " + max_width + "},")
                    #self._code_lines.append("                             {\"roi_x\": " + roi_x + ", \"roi_y\": " + roi_y + ", \"roi_width\": " + roi_width + ", \"roi_height\": " + roi_height + "})")
        
                #self._code_lines.append("\n")
                self._code_lines.append(str1)
                self._code_lines.append(str2)
                self._code_lines_for_object_finder.append(str1)
                self._code_lines_for_object_finder.append(str2)
                
                if sub_rect.click == True or sub_rect.rightclick == True or sub_rect.mousemove == True or sub_rect.hold_and_release is not None:
                    if sub_rect.x_offset is None and sub_rect.y_offset is None: 
                        if sub_rect.hold_and_release is not None:
                            if sub_rect.hold_and_release == 0:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0, False))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")
                            elif sub_rect.hold_and_release == 1:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0, False))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")
                            elif sub_rect.hold_and_release == 2:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0, False))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0, 0 - " + str(sub_rect.release_pixel) + ", False))")
                            elif sub_rect.hold_and_release == 3:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0, 0 + " + str(sub_rect.release_pixel) + ", False))")
                            elif sub_rect.hold_and_release == 4:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0 - " + str(sub_rect.release_pixel) + ", 0, False))")
                            elif sub_rect.hold_and_release == 5:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0 + " + str(sub_rect.release_pixel) + ", 0, False))")
                        else:
                            self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0, False))")
                            self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")
                    else:
                        if sub_rect.hold_and_release is not None:
                            if sub_rect.hold_and_release == 0:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_rect.x_offset) + "), 0 + (" + str(sub_rect.y_offset) + "), True))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")
                            elif sub_rect.hold_and_release == 1:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_rect.x_offset) + "), 0 + (" + str(sub_rect.y_offset) + "), True))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")
                            elif sub_rect.hold_and_release == 2:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_rect.x_offset) + "), 0 + (" + str(sub_rect.y_offset) + "), True))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0 + (" + str(sub_rect.x_offset) + "), 0 + (" + str(sub_rect.y_offset) + ") - " + str(sub_rect.release_pixel) + ", True))")
                            elif sub_rect.hold_and_release == 3:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_rect.x_offset) + "), 0 + (" + str(sub_rect.y_offset) + ")))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0 + (" + str(sub_rect.x_offset) + "), 0 + (" + str(sub_rect.y_offset) + ") + " + str(sub_rect.release_pixel) + ", True))")
                            elif sub_rect.hold_and_release == 4:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_rect.x_offset) + "), 0 + (" + str(sub_rect.y_offset) + ")))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0 + (" + str(sub_rect.x_offset) + ") - " + str(sub_rect.release_pixel) + ",  0 + (" + str(sub_rect.y_offset) + "), True))")
                            elif sub_rect.hold_and_release == 5:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_rect.x_offset) + "), 0 + (" + str(sub_rect.y_offset) + ")))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0 + (" + str(sub_rect.x_offset) + ") + " + str(sub_rect.release_pixel) + ",  0 + (" + str(sub_rect.y_offset) + "), True))")
                        else:
                            self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_rect.x_offset) + "), 0 + (" + str(sub_rect.y_offset) + "), True))")
                            self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")
                else:
                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append(None)")
                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")

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
        
        if self._main_rect_finder.click == True or self._main_rect_finder.rightclick == True or self._main_rect_finder.mousemove == True or self._main_rect_finder.hold_and_release is not None:
        
            self.mouse_or_key_is_set = True
        
            self._code_lines.append("    main_rect_pos = " + name + "_object.get_result(0)")  
        
            if mmanager_declared is False:
                self._code_lines.append("    m = MouseManager()")
                mmanager_declared = True
                
            self._code_lines.append("    time.sleep(sleep_factor)")
            
            if self._main_rect_finder.x_offset is None and self._main_rect_finder.y_offset is None: 
                if self._main_rect_finder.click == True:
                    self._code_lines.append("    m.click_2(main_rect_pos.x + (main_rect_pos.width/2), main_rect_pos.y + (main_rect_pos.height/2), 1, " + str(self._main_rect_finder.number_of_clicks) + ", " + str(self._main_rect_finder.click_delay) + ")")
                elif self._main_rect_finder.rightclick == True:
                    self._code_lines.append("    m.click(main_rect_pos.x + (main_rect_pos.width/2), main_rect_pos.y + (main_rect_pos.height/2), 2)")
                elif self._main_rect_finder.mousemove == True:
                    self._code_lines.append("    m.move(main_rect_pos.x + (main_rect_pos.width/2), main_rect_pos.y + (main_rect_pos.height/2))")
                elif self._main_rect_finder.hold_and_release is not None:
                    if self._main_rect_finder.hold_and_release == 0:
                        self._code_lines.append("    m.hold(main_rect_pos.x + (main_rect_pos.width/2), main_rect_pos.y + (main_rect_pos.height/2))")
                    elif self._main_rect_finder.hold_and_release == 1:
                        self._code_lines.append("    m.release(main_rect_pos.x + (main_rect_pos.width/2), main_rect_pos.y + (main_rect_pos.height/2))")
                    elif self._main_rect_finder.hold_and_release == 2:
                        self._code_lines.append("    m.hold(main_rect_pos.x + (main_rect_pos.width/2), main_rect_pos.y + (main_rect_pos.height/2))")
                        self._code_lines.append("    time.sleep(sleep_factor)")
                        self._code_lines.append("    m.release(main_rect_pos.x + (main_rect_pos.width/2), main_rect_pos.y + (main_rect_pos.height/2) - " + str(self._main_rect_finder.release_pixel) + ")")
                    elif self._main_rect_finder.hold_and_release == 3:
                        self._code_lines.append("    m.hold(main_rect_pos.x + (main_rect_pos.width/2), main_rect_pos.y + (main_rect_pos.height/2))")
                        self._code_lines.append("    time.sleep(sleep_factor)")
                        self._code_lines.append("    m.release(main_rect_pos.x + (main_rect_pos.width/2), main_rect_pos.y + (main_rect_pos.height/2) + " + str(self._main_rect_finder.release_pixel) + ")")
                    elif self._main_rect_finder.hold_and_release == 4:
                        self._code_lines.append("    m.hold(main_rect_pos.x + (main_rect_pos.width/2), main_rect_pos.y + (main_rect_pos.height/2))")
                        self._code_lines.append("    time.sleep(sleep_factor)")
                        self._code_lines.append("    m.release(main_rect_pos.x + (main_rect_pos.width/2) - " + str(self._main_rect_finder.release_pixel) + ", main_rect_pos.y + (main_rect_pos.height/2))")
                    elif self._main_rect_finder.hold_and_release == 5:
                        self._code_lines.append("    m.hold(main_rect_pos.x + (main_rect_pos.width/2), main_rect_pos.y + (main_rect_pos.height/2))")
                        self._code_lines.append("    time.sleep(sleep_factor)")
                        self._code_lines.append("    m.release(main_rect_pos.x + (main_rect_pos.width/2) + " + str(self._main_rect_finder.release_pixel) + ", main_rect_pos.y + (main_rect_pos.height/2))")
            else:
                if self._main_rect_finder.click == True:
                    self._code_lines.append("    m.click_2(main_rect_pos.x + (" + str(self._main_rect_finder.x_offset) + "), main_rect_pos.y + (" + str(self._main_rect_finder.y_offset) + "), 1, " + str(self._main_rect_finder.number_of_clicks) + ", " + str(self._main_rect_finder.click_delay) + ")")
                elif self._main_rect_finder.rightclick == True:
                    self._code_lines.append("    m.click(main_rect_pos.x + (" + str(self._main_rect_finder.x_offset) + "), main_rect_pos.y + (" + str(self._main_rect_finder.y_offset) + "), 2)")
                elif self._main_rect_finder.mousemove == True:
                    self._code_lines.append("    m.move(main_rect_pos.x + (" + str(self._main_rect_finder.x_offset) + "), main_rect_pos.y + (" + str(self._main_rect_finder.y_offset) + "))")
                elif self._main_rect_finder.hold_and_release is not None:
                    if self._main_rect_finder.hold_and_release == 0:
                        self._code_lines.append("    m.hold(main_rect_pos.x + (" + str(self._main_rect_finder.x_offset) + "), main_rect_pos.y + (" + str(self._main_rect_finder.y_offset) + "))")
                    elif self._main_rect_finder.hold_and_release == 1:
                        self._code_lines.append("    m.release(main_rect_pos.x + (" + str(self._main_rect_finder.x_offset) + "), main_rect_pos.y + (" + str(self._main_rect_finder.y_offset) + "))")
                    elif self._main_rect_finder.hold_and_release == 2:
                        self._code_lines.append("    m.hold(main_rect_pos.x + (" + str(self._main_rect_finder.x_offset) + "), main_rect_pos.y + (" + str(self._main_rect_finder.y_offset) + "))")
                        self._code_lines.append("    time.sleep(sleep_factor)")
                        self._code_lines.append("    m.release(main_rect_pos.x + (" + str(self._main_rect_finder.x_offset) + "), main_rect_pos.y + (" + str(self._main_rect_finder.y_offset) + ") - " + str(self._main_rect_finder.release_pixel) + ")")
                    elif self._main_rect_finder.hold_and_release == 3:
                        self._code_lines.append("    m.hold(main_rect_pos.x + (" + str(self._main_rect_finder.x_offset) + "), main_rect_pos.y + (" + str(self._main_rect_finder.y_offset) + "))")
                        self._code_lines.append("    time.sleep(sleep_factor)")
                        self._code_lines.append("    m.release(main_rect_pos.x + (" + str(self._main_rect_finder.x_offset) + "), main_rect_pos.y + (" + str(self._main_rect_finder.y_offset) + ") + " + str(self._main_rect_finder.release_pixel) + ")")
                    elif self._main_rect_finder.hold_and_release == 4:
                        self._code_lines.append("    m.hold(main_rect_pos.x + (" + str(self._main_rect_finder.x_offset) + "), main_rect_pos.y + (" + str(self._main_rect_finder.y_offset) + "))")
                        self._code_lines.append("    time.sleep(sleep_factor)")
                        self._code_lines.append("    m.release(main_rect_pos.x + (" + str(self._main_rect_finder.x_offset) + ") - " + str(self._main_rect_finder.release_pixel) + ",  main_rect_pos.y + (" + str(self._main_rect_finder.y_offset) + "))")
                    elif self._main_rect_finder.hold_and_release == 5:
                        self._code_lines.append("    m.hold(main_rect_pos.x + (" + str(self._main_rect_finder.x_offset) + "), main_rect_pos.y + (" + str(self._main_rect_finder.y_offset) + "))")
                        self._code_lines.append("    time.sleep(sleep_factor)")
                        self._code_lines.append("    m.release(main_rect_pos.x + (" + str(self._main_rect_finder.x_offset) + ") + " + str(self._main_rect_finder.release_pixel) + ",  main_rect_pos.y + (" + str(self._main_rect_finder.y_offset) + "))")
        if self._main_rect_finder.sendkeys != "":
            self.mouse_or_key_is_set = True
        
            if kmanager_declared is False:
                self._code_lines.append("    k  = KeyboardManager()")
                kmanager_declared = True
            keys = unicode(self._main_rect_finder.sendkeys, 'utf-8')
            self._code_lines.append("    time.sleep(sleep_factor)")
            
            if self._main_rect_finder.sendkeys_quotes is True:
                self._code_lines.append("    k.send(\"" + keys + "\", encrypted=" + str(self._main_rect_finder.text_encrypted) + ", delay=" + str(self._main_rect_finder.sendkeys_delay) + ", duration=" + str(self._main_rect_finder.sendkeys_duration) + ")")
            else:
                self._code_lines.append("    k.send(" + keys + ", encrypted=" + str(self._main_rect_finder.text_encrypted) + ", delay=" + str(self._main_rect_finder.sendkeys_delay) + ", duration=" + str(self._main_rect_finder.sendkeys_duration) + ")")
            
        cnt = 0
        for sub_rect in self._sub_rects_finder:
        
            if sub_rect.height != 0 and sub_rect.width !=0:
                if sub_rect.click == True or sub_rect.rightclick == True or sub_rect.mousemove == True or sub_rect.hold_and_release is not None:
                
                    self.mouse_or_key_is_set = True
            
                    self._code_lines.append("    sub_rect_" + str(cnt) + "_pos = " + name + "_object.get_result(0, " + str(cnt) + ")")  
                
                    if mmanager_declared is False:
                        self._code_lines.append("    m = MouseManager()")
                        mmanager_declared = True
                    self._code_lines.append("    time.sleep(sleep_factor)")
                    

                    if sub_rect.x_offset is None and sub_rect.y_offset is None:    
                        if sub_rect.click == True:
                            self._code_lines.append("    m.click_2(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2), sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2), 1, " + str(sub_rect.number_of_clicks) + ", " + str(sub_rect.click_delay) + ")")
                        elif sub_rect.rightclick == True:
                            self._code_lines.append("    m.click(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2), sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2), 2)")
                        elif sub_rect.mousemove == True:
                            self._code_lines.append("    m.move(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2), sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2))")
                        elif sub_rect.hold_and_release is not None:
                            if sub_rect.hold_and_release == 0:
                                self._code_lines.append("    m.hold(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2), sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2))")
                            elif sub_rect.hold_and_release == 1:
                                self._code_lines.append("    m.release(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2), sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2))")
                            elif sub_rect.hold_and_release == 2:
                                self._code_lines.append("    m.hold(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2), sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2))")
                                self._code_lines.append("    time.sleep(sleep_factor)")
                                self._code_lines.append("    m.release(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2), sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2) - " + str(sub_rect.release_pixel) + ")")
                            elif sub_rect.hold_and_release == 3:
                                self._code_lines.append("    m.hold(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2), sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2))")
                                self._code_lines.append("    time.sleep(sleep_factor)")
                                self._code_lines.append("    m.release(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2), sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2) + " + str(sub_rect.release_pixel) + ")")
                            elif sub_rect.hold_and_release == 4:
                                self._code_lines.append("    m.hold(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2), sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2))")
                                self._code_lines.append("    time.sleep(sleep_factor)")
                                self._code_lines.append("    m.release(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2) - " + str(sub_rect.release_pixel) + ", sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2))")
                            elif sub_rect.hold_and_release == 5:
                                self._code_lines.append("    m.hold(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2), sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2))")
                                self._code_lines.append("    time.sleep(sleep_factor)")
                                self._code_lines.append("    m.release(sub_rect_" + str(cnt) + "_pos.x + (sub_rect_" + str(cnt) + "_pos.width/2) + " + str(sub_rect.release_pixel) + ", sub_rect_" + str(cnt) + "_pos.y + (sub_rect_" + str(cnt) + "_pos.height/2))")
                    else:
                        if sub_rect.click == True:
                            self._code_lines.append("    m.click_2(sub_rect_" + str(cnt) + "_pos.x + (" + str(sub_rect.x_offset) + "), sub_rect_" + str(cnt) + "_pos.y + (" + str(sub_rect.y_offset) + "), 1, " + str(sub_rect.number_of_clicks) + ", " + str(sub_rect.click_delay) + ")")
                        elif sub_rect.rightclick == True:
                            self._code_lines.append("    m.click(sub_rect_" + str(cnt) + "_pos.x + (" + str(sub_rect.x_offset) + "), sub_rect_" + str(cnt) + "_pos.y + (" + str(sub_rect.y_offset) + "), 2)")
                        elif sub_rect.mousemove == True:
                            self._code_lines.append("    m.move(sub_rect_" + str(cnt) + "_pos.x + (" + str(sub_rect.x_offset) + "), sub_rect_" + str(cnt) + "_pos.y + (" + str(sub_rect.y_offset) + "))")
                        elif sub_rect.hold_and_release is not None:
                            if sub_rect.hold_and_release == 0:
                                self._code_lines.append("    m.hold(sub_rect_" + str(cnt) + "_pos.x + (" + str(sub_rect.x_offset) + "), sub_rect_" + str(cnt) + "_pos.y + (" + str(sub_rect.y_offset) + "))")
                            elif sub_rect.hold_and_release == 1:
                                self._code_lines.append("    m.release(sub_rect_" + str(cnt) + "_pos.x + (" + str(sub_rect.x_offset) + "), sub_rect_" + str(cnt) + "_pos.y + (" + str(sub_rect.y_offset) + "))")
                            elif sub_rect.hold_and_release == 2:
                                self._code_lines.append("    m.hold(sub_rect_" + str(cnt) + "_pos.x + (" + str(sub_rect.x_offset) + "), sub_rect_" + str(cnt) + "_pos.y + (" + str(sub_rect.y_offset) + "))")
                                self._code_lines.append("    time.sleep(sleep_factor)")
                                self._code_lines.append("    m.release(sub_rect_" + str(cnt) + "_pos.x + (" + str(sub_rect.x_offset) + "), sub_rect_" + str(cnt) + "_pos.y + (" + str(sub_rect.y_offset) + ") - " + str(sub_rect.release_pixel) + ")")
                            elif sub_rect.hold_and_release == 3:
                                self._code_lines.append("    m.hold(sub_rect_" + str(cnt) + "_pos.x + (" + str(sub_rect.x_offset) + "), sub_rect_" + str(cnt) + "_pos.y + (" + str(sub_rect.y_offset) + "))")
                                self._code_lines.append("    time.sleep(sleep_factor)")
                                self._code_lines.append("    m.release(sub_rect_" + str(cnt) + "_pos.x + (" + str(sub_rect.x_offset) + "), sub_rect_" + str(cnt) + "_pos.y + (" + str(sub_rect.y_offset) + ") + " + str(sub_rect.release_pixel) + ")")
                            elif sub_rect.hold_and_release == 4:
                                self._code_lines.append("    m.hold(sub_rect_" + str(cnt) + "_pos.x + (" + str(sub_rect.x_offset) + "), sub_rect_" + str(cnt) + "_pos.y + (" + str(sub_rect.y_offset) + "))")
                                self._code_lines.append("    time.sleep(sleep_factor)")
                                self._code_lines.append("    m.release(sub_rect_" + str(cnt) + "_pos.x + (" + str(sub_rect.x_offset) + ") - " + str(sub_rect.release_pixel) + ",  sub_rect_" + str(cnt) + "_pos.y + (" + str(sub_rect.y_offset) + "))")
                            elif sub_rect.hold_and_release == 5:
                                self._code_lines.append("    m.hold(sub_rect_" + str(cnt) + "_pos.x + (" + str(sub_rect.x_offset) + "), sub_rect_" + str(cnt) + "_pos.y + (" + str(sub_rect.y_offset) + "))")
                                self._code_lines.append("    time.sleep(sleep_factor)")
                                self._code_lines.append("    m.release(sub_rect_" + str(cnt) + "_pos.x + (" + str(sub_rect.x_offset) + ") + " + str(sub_rect.release_pixel) + ",  sub_rect_" + str(cnt) + "_pos.y + (" + str(sub_rect.y_offset) + "))")
                        
                if sub_rect.sendkeys != "":
                
                    self.mouse_or_key_is_set = True
                
                    if kmanager_declared is False:
                        self._code_lines.append("    k  = KeyboardManager()")
                        kmanager_declared = True
                    keys = unicode(sub_rect.sendkeys, 'utf-8')
                    self._code_lines.append("    time.sleep(sleep_factor)")
                    
                    if sub_rect.sendkeys_quotes is True:
                        self._code_lines.append("    k.send(\"" + keys + "\", encrypted=" + str(sub_rect.text_encrypted) + ", delay=" + str(sub_rect.sendkeys_delay) + ", duration=" + str(sub_rect.sendkeys_duration) + ")")
                    else:
                        self._code_lines.append("    k.send(" + keys + ", encrypted=" + str(sub_rect.text_encrypted) + ", delay=" + str(sub_rect.sendkeys_delay) + ", duration=" + str(sub_rect.sendkeys_duration) + ")")
                       
                    
                cnt = cnt + 1
        self._code_lines.append("")
        
        
        #self._code_lines.append("def " + name + "():")
        
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
        
        if self.timeout_exception is False:
        
            self._code_lines.append("    info_manager = InfoManager()")
            self._code_lines.append("    info_manager.set_info(\"DISABLE REPORTS\", True)")
        
        
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
                self._code_lines.append("    elif wait_time + wait_time_disappear < " + repr(self.critical) + ":")
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
  
    def build_code(self):
        if self._main_rect_finder is None:
            return
            
        name = self.object_name
        
        if name == "":
            name = time.strftime("rect_finder_%d_%m_%y_%H_%M_%S")
            
        python_file = open('c:\\alan\\code.txt', 'w')
        
        python_file.write("def " + name + "():" + "\n")
        python_file.write("    rect_finder = RectFinder(\"" + name + "\")" + "\n")
        
        if self._main_rect_finder.use_min_max is False:                  
            height = str(self._main_rect_finder.height)
            width = str(self._main_rect_finder.width)
            width_tolerance = str(self._main_rect_finder.width_tolerance)
            height_tolerance = str(self._main_rect_finder.height_tolerance)
            python_file.write("    rect_finder.set_main_rect({\"height\": " + height + ", \"width\": " + width + ", \"height_tolerance\": " + height_tolerance + ", \"width_tolerance\": " + width_tolerance + "}," + "\n")
        else:
            min_width = str(self._main_rect_finder.min_width)
            max_width = str(self._main_rect_finder.max_width)
            min_height = str(self._main_rect_finder.min_height)
            max_height = str(self._main_rect_finder.max_height)
            python_file.write("    rect_finder.set_main_rect({\"min_width\": " + min_width + ", \"max_width\": " + max_width + ", \"min_height\": " + min_height + ", \"max_height\": " + max_height + "}," + "\n")
            
        for sub_rect in self._sub_rects_finder:
            if sub_rect.height != 0 and sub_rect.width !=0:
            
                #roi_x = str(sub_rect.roi_x - self._main_rect_finder.x)
                roi_x = str(sub_rect.roi_x)
                roi_y = str(sub_rect.roi_y)
                
                roi_width = str(sub_rect.roi_width)
                roi_height = str(sub_rect.roi_height)

                
                if self._main_rect_finder.use_min_max is False:  
                    
                    height = str(sub_rect.height)
                    width = str(sub_rect.width)
                    width_tolerance = str(sub_rect.width_tolerance)
                    height_tolerance = str(sub_rect.height_tolerance)
                
                    python_file.write("    rect_finder.add_sub_rect({\"height\": " + height + ", \"width\": " + width + ", \"height_tolerance\": " + height_tolerance + ", \"width_tolerance\": " + width_tolerance + "}," + "\n")
                    python_file.write("                               {\"roi_x\": " + roi_x + ", \"roi_y\": " + roi_y + ", \"roi_width\": " + width + ", \"roi_height\": " + height + "})" + "\n")
                    
                else:
                    min_width = str(sub_rect.min_width)
                    max_width = str(sub_rect.max_width)
                    min_height = str(sub_rect.min_height)
                    max_height = str(sub_rect.max_height)
                    
                    python_file.write("    rect_finder.add_sub_rect({\"min_height\": " + min_height + ", \"max_height\": " + max_height + ", \"min_width\": " + min_width + ", \"max_width\": " + max_width + "}," + "\n")
                    python_file.write("                               {\"roi_x\": " + roi_x + ", \"roi_y\": " + roi_y + ", \"roi_width\": " + roi_width + ", \"roi_height\": " + roi_height + "})" + "\n")
                    
        
            
  
    def build_xml(self):
        
        if self._main_rect_finder is None:
            return

        name = str(self.object_name)
        
        if name == "":
            name = time.strftime("rect_finder_%d_%m_%y_%H_%M_%S")
            self.object_name = name
        
        root = ET.Element("rect_finder")
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

        main_rect_node = ET.SubElement(root, "main_rect")

        x_node = ET.SubElement(main_rect_node, "x")
        #x_node.set("name", "blah")
        x_node.text = str(self._main_rect_finder.x)
        
        y_node = ET.SubElement(main_rect_node, "y")
        y_node.text = str(self._main_rect_finder.y)
        
        width_node = ET.SubElement(main_rect_node, "width")
        width_node.text = str(self._main_rect_finder.width)
        
        height_node = ET.SubElement(main_rect_node, "height")
        height_node.text = str(self._main_rect_finder.height)
        
        min_width_node = ET.SubElement(main_rect_node, "min_width")
        min_width_node.text = str(self._main_rect_finder.min_width)
        
        max_width_node = ET.SubElement(main_rect_node, "max_width")
        max_width_node.text = str(self._main_rect_finder.max_width)
        
        min_height_node = ET.SubElement(main_rect_node, "min_height")
        min_height_node.text = str(self._main_rect_finder.min_height)
        
        max_height_node = ET.SubElement(main_rect_node, "max_height")
        max_height_node.text = str(self._main_rect_finder.max_height)
        
        width_tolerance_node = ET.SubElement(main_rect_node, "width_tolerance")
        width_tolerance_node.text = str(self._main_rect_finder.width_tolerance)
        
        height_tolerance_node = ET.SubElement(main_rect_node, "height_tolerance")
        height_tolerance_node.text = str(self._main_rect_finder.height_tolerance)
        
        use_min_max_node = ET.SubElement(main_rect_node, "use_min_max")
        use_min_max_node.text = str(self._main_rect_finder.use_min_max)
        
        use_tolerance_node = ET.SubElement(main_rect_node, "use_tolerance")
        use_tolerance_node.text = str(self._main_rect_finder.use_tolerance)
        
        """
        find_node = ET.SubElement(main_rect_node, "find")
        find_node.text = str(self.find)
        
        wait_node = ET.SubElement(main_rect_node, "wait")
        wait_node.text = str(self.wait)
        
        timeout_node = ET.SubElement(main_rect_node, "timeout")
        timeout_node.text = str(self.timeout)
        """
        
        click_node = ET.SubElement(main_rect_node, "click")
        click_node.text = str(self._main_rect_finder.click)
        
        number_of_clicks_node = ET.SubElement(main_rect_node, "number_of_clicks")
        number_of_clicks_node.text = str(self._main_rect_finder.number_of_clicks)
        
        click_delay_node = ET.SubElement(main_rect_node, "click_delay")
        click_delay_node.text = str(self._main_rect_finder.click_delay)

        #doubleclick_node = ET.SubElement(main_rect_node, "doubleclick")
        #doubleclick_node.text = str(self._main_rect_finder.doubleclick)
        
        rightclick_node = ET.SubElement(main_rect_node, "rightclick")
        rightclick_node.text = str(self._main_rect_finder.rightclick)
        
        mousemove_node = ET.SubElement(main_rect_node, "mousemove")
        mousemove_node.text = str(self._main_rect_finder.mousemove)
        
        x_offset_node = ET.SubElement(main_rect_node, "x_offset")
        x_offset_node.text = str(self._main_rect_finder.x_offset)
        
        y_offset_node = ET.SubElement(main_rect_node, "y_offset")
        y_offset_node.text = str(self._main_rect_finder.y_offset)
        
        hold_release_node = ET.SubElement(main_rect_node, "hold_and_release")
        hold_release_node.text = str(self._main_rect_finder.hold_and_release)
        
        release_pixel_node = ET.SubElement(main_rect_node, "release_pixel")
        release_pixel_node.text = str(self._main_rect_finder.release_pixel)

        sendkeys_node = ET.SubElement(main_rect_node, "sendkeys")
        
        sendkeys_node.set("encrypted", str(self._main_rect_finder.text_encrypted))
        sendkeys_node.set("delay", str(self._main_rect_finder.sendkeys_delay))
        sendkeys_node.set("duration", str(self._main_rect_finder.sendkeys_duration))
        sendkeys_node.set("quotes", str(self._main_rect_finder.sendkeys_quotes))
        
        #print self._main_rect_finder.sendkeys
        
        sendkey_text = unicode(self._main_rect_finder.sendkeys, 'utf-8')
        
        #print
        
        sendkeys_node.append(ET.Comment(' --><![CDATA[' + sendkey_text.replace(']]>', ']]]]><![CDATA[>') + ']]><!-- '))
        #sendkeys_node.text = unicode(self._main_rect_finder.sendkeys, 'utf-8')

    
        #tree.write("filename.xml")

        height = str(self._main_rect_finder.height)
        width = str(self._main_rect_finder.width)
        
        sub_rects_root = ET.SubElement(root, "sub_rects")
        
        cnt = 1
        for sub_rect in self._sub_rects_finder:
            if sub_rect.height != 0 and sub_rect.width !=0:
            
                sub_rect_node = ET.SubElement(sub_rects_root, "sub_rect") #ET.SubElement(sub_rects_root, "sub_rect_" + str(cnt))
                sub_rect_node.set("id", str(cnt))
            
                x_node = ET.SubElement(sub_rect_node, "x")
                #x_node.set("name", "blah")
                x_node.text = str(sub_rect.x)
                
                y_node = ET.SubElement(sub_rect_node, "y")
                y_node.text = str(sub_rect.y)
                
                width_node = ET.SubElement(sub_rect_node, "width")
                width_node.text = str(sub_rect.width)
                
                height_node = ET.SubElement(sub_rect_node, "height")
                height_node.text = str(sub_rect.height)
                
                min_width_node = ET.SubElement(sub_rect_node, "min_width")
                min_width_node.text = str(sub_rect.min_width)
                
                max_width_node = ET.SubElement(sub_rect_node, "max_width")
                max_width_node.text = str(sub_rect.max_width)
                
                min_height_node = ET.SubElement(sub_rect_node, "min_height")
                min_height_node.text = str(sub_rect.min_height)
                
                max_height_node = ET.SubElement(sub_rect_node, "max_height")
                max_height_node.text = str(sub_rect.max_height)
                
                width_tolerance_node = ET.SubElement(sub_rect_node, "width_tolerance")
                width_tolerance_node.text = str(sub_rect.width_tolerance)
                
                height_tolerance_node = ET.SubElement(sub_rect_node, "height_tolerance")
                height_tolerance_node.text = str(sub_rect.height_tolerance)
                
                use_min_max_node = ET.SubElement(sub_rect_node, "use_min_max")
                use_min_max_node.text = str(sub_rect.use_min_max)
                
                use_tolerance_node = ET.SubElement(sub_rect_node, "use_tolerance")
                use_tolerance_node.text = str(sub_rect.use_tolerance)
                
                roi_x_node = ET.SubElement(sub_rect_node, "roi_x")
                roi_x_node.text = str(sub_rect.roi_x)
                
                roi_y_node = ET.SubElement(sub_rect_node, "roi_y")
                roi_y_node.text = str(sub_rect.roi_y)
                
                roi_width_node = ET.SubElement(sub_rect_node, "roi_width")
                roi_width_node.text = str(sub_rect.roi_width)
                
                roi_height_node = ET.SubElement(sub_rect_node, "roi_height")
                roi_height_node.text = str(sub_rect.roi_height)
                
                roi_unlimited_up_node = ET.SubElement(sub_rect_node, "roi_unlimited_up")
                roi_unlimited_up_node.text = str(sub_rect.roi_unlimited_up)
                
                roi_unlimited_down_node = ET.SubElement(sub_rect_node, "roi_unlimited_down")
                roi_unlimited_down_node.text = str(sub_rect.roi_unlimited_down)
                
                roi_unlimited_left_node = ET.SubElement(sub_rect_node, "roi_unlimited_left")
                roi_unlimited_left_node.text = str(sub_rect.roi_unlimited_left)
                
                roi_unlimited_right_node = ET.SubElement(sub_rect_node, "roi_unlimited_right")
                roi_unlimited_right_node.text = str(sub_rect.roi_unlimited_right)
                
                click_node = ET.SubElement(sub_rect_node, "click")
                click_node.text = str(sub_rect.click)
                
                number_of_clicks_node = ET.SubElement(sub_rect_node, "number_of_clicks")
                number_of_clicks_node.text = str(sub_rect.number_of_clicks)

                click_delay_node = ET.SubElement(sub_rect_node, "click_delay")
                click_delay_node.text = str(sub_rect.click_delay)
                
                #doubleclick_node = ET.SubElement(sub_rect_node, "doubleclick")
                #doubleclick_node.text = str(sub_rect.doubleclick)
                
                rightclick_node = ET.SubElement(sub_rect_node, "rightclick")
                rightclick_node.text = str(sub_rect.rightclick)

                mousemove_node = ET.SubElement(sub_rect_node, "mousemove")
                mousemove_node.text = str(sub_rect.mousemove)
                
                x_offset_node = ET.SubElement(sub_rect_node, "x_offset")
                x_offset_node.text = str(sub_rect.x_offset)

                y_offset_node = ET.SubElement(sub_rect_node, "y_offset")
                y_offset_node.text = str(sub_rect.y_offset)
                
                hold_release_node = ET.SubElement(sub_rect_node, "hold_and_release")
                hold_release_node.text = str(sub_rect.hold_and_release)

                release_pixel_node = ET.SubElement(sub_rect_node, "release_pixel")
                release_pixel_node.text = str(sub_rect.release_pixel)
                
                sendkeys_node = ET.SubElement(sub_rect_node, "sendkeys")
                sendkeys_node.set("encrypted", str(sub_rect.text_encrypted))
                sendkeys_node.set("delay", str(sub_rect.sendkeys_delay))
                sendkeys_node.set("duration", str(sub_rect.sendkeys_duration))
                sendkeys_node.set("quotes", str(sub_rect.sendkeys_quotes))
                
                #sendkeys_node.text = unicode(sub_rect.sendkeys, 'utf-8')
                sendkeys_node.append(ET.Comment(' --><![CDATA[' + unicode(sub_rect.sendkeys.replace(']]>', ']]]]><![CDATA[>'), 'utf-8') + ']]><!-- '))
                
                cnt = cnt + 1
        
        code_blocks_root = ET.SubElement(root, "code_blocks")
        for block in self._code_blocks:
            block_start_line = block[0]
            block_text = block[1]
            block_end_line = block[2]
           # block_text = unicode(block_text, "utf-8")
            code_block = ET.SubElement(code_blocks_root, "code_block") #ET.SubElement(sub_rects_root, "sub_rect_" + str(cnt))
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
                
        python_file = open(self._path + os.sep + self.object_name + "_RectFinder.xml", 'w')
        tree.write(python_file, encoding='utf-8', xml_declaration=True) 
        #python_file.write(rough_string)        
        python_file.close()
        
        
        """
        python_file.write("def search_on_google():" + "\n")
        python_file.write("    rect = RectFinder(\"test\")" + "\n")
        python_file.write("    rect.set_main_rect({\"height\": " + height + ", \"width\": " + width + ", \"height_tolerance\": 15, \"width_tolerance\": 15}," + "\n")
        
        for sub_rect in self._sub_rects_finder:
            if sub_rect.height != 0 and sub_rect.width !=0:
            
                x = str(sub_rect.x - self._main_rect_finder.x)
                y = str(sub_rect.y - self._main_rect_finder.y)
                height = str(sub_rect.height)
                width = str(sub_rect.width)
                
                python_file.write("    rect.add_sub_rect({\"height\": " + height + ", \"width\": " + width + ", \"height_tolerance\": 15, \"width_tolerance\": 15}," + "\n")
                python_file.write("                      {\"roi_x\": " + x + ", \"roi_y\": " + y + ", \"roi_width\": " + width + ", \"roi_height\": " + height + "})" + "\n")
        
        """
        python_file.close()
        
    def build_code_blocks(self):
        for block in self.parent._code_blocks:
            python_file = open('c:\\alan\\code.txt', 'w')

    def build_objects(self):
        
        #print self._path + "\\rect_finder.xml"
        
        try:
            filehandler = open(self._path + os.sep + self._xml_name,"r")
        except:
            return
            
        doc = minidom.parse(filehandler)
        #data_root = raw_data.getroot()
        
        root_node = doc.getElementsByTagName("rect_finder")[0]
        
        self._main_rect_finder = MainRectForGui()
        
        main_rect_node = doc.getElementsByTagName("main_rect")[0]
        #self.object_name = main_rect_node.getElementsByTagName("name")[0].firstChild.nodeValue
        
        self.object_name = root_node.attributes["name"].value
        #self.find = main_rect_node.attributes["find"].value
        #self.wait = main_rect_node.attributes["wait"].value
        self.timeout = int(root_node.attributes["timeout"].value)
        
        
        if root_node.attributes["timeout_exception"].value == "True":
            self.timeout_exception = True
        else:
            self.timeout_exception = False
        
        self.args_number = int(root_node.attributes["args"].value)
        
        self._main_rect_finder.x = int(main_rect_node.getElementsByTagName("x")[0].firstChild.nodeValue)
        self._main_rect_finder.y = int(main_rect_node.getElementsByTagName("y")[0].firstChild.nodeValue)
        self._main_rect_finder.height = int(main_rect_node.getElementsByTagName("height")[0].firstChild.nodeValue)
        self._main_rect_finder.width = int(main_rect_node.getElementsByTagName("width")[0].firstChild.nodeValue)
        self._main_rect_finder.height = int(main_rect_node.getElementsByTagName("height")[0].firstChild.nodeValue)
        self._main_rect_finder.min_width = int(main_rect_node.getElementsByTagName("min_width")[0].firstChild.nodeValue)
        self._main_rect_finder.min_height = int(main_rect_node.getElementsByTagName("min_height")[0].firstChild.nodeValue)
        self._main_rect_finder.max_width = int(main_rect_node.getElementsByTagName("max_width")[0].firstChild.nodeValue)
        self._main_rect_finder.max_height = int(main_rect_node.getElementsByTagName("max_height")[0].firstChild.nodeValue)
        self._main_rect_finder.width_tolerance = int(main_rect_node.getElementsByTagName("width_tolerance")[0].firstChild.nodeValue)
        self._main_rect_finder.height_tolerance = int(main_rect_node.getElementsByTagName("height_tolerance")[0].firstChild.nodeValue)
        #self.timeout = int(main_rect_node.getElementsByTagName("timeout")[0].firstChild.nodeValue)               
        
        if "True" in main_rect_node.getElementsByTagName("use_tolerance")[0].firstChild.nodeValue:
            self._main_rect_finder.use_tolerance = True
        else:
            self._main_rect_finder.use_tolerance = False
        
        if "True" in main_rect_node.getElementsByTagName("use_min_max")[0].firstChild.nodeValue:
            self._main_rect_finder.use_min_max = True
        else:
            self._main_rect_finder.use_min_max = False

        if "True" in root_node.attributes["find"].value: #main_rect_node.getElementsByTagName("find")[0].firstChild.nodeValue:
            self.find = True
        else:
            self.find = False    
            
        if "True" in root_node.attributes["wait"].value: #main_rect_node.getElementsByTagName("wait")[0].firstChild.nodeValue:
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
            
        if "True" in main_rect_node.getElementsByTagName("click")[0].firstChild.nodeValue:
            self._main_rect_finder.click = True
            self.mouse_or_key_is_set = True
            self._main_rect_finder.mouse_or_key_is_set = True
        else:
            self._main_rect_finder.click = False
            
        try:
            self._main_rect_finder.number_of_clicks = int(main_rect_node.getElementsByTagName("number_of_clicks")[0].firstChild.nodeValue)
        except:
            pass
            
        try:
            self._main_rect_finder.click_delay = int(main_rect_node.getElementsByTagName("click_delay")[0].firstChild.nodeValue)
        except:
            pass
            
        try:
            
            if "True" in main_rect_node.getElementsByTagName("doubleclick")[0].firstChild.nodeValue:
                #self._main_rect_finder.doubleclick = True
                self._main_rect_finder.click = True
                self._main_rect_finder.number_of_clicks = 2
                self._main_rect_finder.click_delay = 10
                self.mouse_or_key_is_set = True
                self._main_rect_finder.mouse_or_key_is_set = True
        except:
            pass
            
        if "True" in main_rect_node.getElementsByTagName("rightclick")[0].firstChild.nodeValue:
            self._main_rect_finder.rightclick = True
            self.mouse_or_key_is_set = True
            self._main_rect_finder.mouse_or_key_is_set = True
        else:
            self._main_rect_finder.rightclick = False
            
        if "True" in main_rect_node.getElementsByTagName("mousemove")[0].firstChild.nodeValue:
            self._main_rect_finder.mousemove = True
            self.mouse_or_key_is_set = True
            self._main_rect_finder.mouse_or_key_is_set = True
        else:
            self._main_rect_finder.mousemove = False
            
        try:
            if "None" in main_rect_node.getElementsByTagName("x_offset")[0].firstChild.nodeValue:
                self._main_rect_finder.x_offset = None
            else:
                self._main_rect_finder.x_offset = int(main_rect_node.getElementsByTagName("x_offset")[0].firstChild.nodeValue)
        except:
            pass
            
        try:
            if "None" in main_rect_node.getElementsByTagName("y_offset")[0].firstChild.nodeValue:
                self._main_rect_finder.y_offset = None
            else:
                self._main_rect_finder.y_offset = int(main_rect_node.getElementsByTagName("y_offset")[0].firstChild.nodeValue)
        except:
            pass
            
        try:    
            if "None" in main_rect_node.getElementsByTagName("hold_and_release")[0].firstChild.nodeValue:
                self._main_rect_finder.hold_and_release = None
            else:
                self._main_rect_finder.hold_and_release = int(main_rect_node.getElementsByTagName("hold_and_release")[0].firstChild.nodeValue)
                self._main_rect_finder.mouse_or_key_is_set = True
                self.mouse_or_key_is_set = True
        except:
            pass
            
        try:    
            self._main_rect_finder.release_pixel = int(main_rect_node.getElementsByTagName("release_pixel")[0].firstChild.nodeValue)
        except:
            pass
            
        if "True" in root_node.attributes["enable_performance"].value:
            self.enable_performance = True
        else:
            self.enable_performance = False
            
        self.warning = float(root_node.attributes["warning_value"].value)
        self.critical = float(root_node.attributes["critical_value"].value)
            
        #self._main_rect_finder.critical = float(root_node.attributes["critical_value"].value)
        
        if main_rect_node.getElementsByTagName("sendkeys")[0].attributes["encrypted"].value == "True":
            self._main_rect_finder.text_encrypted = True
        else:
            self._main_rect_finder.text_encrypted = False
            
        if main_rect_node.getElementsByTagName("sendkeys")[0].attributes["quotes"].value == "True":
            self._main_rect_finder.sendkeys_quotes = True
        else:
            self._main_rect_finder.sendkeys_quotes = False
            
        try:
            self._main_rect_finder.sendkeys_delay = int(main_rect_node.getElementsByTagName("sendkeys")[0].attributes["delay"].value)
        except:
            pass
            
        try:
            self._main_rect_finder.sendkeys_duration = int(main_rect_node.getElementsByTagName("sendkeys")[0].attributes["duration"].value)
        except:
            pass
            
        try:
            self._main_rect_finder.sendkeys = main_rect_node.getElementsByTagName("sendkeys")[0].toxml()
            self._main_rect_finder.sendkeys = re.sub("<sendkeys(.*?)><!-- -->", "", self._main_rect_finder.sendkeys)
            self._main_rect_finder.sendkeys = self._main_rect_finder.sendkeys.replace("<!-- --></sendkeys>","")
            self._main_rect_finder.sendkeys = self._main_rect_finder.sendkeys.replace("<![CDATA[","")
            self._main_rect_finder.sendkeys = self._main_rect_finder.sendkeys.replace("]]>","")
            self._main_rect_finder.sendkeys = self._main_rect_finder.sendkeys.encode('utf-8')
            
            if self._main_rect_finder.sendkeys != "":
                self.mouse_or_key_is_set = True
                self._main_rect_finder.mouse_or_key_is_set = True
            
        except AttributeError:
            self._main_rect_finder.sendkeys = ''.encode('utf-8')
        
        self.__flag_capturing_main_rect = False
        self.__flag_capturing_sub_rect_roi = True
                
        sub_rect_nodes = doc.getElementsByTagName("sub_rect")
        
        #print len(sub_rect_nodes)

        for sub_rect_node in sub_rect_nodes:

            sub_rect_obj = SubRectForGui()
            
            #print int(sub_rect_node.getElementsByTagName("x")[0].firstChild.nodeValue)
        
            #sub_rect_node = doc.getElementsByTagName("main_rect")[0]
            #sub_rect_obj.name = sub_rect_node.getElementsByTagName("name")[0].firstChild.nodeValue
            sub_rect_obj.x = int(sub_rect_node.getElementsByTagName("x")[0].firstChild.nodeValue)
            sub_rect_obj.y = int(sub_rect_node.getElementsByTagName("y")[0].firstChild.nodeValue)
            sub_rect_obj.height = int(sub_rect_node.getElementsByTagName("height")[0].firstChild.nodeValue)
            sub_rect_obj.width = int(sub_rect_node.getElementsByTagName("width")[0].firstChild.nodeValue)
            sub_rect_obj.height = int(sub_rect_node.getElementsByTagName("height")[0].firstChild.nodeValue)
            sub_rect_obj.min_width = int(sub_rect_node.getElementsByTagName("min_width")[0].firstChild.nodeValue)
            sub_rect_obj.min_height = int(sub_rect_node.getElementsByTagName("min_height")[0].firstChild.nodeValue)
            sub_rect_obj.max_width = int(sub_rect_node.getElementsByTagName("max_width")[0].firstChild.nodeValue)
            sub_rect_obj.max_height = int(sub_rect_node.getElementsByTagName("max_height")[0].firstChild.nodeValue)
            sub_rect_obj.width_tolerance = int(sub_rect_node.getElementsByTagName("width_tolerance")[0].firstChild.nodeValue)
            sub_rect_obj.height_tolerance = int(sub_rect_node.getElementsByTagName("height_tolerance")[0].firstChild.nodeValue)
            sub_rect_obj.roi_x = int(sub_rect_node.getElementsByTagName("roi_x")[0].firstChild.nodeValue)
            sub_rect_obj.roi_y = int(sub_rect_node.getElementsByTagName("roi_y")[0].firstChild.nodeValue)
            sub_rect_obj.roi_width = int(sub_rect_node.getElementsByTagName("roi_width")[0].firstChild.nodeValue)
            sub_rect_obj.roi_height = int(sub_rect_node.getElementsByTagName("roi_height")[0].firstChild.nodeValue)
            
            try:
                if "True" in sub_rect_node.getElementsByTagName("roi_unlimited_up")[0].firstChild.nodeValue:
                    sub_rect_obj.roi_unlimited_up = True
                else:
                    sub_rect_obj.roi_unlimited_up = False
            except:
                sub_rect_obj.roi_unlimited_up = False
                
            try:
                if "True" in sub_rect_node.getElementsByTagName("roi_unlimited_down")[0].firstChild.nodeValue:
                    sub_rect_obj.roi_unlimited_down = True
                else:
                    sub_rect_obj.roi_unlimited_down = False
            except:
                sub_rect_obj.roi_unlimited_down = False
                
            try:
                if "True" in sub_rect_node.getElementsByTagName("roi_unlimited_left")[0].firstChild.nodeValue:
                    sub_rect_obj.roi_unlimited_left = True
                else:
                    sub_rect_obj.roi_unlimited_left = False
            except:
                sub_rect_obj.roi_unlimited_left = False
                
            try:
                if "True" in sub_rect_node.getElementsByTagName("roi_unlimited_right")[0].firstChild.nodeValue:
                    sub_rect_obj.roi_unlimited_right = True
                else:
                    sub_rect_obj.roi_unlimited_right = False
            except:
                sub_rect_obj.roi_unlimited_right = False
                
            
            if "True" in sub_rect_node.getElementsByTagName("use_tolerance")[0].firstChild.nodeValue:
                sub_rect_obj.use_tolerance = True
            else:
                sub_rect_obj.use_tolerance = False
            
            if "True" in sub_rect_node.getElementsByTagName("use_min_max")[0].firstChild.nodeValue:
                sub_rect_obj.use_min_max = True
            else:
                sub_rect_obj.use_min_max = False
                
            if "True" in sub_rect_node.getElementsByTagName("click")[0].firstChild.nodeValue:
                sub_rect_obj.click = True
                self.mouse_or_key_is_set = True
                sub_rect_obj.mouse_or_key_is_set = True
            else:
                sub_rect_obj.click = False
                
            try:
                sub_rect_obj.number_of_clicks = int(sub_rect_node.getElementsByTagName("number_of_clicks")[0].firstChild.nodeValue)
            except:
                pass
                
            try:
                sub_rect_obj.click_delay = int(sub_rect_node.getElementsByTagName("click_delay")[0].firstChild.nodeValue)
            except:
                pass
                
            try:
                if "True" in sub_rect_node.getElementsByTagName("doubleclick")[0].firstChild.nodeValue:
                    sub_rect_obj.number_of_clicks = 2
                    sub_rect_obj.click_delay = 10
                    sub_rect_obj.click = True
                    self.mouse_or_key_is_set = True
                    sub_rect_obj.mouse_or_key_is_set = True

            except:
                pass
                
            if "True" in sub_rect_node.getElementsByTagName("rightclick")[0].firstChild.nodeValue:
                sub_rect_obj.rightclick = True
                self.mouse_or_key_is_set = True
                sub_rect_obj.mouse_or_key_is_set = True
            else:
                sub_rect_obj.rightclick = False
                
            if "True" in sub_rect_node.getElementsByTagName("mousemove")[0].firstChild.nodeValue:
                sub_rect_obj.mousemove = True
                self.mouse_or_key_is_set = True
                sub_rect_obj.mouse_or_key_is_set = True
            else:
                sub_rect_obj.mousemove = False
                
            try:
                if "None" in sub_rect_node.getElementsByTagName("x_offset")[0].firstChild.nodeValue:
                    sub_rect_obj.x_offset = None
                else:
                    sub_rect_obj.x_offset = int(sub_rect_node.getElementsByTagName("x_offset")[0].firstChild.nodeValue)
            except:
                pass
                    
            try:
                if "None" in sub_rect_node.getElementsByTagName("y_offset")[0].firstChild.nodeValue:
                    sub_rect_obj.y_offset = None
                else:
                    sub_rect_obj.y_offset = int(sub_rect_node.getElementsByTagName("y_offset")[0].firstChild.nodeValue)
            except:
                pass
                
            try:    
                if "None" in sub_rect_node.getElementsByTagName("hold_and_release")[0].firstChild.nodeValue:
                    sub_rect_obj.hold_and_release = None
                else:
                    sub_rect_obj.hold_and_release = int(sub_rect_node.getElementsByTagName("hold_and_release")[0].firstChild.nodeValue)
                    self.mouse_or_key_is_set = True
                    sub_rect_obj.mouse_or_key_is_set = True
            except:
                pass
                
            try:    
                sub_rect_obj.release_pixel = int(sub_rect_node.getElementsByTagName("release_pixel")[0].firstChild.nodeValue)
            except:
                pass
                
            if sub_rect_node.getElementsByTagName("sendkeys")[0].attributes["encrypted"].value == "True":
                sub_rect_obj.text_encrypted = True
            else:
                sub_rect_obj.text_encrypted = False
                
            if sub_rect_node.getElementsByTagName("sendkeys")[0].attributes["quotes"].value == "True":
                sub_rect_obj.sendkeys_quotes = True
            else:
                sub_rect_obj.sendkeys_quotes = False
                
            try:
                sub_rect_obj.sendkeys_delay = int(sub_rect_node.getElementsByTagName("sendkeys")[0].attributes["delay"].value)
            except:
                pass               
                        
            try:
                sub_rect_obj.sendkeys_duration = int(sub_rect_node.getElementsByTagName("sendkeys")[0].attributes["duration"].value)
            except:
                pass
      
            try:
                sub_rect_obj.sendkeys = sub_rect_node.getElementsByTagName("sendkeys")[0].toxml()                
                sub_rect_obj.sendkeys = re.sub("<sendkeys(.*?)><!-- -->", "", sub_rect_obj.sendkeys)
                sub_rect_obj.sendkeys = sub_rect_obj.sendkeys.replace("<!-- --></sendkeys>","")
                sub_rect_obj.sendkeys = sub_rect_obj.sendkeys.replace("<![CDATA[","")
                sub_rect_obj.sendkeys = sub_rect_obj.sendkeys.replace("]]>","")
                sub_rect_obj.sendkeys = sub_rect_obj.sendkeys.encode('utf-8')
                
                if sub_rect_obj.sendkeys != "":
                    self.mouse_or_key_is_set = True
                    sub_rect_obj.mouse_or_key_is_set = True
            except AttributeError:
                sub_rect_obj.sendkeys = ''.encode('utf-8')
                
            self._sub_rects_finder.append(sub_rect_obj)
            
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
            
        self._main_rect_finder.mouse_or_key_is_set = self.mouse_or_key_is_set
  
        
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
                txt = doc.createTextNode(str(self._main_rect_finder.critical))
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
            critical_node.text = str(self._main_rect_finder.critical)
            
            tree = ET.ElementTree(root)
            python_file = open(filename, 'w')
            tree.write(python_file, encoding='utf-8', xml_declaration=True) 
            #python_file.write(rough_string)        
        python_file.close()            
                
class MainRectForGui:
    
    def __init__(self):
        self.name = ""
        self.x = 0
        self.y = 0
        self.height = 0
        self.width = 0
        self.min_height = 0
        self.max_height = 0
        self.min_width = 0
        self.max_width = 0
        self.height_tolerance = 15
        self.width_tolerance = 15
        self.show = True
        self.show_min_max = False
        self.use_min_max = True
        self.show_tolerance = False
        self.use_tolerance = False
        self.click = False
        self.doubleclick = False
        self.rightclick = False
        self.mousemove = False
        self.xy_offset = None
        self.x_offset = None
        self.y_offset = None
        self.hold_and_release = None
        self.release_pixel = 1
        self.number_of_clicks = 1
        self.click_delay = 10
        self.wait = True
        self.wait_disapp = False
        self.find = False
        self.args_number = 0
        self.timeout = 20
        self.timeout_exception = True
        self.sendkeys = ""
        self.sendkeys_delay = 15
        self.sendkeys_duration = 15
        self.mouse_or_key_is_set = False
        self.sendkeys_quotes = True
        self.text_encrypted = False
        self.enable_performance = True
        self.warning = 10.00
        self.critical = 15.00
        
class SubRectForGui:
    
    def __init__(self):
        self.x = 0
        self.y = 0
        self.height = 0
        self.width = 0
        self.min_height = 0
        self.max_height = 0
        self.min_width = 0
        self.max_width = 0
        self.height_tolerance = 15
        self.width_tolerance = 15
        self.roi_x = 0
        self.roi_y = 0
        self.roi_height = 0
        self.roi_width = 0
        self.roi_unlimited_up = False
        self.roi_unlimited_down = False
        self.roi_unlimited_left = False
        self.roi_unlimited_right = False
        self.deleted_x = None
        self.deleted_y = None
        self.deleted_height = None
        self.deleted_width = None
        self.show = True
        self.show_min_max = False
        self.use_min_max = True
        self.show_tolerance = False
        self.use_tolerance = False
        self.click = False
        self.doubleclick = False
        self.rightclick = False
        self.mousemove = False
        self.xy_offset = None
        self.x_offset = None
        self.y_offset = None
        self.hold_and_release = None
        self.release_pixel = 1
        self.number_of_clicks = 1
        self.click_delay = 10
        self.sendkeys = ""
        self.sendkeys_delay = 15
        self.sendkeys_duration = 15
        self.sendkeys_quotes = True
        self.text_encrypted = False
        
class AlyvixRectFinderPropertiesView(QDialog, Ui_Form):
    def __init__(self, parent):
        QDialog.__init__(self)

        # Set up the user interface from Designer.
        self.setupUi(self)
                        
        self.parent = parent
                
        self.scaling_factor = self.parent.parent.scaling_factor
        
        self.find_radio.hide()
        
        self.added_block = False
        self.keywordname_first_time_edit = False

        
        """
        self.number_bar = NumberBar(self.tab_code)
        self.number_bar.setTextEdit(self.textEdit)
        self.textEdit.installEventFilter(self)
        self.textEdit.viewport().installEventFilter(self)
        self.textEdit.setFrameStyle(QFrame.NoFrame)
        self.textEdit.setAcceptRichText(False)
        """
        
        self.textEdit = LineTextWidget() #LineTextWidget(self.tab_code)
        self.textEdit.setGeometry(QRect(8, 9, 556, 310))
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

        #self.setFixedSize(self.size())
        self.setFixedSize(int(self.frameGeometry().width() * self.scaling_factor), int(self.frameGeometry().height() * self.scaling_factor))
        
        print self.scaling_factor
        
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
                                
        self.gridLayoutWidget_2.setGeometry(QRect(int(self.gridLayoutWidget_2.geometry().x() * self.scaling_factor), int(self.gridLayoutWidget_2.geometry().y() * self.scaling_factor),
                                          int(self.gridLayoutWidget_2.geometry().width() * self.scaling_factor), int(self.gridLayoutWidget_2.geometry().height() * self.scaling_factor)))

        #self.setWindowTitle('Application Object Properties')
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)
        
        if self.parent.action == "edit":
            self.namelineedit.setEnabled(False)
        
        if self.parent._main_rect_finder.show_min_max is False:
            self.show_min_max.setChecked(False)
        else:
            self.show_min_max.setChecked(True)
            
        if self.parent._main_rect_finder.show_tolerance is False:
            self.show_tolerance.setChecked(False)
        else:
            self.show_tolerance.setChecked(True)
            
        if self.parent._main_rect_finder.use_min_max is True:
            self.use_min_max.setChecked(True)
            self.use_tolerance.setChecked(False)
            
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

        else:
            self.use_min_max.setChecked(False)
            self.use_tolerance.setChecked(True)
            
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

        if self.parent._main_rect_finder.click is True:
            self.clickRadio.setChecked(True)
            self.pushButtonXYoffset.setEnabled(True)
            self.clicknumber_spinbox.setEnabled(True)
            self.labelClickNumber.setEnabled(True)
            if self.parent._main_rect_finder.number_of_clicks > 1:
                self.labelClickDelay.setEnabled(True)
                self.clickdelay_spinbox.setEnabled(True)
            else:
                self.labelClickDelay.setEnabled(False)
                self.clickdelay_spinbox.setEnabled(False)
        else:
            self.clickRadio.setChecked(False)
            self.pushButtonXYoffset.setEnabled(False)
            self.clicknumber_spinbox.setEnabled(False)
            self.clickdelay_spinbox.setEnabled(False)
            self.labelClickNumber.setEnabled(False)
            self.labelClickDelay.setEnabled(False)
            
        self.clicknumber_spinbox.setValue(self.parent._main_rect_finder.number_of_clicks)
        self.clickdelay_spinbox.setValue(self.parent._main_rect_finder.click_delay)
       
            
        """
        if self.parent._main_rect_finder.doubleclick is True:
            self.doubleclickRadio.setChecked(True)
            self.pushButtonXYoffset.setEnabled(True)
        else:
            self.doubleclickRadio.setChecked(False)
        """
            
        if self.parent._main_rect_finder.rightclick is True:
            self.rightclickRadio.setChecked(True)
            self.pushButtonXYoffset.setEnabled(True)
        else:
            self.rightclickRadio.setChecked(False)
            
        if self.parent._main_rect_finder.mousemove is True:
            self.movemouseRadio.setChecked(True)
            self.pushButtonXYoffset.setEnabled(True)
        else:
            self.movemouseRadio.setChecked(False)
            
        if self.parent._main_rect_finder.click is False \
            and self.parent._main_rect_finder.mousemove is False\
            and self.parent._main_rect_finder.hold_and_release is None\
            and self.parent._main_rect_finder.rightclick is False:
            self.dontclickRadio.setChecked(True)
            self.pushButtonXYoffset.setEnabled(False)
        else:
            self.dontclickRadio.setChecked(False)
            
        if self.parent._main_rect_finder.hold_and_release is not None:
            self.holdreleaseRadio.setChecked(True)
            self.holdreleaseComboBox.setEnabled(True)
            self.pushButtonXYoffset.setEnabled(True)
            self.holdreleaseComboBox.setCurrentIndex(self.parent._main_rect_finder.hold_and_release)
            
            if self.parent._main_rect_finder.hold_and_release == 0 or self.parent._main_rect_finder.hold_and_release == 1:
                self.holdreleaseSpinBox.setEnabled(False)
                self.holdreleaseSpinBox.setValue(self.parent._main_rect_finder.release_pixel)
            else: 
                self.holdreleaseSpinBox.setEnabled(True)
                self.holdreleaseSpinBox.setValue(self.parent._main_rect_finder.release_pixel)
                
        else:
            self.holdreleaseRadio.setChecked(False)
            self.holdreleaseComboBox.setEnabled(False)
            self.holdreleaseSpinBox.setEnabled(False)
            
        if self.parent._main_rect_finder.text_encrypted is False:
            self.text_encrypted.setChecked(False)
        else:
            self.text_encrypted.setChecked(True)
            
        if self.parent._main_rect_finder.sendkeys_quotes is False:
            self.add_quotes.setChecked(False)
        else:
            self.add_quotes.setChecked(True)
            
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
                    
        self.widget_2.hide()
        
        self.sub_rect_index = 0
        
        cnt = 1
        for sub_rect in self.parent._sub_rects_finder:
        
            if sub_rect.x == 0 and sub_rect.y == 0:
                continue
            item = QListWidgetItem()
            item.setCheckState(Qt.Checked)
            item.setText("sub_component_" + str(cnt))
            self.listWidget.addItem(item)
            cnt = cnt + 1
            
        #self.listWidget.setCurrentIndex(QModelIndex(self.listWidget.rootIndex()))
        self.listWidget.item(0).setSelected(True)
        
        self.min_width_spinbox.setValue(self.parent._main_rect_finder.min_width)
        self.max_width_spinbox.setValue(self.parent._main_rect_finder.max_width)    
        self.min_height_spinbox.setValue(self.parent._main_rect_finder.min_height)
        self.max_height_spinbox.setValue(self.parent._main_rect_finder.max_height)     
        self.height_tolerance_spinbox.setValue(self.parent._main_rect_finder.height_tolerance)
        self.width_tolerance_spinbox.setValue(self.parent._main_rect_finder.width_tolerance)
        self.timeout_spinbox.setValue(self.parent.timeout)      
        self.inserttext.setText(self.parent._main_rect_finder.sendkeys)       

        if self.parent._main_rect_finder.sendkeys == "":
            self.inserttext.setText("Type text strings and shortcuts")
        else:
            self.inserttext.setText(unicode(self.parent._main_rect_finder.sendkeys, 'utf-8'))       

        if self.parent.object_name == "":
            self.namelineedit.setText("Type the keyword name")
        else:
            self.namelineedit.setText(self.parent.object_name)      

        self.spinBoxArgs.setValue(self.parent.args_number)
        
        if self.parent._main_rect_finder.x_offset != None or self.parent._main_rect_finder.y_offset != None:
            self.pushButtonXYoffset.setText("Reset\nPoint")
        
        self.init_block_code()   
                
        self.pushButtonOk.setFocus() 
        
        if self.namelineedit.text() == "Type the keyword name":
            self.namelineedit.setFocus()           
            self.namelineedit.setText("")   

        if self.parent.parent_is_objfinder is True:
            self.wait_disapp_radio.setEnabled(False)
            self.wait_radio.setEnabled(False)
            self.timeout_spinbox.setEnabled(False)
            self.timeout_label.setEnabled(False)
            self.timeout_exception.setEnabled(False)
            self.checkBoxEnablePerformance.setEnabled(False)
            self.doubleSpinBoxWarning.setEnabled(False)
            self.doubleSpinBoxCritical.setEnabled(False)
            self.labelWarning.setEnabled(False)
            self.labelCritical.setEnabled(False)           
            
        self.spinBoxSendKeysDelay.setValue(self.parent._main_rect_finder.sendkeys_delay)
        self.spinBoxSendKeysDuration.setValue(self.parent._main_rect_finder.sendkeys_duration)
        
        self.connect(self.min_width_spinbox, SIGNAL('valueChanged(int)'), self.min_width_spinbox_change_event)
        self.connect(self.max_width_spinbox, SIGNAL('valueChanged(int)'), self.max_width_spinbox_change_event)
        self.connect(self.min_height_spinbox, SIGNAL('valueChanged(int)'), self.min_height_spinbox_change_event)
        self.connect(self.max_height_spinbox, SIGNAL('valueChanged(int)'), self.max_height_spinbox_change_event)
        
        self.connect(self.height_tolerance_spinbox, SIGNAL('valueChanged(int)'), self.height_tolerance_spinbox_event)
        self.connect(self.width_tolerance_spinbox, SIGNAL('valueChanged(int)'), self.width_tolerance_spinbox_event)
        
        
        self.connect(self.show_min_max, SIGNAL('stateChanged(int)'), self.show_min_max_event)
        self.connect(self.show_tolerance, SIGNAL('stateChanged(int)'), self.show_tolerance_event)
        
        self.connect(self.listWidget, SIGNAL('itemSelectionChanged()'), self.listWidget_selection_changed)
        self.connect(self.listWidget, SIGNAL('itemChanged(QListWidgetItem*)'), self, SLOT('listWidget_state_changed(QListWidgetItem*)'))
        
        self.connect(self.use_min_max, SIGNAL('toggled(bool)'), self.use_min_max_event)
        self.connect(self.use_tolerance, SIGNAL('stateChanged(int)'), self.use_tolerance_event)
        self.connect(self.wait_radio, SIGNAL('toggled(bool)'), self.wait_radio_event)
        
        self.connect(self.wait_disapp_radio, SIGNAL('toggled(bool)'), self.wait_disapp_radio_event)
        self.connect(self.find_radio, SIGNAL('toggled(bool)'), self.find_radio_event)
        self.connect(self.timeout_spinbox, SIGNAL('valueChanged(int)'), self.timeout_spinbox_event)
        
        self.connect(self.timeout_exception, SIGNAL('stateChanged(int)'), self.timeout_exception_event)
        
        self.connect(self.clickRadio, SIGNAL('toggled(bool)'), self.clickRadio_event)
        #self.connect(self.doubleclickRadio, SIGNAL('toggled(bool)'), self.doubleclickRadio_event)
        self.connect(self.rightclickRadio, SIGNAL('toggled(bool)'), self.rightclickRadio_event)
        self.connect(self.movemouseRadio, SIGNAL('toggled(bool)'), self.movemouseRadio_event)
        self.connect(self.dontclickRadio, SIGNAL('toggled(bool)'), self.dontclickRadio_event)
        
        self.connect(self.pushButtonXYoffset, SIGNAL('clicked()'), self.pushButtonXYoffset_event)
        
        self.connect(self.holdreleaseRadio, SIGNAL('toggled(bool)'), self.holdreleaseRadio_event)
        
        self.connect(self.holdreleaseComboBox, SIGNAL("currentIndexChanged(int)"), self.holdreleaseComboBox_event)
        self.connect(self.holdreleaseSpinBox, SIGNAL('valueChanged(int)'), self.holdreleaseSpinBox_event)
        
        self.connect(self.clicknumber_spinbox, SIGNAL('valueChanged(int)'), self.clicknumber_spinbox_change_event)    
        self.connect(self.clickdelay_spinbox, SIGNAL('valueChanged(int)'), self.clickdelay_spinbox_change_event) 
        
        self.connect(self.inserttext, SIGNAL("textChanged(QString)"), self, SLOT("inserttext_event(QString)"))
        #self.connect(self.inserttext, SIGNAL("textChanged()"), self, self.inserttext_event)
        
        self.connect(self.spinBoxSendKeysDelay, SIGNAL('valueChanged(int)'), self.sendKeysDelay_spinbox_change_event)  
        self.connect(self.spinBoxSendKeysDuration, SIGNAL('valueChanged(int)'), self.sendKeysDuration_spinbox_change_event)  
        
        self.connect(self.namelineedit, SIGNAL("textChanged(QString)"), self, SLOT("namelineedit_event(QString)"))
        #self.connect(self.inserttext, SIGNAL('cursorPositionChanged ( int, int)'), self.inserttext_textchanged_event)
        self.connect(self.pushButtonAddBlock, SIGNAL('clicked()'), self.add_block_code)
        self.connect(self.pushButtonRemoveBlock, SIGNAL('clicked()'), self.remove_block_code)
        self.connect(self.listWidgetBlocks, SIGNAL('itemSelectionChanged()'), self.listWidgetBlocks_selection_changed)
        #self.connect(self.textEditCustomLines, SIGNAL("textChanged(QString)"), self, SLOT("custom_lines_text_changed(QString)"))
        
        self.connect(self.checkBoxEnablePerformance, SIGNAL('stateChanged(int)'), self.enable_performance_event)
        self.connect(self.doubleSpinBoxWarning, SIGNAL('valueChanged(double)'), self.warning_event)
        self.connect(self.doubleSpinBoxCritical, SIGNAL('valueChanged(double)'), self.critical_event)
        
        #self.inserttext.viewport().installEventFilter(self)
        self.inserttext.installEventFilter(self)
        
        self.connect(self.add_quotes, SIGNAL('stateChanged(int)'), self.add_quotes_event)
        self.connect(self.text_encrypted, SIGNAL('stateChanged(int)'), self.text_encrypted_event)
        
        self.namelineedit.installEventFilter(self)
        
        #self.connect(self.tabWidget, SIGNAL('currentChanged(int)'), self.tab_changed_event)
        
        self.connect(self.spinBoxArgs, SIGNAL('valueChanged(int)'), self.args_spinbox_change_event)
        
        self.connect(self.pushButtonOk, SIGNAL('clicked()'), self.pushButtonOk_event)
        self.connect(self.pushButtonCancel, SIGNAL('clicked()'), self.pushButtonCancel_event)
        
        ###########
        ###########
        self.connect(self.min_width_spinbox_2, SIGNAL('valueChanged(int)'), self.min_width_spinbox_change_event_2)
        self.connect(self.max_width_spinbox_2, SIGNAL('valueChanged(int)'), self.max_width_spinbox_change_event_2)
        self.connect(self.min_height_spinbox_2, SIGNAL('valueChanged(int)'), self.min_height_spinbox_change_event_2)
        self.connect(self.max_height_spinbox_2, SIGNAL('valueChanged(int)'), self.max_height_spinbox_change_event_2)
        
        self.connect(self.height_tolerance_spinbox_2, SIGNAL('valueChanged(int)'), self.height_tolerance_spinbox_event_2)
        self.connect(self.width_tolerance_spinbox_2, SIGNAL('valueChanged(int)'), self.width_tolerance_spinbox_event_2)
        
        self.connect(self.show_min_max_2, SIGNAL('stateChanged(int)'), self.show_min_max_event_2)
        self.connect(self.show_tolerance_2, SIGNAL('stateChanged(int)'), self.show_tolerance_event_2)
        self.connect(self.use_min_max_2, SIGNAL('toggled(bool)'), self.use_min_max_event_2)
        
        self.connect(self.roi_x_spinbox, SIGNAL('valueChanged(int)'), self.roi_x_spinbox_event)
        self.connect(self.roi_y_spinbox, SIGNAL('valueChanged(int)'), self.roi_y_spinbox_event)
        self.connect(self.roi_height_spinbox, SIGNAL('valueChanged(int)'), self.roi_height_spinbox_event)
        self.connect(self.roi_width_spinbox, SIGNAL('valueChanged(int)'), self.roi_width_spinbox_event)
        
        self.connect(self.clickRadio_2, SIGNAL('toggled(bool)'), self.clickRadio_event_2)
        #self.connect(self.doubleclickRadio_2, SIGNAL('toggled(bool)'), self.doubleclickRadio_event_2)
        self.connect(self.movemouseRadio_2, SIGNAL('toggled(bool)'), self.movemouseRadio_event_2)
        self.connect(self.rightclickRadio_2, SIGNAL('toggled(bool)'), self.rightclickRadio_event_2)
        self.connect(self.dontclickRadio_2, SIGNAL('toggled(bool)'), self.dontclickRadio_event_2)
        
        self.connect(self.pushButtonXYoffset_2, SIGNAL('clicked()'), self.pushButtonXYoffset_event_2)
        
        self.connect(self.holdreleaseRadio_2, SIGNAL('toggled(bool)'), self.holdreleaseRadio_event_2)
        
        self.connect(self.holdreleaseComboBox_2, SIGNAL("currentIndexChanged(int)"), self.holdreleaseComboBox_event_2)

        self.connect(self.holdreleaseSpinBox_2, SIGNAL('valueChanged(int)'), self.holdreleaseSpinBox_event_2)
        
        self.connect(self.clicknumber_spinbox_2, SIGNAL('valueChanged(int)'), self.clicknumber_spinbox_change_event_2)    
        self.connect(self.clickdelay_spinbox_2, SIGNAL('valueChanged(int)'), self.clickdelay_spinbox_change_event_2) 
        
        self.connect(self.inserttext_2, SIGNAL("textChanged(QString)"), self, SLOT("inserttext_event_2(QString)"))
        
        self.connect(self.spinBoxSendKeysDelay_2, SIGNAL('valueChanged(int)'), self.sendKeysDelay_spinbox_change_event_2) 
        self.connect(self.spinBoxSendKeysDuration_2, SIGNAL('valueChanged(int)'), self.sendKeysDuration_spinbox_change_event_2) 
        
        self.connect(self.text_encrypted_2, SIGNAL('stateChanged(int)'), self.text_encrypted_event_2)
        #self.connect(self.inserttext, SIGNAL('cursorPositionChanged ( int, int)'), self.inserttext_textchanged_event)
        
        self.connect(self.add_quotes_2, SIGNAL('stateChanged(int)'), self.add_quotes_event_2)
        
        #self.inserttext_2.viewport().installEventFilter(self)
        self.inserttext_2.installEventFilter(self)
        
        self.textEditCustomLines.installEventFilter(self)
        self.roi_y_spinbox.installEventFilter(self)
        self.roi_height_spinbox.installEventFilter(self)
        self.roi_x_spinbox.installEventFilter(self)
        self.roi_width_spinbox.installEventFilter(self)  
        
        if self.parent.last_view_index != 0:
            
            self.listWidget.setCurrentRow(self.parent.last_view_index)

        
    def pushButtonCancel_event(self):
        self.close()
        self.parent.cancel_all()
        
    def is_valid_variable_name(self, name):
        try:
            ast.parse('{} = None'.format(name))
            return True
        except (SyntaxError, ValueError, TypeError) as e:
            return False

    def pushButtonOk_event(self):
        answer = QMessageBox.Yes
        filename = self.parent._alyvix_proxy_path + os.sep + "AlyvixProxy" + self.parent._robot_file_name + ".py"
       
        arg_list = []       
        args_range = range(1, self.parent.args_number + 1)
        
        for arg_num in args_range:
            arg_list.append("arg" + str(arg_num))
        
        if self.parent._main_rect_finder.sendkeys_quotes is False:
            try:
                node = ast.parse(self.parent._main_rect_finder.sendkeys)
                
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
                QMessageBox.critical(self, "Error on main conponent", "Invalid Keystroke syntax on main conponent")
                return True
                
        cnt = 1
        for sub_rect in self.parent._sub_rects_finder:
            if sub_rect.sendkeys_quotes is False:
                try:
                    node = ast.parse(sub_rect.sendkeys)
                    
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
                    QMessageBox.critical(self, "Error on sub component " + str(cnt), "Invalid Keystroke syntax on sub component " + str(cnt))
                    return True
            cnt += 1
        
        #if self.parent.object_name == "" or self.parent.object_name == "Type the keyword name":
        if str(self.namelineedit.text().toUtf8()) == "" or str(self.namelineedit.text().toUtf8()) == "Type the keyword name":
            answer = QMessageBox.warning(self, "Warning", "The object name is empty. Do you want to create it automatically?", QMessageBox.Yes, QMessageBox.No)
        elif self.is_valid_variable_name(self.namelineedit.text()) is False or "#" in self.namelineedit.text():
            QMessageBox.critical(self, "Error", "Keyword name is invalid!")
            return
        elif os.path.isfile(filename) and self.parent.action == "new":
            filename = self.parent._alyvix_proxy_path + os.sep + "AlyvixProxy" + self.parent._robot_file_name + ".py"
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
        self.parent._main_rect_finder.min_width = self.min_width_spinbox.value()
        
        if self.parent._main_rect_finder.min_width > self.parent._main_rect_finder.max_width:
            self.parent._main_rect_finder.max_width = self.parent._main_rect_finder.min_width
            self.max_width_spinbox.setValue(self.parent._main_rect_finder.min_width)
            
        self.parent.update()

        
    def max_width_spinbox_change_event(self, event):
            
        self.parent._main_rect_finder.max_width = self.max_width_spinbox.value()
        
        if self.parent._main_rect_finder.min_width > self.parent._main_rect_finder.max_width:
            self.parent._main_rect_finder.min_width = self.parent._main_rect_finder.max_width
            self.min_width_spinbox.setValue(self.parent._main_rect_finder.max_width)
            
        self.parent.update()
        
    def min_height_spinbox_change_event(self, event):
        self.parent._main_rect_finder.min_height = self.min_height_spinbox.value()
             
        if self.parent._main_rect_finder.min_height > self.parent._main_rect_finder.max_height:
            self.parent._main_rect_finder.max_height = self.parent._main_rect_finder.min_height
            self.max_height_spinbox.setValue(self.parent._main_rect_finder.min_height)
            
            
        self.parent.update()
        
    def max_height_spinbox_change_event(self, event):
    
        self.parent._main_rect_finder.max_height = self.max_height_spinbox.value()

        if self.parent._main_rect_finder.min_height > self.parent._main_rect_finder.max_height:
            self.parent._main_rect_finder.min_height = self.parent._main_rect_finder.max_height
            self.min_height_spinbox.setValue(self.parent._main_rect_finder.max_height)

        self.parent.update()
        
    def show_min_max_event(self, event):
        if self.show_min_max.isChecked() is True:
            self.parent._main_rect_finder.show_min_max = True
            self.show_tolerance.setChecked(False)
        else:
            self.parent._main_rect_finder.show_min_max = False
        self.parent.update()
        
    def show_tolerance_event(self, event):
        if self.show_tolerance.isChecked() is True:
            self.parent._main_rect_finder.show_tolerance = True
            self.show_min_max.setChecked(False)
        else:
            self.parent._main_rect_finder.show_tolerance = False
        self.parent.update()
        
    def height_tolerance_spinbox_event(self, event):
        self.parent._main_rect_finder.height_tolerance = self.height_tolerance_spinbox.value()
        self.parent.update()
        
    def width_tolerance_spinbox_event(self, event):
        self.parent._main_rect_finder.width_tolerance = self.width_tolerance_spinbox.value()
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
            
            if self.show_min_max.isChecked() is True:
                self.show_min_max.setChecked(False)
                self.show_tolerance.setChecked(True)
            
            self.parent._main_rect_finder.use_min_max = False
            self.parent._main_rect_finder.use_tolerance = True
            
            
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
            
            if self.show_tolerance.isChecked() is True:
                self.show_tolerance.setChecked(False)
                self.show_min_max.setChecked(True)
            
            self.parent._main_rect_finder.use_min_max = True
            self.parent._main_rect_finder.use_tolerance = False
        
    def listWidget_selection_changed(self):
    
        selected_index = self.listWidget.currentRow()
        
        self.parent.last_view_index = selected_index
        
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
            self.sub_rect_index = selected_index - 1
            self.update_sub_rect_view()

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
                    self.parent._main_rect_finder.show = show
                else:
                    self.parent._sub_rects_finder[row_index-1].show = show
                    
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

    def update_sub_rect_view(self):
        index = self.sub_rect_index
    
        """
        print self.parent._sub_rects_finder[index].min_width
        print self.parent._sub_rects_finder[index].max_width 
        print self.parent._sub_rects_finder[index].min_height
        print self.parent._sub_rects_finder[index].max_height
        """
        
        self.min_width_spinbox_2.setValue(self.parent._sub_rects_finder[index].min_width)
        self.max_width_spinbox_2.setValue(self.parent._sub_rects_finder[index].max_width)    
        self.min_height_spinbox_2.setValue(self.parent._sub_rects_finder[index].min_height)
        self.max_height_spinbox_2.setValue(self.parent._sub_rects_finder[index].max_height)     
        self.height_tolerance_spinbox_2.setValue(self.parent._sub_rects_finder[index].height_tolerance)
        self.width_tolerance_spinbox_2.setValue(self.parent._sub_rects_finder[index].width_tolerance)   
        
        if self.parent._sub_rects_finder[index].x_offset != None or self.parent._sub_rects_finder[index].y_offset != None:
            self.pushButtonXYoffset_2.setText("Reset\nPoint")
        else:
            self.pushButtonXYoffset_2.setText("Interaction\nPoint")
        
        if self.parent._sub_rects_finder[index].sendkeys == "":
            self.inserttext_2.setText("Type text strings and shortcuts")
        else:
            self.inserttext_2.setText(unicode(self.parent._sub_rects_finder[index].sendkeys, 'utf-8'))
        
        if self.parent._sub_rects_finder[index].text_encrypted is False:
            self.text_encrypted_2.setChecked(False)
        else:
            self.text_encrypted_2.setChecked(True)
            
        if self.parent._sub_rects_finder[index].sendkeys_quotes is False:
            self.add_quotes_2.setChecked(False)
        else:
            self.add_quotes_2.setChecked(True)
            
        if self.parent._sub_rects_finder[index].show_min_max is False:
            self.show_min_max_2.setChecked(False)
        else:
            self.show_min_max_2.setChecked(True)
                        
        if self.parent._sub_rects_finder[self.sub_rect_index].show_tolerance is True:
            self.show_tolerance_2.setChecked(True)
        else:
            self.show_tolerance_2.setChecked(False)
            
        self.roi_x_spinbox.setValue(self.parent._sub_rects_finder[self.sub_rect_index].roi_x)
        self.roi_y_spinbox.setValue(self.parent._sub_rects_finder[self.sub_rect_index].roi_y)
        self.roi_width_spinbox.setValue(self.parent._sub_rects_finder[self.sub_rect_index].roi_width)
        self.roi_height_spinbox.setValue(self.parent._sub_rects_finder[self.sub_rect_index].roi_height)
        
        if self.parent._sub_rects_finder[self.sub_rect_index].use_min_max is True:
            self.use_min_max_2.setChecked(True)
            self.use_tolerance_2.setChecked(False)
        else:
            self.use_min_max_2.setChecked(False)
            self.use_tolerance_2.setChecked(True)
            
        if self.parent._sub_rects_finder[self.sub_rect_index].click is True:
            self.clickRadio_2.setChecked(True)
            self.pushButtonXYoffset_2.setEnabled(True)
            self.clicknumber_spinbox_2.setEnabled(True)
            self.labelClickNumber_2.setEnabled(True)
            
            if self.parent._sub_rects_finder[self.sub_rect_index].number_of_clicks > 1:
                self.labelClickDelay_2.setEnabled(True)
                self.clickdelay_spinbox_2.setEnabled(True)
            else:
                self.labelClickDelay_2.setEnabled(False)
                self.clickdelay_spinbox_2.setEnabled(False)
            
        else:
            self.clickRadio_2.setChecked(False)
            self.pushButtonXYoffset_2.setEnabled(False)
            self.clicknumber_spinbox_2.setEnabled(False)
            self.clickdelay_spinbox_2.setEnabled(False)
            self.labelClickNumber_2.setEnabled(False)
            self.labelClickDelay_2.setEnabled(False)
            
        self.clicknumber_spinbox_2.setValue(self.parent._sub_rects_finder[self.sub_rect_index].number_of_clicks)
        self.clickdelay_spinbox_2.setValue(self.parent._sub_rects_finder[self.sub_rect_index].click_delay)
        
        self.spinBoxSendKeysDelay_2.setValue(self.parent._sub_rects_finder[self.sub_rect_index].sendkeys_delay)
        self.spinBoxSendKeysDuration_2.setValue(self.parent._sub_rects_finder[self.sub_rect_index].sendkeys_duration)
       
            
        """
        if self.parent._sub_rects_finder[self.sub_rect_index].doubleclick is True:
            self.doubleclickRadio_2.setChecked(True)
            self.pushButtonXYoffset_2.setEnabled(True)
        else:
            self.doubleclickRadio_2.setChecked(False)
        """
            
        if self.parent._sub_rects_finder[self.sub_rect_index].rightclick is True:
            self.rightclickRadio_2.setChecked(True)
            self.pushButtonXYoffset_2.setEnabled(True)
        else:
            self.rightclickRadio_2.setChecked(False)
            
        if self.parent._sub_rects_finder[self.sub_rect_index].mousemove is True:
            self.movemouseRadio_2.setChecked(True)
            self.pushButtonXYoffset_2.setEnabled(True)
        else:
            self.movemouseRadio_2.setChecked(False)
            
        if self.parent._sub_rects_finder[self.sub_rect_index].click is False \
            and self.parent._sub_rects_finder[self.sub_rect_index].rightclick is False \
            and self.parent._sub_rects_finder[self.sub_rect_index].hold_and_release is None \
            and self.parent._sub_rects_finder[self.sub_rect_index].mousemove is False:
            self.dontclickRadio_2.setChecked(True)
            self.pushButtonXYoffset_2.setEnabled(False)
        else:
            self.dontclickRadio_2.setChecked(False)
            
        if self.parent._sub_rects_finder[self.sub_rect_index].hold_and_release is not None:
            self.holdreleaseComboBox_2.setCurrentIndex(self.parent._sub_rects_finder[self.sub_rect_index].hold_and_release)
            self.holdreleaseRadio_2.setChecked(True)
            self.holdreleaseComboBox_2.setEnabled(True)
            self.pushButtonXYoffset_2.setEnabled(True)

            
            if self.parent._sub_rects_finder[self.sub_rect_index].hold_and_release == 0 or self.parent._sub_rects_finder[self.sub_rect_index].hold_and_release == 1:
                self.holdreleaseSpinBox_2.setEnabled(False)
                self.holdreleaseSpinBox_2.setValue(self.parent._sub_rects_finder[self.sub_rect_index].release_pixel)
            else: 
                self.holdreleaseSpinBox_2.setEnabled(True)
                self.holdreleaseSpinBox_2.setValue(self.parent._sub_rects_finder[self.sub_rect_index].release_pixel)
                
        else:
            self.holdreleaseRadio_2.setChecked(False)
            self.holdreleaseComboBox_2.setEnabled(False)
            self.holdreleaseSpinBox_2.setEnabled(False)
            
    def timeout_exception_event(self, event):
        if self.timeout_exception.isChecked() is True:
            self.parent.timeout_exception = True
        else:
            self.parent.timeout_exception = False
            
    def clickRadio_event(self, event):
        if event is False:
            self.parent._main_rect_finder.click = False
        else:
            self.parent._main_rect_finder.click = True
            self.pushButtonXYoffset.setEnabled(True)
            self.labelClickNumber.setEnabled(True)
            self.clicknumber_spinbox.setEnabled(True)
            
            if self.clicknumber_spinbox.value() > 1:
                self.labelClickDelay.setEnabled(True)
                self.clickdelay_spinbox.setEnabled(True)
            else:
                self.labelClickDelay.setEnabled(False)
                self.clickdelay_spinbox.setEnabled(False)
            
            self.holdreleaseComboBox.setEnabled(False)
            self.holdreleaseSpinBox.setEnabled(False)
            
        self.parent.update()
        
    def doubleclickRadio_event(self, event):
        if event is False:
            self.parent._main_rect_finder.doubleclick = False
        else:
            self.parent._main_rect_finder.doubleclick = True 
            self.pushButtonXYoffset.setEnabled(True)
            
        self.parent.update()
            
    def rightclickRadio_event(self, event):
        if event is False:
            self.parent._main_rect_finder.rightclick = False
        else:
            self.parent._main_rect_finder.rightclick = True 
            self.pushButtonXYoffset.setEnabled(True)
            self.labelClickNumber.setEnabled(False)
            self.clicknumber_spinbox.setEnabled(False)
            self.labelClickDelay.setEnabled(False)
            self.clickdelay_spinbox.setEnabled(False)
            self.holdreleaseComboBox.setEnabled(False)
            self.holdreleaseSpinBox.setEnabled(False)
            
        self.parent.update()
            
    def movemouseRadio_event(self, event):
        if event is False:
            self.parent._main_rect_finder.mousemove = False
        else:
            self.parent._main_rect_finder.mousemove = True 
            self.pushButtonXYoffset.setEnabled(True)
            self.labelClickNumber.setEnabled(False)
            self.clicknumber_spinbox.setEnabled(False)
            self.labelClickDelay.setEnabled(False)
            self.clickdelay_spinbox.setEnabled(False)
            self.holdreleaseComboBox.setEnabled(False)
            self.holdreleaseSpinBox.setEnabled(False)
            
        self.parent.update()
             
    def dontclickRadio_event(self, event):
        if event is True:
            self.parent._main_rect_finder.click = False
            self.parent._main_rect_finder.doubleclick = False
            self.parent._main_rect_finder.rightclick = False
            self.parent._main_rect_finder.mousemove = False
            self.parent._main_rect_finder.hold_and_release = None
            self.pushButtonXYoffset.setEnabled(False)
            self.labelClickNumber.setEnabled(False)
            self.clicknumber_spinbox.setEnabled(False)
            self.labelClickDelay.setEnabled(False)
            self.clickdelay_spinbox.setEnabled(False)
            self.holdreleaseComboBox.setEnabled(False)
            self.holdreleaseSpinBox.setEnabled(False)
            
        self.parent.update()
            
    def pushButtonXYoffset_event(self):
        if str(self.pushButtonXYoffset.text()) != "Reset\nPoint":
            self.parent.set_xy_offset = -1  #-1 for main, other int for sub index
            self.parent._main_rect_finder.show_min_max = False
            self.parent._main_rect_finder.show_tolerance = False
            self.pushButtonXYoffset.setText("Reset\nPoint")
            self.hide()
        else:
            self.parent._main_rect_finder.x_offset = None
            self.parent._main_rect_finder.y_offset = None
            self.pushButtonXYoffset.setText("Interaction\nPoint")
            self.parent.update()
        
    def holdreleaseRadio_event(self, event):  
        if event is False:
            self.parent._main_rect_finder.hold_and_release = None
        else:
            self.parent._main_rect_finder.click = False
            self.parent._main_rect_finder.doubleclick = False
            self.parent._main_rect_finder.mousemove = False 
            self.parent._main_rect_finder.rightclick = False
            self.pushButtonXYoffset.setEnabled(True)  
            self.labelClickNumber.setEnabled(False)
            self.clicknumber_spinbox.setEnabled(False)
            self.labelClickDelay.setEnabled(False)
            self.clickdelay_spinbox.setEnabled(False)
            self.holdreleaseComboBox.setEnabled(True)
            
            combo_index = self.holdreleaseComboBox.currentIndex()
            
            if combo_index == 0 or combo_index == 1:
                self.holdreleaseSpinBox.setEnabled(False)
            else: 
                self.holdreleaseSpinBox.setEnabled(True)
                
            self.parent._main_rect_finder.hold_and_release = combo_index
                
    def holdreleaseComboBox_event(self, event):
        if event == 0 or event == 1:
            self.holdreleaseSpinBox.setEnabled(False)
        else: 
            self.holdreleaseSpinBox.setEnabled(True)
            
        self.parent._main_rect_finder.hold_and_release = event
        
    def holdreleaseSpinBox_event(self, event):
        self.parent._main_rect_finder.release_pixel = self.holdreleaseSpinBox.value()
        
    def clickdelay_spinbox_change_event (self, event):
        self.parent._main_rect_finder.click_delay = self.clickdelay_spinbox.value()
        self.parent.build_code_array()
        
    def clicknumber_spinbox_change_event (self, event):
        self.parent._main_rect_finder.number_of_clicks = self.clicknumber_spinbox.value()
        
        if self.clicknumber_spinbox.value() > 1 and self.parent._main_rect_finder.click is True:
            self.labelClickDelay.setEnabled(True)
            self.clickdelay_spinbox.setEnabled(True)
        else:
            self.labelClickDelay.setEnabled(False)
            self.clickdelay_spinbox.setEnabled(False)
        
        self.parent.build_code_array()
            
    @pyqtSlot(QString)
    def inserttext_event(self, text):
        if self.inserttext.text() == "Type text strings and shortcuts": #or self.inserttext.text() == "#k.send('Type here the key')":
            self.parent._main_rect_finder.sendkeys = "".encode('utf-8')
        else:
            self.parent._main_rect_finder.sendkeys = str(text.toUtf8()) #str(self.inserttext.text().toUtf8())
            
    def sendKeysDelay_spinbox_change_event(self, event):
        self.parent._main_rect_finder.sendkeys_delay = self.spinBoxSendKeysDelay.value()
        
    def sendKeysDuration_spinbox_change_event(self, event):
        self.parent._main_rect_finder.sendkeys_duration = self.spinBoxSendKeysDuration.value()
        
    @pyqtSlot(QString)
    def namelineedit_event(self, text):
        if text == "Type the keyword name":
            self.parent.object_name = "".encode('utf-8')
        else:
            self.parent.object_name = str(text.toUtf8()).replace(" ", "_")
    
    def text_encrypted_event(self, event):
        if self.text_encrypted.isChecked() is True:
            self.parent._main_rect_finder.text_encrypted = True
        else:
            self.parent._main_rect_finder.text_encrypted = False
    
    def add_quotes_event(self, event):
        if self.add_quotes.isChecked() is True:
            self.parent._main_rect_finder.sendkeys_quotes = True
        else:
            self.parent._main_rect_finder.sendkeys_quotes = False
        
    def eventFilter(self, obj, event):

        if event.type() == event.MouseButtonPress:
        
            if self.namelineedit.text() == "Type the keyword name" and obj.objectName() == "namelineedit":
                self.namelineedit.setText("")
                return True
        
            if self.inserttext.text() == "Type text strings and shortcuts" and obj.objectName() == "inserttext":
                self.inserttext.setText("")
                return True
                    
            if self.inserttext_2.text() == "Type text strings and shortcuts" and obj.objectName() == "inserttext_2":
                self.inserttext_2.setText("")
                return True
                
        if event.type()== event.FocusOut:

            if obj.objectName() == "roi_y_spinbox":

                absolute_sub_roi_y = self.parent._main_rect_finder.y + self.parent._sub_rects_finder[self.sub_rect_index].roi_y
                absolute_sub_rect_y = self.parent._sub_rects_finder[self.sub_rect_index].y
        
                if absolute_sub_roi_y > absolute_sub_rect_y:
                    self.parent._sub_rects_finder[self.sub_rect_index].roi_y = self.parent._sub_rects_finder[self.sub_rect_index].y - self.parent._main_rect_finder.y
                    self.roi_y_spinbox.setValue(self.parent._sub_rects_finder[self.sub_rect_index].roi_y)
                    self.parent.update()
                    return True
                    
                if absolute_sub_roi_y + self.parent._sub_rects_finder[self.sub_rect_index].roi_height < absolute_sub_rect_y + self.parent._sub_rects_finder[self.sub_rect_index].height:
                    self.parent._sub_rects_finder[self.sub_rect_index].roi_y = self.parent._sub_rects_finder[self.sub_rect_index].y - self.parent._main_rect_finder.y
                    self.roi_y_spinbox.setValue(self.parent._sub_rects_finder[self.sub_rect_index].roi_y)
                    self.parent.update()
                    return True
                    
            elif obj.objectName() == "roi_height_spinbox":
                
                absolute_sub_roi_y = self.parent._main_rect_finder.y + self.parent._sub_rects_finder[self.sub_rect_index].roi_y
                absolute_sub_rect_y = self.parent._sub_rects_finder[self.sub_rect_index].y
                if absolute_sub_roi_y + self.parent._sub_rects_finder[self.sub_rect_index].roi_height < absolute_sub_rect_y + self.parent._sub_rects_finder[self.sub_rect_index].height:
                    px_to_add = (absolute_sub_rect_y + self.parent._sub_rects_finder[self.sub_rect_index].height) - (absolute_sub_roi_y + self.parent._sub_rects_finder[self.sub_rect_index].roi_height)
                    height = absolute_sub_roi_y - px_to_add
                    self.parent._sub_rects_finder[self.sub_rect_index].roi_height = self.parent._sub_rects_finder[self.sub_rect_index].roi_height  + px_to_add
                    self.roi_height_spinbox.setValue(self.parent._sub_rects_finder[self.sub_rect_index].roi_height)
                    self.parent.update()
                    return True
                    
            elif obj.objectName() == "roi_x_spinbox":

                absolute_sub_roi_x = self.parent._main_rect_finder.x + self.parent._sub_rects_finder[self.sub_rect_index].roi_x
                absolute_sub_rect_x = self.parent._sub_rects_finder[self.sub_rect_index].x
        
                if absolute_sub_roi_x > absolute_sub_rect_x:
                    self.parent._sub_rects_finder[self.sub_rect_index].roi_x = self.parent._sub_rects_finder[self.sub_rect_index].x - self.parent._main_rect_finder.x
                    self.roi_x_spinbox.setValue(self.parent._sub_rects_finder[self.sub_rect_index].roi_x)
                    self.parent.update()
                    return True
                    
                if absolute_sub_roi_x + self.parent._sub_rects_finder[self.sub_rect_index].roi_width < absolute_sub_rect_x + self.parent._sub_rects_finder[self.sub_rect_index].width:
                    self.parent._sub_rects_finder[self.sub_rect_index].roi_x = self.parent._sub_rects_finder[self.sub_rect_index].x - self.parent._main_rect_finder.x
                    self.roi_x_spinbox.setValue(self.parent._sub_rects_finder[self.sub_rect_index].roi_x)
                    self.parent.update()
                    return True
                    
            elif obj.objectName() == "roi_width_spinbox":
                
                absolute_sub_roi_x = self.parent._main_rect_finder.x + self.parent._sub_rects_finder[self.sub_rect_index].roi_x
                absolute_sub_rect_x = self.parent._sub_rects_finder[self.sub_rect_index].x
                if absolute_sub_roi_x + self.parent._sub_rects_finder[self.sub_rect_index].roi_width < absolute_sub_rect_x + self.parent._sub_rects_finder[self.sub_rect_index].width:
                    px_to_add = (absolute_sub_rect_x + self.parent._sub_rects_finder[self.sub_rect_index].width) - (absolute_sub_roi_x + self.parent._sub_rects_finder[self.sub_rect_index].roi_width)
                    height = absolute_sub_roi_x - px_to_add
                    self.parent._sub_rects_finder[self.sub_rect_index].roi_width = self.parent._sub_rects_finder[self.sub_rect_index].roi_width  + px_to_add
                    self.roi_width_spinbox.setValue(self.parent._sub_rects_finder[self.sub_rect_index].roi_width)
                    self.parent.update()
                    return True
            elif self.namelineedit.text() == "" and obj.objectName() == "namelineedit":
                self.namelineedit.setText("Type the keyword name")
                return True
            elif obj.objectName() == "namelineedit":
                self.namelineedit.setText(self.parent.object_name)
                return True
        
            if self.inserttext.text() == "" and obj.objectName() == "inserttext":
                self.inserttext.setText("Type text strings and shortcuts")
                return True
                
            if self.inserttext_2.text() == "" and obj.objectName() == "inserttext_2":
                self.inserttext_2.setText("Type text strings and shortcuts")
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
                #print str(index) + ":" + str(end_line)
                self.listWidgetBlocks.addItem(item)
                
                self.parent._code_blocks.append((index, str(self.textEditCustomLines.toPlainText().toUtf8()), end_line))
                #print self.parent._code_blocks
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

    @pyqtSlot(QString)
    def inserttext_event_2(self, text):
        if self.inserttext_2.text() == "Type text strings and shortcuts": # or self.inserttext_2.text() == "#k.send('Type here the key')":
            self.parent._sub_rects_finder[self.sub_rect_index].sendkeys = "".encode('utf-8')
        else:
            self.parent._sub_rects_finder[self.sub_rect_index].sendkeys = str(text.toUtf8())
            
    def sendKeysDelay_spinbox_change_event_2(self, event):
        self.parent._sub_rects_finder[self.sub_rect_index].sendkeys_delay = self.spinBoxSendKeysDelay_2.value()
        
    def sendKeysDuration_spinbox_change_event_2(self, event):
        self.parent._sub_rects_finder[self.sub_rect_index].sendkeys_duration = self.spinBoxSendKeysDuration_2.value()

    def text_encrypted_event_2(self, event):
        if self.text_encrypted_2.isChecked() is True:
            self.parent._sub_rects_finder[self.sub_rect_index].text_encrypted = True
        else:
            self.parent._sub_rects_finder[self.sub_rect_index].text_encrypted = False
    
    def add_quotes_event_2(self, event):
        if self.add_quotes_2.isChecked() is True:
            self.parent._sub_rects_finder[self.sub_rect_index].sendkeys_quotes = True
        else:
            self.parent._sub_rects_finder[self.sub_rect_index].sendkeys_quotes = False
            
    def min_width_spinbox_change_event_2(self, event):
        self.parent._sub_rects_finder[self.sub_rect_index].min_width = self.min_width_spinbox_2.value()
        
        #print "min w", self.parent._sub_rects_finder[self.sub_rect_index].min_width, "max w", self.max_width_spinbox_2.value()
        
        if self.parent._sub_rects_finder[self.sub_rect_index].min_width > self.parent._sub_rects_finder[self.sub_rect_index].max_width:
            self.parent._sub_rects_finder[self.sub_rect_index].max_width = self.parent._sub_rects_finder[self.sub_rect_index].min_width
            self.max_width_spinbox_2.setValue(self.parent._sub_rects_finder[self.sub_rect_index].min_width)
        
        self.parent.update()
        
    def max_width_spinbox_change_event_2(self, event):
            
        self.parent._sub_rects_finder[self.sub_rect_index].max_width = self.max_width_spinbox_2.value()
        
        if self.parent._sub_rects_finder[self.sub_rect_index].min_width > self.parent._sub_rects_finder[self.sub_rect_index].max_width:
            self.parent._sub_rects_finder[self.sub_rect_index].min_width = self.parent._sub_rects_finder[self.sub_rect_index].max_width
            self.min_width_spinbox_2.setValue(self.parent._sub_rects_finder[self.sub_rect_index].max_width)
        
        self.parent.update()
        
    def min_height_spinbox_change_event_2(self, event):
        self.parent._sub_rects_finder[self.sub_rect_index].min_height = self.min_height_spinbox_2.value()
        
        if self.parent._sub_rects_finder[self.sub_rect_index].min_height > self.parent._sub_rects_finder[self.sub_rect_index].max_height:
            self.parent._sub_rects_finder[self.sub_rect_index].max_height = self.parent._sub_rects_finder[self.sub_rect_index].min_height
            self.max_height_spinbox_2.setValue(self.parent._sub_rects_finder[self.sub_rect_index].min_height)
        
        self.parent.update()
        
    def max_height_spinbox_change_event_2(self, event):
        self.parent._sub_rects_finder[self.sub_rect_index].max_height = self.max_height_spinbox_2.value()
        
        if self.parent._sub_rects_finder[self.sub_rect_index].min_height > self.parent._sub_rects_finder[self.sub_rect_index].max_height:
            self.parent._sub_rects_finder[self.sub_rect_index].min_height = self.parent._sub_rects_finder[self.sub_rect_index].max_height
            self.min_height_spinbox_2.setValue(self.parent._sub_rects_finder[self.sub_rect_index].max_height)
        
        self.parent.update()
        
    def show_min_max_event_2(self, event):
        if self.show_min_max_2.isChecked() is True:
            self.parent._sub_rects_finder[self.sub_rect_index].show_min_max = True
            self.show_tolerance_2.setChecked(False)
        else:
            self.parent._sub_rects_finder[self.sub_rect_index].show_min_max  = False
        self.parent.update()
        
    def show_tolerance_event_2(self, event):
        if self.show_tolerance_2.isChecked() is True:
            self.parent._sub_rects_finder[self.sub_rect_index].show_tolerance = True
            self.show_min_max_2.setChecked(False)
        else:
            self.parent._sub_rects_finder[self.sub_rect_index].show_tolerance = False
        self.parent.update()
        
    def height_tolerance_spinbox_event_2(self, event):
        self.parent._sub_rects_finder[self.sub_rect_index].height_tolerance = self.height_tolerance_spinbox_2.value()
        self.parent.update()
        
    def width_tolerance_spinbox_event_2(self, event):
        self.parent._sub_rects_finder[self.sub_rect_index].width_tolerance = self.width_tolerance_spinbox_2.value()
        self.parent.update()
        
    def use_tolerance_event_2(self, event):
        pass   
            
    def roi_x_spinbox_event(self, event):  
        self.parent._sub_rects_finder[self.sub_rect_index].roi_x = self.roi_x_spinbox.value()
        self.parent.update()
        
    def roi_y_spinbox_event(self, event):
        self.parent._sub_rects_finder[self.sub_rect_index].roi_y = self.roi_y_spinbox.value()
        self.parent.update()
        
    def roi_width_spinbox_event(self, event):
        self.parent._sub_rects_finder[self.sub_rect_index].roi_width = self.roi_width_spinbox.value()
        self.parent.update()
        
    def roi_height_spinbox_event(self, event):
        self.parent._sub_rects_finder[self.sub_rect_index].roi_height = self.roi_height_spinbox.value()
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
            
            if self.show_min_max_2.isChecked() is True:
                self.show_min_max_2.setChecked(False)
                self.show_tolerance_2.setChecked(True)
            
            self.parent._sub_rects_finder[self.sub_rect_index].use_min_max = False
            self.parent._sub_rects_finder[self.sub_rect_index].use_tolerance = True
            
            
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
            
            if self.show_tolerance_2.isChecked() is True:
                self.show_tolerance_2.setChecked(False)
                self.show_min_max_2.setChecked(True)
            
            self.parent._sub_rects_finder[self.sub_rect_index].use_min_max = True
            self.parent._sub_rects_finder[self.sub_rect_index].use_tolerance = False
            
    def clickRadio_event_2(self, event):
        if event is False:
            self.parent._sub_rects_finder[self.sub_rect_index].click = False
        else:
            self.parent._sub_rects_finder[self.sub_rect_index].click = True
            self.pushButtonXYoffset_2.setEnabled(True)
            self.labelClickNumber_2.setEnabled(True)
            self.clicknumber_spinbox_2.setEnabled(True)
            if self.clicknumber_spinbox_2.value() > 1: #and self.parent._sub_rects_finder[self.sub_rect_index].click is True:
                self.labelClickDelay_2.setEnabled(True)
                self.clickdelay_spinbox_2.setEnabled(True)
            else:
                self.labelClickDelay_2.setEnabled(False)
                self.clickdelay_spinbox_2.setEnabled(False)
            self.holdreleaseComboBox_2.setEnabled(False)
            self.holdreleaseSpinBox_2.setEnabled(False)
            
        self.parent.update()
        
    def doubleclickRadio_event_2(self, event):
        if event is False:
            self.parent._sub_rects_finder[self.sub_rect_index].doubleclick = False
        else:
            self.parent._sub_rects_finder[self.sub_rect_index].doubleclick = True 
            self.pushButtonXYoffset_2.setEnabled(True)
            
        self.parent.update()
            
    def movemouseRadio_event_2(self, event):
        if event is False:
            self.parent._sub_rects_finder[self.sub_rect_index].mousemove = False
        else:
            self.parent._sub_rects_finder[self.sub_rect_index].mousemove = True 
            self.pushButtonXYoffset_2.setEnabled(True)
            self.labelClickNumber_2.setEnabled(False)
            self.clicknumber_spinbox_2.setEnabled(False)
            self.labelClickDelay_2.setEnabled(False)
            self.clickdelay_spinbox_2.setEnabled(False)
            self.holdreleaseComboBox_2.setEnabled(False)
            self.holdreleaseSpinBox_2.setEnabled(False)
            
        self.parent.update()
            
    def rightclickRadio_event_2(self, event):
        if event is False:
            self.parent._sub_rects_finder[self.sub_rect_index].rightclick = False
        else:
            self.parent._sub_rects_finder[self.sub_rect_index].rightclick = True 
            self.pushButtonXYoffset_2.setEnabled(True)
            self.labelClickNumber_2.setEnabled(False)
            self.clicknumber_spinbox_2.setEnabled(False)
            self.labelClickDelay_2.setEnabled(False)
            self.clickdelay_spinbox_2.setEnabled(False)
            self.holdreleaseComboBox_2.setEnabled(False)
            self.holdreleaseSpinBox_2.setEnabled(False)
            
        self.parent.update()
             
    def dontclickRadio_event_2(self, event):
        if event is True:
            self.parent._sub_rects_finder[self.sub_rect_index].click = False
            self.parent._sub_rects_finder[self.sub_rect_index].doubleclick = False
            self.parent._sub_rects_finder[self.sub_rect_index].rightclick = False
            self.parent._sub_rects_finder[self.sub_rect_index].mousemove = False
            self.pushButtonXYoffset_2.setEnabled(False)
            self.labelClickNumber_2.setEnabled(False)
            self.clicknumber_spinbox_2.setEnabled(False)
            self.labelClickDelay_2.setEnabled(False)
            self.clickdelay_spinbox_2.setEnabled(False)
            self.holdreleaseComboBox_2.setEnabled(False)
            self.holdreleaseSpinBox_2.setEnabled(False)
            
        self.parent.update()
            
    def pushButtonXYoffset_event_2(self):

        if str(self.pushButtonXYoffset_2.text()) != "Reset\nPoint":
            self.parent.set_xy_offset = self.sub_rect_index  #-1 for main, other int for sub index
            self.parent._sub_rects_finder[self.sub_rect_index].show_min_max = False
            self.parent._sub_rects_finder[self.sub_rect_index].show_tolerance = False
            self.hide()
        else:
            self.parent._sub_rects_finder[self.sub_rect_index].x_offset = None
            self.parent._sub_rects_finder[self.sub_rect_index].y_offset = None
            self.pushButtonXYoffset_2.setText("Interaction\nPoint")
            self.parent.update()
        
    def holdreleaseRadio_event_2(self, event):  
        if event is False:
            self.parent._sub_rects_finder[self.sub_rect_index].hold_and_release = None
        else:
            self.parent._sub_rects_finder[self.sub_rect_index].click = False
            self.parent._sub_rects_finder[self.sub_rect_index].doubleclick = False
            self.parent._sub_rects_finder[self.sub_rect_index].mousemove = False 
            self.parent._sub_rects_finder[self.sub_rect_index].rightclick = False
            self.pushButtonXYoffset_2.setEnabled(True)  
            self.labelClickNumber_2.setEnabled(False)
            self.clicknumber_spinbox_2.setEnabled(False)
            self.labelClickDelay_2.setEnabled(False)
            self.clickdelay_spinbox_2.setEnabled(False)
            self.holdreleaseComboBox_2.setEnabled(True)
            
            combo_index = self.holdreleaseComboBox_2.currentIndex()
            
            if combo_index == 0 or combo_index == 1:
                self.holdreleaseSpinBox_2.setEnabled(False)
            else: 
                self.holdreleaseSpinBox_2.setEnabled(True)
            
            self.parent._sub_rects_finder[self.sub_rect_index].hold_and_release = combo_index
            
    def holdreleaseComboBox_event_2(self, event):
        if event == 0 or event == 1:
            self.holdreleaseSpinBox_2.setEnabled(False)
        else: 
            self.holdreleaseSpinBox_2.setEnabled(True)
            
        self.parent._sub_rects_finder[self.sub_rect_index].hold_and_release = event
        
    def holdreleaseSpinBox_event_2(self, event):
        self.parent._sub_rects_finder[self.sub_rect_index].release_pixel = self.holdreleaseSpinBox_2.value()
        
    def clickdelay_spinbox_change_event_2 (self, event):
        self.parent._sub_rects_finder[self.sub_rect_index].click_delay = self.clickdelay_spinbox_2.value()
        self.parent.build_code_array()
        
    def clicknumber_spinbox_change_event_2 (self, event):
        self.parent._sub_rects_finder[self.sub_rect_index].number_of_clicks = self.clicknumber_spinbox_2.value()
        
        if self.clicknumber_spinbox_2.value() > 1 and self.parent._sub_rects_finder[self.sub_rect_index].click is True:
            self.labelClickDelay_2.setEnabled(True)
            self.clickdelay_spinbox_2.setEnabled(True)
        else:
            self.labelClickDelay_2.setEnabled(False)
            self.clickdelay_spinbox_2.setEnabled(False)
            
        self.parent.build_code_array()
        
    def closeEvent(self, event):
            
        self.parent.parent.show()
        self.parent.close()

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