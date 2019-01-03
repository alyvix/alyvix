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
import re

import numpy as np

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
from contouring import Contouring

import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET

from distutils.sysconfig import get_python_lib


class AlyvixTextFinderView(QWidget):

    def __init__(self, parent):
        QWidget.__init__(self)
        #self.setupUi(self)
        
        self._last_pos = None
        
        self.ignore_release = False
        
        self._ctrl_is_pressed = False
        
        self._dont_build_rect = False
        
        self._space_toggle = False
        
        self._imageBoxes = []
        self._textBoxes = []
        self._rectBoxes = []
        self._boundingRects = []
        self._show_boundingrects = False
        
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
        self.scraper = False
        
        self.parent_is_objfinder = False
        
        self.mouse_or_key_is_set = False
        
        self.setMouseTracking(True)
        
        self._bg_pixmap = QPixmap()
        self.__capturing = False
        
        self.__drag_border = False
        
        
        self.__click_position = QPoint(0,0)
        
        self._main_text = None
        
        self._sub_texts_finder = []
        
        self.__deleted_texts = []
        
        self.last_view_index = 0
        
        #flags
        #self.__flag_mouse_left_button_is_pressed = False
        
        self.__flag_mouse_is_inside_rect = None
        
        self.__move_index = None
        self.__flag_moving_rect = False
        self.__position_offset_x = 0
        self.__position_offset_y = 0
        
        self.__flag_capturing_main_text_rect_roi = True
        self.__flag_capturing_main_text_rect = False
        self.__flag_capturing_sub_text_rect_roi = False
        self.__flag_capturing_sub_text = False
        
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
        
        self.set_xy_offset = None  #-1 for main, other int for sub index
        self.last_xy_offset_index = None
        self.__flag_need_to_delete_main_roi = False
        self.__flag_need_to_restore_main_roi = False
        self.__flag_need_to_restore_main_text_rect = False
        self.__flag_need_to_delete_roi = False
        self.__flag_need_to_restore_roi = False
        self._flag_show_min_max = False
        self._self_show_tolerance = False

        self.__index_deleted_rect_inside_roi = -1
        self.__restored_rect_roi = False
        
        
        self._old_width_rect = 0
        self._old_height_rect = 0
        self._old_x_rect = 0
        self._old_y_rect = 0
        self._old_roi_width_rect = 0
        self._old_roi_height_rect = 0
        self._old_roi_x_rect = 0
        self._old_roi_y_rect = 0
    
        self.parent = parent
        self.scaling_factor = self.parent.scaling_factor

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
        
        if self.parent.build_objects is True:
            self.build_objects()
        self.old_mouse_or_key_is_set = self.mouse_or_key_is_set
        self.__old_code_v220 = self.get_old_code_v220()
        self.__old_code_v230 = self.get_old_code_v230()
        self.__old_code_v250 = self.get_old_code_v250()
        self.__old_code = self.get_old_code()
        self.mouse_or_key_is_set = self.old_mouse_or_key_is_set
        #print self.__old_code
        
        self._old_main_text = copy.deepcopy(self._main_text)
        self._old_sub_text = copy.deepcopy(self._sub_texts_finder)
        
        self.esc_pressed = False
        self.ok_pressed = False
        
        self._is_saving = False
        
    def set_bg_pixmap(self, image):
        self._bg_pixmap = QPixmap.fromImage(image)

        scaling_factor = self.scaling_factor

        #original = cv2.imread(self.parent.path + os.sep + self.parent.xml_name.replace("xml", "png"))
        
        if not os.path.exists(self._path):
            os.makedirs(self._path)
            
        image_name = self._path + os.sep + time.strftime("image_finder_%d_%m_%y_%H_%M_%S_temp_img.png")
        self._bg_pixmap.save(image_name,"PNG", -1)
        time.sleep(0.05)
        #original = cv2.imread(image_name)
                #print cv_image
        #time.sleep(0.1)

        #print scaling_factor
        
        contouring_manager = Contouring(
            canny_threshold1=250*0.2,
            canny_threshold2=250*0.3,
            canny_apertureSize=3,
            hough_threshold=10,
            hough_minLineLength=30,
            hough_maxLineGap=1,
            line_angle_tolerance=0,
            ellipse_width=2,
            ellipse_height=2,
            text_roi_emptiness=0.45,
            text_roi_proportion=1.3,
            image_roi_emptiness=0.1,
            vline_hw_proportion=2,
            vline_w_maxsize=10,
            hline_wh_proportion=2,
            hline_h_maxsize=10,
            rect_w_minsize=5,
            rect_h_minsize=5,
            rect_w_maxsize_01=800,
            rect_h_maxsize_01=100,
            rect_w_maxsize_02=100,
            rect_h_maxsize_02=800,
            rect_hw_proportion=2,
            rect_hw_w_maxsize=10,
            rect_wh_proportion=2,
            rect_wh_h_maxsize=10,
            hrect_proximity=10,
            vrect_proximity=10,
            vrect_others_proximity=40,
            hrect_others_proximity=80)
        # numpy_matrix = contouring.auto_contouring('lena.png')
        numpy_matrix = contouring_manager.auto_contouring(image_name, scaling_factor=self.scaling_factor)
        os.remove(image_name)
        
        #self._rectBoxes = contouring_manager.getRectBoxes(scaling_factor=self.scaling_factor)
        #self._imageBoxes = contouring_manager.getImageBoxes(scaling_factor=self.scaling_factor)
        self._textBoxes = contouring_manager.getTextBoxes(scaling_factor=self.scaling_factor)
           
           
        self._boundingRects.extend(self._textBoxes)
        #self._boundingRects.extend(self._imageBoxes)
        #self._boundingRects.extend(self._rectBoxes)
        
    def save_all(self):
    
        if self._main_text != None and self.ok_pressed is False:
        
            extra_path = get_python_lib() + os.sep + "alyvix" + os.sep + "robotproxy" + os.sep + self._path.split(os.sep)[-1] + "_extra" + os.sep + self.object_name
            #print "AAAAAAAAAAAAAAAAAAAAAAA:", template_image_path
            
            if not os.path.exists(extra_path):
                os.makedirs(extra_path)
        
            #scraper_file_name = self._path + os.sep + self.object_name + "_TextFinder.alyscraper"
            scraper_file_name = extra_path + os.sep + "scraper.txt"
            
            if self.scraper is True:
                self._sub_texts_finder = []
                
                self._main_text.text = ""
                self._main_text.quotes_ocr = True
                self._main_text.sendkeys_quotes = True
                self._main_text.sendkeys = ""
                self._main_text.text_encrypted = False

                if not os.path.exists(scraper_file_name):
                    with open(scraper_file_name, 'w') as f:
                        
                        f.write("scraper=true")

                        f.close()
            else:
            
                if os.path.exists(scraper_file_name):
                    os.remove(scraper_file_name)
                    
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
                
            self.parent.update_list()
                
        try:
            if self.parent.parent.is_object_finder_menu:
            
                sel_index = self.parent.parent.last_selected_index
                
                obj_main_redraw = False
                obj_sub_redraw = False
                
                #print self.parent.parent.last_selected_index
                
                old_main_pos = None
            
                if sel_index == 0:
                    if self.parent.parent._main_object_finder.x != self._main_text.x or self.parent.parent._main_object_finder.y != self._main_text.y or \
                    self.parent.parent._main_object_finder.height != self._main_text.height or \
                    self.parent.parent._main_object_finder.width != self._main_text.width or \
                    self.parent.parent._main_object_finder.roi_width != self._main_text.roi_width or \
                    self.parent.parent._main_object_finder.roi_height != self._main_text.roi_height or \
                    self.parent.parent._main_object_finder.roi_x != self._main_text.roi_x + self._main_object_finder.x or \
                    self.parent.parent._main_object_finder.roi_y != self._main_text.roi_y + self._main_object_finder.y or \
                    self.parent.parent._main_object_finder.roi_unlimited_up != self._main_text.roi_unlimited_up or \
                    self.parent.parent._main_object_finder.roi_unlimited_down != self._main_text.roi_unlimited_down or \
                    self.parent.parent._main_object_finder.roi_unlimited_left != self._main_text.roi_unlimited_left or \
                    self.parent.parent._main_object_finder.roi_unlimited_right != self._main_text.roi_unlimited_right:
                        obj_main_redraw = True
                        old_main_pos = (self.parent.parent._main_object_finder.x, self.parent.parent._main_object_finder.y)
                        self.parent.parent._main_object_finder.x = self._main_text.x
                        self.parent.parent._main_object_finder.y = self._main_text.y
                        self.parent.parent._main_object_finder.height = self._main_text.height
                        self.parent.parent._main_object_finder.width = self._main_text.width
                        self.parent.parent._main_object_finder.roi_unlimited_up = self._main_text.roi_unlimited_up
                        self.parent.parent._main_object_finder.roi_unlimited_down = self._main_text.roi_unlimited_down 
                        self.parent.parent._main_object_finder.roi_unlimited_left = self._main_text.roi_unlimited_left
                        self.parent.parent._main_object_finder.roi_unlimited_right = self._main_text.roi_unlimited_right
                else:
                
                    #print self.parent.parent._sub_objects_finder[sel_index-1].x, self.parent.parent._sub_objects_finder[sel_index-1].y, self.parent.parent._sub_objects_finder[sel_index-1].height, self.parent.parent._sub_objects_finder[sel_index-1].width 
                    
                    #print self._main_text.x, self._main_text.y, self._main_text.height, self._main_text.width
                    #print self.parent.parent._sub_objects_finder[sel_index-1].roi_x
                
                    if self.parent.parent._sub_objects_finder[sel_index-1].x != self._main_text.x or self.parent.parent._sub_objects_finder[sel_index-1].y != self._main_text.y or \
                        self.parent.parent._sub_objects_finder[sel_index-1].height != self._main_text.height or \
                        self.parent.parent._sub_objects_finder[sel_index-1].width != self._main_text.width or \
                        self.parent.parent._sub_objects_finder[sel_index-1].roi_width != self._main_text.roi_width or \
                        self.parent.parent._sub_objects_finder[sel_index-1].roi_height != self._main_text.roi_height or \
                        self.parent.parent._sub_objects_finder[sel_index-1].roi_x != self._main_text.roi_x + self._main_object_finder.x or \
                        self.parent.parent._sub_objects_finder[sel_index-1].roi_y != self._main_text.roi_y + self._main_object_finder.y or \
                        self.parent.parent._sub_objects_finder[sel_index-1].roi_unlimited_up != self._main_text.roi_unlimited_up or \
                        self.parent.parent._sub_objects_finder[sel_index-1].roi_unlimited_down != self._main_text.roi_unlimited_down or \
                        self.parent.parent._sub_objects_finder[sel_index-1].roi_unlimited_left != self._main_text.roi_unlimited_left or \
                        self.parent.parent._sub_objects_finder[sel_index-1].roi_unlimited_right != self._main_text.roi_unlimited_right:
                        
                        #print "different"
                        
                        obj_sub_redraw = True
                        self.parent.parent._sub_objects_finder[sel_index-1].x = self._main_text.x
                        self.parent.parent._sub_objects_finder[sel_index-1].y = self._main_text.y
                        self.parent.parent._sub_objects_finder[sel_index-1].height = self._main_text.height
                        self.parent.parent._sub_objects_finder[sel_index-1].width = self._main_text.width
                        

                        
                        self.parent.parent._sub_objects_finder[sel_index-1].roi_x = self._main_text.roi_x - self.parent.parent._main_object_finder.x
                        self.parent.parent._sub_objects_finder[sel_index-1].roi_y = self._main_text.roi_y - self.parent.parent._main_object_finder.y
                        self.parent.parent._sub_objects_finder[sel_index-1].roi_height = self._main_text.roi_height
                        self.parent.parent._sub_objects_finder[sel_index-1].roi_width = self._main_text.roi_width
                        
                        self.parent.parent._sub_objects_finder[sel_index-1].roi_unlimited_up = self._main_text.roi_unlimited_up
                        self.parent.parent._sub_objects_finder[sel_index-1].roi_unlimited_down = self._main_text.roi_unlimited_down 
                        self.parent.parent._sub_objects_finder[sel_index-1].roi_unlimited_left = self._main_text.roi_unlimited_left
                        self.parent.parent._sub_objects_finder[sel_index-1].roi_unlimited_right = self._main_text.roi_unlimited_right
                        
                        """
                        self.parent.parent._sub_objects_finder[sel_index-1].roi_x =  (self.parent.parent._sub_objects_finder[sel_index-1].x - self.parent.parent._main_object_finder.x) - roi_width_half
                        self.parent.parent._sub_objects_finder[sel_index-1].roi_y =  (self.parent.parent._sub_objects_finder[sel_index-1].y - self.parent.parent._main_object_finder.y) - roi_height_half
                        self.parent.parent._sub_objects_finder[sel_index-1].roi_height = roi_height
                        self.parent.parent._sub_objects_finder[sel_index-1].roi_width = roi_width
                        """
                        
                        """
                        self.parent.parent._sub_objects_finder[sel_index-1].roi_x = 0
                        self.parent.parent._sub_objects_finder[sel_index-1].roi_y = 0
                        self.parent.parent._sub_objects_finder[sel_index-1].roi_height = 0
                        self.parent.parent._sub_objects_finder[sel_index-1].roi_width = 0
                        """
                        
                        self.parent.parent._sub_objects_finder[sel_index-1].roi_unlimited_up = self._main_text.roi_unlimited_up
                        self.parent.parent._sub_objects_finder[sel_index-1].roi_unlimited_down = self._main_text.roi_unlimited_down
                        self.parent.parent._sub_objects_finder[sel_index-1].roi_unlimited_left = self._main_text.roi_unlimited_left
                        self.parent.parent._sub_objects_finder[sel_index-1].roi_unlimited_right = self._main_text.roi_unlimited_right
                    
                        self.parent.parent.redraw_index_from_finder = sel_index-1
                
                try:
                    #self.parent.parent.pv.showFullScreen()
                    if obj_main_redraw is True:
                        self.parent.parent.reset_all_sub_roi(old_main_pos)
                        #self.parent.parent.pv = PaintingView(self.parent.parent)
                        #image = QImage(self.parent.parent._main_object_finder.xml_path.replace("xml", "png"))   
                        #self.parent.parent.pv.set_bg_pixmap(image)
                        #self.parent.parent._main_deleted = True
                        self.parent.parent.pv.update()
                    elif obj_sub_redraw is True:
                        self.parent.parent.sub_object_index = sel_index-1
                        
                        try:
                            self.parent.parent._old_main_object = copy.deepcopy(self.parent.parent._main_object_finder)
                            self.parent.parent._old_sub_objects = copy.deepcopy(self.parent.parent._sub_objects_finder)
                        except:
                            pass
                        #self.parent.parent.redraw_roi_event()
                        self.parent.parent.pv.update()
                    else:
                        #print self.parent.parent._sub_objects_finder[sel_index-1].roi_x
                
                        self.parent.parent.pv.update()
                        #print self.parent.parent._sub_objects_finder[sel_index-1].roi_x
                
                    sel_index = None
                except:
                    pass
            
                if self.mouse_or_key_is_set is True:
                    
                    self.parent.parent._main_object_finder.mouse_or_key_is_set = True
                    #print "build_objjjjjjjjjjjjjjjjjjjjj"
        except Exception, ex:
        
            print Exception, ex
            
        try:
            if self.parent.is_AlyvixMainMenuController is True:
                self.parent.set_last_name(str(self.object_name))
                self.parent.update_list()
        except:
            pass
        self.parent.show()
        self.close()
        
    def cancel_all(self):
        self._main_text = copy.deepcopy(self._old_main_text)
        self._sub_texts_finder = copy.deepcopy(self._old_sub_text)
        try:
            if self.parent.is_AlyvixMainMenuController is True:
                self.parent.update_list()
        except:
            pass
        self.parent.show()
        self.close()
        
    def keyPressEvent(self, event):
    
        if event.modifiers() == Qt.ControlModifier:
            self._ctrl_is_pressed = True
            self._dont_build_rect = True
            
    
        if event.key() == Qt.Key_Space and self.__flag_capturing_sub_text is False and self.__flag_capturing_main_text_rect is False and self.set_xy_offset is None and self._space_toggle is False:
            self._show_boundingrects = True
            self.ignore_release = True
            self._dont_build_rect = True
            self._space_toggle = True
            self.update()
            
        elif event.key() == Qt.Key_Space and self.__flag_capturing_sub_text is False and self.__flag_capturing_main_text_rect is False and self.set_xy_offset is None and self._space_toggle is True:
            self._show_boundingrects = False
            self.ignore_release = False
            self._dont_build_rect = False
            #self.ignore_release = False
            self._space_toggle = False
            self.update()
            
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Z: 
            if self.set_xy_offset is None and self._show_boundingrects is False:
                self.delete_rect()

        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Y:
            if self.set_xy_offset is None and self._show_boundingrects is False:
                self.restore_rect()
        if event.key() == Qt.Key_Escape:
            if len(self._sub_texts_finder) == 0 and self._main_text is None:
                try:
                    self.image_view_properties.close()
                except:
                    pass
                self.parent.show()
                self.close()
            else:
            
                if len(self._sub_texts_finder) > 0:
            
                    index = -1 #self.__index_deleted_rect_inside_roi
                    if  self._sub_texts_finder[index].x == 0 and self._sub_texts_finder[index].y == 0 \
                        and self._sub_texts_finder[index].width == 0 and self._sub_texts_finder[index].height == 0:
                     
                        del self._sub_texts_finder[-1]
                        self.__flag_need_to_delete_roi = False
                        self.__flag_need_to_restore_roi = True
                        self.__flag_capturing_sub_text_rect_roi = True
                        self.__flag_capturing_sub_text = False
                    
                elif self._main_text.x == 0 and self._main_text.y == 0 \
                        and self._main_text.width == 0 and self._main_text.height == 0:

                    self._main_text = None
                    self.__flag_need_to_delete_main_roi = False
                    self.__flag_need_to_restore_main_roi = True
                    self.__flag_capturing_main_text_rect_roi = True
                    self.__flag_capturing_sub_text_rect_roi = False
                    #self.__flag_need_to_restore_main_text_rect = False
                    
                #self.update()
                self.set_xy_offset = None
                                
                self._ctrl_is_pressed = False
            
            
                self._show_boundingrects = False
                self.ignore_release = False
                self._dont_build_rect = False
                #self.ignore_release = False
                self._space_toggle = False
                self.update()
                    
                if self._main_text is not None:

                    self.image_view_properties = AlyvixTextFinderPropertiesView(self)
                    self.image_view_properties.show()
            """
            if self._main_text is None and self.esc_pressed is False:
                self.esc_pressed = True
                try:
                    self.image_view_properties.close()
                except:
                    pass
                self.parent.show()
                self.close()
            elif self.set_xy_offset is not None:
                if self.set_xy_offset == -1:
                    self._main_text.x_offset = None
                    self._main_text.y_offset = None
                else:
                    self._sub_texts_finder[self.set_xy_offset].x_offset = None
                    self._sub_texts_finder[self.set_xy_offset].y_offset = None
                self.set_xy_offset = None
                self.last_xy_offset_index = None
                self.update()
                self.image_view_properties = AlyvixTextFinderPropertiesView(self)
                self.image_view_properties.show()
            """
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_O: #and self.set_xy_offset is None:
            if len(self._sub_texts_finder) == 0 and self._main_text is None:
                try:
                    self.image_view_properties.close()
                except:
                    pass
                self._ctrl_is_pressed = False
                self.parent.show()
                self.close()
            else:
            
                if len(self._sub_texts_finder) > 0:
            
                    index = -1 #self.__index_deleted_rect_inside_roi
                    if  self._sub_texts_finder[index].x == 0 and self._sub_texts_finder[index].y == 0 \
                        and self._sub_texts_finder[index].width == 0 and self._sub_texts_finder[index].height == 0:
                     
                        del self._sub_texts_finder[-1]
                        self.__flag_need_to_delete_roi = False
                        self.__flag_need_to_restore_roi = True
                        self.__flag_capturing_sub_text_rect_roi = True
                        self.__flag_capturing_sub_text = False
                    
                elif self._main_text.x == 0 and self._main_text.y == 0 \
                        and self._main_text.width == 0 and self._main_text.height == 0:

                    self._main_text = None
                    self.__flag_need_to_delete_main_roi = False
                    self.__flag_need_to_restore_main_roi = True
                    self.__flag_capturing_main_text_rect_roi = True
                    self.__flag_capturing_sub_text_rect_roi = False
                    #self.__flag_need_to_restore_main_text_rect = False
                    
                self.update()
                self.set_xy_offset = None
                self._ctrl_is_pressed = False

                self._show_boundingrects = False
                self.ignore_release = False
                self._dont_build_rect = False
                #self.ignore_release = False
                self._space_toggle = False
                self.update()
                
                if self._main_text is not None:
                    
                    self.image_view_properties = AlyvixTextFinderPropertiesView(self)
                    self.image_view_properties.show()
                    
        if event.key() == Qt.Key_Down:
        
            if self.__flag_capturing_sub_text == True:
                self._sub_texts_finder[-1].roi_unlimited_down = True
                self.update()
            elif self.__flag_capturing_main_text_rect == True:
                self._main_text.roi_unlimited_down = True
                self.update()
                
        if event.key() == Qt.Key_Up:
        
            if self.__flag_capturing_sub_text == True:
                self._sub_texts_finder[-1].roi_unlimited_up = True
                self.update()
            elif self.__flag_capturing_main_text_rect == True:
                self._main_text.roi_unlimited_up = True
                self.update()
                
        if event.key() == Qt.Key_Left:
        
            if self.__flag_capturing_sub_text == True:
                self._sub_texts_finder[-1].roi_unlimited_left = True
                self.update()
            elif self.__flag_capturing_main_text_rect == True:
                self._main_text.roi_unlimited_left = True
                self.update()
                
        if event.key() == Qt.Key_Right:
        
            if self.__flag_capturing_sub_text == True:
                self._sub_texts_finder[-1].roi_unlimited_right = True
                self.update()
            elif self.__flag_capturing_main_text_rect == True:
                self._main_text.roi_unlimited_right = True
                self.update()
                
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
    
    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Control:
            self._ctrl_is_pressed = False
            self.ignore_release = False
            self._dont_build_rect = False
            
        """
        if event.key() == Qt.Key_Space: 
            self._show_boundingrects = False
            self.ignore_release = False
            self._dont_build_rect = False
            #self.ignore_release = False
        """
        self.update()
    
    def closeEvent(self, event):
        self.close
        
    def mouseMoveEvent(self, event):
        self.update()
        
    def mouseDoubleClickEvent(self, event):
        if self._ctrl_is_pressed is True or self._show_boundingrects is True:
            event.ignore()
            return
            
        if self.is_mouse_inside_rect(self._main_text) and self.set_xy_offset is None:
        
            if len(self._sub_texts_finder) > 0:
        
                index = -1 #self.__index_deleted_rect_inside_roi
                if  self._sub_texts_finder[index].x == 0 and self._sub_texts_finder[index].y == 0 \
                    and self._sub_texts_finder[index].width == 0 and self._sub_texts_finder[index].height == 0:
                 
                    del self._sub_texts_finder[-1]
                    self.__flag_need_to_delete_roi = False
                    self.__flag_need_to_restore_roi = True
                    self.__flag_capturing_sub_text_rect_roi = True
                    self.__flag_capturing_sub_text = False
        
            self.image_view_properties = AlyvixTextFinderPropertiesView(self)
            self.image_view_properties.show()
        
    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
        
            if event.modifiers() == Qt.ControlModifier and self.set_xy_offset is None and self._show_boundingrects is False:
                self.ignore_release = True
            
                if self.__flag_mouse_is_inside_rect is not None and self.__flag_mouse_is_inside_rect == 0:
                    index = self.__flag_mouse_is_inside_rect -1
                    """
                    percentage_screen_w = int(0.1 * self._bg_pixmap.width())
                    percentage_screen_h = int(0.1 * self._bg_pixmap.height())
                    percentage_object_w = int(0.5 * self._main_text.width)
                    percentage_object_h = int(0.5 * self._main_text.height)
                    
                    roi_height = percentage_screen_h + percentage_object_h + self._main_text.height
                    
                    roi_width = percentage_screen_w + percentage_object_w + self._main_text.width
                    """
                    
                                        
                    #roi_height = int(15*self.scaling_factor) + self._main_text.height
                    
                    #roi_width = int(15*self.scaling_factor) + self._main_text.width
                    
                    #roi_width_half = int((roi_width - self._main_text.width)/2)
                    #roi_height_half = int((roi_height - self._main_text.height)/2)
                    
                    #self._main_text.roi_x =  (self._main_text.x) - roi_width_half
                    #self._main_text.roi_y =  (self._main_text.y) - roi_height_half
                    #self._main_text.roi_height = roi_height
                    #self._main_text.roi_width = roi_width
                    
                    """
                    self._main_text.roi_x =  (self._main_text.x) - int(1*self.scaling_factor)
                    self._main_text.roi_y =  (self._main_text.y) - int(1*self.scaling_factor)
                    self._main_text.roi_height = self._main_text.height + int(6*self.scaling_factor)
                    self._main_text.roi_width = self._main_text.width + int(6*self.scaling_factor)
                    """
                                                     
                    hw_factor = 0
                                        
                    if self._main_text.height < self._main_text.width:
                        hw_factor = self._main_text.height
                    else:
                        hw_factor = self._main_text.width
                        
                        
                    sc_factor = 0
                                        
                    if self._bg_pixmap.height() < self._bg_pixmap.width():
                        sc_factor = self._bg_pixmap.height()
                    else:
                        sc_factor = self._bg_pixmap.width()
                        
                    percentage_screen_w = int(0.0125 * sc_factor)
                    percentage_screen_h = int(0.0125 * sc_factor)
                    percentage_object_w = int(0.2 * hw_factor) #self._main_text.width)
                    percentage_object_h = int(0.2 * hw_factor) #self._main_text.height)
                    
                    roi_height = percentage_screen_h + percentage_object_h + self._main_text.height
                    
                    roi_width = percentage_screen_w + percentage_object_w + self._main_text.width
                    
                    
                    """
                    hw_factor = 0
                    
                    if self._main_text.height < self._main_text.width:
                        hw_factor = self._main_text.height
                    else:
                        hw_factor = self._main_text.width
                        
                    roi_height = int(0.95 * hw_factor) + self._main_text.height

                    roi_width = int(0.95 * hw_factor) + self._main_text.width
                    """


                    roi_width_half = int((roi_width - self._main_text.width)/2)

                    roi_height_half = int((roi_height - self._main_text.height)/2)


                    self._main_text.roi_x =  self._main_text.x - roi_width_half
                    self._main_text.roi_y =  self._main_text.y - roi_height_half
                    self._main_text.roi_height = roi_height
                    self._main_text.roi_width = roi_width
                    
                    """
                    roi_height = int(0.30*hw_factor*self.scaling_factor) + self._main_text.height #int(10*self.scaling_factor) + self._main_text.height

                    roi_width = int(0.30*hw_factor*self.scaling_factor) + self._main_text.width #int(10*self.scaling_factor) + self._main_text.width


                    roi_width_half = int((roi_width - self._main_text.width)/2)
                    roi_height_half = int((roi_height - self._main_text.height)/2)

                    self._main_text.roi_x =  self._main_text.x - roi_width_half
                    self._main_text.roi_y =  self._main_text.y - roi_height_half
                    self._main_text.roi_height = roi_height
                    self._main_text.roi_width = roi_width
                    """
                    
                    if self._main_text.roi_y < 0:
                    
                        under_zero = abs(self._main_text.roi_y)
                        self._main_text.roi_y = self._main_text.roi_y + under_zero
                        self._main_text.roi_height = self._main_text.roi_height - under_zero
                        
                    
                    if self._main_text.roi_y + self._main_text.roi_height > self._bg_pixmap.height():
                    
                        diff = (self._main_text.roi_y + self._main_text.roi_height) - self._bg_pixmap.height()
                        
                        self._main_text.roi_height = self._main_text.roi_height - diff - 1
                    
                    
                    if self._main_text.roi_x < 0:
                    
                        under_zero = abs(self._main_text.roi_x)
                        self._main_text.roi_x = self._main_text.roi_x + under_zero
                        self._main_text.roi_width = self._main_text.roi_width - under_zero
                        
                    
                    if self._main_text.roi_x + self._main_text.roi_width > self._bg_pixmap.width():
                    
                        diff = (self._main_text.roi_x + self._main_text.roi_width) - self._bg_pixmap.width()
                        
                        self._main_text.roi_width = self._main_text.roi_width - diff - 1


                    self._main_text.roi_unlimited_left = False
                    
                    self._main_text.roi_unlimited_right = False
                    
                    self._main_text.roi_unlimited_up = False
                    
                    self._main_text.roi_unlimited_down = False
                    
                elif self.__flag_mouse_is_inside_rect is not None and self.__flag_mouse_is_inside_rect != 0:
                    index = self.__flag_mouse_is_inside_rect -1
                    
                    """
                    percentage_screen_w = int(0.1 * self._bg_pixmap.width())
                    percentage_screen_h = int(0.1 * self._bg_pixmap.height())
                    percentage_object_w = int(0.5 * self._sub_texts_finder[index].width)
                    percentage_object_h = int(0.5 * self._sub_texts_finder[index].height)
                    
                    roi_height = percentage_screen_h + percentage_object_h + self._sub_texts_finder[index].height
                    
                    roi_width = percentage_screen_w + percentage_object_w + self._sub_texts_finder[index].width
                    
                    roi_width_half = int((roi_width - self._sub_texts_finder[index].width)/2)
                    roi_height_half = int((roi_height - self._sub_texts_finder[index].height)/2)
                    """
                    self.ignore_release = True
                    #roi_height = int(15*self.scaling_factor) + self._sub_texts_finder[index].height
                    
                    #roi_width = int(15*self.scaling_factor) + self._sub_texts_finder[index].width
                    
                    #roi_width_half = int((roi_width - self._sub_texts_finder[index].width)/2)
                    #roi_height_half = int((roi_height - self._sub_texts_finder[index].height)/2)
                    
                    """
                    self._sub_texts_finder[index].roi_x =  (self._sub_texts_finder[index].x - self._main_text.x) - int(1*self.scaling_factor)
                    self._sub_texts_finder[index].roi_y =  (self._sub_texts_finder[index].y - self._main_text.y) - int(1*self.scaling_factor)
                    self._sub_texts_finder[index].roi_height = self._sub_texts_finder[index].height + int(6*self.scaling_factor)
                    self._sub_texts_finder[index].roi_width = self._sub_texts_finder[index].width + int(6*self.scaling_factor)
                    """
                    
                    hw_factor = 0
                                        
                    if self._sub_texts_finder[index].height < self._sub_texts_finder[index].width:
                        hw_factor = self._sub_texts_finder[index].height
                    else:
                        hw_factor = self._sub_texts_finder[index].width
                        
                        
                    sc_factor = 0
                                        
                    if self._bg_pixmap.height() < self._bg_pixmap.width():
                        sc_factor = self._bg_pixmap.height()
                    else:
                        sc_factor = self._bg_pixmap.width()
                        
                    percentage_screen_w = int(0.0125 * sc_factor)
                    percentage_screen_h = int(0.0125 * sc_factor)
                    percentage_object_w = int(0.2 * hw_factor) #self._sub_texts_finder[index].width)
                    percentage_object_h = int(0.2 * hw_factor) #self._sub_texts_finder[index].height)
                    
                    roi_height = percentage_screen_h + percentage_object_h + self._sub_texts_finder[index].height
                    
                    roi_width = percentage_screen_w + percentage_object_w + self._sub_texts_finder[index].width
                    
                    
                    """
                    hw_factor = 0
                    
                    if self._sub_texts_finder[index].height < self._sub_texts_finder[index].width:
                        hw_factor = self._sub_texts_finder[index].height
                    else:
                        hw_factor = self._sub_texts_finder[index].width
                    
                    roi_height = int(0.95 * hw_factor) + self._sub_texts_finder[index].height

                    roi_width = int(0.95 * hw_factor) + self._sub_texts_finder[index].width
                    """

                    roi_width_half = int((roi_width - self._sub_texts_finder[index].width)/2)

                    roi_height_half = int((roi_height - self._sub_texts_finder[index].height)/2)


                    self._sub_texts_finder[index].roi_x =  (self._sub_texts_finder[index].x - self._main_text.x) - roi_width_half
                    self._sub_texts_finder[index].roi_y =  (self._sub_texts_finder[index].y - self._main_text.y) - roi_height_half
                    self._sub_texts_finder[index].roi_height = self._sub_texts_finder[index].height + (roi_height_half*2)
                    self._sub_texts_finder[index].roi_width = self._sub_texts_finder[index].width + (roi_width_half*2)
                    
                    """
                    roi_height = int(0.30*hw_factor*self.scaling_factor) + self._sub_texts_finder[index].height #int(10*self.scaling_factor) + self._sub_texts_finder[index].height

                    roi_width = int(0.30*hw_factor*self.scaling_factor) + self._sub_texts_finder[index].width #int(10*self.scaling_factor) + self._sub_texts_finder[index].width

                    roi_width_half = int((roi_width - self._sub_texts_finder[index].width)/2)
                    roi_height_half = int((roi_height - self._sub_texts_finder[index].height)/2)

                    self._sub_texts_finder[index].roi_x =  (self._sub_texts_finder[index].x - self._main_text.x) - roi_width_half
                    self._sub_texts_finder[index].roi_y =  (self._sub_texts_finder[index].y - self._main_text.y) - roi_height_half
                    self._sub_texts_finder[index].roi_height = roi_height
                    self._sub_texts_finder[index].roi_width = roi_width
                    """
                    
                    #self._sub_texts_finder[index].roi_x =  (self._sub_texts_finder[index].x - self._main_text.x) - roi_width_half
                    #self._sub_texts_finder[index].roi_y =  (self._sub_texts_finder[index].y - self._main_text.y) - roi_height_half
                    #self._sub_texts_finder[index].roi_height = roi_height
                    #self._sub_texts_finder[index].roi_width = roi_width
                    
                    
                    if self._main_text.y + self._sub_texts_finder[index].roi_y < 0:
                    
                        under_zero = abs(self._main_text.y + self._sub_texts_finder[index].roi_y)
                        self._sub_texts_finder[index].roi_y = self._sub_texts_finder[index].roi_y + under_zero
                        self._sub_texts_finder[index].roi_height = self._sub_texts_finder[index].roi_height - under_zero
                        
                    
                    if self._main_text.y + self._sub_texts_finder[index].roi_y + self._sub_texts_finder[index].roi_height > self._bg_pixmap.height():
                    
                        diff = (self._main_text.y + self._sub_texts_finder[index].roi_y + self._sub_texts_finder[index].roi_height) - self._bg_pixmap.height()
                        
                        self._sub_texts_finder[index].roi_height = self._sub_texts_finder[index].roi_height - diff - 1
                        
                    if self._main_text.x + self._sub_texts_finder[index].roi_x < 0:
                    
                        under_zero = abs(self._main_text.x + self._sub_texts_finder[index].roi_x)
                        self._sub_texts_finder[index].roi_x = self._sub_texts_finder[index].roi_x + under_zero
                        self._sub_texts_finder[index].roi_width = self._sub_texts_finder[index].roi_width - under_zero
                        
                    
                    if self._main_text.x + self._sub_texts_finder[index].roi_x + self._sub_texts_finder[index].roi_width > self._bg_pixmap.width():
                    
                        diff = (self._main_text.x + self._sub_texts_finder[index].roi_x + self._sub_texts_finder[index].roi_width) - self._bg_pixmap.width()
                        
                        self._sub_texts_finder[index].roi_width = self._sub_texts_finder[index].roi_width - diff - 1
                    


                    self._sub_texts_finder[index].roi_unlimited_left = False
                    
                    self._sub_texts_finder[index].roi_unlimited_right = False
                    
                    self._sub_texts_finder[index].roi_unlimited_up = False
                    
                    self._sub_texts_finder[index].roi_unlimited_down = False
                
                
            
            elif self.ignore_release is False and self._show_boundingrects is False:
        
                self.__click_position = QPoint(QCursor.pos())

                if self.set_xy_offset is not None:
                    if self.set_xy_offset == -1:
                        self._main_text.x_offset = self.__click_position.x() - self._main_text.x
                        self._main_text.y_offset = self.__click_position.y() - self._main_text.y
                    else:
                        self._sub_texts_finder[self.set_xy_offset].x_offset = self.__click_position.x() - self._sub_texts_finder[self.set_xy_offset].x
                        self._sub_texts_finder[self.set_xy_offset].y_offset = self.__click_position.y() - self._sub_texts_finder[self.set_xy_offset].y
                elif self.__flag_mouse_is_on_border is not None:
                    self.__border_index = self.__flag_mouse_is_on_border
                    self.__drag_border = True
                    if self.__border_index == 0:
                        self._old_height_rect = self._main_text.height
                        self._old_width_rect = self._main_text.width
                        self._old_x_rect = self._main_text.x
                        self._old_y_rect = self._main_text.y
                        
                        self._old_roi_height_rect = self._main_text.roi_height
                        self._old_roi_width_rect = self._main_text.roi_width
                        self._old_roi_x_rect = self._main_text.roi_x
                        self._old_roi_y_rect = self._main_text.roi_y
                    else:
                        self._old_height_rect = self._sub_texts_finder[self.__border_index-1].height
                        self._old_width_rect = self._sub_texts_finder[self.__border_index-1].width
                        self._old_x_rect = self._sub_texts_finder[self.__border_index-1].x
                        self._old_y_rect = self._sub_texts_finder[self.__border_index-1].y
                        
                        self._old_roi_height_rect = self._sub_texts_finder[self.__border_index-1].roi_height
                        self._old_roi_width_rect = self._sub_texts_finder[self.__border_index-1].roi_width
                        self._old_roi_x_rect = self._sub_texts_finder[self.__border_index-1].roi_x
                        self._old_roi_y_rect = self._sub_texts_finder[self.__border_index-1].roi_y
           
                elif self.__flag_mouse_is_inside_rect is not None:
                    self.__move_index = self.__flag_mouse_is_inside_rect
                    
            
                    if self.__move_index == 0:
                        rect = self._main_text
                    else:
                        rect = self._sub_texts_finder[self.__move_index - 1]
                    
                    self.__position_offset_x = self.__click_position.x() - rect.x
                    self.__position_offset_y =  self.__click_position.y() - rect.y

                
                else:
                    self.__capturing = True
                
        elif event.buttons() == Qt.RightButton and self.set_xy_offset is None:
        
            if event.modifiers() == Qt.ControlModifier and self._show_boundingrects is False:
                self.ignore_release = True
                index = 0
                delete_sub = False
                delete_main = False
                
                if self.__flag_mouse_is_inside_rect is not None and self.__flag_mouse_is_inside_rect == 0 and len(self._sub_texts_finder) == 0:
                    index = 0
                    delete_main = True
                
                if self.__flag_mouse_is_on_border == 0 and self.__flag_mouse_is_on_border is not None and len(self._sub_texts_finder) == 0:
                    index = 0
                    delete_main = True

                
                if self.__flag_mouse_is_inside_rect is not None and self.__flag_mouse_is_inside_rect != 0 and len(self._sub_texts_finder) > 0:
                    index = self.__flag_mouse_is_inside_rect -1
                    delete_sub = True
                
                if self.__flag_mouse_is_on_border != 0 and self.__flag_mouse_is_on_border is not None and len(self._sub_texts_finder) > 0:
                    index = self.__flag_mouse_is_on_border -1
                    delete_sub = True
                    
                if delete_sub is True:
                    if self._sub_texts_finder[-1].x != 0 and self._sub_texts_finder[-1].y != 0 \
                    and self._sub_texts_finder[-1].width != 0 and self._sub_texts_finder[-1].height != 0:

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

                        self.__deleted_texts.append(self._sub_texts_finder[index])
                        del self._sub_texts_finder[index]
                        
                        self.__flag_need_to_delete_roi = False
                        self.__flag_need_to_restore_roi = True
                        self.__flag_capturing_sub_text_rect_roi = True
                        self.__flag_capturing_sub_text = False


                elif delete_main is True:

                    #self._sub_texts_finder = []
                    #self.__deleted_texts = []
                
                    self._main_text.deleted_x = self._main_text.x
                    self._main_text.deleted_y = self._main_text.y
                    self._main_text.deleted_width = self._main_text.width
                    self._main_text.deleted_height = self._main_text.height

                    self._main_text.x = 0
                    self._main_text.y = 0
                    self._main_text.width = 0
                    self._main_text.height = 0
                    
                            
                    self.__deleted_texts.append(self._main_text)
                    self._main_text = None

                    self.__flag_need_to_delete_main_roi = True
                    self.__flag_need_to_restore_main_roi = False
                    self.__flag_capturing_main_text_rect_roi = False
                    self.__flag_capturing_main_text_rect = True
                    self.__flag_need_to_restore_main_text_rect = True

                    
                    self.__flag_need_to_delete_main_roi = False
                    self.__flag_need_to_restore_main_roi = True
                    self.__flag_capturing_main_text_rect_roi = True
                    self.__flag_capturing_main_text_rect = False
                    self.__flag_capturing_sub_text_rect_roi = True
                    
            else:

                rect = self.is_mouse_inside_bounding_rects()
        
                if self.__flag_mouse_is_on_border == 0 and self.__flag_mouse_is_on_border is not None and self._show_boundingrects is False:

                    index = self.__flag_mouse_is_on_border-1
                    
                    
                    if self.__flag_mouse_is_on_left_border_roi is True:
                        self._main_text.roi_unlimited_left = True
                        
                    if self.__flag_mouse_is_on_right_border_roi is True:
                        self._main_text.roi_unlimited_right = True
                        
                    if self.__flag_mouse_is_on_top_border_roi is True:
                        self._main_text.roi_unlimited_up = True
                        
                    if self.__flag_mouse_is_on_bottom_border_roi is True:
                        self._main_text.roi_unlimited_down = True
                        
                elif self.__flag_mouse_is_on_border != 0 and self.__flag_mouse_is_on_border is not None and self._show_boundingrects is False:

                    index = self.__flag_mouse_is_on_border-1
                    
                    
                    if self.__flag_mouse_is_on_left_border_roi is True:
                        self._sub_texts_finder[index].roi_unlimited_left = True
                        
                    if self.__flag_mouse_is_on_right_border_roi is True:
                        self._sub_texts_finder[index].roi_unlimited_right = True
                        
                    if self.__flag_mouse_is_on_top_border_roi is True:
                        self._sub_texts_finder[index].roi_unlimited_up = True
                        
                    if self.__flag_mouse_is_on_bottom_border_roi is True:
                        self._sub_texts_finder[index].roi_unlimited_down = True

                elif rect is not None and self.__flag_capturing_sub_text is False and self.__flag_capturing_main_text_rect is False:
                    self.add_rect_from_boundings_rects(rect)
                    
            self.update()
            
    def mouseReleaseEvent(self, event):
        if self._ctrl_is_pressed is True:
            event.ignore()
            self.ignore_release = False
            self.update()
            return
    
        if self.ignore_release is True:
            self.ignore_release = False
            event.ignore()
        elif event.button() == Qt.LeftButton:
            self.__capturing = False
            
            if self.set_xy_offset is not None:
                
                self.last_xy_offset_index = self.set_xy_offset
                #self.set_xy_offset = None
            elif self.__move_index is not None:
                self.__move_index = None
                
            elif self.__drag_border is True:
                self.__drag_border = False
                self.__flag_mouse_is_on_left_border = False
                self.__flag_mouse_is_on_right_border = False
                self.__flag_mouse_is_on_top_border = False
                self.__flag_mouse_is_on_bottom_border = False
                self.__flag_mouse_is_on_border = None
                self.__border_index = None
            
            
            elif self.__flag_capturing_main_text_rect_roi is True:
                self.last_xy_offset_index = None
                self.__flag_capturing_main_text_rect_roi = False
                self.__flag_capturing_main_text_rect = True
                self.__flag_need_to_delete_main_roi = True
                #if len(self.__deleted_texts) > 0:
                #    del self.__deleted_texts[-1]
                self.add_main_text_roi()
                
            elif self.__flag_capturing_main_text_rect is True:
                self.last_xy_offset_index = None
                #self.__flag_capturing_main_text_rect_roi = False
                self.__flag_capturing_main_text_rect = False
                self.__flag_capturing_sub_text_rect_roi = True
                self.__flag_need_to_delete_main_roi = False
                self.add_main_rect()
            elif self.__flag_capturing_sub_text_rect_roi is True:
                self.last_xy_offset_index = None
                self.__flag_capturing_sub_text_rect_roi = False
                self.__flag_capturing_sub_text = True
                self.__flag_need_to_delete_roi = True
                if len(self.__deleted_texts) > 0:
                    del self.__deleted_texts[-1]
                self.add_sub_text_roi()
            elif self.__flag_capturing_sub_text is True:
                self.last_xy_offset_index = None
                self.__flag_capturing_sub_text = False
                self.__flag_capturing_sub_text_rect_roi = True
                self.__flag_need_to_delete_roi = False
                self.add_sub_text_attributes()
            
        self.update()
        

    """    
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
    """
        
    def paintEvent(self, event):
    
        mouse_on_border = False
    
        qp = QPainter()
        qp.begin(self)
        qp.drawPixmap(0, 0, self._bg_pixmap)
        
        
        self.__flag_mouse_is_inside_rect = None
        self.__index_of_rectangle_with_mouse_inside = -2
        
                
        if self._show_boundingrects is True:
            self.setCursor(QCursor(Qt.ArrowCursor))
            self.draw_bounding_rects(qp)
        
        else:
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

            
            if self._main_text is not None:
            
                    

                if self.__drag_border is False and self.set_xy_offset is None and self.__move_index is None and self.__capturing is False and self._main_text.show is True:
                
                    if self.is_mouse_inside_rect(self._main_text):
                        self.__flag_mouse_is_inside_rect = 0
                        self.setCursor(QCursor(Qt.SizeAllCursor))
                    elif self.is_mouse_on_left_border_roi(self._main_text) and self.is_mouse_on_top_border_roi(self._main_text):
                        self.__flag_mouse_is_on_left_up_corner_roi = True
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
                        
                        self.__flag_mouse_is_on_right_up_corner_roi = False
                        self.__flag_mouse_is_on_right_bottom_corner_roi = False
                        self.__flag_mouse_is_on_left_bottom_corner_roi = False
                        self.__flag_mouse_is_on_border = 0
                        mouse_on_border = True
                        self.setCursor(QCursor(Qt.SizeFDiagCursor))
                        #self.setCursor(Qt.SizeFDiagCursor)
                        
                    elif self.is_mouse_on_right_border_roi(self._main_text) and self.is_mouse_on_top_border_roi(self._main_text):
                        self.__flag_mouse_is_on_right_up_corner_roi = True
                        
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
                        self.__flag_mouse_is_on_right_bottom_corner_roi = False
                        self.__flag_mouse_is_on_left_bottom_corner_roi = False

                        self.__flag_mouse_is_on_border = 0
                        mouse_on_border = True
                        self.setCursor(QCursor(Qt.SizeBDiagCursor))
                        #QApplication.setOverrideCursor(Qt.SizeBDiagCursor)
                        
                    elif self.is_mouse_on_right_border_roi(self._main_text) and self.is_mouse_on_bottom_border_roi(self._main_text):
                        self.__flag_mouse_is_on_right_bottom_corner_roi = True
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

                        self.__flag_mouse_is_on_left_bottom_corner_roi = False


                        self.__flag_mouse_is_on_border = 0
                        mouse_on_border = True
                        self.setCursor(QCursor(Qt.SizeFDiagCursor))
                        #QApplication.setOverrideCursor(Qt.SizeFDiagCursor)
                        
                    elif self.is_mouse_on_left_border_roi(self._main_text) and self.is_mouse_on_bottom_border_roi(self._main_text):
                        self.__flag_mouse_is_on_left_bottom_corner_roi = True
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


                        self.__flag_mouse_is_on_border = 0
                        mouse_on_border = True
                        self.setCursor(QCursor(Qt.SizeBDiagCursor))
                        #QApplication.setOverrideCursor(Qt.SizeBDiagCursor)
                        
                    elif self.is_mouse_on_left_border_roi(self._main_text):
                        self.__flag_mouse_is_on_left_border_roi = True
                        self.__flag_mouse_is_on_left_border = False
                        self.__flag_mouse_is_on_right_border = False
                        self.__flag_mouse_is_on_top_border = False
                        self.__flag_mouse_is_on_bottom_border = False

                        self.__flag_mouse_is_on_left_up_corner = False
                        self.__flag_mouse_is_on_right_up_corner = False
                        self.__flag_mouse_is_on_right_bottom_corner = False
                        self.__flag_mouse_is_on_left_bottom_corner = False

                        self.__flag_mouse_is_on_right_border_roi = False
                        self.__flag_mouse_is_on_top_border_roi = False
                        self.__flag_mouse_is_on_bottom_border_roi = False

                        self.__flag_mouse_is_on_left_up_corner_roi = False
                        self.__flag_mouse_is_on_right_up_corner_roi = False
                        self.__flag_mouse_is_on_right_bottom_corner_roi = False
                        self.__flag_mouse_is_on_left_bottom_corner_roi = False


                        self.__flag_mouse_is_on_border = 0
                        mouse_on_border = True
                        self.setCursor(QCursor(Qt.SizeHorCursor))
                        #QApplication.setOverrideCursor(Qt.SizeHorCursor)
                                            
                    elif self.is_mouse_on_top_border_roi(self._main_text):
                        self.__flag_mouse_is_on_top_border_roi = True
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
                        self.__flag_mouse_is_on_bottom_border_roi = False

                        self.__flag_mouse_is_on_left_up_corner_roi = False
                        self.__flag_mouse_is_on_right_up_corner_roi = False
                        self.__flag_mouse_is_on_right_bottom_corner_roi = False
                        self.__flag_mouse_is_on_left_bottom_corner_roi = False


                        self.__flag_mouse_is_on_border = 0
                        mouse_on_border = True
                        self.setCursor(QCursor(Qt.SizeVerCursor))
                        #QApplication.setOverrideCursor(Qt.SizeVerCursor)
                        
                    elif self.is_mouse_on_right_border_roi(self._main_text):
                        self.__flag_mouse_is_on_right_border_roi = True
                        self.__flag_mouse_is_on_left_border = False
                        self.__flag_mouse_is_on_right_border = False
                        self.__flag_mouse_is_on_top_border = False
                        self.__flag_mouse_is_on_bottom_border = False

                        self.__flag_mouse_is_on_left_up_corner = False
                        self.__flag_mouse_is_on_right_up_corner = False
                        self.__flag_mouse_is_on_right_bottom_corner = False
                        self.__flag_mouse_is_on_left_bottom_corner = False

                        self.__flag_mouse_is_on_left_border_roi = False

                        self.__flag_mouse_is_on_top_border_roi = False
                        self.__flag_mouse_is_on_bottom_border_roi = False

                        self.__flag_mouse_is_on_left_up_corner_roi = False
                        self.__flag_mouse_is_on_right_up_corner_roi = False
                        self.__flag_mouse_is_on_right_bottom_corner_roi = False
                        self.__flag_mouse_is_on_left_bottom_corner_roi = False


                        self.__flag_mouse_is_on_border = 0
                        mouse_on_border = True
                        self.setCursor(QCursor(Qt.SizeHorCursor))
                        #QApplication.setOverrideCursor(Qt.SizeHorCursor)

                        
                    elif self.is_mouse_on_bottom_border_roi(self._main_text):
                        self.__flag_mouse_is_on_bottom_border_roi = True
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

                        self.__flag_mouse_is_on_left_up_corner_roi = False
                        self.__flag_mouse_is_on_right_up_corner_roi = False
                        self.__flag_mouse_is_on_right_bottom_corner_roi = False
                        self.__flag_mouse_is_on_left_bottom_corner_roi = False


                        self.__flag_mouse_is_on_border = 0
                        mouse_on_border = True
                        self.setCursor(QCursor(Qt.SizeVerCursor))

                    elif self.is_mouse_on_left_border(self._main_text) and self.is_mouse_on_top_border(self._main_text):
                        self.__flag_mouse_is_on_left_up_corner = True
                        self.__flag_mouse_is_on_left_border = False
                        self.__flag_mouse_is_on_right_border = False
                        self.__flag_mouse_is_on_top_border = False
                        self.__flag_mouse_is_on_bottom_border = False

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


                        self.__flag_mouse_is_on_border = 0
                        mouse_on_border = True
                        self.setCursor(QCursor(Qt.SizeFDiagCursor))
                        #self.setCursor(Qt.SizeFDiagCursor)
                        
                    elif self.is_mouse_on_right_border(self._main_text) and self.is_mouse_on_top_border(self._main_text):
                        self.__flag_mouse_is_on_right_up_corner = True
                        self.__flag_mouse_is_on_left_border = False
                        self.__flag_mouse_is_on_right_border = False
                        self.__flag_mouse_is_on_top_border = False
                        self.__flag_mouse_is_on_bottom_border = False

                        self.__flag_mouse_is_on_left_up_corner = False
 
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


                        self.__flag_mouse_is_on_border = 0
                        mouse_on_border = True
                        self.setCursor(QCursor(Qt.SizeBDiagCursor))
                        #QApplication.setOverrideCursor(Qt.SizeBDiagCursor)
                        
                    elif self.is_mouse_on_right_border(self._main_text) and self.is_mouse_on_bottom_border(self._main_text):
                        self.__flag_mouse_is_on_right_bottom_corner = True
                        self.__flag_mouse_is_on_left_border = False
                        self.__flag_mouse_is_on_right_border = False
                        self.__flag_mouse_is_on_top_border = False
                        self.__flag_mouse_is_on_bottom_border = False

                        self.__flag_mouse_is_on_left_up_corner = False
                        self.__flag_mouse_is_on_right_up_corner = False

                        self.__flag_mouse_is_on_left_bottom_corner = False

                        self.__flag_mouse_is_on_left_border_roi = False
                        self.__flag_mouse_is_on_right_border_roi = False
                        self.__flag_mouse_is_on_top_border_roi = False
                        self.__flag_mouse_is_on_bottom_border_roi = False

                        self.__flag_mouse_is_on_left_up_corner_roi = False
                        self.__flag_mouse_is_on_right_up_corner_roi = False
                        self.__flag_mouse_is_on_right_bottom_corner_roi = False
                        self.__flag_mouse_is_on_left_bottom_corner_roi = False


                        self.__flag_mouse_is_on_border = 0
                        mouse_on_border = True
                        self.setCursor(QCursor(Qt.SizeFDiagCursor))
                        #QApplication.setOverrideCursor(Qt.SizeFDiagCursor)
                        
                    elif self.is_mouse_on_left_border(self._main_text) and self.is_mouse_on_bottom_border(self._main_text):
                        self.__flag_mouse_is_on_left_bottom_corner = True
                        self.__flag_mouse_is_on_left_border = False
                        self.__flag_mouse_is_on_right_border = False
                        self.__flag_mouse_is_on_top_border = False
                        self.__flag_mouse_is_on_bottom_border = False

                        self.__flag_mouse_is_on_left_up_corner = False
                        self.__flag_mouse_is_on_right_up_corner = False
                        self.__flag_mouse_is_on_right_bottom_corner = False

                        self.__flag_mouse_is_on_left_border_roi = False
                        self.__flag_mouse_is_on_right_border_roi = False
                        self.__flag_mouse_is_on_top_border_roi = False
                        self.__flag_mouse_is_on_bottom_border_roi = False

                        self.__flag_mouse_is_on_left_up_corner_roi = False
                        self.__flag_mouse_is_on_right_up_corner_roi = False
                        self.__flag_mouse_is_on_right_bottom_corner_roi = False
                        self.__flag_mouse_is_on_left_bottom_corner_roi = False


                        self.__flag_mouse_is_on_border = 0
                        mouse_on_border = True
                        self.setCursor(QCursor(Qt.SizeBDiagCursor))
                        #QApplication.setOverrideCursor(Qt.SizeBDiagCursor)
                        
                    elif self.is_mouse_on_left_border(self._main_text):
                        self.__flag_mouse_is_on_left_border = True
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


                        self.__flag_mouse_is_on_border = 0
                        mouse_on_border = True
                        self.setCursor(QCursor(Qt.SizeHorCursor))
                        #QApplication.setOverrideCursor(Qt.SizeHorCursor)
                                            
                    elif self.is_mouse_on_top_border(self._main_text):
                        self.__flag_mouse_is_on_top_border = True
                        self.__flag_mouse_is_on_left_border = False
                        self.__flag_mouse_is_on_right_border = False

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


                        self.__flag_mouse_is_on_border = 0
                        mouse_on_border = True
                        self.setCursor(QCursor(Qt.SizeVerCursor))
                        #QApplication.setOverrideCursor(Qt.SizeVerCursor)
                        
                    elif self.is_mouse_on_right_border(self._main_text):
                        self.__flag_mouse_is_on_right_border = True
                        self.__flag_mouse_is_on_left_border = False

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


                        self.__flag_mouse_is_on_border = 0
                        mouse_on_border = True
                        self.setCursor(QCursor(Qt.SizeHorCursor))
                        #QApplication.setOverrideCursor(Qt.SizeHorCursor)

                        
                    elif self.is_mouse_on_bottom_border(self._main_text):
                        self.__flag_mouse_is_on_bottom_border = True
                        self.__flag_mouse_is_on_left_border = False
                        self.__flag_mouse_is_on_right_border = False
                        self.__flag_mouse_is_on_top_border = False

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


                        self.__flag_mouse_is_on_border = 0
                        mouse_on_border = True
                        self.setCursor(QCursor(Qt.SizeVerCursor))
                        #QApplication.setOverrideCursor(Qt.SizeVerCursor)

                elif self.__drag_border is True and self.set_xy_offset is None and self._main_text.show is True:
                    self.update_border()
                elif self.__move_index is not None and self.set_xy_offset is None and self._main_text.show is True:
                    self.update_position()
                            
                self.draw_main_text_rect(qp)
                    
            rect_index = 0
            #self.__sub_template_color_index = 0

            cnt_sub = 1
            cnt_sub_text = 1
            for sub_text_finder in self._sub_texts_finder:



                if self.__drag_border is False and self.set_xy_offset is None and self.__move_index is None and self.__capturing is False and sub_text_finder.show is True:
                                            
                    
                    #if sub_text_finder.show_min_max is False and sub_text_finder.show_tolerance is False:
                    if self.is_mouse_inside_rect(sub_text_finder) and self.__flag_mouse_is_on_border is None:
                        self.__flag_mouse_is_inside_rect = cnt_sub
                        self.setCursor(QCursor(Qt.SizeAllCursor))
                        
            
                    elif self.is_mouse_on_left_border_roi(sub_text_finder) and self.is_mouse_on_top_border_roi(sub_text_finder):
                        self.__flag_mouse_is_on_left_up_corner_roi = True
                                    
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
                        self.__flag_mouse_is_on_right_up_corner_roi = False
                        self.__flag_mouse_is_on_right_bottom_corner_roi = False
                        self.__flag_mouse_is_on_left_bottom_corner_roi = False
                        
                        self.__flag_mouse_is_on_border = cnt_sub
                        mouse_on_border = True
                        self.setCursor(QCursor(Qt.SizeFDiagCursor))
                        #self.setCursor(Qt.SizeFDiagCursor)
                        
                    elif self.is_mouse_on_right_border_roi(sub_text_finder) and self.is_mouse_on_top_border_roi(sub_text_finder):
                        self.__flag_mouse_is_on_right_up_corner_roi = True
                        
                                    
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
                        self.__flag_mouse_is_on_right_bottom_corner_roi = False
                        self.__flag_mouse_is_on_left_bottom_corner_roi = False
                        
                        self.__flag_mouse_is_on_border = cnt_sub
                        mouse_on_border = True
                        self.setCursor(QCursor(Qt.SizeBDiagCursor))
                        #QApplication.setOverrideCursor(Qt.SizeBDiagCursor)
                        
                    elif self.is_mouse_on_right_border_roi(sub_text_finder) and self.is_mouse_on_bottom_border_roi(sub_text_finder):
                        self.__flag_mouse_is_on_right_bottom_corner_roi = True
                            
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
                        self.__flag_mouse_is_on_left_bottom_corner_roi = False
                        
                        self.__flag_mouse_is_on_border = cnt_sub
                        mouse_on_border = True
                        self.setCursor(QCursor(Qt.SizeFDiagCursor))
                        #QApplication.setOverrideCursor(Qt.SizeFDiagCursor)
                        
                    elif self.is_mouse_on_left_border_roi(sub_text_finder) and self.is_mouse_on_bottom_border_roi(sub_text_finder):
                        self.__flag_mouse_is_on_left_bottom_corner_roi = True
                                   
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
                        
                        self.__flag_mouse_is_on_border = cnt_sub
                        mouse_on_border = True
                        self.setCursor(QCursor(Qt.SizeBDiagCursor))
                        #QApplication.setOverrideCursor(Qt.SizeBDiagCursor)
                        
                    elif self.is_mouse_on_left_border_roi(sub_text_finder):
                        self.__flag_mouse_is_on_left_border_roi = True
                                        
                        self.__flag_mouse_is_on_left_border = False
                        self.__flag_mouse_is_on_right_border = False
                        self.__flag_mouse_is_on_top_border = False
                        self.__flag_mouse_is_on_bottom_border = False
                        
                        self.__flag_mouse_is_on_left_up_corner = False
                        self.__flag_mouse_is_on_right_up_corner = False
                        self.__flag_mouse_is_on_right_bottom_corner = False
                        self.__flag_mouse_is_on_left_bottom_corner = False
                        
                        self.__flag_mouse_is_on_right_border_roi = False
                        self.__flag_mouse_is_on_top_border_roi = False
                        self.__flag_mouse_is_on_bottom_border_roi = False
                        
                        self.__flag_mouse_is_on_left_up_corner_roi = False
                        self.__flag_mouse_is_on_right_up_corner_roi = False
                        self.__flag_mouse_is_on_right_bottom_corner_roi = False
                        self.__flag_mouse_is_on_left_bottom_corner_roi = False
                        
                        self.__flag_mouse_is_on_border = cnt_sub
                        mouse_on_border = True
                        self.setCursor(QCursor(Qt.SizeHorCursor))
                        #QApplication.setOverrideCursor(Qt.SizeHorCursor)
                                            
                    elif self.is_mouse_on_top_border_roi(sub_text_finder):
                        self.__flag_mouse_is_on_top_border_roi = True
                                        
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
                        self.__flag_mouse_is_on_bottom_border_roi = False
                        
                        self.__flag_mouse_is_on_left_up_corner_roi = False
                        self.__flag_mouse_is_on_right_up_corner_roi = False
                        self.__flag_mouse_is_on_right_bottom_corner_roi = False
                        self.__flag_mouse_is_on_left_bottom_corner_roi = False
                        
                        self.__flag_mouse_is_on_border = cnt_sub
                        mouse_on_border = True
                        self.setCursor(QCursor(Qt.SizeVerCursor))
                        #QApplication.setOverrideCursor(Qt.SizeVerCursor)
                        
                    elif self.is_mouse_on_right_border_roi(sub_text_finder):
                        self.__flag_mouse_is_on_right_border_roi = True
                                        
                        self.__flag_mouse_is_on_left_border = False
                        self.__flag_mouse_is_on_right_border = False
                        self.__flag_mouse_is_on_top_border = False
                        self.__flag_mouse_is_on_bottom_border = False
                        
                        self.__flag_mouse_is_on_left_up_corner = False
                        self.__flag_mouse_is_on_right_up_corner = False
                        self.__flag_mouse_is_on_right_bottom_corner = False
                        self.__flag_mouse_is_on_left_bottom_corner = False
                        
                        self.__flag_mouse_is_on_left_border_roi = False
                        self.__flag_mouse_is_on_top_border_roi = False
                        self.__flag_mouse_is_on_bottom_border_roi = False
                        
                        self.__flag_mouse_is_on_left_up_corner_roi = False
                        self.__flag_mouse_is_on_right_up_corner_roi = False
                        self.__flag_mouse_is_on_right_bottom_corner_roi = False
                        self.__flag_mouse_is_on_left_bottom_corner_roi = False
                        
                        self.__flag_mouse_is_on_border = cnt_sub
                        mouse_on_border = True
                        self.setCursor(QCursor(Qt.SizeHorCursor))
                        #QApplication.setOverrideCursor(Qt.SizeHorCursor)

                        
                    elif self.is_mouse_on_bottom_border_roi(sub_text_finder):
                        self.__flag_mouse_is_on_bottom_border_roi = True
                            
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
                        
                        self.__flag_mouse_is_on_left_up_corner_roi = False
                        self.__flag_mouse_is_on_right_up_corner_roi = False
                        self.__flag_mouse_is_on_right_bottom_corner_roi = False
                        self.__flag_mouse_is_on_left_bottom_corner_roi = False
                        
                        self.__flag_mouse_is_on_border = cnt_sub
                        mouse_on_border = True
                        self.setCursor(QCursor(Qt.SizeVerCursor))

                    elif self.is_mouse_on_left_border(sub_text_finder) and self.is_mouse_on_top_border(sub_text_finder):
                        self.__flag_mouse_is_on_left_up_corner = True
                                        
                        self.__flag_mouse_is_on_left_border = False
                        self.__flag_mouse_is_on_right_border = False
                        self.__flag_mouse_is_on_top_border = False
                        self.__flag_mouse_is_on_bottom_border = False
                        
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
                        
                        self.__flag_mouse_is_on_border = cnt_sub
                        mouse_on_border = True
                        self.setCursor(QCursor(Qt.SizeFDiagCursor))
                        #self.setCursor(Qt.SizeFDiagCursor)
                        
                    elif self.is_mouse_on_right_border(sub_text_finder) and self.is_mouse_on_top_border(sub_text_finder):
                        self.__flag_mouse_is_on_right_up_corner = True
                                        
                        self.__flag_mouse_is_on_left_border = False
                        self.__flag_mouse_is_on_right_border = False
                        self.__flag_mouse_is_on_top_border = False
                        self.__flag_mouse_is_on_bottom_border = False
                        
                        self.__flag_mouse_is_on_left_up_corner = False
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
                        
                        self.__flag_mouse_is_on_border = cnt_sub
                        mouse_on_border = True
                        self.setCursor(QCursor(Qt.SizeBDiagCursor))
                        #QApplication.setOverrideCursor(Qt.SizeBDiagCursor)
                        
                    elif self.is_mouse_on_right_border(sub_text_finder) and self.is_mouse_on_bottom_border(sub_text_finder):
                        self.__flag_mouse_is_on_right_bottom_corner = True
                                        
                        self.__flag_mouse_is_on_left_border = False
                        self.__flag_mouse_is_on_right_border = False
                        self.__flag_mouse_is_on_top_border = False
                        self.__flag_mouse_is_on_bottom_border = False
                        
                        self.__flag_mouse_is_on_left_up_corner = False
                        self.__flag_mouse_is_on_right_up_corner = False
                        self.__flag_mouse_is_on_left_bottom_corner = False
                        
                        self.__flag_mouse_is_on_left_border_roi = False
                        self.__flag_mouse_is_on_right_border_roi = False
                        self.__flag_mouse_is_on_top_border_roi = False
                        self.__flag_mouse_is_on_bottom_border_roi = False
                        
                        self.__flag_mouse_is_on_left_up_corner_roi = False
                        self.__flag_mouse_is_on_right_up_corner_roi = False
                        self.__flag_mouse_is_on_right_bottom_corner_roi = False
                        self.__flag_mouse_is_on_left_bottom_corner_roi = False
                        
                        self.__flag_mouse_is_on_border = cnt_sub
                        mouse_on_border = True
                        self.setCursor(QCursor(Qt.SizeFDiagCursor))
                        #QApplication.setOverrideCursor(Qt.SizeFDiagCursor)
                        
                    elif self.is_mouse_on_left_border(sub_text_finder) and self.is_mouse_on_bottom_border(sub_text_finder):
                        self.__flag_mouse_is_on_left_bottom_corner = True
                        
                        self.__flag_mouse_is_on_left_border = False
                        self.__flag_mouse_is_on_right_border = False
                        self.__flag_mouse_is_on_top_border = False
                        self.__flag_mouse_is_on_bottom_border = False

                        self.__flag_mouse_is_on_left_up_corner = False
                        self.__flag_mouse_is_on_right_up_corner = False
                        self.__flag_mouse_is_on_right_bottom_corner = False

                        self.__flag_mouse_is_on_left_border_roi = False
                        self.__flag_mouse_is_on_right_border_roi = False
                        self.__flag_mouse_is_on_top_border_roi = False
                        self.__flag_mouse_is_on_bottom_border_roi = False

                        self.__flag_mouse_is_on_left_up_corner_roi = False
                        self.__flag_mouse_is_on_right_up_corner_roi = False
                        self.__flag_mouse_is_on_right_bottom_corner_roi = False
                        self.__flag_mouse_is_on_left_bottom_corner_roi = False
                        
                        self.__flag_mouse_is_on_border = cnt_sub
                        mouse_on_border = True
                        self.setCursor(QCursor(Qt.SizeBDiagCursor))
                        #QApplication.setOverrideCursor(Qt.SizeBDiagCursor)
                        
                    elif self.is_mouse_on_left_border(sub_text_finder):
                        self.__flag_mouse_is_on_left_border = True

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


                        self.__flag_mouse_is_on_border = cnt_sub
                        mouse_on_border = True
                        self.setCursor(QCursor(Qt.SizeHorCursor))
                        #QApplication.setOverrideCursor(Qt.SizeHorCursor)
                                            
                    elif self.is_mouse_on_top_border(sub_text_finder):
                        self.__flag_mouse_is_on_top_border = True
                        self.__flag_mouse_is_on_left_border = False
                        self.__flag_mouse_is_on_right_border = False

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

                        self.__flag_mouse_is_on_border = cnt_sub
                        mouse_on_border = True
                        self.setCursor(QCursor(Qt.SizeVerCursor))
                        #QApplication.setOverrideCursor(Qt.SizeVerCursor)
                        
                    elif self.is_mouse_on_right_border(sub_text_finder):
                        self.__flag_mouse_is_on_right_border = True
                        self.__flag_mouse_is_on_left_border = False

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

                        self.__flag_mouse_is_on_border = cnt_sub
                        mouse_on_border = True
                        self.setCursor(QCursor(Qt.SizeHorCursor))
                        #QApplication.setOverrideCursor(Qt.SizeHorCursor)

                        
                    elif self.is_mouse_on_bottom_border(sub_text_finder):
                        self.__flag_mouse_is_on_bottom_border = True
                        self.__flag_mouse_is_on_left_border = False
                        self.__flag_mouse_is_on_right_border = False
                        self.__flag_mouse_is_on_top_border = False

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

                        
                        self.__flag_mouse_is_on_border = cnt_sub
                        mouse_on_border = True
                        self.setCursor(QCursor(Qt.SizeVerCursor))
                        #QApplication.setOverrideCursor(Qt.SizeVerCursor)
                        
                    cnt_sub = cnt_sub + 1

                elif self.__drag_border is True and self.set_xy_offset is None and sub_text_finder.show is True:
                    self.update_border()
                elif self.__move_index is not None and self.set_xy_offset is None and sub_text_finder.show is True:
                    self.update_position()
                elif sub_text_finder.show is False:
                    cnt_sub = cnt_sub + 1
            
                self.draw_sub_textangle(qp, sub_text_finder, cnt_sub_text)
                cnt_sub_text += 1
                
            if mouse_on_border is False:
                self.__flag_mouse_is_on_border = None
                
                        
            #if self.__flag_mouse_is_on_border is None:
            #    self.setCursor(QCursor(Qt.CrossCursor))


            if self.set_xy_offset is None and self.__flag_mouse_is_on_border is None and self.__flag_mouse_is_inside_rect is None:
            
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
            elif self.set_xy_offset is not None:
                self.draw_cross_lines(qp)
                
        qp.end()
        
    def calc_threshold_inside(self, rect, roi=False):
        
    
        if roi is True:
            if rect.roi_height > 16 * self.scaling_factor and rect.roi_width > 16 * self.scaling_factor:
                return int((6 *self.scaling_factor))
            elif rect.roi_height > 12 * self.scaling_factor and rect.roi_width > 12 * self.scaling_factor:
                return int((4 *self.scaling_factor))
            elif rect.roi_height > 8 * self.scaling_factor and rect.roi_width > 8 * self.scaling_factor:
                return int((2 *self.scaling_factor))
            elif rect.roi_height > 4 * self.scaling_factor and rect.roi_width > 4 * self.scaling_factor:
                return int((1 *self.scaling_factor))
            else:
                return 0

        else:
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
                
    def is_mouse_inside_bounding_rects(self):
        mouse_position = QPoint(QCursor.pos())
        
        mouse_in_rects = []
        
        for box in self._boundingRects:
            
            x, y, w, h = box
            
            if (mouse_position.x() > x and
                    mouse_position.x() < w + x and
                    mouse_position.y() > y and
                    mouse_position.y() < h + y):
                    
                mouse_in_rects.append(box)
                
        if len(mouse_in_rects) > 0:
            mouse_in_rects = sorted(mouse_in_rects, key=lambda element: (element[2], element[3]))
            return mouse_in_rects[0]
        else:
            return None
        
    def is_mouse_inside_rect(self, rect):
    
        mouse_position = QPoint(QCursor.pos())
        threshold = self.calc_threshold_inside(rect)
        
        if (mouse_position.x() > rect.x + threshold and
                mouse_position.x() < rect.width + rect.x - threshold and
                mouse_position.y() > rect.y + threshold and
                mouse_position.y() < rect.height + rect.y - threshold):
            return True
        else:
            return False
            
    def update_position(self):
    
        rect = None
        
        if self.__move_index is None:
            return
        
        if self.__move_index == 0:
            rect = self._main_text
            
            self.__flag_need_to_delete_main_roi = False
            self.__flag_need_to_restore_main_roi = False
            self.__flag_need_to_restore_main_text_rect = False
            self.__flag_need_to_delete_roi = False
            self.__flag_need_to_restore_roi = False
            
            self.__flag_capturing_main_text_rect_roi = False
            self.__flag_capturing_main_text_rect = True
            self.__flag_need_to_delete_main_roi = True     

            self.__flag_capturing_main_text_rect = False
            self.__flag_capturing_sub_text_rect_roi = True
            self.__flag_need_to_delete_main_roi = False

            #self._sub_texts_finder = []
            self.__deleted_texts = []
            
        else:
            rect = self._sub_texts_finder[self.__move_index - 1]
            
        #print rect.roi_x, rect.roi_y, rect.roi_width, rect.roi_height
    
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
            
        if self.__move_index == 0:
            if rect.roi_x + rect.roi_width > self._bg_pixmap.width():
                rect.roi_width = self._bg_pixmap.width() - rect.roi_x
                
            if rect.roi_y + rect.roi_height > self._bg_pixmap.height():
                rect.roi_height = self._bg_pixmap.height() - rect.roi_y
         
               
            if rect.roi_x < 0:
                old_roi_x = rect.roi_x
                rect.roi_x = 0
                
                width_diff = rect.roi_x - old_roi_x
                rect.roi_width = rect.roi_width - width_diff
                
            if rect.roi_y < 0:
                old_roi_y = rect.roi_y
                rect.roi_y = 0
                
                height_diff = rect.roi_y - old_roi_y
                rect.roi_height = rect.roi_height - height_diff
                
        
        else:
            if self._main_text.x + rect.roi_x + rect.roi_width > self._bg_pixmap.width():
                rect.roi_width = self._bg_pixmap.width() - (self._main_text.x + rect.roi_x)
                
            if self._main_text.y + rect.roi_y + rect.roi_height > self._bg_pixmap.height():
                rect.roi_height = self._bg_pixmap.height() - (self._main_text.y + rect.roi_y)
         
               
            if self._main_text.x + rect.roi_x < 0:
                old_roi_x = rect.roi_x
                rect.roi_x = -self._main_text.x
                
                width_diff = rect.roi_x - old_roi_x
                rect.roi_width = rect.roi_width - width_diff
                
            if self._main_text.y + rect.roi_y < 0:
                old_roi_y = rect.roi_y
                rect.roi_y = -self._main_text.y
                
                height_diff = rect.roi_y - old_roi_y
                rect.roi_height = rect.roi_height - height_diff
                
        
        x_offset =  old_x - rect.x
        y_offset =  old_y - rect.y

        if rect.x_offset is not None and rect.y_offset is not None:
            rect.y_offset = rect.y_offset + y_offset
            rect.x_offset = rect.x_offset + x_offset
            
        if self.__move_index == 0:
        
            rect.roi_x = rect.roi_x - x_offset
            rect.roi_y = rect.roi_y - y_offset
            
            for sub_image_finder in self._sub_texts_finder:
                sub_image_finder.roi_x = sub_image_finder.roi_x + x_offset
                sub_image_finder.roi_y = sub_image_finder.roi_y + y_offset
        else:
            rect.roi_x = rect.roi_x - x_offset
            rect.roi_y = rect.roi_y - y_offset
            


        
    def calc_threshold_border(self, rect, roi=False):
        
    
        if roi is True:
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
        else:
            if rect.height > 16 * self.scaling_factor and rect.width > 16 * self.scaling_factor:
                return int((8 *self.scaling_factor))
            elif rect.height > 12 * self.scaling_factor and rect.width > 12 * self.scaling_factor:
                return int((6 *self.scaling_factor))
            elif rect.height > 8 * self.scaling_factor and rect.width > 8 * self.scaling_factor:
                return int((4 *self.scaling_factor))
            elif rect.height > 4 * self.scaling_factor and rect.width > 4 * self.scaling_factor:
                return int((2 *self.scaling_factor))
            else:
                return int(self.scaling_factor)
        
            
    def update_border(self):
    
        rect = None
        
        if self.__border_index is None:
            return
        
        if self.__border_index == 0:
            rect = self._main_text
            
            self.__flag_need_to_delete_main_roi = False
            self.__flag_need_to_restore_main_roi = False
            self.__flag_need_to_restore_main_text_rect = False
            self.__flag_need_to_delete_roi = False
            self.__flag_need_to_restore_roi = False
            
            self.__flag_capturing_main_text_rect_roi = False
            self.__flag_capturing_main_text_rect = True
            self.__flag_need_to_delete_main_roi = True     

            self.__flag_capturing_main_text_rect = False
            self.__flag_capturing_sub_text_rect_roi = True
            self.__flag_need_to_delete_main_roi = False

            #self._sub_texts_finder = []
            self.__deleted_texts = []
            
        else:
            rect = self._sub_texts_finder[self.__border_index - 1]
            
            
            
            
            
            
            
            
            
        if  self.__flag_mouse_is_on_left_up_corner_roi is True:
            
            mouse_position = QPoint(QCursor.pos())
        
            if self.__border_index == 0:
                """
                old_x = rect.roi_x
                old_width = rect.roi_width 
                
                
                rect.roi_x = mouse_position.x()
                rect.roi_width =  (self._old_roi_x_rect - mouse_position.x()) + (self._old_roi_width_rect) #rect.roi_width + (rect.roi_x + 0 - mouse_position.x())

                
                
                if rect.x < rect.roi_x:
                    rect.roi_x = rect.x -1
                    rect.roi_width = self._old_roi_width_rect + (self._old_roi_x_rect - rect.x) + 1
                """
                    
                old_roi_x = rect.roi_x
                old_x = rect.x
                old_roi_width = rect.roi_width 
                old_width = rect.width
                
                
                rect.roi_x = mouse_position.x()
                rect.roi_width = (self._old_roi_x_rect - mouse_position.x()) + (self._old_roi_width_rect) #rect.roi_width + (rect.roi_x + self._main_text.x - mouse_position.x())

                
                
                if rect.x < rect.roi_x: #+ self._main_text.x:
                    rect.x = rect.roi_x
                    rect.width = rect.width - (rect.x - old_x)
                    

                if rect.width < int(4 * self.scaling_factor):
                    
                    rect.x = self._old_x_rect + self._old_width_rect - (4 * self.scaling_factor)
                    rect.width = (4 * self.scaling_factor)
                    rect.roi_x = rect.x #- self._main_text.x# - 1
                    rect.roi_width = self._old_roi_width_rect - (rect.roi_x - self._old_roi_x_rect)
                    
                                
                x_offset =  old_x - rect.x
                
                if rect.x_offset is not None and rect.x_offset is not None:
                    rect.x_offset = rect.x_offset + x_offset
                    
                for sub_image_finder in self._sub_texts_finder:
                    sub_image_finder.roi_x = sub_image_finder.roi_x + x_offset

            else:
                """
                old_x = rect.roi_x
                old_width = rect.roi_width 
                
                
                rect.roi_x = mouse_position.x() - self._main_text.x
                rect.roi_width = self._old_roi_width_rect + ((self._old_roi_x_rect + self._main_text.x) - mouse_position.x()) #rect.roi_width + (rect.roi_x + self._main_text.x - mouse_position.x())

                
                
                if rect.x < rect.roi_x + self._main_text.x:
                    rect.roi_x = rect.x - self._main_text.x - 1 #rect.roi_x +  self._main_text.x
                    rect.roi_width = self._old_roi_width_rect - (rect.x - (self._old_roi_x_rect + self._main_text.x))
                    
                """
                
                old_roi_x = rect.roi_x
                old_x = rect.x
                old_roi_width = rect.roi_width 
                old_width = rect.width
                
                
                rect.roi_x = mouse_position.x() - self._main_text.x
                rect.roi_width = self._old_roi_width_rect + ((self._old_roi_x_rect + self._main_text.x) - mouse_position.x()) #rect.roi_width + (rect.roi_x + self._main_text.x - mouse_position.x())

                
                
                if rect.x < rect.roi_x + self._main_text.x:
                    #rect.roi_x = rect.x - self._main_text.x - 1 #rect.roi_x +  self._main_text.x
                    #rect.roi_width = self._old_roi_width_rect - (rect.x - (self._old_roi_x_rect + self._main_text.x))
                    rect.x = (rect.roi_x + self._main_text.x)#+1
                    rect.width = rect.width - (rect.x - old_x)
                    

                if rect.width < int(4 * self.scaling_factor):
                    
                    rect.x = self._old_x_rect + self._old_width_rect - (4 * self.scaling_factor)
                    rect.width = (4 * self.scaling_factor)
                    rect.roi_x = rect.x - self._main_text.x# - 1
                    rect.roi_width = self._old_roi_width_rect - (rect.roi_x - self._old_roi_x_rect)
                    
                                
                x_offset =  old_x - rect.x
                
                if rect.x_offset is not None and rect.x_offset is not None:
                    rect.x_offset = rect.x_offset + x_offset

            if self.__border_index == 0:
                """
                old_y = rect.roi_y
                old_height = rect.roi_height 
                
                
                rect.roi_y = mouse_position.y()
                rect.roi_height =  (self._old_roi_y_rect - mouse_position.y()) + (self._old_roi_height_rect) #rect.roi_height + (rect.roi_y + 0 - mouse_position.y())

                
                
                if rect.y < rect.roi_y:
                    rect.roi_y = rect.y -1
                    rect.roi_height = self._old_roi_height_rect + (self._old_roi_y_rect - rect.y) + 1
                """
                    
                old_roi_y = rect.roi_y
                old_y = rect.y
                old_roi_height = rect.roi_height 
                old_height = rect.height
                
                
                rect.roi_y = mouse_position.y()
                rect.roi_height = (self._old_roi_y_rect - mouse_position.y()) + (self._old_roi_height_rect) #rect.roi_height + (rect.roi_y + self._main_text.y - mouse_position.y())

                
                
                if rect.y < rect.roi_y: #+ self._main_text.y:
                    rect.y = rect.roi_y
                    rect.height = rect.height - (rect.y - old_y)
                    

                if rect.height < int(4 * self.scaling_factor):
                    
                    rect.y = self._old_y_rect + self._old_height_rect - (4 * self.scaling_factor)
                    rect.height = (4 * self.scaling_factor)
                    rect.roi_y = rect.y #- self._main_text.y# - 1
                    rect.roi_height = self._old_roi_height_rect - (rect.roi_y - self._old_roi_y_rect)
                    
                                
                y_offset =  old_y - rect.y
                
                if rect.y_offset is not None and rect.y_offset is not None:
                    rect.y_offset = rect.y_offset + y_offset
                    
                for sub_image_finder in self._sub_texts_finder:
                    sub_image_finder.roi_y = sub_image_finder.roi_y + y_offset

            else:
                """
                old_y = rect.roi_y
                old_height = rect.roi_height 
                
                
                rect.roi_y = mouse_position.y() - self._main_text.y
                rect.roi_height = self._old_roi_height_rect + ((self._old_roi_y_rect + self._main_text.y) - mouse_position.y()) #rect.roi_height + (rect.roi_y + self._main_text.y - mouse_position.y())

                
                
                if rect.y < rect.roi_y + self._main_text.y:
                    rect.roi_y = rect.y - self._main_text.y - 1 #rect.roi_y +  self._main_text.y
                    rect.roi_height = self._old_roi_height_rect - (rect.y - (self._old_roi_y_rect + self._main_text.y))
                    
                """
                
                old_roi_y = rect.roi_y
                old_y = rect.y
                old_roi_height = rect.roi_height 
                old_height = rect.height
                
                
                rect.roi_y = mouse_position.y() - self._main_text.y
                rect.roi_height = self._old_roi_height_rect + ((self._old_roi_y_rect + self._main_text.y) - mouse_position.y()) #rect.roi_height + (rect.roi_y + self._main_text.y - mouse_position.y())

                
                
                if rect.y < rect.roi_y + self._main_text.y:
                    #rect.roi_y = rect.y - self._main_text.y - 1 #rect.roi_y +  self._main_text.y
                    #rect.roi_height = self._old_roi_height_rect - (rect.y - (self._old_roi_y_rect + self._main_text.y))
                    rect.y = (rect.roi_y + self._main_text.y)#+1
                    rect.height = rect.height - (rect.y - old_y)
                    

                if rect.height < int(4 * self.scaling_factor):
                    
                    rect.y = self._old_y_rect + self._old_height_rect - (4 * self.scaling_factor)
                    rect.height = (4 * self.scaling_factor)
                    rect.roi_y = rect.y - self._main_text.y# - 1
                    rect.roi_height = self._old_roi_height_rect - (rect.roi_y - self._old_roi_y_rect)
                    
                                
                y_offset =  old_y - rect.y
                
                if rect.y_offset is not None and rect.y_offset is not None:
                    rect.y_offset = rect.y_offset + y_offset                    
                    
                
        elif  self.__flag_mouse_is_on_right_up_corner_roi == True:
        
            mouse_position = QPoint(QCursor.pos())
            
            if self.__border_index == 0:

                """
                old_width = rect.roi_width 
                
                #rect.width = mouse_position.x() - rect.x
                
                rect.roi_width = mouse_position.x() - rect.roi_x
                #rect.roi_width = self._old_roi_width_rect + ((self._old_roi_x_rect + self._main_teyt.x) - mouse_position.x()) #rect.roi_width + (rect.roi_x + self._main_teyt.x - mouse_position.x())


                if rect.x + rect.width > rect.roi_x + rect.roi_width:
                    #rect.x = old_x #rect.roi_x +  self._main_teyt.x
                    rect.roi_width = ((rect.x + rect.width) - rect.roi_x) + 1
                """
                
                old_roi_x = rect.roi_x
                old_x = rect.x
                old_roi_width = rect.roi_width
                old_width = rect.width
                
                #rect.width = mouse_position.x() - rect.x
                
                rect.roi_width = mouse_position.x() - rect.roi_x
                #rect.roi_width = self._old_roi_width_rect + ((self._old_roi_x_rect + self._main_text.x) - mouse_position.x()) #rect.roi_width + (rect.roi_x + self._main_text.x - mouse_position.x())


                if rect.x + rect.width > rect.roi_x + rect.roi_width:
                    #rect.x = old_x #rect.roi_x +  self._main_text.x
                    rect.width = rect.roi_x + rect.roi_width - rect.x
                    #rect.roi_x + self._main_text.x + rect.roi_width - rect.x
                    
                if rect.width < int(4 * self.scaling_factor):
                    
                    #rect.x = self._old_x_rect + self._old_width_rect - (4 * self.scaling_factor)
                    rect.width = (4 * self.scaling_factor)
                    #rect.roi_x = rect.x - self._main_text.x# - 1
                    rect.roi_width = (rect.x + rect.width) - (rect.roi_x)

            else:

            
                old_roi_x = rect.roi_x
                old_x = rect.x
                old_roi_width = rect.roi_width
                old_width = rect.width
                
                #rect.width = mouse_position.x() - rect.x
                
                rect.roi_width = mouse_position.x() - (rect.roi_x + self._main_text.x)
                #rect.roi_width = self._old_roi_width_rect + ((self._old_roi_x_rect + self._main_text.x) - mouse_position.x()) #rect.roi_width + (rect.roi_x + self._main_text.x - mouse_position.x())


                if rect.x + rect.width > rect.roi_x + self._main_text.x + rect.roi_width:
                    #rect.x = old_x #rect.roi_x +  self._main_text.x
                    rect.width = rect.roi_x + self._main_text.x + rect.roi_width - rect.x
                    
                if rect.width < int(4 * self.scaling_factor):
                    
                    #rect.x = self._old_x_rect + self._old_width_rect - (4 * self.scaling_factor)
                    rect.width = (4 * self.scaling_factor)
                    #rect.roi_x = rect.x - self._main_text.x# - 1
                    rect.roi_width = (rect.x + rect.width) - (rect.roi_x + self._main_text.x)

            if self.__border_index == 0:
                """
                old_y = rect.roi_y
                old_height = rect.roi_height 
                
                
                rect.roi_y = mouse_position.y()
                rect.roi_height =  (self._old_roi_y_rect - mouse_position.y()) + (self._old_roi_height_rect) #rect.roi_height + (rect.roi_y + 0 - mouse_position.y())

                
                
                if rect.y < rect.roi_y:
                    rect.roi_y = rect.y -1
                    rect.roi_height = self._old_roi_height_rect + (self._old_roi_y_rect - rect.y) + 1
                """
                    
                old_roi_y = rect.roi_y
                old_y = rect.y
                old_roi_height = rect.roi_height 
                old_height = rect.height
                
                
                rect.roi_y = mouse_position.y()
                rect.roi_height = (self._old_roi_y_rect - mouse_position.y()) + (self._old_roi_height_rect) #rect.roi_height + (rect.roi_y + self._main_text.y - mouse_position.y())

                
                
                if rect.y < rect.roi_y: #+ self._main_text.y:
                    rect.y = rect.roi_y
                    rect.height = rect.height - (rect.y - old_y)
                    

                if rect.height < int(4 * self.scaling_factor):
                    
                    rect.y = self._old_y_rect + self._old_height_rect - (4 * self.scaling_factor)
                    rect.height = (4 * self.scaling_factor)
                    rect.roi_y = rect.y #- self._main_text.y# - 1
                    rect.roi_height = self._old_roi_height_rect - (rect.roi_y - self._old_roi_y_rect)
                    
                                
                y_offset =  old_y - rect.y
                
                if rect.y_offset is not None and rect.y_offset is not None:
                    rect.y_offset = rect.y_offset + y_offset
                    
                for sub_image_finder in self._sub_texts_finder:
                    sub_image_finder.roi_y = sub_image_finder.roi_y + y_offset

            else:
                """
                old_y = rect.roi_y
                old_height = rect.roi_height 
                
                
                rect.roi_y = mouse_position.y() - self._main_text.y
                rect.roi_height = self._old_roi_height_rect + ((self._old_roi_y_rect + self._main_text.y) - mouse_position.y()) #rect.roi_height + (rect.roi_y + self._main_text.y - mouse_position.y())

                
                
                if rect.y < rect.roi_y + self._main_text.y:
                    rect.roi_y = rect.y - self._main_text.y - 1 #rect.roi_y +  self._main_text.y
                    rect.roi_height = self._old_roi_height_rect - (rect.y - (self._old_roi_y_rect + self._main_text.y))
                    
                """
                
                old_roi_y = rect.roi_y
                old_y = rect.y
                old_roi_height = rect.roi_height 
                old_height = rect.height
                
                
                rect.roi_y = mouse_position.y() - self._main_text.y
                rect.roi_height = self._old_roi_height_rect + ((self._old_roi_y_rect + self._main_text.y) - mouse_position.y()) #rect.roi_height + (rect.roi_y + self._main_text.y - mouse_position.y())

                
                
                if rect.y < rect.roi_y + self._main_text.y:
                    #rect.roi_y = rect.y - self._main_text.y - 1 #rect.roi_y +  self._main_text.y
                    #rect.roi_height = self._old_roi_height_rect - (rect.y - (self._old_roi_y_rect + self._main_text.y))
                    rect.y = (rect.roi_y + self._main_text.y)#+1
                    rect.height = rect.height - (rect.y - old_y)
                    

                if rect.height < int(4 * self.scaling_factor):
                    
                    rect.y = self._old_y_rect + self._old_height_rect - (4 * self.scaling_factor)
                    rect.height = (4 * self.scaling_factor)
                    rect.roi_y = rect.y - self._main_text.y# - 1
                    rect.roi_height = self._old_roi_height_rect - (rect.roi_y - self._old_roi_y_rect)
                    
                                
                y_offset =  old_y - rect.y
                
                if rect.y_offset is not None and rect.y_offset is not None:
                    rect.y_offset = rect.y_offset + y_offset
                
        elif  self.__flag_mouse_is_on_right_bottom_corner_roi == True:
        
            mouse_position = QPoint(QCursor.pos())
            
                    
            if self.__border_index == 0:

                """
                old_width = rect.roi_width 
                
                #rect.width = mouse_position.x() - rect.x
                
                rect.roi_width = mouse_position.x() - rect.roi_x
                #rect.roi_width = self._old_roi_width_rect + ((self._old_roi_x_rect + self._main_teyt.x) - mouse_position.x()) #rect.roi_width + (rect.roi_x + self._main_teyt.x - mouse_position.x())


                if rect.x + rect.width > rect.roi_x + rect.roi_width:
                    #rect.x = old_x #rect.roi_x +  self._main_teyt.x
                    rect.roi_width = ((rect.x + rect.width) - rect.roi_x) + 1
                """
                
                old_roi_x = rect.roi_x
                old_x = rect.x
                old_roi_width = rect.roi_width
                old_width = rect.width
                
                #rect.width = mouse_position.x() - rect.x
                
                rect.roi_width = mouse_position.x() - rect.roi_x
                #rect.roi_width = self._old_roi_width_rect + ((self._old_roi_x_rect + self._main_text.x) - mouse_position.x()) #rect.roi_width + (rect.roi_x + self._main_text.x - mouse_position.x())


                if rect.x + rect.width > rect.roi_x + rect.roi_width:
                    #rect.x = old_x #rect.roi_x +  self._main_text.x
                    rect.width = rect.roi_x + rect.roi_width - rect.x
                    #rect.roi_x + self._main_text.x + rect.roi_width - rect.x
                    
                if rect.width < int(4 * self.scaling_factor):
                    
                    #rect.x = self._old_x_rect + self._old_width_rect - (4 * self.scaling_factor)
                    rect.width = (4 * self.scaling_factor)
                    #rect.roi_x = rect.x - self._main_text.x# - 1
                    rect.roi_width = (rect.x + rect.width) - (rect.roi_x)

            else:

            
                old_roi_x = rect.roi_x
                old_x = rect.x
                old_roi_width = rect.roi_width
                old_width = rect.width
                
                #rect.width = mouse_position.x() - rect.x
                
                rect.roi_width = mouse_position.x() - (rect.roi_x + self._main_text.x)
                #rect.roi_width = self._old_roi_width_rect + ((self._old_roi_x_rect + self._main_text.x) - mouse_position.x()) #rect.roi_width + (rect.roi_x + self._main_text.x - mouse_position.x())


                if rect.x + rect.width > rect.roi_x + self._main_text.x + rect.roi_width:
                    #rect.x = old_x #rect.roi_x +  self._main_text.x
                    rect.width = rect.roi_x + self._main_text.x + rect.roi_width - rect.x
                    
                if rect.width < int(4 * self.scaling_factor):
                    
                    #rect.x = self._old_x_rect + self._old_width_rect - (4 * self.scaling_factor)
                    rect.width = (4 * self.scaling_factor)
                    #rect.roi_x = rect.x - self._main_text.x# - 1
                    rect.roi_width = (rect.x + rect.width) - (rect.roi_x + self._main_text.x)
                    
            
            if self.__border_index == 0:

                """
                old_height = rect.roi_height 
                
                #rect.height = mouse_position.y() - rect.y
                
                rect.roi_height = mouse_position.y() - rect.roi_y
                #rect.roi_height = self._old_roi_height_rect + ((self._old_roi_y_rect + self._main_teyt.y) - mouse_position.y()) #rect.roi_height + (rect.roi_y + self._main_teyt.y - mouse_position.y())


                if rect.y + rect.height > rect.roi_y + rect.roi_height:
                    #rect.y = old_y #rect.roi_y +  self._main_teyt.y
                    rect.roi_height = ((rect.y + rect.height) - rect.roi_y) + 1
                """
                
                old_roi_y = rect.roi_y
                old_y = rect.y
                old_roi_height = rect.roi_height
                old_height = rect.height
                
                #rect.height = mouse_position.y() - rect.y
                
                rect.roi_height = mouse_position.y() - rect.roi_y
                #rect.roi_height = self._old_roi_height_rect + ((self._old_roi_y_rect + self._main_text.y) - mouse_position.y()) #rect.roi_height + (rect.roi_y + self._main_text.y - mouse_position.y())


                if rect.y + rect.height > rect.roi_y + rect.roi_height:
                    #rect.y = old_y #rect.roi_y +  self._main_text.y
                    rect.height = rect.roi_y + rect.roi_height - rect.y
                    #rect.roi_y + self._main_text.y + rect.roi_height - rect.y
                    
                if rect.height < int(4 * self.scaling_factor):
                    
                    #rect.y = self._old_y_rect + self._old_height_rect - (4 * self.scaling_factor)
                    rect.height = (4 * self.scaling_factor)
                    #rect.roi_y = rect.y - self._main_text.y# - 1
                    rect.roi_height = (rect.y + rect.height) - (rect.roi_y)

            else:

            
                old_roi_y = rect.roi_y
                old_y = rect.y
                old_roi_height = rect.roi_height
                old_height = rect.height
                
                #rect.height = mouse_position.y() - rect.y
                
                rect.roi_height = mouse_position.y() - (rect.roi_y + self._main_text.y)
                #rect.roi_height = self._old_roi_height_rect + ((self._old_roi_y_rect + self._main_text.y) - mouse_position.y()) #rect.roi_height + (rect.roi_y + self._main_text.y - mouse_position.y())


                if rect.y + rect.height > rect.roi_y + self._main_text.y + rect.roi_height:
                    #rect.y = old_y #rect.roi_y +  self._main_text.y
                    rect.height = rect.roi_y + self._main_text.y + rect.roi_height - rect.y
                    
                if rect.height < int(4 * self.scaling_factor):
                    
                    #rect.y = self._old_y_rect + self._old_height_rect - (4 * self.scaling_factor)
                    rect.height = (4 * self.scaling_factor)
                    #rect.roi_y = rect.y - self._main_text.y# - 1
                    rect.roi_height = (rect.y + rect.height) - (rect.roi_y + self._main_text.y)
                
        elif  self.__flag_mouse_is_on_left_bottom_corner_roi == True:
            mouse_position = QPoint(QCursor.pos())
            
            if self.__border_index == 0:
                """
                old_x = rect.roi_x
                old_width = rect.roi_width 
                
                
                rect.roi_x = mouse_position.x()
                rect.roi_width =  (self._old_roi_x_rect - mouse_position.x()) + (self._old_roi_width_rect) #rect.roi_width + (rect.roi_x + 0 - mouse_position.x())

                
                
                if rect.x < rect.roi_x:
                    rect.roi_x = rect.x -1
                    rect.roi_width = self._old_roi_width_rect + (self._old_roi_x_rect - rect.x) + 1
                """
                    
                old_roi_x = rect.roi_x
                old_x = rect.x
                old_roi_width = rect.roi_width 
                old_width = rect.width
                
                
                rect.roi_x = mouse_position.x()
                rect.roi_width = (self._old_roi_x_rect - mouse_position.x()) + (self._old_roi_width_rect) #rect.roi_width + (rect.roi_x + self._main_text.x - mouse_position.x())

                
                
                if rect.x < rect.roi_x: #+ self._main_text.x:
                    rect.x = rect.roi_x
                    rect.width = rect.width - (rect.x - old_x)
                    

                if rect.width < int(4 * self.scaling_factor):
                    
                    rect.x = self._old_x_rect + self._old_width_rect - (4 * self.scaling_factor)
                    rect.width = (4 * self.scaling_factor)
                    rect.roi_x = rect.x #- self._main_text.x# - 1
                    rect.roi_width = self._old_roi_width_rect - (rect.roi_x - self._old_roi_x_rect)
                    
                                
                x_offset =  old_x - rect.x
                
                if rect.x_offset is not None and rect.x_offset is not None:
                    rect.x_offset = rect.x_offset + x_offset
                    
                for sub_image_finder in self._sub_texts_finder:
                    sub_image_finder.roi_x = sub_image_finder.roi_x + x_offset

            else:
                """
                old_x = rect.roi_x
                old_width = rect.roi_width 
                
                
                rect.roi_x = mouse_position.x() - self._main_text.x
                rect.roi_width = self._old_roi_width_rect + ((self._old_roi_x_rect + self._main_text.x) - mouse_position.x()) #rect.roi_width + (rect.roi_x + self._main_text.x - mouse_position.x())

                
                
                if rect.x < rect.roi_x + self._main_text.x:
                    rect.roi_x = rect.x - self._main_text.x - 1 #rect.roi_x +  self._main_text.x
                    rect.roi_width = self._old_roi_width_rect - (rect.x - (self._old_roi_x_rect + self._main_text.x))
                    
                """
                
                old_roi_x = rect.roi_x
                old_x = rect.x
                old_roi_width = rect.roi_width 
                old_width = rect.width
                
                
                rect.roi_x = mouse_position.x() - self._main_text.x
                rect.roi_width = self._old_roi_width_rect + ((self._old_roi_x_rect + self._main_text.x) - mouse_position.x()) #rect.roi_width + (rect.roi_x + self._main_text.x - mouse_position.x())

                
                
                if rect.x < rect.roi_x + self._main_text.x:
                    #rect.roi_x = rect.x - self._main_text.x - 1 #rect.roi_x +  self._main_text.x
                    #rect.roi_width = self._old_roi_width_rect - (rect.x - (self._old_roi_x_rect + self._main_text.x))
                    rect.x = (rect.roi_x + self._main_text.x)#+1
                    rect.width = rect.width - (rect.x - old_x)
                    

                if rect.width < int(4 * self.scaling_factor):
                    
                    rect.x = self._old_x_rect + self._old_width_rect - (4 * self.scaling_factor)
                    rect.width = (4 * self.scaling_factor)
                    rect.roi_x = rect.x - self._main_text.x# - 1
                    rect.roi_width = self._old_roi_width_rect - (rect.roi_x - self._old_roi_x_rect)
                    
                                
                x_offset =  old_x - rect.x
                
                if rect.x_offset is not None and rect.x_offset is not None:
                    rect.x_offset = rect.x_offset + x_offset
                
            if self.__border_index == 0:

                """
                old_height = rect.roi_height 
                
                #rect.height = mouse_position.y() - rect.y
                
                rect.roi_height = mouse_position.y() - rect.roi_y
                #rect.roi_height = self._old_roi_height_rect + ((self._old_roi_y_rect + self._main_teyt.y) - mouse_position.y()) #rect.roi_height + (rect.roi_y + self._main_teyt.y - mouse_position.y())


                if rect.y + rect.height > rect.roi_y + rect.roi_height:
                    #rect.y = old_y #rect.roi_y +  self._main_teyt.y
                    rect.roi_height = ((rect.y + rect.height) - rect.roi_y) + 1
                """
                
                old_roi_y = rect.roi_y
                old_y = rect.y
                old_roi_height = rect.roi_height
                old_height = rect.height
                
                #rect.height = mouse_position.y() - rect.y
                
                rect.roi_height = mouse_position.y() - rect.roi_y
                #rect.roi_height = self._old_roi_height_rect + ((self._old_roi_y_rect + self._main_text.y) - mouse_position.y()) #rect.roi_height + (rect.roi_y + self._main_text.y - mouse_position.y())


                if rect.y + rect.height > rect.roi_y + rect.roi_height:
                    #rect.y = old_y #rect.roi_y +  self._main_text.y
                    rect.height = rect.roi_y + rect.roi_height - rect.y
                    #rect.roi_y + self._main_text.y + rect.roi_height - rect.y
                    
                if rect.height < int(4 * self.scaling_factor):
                    
                    #rect.y = self._old_y_rect + self._old_height_rect - (4 * self.scaling_factor)
                    rect.height = (4 * self.scaling_factor)
                    #rect.roi_y = rect.y - self._main_text.y# - 1
                    rect.roi_height = (rect.y + rect.height) - (rect.roi_y)

            else:

            
                old_roi_y = rect.roi_y
                old_y = rect.y
                old_roi_height = rect.roi_height
                old_height = rect.height
                
                #rect.height = mouse_position.y() - rect.y
                
                rect.roi_height = mouse_position.y() - (rect.roi_y + self._main_text.y)
                #rect.roi_height = self._old_roi_height_rect + ((self._old_roi_y_rect + self._main_text.y) - mouse_position.y()) #rect.roi_height + (rect.roi_y + self._main_text.y - mouse_position.y())


                if rect.y + rect.height > rect.roi_y + self._main_text.y + rect.roi_height:
                    #rect.y = old_y #rect.roi_y +  self._main_text.y
                    rect.height = rect.roi_y + self._main_text.y + rect.roi_height - rect.y
                    
                if rect.height < int(4 * self.scaling_factor):
                    
                    #rect.y = self._old_y_rect + self._old_height_rect - (4 * self.scaling_factor)
                    rect.height = (4 * self.scaling_factor)
                    #rect.roi_y = rect.y - self._main_text.y# - 1
                    rect.roi_height = (rect.y + rect.height) - (rect.roi_y + self._main_text.y)
        
        elif self.__flag_mouse_is_on_left_border_roi is True:
        
            mouse_position = QPoint(QCursor.pos())
            
            if self.__border_index == 0:
                """
                old_x = rect.roi_x
                old_width = rect.roi_width 
                
                
                rect.roi_x = mouse_position.x()
                rect.roi_width =  (self._old_roi_x_rect - mouse_position.x()) + (self._old_roi_width_rect) #rect.roi_width + (rect.roi_x + 0 - mouse_position.x())

                
                
                if rect.x < rect.roi_x:
                    rect.roi_x = rect.x -1
                    rect.roi_width = self._old_roi_width_rect + (self._old_roi_x_rect - rect.x) + 1
                """
                    
                old_roi_x = rect.roi_x
                old_x = rect.x
                old_roi_width = rect.roi_width 
                old_width = rect.width
                
                
                rect.roi_x = mouse_position.x()
                rect.roi_width = (self._old_roi_x_rect - mouse_position.x()) + (self._old_roi_width_rect) #rect.roi_width + (rect.roi_x + self._main_text.x - mouse_position.x())

                
                
                if rect.x < rect.roi_x: #+ self._main_text.x:
                    rect.x = rect.roi_x
                    rect.width = rect.width - (rect.x - old_x)
                    

                if rect.width < int(4 * self.scaling_factor):
                    
                    rect.x = self._old_x_rect + self._old_width_rect - (4 * self.scaling_factor)
                    rect.width = (4 * self.scaling_factor)
                    rect.roi_x = rect.x #- self._main_text.x# - 1
                    rect.roi_width = self._old_roi_width_rect - (rect.roi_x - self._old_roi_x_rect)
                    
                                
                x_offset =  old_x - rect.x
                
                if rect.x_offset is not None and rect.x_offset is not None:
                    rect.x_offset = rect.x_offset + x_offset
                    
                for sub_image_finder in self._sub_texts_finder:
                    sub_image_finder.roi_x = sub_image_finder.roi_x + x_offset

            else:
                """
                old_x = rect.roi_x
                old_width = rect.roi_width 
                
                
                rect.roi_x = mouse_position.x() - self._main_text.x
                rect.roi_width = self._old_roi_width_rect + ((self._old_roi_x_rect + self._main_text.x) - mouse_position.x()) #rect.roi_width + (rect.roi_x + self._main_text.x - mouse_position.x())

                
                
                if rect.x < rect.roi_x + self._main_text.x:
                    rect.roi_x = rect.x - self._main_text.x - 1 #rect.roi_x +  self._main_text.x
                    rect.roi_width = self._old_roi_width_rect - (rect.x - (self._old_roi_x_rect + self._main_text.x))
                    
                """
                
                old_roi_x = rect.roi_x
                old_x = rect.x
                old_roi_width = rect.roi_width 
                old_width = rect.width
                
                
                rect.roi_x = mouse_position.x() - self._main_text.x
                rect.roi_width = self._old_roi_width_rect + ((self._old_roi_x_rect + self._main_text.x) - mouse_position.x()) #rect.roi_width + (rect.roi_x + self._main_text.x - mouse_position.x())

                
                
                if rect.x < rect.roi_x + self._main_text.x:
                    #rect.roi_x = rect.x - self._main_text.x - 1 #rect.roi_x +  self._main_text.x
                    #rect.roi_width = self._old_roi_width_rect - (rect.x - (self._old_roi_x_rect + self._main_text.x))
                    rect.x = (rect.roi_x + self._main_text.x)#+1
                    rect.width = rect.width - (rect.x - old_x)
                    

                if rect.width < int(4 * self.scaling_factor):
                    
                    rect.x = self._old_x_rect + self._old_width_rect - (4 * self.scaling_factor)
                    rect.width = (4 * self.scaling_factor)
                    rect.roi_x = rect.x - self._main_text.x# - 1
                    rect.roi_width = self._old_roi_width_rect - (rect.roi_x - self._old_roi_x_rect)
                    
                                
                x_offset =  old_x - rect.x
                
                if rect.x_offset is not None and rect.x_offset is not None:
                    rect.x_offset = rect.x_offset + x_offset
                    
        elif self.__flag_mouse_is_on_top_border_roi is True:
        
            mouse_position = QPoint(QCursor.pos())
            
            if self.__border_index == 0:
                """
                old_y = rect.roi_y
                old_height = rect.roi_height 
                
                
                rect.roi_y = mouse_position.y()
                rect.roi_height =  (self._old_roi_y_rect - mouse_position.y()) + (self._old_roi_height_rect) #rect.roi_height + (rect.roi_y + 0 - mouse_position.y())

                
                
                if rect.y < rect.roi_y:
                    rect.roi_y = rect.y -1
                    rect.roi_height = self._old_roi_height_rect + (self._old_roi_y_rect - rect.y) + 1
                """
                    
                old_roi_y = rect.roi_y
                old_y = rect.y
                old_roi_height = rect.roi_height 
                old_height = rect.height
                
                
                rect.roi_y = mouse_position.y()
                rect.roi_height = (self._old_roi_y_rect - mouse_position.y()) + (self._old_roi_height_rect) #rect.roi_height + (rect.roi_y + self._main_text.y - mouse_position.y())

                
                
                if rect.y < rect.roi_y: #+ self._main_text.y:
                    rect.y = rect.roi_y
                    rect.height = rect.height - (rect.y - old_y)
                    

                if rect.height < int(4 * self.scaling_factor):
                    
                    rect.y = self._old_y_rect + self._old_height_rect - (4 * self.scaling_factor)
                    rect.height = (4 * self.scaling_factor)
                    rect.roi_y = rect.y #- self._main_text.y# - 1
                    rect.roi_height = self._old_roi_height_rect - (rect.roi_y - self._old_roi_y_rect)
                    
                                
                y_offset =  old_y - rect.y
                
                if rect.y_offset is not None and rect.y_offset is not None:
                    rect.y_offset = rect.y_offset + y_offset
                    
                for sub_image_finder in self._sub_texts_finder:
                    sub_image_finder.roi_y = sub_image_finder.roi_y + y_offset

            else:
                """
                old_y = rect.roi_y
                old_height = rect.roi_height 
                
                
                rect.roi_y = mouse_position.y() - self._main_text.y
                rect.roi_height = self._old_roi_height_rect + ((self._old_roi_y_rect + self._main_text.y) - mouse_position.y()) #rect.roi_height + (rect.roi_y + self._main_text.y - mouse_position.y())

                
                
                if rect.y < rect.roi_y + self._main_text.y:
                    rect.roi_y = rect.y - self._main_text.y - 1 #rect.roi_y +  self._main_text.y
                    rect.roi_height = self._old_roi_height_rect - (rect.y - (self._old_roi_y_rect + self._main_text.y))
                    
                """
                
                old_roi_y = rect.roi_y
                old_y = rect.y
                old_roi_height = rect.roi_height 
                old_height = rect.height
                
                
                rect.roi_y = mouse_position.y() - self._main_text.y
                rect.roi_height = self._old_roi_height_rect + ((self._old_roi_y_rect + self._main_text.y) - mouse_position.y()) #rect.roi_height + (rect.roi_y + self._main_text.y - mouse_position.y())

                
                
                if rect.y < rect.roi_y + self._main_text.y:
                    #rect.roi_y = rect.y - self._main_text.y - 1 #rect.roi_y +  self._main_text.y
                    #rect.roi_height = self._old_roi_height_rect - (rect.y - (self._old_roi_y_rect + self._main_text.y))
                    rect.y = (rect.roi_y + self._main_text.y)#+1
                    rect.height = rect.height - (rect.y - old_y)
                    

                if rect.height < int(4 * self.scaling_factor):
                    
                    rect.y = self._old_y_rect + self._old_height_rect - (4 * self.scaling_factor)
                    rect.height = (4 * self.scaling_factor)
                    rect.roi_y = rect.y - self._main_text.y# - 1
                    rect.roi_height = self._old_roi_height_rect - (rect.roi_y - self._old_roi_y_rect)
                    
                                
                y_offset =  old_y - rect.y
                
                if rect.y_offset is not None and rect.y_offset is not None:
                    rect.y_offset = rect.y_offset + y_offset
                
        elif self.__flag_mouse_is_on_bottom_border_roi is True:
        
            mouse_position = QPoint(QCursor.pos())

            if self.__border_index == 0:

                """
                old_height = rect.roi_height 
                
                #rect.height = mouse_position.y() - rect.y
                
                rect.roi_height = mouse_position.y() - rect.roi_y
                #rect.roi_height = self._old_roi_height_rect + ((self._old_roi_y_rect + self._main_teyt.y) - mouse_position.y()) #rect.roi_height + (rect.roi_y + self._main_teyt.y - mouse_position.y())


                if rect.y + rect.height > rect.roi_y + rect.roi_height:
                    #rect.y = old_y #rect.roi_y +  self._main_teyt.y
                    rect.roi_height = ((rect.y + rect.height) - rect.roi_y) + 1
                """
                
                old_roi_y = rect.roi_y
                old_y = rect.y
                old_roi_height = rect.roi_height
                old_height = rect.height
                
                #rect.height = mouse_position.y() - rect.y
                
                rect.roi_height = mouse_position.y() - rect.roi_y
                #rect.roi_height = self._old_roi_height_rect + ((self._old_roi_y_rect + self._main_text.y) - mouse_position.y()) #rect.roi_height + (rect.roi_y + self._main_text.y - mouse_position.y())


                if rect.y + rect.height > rect.roi_y + rect.roi_height:
                    #rect.y = old_y #rect.roi_y +  self._main_text.y
                    rect.height = rect.roi_y + rect.roi_height - rect.y
                    #rect.roi_y + self._main_text.y + rect.roi_height - rect.y
                    
                if rect.height < int(4 * self.scaling_factor):
                    
                    #rect.y = self._old_y_rect + self._old_height_rect - (4 * self.scaling_factor)
                    rect.height = (4 * self.scaling_factor)
                    #rect.roi_y = rect.y - self._main_text.y# - 1
                    rect.roi_height = (rect.y + rect.height) - (rect.roi_y)

            else:

            
                old_roi_y = rect.roi_y
                old_y = rect.y
                old_roi_height = rect.roi_height
                old_height = rect.height
                
                #rect.height = mouse_position.y() - rect.y
                
                rect.roi_height = mouse_position.y() - (rect.roi_y + self._main_text.y)
                #rect.roi_height = self._old_roi_height_rect + ((self._old_roi_y_rect + self._main_text.y) - mouse_position.y()) #rect.roi_height + (rect.roi_y + self._main_text.y - mouse_position.y())


                if rect.y + rect.height > rect.roi_y + self._main_text.y + rect.roi_height:
                    #rect.y = old_y #rect.roi_y +  self._main_text.y
                    rect.height = rect.roi_y + self._main_text.y + rect.roi_height - rect.y
                    
                if rect.height < int(4 * self.scaling_factor):
                    
                    #rect.y = self._old_y_rect + self._old_height_rect - (4 * self.scaling_factor)
                    rect.height = (4 * self.scaling_factor)
                    #rect.roi_y = rect.y - self._main_text.y# - 1
                    rect.roi_height = (rect.y + rect.height) - (rect.roi_y + self._main_text.y)

            #print rect.x
        elif self.__flag_mouse_is_on_right_border_roi is True:
        
            mouse_position = QPoint(QCursor.pos())
        
            if self.__border_index == 0:

                """
                old_width = rect.roi_width 
                
                #rect.width = mouse_position.x() - rect.x
                
                rect.roi_width = mouse_position.x() - rect.roi_x
                #rect.roi_width = self._old_roi_width_rect + ((self._old_roi_x_rect + self._main_teyt.x) - mouse_position.x()) #rect.roi_width + (rect.roi_x + self._main_teyt.x - mouse_position.x())


                if rect.x + rect.width > rect.roi_x + rect.roi_width:
                    #rect.x = old_x #rect.roi_x +  self._main_teyt.x
                    rect.roi_width = ((rect.x + rect.width) - rect.roi_x) + 1
                """
                
                old_roi_x = rect.roi_x
                old_x = rect.x
                old_roi_width = rect.roi_width
                old_width = rect.width
                
                #rect.width = mouse_position.x() - rect.x
                
                rect.roi_width = mouse_position.x() - rect.roi_x
                #rect.roi_width = self._old_roi_width_rect + ((self._old_roi_x_rect + self._main_text.x) - mouse_position.x()) #rect.roi_width + (rect.roi_x + self._main_text.x - mouse_position.x())


                if rect.x + rect.width > rect.roi_x + rect.roi_width:
                    #rect.x = old_x #rect.roi_x +  self._main_text.x
                    rect.width = rect.roi_x + rect.roi_width - rect.x
                    #rect.roi_x + self._main_text.x + rect.roi_width - rect.x
                    
                if rect.width < int(4 * self.scaling_factor):
                    
                    #rect.x = self._old_x_rect + self._old_width_rect - (4 * self.scaling_factor)
                    rect.width = (4 * self.scaling_factor)
                    #rect.roi_x = rect.x - self._main_text.x# - 1
                    rect.roi_width = (rect.x + rect.width) - (rect.roi_x)

            else:

            
                old_roi_x = rect.roi_x
                old_x = rect.x
                old_roi_width = rect.roi_width
                old_width = rect.width
                
                #rect.width = mouse_position.x() - rect.x
                
                rect.roi_width = mouse_position.x() - (rect.roi_x + self._main_text.x)
                #rect.roi_width = self._old_roi_width_rect + ((self._old_roi_x_rect + self._main_text.x) - mouse_position.x()) #rect.roi_width + (rect.roi_x + self._main_text.x - mouse_position.x())


                if rect.x + rect.width > rect.roi_x + self._main_text.x + rect.roi_width:
                    #rect.x = old_x #rect.roi_x +  self._main_text.x
                    rect.width = rect.roi_x + self._main_text.x + rect.roi_width - rect.x
                    
                if rect.width < int(4 * self.scaling_factor):
                    
                    #rect.x = self._old_x_rect + self._old_width_rect - (4 * self.scaling_factor)
                    rect.width = (4 * self.scaling_factor)
                    #rect.roi_x = rect.x - self._main_text.x# - 1
                    rect.roi_width = (rect.x + rect.width) - (rect.roi_x + self._main_text.x)

        elif  self.__flag_mouse_is_on_left_up_corner is True:
        
                                
            mouse_position = QPoint(QCursor.pos())
            
            if self.__border_index == 0:

                old_x = rect.x
                
                #rect.width = rect.width + (rect.x - mouse_position.x())
                #rect.x = mouse_position.x()

                                        
                rect.x = mouse_position.x()
                rect.width = self._old_width_rect + (self._old_x_rect - mouse_position.x()) 
                
                
                if rect.x < 1:
                    rect.x = 1
            
                if  mouse_position.x() < (rect.roi_x):
                    rect.roi_width = rect.roi_width + (rect.roi_x - rect.x)
                    rect.roi_x = rect.roi_x - (rect.roi_x - rect.x)
                    """
                    if rect.roi_unlimited_left:
                        rect.roi_width = rect.roi_width + (rect.roi_x - rect.x)
                        rect.roi_x = rect.roi_x - (rect.roi_x - rect.x)
                    else:
                        rect.x = rect.roi_x + 1
                        rect.width = self._old_width_rect + (self._old_x_rect - rect.roi_x) 
                        
                        #rect.roi_width = rect.roi_width + (rect.roi_x - rect.x)
                        #rect.roi_x = rect.roi_x - (rect.roi_x - rect.x)
                    """
                        
                
                if rect.width < int(4 * self.scaling_factor):
                    rect.width = int(4 * self.scaling_factor)
                    rect.x = self._old_x_rect + self._old_width_rect - int(4 * self.scaling_factor)
                     
                x_offset =  old_x - rect.x

                                        
                if rect.x_offset is not None and rect.y_offset is not None:
                    rect.x_offset = rect.x_offset + x_offset
                
                #print x_offset
                            
                if self.__border_index == 0:
                    for sub_image_finder in self._sub_texts_finder:
                        sub_image_finder.roi_x = sub_image_finder.roi_x + x_offset
            else:
                old_x = rect.x
                
                #rect.width = rect.width + (rect.x - mouse_position.x())
                #rect.x = mouse_position.x()

                                        
                rect.x = mouse_position.x()
                rect.width = self._old_width_rect + (self._old_x_rect - mouse_position.x()) 
                
                
                if rect.x < 1:
                    rect.x = 1
                
                if self.__border_index != 0:
                    if  mouse_position.x() < (rect.roi_x +  self._main_text.x):
                        rect.roi_width = rect.roi_width + ((rect.roi_x + self._main_text.x) - rect.x)
                        rect.roi_x = rect.roi_x - ((rect.roi_x + self._main_text.x) - rect.x)
                        """
                        if rect.roi_unlimited_left:
                            rect.roi_width = rect.roi_width + ((rect.roi_x + self._main_text.x) - rect.x)
                            rect.roi_x = rect.roi_x - ((rect.roi_x + self._main_text.x) - rect.x)
                        else:
                            rect.x = rect.roi_x +  self._main_text.x + 1
                            rect.width = self._old_width_rect + (self._old_x_rect - (rect.roi_x +  self._main_text.x)) 
                            
                            #rect.roi_width = rect.roi_width + ((rect.roi_x + self._main_text.x) - rect.x)
                            #rect.roi_x = rect.roi_x - ((rect.roi_x + self._main_text.x) - rect.x)
                        """    
                
                if rect.width < int(4 * self.scaling_factor):
                    rect.width = int(4 * self.scaling_factor)
                    rect.x = self._old_x_rect + self._old_width_rect - int(4 * self.scaling_factor)
                     
                x_offset =  old_x - rect.x

                                        
                if rect.x_offset is not None and rect.y_offset is not None:
                    rect.x_offset = rect.x_offset + x_offset
                
                #print x_offset
                            
                if self.__border_index == 0:
                    for sub_image_finder in self._sub_texts_finder:
                        sub_image_finder.roi_x = sub_image_finder.roi_x + x_offset


            if self.__border_index == 0:

                old_y = rect.y
                
                #rect.height = rect.height + (rect.y - mouse_position.y())
                #rect.y = mouse_position.y()

                                        
                rect.y = mouse_position.y()
                rect.height = self._old_height_rect + (self._old_y_rect - mouse_position.y()) 
                
                
                if rect.y < 1:
                    rect.y = 1
            
                if  mouse_position.y() < (rect.roi_y):

                    rect.roi_height = rect.roi_height + (rect.roi_y - rect.y)
                    rect.roi_y = rect.roi_y - (rect.roi_y - rect.y)
                    """
                    if rect.roi_unlimited_left:
                        rect.roi_height = rect.roi_height + (rect.roi_y - rect.y)
                        rect.roi_y = rect.roi_y - (rect.roi_y - rect.y)
                    else:
                        rect.y = rect.roi_y + 1
                        rect.height = self._old_height_rect + (self._old_y_rect - rect.roi_y) 
                        
                        #rect.roi_height = rect.roi_height + (rect.roi_y - rect.y)
                        #rect.roi_y = rect.roi_y - (rect.roi_y - rect.y)
                    """
                
                if rect.height < int(4 * self.scaling_factor):
                    rect.height = int(4 * self.scaling_factor)
                    rect.y = self._old_y_rect + self._old_height_rect - int(4 * self.scaling_factor)
                     
                y_offset =  old_y - rect.y

                                        
                if rect.y_offset is not None and rect.y_offset is not None:
                    rect.y_offset = rect.y_offset + y_offset
                
                #print y_offset
                            
                if self.__border_index == 0:
                    for sub_image_finder in self._sub_texts_finder:
                        sub_image_finder.roi_y = sub_image_finder.roi_y + y_offset
            else:
                old_y = rect.y
                
                rect.y = mouse_position.y()
                rect.height = self._old_height_rect + (self._old_y_rect - mouse_position.y()) 
                
                if rect.y < 1:
                    rect.y = 1
                    
                if self.__border_index != 0:
                    if  mouse_position.y() < (rect.roi_y +  self._main_text.y):
                        rect.roi_height = rect.roi_height + ((rect.roi_y + self._main_text.y) - rect.y)
                        rect.roi_y = rect.roi_y - ((rect.roi_y + self._main_text.y) - rect.y)
                        """
                        if rect.roi_unlimited_up:
                            rect.roi_height = rect.roi_height + ((rect.roi_y + self._main_text.y) - rect.y)
                            rect.roi_y = rect.roi_y - ((rect.roi_y + self._main_text.y) - rect.y)
                        else:
                            rect.y = rect.roi_y +  self._main_text.y + 1
                            rect.height = self._old_height_rect + (self._old_y_rect - (rect.roi_y +  self._main_text.y)) 
                            
                            #rect.roi_height = rect.roi_height + ((rect.roi_y + self._main_text.y) - rect.y)
                            #rect.roi_y = rect.roi_y - ((rect.roi_y + self._main_text.y) - rect.y)
                        """

                
                if rect.height < int(4 * self.scaling_factor):
                    rect.height = int(4 * self.scaling_factor)
                    rect.y = self._old_y_rect + self._old_height_rect - int(4 * self.scaling_factor)
                    
                     
                y_offset =  old_y - rect.y
                
                if rect.x_offset is not None and rect.y_offset is not None:
                    rect.y_offset = rect.y_offset + y_offset
                    
                #print x_offset
                if self.__border_index == 0:
                    for sub_image_finder in self._sub_texts_finder:
                        sub_image_finder.roi_y = sub_image_finder.roi_y + y_offset
                
                
        elif  self.__flag_mouse_is_on_right_up_corner == True:
        
            mouse_position = QPoint(QCursor.pos())
            
            
            if self.__border_index == 0:
                old_width = rect.width 
                
                rect.width = mouse_position.x() - rect.x
                
                if rect.x + rect.width > self._bg_pixmap.width() + 1:
                    rect.width = self._bg_pixmap.width() - rect.x - 1
                
                

                if  rect.x + rect.width > rect.roi_x + rect.roi_width:

                    rect.roi_width = rect.roi_width + ((rect.x + rect.width) - (rect.roi_x + rect.roi_width))
                    #rect.roi_x = rect.roi_x - ((rect.roi_x + self._main_text.x) - rect.x)

                    """
                    if rect.roi_unlimited_right:
                        rect.roi_width = rect.roi_width + ((rect.x + rect.width) - (rect.roi_x + rect.roi_width))
                        #rect.roi_x = rect.roi_x - ((rect.roi_x + self._main_text.x) - rect.x)
                    else:
                        # -- rect.x = rect.roi_x +  self._main_text.x
                        rect.width = self._old_width_rect + ((rect.roi_x + rect.roi_width) - (self._old_x_rect + self._old_width_rect)) -1

                        #rect.roi_width = rect.roi_width + ((rect.x + rect.width) - (rect.roi_x + self._main_text.x + rect.roi_width))
                        #rect.roi_x = rect.roi_x - ((rect.roi_x + self._main_text.x) - rect.x)
                    """

                
                if rect.width < int(4 * self.scaling_factor):
                    rect.width = int(4 * self.scaling_factor)
                    #rect.x = self._old_x_rect + self._old_width_rect + 4
                
            
            else:
                old_width = rect.width 
                
                rect.width = mouse_position.x() - rect.x
                
                if rect.x + rect.width > self._bg_pixmap.width() + 1:
                    rect.width = self._bg_pixmap.width() - rect.x - 1
                
                
                if self.__border_index != 0:
                    if  rect.x + rect.width > rect.roi_x + self._main_text.x + rect.roi_width:
                        rect.roi_width = rect.roi_width + ((rect.x + rect.width) - (rect.roi_x + self._main_text.x + rect.roi_width))
                        #rect.roi_x = rect.roi_x - ((rect.roi_x + self._main_text.x) - rect.x)
                        """
                        if rect.roi_unlimited_right:
                            rect.roi_width = rect.roi_width + ((rect.x + rect.width) - (rect.roi_x + self._main_text.x + rect.roi_width))
                            #rect.roi_x = rect.roi_x - ((rect.roi_x + self._main_text.x) - rect.x)
                        else:
                            # -- rect.x = rect.roi_x +  self._main_text.x
                            rect.width = self._old_width_rect + ((rect.roi_x + rect.roi_width + self._main_text.x) - (self._old_x_rect + self._old_width_rect)) -1

                            #rect.roi_width = rect.roi_width + ((rect.x + rect.width) - (rect.roi_x + self._main_text.x + rect.roi_width))
                            #rect.roi_x = rect.roi_x - ((rect.roi_x + self._main_text.x) - rect.x)
                        """

                
                if rect.width < int(4 * self.scaling_factor):
                    rect.width = int(4 * self.scaling_factor)
                    #rect.x = self._old_x_rect + self._old_width_rect + 4



            if self.__border_index == 0:

                old_y = rect.y
                
                #rect.height = rect.height + (rect.y - mouse_position.y())
                #rect.y = mouse_position.y()

                                        
                rect.y = mouse_position.y()
                rect.height = self._old_height_rect + (self._old_y_rect - mouse_position.y()) 
                
                
                if rect.y < 1:
                    rect.y = 1
            
                if  mouse_position.y() < (rect.roi_y):

                    rect.roi_height = rect.roi_height + (rect.roi_y - rect.y)
                    rect.roi_y = rect.roi_y - (rect.roi_y - rect.y)
                    """
                    if rect.roi_unlimited_left:
                        rect.roi_height = rect.roi_height + (rect.roi_y - rect.y)
                        rect.roi_y = rect.roi_y - (rect.roi_y - rect.y)
                    else:
                        rect.y = rect.roi_y + 1
                        rect.height = self._old_height_rect + (self._old_y_rect - rect.roi_y) 
                        
                        #rect.roi_height = rect.roi_height + (rect.roi_y - rect.y)
                        #rect.roi_y = rect.roi_y - (rect.roi_y - rect.y)
                    """
                
                if rect.height < int(4 * self.scaling_factor):
                    rect.height = int(4 * self.scaling_factor)
                    rect.y = self._old_y_rect + self._old_height_rect - int(4 * self.scaling_factor)
                     
                y_offset =  old_y - rect.y

                                        
                if rect.y_offset is not None and rect.y_offset is not None:
                    rect.y_offset = rect.y_offset + y_offset
                
                #print y_offset
                            
                if self.__border_index == 0:
                    for sub_image_finder in self._sub_texts_finder:
                        sub_image_finder.roi_y = sub_image_finder.roi_y + y_offset
            else:
                old_y = rect.y
                
                rect.y = mouse_position.y()
                rect.height = self._old_height_rect + (self._old_y_rect - mouse_position.y()) 
                
                if rect.y < 1:
                    rect.y = 1
                    
                if self.__border_index != 0:
                    if  mouse_position.y() < (rect.roi_y +  self._main_text.y):
                        rect.roi_height = rect.roi_height + ((rect.roi_y + self._main_text.y) - rect.y)
                        rect.roi_y = rect.roi_y - ((rect.roi_y + self._main_text.y) - rect.y)
                        """
                        if rect.roi_unlimited_up:
                            rect.roi_height = rect.roi_height + ((rect.roi_y + self._main_text.y) - rect.y)
                            rect.roi_y = rect.roi_y - ((rect.roi_y + self._main_text.y) - rect.y)
                        else:
                            rect.y = rect.roi_y +  self._main_text.y + 1
                            rect.height = self._old_height_rect + (self._old_y_rect - (rect.roi_y +  self._main_text.y)) 
                            
                            #rect.roi_height = rect.roi_height + ((rect.roi_y + self._main_text.y) - rect.y)
                            #rect.roi_y = rect.roi_y - ((rect.roi_y + self._main_text.y) - rect.y)
                        """

                
                if rect.height < int(4 * self.scaling_factor):
                    rect.height = int(4 * self.scaling_factor)
                    rect.y = self._old_y_rect + self._old_height_rect - int(4 * self.scaling_factor)
                    
                     
                y_offset =  old_y - rect.y
                
                if rect.x_offset is not None and rect.y_offset is not None:
                    rect.y_offset = rect.y_offset + y_offset
                    
                #print x_offset
                if self.__border_index == 0:
                    for sub_image_finder in self._sub_texts_finder:
                        sub_image_finder.roi_y = sub_image_finder.roi_y + y_offset
                
                
        elif  self.__flag_mouse_is_on_right_bottom_corner == True:
        
            mouse_position = QPoint(QCursor.pos())
            
            if self.__border_index == 0:
            
                old_height = rect.height 
                
                rect.height = mouse_position.y() - rect.y
           
                if rect.y + rect.height > self._bg_pixmap.height() + 1:
                    rect.height = self._bg_pixmap.height() - rect.y - 1
                
                

                if  rect.y + rect.height > rect.roi_y + rect.roi_height:
                
                    rect.roi_height = rect.roi_height + ((rect.y + rect.height) - (rect.roi_y + rect.roi_height))
                    #rect.roi_y = rect.roi_y - ((rect.roi_y + self._main_text.y) - rect.y)
                
                    """
                    if rect.roi_unlimited_down:
                        rect.roi_height = rect.roi_height + ((rect.y + rect.height) - (rect.roi_y + rect.roi_height))
                        #rect.roi_y = rect.roi_y - ((rect.roi_y + self._main_text.y) - rect.y)
                    else:
                        # -- rect.y = rect.roi_y +  self._main_text.y
                        rect.height = self._old_height_rect + ((rect.roi_y + rect.roi_height) - (self._old_y_rect + self._old_height_rect)) -1

                        #rect.roi_height = rect.roi_height + ((rect.y + rect.height) - (rect.roi_y + self._main_text.y + rect.roi_height))
                        #rect.roi_y = rect.roi_y - ((rect.roi_y + self._main_text.y) - rect.y)
                    """
                
                if rect.height < int(4 * self.scaling_factor):
                    rect.height = int(4 * self.scaling_factor)
                    #rect.y = self._old_y_rect + self._old_height_rect + 4
                
            
            else:

                old_height = rect.height 
                
                rect.height = mouse_position.y() - rect.y
           
                if rect.y + rect.height > self._bg_pixmap.height() + 1:
                    rect.height = self._bg_pixmap.height() - rect.y - 1
                
                
                if self.__border_index != 0:
                    if  rect.y + rect.height > rect.roi_y + self._main_text.y + rect.roi_height:
                        rect.roi_height = rect.roi_height + ((rect.y + rect.height) - (rect.roi_y + self._main_text.y + rect.roi_height))
                        #rect.roi_y = rect.roi_y - ((rect.roi_y + self._main_text.y) - rect.y)
                        """
                        if rect.roi_unlimited_down:
                            rect.roi_height = rect.roi_height + ((rect.y + rect.height) - (rect.roi_y + self._main_text.y + rect.roi_height))
                            #rect.roi_y = rect.roi_y - ((rect.roi_y + self._main_text.y) - rect.y)
                        else:
                            # -- rect.y = rect.roi_y +  self._main_text.y
                            rect.height = self._old_height_rect + ((rect.roi_y + rect.roi_height + self._main_text.y) - (self._old_y_rect + self._old_height_rect)) -1

                            #rect.roi_height = rect.roi_height + ((rect.y + rect.height) - (rect.roi_y + self._main_text.y + rect.roi_height))
                            #rect.roi_y = rect.roi_y - ((rect.roi_y + self._main_text.y) - rect.y)
                        """
                
                if rect.height < int(4 * self.scaling_factor):
                    rect.height = int(4 * self.scaling_factor)
                    #rect.y = self._old_y_rect + self._old_height_rect + 4

            if self.__border_index == 0:
                old_width = rect.width 
                
                rect.width = mouse_position.x() - rect.x
                
                if rect.x + rect.width > self._bg_pixmap.width() + 1:
                    rect.width = self._bg_pixmap.width() - rect.x - 1
                
                

                if  rect.x + rect.width > rect.roi_x + rect.roi_width:

                    rect.roi_width = rect.roi_width + ((rect.x + rect.width) - (rect.roi_x + rect.roi_width))
                    #rect.roi_x = rect.roi_x - ((rect.roi_x + self._main_text.x) - rect.x)

                    """
                    if rect.roi_unlimited_right:
                        rect.roi_width = rect.roi_width + ((rect.x + rect.width) - (rect.roi_x + rect.roi_width))
                        #rect.roi_x = rect.roi_x - ((rect.roi_x + self._main_text.x) - rect.x)
                    else:
                        # -- rect.x = rect.roi_x +  self._main_text.x
                        rect.width = self._old_width_rect + ((rect.roi_x + rect.roi_width) - (self._old_x_rect + self._old_width_rect)) -1

                        #rect.roi_width = rect.roi_width + ((rect.x + rect.width) - (rect.roi_x + self._main_text.x + rect.roi_width))
                        #rect.roi_x = rect.roi_x - ((rect.roi_x + self._main_text.x) - rect.x)
                    """

                
                if rect.width < int(4 * self.scaling_factor):
                    rect.width = int(4 * self.scaling_factor)
                    #rect.x = self._old_x_rect + self._old_width_rect + 4
                
            
            else:
                old_width = rect.width 
                
                rect.width = mouse_position.x() - rect.x
                
                if rect.x + rect.width > self._bg_pixmap.width() + 1:
                    rect.width = self._bg_pixmap.width() - rect.x - 1
                
                
                if self.__border_index != 0:
                    if  rect.x + rect.width > rect.roi_x + self._main_text.x + rect.roi_width:
                        rect.roi_width = rect.roi_width + ((rect.x + rect.width) - (rect.roi_x + self._main_text.x + rect.roi_width))
                        #rect.roi_x = rect.roi_x - ((rect.roi_x + self._main_text.x) - rect.x)
                        """
                        if rect.roi_unlimited_right:
                            rect.roi_width = rect.roi_width + ((rect.x + rect.width) - (rect.roi_x + self._main_text.x + rect.roi_width))
                            #rect.roi_x = rect.roi_x - ((rect.roi_x + self._main_text.x) - rect.x)
                        else:
                            # -- rect.x = rect.roi_x +  self._main_text.x
                            rect.width = self._old_width_rect + ((rect.roi_x + rect.roi_width + self._main_text.x) - (self._old_x_rect + self._old_width_rect)) -1

                            #rect.roi_width = rect.roi_width + ((rect.x + rect.width) - (rect.roi_x + self._main_text.x + rect.roi_width))
                            #rect.roi_x = rect.roi_x - ((rect.roi_x + self._main_text.x) - rect.x)
                        """

                
                if rect.width < int(4 * self.scaling_factor):
                    rect.width = int(4 * self.scaling_factor)
                    #rect.x = self._old_x_rect + self._old_width_rect + 4


                
        elif  self.__flag_mouse_is_on_left_bottom_corner == True:
            mouse_position = QPoint(QCursor.pos())

            if self.__border_index == 0:
            
                old_height = rect.height 
                
                rect.height = mouse_position.y() - rect.y
           
                if rect.y + rect.height > self._bg_pixmap.height() + 1:
                    rect.height = self._bg_pixmap.height() - rect.y - 1
                
                

                if  rect.y + rect.height > rect.roi_y + rect.roi_height:
                
                    rect.roi_height = rect.roi_height + ((rect.y + rect.height) - (rect.roi_y + rect.roi_height))
                    #rect.roi_y = rect.roi_y - ((rect.roi_y + self._main_text.y) - rect.y)
                
                    """
                    if rect.roi_unlimited_down:
                        rect.roi_height = rect.roi_height + ((rect.y + rect.height) - (rect.roi_y + rect.roi_height))
                        #rect.roi_y = rect.roi_y - ((rect.roi_y + self._main_text.y) - rect.y)
                    else:
                        # -- rect.y = rect.roi_y +  self._main_text.y
                        rect.height = self._old_height_rect + ((rect.roi_y + rect.roi_height) - (self._old_y_rect + self._old_height_rect)) -1

                        #rect.roi_height = rect.roi_height + ((rect.y + rect.height) - (rect.roi_y + self._main_text.y + rect.roi_height))
                        #rect.roi_y = rect.roi_y - ((rect.roi_y + self._main_text.y) - rect.y)
                    """
                
                if rect.height < int(4 * self.scaling_factor):
                    rect.height = int(4 * self.scaling_factor)
                    #rect.y = self._old_y_rect + self._old_height_rect + 4
                
            
            else:

                old_height = rect.height 
                
                rect.height = mouse_position.y() - rect.y
           
                if rect.y + rect.height > self._bg_pixmap.height() + 1:
                    rect.height = self._bg_pixmap.height() - rect.y - 1
                
                
                if self.__border_index != 0:
                    if  rect.y + rect.height > rect.roi_y + self._main_text.y + rect.roi_height:
                        rect.roi_height = rect.roi_height + ((rect.y + rect.height) - (rect.roi_y + self._main_text.y + rect.roi_height))
                        #rect.roi_y = rect.roi_y - ((rect.roi_y + self._main_text.y) - rect.y)
                        """
                        if rect.roi_unlimited_down:
                            rect.roi_height = rect.roi_height + ((rect.y + rect.height) - (rect.roi_y + self._main_text.y + rect.roi_height))
                            #rect.roi_y = rect.roi_y - ((rect.roi_y + self._main_text.y) - rect.y)
                        else:
                            # -- rect.y = rect.roi_y +  self._main_text.y
                            rect.height = self._old_height_rect + ((rect.roi_y + rect.roi_height + self._main_text.y) - (self._old_y_rect + self._old_height_rect)) -1

                            #rect.roi_height = rect.roi_height + ((rect.y + rect.height) - (rect.roi_y + self._main_text.y + rect.roi_height))
                            #rect.roi_y = rect.roi_y - ((rect.roi_y + self._main_text.y) - rect.y)
                        """
                
                if rect.height < int(4 * self.scaling_factor):
                    rect.height = int(4 * self.scaling_factor)
                    #rect.y = self._old_y_rect + self._old_height_rect + 4
                    
            if self.__border_index == 0:

                old_x = rect.x
                
                #rect.width = rect.width + (rect.x - mouse_position.x())
                #rect.x = mouse_position.x()

                                        
                rect.x = mouse_position.x()
                rect.width = self._old_width_rect + (self._old_x_rect - mouse_position.x()) 
                
                
                if rect.x < 1:
                    rect.x = 1
            
                if  mouse_position.x() < (rect.roi_x):
                    rect.roi_width = rect.roi_width + (rect.roi_x - rect.x)
                    rect.roi_x = rect.roi_x - (rect.roi_x - rect.x)
                    """
                    if rect.roi_unlimited_left:
                        rect.roi_width = rect.roi_width + (rect.roi_x - rect.x)
                        rect.roi_x = rect.roi_x - (rect.roi_x - rect.x)
                    else:
                        rect.x = rect.roi_x + 1
                        rect.width = self._old_width_rect + (self._old_x_rect - rect.roi_x) 
                        
                        #rect.roi_width = rect.roi_width + (rect.roi_x - rect.x)
                        #rect.roi_x = rect.roi_x - (rect.roi_x - rect.x)
                    """
                        
                
                if rect.width < int(4 * self.scaling_factor):
                    rect.width = int(4 * self.scaling_factor)
                    rect.x = self._old_x_rect + self._old_width_rect - int(4 * self.scaling_factor)
                     
                x_offset =  old_x - rect.x

                                        
                if rect.x_offset is not None and rect.y_offset is not None:
                    rect.x_offset = rect.x_offset + x_offset
                
                #print x_offset
                            
                if self.__border_index == 0:
                    for sub_image_finder in self._sub_texts_finder:
                        sub_image_finder.roi_x = sub_image_finder.roi_x + x_offset
            else:
                old_x = rect.x
                
                #rect.width = rect.width + (rect.x - mouse_position.x())
                #rect.x = mouse_position.x()

                                        
                rect.x = mouse_position.x()
                rect.width = self._old_width_rect + (self._old_x_rect - mouse_position.x()) 
                
                
                if rect.x < 1:
                    rect.x = 1
                
                if self.__border_index != 0:
                    if  mouse_position.x() < (rect.roi_x +  self._main_text.x):
                        rect.roi_width = rect.roi_width + ((rect.roi_x + self._main_text.x) - rect.x)
                        rect.roi_x = rect.roi_x - ((rect.roi_x + self._main_text.x) - rect.x)
                        """
                        if rect.roi_unlimited_left:
                            rect.roi_width = rect.roi_width + ((rect.roi_x + self._main_text.x) - rect.x)
                            rect.roi_x = rect.roi_x - ((rect.roi_x + self._main_text.x) - rect.x)
                        else:
                            rect.x = rect.roi_x +  self._main_text.x + 1
                            rect.width = self._old_width_rect + (self._old_x_rect - (rect.roi_x +  self._main_text.x)) 
                            
                            #rect.roi_width = rect.roi_width + ((rect.roi_x + self._main_text.x) - rect.x)
                            #rect.roi_x = rect.roi_x - ((rect.roi_x + self._main_text.x) - rect.x)
                        """    
                
                if rect.width < int(4 * self.scaling_factor):
                    rect.width = int(4 * self.scaling_factor)
                    rect.x = self._old_x_rect + self._old_width_rect - int(4 * self.scaling_factor)
                     
                x_offset =  old_x - rect.x

                                        
                if rect.x_offset is not None and rect.y_offset is not None:
                    rect.x_offset = rect.x_offset + x_offset
                
                #print x_offset
                            
                if self.__border_index == 0:
                    for sub_image_finder in self._sub_texts_finder:
                        sub_image_finder.roi_x = sub_image_finder.roi_x + x_offset
                    
                    
        
        elif self.__flag_mouse_is_on_left_border is True:
        
            mouse_position = QPoint(QCursor.pos())
            
            if self.__border_index == 0:

                old_x = rect.x
                
                #rect.width = rect.width + (rect.x - mouse_position.x())
                #rect.x = mouse_position.x()

                                        
                rect.x = mouse_position.x()
                rect.width = self._old_width_rect + (self._old_x_rect - mouse_position.x()) 
                
                
                if rect.x < 1:
                    rect.x = 1
            
                if  mouse_position.x() < (rect.roi_x):
                    rect.roi_width = rect.roi_width + (rect.roi_x - rect.x)
                    rect.roi_x = rect.roi_x - (rect.roi_x - rect.x)
                    """
                    if rect.roi_unlimited_left:
                        rect.roi_width = rect.roi_width + (rect.roi_x - rect.x)
                        rect.roi_x = rect.roi_x - (rect.roi_x - rect.x)
                    else:
                        rect.x = rect.roi_x + 1
                        rect.width = self._old_width_rect + (self._old_x_rect - rect.roi_x) 
                        
                        #rect.roi_width = rect.roi_width + (rect.roi_x - rect.x)
                        #rect.roi_x = rect.roi_x - (rect.roi_x - rect.x)
                    """
                        
                
                if rect.width < int(4 * self.scaling_factor):
                    rect.width = int(4 * self.scaling_factor)
                    rect.x = self._old_x_rect + self._old_width_rect - int(4 * self.scaling_factor)
                     
                x_offset =  old_x - rect.x

                                        
                if rect.x_offset is not None and rect.y_offset is not None:
                    rect.x_offset = rect.x_offset + x_offset
                
                #print x_offset
                            
                if self.__border_index == 0:
                    for sub_image_finder in self._sub_texts_finder:
                        sub_image_finder.roi_x = sub_image_finder.roi_x + x_offset
            else:
                old_x = rect.x
                
                #rect.width = rect.width + (rect.x - mouse_position.x())
                #rect.x = mouse_position.x()

                                        
                rect.x = mouse_position.x()
                rect.width = self._old_width_rect + (self._old_x_rect - mouse_position.x()) 
                
                
                if rect.x < 1:
                    rect.x = 1
                
                if self.__border_index != 0:
                    if  mouse_position.x() < (rect.roi_x +  self._main_text.x):
                        rect.roi_width = rect.roi_width + ((rect.roi_x + self._main_text.x) - rect.x)
                        rect.roi_x = rect.roi_x - ((rect.roi_x + self._main_text.x) - rect.x)
                        """
                        if rect.roi_unlimited_left:
                            rect.roi_width = rect.roi_width + ((rect.roi_x + self._main_text.x) - rect.x)
                            rect.roi_x = rect.roi_x - ((rect.roi_x + self._main_text.x) - rect.x)
                        else:
                            rect.x = rect.roi_x +  self._main_text.x + 1
                            rect.width = self._old_width_rect + (self._old_x_rect - (rect.roi_x +  self._main_text.x)) 
                            
                            #rect.roi_width = rect.roi_width + ((rect.roi_x + self._main_text.x) - rect.x)
                            #rect.roi_x = rect.roi_x - ((rect.roi_x + self._main_text.x) - rect.x)
                        """    
                
                if rect.width < int(4 * self.scaling_factor):
                    rect.width = int(4 * self.scaling_factor)
                    rect.x = self._old_x_rect + self._old_width_rect - int(4 * self.scaling_factor)
                     
                x_offset =  old_x - rect.x

                                        
                if rect.x_offset is not None and rect.y_offset is not None:
                    rect.x_offset = rect.x_offset + x_offset
                
                #print x_offset
                            
                if self.__border_index == 0:
                    for sub_image_finder in self._sub_texts_finder:
                        sub_image_finder.roi_x = sub_image_finder.roi_x + x_offset
                
        elif self.__flag_mouse_is_on_top_border is True:
        
            mouse_position = QPoint(QCursor.pos())

            if self.__border_index == 0:

                old_y = rect.y
                
                #rect.height = rect.height + (rect.y - mouse_position.y())
                #rect.y = mouse_position.y()

                                        
                rect.y = mouse_position.y()
                rect.height = self._old_height_rect + (self._old_y_rect - mouse_position.y()) 
                
                
                if rect.y < 1:
                    rect.y = 1
            
                if  mouse_position.y() < (rect.roi_y):

                    rect.roi_height = rect.roi_height + (rect.roi_y - rect.y)
                    rect.roi_y = rect.roi_y - (rect.roi_y - rect.y)
                    """
                    if rect.roi_unlimited_left:
                        rect.roi_height = rect.roi_height + (rect.roi_y - rect.y)
                        rect.roi_y = rect.roi_y - (rect.roi_y - rect.y)
                    else:
                        rect.y = rect.roi_y + 1
                        rect.height = self._old_height_rect + (self._old_y_rect - rect.roi_y) 
                        
                        #rect.roi_height = rect.roi_height + (rect.roi_y - rect.y)
                        #rect.roi_y = rect.roi_y - (rect.roi_y - rect.y)
                    """
                
                if rect.height < int(4 * self.scaling_factor):
                    rect.height = int(4 * self.scaling_factor)
                    rect.y = self._old_y_rect + self._old_height_rect - int(4 * self.scaling_factor)
                     
                y_offset =  old_y - rect.y

                                        
                if rect.y_offset is not None and rect.y_offset is not None:
                    rect.y_offset = rect.y_offset + y_offset
                
                #print y_offset
                            
                if self.__border_index == 0:
                    for sub_image_finder in self._sub_texts_finder:
                        sub_image_finder.roi_y = sub_image_finder.roi_y + y_offset
            else:
                old_y = rect.y
                
                rect.y = mouse_position.y()
                rect.height = self._old_height_rect + (self._old_y_rect - mouse_position.y()) 
                
                if rect.y < 1:
                    rect.y = 1
                    
                if self.__border_index != 0:
                    if  mouse_position.y() < (rect.roi_y +  self._main_text.y):
                        rect.roi_height = rect.roi_height + ((rect.roi_y + self._main_text.y) - rect.y)
                        rect.roi_y = rect.roi_y - ((rect.roi_y + self._main_text.y) - rect.y)
                        """
                        if rect.roi_unlimited_up:
                            rect.roi_height = rect.roi_height + ((rect.roi_y + self._main_text.y) - rect.y)
                            rect.roi_y = rect.roi_y - ((rect.roi_y + self._main_text.y) - rect.y)
                        else:
                            rect.y = rect.roi_y +  self._main_text.y + 1
                            rect.height = self._old_height_rect + (self._old_y_rect - (rect.roi_y +  self._main_text.y)) 
                            
                            #rect.roi_height = rect.roi_height + ((rect.roi_y + self._main_text.y) - rect.y)
                            #rect.roi_y = rect.roi_y - ((rect.roi_y + self._main_text.y) - rect.y)
                        """

                
                if rect.height < int(4 * self.scaling_factor):
                    rect.height = int(4 * self.scaling_factor)
                    rect.y = self._old_y_rect + self._old_height_rect - int(4 * self.scaling_factor)
                    
                     
                y_offset =  old_y - rect.y
                
                if rect.x_offset is not None and rect.y_offset is not None:
                    rect.y_offset = rect.y_offset + y_offset
                    
                #print x_offset
                if self.__border_index == 0:
                    for sub_image_finder in self._sub_texts_finder:
                        sub_image_finder.roi_y = sub_image_finder.roi_y + y_offset
                
        elif self.__flag_mouse_is_on_bottom_border is True:
        
            mouse_position = QPoint(QCursor.pos())
            
            if self.__border_index == 0:
            
                old_height = rect.height 
                
                rect.height = mouse_position.y() - rect.y
           
                if rect.y + rect.height > self._bg_pixmap.height() + 1:
                    rect.height = self._bg_pixmap.height() - rect.y - 1
                
                

                if  rect.y + rect.height > rect.roi_y + rect.roi_height:
                
                    rect.roi_height = rect.roi_height + ((rect.y + rect.height) - (rect.roi_y + rect.roi_height))
                    #rect.roi_y = rect.roi_y - ((rect.roi_y + self._main_text.y) - rect.y)
                
                    """
                    if rect.roi_unlimited_down:
                        rect.roi_height = rect.roi_height + ((rect.y + rect.height) - (rect.roi_y + rect.roi_height))
                        #rect.roi_y = rect.roi_y - ((rect.roi_y + self._main_text.y) - rect.y)
                    else:
                        # -- rect.y = rect.roi_y +  self._main_text.y
                        rect.height = self._old_height_rect + ((rect.roi_y + rect.roi_height) - (self._old_y_rect + self._old_height_rect)) -1

                        #rect.roi_height = rect.roi_height + ((rect.y + rect.height) - (rect.roi_y + self._main_text.y + rect.roi_height))
                        #rect.roi_y = rect.roi_y - ((rect.roi_y + self._main_text.y) - rect.y)
                    """
                
                if rect.height < int(4 * self.scaling_factor):
                    rect.height = int(4 * self.scaling_factor)
                    #rect.y = self._old_y_rect + self._old_height_rect + 4
                
            
            else:

                old_height = rect.height 
                
                rect.height = mouse_position.y() - rect.y
           
                if rect.y + rect.height > self._bg_pixmap.height() + 1:
                    rect.height = self._bg_pixmap.height() - rect.y - 1
                
                
                if self.__border_index != 0:
                    if  rect.y + rect.height > rect.roi_y + self._main_text.y + rect.roi_height:
                        rect.roi_height = rect.roi_height + ((rect.y + rect.height) - (rect.roi_y + self._main_text.y + rect.roi_height))
                        #rect.roi_y = rect.roi_y - ((rect.roi_y + self._main_text.y) - rect.y)
                        """
                        if rect.roi_unlimited_down:
                            rect.roi_height = rect.roi_height + ((rect.y + rect.height) - (rect.roi_y + self._main_text.y + rect.roi_height))
                            #rect.roi_y = rect.roi_y - ((rect.roi_y + self._main_text.y) - rect.y)
                        else:
                            # -- rect.y = rect.roi_y +  self._main_text.y
                            rect.height = self._old_height_rect + ((rect.roi_y + rect.roi_height + self._main_text.y) - (self._old_y_rect + self._old_height_rect)) -1

                            #rect.roi_height = rect.roi_height + ((rect.y + rect.height) - (rect.roi_y + self._main_text.y + rect.roi_height))
                            #rect.roi_y = rect.roi_y - ((rect.roi_y + self._main_text.y) - rect.y)
                        """
                
                if rect.height < int(4 * self.scaling_factor):
                    rect.height = int(4 * self.scaling_factor)
                    #rect.y = self._old_y_rect + self._old_height_rect + 4
                

            #print rect.x
        elif self.__flag_mouse_is_on_right_border is True:
        
            mouse_position = QPoint(QCursor.pos())

            if self.__border_index == 0:
                old_width = rect.width 
                
                rect.width = mouse_position.x() - rect.x
                
                if rect.x + rect.width > self._bg_pixmap.width() + 1:
                    rect.width = self._bg_pixmap.width() - rect.x - 1
                
                

                if  rect.x + rect.width > rect.roi_x + rect.roi_width:

                    rect.roi_width = rect.roi_width + ((rect.x + rect.width) - (rect.roi_x + rect.roi_width))
                    #rect.roi_x = rect.roi_x - ((rect.roi_x + self._main_text.x) - rect.x)

                    """
                    if rect.roi_unlimited_right:
                        rect.roi_width = rect.roi_width + ((rect.x + rect.width) - (rect.roi_x + rect.roi_width))
                        #rect.roi_x = rect.roi_x - ((rect.roi_x + self._main_text.x) - rect.x)
                    else:
                        # -- rect.x = rect.roi_x +  self._main_text.x
                        rect.width = self._old_width_rect + ((rect.roi_x + rect.roi_width) - (self._old_x_rect + self._old_width_rect)) -1

                        #rect.roi_width = rect.roi_width + ((rect.x + rect.width) - (rect.roi_x + self._main_text.x + rect.roi_width))
                        #rect.roi_x = rect.roi_x - ((rect.roi_x + self._main_text.x) - rect.x)
                    """

                
                if rect.width < int(4 * self.scaling_factor):
                    rect.width = int(4 * self.scaling_factor)
                    #rect.x = self._old_x_rect + self._old_width_rect + 4
                
            
            else:
                old_width = rect.width 
                
                rect.width = mouse_position.x() - rect.x
                
                if rect.x + rect.width > self._bg_pixmap.width() + 1:
                    rect.width = self._bg_pixmap.width() - rect.x - 1
                
                
                if self.__border_index != 0:
                    if  rect.x + rect.width > rect.roi_x + self._main_text.x + rect.roi_width:
                        rect.roi_width = rect.roi_width + ((rect.x + rect.width) - (rect.roi_x + self._main_text.x + rect.roi_width))
                        #rect.roi_x = rect.roi_x - ((rect.roi_x + self._main_text.x) - rect.x)
                        """
                        if rect.roi_unlimited_right:
                            rect.roi_width = rect.roi_width + ((rect.x + rect.width) - (rect.roi_x + self._main_text.x + rect.roi_width))
                            #rect.roi_x = rect.roi_x - ((rect.roi_x + self._main_text.x) - rect.x)
                        else:
                            # -- rect.x = rect.roi_x +  self._main_text.x
                            rect.width = self._old_width_rect + ((rect.roi_x + rect.roi_width + self._main_text.x) - (self._old_x_rect + self._old_width_rect)) -1

                            #rect.roi_width = rect.roi_width + ((rect.x + rect.width) - (rect.roi_x + self._main_text.x + rect.roi_width))
                            #rect.roi_x = rect.roi_x - ((rect.roi_x + self._main_text.x) - rect.x)
                        """

                
                if rect.width < int(4 * self.scaling_factor):
                    rect.width = int(4 * self.scaling_factor)
                    #rect.x = self._old_x_rect + self._old_width_rect + 4


        
     
    def is_mouse_on_left_border(self, rect):
        mouse_position = QPoint(QCursor.pos())
        
        threshold = self.calc_threshold_border(rect)
        
        if (mouse_position.x() > rect.x - threshold and
                mouse_position.x() < rect.x + threshold and
                mouse_position.y() > rect.y - threshold and
                mouse_position.y() < rect.height + rect.y + threshold):
            return True
        else:
            return False
            
    def is_mouse_on_left_border_roi(self, rect):
    
        threshold = self.calc_threshold_border(rect, True)
    
        if rect.x == 0 and rect.width == 0 and rect.y == 0 and rect.height == 0:
            return False
        mouse_position = QPoint(QCursor.pos())
        
        
        if (rect.roi_unlimited_left is True ):
            return False
        elif (mouse_position.x() > rect.roi_x - threshold and
                mouse_position.x() < rect.roi_x + threshold and
                mouse_position.y() > rect.roi_y - threshold and
                mouse_position.y() < rect.roi_height + rect.roi_y + threshold):
            return True
        elif ((rect.roi_unlimited_up is True or rect.roi_unlimited_down is True) and
                mouse_position.x() > rect.roi_x - threshold and
                mouse_position.x() < rect.roi_x + threshold): #and
                #mouse_position.y() > rect.roi_y + self._main_text.y - int((8 *self.scaling_factor)) and
                #mouse_position.y() < rect.roi_y + self._main_text.y + int((8 *self.scaling_factor))):
            return True
        elif (mouse_position.x() > rect.roi_x + self._main_text.x - threshold and
                mouse_position.x() < rect.roi_x + self._main_text.x + threshold and
                mouse_position.y() > rect.roi_y + self._main_text.y - threshold and
                mouse_position.y() < rect.roi_height + rect.roi_y + self._main_text.y + threshold):
            return True
        elif ((rect.roi_unlimited_up is True or rect.roi_unlimited_down is True) and
                mouse_position.x() > rect.roi_x + self._main_text.x - threshold and
                mouse_position.x() < rect.roi_x + self._main_text.x + threshold): #and
                #mouse_position.y() > rect.roi_y + self._main_text.y - int((8 *self.scaling_factor)) and
                #mouse_position.y() < rect.roi_y + self._main_text.y + int((8 *self.scaling_factor))):
            return True
        else:
            return False
            
    def is_mouse_on_right_border(self, rect):
        mouse_position = QPoint(QCursor.pos())
        
        threshold = self.calc_threshold_border(rect)
        
        if (mouse_position.x() > rect.x + rect.width - threshold and
                mouse_position.x() < rect.x + rect.width + threshold and
                mouse_position.y() > rect.y - threshold and
                mouse_position.y() < rect.height + rect.y + threshold):
            return True
        else:
            return False
            
    def is_mouse_on_right_border_roi(self, rect):
    
        threshold = self.calc_threshold_border(rect, True)
    
        if rect.x == 0 and rect.width == 0 and rect.y == 0 and rect.height == 0:
            return False
            
        mouse_position = QPoint(QCursor.pos())
        
        if (rect.roi_unlimited_right is True ):
            return False
        elif (mouse_position.x() > rect.roi_x + rect.roi_width - threshold and
                mouse_position.x() < rect.roi_x + rect.roi_width + threshold and
                mouse_position.y() > rect.roi_y - threshold and
                mouse_position.y() < rect.roi_height + rect.roi_y + threshold):
            return True
        elif ((rect.roi_unlimited_up is True or rect.roi_unlimited_down is True) and
                mouse_position.x() > rect.roi_x + rect.roi_width - threshold and
                mouse_position.x() < rect.roi_x + rect.roi_width + threshold):
            return True
            
            
        elif (mouse_position.x() > rect.roi_x + self._main_text.x + rect.roi_width - threshold and
                mouse_position.x() < rect.roi_x + self._main_text.x + rect.roi_width + threshold and
                mouse_position.y() > rect.roi_y + self._main_text.y - threshold and
                mouse_position.y() < rect.roi_height + rect.roi_y + self._main_text.y + threshold):
            return True
        elif ((rect.roi_unlimited_up is True or rect.roi_unlimited_down is True) and
                mouse_position.x() > rect.roi_x + self._main_text.x + rect.roi_width - threshold and
                mouse_position.x() < rect.roi_x + self._main_text.x + rect.roi_width + threshold):
            return True
        else:
            return False
            
    def is_mouse_on_top_border(self, rect):
        mouse_position = QPoint(QCursor.pos())
        threshold = self.calc_threshold_border(rect)
        
        if (mouse_position.x() > rect.x - threshold and
                mouse_position.x() < rect.x + rect.width + threshold and
                mouse_position.y() > rect.y - threshold and
                mouse_position.y() < rect.y + threshold):
            return True
        else:
            return False
            
    def is_mouse_on_top_border_roi(self, rect):
        if rect.x == 0 and rect.width == 0 and rect.y == 0 and rect.height == 0:
            return False
            
        mouse_position = QPoint(QCursor.pos())
        threshold = self.calc_threshold_border(rect, True)
            
    
        if (rect.roi_unlimited_up is True ):
            return False
        elif (mouse_position.x() > rect.roi_x - threshold and
                mouse_position.x() < rect.roi_x + rect.roi_width + threshold and
                mouse_position.y() > rect.roi_y - threshold and
                mouse_position.y() < rect.roi_y + threshold):
            return True
        elif ((rect.roi_unlimited_left is True or rect.roi_unlimited_right is True) and
                mouse_position.y() > rect.roi_y - threshold and
                mouse_position.y() < rect.roi_y + threshold):
            return True

        elif (mouse_position.x() > rect.roi_x + self._main_text.x - threshold and
                mouse_position.x() < rect.roi_x + self._main_text.x + rect.roi_width + threshold and
                mouse_position.y() > rect.roi_y + self._main_text.y - threshold and
                mouse_position.y() < rect.roi_y + self._main_text.y + threshold):
            return True
        elif ((rect.roi_unlimited_left is True or rect.roi_unlimited_right is True) and
                mouse_position.y() > rect.roi_y + self._main_text.y - threshold and
                mouse_position.y() < rect.roi_y + self._main_text.y + threshold):
            return True

        else:
            return False
            
    def is_mouse_on_bottom_border(self, rect):
        mouse_position = QPoint(QCursor.pos())
        threshold = self.calc_threshold_border(rect)
        
        if (mouse_position.x() > rect.x - threshold and
                mouse_position.x() < rect.x + rect.width + threshold and
                mouse_position.y() > rect.y + rect.height - threshold and
                mouse_position.y() < rect.y + rect.height + threshold):
            return True
        else:
            return False
            
    def is_mouse_on_bottom_border_roi(self, rect):
        if rect.x == 0 and rect.width == 0 and rect.y == 0 and rect.height == 0:
            return False
            
        mouse_position = QPoint(QCursor.pos())
        threshold = self.calc_threshold_border(rect, True)
        
        if (rect.roi_unlimited_down is True ):
            return False
        elif (mouse_position.x() > rect.roi_x - threshold and
                mouse_position.x() < rect.roi_x + rect.roi_width + threshold and
                mouse_position.y() > rect.roi_y + rect.roi_height - threshold and
                mouse_position.y() < rect.roi_y + rect.roi_height + threshold):
            return True
        elif ((rect.roi_unlimited_left is True or rect.roi_unlimited_right is True) and
                mouse_position.y() > rect.roi_y + rect.roi_height - threshold and
                mouse_position.y() < rect.roi_y + rect.roi_height + threshold):
            return True
        elif (mouse_position.x() > rect.roi_x + self._main_text.x - threshold and
                mouse_position.x() < rect.roi_x + self._main_text.x + rect.roi_width + threshold and
                mouse_position.y() > rect.roi_y + self._main_text.y + rect.roi_height - threshold and
                mouse_position.y() < rect.roi_y + self._main_text.y + rect.roi_height + threshold):
            return True
        elif ((rect.roi_unlimited_left is True or rect.roi_unlimited_right is True) and
                mouse_position.y() > rect.roi_y + self._main_text.y + rect.roi_height - threshold and
                mouse_position.y() < rect.roi_y + self._main_text.y + rect.roi_height + threshold):
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
            
            roi_x =  self._main_text.roi_x
            roi_y =  self._main_text.roi_y
            roi_width =  self._main_text.roi_width
            roi_height =  self._main_text.roi_height

            if  self._main_text.roi_unlimited_up is True:
                roi_y = 0
                roi_height =  self._main_text.roi_y + roi_height

            if  self._main_text.roi_unlimited_down is True:
                if  self._main_text.roi_unlimited_up is True:
                    roi_height = self._bg_pixmap.height()-1
                else:
                    roi_height = self._bg_pixmap.height() - ( self._main_text.roi_y + 1)

            if  self._main_text.roi_unlimited_left is True:
                roi_x = 0
                roi_width =  self._main_text.roi_x + roi_width

            if  self._main_text.roi_unlimited_right is True:
                if  self._main_text.roi_unlimited_left is True:
                    roi_width = self._bg_pixmap.width() -1
                else:
                    roi_width = self._bg_pixmap.width() - ( self._main_text.roi_x + 1)
            
            OuterPath_roi.addRect(roi_x,
                    roi_y,
                    roi_width,
                    roi_height)
                
            if self._main_text.x != 0 and self._main_text.y != 0:
            
                        
                font = qp.font()
                font.setPixelSize(11 * self.scaling_factor);
                
                qp.setFont(font)
                qp.drawText( QPoint(self._main_text.x -1,self._main_text.y -(6*self.scaling_factor)), "M" )
            
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
                
            
                qp.drawRect(QRect(roi_x,
                    roi_y,
                    roi_width,
                    roi_height))  
                    
                qp.fillRect(self._main_text.x,
                    self._main_text.y,
                    self._main_text.width,
                    self._main_text.height,
                    QBrush(QColor(255, 0, 255, 130)))
                
                    
                qp.drawRect(QRect(self._main_text.x,
                    self._main_text.y,
                    self._main_text.width,
                    self._main_text.height))
                    
                if self._main_text.click is True or self._main_text.rightclick is True or self._main_text.mousemove is True or self._main_text.hold_and_release is not None:
                    
                    if self._main_text.x_offset is None and self._main_text.y_offset is None:
                        click_pos = QPoint(self._main_text.x + (self._main_text.width/2), self._main_text.y + (self._main_text.height/2))
                    else:
                        click_pos = QPoint(self._main_text.x + self._main_text.x_offset, self._main_text.y + self._main_text.y_offset)
                        
                    old_brush = qp.brush()
                        
                    qp.setBrush(QColor(255, 0, 255, 130))
                    qp.drawLine(self._main_text.x + (self._main_text.width/2), self._main_text.y + (self._main_text.height/2), click_pos.x(), click_pos.y())
                    qp.drawEllipse(click_pos, 5*self.scaling_factor, 5*self.scaling_factor)
                    qp.setBrush(old_brush)
            
            else:
                qp.fillRect(roi_x,
                    roi_y,
                    roi_width,
                    roi_height,
                    QBrush(QColor(255, 0, 255, 180), Qt.BDiagPattern))
                    
                qp.drawRect(QRect(roi_x,
                    roi_y,
                    roi_width,
                    roi_height))  
                
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
        
     
    def draw_sub_textangle(self, qp, text_finder, cnt):
    
            if text_finder.show is False:
                return
    
            pen = QPen()
            pen.setWidth(1)
            pen.setStyle(Qt.SolidLine)
            pen.setBrush(QBrush(QColor(255, 0, 198, 255)))
            qp.setPen(pen)
            
            OuterPath_roi = QPainterPath()
            OuterPath_roi.setFillRule(Qt.WindingFill)
            
            roi_x = text_finder.roi_x + self._main_text.x
            roi_y = text_finder.roi_y + self._main_text.y
            roi_width = text_finder.roi_width
            roi_height = text_finder.roi_height
            
            if text_finder.roi_unlimited_up is True:
                roi_y = 0
                roi_height = text_finder.roi_y + self._main_text.y + roi_height

            if text_finder.roi_unlimited_down is True:
                if text_finder.roi_unlimited_up is True:
                    roi_height = self._bg_pixmap.height()-1
                else:
                    roi_height = self._bg_pixmap.height() - (text_finder.roi_y + self._main_text.y + 1)
                    
                    #print self._bg_pixmap.width(), (text_finder.roi_x + self._main_text.x)

            if text_finder.roi_unlimited_left is True:
                roi_x = 0
                roi_width = text_finder.roi_x + self._main_text.x + roi_width

            if text_finder.roi_unlimited_right is True:
                if text_finder.roi_unlimited_left is True:
                    roi_width = self._bg_pixmap.width() -1
                else:
                    roi_width = self._bg_pixmap.width() - (text_finder.roi_x + self._main_text.x + 1)
            
            OuterPath_roi.addRect(roi_x,
                    roi_y,
                    roi_width,
                    roi_height)
                
            if text_finder.x != 0 and text_finder.y != 0:
            
                InnerPath_roi = QPainterPath()
                
                """
                InnerPath_roi.addRect(text_finder.x,
                    text_finder.y,
                    text_finder.width,
                    text_finder.height)
                """
                
                font = qp.font()
                font.setPixelSize(11 * self.scaling_factor);

                qp.setFont(font)
                qp.drawText( QPoint(text_finder.x -1, text_finder.y -(6*self.scaling_factor)), str(cnt) )

                InnerPath_roi.addRect(text_finder.x,
                    text_finder.y,
                    text_finder.width,
                    text_finder.height)
                    
                                            
                FillPath_roi = OuterPath_roi.subtracted(InnerPath_roi)
                qp.fillPath(FillPath_roi, QBrush(QColor(172, 96, 246, 180), Qt.BDiagPattern))
                
                qp.drawRect(QRect(roi_x,
                    roi_y,
                    roi_width,
                    roi_height))   
                    
                qp.fillRect(text_finder.x,
                    text_finder.y,
                    text_finder.width,
                    text_finder.height,
                    QBrush(QColor(172, 96, 246, 130)))
                
                    
                qp.drawRect(QRect(text_finder.x,
                    text_finder.y,
                    text_finder.width,
                    text_finder.height))
                    
                if text_finder.click is True or text_finder.rightclick is True or text_finder.mousemove is True or text_finder.hold_and_release is not None:
                        
                    
                    if text_finder.x_offset is None and text_finder.y_offset is None:
                        click_pos = QPoint(text_finder.x + (text_finder.width/2), text_finder.y + (text_finder.height/2))
                    else:
                        click_pos = QPoint(text_finder.x + text_finder.x_offset, text_finder.y + text_finder.y_offset)
                        
                    old_brush = qp.brush()
                        
                    qp.setBrush(QColor(172, 96, 246, 130))
                    qp.drawLine(text_finder.x + (text_finder.width/2), text_finder.y + (text_finder.height/2), click_pos.x(), click_pos.y())
                    qp.drawEllipse(click_pos, 5*self.scaling_factor, 5*self.scaling_factor)
                    qp.setBrush(old_brush)
            
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
        
    def draw_bounding_rects(self, qp):
            
        mouse_position = QPoint(QCursor.pos())
        
        pen = QPen()
        pen.setWidth(1)
        pen.setStyle(Qt.SolidLine)
        
        m_x = None
        m_y = None
        m_w = None
        m_h = None
        
        if self._main_text is not None:
            m_x = self._main_text.x
            m_y = self._main_text.y
            m_w = self._main_text.width
            m_h = self._main_text.height
        
                    
        for box in self._textBoxes:

        
            x, y, w, h = box
            
            is_in_objects = False
            
                        
            if x == m_x and y == m_y and w == m_w and h == m_h:
                is_in_objects = True
            
            for sub_box in self._sub_texts_finder:
            
                if is_in_objects is True:
                    break
                    
                s_x = sub_box.x
                s_y = sub_box.y
                s_w = sub_box.width
                s_h = sub_box.height
                
                if x == s_x and y == s_y and w == s_w and h == s_h:
                    is_in_objects = True
                    break

            if is_in_objects is True:
                pen.setBrush(QBrush(QColor(255, 0, 0, 255)))
                qp.setPen(pen)
                
                qp.fillRect(x + 1,
                    y + 1,
                    w - 1,
                    h - 1,
                    QBrush(QColor(255, 0, 255, 130)))
                    
            else:
            
                pen.setBrush(QBrush(QColor(0, 255, 0, 255)))

                qp.setPen(pen)
                
                qp.fillRect(x + 1,
                    y + 1,
                    w - 1,
                    h - 1,
                    QBrush(QColor(32, 178, 170, 100)))
                    
            rect = QRect(x, y,
                w, h)
            
            qp.drawRect(rect)
            
    def add_rect_from_boundings_rects(self, rect):
        x, y, width, height = rect
        
        if self._main_text is None or (self._main_text.x == 0 and self._main_text.y == 0 and self._main_text.width == 0 and self._main_text.height == 0):
        

            self.last_xy_offset_index = None
            text_finder = MainTextForGui()
            
            """
            self.__flag_capturing_main_text_rect = False
            self.__flag_capturing_main_text_rect_roi = False
            self.__flag_capturing_sub_text_rect_roi = True
            """
            
            self.__flag_need_to_delete_main_roi = False
            self.__flag_need_to_restore_main_roi = False
            self.__flag_need_to_restore_main_text_rect = False
            self.__flag_need_to_delete_roi = False
            self.__flag_need_to_restore_roi = False
            
            self.__flag_capturing_main_text_rect_roi = False
            self.__flag_capturing_main_text_rect = True
            self.__flag_need_to_delete_main_roi = True     

            self.__flag_capturing_main_text_rect = False
            self.__flag_capturing_sub_text_rect_roi = True
            self.__flag_need_to_delete_main_roi = False

            self._sub_texts_finder = []
            self.__deleted_texts = []
            
        else:
            text_finder = SubTextForGui()   
            self.__flag_capturing_sub_text_rect_roi = False
            self.__flag_capturing_sub_text = True
            self.__flag_need_to_delete_roi = True

            self.__flag_capturing_sub_text = False
            self.__flag_capturing_sub_text_rect_roi = True
            self.__flag_need_to_delete_roi = False
            
            if len(self.__deleted_texts) > 0:
                del self.__deleted_texts[-1]
        
        text_finder.x = x
        text_finder.y = y
        text_finder.height = height
        text_finder.width = width
        text_finder.min_height = height/2
        text_finder.max_height = height*2
        text_finder.min_width = width/2
        text_finder.max_width = width*2
        """
        percentage_screen_w = int(0.1 * self._bg_pixmap.width())
        percentage_screen_h = int(0.1 * self._bg_pixmap.height())
        percentage_object_w = int(0.5 * text_finder.width)
        percentage_object_h = int(0.5 * text_finder.height)

        roi_height = percentage_screen_h + percentage_object_h + text_finder.height

        roi_width = percentage_screen_w + percentage_object_w + text_finder.width

        roi_width_half = int((roi_width - text_finder.width)/2)
        roi_height_half = int((roi_height - text_finder.height)/2)
        
        """


        if self._main_text is None or (self._main_text.x == 0 and self._main_text.y == 0 and self._main_text.width == 0 and self._main_text.height == 0):

            """                    
            text_finder.roi_x =  (text_finder.x) - int(1*self.scaling_factor)
            text_finder.roi_y =  (text_finder.y) - int(1*self.scaling_factor)
            text_finder.roi_height = text_finder.height + int(6*self.scaling_factor)
            text_finder.roi_width = text_finder.width + int(6*self.scaling_factor)
            """
             
            """
            text_finder.roi_x =  text_finder.x - roi_width_half
            text_finder.roi_y =  text_finder.y - roi_height_half
            text_finder.roi_height = roi_height
            text_finder.roi_width = roi_width

            """
            
                                
            hw_factor = 0
                                
            if text_finder.height < text_finder.width:
                hw_factor = text_finder.height
            else:
                hw_factor = text_finder.width
                
                
            sc_factor = 0
                                
            if self._bg_pixmap.height() < self._bg_pixmap.width():
                sc_factor = self._bg_pixmap.height()
            else:
                sc_factor = self._bg_pixmap.width()
                
            percentage_screen_w = int(0.0125 * sc_factor)
            percentage_screen_h = int(0.0125 * sc_factor)
            percentage_object_w = int(0.2 * hw_factor) #text_finder.width)
            percentage_object_h = int(0.2 * hw_factor) #text_finder.height)
            
            roi_height = percentage_screen_h + percentage_object_h + text_finder.height
            
            roi_width = percentage_screen_w + percentage_object_w + text_finder.width
            
            """
            hw_factor = 0
            
            if text_finder.height < text_finder.width:
                hw_factor = text_finder.height
            else:
                hw_factor = text_finder.width
                
            roi_height = int(0.95 * hw_factor) + text_finder.height

            roi_width = int(0.95 * hw_factor) + text_finder.width
            """

            roi_width_half = int((roi_width - text_finder.width)/2)

            roi_height_half = int((roi_height - text_finder.height)/2)


            text_finder.roi_x =  text_finder.x - roi_width_half
            text_finder.roi_y =  text_finder.y - roi_height_half
            text_finder.roi_height = roi_height
            text_finder.roi_width = roi_width
            
            """
            roi_height = int(0.30*hw_factor*self.scaling_factor) + text_finder.height #int(10*self.scaling_factor) + text_finder.height

            roi_width = int(0.30*hw_factor*self.scaling_factor) + text_finder.width #int(10*self.scaling_factor) + text_finder.width


            roi_width_half = int((roi_width - text_finder.width)/2)
            roi_height_half = int((roi_height - text_finder.height)/2)

            text_finder.roi_x =  text_finder.x - roi_width_half
            text_finder.roi_y =  text_finder.y - roi_height_half
            text_finder.roi_height = roi_height
            text_finder.roi_width = roi_width
            """
            
            
            if text_finder.roi_y < 0:
            
                under_zero = abs(text_finder.roi_y)
                text_finder.roi_y = text_finder.roi_y + under_zero
                text_finder.roi_height = text_finder.roi_height - under_zero
                
            
            if text_finder.roi_y + text_finder.roi_height > self._bg_pixmap.height():
            
                diff = (text_finder.roi_y + text_finder.roi_height) - self._bg_pixmap.height()
                
                text_finder.roi_height = text_finder.roi_height - diff - 1
            
            
            if text_finder.roi_x < 0:
            
                under_zero = abs(text_finder.roi_x)
                text_finder.roi_x = text_finder.roi_x + under_zero
                text_finder.roi_width = text_finder.roi_width - under_zero
                
            
            if text_finder.roi_x + text_finder.roi_width > self._bg_pixmap.width():
            
                diff = (text_finder.roi_x + text_finder.roi_width) - self._bg_pixmap.width()
                
                text_finder.roi_width = text_finder.roi_width - diff - 1


            
            self._main_text = text_finder
            
        else: 
               
            """
            text_finder.roi_x =  (text_finder.x - self._main_text.x) - int(1*self.scaling_factor)
            text_finder.roi_y =  (text_finder.y - self._main_text.y) - int(1*self.scaling_factor)
            text_finder.roi_height = text_finder.height + int(6*self.scaling_factor)
            text_finder.roi_width = text_finder.width + int(6*self.scaling_factor)
            """

            """
            text_finder.roi_x =  (text_finder.x - self._main_text.x) - roi_width_half
            text_finder.roi_y =  (text_finder.y - self._main_text.y) - roi_height_half
            text_finder.roi_height = roi_height
            text_finder.roi_width = roi_width
            """
            
            hw_factor = 0
                                
            if text_finder.height < text_finder.width:
                hw_factor = text_finder.height
            else:
                hw_factor = text_finder.width
                
                
            sc_factor = 0
                                
            if self._bg_pixmap.height() < self._bg_pixmap.width():
                sc_factor = self._bg_pixmap.height()
            else:
                sc_factor = self._bg_pixmap.width()
                
            percentage_screen_w = int(0.0125 * sc_factor)
            percentage_screen_h = int(0.0125 * sc_factor)
            percentage_object_w = int(0.2 * hw_factor) #text_finder.width)
            percentage_object_h = int(0.2 * hw_factor) #text_finder.height)
            
            roi_height = percentage_screen_h + percentage_object_h + text_finder.height
            
            roi_width = percentage_screen_w + percentage_object_w + text_finder.width
            
            """
            
            hw_factor = 0
            
            if text_finder.height < text_finder.width:
                hw_factor = text_finder.height
            else:
                hw_factor = text_finder.width
                

            roi_height = int(0.95 * hw_factor) + text_finder.height

            roi_width = int(0.95 * hw_factor) + text_finder.width
            """


            roi_width_half = int((roi_width - text_finder.width)/2)

            roi_height_half = int((roi_height - text_finder.height)/2)


            text_finder.roi_x =  (text_finder.x - self._main_text.x) - roi_width_half
            text_finder.roi_y =  (text_finder.y - self._main_text.y) - roi_height_half
            text_finder.roi_height = text_finder.height + (roi_height_half*2)
            text_finder.roi_width = text_finder.width + (roi_width_half*2)

            """
            roi_height = int(0.30*hw_factor*self.scaling_factor) + text_finder.height #int(10*self.scaling_factor) + text_finder.height

            roi_width = int(0.30*hw_factor*self.scaling_factor) + text_finder.width #int(10*self.scaling_factor) + text_finder.width

            roi_width_half = int((roi_width - text_finder.width)/2)
            roi_height_half = int((roi_height - text_finder.height)/2)

            text_finder.roi_x =  (text_finder.x - self._main_text.x) - roi_width_half
            text_finder.roi_y =  (text_finder.y - self._main_text.y) - roi_height_half
            text_finder.roi_height = roi_height
            text_finder.roi_width = roi_width
            """
            
            if self._main_text.y + text_finder.roi_y < 0:
                    
                under_zero = abs(self._main_text.y + text_finder.roi_y)
                text_finder.roi_y = text_finder.roi_y + under_zero
                text_finder.roi_height = text_finder.roi_height - under_zero
                
            
            if self._main_text.y + text_finder.roi_y + text_finder.roi_height > self._bg_pixmap.height():
            
                diff = (self._main_text.y + text_finder.roi_y + text_finder.roi_height) - self._bg_pixmap.height()
                
                text_finder.roi_height = text_finder.roi_height - diff - 1
                
            if self._main_text.x + text_finder.roi_x < 0:
            
                under_zero = abs(self._main_text.x + text_finder.roi_x)
                text_finder.roi_x = text_finder.roi_x + under_zero
                text_finder.roi_width = text_finder.roi_width - under_zero
                
            
            if self._main_text.x + text_finder.roi_x + text_finder.roi_width > self._bg_pixmap.width():
            
                diff = (self._main_text.x + text_finder.roi_x + text_finder.roi_width) - self._bg_pixmap.width()
                
                text_finder.roi_width = text_finder.roi_width - diff - 1
                                
            self._sub_texts_finder.append(text_finder)
            
        
    
    def add_main_rect(self):
    
        rect_attributes = self.convert_mouse_position_into_rect()
        
        if rect_attributes is not None:
        
            x, y, width, height = rect_attributes
            
            roi_x = self._main_text.roi_x
            roi_y = self._main_text.roi_y
            roi_width = self._main_text.roi_width
            roi_height = self._main_text.roi_height

            if self._main_text.roi_unlimited_up is True:
                roi_y = 0
                roi_height = self._main_text.roi_y + roi_height

            if self._main_text.roi_unlimited_down is True:
                if self._main_text.roi_unlimited_up is True:
                    roi_height = self._bg_pixmap.height()-1
                else:
                    roi_height = self._bg_pixmap.height() - (self._main_text.roi_y + 1)
                    

            if self._main_text.roi_unlimited_left is True:
                roi_x = 0
                roi_width = self._main_text.roi_x + roi_width

            if self._main_text.roi_unlimited_right is True:
                if self._main_text.roi_unlimited_left is True:
                    roi_width = self._bg_pixmap.width() -1
                else:
                    roi_width = self._bg_pixmap.width() - (self._main_text.roi_x + 1)
            
            if (x + width > roi_x + roi_width) or (x < roi_x) or \
                (y + height > roi_y + roi_height) or (y < roi_y):
                self.__flag_capturing_main_text_rect = True
                self.__flag_capturing_main_text_rect_roi = False
                return
        
            #text_finder = MainTextForGui()
            self._main_text.x = x
            self._main_text.y = y
            self._main_text.height = height
            self._main_text.width = width
            
            self._sub_texts_finder = []
            self.__deleted_texts = []
            
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
            
            roi_x = text_finder.roi_x + self._main_text.x
            roi_y = text_finder.roi_y + self._main_text.y
            roi_width = text_finder.roi_width
            roi_height = text_finder.roi_height

            if text_finder.roi_unlimited_up is True:
                roi_y = 0
                roi_height = text_finder.roi_y + self._main_text.y + roi_height

            if text_finder.roi_unlimited_down is True:
                if text_finder.roi_unlimited_up is True:
                    roi_height = self._bg_pixmap.height()-1
                else:
                    roi_height = self._bg_pixmap.height() - (text_finder.roi_y + self._main_text.y + 1)
                    
                    #print self._bg_pixmap.width(), (text_finder.roi_x + self._main_text.x)

            if text_finder.roi_unlimited_left is True:
                roi_x = 0
                roi_width = text_finder.roi_x + self._main_text.x + roi_width

            if text_finder.roi_unlimited_right is True:
                if text_finder.roi_unlimited_left is True:
                    roi_width = self._bg_pixmap.width() -1
                else:
                    roi_width = self._bg_pixmap.width() - (text_finder.roi_x + self._main_text.x + 1)
            
            if (x + width > roi_x + roi_width) or (x < roi_x) or \
                (y + height > roi_y + roi_height) or (y < roi_y):
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
        
                
        if self._dont_build_rect is True:
            self._dont_build_rect = False
            return
        
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
            if  self._sub_texts_finder[index].x != 0 and self._sub_texts_finder[index].y != 0 \
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
        
            #self._sub_texts_finder = []
            #self.__deleted_texts = []
            self.__deleted_texts.append(self._main_text)
            self._main_text = None
            #print "deleted main"
            self.__flag_need_to_delete_main_roi = False
            self.__flag_need_to_restore_main_roi = True
            self.__flag_capturing_main_text_rect_roi = True
            self.__flag_capturing_main_text_rect = False
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
            file_code_string = file_code_string.replace(unicode(self.__old_code_v230, 'utf-8'), current_code_string)
            file_code_string = file_code_string.replace(unicode(self.__old_code_v250, 'utf-8'), current_code_string)
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
        
    def get_old_code_v230(self):
        if self._main_text is None:
            return "".encode('utf-8')
        
        self.build_code_array_v230()
        return self.build_code_string()
        
    def get_old_code_v250(self):
        if self._main_text is None:
            return "".encode('utf-8')
        
        self.build_code_array_v250()
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
        
        if self._main_text.click == True or self._main_text.rightclick == True or self._main_text.mousemove == True:
        
            self._code_lines.append("    main_text_pos = " + name + "_object.get_result(0)")  
        
            if mmanager_declared is False:
                self._code_lines.append("    m = MouseManager()")
                mmanager_declared = True
                
            self._code_lines.append("    time.sleep(2)")
                                
            if self._main_text.click == True and self._main_text.number_of_clicks == 1:
                self._code_lines.append("    m.click(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2), 1)")
            elif self._main_text.click == True and self._main_text.number_of_clicks == 2:
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
                if sub_text.click == True or sub_text.rightclick == True or sub_text.mousemove == True:
            
                    self._code_lines.append("    sub_text_" + str(cnt) + "_pos = " + name + "_object.get_result(0, " + str(cnt) + ")")  
                
                    if mmanager_declared is False:
                        self._code_lines.append("    m = MouseManager()")
                        mmanager_declared = True
                    self._code_lines.append("    time.sleep(2)")
                                        
                    if sub_text.click == True and sub_text.number_of_clicks == 1:
                        self._code_lines.append("    m.click(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2), 1)")
                    elif sub_text.click == True and sub_text.number_of_clicks == 2:
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
        
    def build_code_array_v230(self):
    
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
                                
            if self._main_text.click == True and self._main_text.number_of_clicks == 1:
                self._code_lines.append("    m.click(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2), 1)")
            elif self._main_text.click == True and self._main_text.number_of_clicks == 2:
                self._code_lines.append("    m.click(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2), 1, 2)")
            elif self._main_text.rightclick == True:
                self._code_lines.append("    m.click(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2), 2)")
            elif self._main_text.mousemove == True:
                self._code_lines.append("    m.move(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2))")

                
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
                                        
                    if sub_text.click == True and sub_text.number_of_clicks == 1:
                        self._code_lines.append("    m.click(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2), 1)")
                    elif sub_text.click == True and sub_text.number_of_clicks == 2:
                        self._code_lines.append("    m.click(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2), 1, 2)")
                    elif sub_text.rightclick == True:
                        self._code_lines.append("    m.click(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2), 2)")
                    elif sub_text.mousemove == True:
                        self._code_lines.append("    m.move(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2))")
                        
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
        
    def build_code_array_v240(self):
    
        self.mouse_or_key_is_set = False
    
        kmanager_declared = False
        mmanager_declared = False
       
        if self._main_text is None:
            return
            
        self._code_lines = []
        self._code_lines_for_object_finder = []
            
        name = self.object_name
        
        if name == "" and self.ok_pressed is True:
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
        
             
        if self._main_text.click == True or self._main_text.rightclick == True or self._main_text.mousemove == True or self._main_text.hold_and_release is not None:
            if self._main_text.x_offset is None and self._main_text.y_offset is None: 
                if self._main_text.hold_and_release is not None:
                    if self._main_text.hold_and_release == 0:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
                    elif self._main_text.hold_and_release == 1:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
                    elif self._main_text.hold_and_release == 2:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0, 0 - " + str(self._main_text.release_pixel) + ", False)")
                    elif self._main_text.hold_and_release == 3:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0, 0 + " + str(self._main_text.release_pixel) + ", False)")
                    elif self._main_text.hold_and_release == 4:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0 - " + str(self._main_text.release_pixel) + ", 0, False)")
                    elif self._main_text.hold_and_release == 5:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0 + " + str(self._main_text.release_pixel) + ", 0, False)")
                else:
                    self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                    self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
            else:
                if self._main_text.hold_and_release is not None:
                    if self._main_text.hold_and_release == 0:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_text.x_offset) + "), 0 + (" + str(self._main_text.y_offset) + "), True)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
                    elif self._main_text.hold_and_release == 1:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_text.x_offset) + "), 0 + (" + str(self._main_text.y_offset) + "), True)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
                    elif self._main_text.hold_and_release == 2:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_text.x_offset) + "), 0 + (" + str(self._main_text.y_offset) + "), True)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0 + (" + str(self._main_text.x_offset) + "), 0 + (" + str(self._main_text.y_offset) + ") - " + str(self._main_text.release_pixel) + ", True)")
                    elif self._main_text.hold_and_release == 3:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_text.x_offset) + "), 0 + (" + str(self._main_text.y_offset) + "), True)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0 + (" + str(self._main_text.x_offset) + "), 0 + (" + str(self._main_text.y_offset) + ") + " + str(self._main_text.release_pixel) + ", True)")
                    elif self._main_text.hold_and_release == 4:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_text.x_offset) + "), 0 + (" + str(self._main_text.y_offset) + "), True)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0 + (" + str(self._main_text.x_offset) + ") - " + str(self._main_text.release_pixel) + ",  0 + (" + str(self._main_text.y_offset) + "), True)")
                    elif self._main_text.hold_and_release == 5:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_text.x_offset) + "), 0 + (" + str(self._main_text.y_offset) + "), True)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0 + (" + str(self._main_text.x_offset) + ") + " + str(self._main_text.release_pixel) + ",  0 + (" + str(self._main_text.y_offset) + "), True)")
                else:
                    self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_text.x_offset) + "), 0 + (" + str(self._main_text.y_offset) + "), True)")
                    self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
        else:
            self._code_lines.append("    "  + name + "_object.main_xy_coordinates = None")
            self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
        
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
                
                if sub_text.click == True or sub_text.rightclick == True or sub_text.mousemove == True or sub_text.hold_and_release is not None:
                    if sub_text.x_offset is None and sub_text.y_offset is None: 
                        if sub_text.hold_and_release is not None:
                            if sub_text.hold_and_release == 0:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0, False))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")
                            elif sub_text.hold_and_release == 1:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0, False))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")
                            elif sub_text.hold_and_release == 2:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0, False))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0, 0 - " + str(sub_text.release_pixel) + ", False))")
                            elif sub_text.hold_and_release == 3:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0, 0 + " + str(sub_text.release_pixel) + ", False))")
                            elif sub_text.hold_and_release == 4:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0 - " + str(sub_text.release_pixel) + ", 0, False))")
                            elif sub_text.hold_and_release == 5:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0 + " + str(sub_text.release_pixel) + ", 0, False))")
                        else:
                            self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0, False))")
                            self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")
                    else:
                        if sub_text.hold_and_release is not None:
                            if sub_text.hold_and_release == 0:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_text.x_offset) + "), 0 + (" + str(sub_text.y_offset) + "), True))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")
                            elif sub_text.hold_and_release == 1:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_text.x_offset) + "), 0 + (" + str(sub_text.y_offset) + "), True))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")
                            elif sub_text.hold_and_release == 2:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_text.x_offset) + "), 0 + (" + str(sub_text.y_offset) + "), True))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0 + (" + str(sub_text.x_offset) + "), 0 + (" + str(sub_text.y_offset) + ") - " + str(sub_text.release_pixel) + ", True))")
                            elif sub_text.hold_and_release == 3:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_text.x_offset) + "), 0 + (" + str(sub_text.y_offset) + ")))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0 + (" + str(sub_text.x_offset) + "), 0 + (" + str(sub_text.y_offset) + ") + " + str(sub_text.release_pixel) + ", True))")
                            elif sub_text.hold_and_release == 4:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_text.x_offset) + "), 0 + (" + str(sub_text.y_offset) + ")))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0 + (" + str(sub_text.x_offset) + ") - " + str(sub_text.release_pixel) + ",  0 + (" + str(sub_text.y_offset) + "), True))")
                            elif sub_text.hold_and_release == 5:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_text.x_offset) + "), 0 + (" + str(sub_text.y_offset) + ")))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0 + (" + str(sub_text.x_offset) + ") + " + str(sub_text.release_pixel) + ",  0 + (" + str(sub_text.y_offset) + "), True))")
                        else:
                            self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_text.x_offset) + "), 0 + (" + str(sub_text.y_offset) + "), True))")
                            self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")
                else:
                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append(None)")
                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")
    
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
        
        if self._main_text.click == True or self._main_text.rightclick == True or self._main_text.mousemove == True or self._main_text.hold_and_release is not None:
        
            self.mouse_or_key_is_set = True
        
            self._code_lines.append("    main_text_pos = " + name + "_object.get_result(0)")  
        
            if mmanager_declared is False:
                self._code_lines.append("    m = MouseManager()")
                mmanager_declared = True
                
            self._code_lines.append("    time.sleep(sleep_factor)")
            
            if self._main_text.x_offset is None and self._main_text.y_offset is None:             
                if self._main_text.click == True:
                    self._code_lines.append("    m.click_2(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2), 1, " + str(self._main_text.number_of_clicks) + ", " + str(self._main_text.click_delay) + ")")
                elif self._main_text.rightclick == True:
                    self._code_lines.append("    m.click(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2), 2)")
                elif self._main_text.mousemove == True:
                    self._code_lines.append("    m.move(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2))")
                elif self._main_text.hold_and_release is not None:
                    if self._main_text.hold_and_release == 0:
                        self._code_lines.append("    m.hold(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2))")
                    elif self._main_text.hold_and_release == 1:
                        self._code_lines.append("    m.release(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2))")
                    elif self._main_text.hold_and_release == 2:
                        self._code_lines.append("    m.hold(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2))")
                        self._code_lines.append("    time.sleep(sleep_factor)")
                        self._code_lines.append("    m.release(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2) - " + str(self._main_text.release_pixel) + ")")
                    elif self._main_text.hold_and_release == 3:
                        self._code_lines.append("    m.hold(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2))")
                        self._code_lines.append("    time.sleep(sleep_factor)")
                        self._code_lines.append("    m.release(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2) + " + str(self._main_text.release_pixel) + ")")
                    elif self._main_text.hold_and_release == 4:
                        self._code_lines.append("    m.hold(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2))")
                        self._code_lines.append("    time.sleep(sleep_factor)")
                        self._code_lines.append("    m.release(main_text_pos.x + (main_text_pos.width/2) - " + str(self._main_text.release_pixel) + ", main_text_pos.y + (main_text_pos.height/2))")
                    elif self._main_text.hold_and_release == 5:
                        self._code_lines.append("    m.hold(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2))")
                        self._code_lines.append("    time.sleep(sleep_factor)")
                        self._code_lines.append("    m.release(main_text_pos.x + (main_text_pos.width/2) + " + str(self._main_text.release_pixel) + ", main_text_pos.y + (main_text_pos.height/2))")
            else:
                if self._main_text.click == True:
                    self._code_lines.append("    m.click_2(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + "), 1, " + str(self._main_text.number_of_clicks) + ", " + str(self._main_text.click_delay) + ")")
                elif self._main_text.rightclick == True:
                    self._code_lines.append("    m.click(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + "), 2)")
                elif self._main_text.mousemove == True:
                    self._code_lines.append("    m.move(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + "))")
                elif self._main_text.hold_and_release is not None:
                    if self._main_text.hold_and_release == 0:
                        self._code_lines.append("    m.hold(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + "))")
                    elif self._main_text.hold_and_release == 1:
                        self._code_lines.append("    m.release(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + "))")
                    elif self._main_text.hold_and_release == 2:
                        self._code_lines.append("    m.hold(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + "))")
                        self._code_lines.append("    time.sleep(sleep_factor)")
                        self._code_lines.append("    m.release(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + ") - " + str(self._main_text.release_pixel) + ")")
                    elif self._main_text.hold_and_release == 3:
                        self._code_lines.append("    m.hold(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + "))")
                        self._code_lines.append("    time.sleep(sleep_factor)")
                        self._code_lines.append("    m.release(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + ") + " + str(self._main_text.release_pixel) + ")")
                    elif self._main_text.hold_and_release == 4:
                        self._code_lines.append("    m.hold(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + "))")
                        self._code_lines.append("    time.sleep(sleep_factor)")
                        self._code_lines.append("    m.release(main_text_pos.x + (" + str(self._main_text.x_offset) + ") - " + str(self._main_text.release_pixel) + ",  main_text_pos.y + (" + str(self._main_text.y_offset) + "))")
                    elif self._main_text.hold_and_release == 5:
                        self._code_lines.append("    m.hold(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + "))")
                        self._code_lines.append("    time.sleep(sleep_factor)")
                        self._code_lines.append("    m.release(main_text_pos.x + (" + str(self._main_text.x_offset) + ") + " + str(self._main_text.release_pixel) + ",  main_text_pos.y + (" + str(self._main_text.y_offset) + "))")
                
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
                if sub_text.click == True or sub_text.rightclick == True or sub_text.mousemove == True or sub_text.hold_and_release is not None:
                
                    self.mouse_or_key_is_set = True
            
                    self._code_lines.append("    sub_text_" + str(cnt) + "_pos = " + name + "_object.get_result(0, " + str(cnt) + ")")  
                
                    if mmanager_declared is False:
                        self._code_lines.append("    m = MouseManager()")
                        mmanager_declared = True
                    self._code_lines.append("    time.sleep(sleep_factor)")
                                      
                    if sub_text.x_offset is None and sub_text.y_offset is None:     
                        if sub_text.click == True:
                            self._code_lines.append("    m.click_2(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2), 1, " + str(sub_text.number_of_clicks) + ", " + str(sub_text.click_delay) + ")")
                        elif sub_text.rightclick == True:
                            self._code_lines.append("    m.click(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2), 2)")
                        elif sub_text.mousemove == True:
                            self._code_lines.append("    m.move(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2))")
                        elif sub_text.hold_and_release is not None:
                            if sub_text.hold_and_release == 0:
                                self._code_lines.append("    m.hold(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2))")
                            elif sub_text.hold_and_release == 1:
                                self._code_lines.append("    m.release(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2))")
                            elif sub_text.hold_and_release == 2:
                                self._code_lines.append("    m.hold(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2))")
                                self._code_lines.append("    time.sleep(sleep_factor)")
                                self._code_lines.append("    m.release(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2) - " + str(sub_text.release_pixel) + ")")
                            elif sub_text.hold_and_release == 3:
                                self._code_lines.append("    m.hold(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2))")
                                self._code_lines.append("    time.sleep(sleep_factor)")
                                self._code_lines.append("    m.release(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2) + " + str(sub_text.release_pixel) + ")")
                            elif sub_text.hold_and_release == 4:
                                self._code_lines.append("    m.hold(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2))")
                                self._code_lines.append("    time.sleep(sleep_factor)")
                                self._code_lines.append("    m.release(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2) - " + str(sub_text.release_pixel) + ", sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2))")
                            elif sub_text.hold_and_release == 5:
                                self._code_lines.append("    m.hold(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2))")
                                self._code_lines.append("    time.sleep(sleep_factor)")
                                self._code_lines.append("    m.release(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2) + " + str(sub_text.release_pixel) + ", sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2))")
                    else:
                        if sub_text.click == True:
                            self._code_lines.append("    m.click_2(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "), 1, " + str(sub_text.number_of_clicks) + ", " + str(sub_text.click_delay) + ")")
                        elif sub_text.rightclick == True:
                            self._code_lines.append("    m.click(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "), 2)")
                        elif sub_text.mousemove == True:
                            self._code_lines.append("    m.move(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "))")
                        elif sub_text.hold_and_release is not None:
                            if sub_text.hold_and_release == 0:
                                self._code_lines.append("    m.hold(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "))")
                            elif sub_text.hold_and_release == 1:
                                self._code_lines.append("    m.release(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "))")
                            elif sub_text.hold_and_release == 2:
                                self._code_lines.append("    m.hold(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "))")
                                self._code_lines.append("    time.sleep(sleep_factor)")
                                self._code_lines.append("    m.release(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + ") - " + str(sub_text.release_pixel) + ")")
                            elif sub_text.hold_and_release == 3:
                                self._code_lines.append("    m.hold(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "))")
                                self._code_lines.append("    time.sleep(sleep_factor)")
                                self._code_lines.append("    m.release(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + ") + " + str(sub_text.release_pixel) + ")")
                            elif sub_text.hold_and_release == 4:
                                self._code_lines.append("    m.hold(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "))")
                                self._code_lines.append("    time.sleep(sleep_factor)")
                                self._code_lines.append("    m.release(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + ") - " + str(sub_text.release_pixel) + ",  sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "))")
                            elif sub_text.hold_and_release == 5:
                                self._code_lines.append("    m.hold(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "))")
                                self._code_lines.append("    time.sleep(sleep_factor)")
                                self._code_lines.append("    m.release(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + ") + " + str(sub_text.release_pixel) + ",  sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "))")
                        
                         
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
        
    def build_code_array_v250(self):
    
        self.mouse_or_key_is_set = False
    
        kmanager_declared = False
        mmanager_declared = False
       
        if self._main_text is None:
            return
            
        self._code_lines = []
        self._code_lines_for_object_finder = []
            
        name = self.object_name
        
        if name == "" and self.ok_pressed is True:
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
        
             
        if self.scraper is False:
            if self._main_text.click == True or self._main_text.rightclick == True or self._main_text.mousemove == True or self._main_text.hold_and_release is not None:
                if self._main_text.x_offset is None and self._main_text.y_offset is None: 
                    if self._main_text.hold_and_release is not None:
                        if self._main_text.hold_and_release == 0:
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
                        elif self._main_text.hold_and_release == 1:
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
                        elif self._main_text.hold_and_release == 2:
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0, 0 - " + str(self._main_text.release_pixel) + ", False)")
                        elif self._main_text.hold_and_release == 3:
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0, 0 + " + str(self._main_text.release_pixel) + ", False)")
                        elif self._main_text.hold_and_release == 4:
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0 - " + str(self._main_text.release_pixel) + ", 0, False)")
                        elif self._main_text.hold_and_release == 5:
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0 + " + str(self._main_text.release_pixel) + ", 0, False)")
                    else:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
                else:
                    if self._main_text.hold_and_release is not None:
                        if self._main_text.hold_and_release == 0:
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_text.x_offset) + "), 0 + (" + str(self._main_text.y_offset) + "), True)")
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
                        elif self._main_text.hold_and_release == 1:
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_text.x_offset) + "), 0 + (" + str(self._main_text.y_offset) + "), True)")
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
                        elif self._main_text.hold_and_release == 2:
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_text.x_offset) + "), 0 + (" + str(self._main_text.y_offset) + "), True)")
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0 + (" + str(self._main_text.x_offset) + "), 0 + (" + str(self._main_text.y_offset) + ") - " + str(self._main_text.release_pixel) + ", True)")
                        elif self._main_text.hold_and_release == 3:
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_text.x_offset) + "), 0 + (" + str(self._main_text.y_offset) + "), True)")
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0 + (" + str(self._main_text.x_offset) + "), 0 + (" + str(self._main_text.y_offset) + ") + " + str(self._main_text.release_pixel) + ", True)")
                        elif self._main_text.hold_and_release == 4:
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_text.x_offset) + "), 0 + (" + str(self._main_text.y_offset) + "), True)")
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0 + (" + str(self._main_text.x_offset) + ") - " + str(self._main_text.release_pixel) + ",  0 + (" + str(self._main_text.y_offset) + "), True)")
                        elif self._main_text.hold_and_release == 5:
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_text.x_offset) + "), 0 + (" + str(self._main_text.y_offset) + "), True)")
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0 + (" + str(self._main_text.x_offset) + ") + " + str(self._main_text.release_pixel) + ",  0 + (" + str(self._main_text.y_offset) + "), True)")
                    else:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_text.x_offset) + "), 0 + (" + str(self._main_text.y_offset) + "), True)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
            else:
                self._code_lines.append("    "  + name + "_object.main_xy_coordinates = None")
                self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
        
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
                    
                    if sub_text.click == True or sub_text.rightclick == True or sub_text.mousemove == True or sub_text.hold_and_release is not None:
                        if sub_text.x_offset is None and sub_text.y_offset is None: 
                            if sub_text.hold_and_release is not None:
                                if sub_text.hold_and_release == 0:
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0, False))")
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")
                                elif sub_text.hold_and_release == 1:
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0, False))")
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")
                                elif sub_text.hold_and_release == 2:
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0, False))")
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0, 0 - " + str(sub_text.release_pixel) + ", False))")
                                elif sub_text.hold_and_release == 3:
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0))")
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0, 0 + " + str(sub_text.release_pixel) + ", False))")
                                elif sub_text.hold_and_release == 4:
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0))")
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0 - " + str(sub_text.release_pixel) + ", 0, False))")
                                elif sub_text.hold_and_release == 5:
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0))")
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0 + " + str(sub_text.release_pixel) + ", 0, False))")
                            else:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0, False))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")
                        else:
                            if sub_text.hold_and_release is not None:
                                if sub_text.hold_and_release == 0:
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_text.x_offset) + "), 0 + (" + str(sub_text.y_offset) + "), True))")
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")
                                elif sub_text.hold_and_release == 1:
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_text.x_offset) + "), 0 + (" + str(sub_text.y_offset) + "), True))")
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")
                                elif sub_text.hold_and_release == 2:
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_text.x_offset) + "), 0 + (" + str(sub_text.y_offset) + "), True))")
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0 + (" + str(sub_text.x_offset) + "), 0 + (" + str(sub_text.y_offset) + ") - " + str(sub_text.release_pixel) + ", True))")
                                elif sub_text.hold_and_release == 3:
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_text.x_offset) + "), 0 + (" + str(sub_text.y_offset) + ")))")
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0 + (" + str(sub_text.x_offset) + "), 0 + (" + str(sub_text.y_offset) + ") + " + str(sub_text.release_pixel) + ", True))")
                                elif sub_text.hold_and_release == 4:
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_text.x_offset) + "), 0 + (" + str(sub_text.y_offset) + ")))")
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0 + (" + str(sub_text.x_offset) + ") - " + str(sub_text.release_pixel) + ",  0 + (" + str(sub_text.y_offset) + "), True))")
                                elif sub_text.hold_and_release == 5:
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_text.x_offset) + "), 0 + (" + str(sub_text.y_offset) + ")))")
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0 + (" + str(sub_text.x_offset) + ") + " + str(sub_text.release_pixel) + ",  0 + (" + str(sub_text.y_offset) + "), True))")
                            else:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_text.x_offset) + "), 0 + (" + str(sub_text.y_offset) + "), True))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")
                    else:
                        self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append(None)")
                        self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")
        
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
            
            if self._main_text.click == True or self._main_text.rightclick == True or self._main_text.mousemove == True or self._main_text.hold_and_release is not None:
            
                self.mouse_or_key_is_set = True
            
                self._code_lines.append("    main_text_pos = " + name + "_object.get_result(0)")  
            
                if mmanager_declared is False:
                    self._code_lines.append("    m = MouseManager()")
                    mmanager_declared = True
                    
                self._code_lines.append("    time.sleep(sleep_factor)")
                
                if self._main_text.x_offset is None and self._main_text.y_offset is None:             
                    if self._main_text.click == True:
                        self._code_lines.append("    m.click_2(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2), 1, " + str(self._main_text.number_of_clicks) + ", " + str(self._main_text.click_delay) + ")")
                    elif self._main_text.rightclick == True:
                        self._code_lines.append("    m.click(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2), 2)")
                    elif self._main_text.mousemove == True:
                        self._code_lines.append("    m.move(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2))")
                    elif self._main_text.hold_and_release is not None:
                        if self._main_text.hold_and_release == 0:
                            self._code_lines.append("    m.hold(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2))")
                        elif self._main_text.hold_and_release == 1:
                            self._code_lines.append("    m.release(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2))")
                        elif self._main_text.hold_and_release == 2:
                            self._code_lines.append("    m.hold(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2))")
                            self._code_lines.append("    time.sleep(sleep_factor)")
                            self._code_lines.append("    m.release(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2) - " + str(self._main_text.release_pixel) + ")")
                        elif self._main_text.hold_and_release == 3:
                            self._code_lines.append("    m.hold(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2))")
                            self._code_lines.append("    time.sleep(sleep_factor)")
                            self._code_lines.append("    m.release(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2) + " + str(self._main_text.release_pixel) + ")")
                        elif self._main_text.hold_and_release == 4:
                            self._code_lines.append("    m.hold(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2))")
                            self._code_lines.append("    time.sleep(sleep_factor)")
                            self._code_lines.append("    m.release(main_text_pos.x + (main_text_pos.width/2) - " + str(self._main_text.release_pixel) + ", main_text_pos.y + (main_text_pos.height/2))")
                        elif self._main_text.hold_and_release == 5:
                            self._code_lines.append("    m.hold(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2))")
                            self._code_lines.append("    time.sleep(sleep_factor)")
                            self._code_lines.append("    m.release(main_text_pos.x + (main_text_pos.width/2) + " + str(self._main_text.release_pixel) + ", main_text_pos.y + (main_text_pos.height/2))")
                else:
                    if self._main_text.click == True:
                        self._code_lines.append("    m.click_2(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + "), 1, " + str(self._main_text.number_of_clicks) + ", " + str(self._main_text.click_delay) + ")")
                    elif self._main_text.rightclick == True:
                        self._code_lines.append("    m.click(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + "), 2)")
                    elif self._main_text.mousemove == True:
                        self._code_lines.append("    m.move(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + "))")
                    elif self._main_text.hold_and_release is not None:
                        if self._main_text.hold_and_release == 0:
                            self._code_lines.append("    m.hold(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + "))")
                        elif self._main_text.hold_and_release == 1:
                            self._code_lines.append("    m.release(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + "))")
                        elif self._main_text.hold_and_release == 2:
                            self._code_lines.append("    m.hold(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + "))")
                            self._code_lines.append("    time.sleep(sleep_factor)")
                            self._code_lines.append("    m.release(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + ") - " + str(self._main_text.release_pixel) + ")")
                        elif self._main_text.hold_and_release == 3:
                            self._code_lines.append("    m.hold(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + "))")
                            self._code_lines.append("    time.sleep(sleep_factor)")
                            self._code_lines.append("    m.release(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + ") + " + str(self._main_text.release_pixel) + ")")
                        elif self._main_text.hold_and_release == 4:
                            self._code_lines.append("    m.hold(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + "))")
                            self._code_lines.append("    time.sleep(sleep_factor)")
                            self._code_lines.append("    m.release(main_text_pos.x + (" + str(self._main_text.x_offset) + ") - " + str(self._main_text.release_pixel) + ",  main_text_pos.y + (" + str(self._main_text.y_offset) + "))")
                        elif self._main_text.hold_and_release == 5:
                            self._code_lines.append("    m.hold(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + "))")
                            self._code_lines.append("    time.sleep(sleep_factor)")
                            self._code_lines.append("    m.release(main_text_pos.x + (" + str(self._main_text.x_offset) + ") + " + str(self._main_text.release_pixel) + ",  main_text_pos.y + (" + str(self._main_text.y_offset) + "))")
                    
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
                    if sub_text.click == True or sub_text.rightclick == True or sub_text.mousemove == True or sub_text.hold_and_release is not None:
                    
                        self.mouse_or_key_is_set = True
                
                        self._code_lines.append("    sub_text_" + str(cnt) + "_pos = " + name + "_object.get_result(0, " + str(cnt) + ")")  
                    
                        if mmanager_declared is False:
                            self._code_lines.append("    m = MouseManager()")
                            mmanager_declared = True
                        self._code_lines.append("    time.sleep(sleep_factor)")
                                          
                        if sub_text.x_offset is None and sub_text.y_offset is None:     
                            if sub_text.click == True:
                                self._code_lines.append("    m.click_2(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2), 1, " + str(sub_text.number_of_clicks) + ", " + str(sub_text.click_delay) + ")")
                            elif sub_text.rightclick == True:
                                self._code_lines.append("    m.click(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2), 2)")
                            elif sub_text.mousemove == True:
                                self._code_lines.append("    m.move(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2))")
                            elif sub_text.hold_and_release is not None:
                                if sub_text.hold_and_release == 0:
                                    self._code_lines.append("    m.hold(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2))")
                                elif sub_text.hold_and_release == 1:
                                    self._code_lines.append("    m.release(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2))")
                                elif sub_text.hold_and_release == 2:
                                    self._code_lines.append("    m.hold(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2))")
                                    self._code_lines.append("    time.sleep(sleep_factor)")
                                    self._code_lines.append("    m.release(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2) - " + str(sub_text.release_pixel) + ")")
                                elif sub_text.hold_and_release == 3:
                                    self._code_lines.append("    m.hold(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2))")
                                    self._code_lines.append("    time.sleep(sleep_factor)")
                                    self._code_lines.append("    m.release(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2) + " + str(sub_text.release_pixel) + ")")
                                elif sub_text.hold_and_release == 4:
                                    self._code_lines.append("    m.hold(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2))")
                                    self._code_lines.append("    time.sleep(sleep_factor)")
                                    self._code_lines.append("    m.release(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2) - " + str(sub_text.release_pixel) + ", sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2))")
                                elif sub_text.hold_and_release == 5:
                                    self._code_lines.append("    m.hold(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2))")
                                    self._code_lines.append("    time.sleep(sleep_factor)")
                                    self._code_lines.append("    m.release(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2) + " + str(sub_text.release_pixel) + ", sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2))")
                        else:
                            if sub_text.click == True:
                                self._code_lines.append("    m.click_2(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "), 1, " + str(sub_text.number_of_clicks) + ", " + str(sub_text.click_delay) + ")")
                            elif sub_text.rightclick == True:
                                self._code_lines.append("    m.click(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "), 2)")
                            elif sub_text.mousemove == True:
                                self._code_lines.append("    m.move(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "))")
                            elif sub_text.hold_and_release is not None:
                                if sub_text.hold_and_release == 0:
                                    self._code_lines.append("    m.hold(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "))")
                                elif sub_text.hold_and_release == 1:
                                    self._code_lines.append("    m.release(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "))")
                                elif sub_text.hold_and_release == 2:
                                    self._code_lines.append("    m.hold(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "))")
                                    self._code_lines.append("    time.sleep(sleep_factor)")
                                    self._code_lines.append("    m.release(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + ") - " + str(sub_text.release_pixel) + ")")
                                elif sub_text.hold_and_release == 3:
                                    self._code_lines.append("    m.hold(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "))")
                                    self._code_lines.append("    time.sleep(sleep_factor)")
                                    self._code_lines.append("    m.release(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + ") + " + str(sub_text.release_pixel) + ")")
                                elif sub_text.hold_and_release == 4:
                                    self._code_lines.append("    m.hold(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "))")
                                    self._code_lines.append("    time.sleep(sleep_factor)")
                                    self._code_lines.append("    m.release(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + ") - " + str(sub_text.release_pixel) + ",  sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "))")
                                elif sub_text.hold_and_release == 5:
                                    self._code_lines.append("    m.hold(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "))")
                                    self._code_lines.append("    time.sleep(sleep_factor)")
                                    self._code_lines.append("    m.release(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + ") + " + str(sub_text.release_pixel) + ",  sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "))")
                            
                             
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

        if self.scraper is False:
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

            
        else:
            self._code_lines.append("    return " + name + "_object.scraper()")
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
        
        if name == "" and self.ok_pressed is True:
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
        
        roi_unlimited_up = str(self._main_text.roi_unlimited_up)
        roi_unlimited_down = str(self._main_text.roi_unlimited_down)
        roi_unlimited_left = str(self._main_text.roi_unlimited_left)
        roi_unlimited_right = str(self._main_text.roi_unlimited_right)
        
        self._code_lines.append("    global " + name + "_object")  
        self._code_lines.append("    " + name + "_object = TextFinder(\"" + name + "\")")
        
        text_to_find = ""
        
        if self._main_text.quotes_ocr is True:
            text_to_find = "\"" + unicode(self._main_text.text, "utf8") + "\""
        else:
            text_to_find = self._main_text.text + ".encode('utf8')"
            
        str_channel = ""
            
        if self._main_text.red_channel is False:
            str_channel = str_channel + "\"red_channel\": False, "
            
        if self._main_text.green_channel is False:
            str_channel = str_channel + "\"green_channel\": False, "
            
        if self._main_text.blue_channel is False:
            str_channel = str_channel + "\"blue_channel\": False, "
            
        if str_channel != "":
            str_channel = ", " + str_channel[:-2]
            
        
        if self._main_text.whitelist == "'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ&:/-_\,+()*.=[]<>@":
            str1 = "    " + name + "_object.set_main_component({\"text\": " + text_to_find + ", \"lang\": \""  + self._main_text.lang + "\"" + str_channel + "},"
        else:
            str1 = "    " + name + "_object.set_main_component({\"text\": " + text_to_find + ", \"lang\": \""  + self._main_text.lang + "\"" + ", \"whitelist\": \"" + unicode(self._main_text.whitelist, "utf8") + "\"" + str_channel + "},"
            
        str2 ="                                   {\"roi_x\": " + roi_x + ", \"roi_y\": " + roi_y + ", \"roi_width\": " + roi_width + ", \"roi_height\": " + roi_height + ", \"roi_unlimited_up\": " + roi_unlimited_up + ", \"roi_unlimited_down\": " + roi_unlimited_down + ", \"roi_unlimited_left\": " + roi_unlimited_left + ", \"roi_unlimited_right\": " + roi_unlimited_right + "})"
            
        self._code_lines.append(str1)
        self._code_lines.append(str2)
        self._code_lines_for_object_finder.append(str1)
        self._code_lines_for_object_finder.append(str2)
        

        if self.scraper is False:
            if self._main_text.click == True or self._main_text.rightclick == True or self._main_text.mousemove == True or self._main_text.hold_and_release is not None:
                if self._main_text.x_offset is None and self._main_text.y_offset is None: 
                    if self._main_text.hold_and_release is not None:
                        if self._main_text.hold_and_release == 0:
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
                        elif self._main_text.hold_and_release == 1:
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
                        elif self._main_text.hold_and_release == 2:
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0, 0 - " + str(self._main_text.release_pixel) + ", False)")
                        elif self._main_text.hold_and_release == 3:
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0, 0 + " + str(self._main_text.release_pixel) + ", False)")
                        elif self._main_text.hold_and_release == 4:
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0 - " + str(self._main_text.release_pixel) + ", 0, False)")
                        elif self._main_text.hold_and_release == 5:
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0 + " + str(self._main_text.release_pixel) + ", 0, False)")
                    else:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0, 0, False)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
                else:
                    if self._main_text.hold_and_release is not None:
                        if self._main_text.hold_and_release == 0:
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_text.x_offset) + "), 0 + (" + str(self._main_text.y_offset) + "), True)")
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
                        elif self._main_text.hold_and_release == 1:
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_text.x_offset) + "), 0 + (" + str(self._main_text.y_offset) + "), True)")
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
                        elif self._main_text.hold_and_release == 2:
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_text.x_offset) + "), 0 + (" + str(self._main_text.y_offset) + "), True)")
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0 + (" + str(self._main_text.x_offset) + "), 0 + (" + str(self._main_text.y_offset) + ") - " + str(self._main_text.release_pixel) + ", True)")
                        elif self._main_text.hold_and_release == 3:
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_text.x_offset) + "), 0 + (" + str(self._main_text.y_offset) + "), True)")
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0 + (" + str(self._main_text.x_offset) + "), 0 + (" + str(self._main_text.y_offset) + ") + " + str(self._main_text.release_pixel) + ", True)")
                        elif self._main_text.hold_and_release == 4:
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_text.x_offset) + "), 0 + (" + str(self._main_text.y_offset) + "), True)")
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0 + (" + str(self._main_text.x_offset) + ") - " + str(self._main_text.release_pixel) + ",  0 + (" + str(self._main_text.y_offset) + "), True)")
                        elif self._main_text.hold_and_release == 5:
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_text.x_offset) + "), 0 + (" + str(self._main_text.y_offset) + "), True)")
                            self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = (0 + (" + str(self._main_text.x_offset) + ") + " + str(self._main_text.release_pixel) + ",  0 + (" + str(self._main_text.y_offset) + "), True)")
                    else:
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates = (0 + (" + str(self._main_text.x_offset) + "), 0 + (" + str(self._main_text.y_offset) + "), True)")
                        self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
            else:
                self._code_lines.append("    "  + name + "_object.main_xy_coordinates = None")
                self._code_lines.append("    "  + name + "_object.main_xy_coordinates_release = None")
        
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
                    
                    roi_unlimited_up = str(sub_text.roi_unlimited_up)
                    roi_unlimited_down = str(sub_text.roi_unlimited_down)
                    roi_unlimited_left = str(sub_text.roi_unlimited_left)
                    roi_unlimited_right = str(sub_text.roi_unlimited_right)
                    
                    str_channel = ""
            
                    if sub_text.red_channel is False:
                        str_channel = str_channel + "\"red_channel\": False, "
                        
                    if sub_text.green_channel is False:
                        str_channel = str_channel + "\"green_channel\": False, "
                        
                    if sub_text.blue_channel is False:
                        str_channel = str_channel + "\"blue_channel\": False, "
                        
                    if str_channel != "":
                        str_channel = ", " + str_channel[:-2]
                        
                    text_to_find = ""
                    if sub_text.quotes_ocr is True:
                        text_to_find = "\"" + unicode(sub_text.text, "utf8") + "\""
                    else:
                        text_to_find = sub_text.text + ".encode('utf8')"
                
                    #str1 = "    text_finder.add_sub_component({\"path\": \"" + sub_text.path + "\", \"threshold\":" + repr(sub_text.threshold) + "},"
                    if sub_text.whitelist == "'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ&:/-_\,+()*.=[]<>@":
                        str1 = "    " + name + "_object.add_sub_component({\"text\": " + text_to_find + ", \"lang\": \"" + sub_text.lang + "\"" + str_channel + "},"
                    else:
                        str1 = "    " + name + "_object.add_sub_component({\"text\": " + text_to_find + ", \"lang\": \"" + sub_text.lang + "\", \"whitelist\": \"" + unicode(sub_text.whitelist, "utf8") + "\"" + str_channel + "},"
                        
                    
                    str2 = "                                  {\"roi_x\": " + roi_x + ", \"roi_y\": " + roi_y + ", \"roi_width\": " + roi_width + ", \"roi_height\": " + roi_height + ", \"roi_unlimited_up\": " + roi_unlimited_up + ", \"roi_unlimited_down\": " + roi_unlimited_down + ", \"roi_unlimited_left\": " + roi_unlimited_left + ", \"roi_unlimited_right\": " + roi_unlimited_right + "})"
        
                    self._code_lines.append(str1)
                    self._code_lines.append(str2)
                    self._code_lines_for_object_finder.append(str1)
                    self._code_lines_for_object_finder.append(str2)
                    
                    if sub_text.click == True or sub_text.rightclick == True or sub_text.mousemove == True or sub_text.hold_and_release is not None:
                        if sub_text.x_offset is None and sub_text.y_offset is None: 
                            if sub_text.hold_and_release is not None:
                                if sub_text.hold_and_release == 0:
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0, False))")
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")
                                elif sub_text.hold_and_release == 1:
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0, False))")
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")
                                elif sub_text.hold_and_release == 2:
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0, False))")
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0, 0 - " + str(sub_text.release_pixel) + ", False))")
                                elif sub_text.hold_and_release == 3:
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0))")
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0, 0 + " + str(sub_text.release_pixel) + ", False))")
                                elif sub_text.hold_and_release == 4:
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0))")
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0 - " + str(sub_text.release_pixel) + ", 0, False))")
                                elif sub_text.hold_and_release == 5:
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0))")
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0 + " + str(sub_text.release_pixel) + ", 0, False))")
                            else:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0, 0, False))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")
                        else:
                            if sub_text.hold_and_release is not None:
                                if sub_text.hold_and_release == 0:
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_text.x_offset) + "), 0 + (" + str(sub_text.y_offset) + "), True))")
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")
                                elif sub_text.hold_and_release == 1:
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_text.x_offset) + "), 0 + (" + str(sub_text.y_offset) + "), True))")
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")
                                elif sub_text.hold_and_release == 2:
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_text.x_offset) + "), 0 + (" + str(sub_text.y_offset) + "), True))")
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0 + (" + str(sub_text.x_offset) + "), 0 + (" + str(sub_text.y_offset) + ") - " + str(sub_text.release_pixel) + ", True))")
                                elif sub_text.hold_and_release == 3:
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_text.x_offset) + "), 0 + (" + str(sub_text.y_offset) + ")))")
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0 + (" + str(sub_text.x_offset) + "), 0 + (" + str(sub_text.y_offset) + ") + " + str(sub_text.release_pixel) + ", True))")
                                elif sub_text.hold_and_release == 4:
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_text.x_offset) + "), 0 + (" + str(sub_text.y_offset) + ")))")
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0 + (" + str(sub_text.x_offset) + ") - " + str(sub_text.release_pixel) + ",  0 + (" + str(sub_text.y_offset) + "), True))")
                                elif sub_text.hold_and_release == 5:
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_text.x_offset) + "), 0 + (" + str(sub_text.y_offset) + ")))")
                                    self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append((0 + (" + str(sub_text.x_offset) + ") + " + str(sub_text.release_pixel) + ",  0 + (" + str(sub_text.y_offset) + "), True))")
                            else:
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append((0 + (" + str(sub_text.x_offset) + "), 0 + (" + str(sub_text.y_offset) + "), True))")
                                self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")
                    else:
                        self._code_lines.append("    "  + name + "_object.sub_xy_coordinates.append(None)")
                        self._code_lines.append("    "  + name + "_object.sub_xy_coordinates_release.append(None)")
        
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
            
            if self._main_text.click == True or self._main_text.rightclick == True or self._main_text.mousemove == True or self._main_text.hold_and_release is not None:
            
                self.mouse_or_key_is_set = True
            
                self._code_lines.append("    main_text_pos = " + name + "_object.get_result(0)")  
            
                if mmanager_declared is False:
                    self._code_lines.append("    m = MouseManager()")
                    mmanager_declared = True
                    
                self._code_lines.append("    time.sleep(sleep_factor)")
                
                if self._main_text.x_offset is None and self._main_text.y_offset is None:             
                    if self._main_text.click == True:
                        self._code_lines.append("    m.click_2(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2), 1, " + str(self._main_text.number_of_clicks) + ", " + str(self._main_text.click_delay) + ")")
                    elif self._main_text.rightclick == True:
                        self._code_lines.append("    m.click(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2), 2)")
                    elif self._main_text.mousemove == True:
                        self._code_lines.append("    m.move(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2))")
                    elif self._main_text.hold_and_release is not None:
                        if self._main_text.hold_and_release == 0:
                            self._code_lines.append("    m.hold(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2))")
                        elif self._main_text.hold_and_release == 1:
                            self._code_lines.append("    m.release(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2))")
                        elif self._main_text.hold_and_release == 2:
                            self._code_lines.append("    m.hold(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2))")
                            self._code_lines.append("    time.sleep(sleep_factor)")
                            self._code_lines.append("    m.release(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2) - " + str(self._main_text.release_pixel) + ")")
                        elif self._main_text.hold_and_release == 3:
                            self._code_lines.append("    m.hold(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2))")
                            self._code_lines.append("    time.sleep(sleep_factor)")
                            self._code_lines.append("    m.release(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2) + " + str(self._main_text.release_pixel) + ")")
                        elif self._main_text.hold_and_release == 4:
                            self._code_lines.append("    m.hold(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2))")
                            self._code_lines.append("    time.sleep(sleep_factor)")
                            self._code_lines.append("    m.release(main_text_pos.x + (main_text_pos.width/2) - " + str(self._main_text.release_pixel) + ", main_text_pos.y + (main_text_pos.height/2))")
                        elif self._main_text.hold_and_release == 5:
                            self._code_lines.append("    m.hold(main_text_pos.x + (main_text_pos.width/2), main_text_pos.y + (main_text_pos.height/2))")
                            self._code_lines.append("    time.sleep(sleep_factor)")
                            self._code_lines.append("    m.release(main_text_pos.x + (main_text_pos.width/2) + " + str(self._main_text.release_pixel) + ", main_text_pos.y + (main_text_pos.height/2))")
                else:
                    if self._main_text.click == True:
                        self._code_lines.append("    m.click_2(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + "), 1, " + str(self._main_text.number_of_clicks) + ", " + str(self._main_text.click_delay) + ")")
                    elif self._main_text.rightclick == True:
                        self._code_lines.append("    m.click(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + "), 2)")
                    elif self._main_text.mousemove == True:
                        self._code_lines.append("    m.move(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + "))")
                    elif self._main_text.hold_and_release is not None:
                        if self._main_text.hold_and_release == 0:
                            self._code_lines.append("    m.hold(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + "))")
                        elif self._main_text.hold_and_release == 1:
                            self._code_lines.append("    m.release(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + "))")
                        elif self._main_text.hold_and_release == 2:
                            self._code_lines.append("    m.hold(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + "))")
                            self._code_lines.append("    time.sleep(sleep_factor)")
                            self._code_lines.append("    m.release(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + ") - " + str(self._main_text.release_pixel) + ")")
                        elif self._main_text.hold_and_release == 3:
                            self._code_lines.append("    m.hold(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + "))")
                            self._code_lines.append("    time.sleep(sleep_factor)")
                            self._code_lines.append("    m.release(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + ") + " + str(self._main_text.release_pixel) + ")")
                        elif self._main_text.hold_and_release == 4:
                            self._code_lines.append("    m.hold(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + "))")
                            self._code_lines.append("    time.sleep(sleep_factor)")
                            self._code_lines.append("    m.release(main_text_pos.x + (" + str(self._main_text.x_offset) + ") - " + str(self._main_text.release_pixel) + ",  main_text_pos.y + (" + str(self._main_text.y_offset) + "))")
                        elif self._main_text.hold_and_release == 5:
                            self._code_lines.append("    m.hold(main_text_pos.x + (" + str(self._main_text.x_offset) + "), main_text_pos.y + (" + str(self._main_text.y_offset) + "))")
                            self._code_lines.append("    time.sleep(sleep_factor)")
                            self._code_lines.append("    m.release(main_text_pos.x + (" + str(self._main_text.x_offset) + ") + " + str(self._main_text.release_pixel) + ",  main_text_pos.y + (" + str(self._main_text.y_offset) + "))")
                    
            if self._main_text.sendkeys != "":
            
                self.mouse_or_key_is_set = True
            
                if kmanager_declared is False:
                    self._code_lines.append("    k  = KeyboardManager()")
                    kmanager_declared = True
                keys = unicode(self._main_text.sendkeys, 'utf-8')
                self._code_lines.append("    time.sleep(sleep_factor)")
                
                if self._main_text.sendkeys_quotes is True:
                    self._code_lines.append("    k.send(\"" + keys + "\", encrypted=" + str(self._main_text.text_encrypted) + ", delay=" + str(self._main_text.sendkeys_delay) + ", duration=" + str(self._main_text.sendkeys_duration) + ")")
                else:
                    self._code_lines.append("    k.send(" + keys + ", encrypted=" + str(self._main_text.text_encrypted) + ", delay=" + str(self._main_text.sendkeys_delay) + ", duration=" + str(self._main_text.sendkeys_duration) + ")")
                
            if self._main_text.enable_scrolls is True and self._main_text.scrolls_value != 0:
                self._code_lines.append("    time.sleep(sleep_factor)")
                
                direction = "m.wheel_up"
                
                if self._main_text.scrolls_direction == 0:
                    direction = "m.wheel_up"
                elif self._main_text.scrolls_direction == 1:
                    direction = "m.wheel_down"
                elif self._main_text.scrolls_direction == 2:
                    direction = "m.wheel_left"
                elif self._main_text.scrolls_direction == 3:
                    direction = "m.wheel_right"
                
                self._code_lines.append("    m.scroll(" + str(self._main_text.scrolls_value) + ", " + direction + ")")
            
            cnt = 0
            for sub_text in self._sub_texts_finder:
            
                if sub_text.height != 0 and sub_text.width !=0:
                    if sub_text.click == True or sub_text.rightclick == True or sub_text.mousemove == True or sub_text.hold_and_release is not None:
                    
                        self.mouse_or_key_is_set = True
                
                        self._code_lines.append("    sub_text_" + str(cnt) + "_pos = " + name + "_object.get_result(0, " + str(cnt) + ")")  
                    
                        if mmanager_declared is False:
                            self._code_lines.append("    m = MouseManager()")
                            mmanager_declared = True
                        self._code_lines.append("    time.sleep(sleep_factor)")
                                          
                        if sub_text.x_offset is None and sub_text.y_offset is None:     
                            if sub_text.click == True:
                                self._code_lines.append("    m.click_2(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2), 1, " + str(sub_text.number_of_clicks) + ", " + str(sub_text.click_delay) + ")")
                            elif sub_text.rightclick == True:
                                self._code_lines.append("    m.click(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2), 2)")
                            elif sub_text.mousemove == True:
                                self._code_lines.append("    m.move(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2))")
                            elif sub_text.hold_and_release is not None:
                                if sub_text.hold_and_release == 0:
                                    self._code_lines.append("    m.hold(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2))")
                                elif sub_text.hold_and_release == 1:
                                    self._code_lines.append("    m.release(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2))")
                                elif sub_text.hold_and_release == 2:
                                    self._code_lines.append("    m.hold(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2))")
                                    self._code_lines.append("    time.sleep(sleep_factor)")
                                    self._code_lines.append("    m.release(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2) - " + str(sub_text.release_pixel) + ")")
                                elif sub_text.hold_and_release == 3:
                                    self._code_lines.append("    m.hold(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2))")
                                    self._code_lines.append("    time.sleep(sleep_factor)")
                                    self._code_lines.append("    m.release(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2) + " + str(sub_text.release_pixel) + ")")
                                elif sub_text.hold_and_release == 4:
                                    self._code_lines.append("    m.hold(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2))")
                                    self._code_lines.append("    time.sleep(sleep_factor)")
                                    self._code_lines.append("    m.release(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2) - " + str(sub_text.release_pixel) + ", sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2))")
                                elif sub_text.hold_and_release == 5:
                                    self._code_lines.append("    m.hold(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2), sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2))")
                                    self._code_lines.append("    time.sleep(sleep_factor)")
                                    self._code_lines.append("    m.release(sub_text_" + str(cnt) + "_pos.x + (sub_text_" + str(cnt) + "_pos.width/2) + " + str(sub_text.release_pixel) + ", sub_text_" + str(cnt) + "_pos.y + (sub_text_" + str(cnt) + "_pos.height/2))")
                        else:
                            if sub_text.click == True:
                                self._code_lines.append("    m.click_2(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "), 1, " + str(sub_text.number_of_clicks) + ", " + str(sub_text.click_delay) + ")")
                            elif sub_text.rightclick == True:
                                self._code_lines.append("    m.click(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "), 2)")
                            elif sub_text.mousemove == True:
                                self._code_lines.append("    m.move(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "))")
                            elif sub_text.hold_and_release is not None:
                                if sub_text.hold_and_release == 0:
                                    self._code_lines.append("    m.hold(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "))")
                                elif sub_text.hold_and_release == 1:
                                    self._code_lines.append("    m.release(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "))")
                                elif sub_text.hold_and_release == 2:
                                    self._code_lines.append("    m.hold(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "))")
                                    self._code_lines.append("    time.sleep(sleep_factor)")
                                    self._code_lines.append("    m.release(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + ") - " + str(sub_text.release_pixel) + ")")
                                elif sub_text.hold_and_release == 3:
                                    self._code_lines.append("    m.hold(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "))")
                                    self._code_lines.append("    time.sleep(sleep_factor)")
                                    self._code_lines.append("    m.release(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + ") + " + str(sub_text.release_pixel) + ")")
                                elif sub_text.hold_and_release == 4:
                                    self._code_lines.append("    m.hold(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "))")
                                    self._code_lines.append("    time.sleep(sleep_factor)")
                                    self._code_lines.append("    m.release(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + ") - " + str(sub_text.release_pixel) + ",  sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "))")
                                elif sub_text.hold_and_release == 5:
                                    self._code_lines.append("    m.hold(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + "), sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "))")
                                    self._code_lines.append("    time.sleep(sleep_factor)")
                                    self._code_lines.append("    m.release(sub_text_" + str(cnt) + "_pos.x + (" + str(sub_text.x_offset) + ") + " + str(sub_text.release_pixel) + ",  sub_text_" + str(cnt) + "_pos.y + (" + str(sub_text.y_offset) + "))")
                            
                             
                    if sub_text.sendkeys != "":
                    
                        self.mouse_or_key_is_set = True
                    
                        if kmanager_declared is False:
                            self._code_lines.append("    k  = KeyboardManager()")
                            kmanager_declared = True
                        keys = unicode(sub_text.sendkeys, 'utf-8')
                        self._code_lines.append("    time.sleep(sleep_factor)")
                        
                        if sub_text.sendkeys_quotes is True:
                            self._code_lines.append("    k.send(\"" + keys + "\", encrypted=" + str(sub_text.text_encrypted) + ", delay=" + str(sub_text.sendkeys_delay) + ", duration=" + str(sub_text.sendkeys_duration) + ")")
                        else:
                            self._code_lines.append("    k.send(" + keys + ", encrypted=" + str(sub_text.text_encrypted) + ", delay=" + str(sub_text.sendkeys_delay) + ", duration=" + str(sub_text.sendkeys_duration) + ")")
                                  
                                        
                    if sub_text.enable_scrolls is True and sub_text.scrolls_value != 0:
                        self._code_lines.append("    time.sleep(sleep_factor)")
                        
                        direction = "m.wheel_up"
                        
                        if sub_text.scrolls_direction == 0:
                            direction = "m.wheel_up"
                        elif sub_text.scrolls_direction == 1:
                            direction = "m.wheel_down"
                        elif sub_text.scrolls_direction == 2:
                            direction = "m.wheel_left"
                        elif sub_text.scrolls_direction == 3:
                            direction = "m.wheel_right"
                        
                        self._code_lines.append("    m.scroll(" + str(sub_text.scrolls_value) + ", " + direction + ")")     
                    
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
        
        if self.timeout_exception is False:
        
            self._code_lines.append("    info_manager = InfoManager()")
            self._code_lines.append("    info_manager.set_info(\"DISABLE REPORTS\", True)")
        

        if self.scraper is False:
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

            
        else:
            self._code_lines.append("    return " + name + "_object.scraper()")
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
        root.set("scraper", str(self.scraper))
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
        
        """
        red_channel_node = ET.SubElement(main_text_node, "red_channel")
        red_channel_node.text = str(self._main_text.red_channel)
        
        green_channel_node = ET.SubElement(main_text_node, "green_channel")
        green_channel_node.text = str(self._main_text.green_channel)
        
        blue_channel_node = ET.SubElement(main_text_node, "blue_channel")
        blue_channel_node.text = str(self._main_text.blue_channel)
        """
        
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
        
        roi_unlimited_up_node = ET.SubElement(main_text_node, "roi_unlimited_up")
        roi_unlimited_up_node.text = str(self._main_text.roi_unlimited_up)
        
        roi_unlimited_down_node = ET.SubElement(main_text_node, "roi_unlimited_down")
        roi_unlimited_down_node.text = str(self._main_text.roi_unlimited_down)
        
        roi_unlimited_left_node = ET.SubElement(main_text_node, "roi_unlimited_left")
        roi_unlimited_left_node.text = str(self._main_text.roi_unlimited_left)
        
        roi_unlimited_right_node = ET.SubElement(main_text_node, "roi_unlimited_right")
        roi_unlimited_right_node.text = str(self._main_text.roi_unlimited_right)
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
        
        number_of_clicks_node = ET.SubElement(main_text_node, "number_of_clicks")
        number_of_clicks_node.text = str(self._main_text.number_of_clicks)
        
        click_delay_node = ET.SubElement(main_text_node, "click_delay")
        click_delay_node.text = str(self._main_text.click_delay)

        #doubleclick_node = ET.SubElement(main_text_node, "doubleclick")
        #doubleclick_node.text = str(self._main_text.doubleclick)
        
        rightclick_node = ET.SubElement(main_text_node, "rightclick")
        rightclick_node.text = str(self._main_text.rightclick)
        
        mousemove_node = ET.SubElement(main_text_node, "mousemove")
        mousemove_node.text = str(self._main_text.mousemove)
        
        x_offset_node = ET.SubElement(main_text_node, "x_offset")
        x_offset_node.text = str(self._main_text.x_offset)
        
        y_offset_node = ET.SubElement(main_text_node, "y_offset")
        y_offset_node.text = str(self._main_text.y_offset)
        
        hold_release_node = ET.SubElement(main_text_node, "hold_and_release")
        hold_release_node.text = str(self._main_text.hold_and_release)
        
        release_pixel_node = ET.SubElement(main_text_node, "release_pixel")
        release_pixel_node.text = str(self._main_text.release_pixel)
        
        scrolls_enabled_node = ET.SubElement(main_text_node, "enable_scrolls")
        scrolls_enabled_node.text = str(self._main_text.enable_scrolls)
        
        scrolls_value_node = ET.SubElement(main_text_node, "scrolls_value")
        scrolls_value_node.text = str(self._main_text.scrolls_value)
        
        scrolls_direction_node = ET.SubElement(main_text_node, "scrolls_direction")
        scrolls_direction_node.text = str(self._main_text.scrolls_direction)

        sendkeys_node = ET.SubElement(main_text_node, "sendkeys")
        
        sendkeys_node.set("encrypted", str(self._main_text.text_encrypted))
        sendkeys_node.set("delay", str(self._main_text.sendkeys_delay))
        sendkeys_node.set("duration", str(self._main_text.sendkeys_duration))
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
                
                """
                red_channel_node = ET.SubElement(sub_text_node, "red_channel")
                red_channel_node.text = str(sub_text.red_channel)

                green_channel_node = ET.SubElement(sub_text_node, "green_channel")
                green_channel_node.text = str(sub_text.green_channel)

                blue_channel_node = ET.SubElement(sub_text_node, "blue_channel")
                blue_channel_node.text = str(sub_text.blue_channel)
                """
                #whitelist_node.text = str(sub_text.whitelist)
                
                roi_x_node = ET.SubElement(sub_text_node, "roi_x")
                roi_x_node.text = str(sub_text.roi_x)
                
                roi_y_node = ET.SubElement(sub_text_node, "roi_y")
                roi_y_node.text = str(sub_text.roi_y)
                
                roi_width_node = ET.SubElement(sub_text_node, "roi_width")
                roi_width_node.text = str(sub_text.roi_width)
                
                roi_height_node = ET.SubElement(sub_text_node, "roi_height")
                roi_height_node.text = str(sub_text.roi_height)
                
                roi_unlimited_up_node = ET.SubElement(sub_text_node, "roi_unlimited_up")
                roi_unlimited_up_node.text = str(sub_text.roi_unlimited_up)
                
                roi_unlimited_down_node = ET.SubElement(sub_text_node, "roi_unlimited_down")
                roi_unlimited_down_node.text = str(sub_text.roi_unlimited_down)
                
                roi_unlimited_left_node = ET.SubElement(sub_text_node, "roi_unlimited_left")
                roi_unlimited_left_node.text = str(sub_text.roi_unlimited_left)
                
                roi_unlimited_right_node = ET.SubElement(sub_text_node, "roi_unlimited_right")
                roi_unlimited_right_node.text = str(sub_text.roi_unlimited_right)
                
                click_node = ET.SubElement(sub_text_node, "click")
                click_node.text = str(sub_text.click)
                
                number_of_clicks_node = ET.SubElement(sub_text_node, "number_of_clicks")
                number_of_clicks_node.text = str(sub_text.number_of_clicks)

                click_delay_node = ET.SubElement(sub_text_node, "click_delay")
                click_delay_node.text = str(sub_text.click_delay)
                
                #doubleclick_node = ET.SubElement(sub_text_node, "doubleclick")
                #doubleclick_node.text = str(sub_text.doubleclick)
                
                rightclick_node = ET.SubElement(sub_text_node, "rightclick")
                rightclick_node.text = str(sub_text.rightclick)

                mousemove_node = ET.SubElement(sub_text_node, "mousemove")
                mousemove_node.text = str(sub_text.mousemove)
                
                x_offset_node = ET.SubElement(sub_text_node, "x_offset")
                x_offset_node.text = str(sub_text.x_offset)

                y_offset_node = ET.SubElement(sub_text_node, "y_offset")
                y_offset_node.text = str(sub_text.y_offset)
                
                hold_release_node = ET.SubElement(sub_text_node, "hold_and_release")
                hold_release_node.text = str(sub_text.hold_and_release)

                release_pixel_node = ET.SubElement(sub_text_node, "release_pixel")
                release_pixel_node.text = str(sub_text.release_pixel)
                
                scrolls_enabled_node = ET.SubElement(sub_text_node, "enable_scrolls")
                scrolls_enabled_node.text = str(sub_text.enable_scrolls)

                scrolls_value_node = ET.SubElement(sub_text_node, "scrolls_value")
                scrolls_value_node.text = str(sub_text.scrolls_value)

                scrolls_direction_node = ET.SubElement(sub_text_node, "scrolls_direction")
                scrolls_direction_node.text = str(sub_text.scrolls_direction)
                
                sendkeys_node = ET.SubElement(sub_text_node, "sendkeys")
                sendkeys_node.set("encrypted", str(sub_text.text_encrypted))
                sendkeys_node.set("delay", str(sub_text.sendkeys_delay))
                sendkeys_node.set("duration", str(sub_text.sendkeys_duration))
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
        
        
        try:
            #print self._path + "\\text_finder.xml"
            #print "tx path", self._path + os.sep + self._xml_name
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
         
        """
        try:
            if "True" in main_text_node.getElementsByTagName("red_channel")[0].firstChild.nodeValue:
                self._main_text.red_channel = True
            else:
                self._main_text.red_channel = False
        except:
            pass
            
        try:
            if "True" in main_text_node.getElementsByTagName("green_channel")[0].firstChild.nodeValue:
                self._main_text.green_channel = True
            else:
                self._main_text.green_channel = False
        except:
            pass
            
        try:
            if "True" in main_text_node.getElementsByTagName("blue_channel")[0].firstChild.nodeValue:
                self._main_text.blue_channel = True
            else:
                self._main_text.blue_channel = False
        except:
            pass 
        """
        
        self._main_text.lang = main_text_node.getElementsByTagName("lang")[0].firstChild.nodeValue.encode('utf-8')
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
        
        try:
            if "True" in main_text_node.getElementsByTagName("roi_unlimited_up")[0].firstChild.nodeValue:
                self._main_text.roi_unlimited_up = True
            else:
                self._main_text.roi_unlimited_up = False
        except:
            self._main_text.roi_unlimited_up = False
            
        try:
            if "True" in main_text_node.getElementsByTagName("roi_unlimited_down")[0].firstChild.nodeValue:
                self._main_text.roi_unlimited_down = True
            else:
                self._main_text.roi_unlimited_down = False
        except:
            self._main_text.roi_unlimited_down = False
            
        try:
            if "True" in main_text_node.getElementsByTagName("roi_unlimited_left")[0].firstChild.nodeValue:
                self._main_text.roi_unlimited_left = True
            else:
                self._main_text.roi_unlimited_left = False
        except:
            self._main_text.roi_unlimited_left = False
            
        try:
            if "True" in main_text_node.getElementsByTagName("roi_unlimited_right")[0].firstChild.nodeValue:
                self._main_text.roi_unlimited_right = True
            else:
                self._main_text.roi_unlimited_right = False
        except:
            self._main_text.roi_unlimited_right = False
        
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
            
        try:
            if "True" in root_node.attributes["scraper"].value: #main_template_node.getElementsByTagName("wait")[0].firstChild.nodeValue:
                self.scraper = True
            else:
                self.scraper = False
        except:
            self.scraper = False
            
        try:    
            if "True" in main_text_node.getElementsByTagName("enable_scrolls")[0].firstChild.nodeValue:
                self._main_text.enable_scrolls = True
            else:
                self._main_text.enable_scrolls = False
        except:
            pass
            
        if "True" in main_text_node.getElementsByTagName("click")[0].firstChild.nodeValue:
            self._main_text.click = True
            self.mouse_or_key_is_set = True
            self._main_text.mouse_or_key_is_set = True
            self._main_text.enable_scrolls = True
        else:
            self._main_text.click = False
            
        try:
            self._main_text.number_of_clicks = int(main_text_node.getElementsByTagName("number_of_clicks")[0].firstChild.nodeValue)
        except:
            pass
            
        try:    
            self._main_text.click_delay = int(main_text_node.getElementsByTagName("click_delay")[0].firstChild.nodeValue)
        except:
            pass
        
        try:        
            if "True" in main_text_node.getElementsByTagName("doubleclick")[0].firstChild.nodeValue:
                self._main_text.click = True
                self._main_text.number_of_clicks = 2
                elf._main_text.click_delay = 10
                self.mouse_or_key_is_set = True
                self._main_text.mouse_or_key_is_set = True
                self._main_text.enable_scrolls = True
        except:
            pass
                
        if "True" in main_text_node.getElementsByTagName("rightclick")[0].firstChild.nodeValue:
            self._main_text.rightclick = True
            self.mouse_or_key_is_set = True
            self._main_text.mouse_or_key_is_set = True
            self._main_text.enable_scrolls = True
        else:
            self._main_text.rightclick = False
            
        if "True" in main_text_node.getElementsByTagName("mousemove")[0].firstChild.nodeValue:
            self._main_text.mousemove = True
            self.mouse_or_key_is_set = True
            self._main_text.mouse_or_key_is_set = True
            self._main_text.enable_scrolls = True
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
            
        try:    
            if "None" in main_text_node.getElementsByTagName("hold_and_release")[0].firstChild.nodeValue:
                self._main_text.hold_and_release = None
            else:
                self._main_text.hold_and_release = int(main_text_node.getElementsByTagName("hold_and_release")[0].firstChild.nodeValue)
                self._main_text.mouse_or_key_is_set = True
                self.mouse_or_key_is_set = True
        except:
            pass
            
        try:    
            self._main_text.release_pixel = int(main_text_node.getElementsByTagName("release_pixel")[0].firstChild.nodeValue)
        except:
            pass
            
            
        try:    
            self._main_text.scrolls_value = int(main_text_node.getElementsByTagName("scrolls_value")[0].firstChild.nodeValue)
        except:
            pass
        
        try:    
            self._main_text.scrolls_direction = int(main_text_node.getElementsByTagName("scrolls_direction")[0].firstChild.nodeValue)
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
            self._main_text.sendkeys_delay = int(main_text_node.getElementsByTagName("sendkeys")[0].attributes["delay"].value)
        except:
            pass
            
        try:
            self._main_text.sendkeys_duration = int(main_text_node.getElementsByTagName("sendkeys")[0].attributes["duration"].value)
        except:
            pass
        
        try:
            self._main_text.sendkeys = main_text_node.getElementsByTagName("sendkeys")[0].toxml()
            self._main_text.sendkeys = re.sub("<sendkeys(.*?)><!-- -->", "", self._main_text.sendkeys)
            self._main_text.sendkeys = self._main_text.sendkeys.replace("<!-- --></sendkeys>","")
            self._main_text.sendkeys = self._main_text.sendkeys.replace("<![CDATA[","")
            self._main_text.sendkeys = self._main_text.sendkeys.replace("]]>","")
            self._main_text.sendkeys = self._main_text.sendkeys.encode('utf-8')
            
            if self._main_text.sendkeys != "":
                self.mouse_or_key_is_set = True
                self._main_text.mouse_or_key_is_set = True
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
                
            """
            try:
                if "True" in sub_text_node.getElementsByTagName("red_channel")[0].firstChild.nodeValue:
                    sub_text_obj.red_channel = True
                else:
                    sub_text_obj.red_channel = False
            except:
                pass
                
            try:
                if "True" in sub_text_node.getElementsByTagName("green_channel")[0].firstChild.nodeValue:
                    sub_text_obj.green_channel = True
                else:
                    sub_text_obj.green_channel = False
            except:
                pass
                                  
            try:
                if "True" in sub_text_node.getElementsByTagName("blue_channel")[0].firstChild.nodeValue:
                    sub_text_obj.blue_channel = True
                else:
                    sub_text_obj.blue_channel = False
            except:
                pass  
            """
            
            sub_text_obj.lang = sub_text_node.getElementsByTagName("lang")[0].firstChild.nodeValue.encode('utf-8')
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
            
            try:
                if "True" in sub_text_node.getElementsByTagName("roi_unlimited_up")[0].firstChild.nodeValue:
                    sub_text_obj.roi_unlimited_up = True
                else:
                    sub_text_obj.roi_unlimited_up = False
            except:
                sub_text_obj.roi_unlimited_up = False
                
            try:
                if "True" in sub_text_node.getElementsByTagName("roi_unlimited_down")[0].firstChild.nodeValue:
                    sub_text_obj.roi_unlimited_down = True
                else:
                    sub_text_obj.roi_unlimited_down = False
            except:
                sub_text_obj.roi_unlimited_down = False
                
            try:
                if "True" in sub_text_node.getElementsByTagName("roi_unlimited_left")[0].firstChild.nodeValue:
                    sub_text_obj.roi_unlimited_left = True
                else:
                    sub_text_obj.roi_unlimited_left = False
            except:
                sub_text_obj.roi_unlimited_left = False
                
            try:
                if "True" in sub_text_node.getElementsByTagName("roi_unlimited_right")[0].firstChild.nodeValue:
                    sub_text_obj.roi_unlimited_right = True
                else:
                    sub_text_obj.roi_unlimited_right = False
            except:
                sub_text_obj.roi_unlimited_right = False
                
                                
            try:    
                if "True" in sub_text_node.getElementsByTagName("enable_scrolls")[0].firstChild.nodeValue:
                    sub_text_obj.enable_scrolls = True
                else:
                    sub_text_obj.enable_scrolls = False
            except:
                pass
                
            if "True" in sub_text_node.getElementsByTagName("click")[0].firstChild.nodeValue:
                sub_text_obj.click = True
                self.mouse_or_key_is_set = True
                sub_text_obj.mouse_or_key_is_set = True
                sub_text_obj.enable_scrolls = True
            else:
                sub_text_obj.click = False
                
            try:
                sub_text_obj.number_of_clicks = int(sub_text_node.getElementsByTagName("number_of_clicks")[0].firstChild.nodeValue)
            except:
                pass
                
            try:
                sub_text_obj.click_delay = int(sub_text_node.getElementsByTagName("click_delay")[0].firstChild.nodeValue)
            except:
                pass
               
            try:
                if "True" in sub_text_node.getElementsByTagName("doubleclick")[0].firstChild.nodeValue:
                    sub_text_obj.click = True
                    self.mouse_or_key_is_set = True
                    sub_text_obj.number_of_clicks = 2
                    sub_text_obj.click_delay = 10
                    sub_text_obj.enable_scrolls = True
            except:
                pass
                
            if "True" in sub_text_node.getElementsByTagName("rightclick")[0].firstChild.nodeValue:
                sub_text_obj.rightclick = True
                self.mouse_or_key_is_set = True
                sub_text_obj.mouse_or_key_is_set = True
                sub_text_obj.enable_scrolls = True
            else:
                sub_text_obj.rightclick = False
                
            if "True" in sub_text_node.getElementsByTagName("mousemove")[0].firstChild.nodeValue:
                sub_text_obj.mousemove = True
                self.mouse_or_key_is_set = True
                sub_text_obj.mouse_or_key_is_set = True
                sub_text_obj.enable_scrolls = True
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
                
            try:    
                if "None" in sub_text_node.getElementsByTagName("hold_and_release")[0].firstChild.nodeValue:
                    sub_text_obj.hold_and_release = None
                else:
                    sub_text_obj.hold_and_release = int(sub_text_node.getElementsByTagName("hold_and_release")[0].firstChild.nodeValue)
                    self.mouse_or_key_is_set = True
                    sub_text_obj.mouse_or_key_is_set = True
            except:
                pass
                
            try:    
                sub_text_obj.release_pixel = int(sub_text_node.getElementsByTagName("release_pixel")[0].firstChild.nodeValue)
            except:
                pass

                
            try:    
                sub_text_obj.scrolls_value = int(sub_text_node.getElementsByTagName("scrolls_value")[0].firstChild.nodeValue)
            except:
                pass
            
            try:    
                sub_text_obj.scrolls_direction = int(sub_text_node.getElementsByTagName("scrolls_direction")[0].firstChild.nodeValue)
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
                sub_text_obj.sendkeys_delay = int(sub_text_node.getElementsByTagName("sendkeys")[0].attributes["delay"].value)
            except:
                pass               
                        
            try:
                sub_text_obj.sendkeys_duration = int(sub_text_node.getElementsByTagName("sendkeys")[0].attributes["duration"].value)
            except:
                pass
            
            try:
                sub_text_obj.sendkeys = sub_text_node.getElementsByTagName("sendkeys")[0].toxml()                
                sub_text_obj.sendkeys = re.sub("<sendkeys(.*?)><!-- -->", "", sub_text_obj.sendkeys)
                sub_text_obj.sendkeys = sub_text_obj.sendkeys.replace("<!-- --></sendkeys>","")
                sub_text_obj.sendkeys = sub_text_obj.sendkeys.replace("<![CDATA[","")
                sub_text_obj.sendkeys = sub_text_obj.sendkeys.replace("]]>","")
                sub_text_obj.sendkeys = sub_text_obj.sendkeys.encode('utf-8')
                
                if sub_text_obj.sendkeys != "":
                    self.mouse_or_key_is_set = True
                    sub_text_obj.mouse_or_key_is_set = True
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
        self.red_channel = True
        self.blue_channel = True
        self.green_channel = True
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
        self.roi_unlimited_up = False
        self.roi_unlimited_down = False
        self.roi_unlimited_left = False
        self.roi_unlimited_right = False
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
        self.hold_and_release = None
        self.scrolls_value = 0
        self.scrolls_direction = 1
        self.enable_scrolls = False
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
        self.sendkeys_delay = 30
        self.sendkeys_duration = 30
        self.mouse_or_key_is_set = False
        self.sendkeys_quotes = True
        self.text_encrypted = False
        self.enable_performance = True
        self.warning = 10.00
        self.critical = 15.00
        
class SubTextForGui:
    
    def __init__(self):
        self.red_channel = True
        self.blue_channel = True
        self.green_channel = True
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
        self.roi_unlimited_up = False
        self.roi_unlimited_down = False
        self.roi_unlimited_left = False
        self.roi_unlimited_right = False
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
        self.hold_and_release = None
        self.scrolls_value = 0
        self.scrolls_direction = 1
        self.enable_scrolls = False
        self.release_pixel = 1
        self.number_of_clicks = 1
        self.click_delay = 10
        self.doubleclick = False
        self.sendkeys = ""
        self.sendkeys_delay = 30
        self.sendkeys_duration = 30
        self.sendkeys_quotes = True
        self.text_encrypted = False
        
class AlyvixTextFinderPropertiesView(QDialog, Ui_Form):
    def __init__(self, parent):
        QDialog.__init__(self)

        # Set up the user interface from Designer.
        self.setupUi(self)
        
        self.setTabOrder(self.namelineedit, self.pushButtonOk)
        self.setTabOrder(self.pushButtonOk, self.pushButtonCancel)
                        
        self.parent = parent
        self.added_block = False
        
        self.scaling_factor = self.parent.parent.scaling_factor
        
        self.find_radio.hide()
        
        """
        self.number_bar = NumberBar(self.tab_code)
        self.number_bar.setTextEdit(self.textEdit)
        self.textEdit.installEventFilter(self)
        self.textEdit.viewport().installEventFilter(self)
        self.textEdit.setFrameStyle(QFrame.NoFrame)
        self.textEdit.setAcceptRichText(False)
        """
        
        self.textEdit = LineTextWidget()
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
                                
        self.gridLayoutWidget_2.setGeometry(QRect(int(self.gridLayoutWidget_2.geometry().x() * self.scaling_factor), int(self.gridLayoutWidget_2.geometry().y() * self.scaling_factor),
                                          int(self.gridLayoutWidget_2.geometry().width() * self.scaling_factor), int(self.gridLayoutWidget_2.geometry().height() * self.scaling_factor)))


        self.gridLayoutWidget_3.setGeometry(QRect(int(self.gridLayoutWidget_3.geometry().x() * self.scaling_factor), int(self.gridLayoutWidget_3.geometry().y() * self.scaling_factor),
                                          int(self.gridLayoutWidget_3.geometry().width() * self.scaling_factor), int(self.gridLayoutWidget_3.geometry().height() * self.scaling_factor)))
                
        #self.setWindowTitle('Application Object Properties')
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)
        
        if self.parent._last_pos is not None:
            self.move(self.parent._last_pos[0],self.parent._last_pos[1])
            
        #self.lineEditText.setText(self.parent._main_text.text)
        #self.lineEditLang.setText(self.parent._main_text.lang)
        
        
        list1 = self.get_lang_list()
        self.comboBoxLang.clear()
        self.comboBoxLang.addItems(list1)
        
        index = self.comboBoxLang.findText(self.parent._main_text.lang)
        
        #print index
        
        if index == -1:
            index = self.comboBoxLang.findText("eng")
            self.comboBoxLang.setCurrentIndex(index)
        else:
            self.comboBoxLang.setCurrentIndex(index)
        
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
            self.clicknumber_spinbox.setEnabled(True)
            self.labelClickNumber.setEnabled(True)
            
            if self.parent._main_text.number_of_clicks > 1:
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
            
        self.clicknumber_spinbox.setValue(self.parent._main_text.number_of_clicks)
        self.clickdelay_spinbox.setValue(self.parent._main_text.click_delay)    
            
        """
        if self.parent._main_text.doubleclick is True:
            self.doubleclickRadio.setChecked(True)
            self.pushButtonXYoffset.setEnabled(True)
        else:
            self.doubleclickRadio.setChecked(False)
        """
            
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
            and self.parent._main_text.mousemove is False\
            and self.parent._main_text.hold_and_release is None\
            and self.parent._main_text.rightclick is False:
            self.dontclickRadio.setChecked(True)
            self.pushButtonXYoffset.setEnabled(False)
        else:
            self.dontclickRadio.setChecked(False)
            
        if self.parent._main_text.hold_and_release is not None:
            self.holdreleaseRadio.setChecked(True)
            self.holdreleaseComboBox.setEnabled(True)
            self.pushButtonXYoffset.setEnabled(True)
            self.holdreleaseComboBox.setCurrentIndex(self.parent._main_text.hold_and_release)
            
            if self.parent._main_text.hold_and_release == 0 or self.parent._main_text.hold_and_release == 1:
                self.holdreleaseSpinBox.setEnabled(False)
                self.labelPixels.setEnabled(False)
                self.holdreleaseSpinBox.setValue(self.parent._main_text.release_pixel)
            else: 
                self.holdreleaseSpinBox.setEnabled(True)
                self.labelPixels.setEnabled(True)
                self.holdreleaseSpinBox.setValue(self.parent._main_text.release_pixel)
                
        else:
            self.holdreleaseRadio.setChecked(False)
            self.labelPixels.setEnabled(False)
            self.holdreleaseComboBox.setEnabled(False)
            self.holdreleaseSpinBox.setEnabled(False)
            
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
            if sub_text.show is True:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            item.setText("sub_component_" + str(cnt))
            self.listWidget.addItem(item)
            cnt = cnt + 1

        
        if self.parent._main_text.show is True:
            self.listWidget.item(0).setCheckState(Qt.Checked)
        else:
            self.listWidget.item(0).setCheckState(Qt.Unchecked)
                        
        #self.listWidget.setCurrentIndex(QModelIndex(self.listWidget.rootIndex()))
        self.listWidget.item(0).setSelected(True)
        
        self.timeout_spinbox.setValue(self.parent.timeout)      
        self.inserttext.setText(self.parent._main_text.sendkeys)       

        if self.parent._main_text.sendkeys == "":
            self.inserttext.setText("Type text strings and shortcuts")
        else:
            self.inserttext.setText(unicode(self.parent._main_text.sendkeys, 'utf-8'))       
            
        if self.parent._main_text.text == "":
            self.lineEditText.setText("Type here the Text to find")
        else:
            self.lineEditText.setText(unicode(self.parent._main_text.text, 'utf-8'))      

        if self.parent.object_name == "":
            self.namelineedit.setText("Type the keyword name")
        else:
            self.namelineedit.setText(self.parent.object_name)      

        
        self.spinBoxArgs.setValue(self.parent.args_number)
        
        if self.parent._main_text.x_offset != None or self.parent._main_text.y_offset != None:
            self.pushButtonXYoffset.setText("Reset\nPoint")
        
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
            
        if parent.scraper is True:
            self.enable_scraper.setCheckState(Qt.Checked)
            #self.parent._main_text.quotes_ocr = True
            self.labelArgs.setEnabled(False)
            self.spinBoxArgs.setEnabled(False)
            self.add_quotes_ocr.setEnabled(False)
            self.wait_radio.setEnabled(False)
            self.wait_disapp_radio.setEnabled(False)
            self.labelWarning.setEnabled(False)
            self.doubleSpinBoxWarning.setEnabled(False)
            self.labelCritical.setEnabled(False)
            self.doubleSpinBoxCritical.setEnabled(False)
            self.timeout_label.setEnabled(False)
            self.timeout_spinbox.setEnabled(False)
            self.listWidget.setEnabled(False)
            self.lineEditText.setEnabled(False)
            self.spinBoxSendKeysDuration.setEnabled(False)
            self.spinBoxSendKeysDelay.setEnabled(False)
            self.labelSendKeysDuration.setEnabled(False)
            self.labelSendKeysDelay.setEnabled(False)
            
            
            self.timeout_exception.setEnabled(False)
            self.checkBoxEnablePerformance.setEnabled(False)
            self.clickRadio.setEnabled(False)
            self.rightclickRadio.setEnabled(False)
            self.movemouseRadio.setEnabled(False)
            self.dontclickRadio.setEnabled(False)
            self.pushButtonXYoffset.setEnabled(False)
            self.labelClickNumber.setEnabled(False)
            self.clicknumber_spinbox.setEnabled(False)
            self.labelClickDelay.setEnabled(False)
            self.clickdelay_spinbox.setEnabled(False)
            self.holdreleaseRadio.setEnabled(False)
            self.holdreleaseComboBox.setEnabled(False)
            self.holdreleaseSpinBox.setEnabled(False)
            self.labelPixels.setEnabled(False)
            self.inserttext.setEnabled(False)
            self.add_quotes.setEnabled(False)
            self.text_encrypted.setEnabled(False)
            
        else:
            #self.parent._main_text.quotes_ocr = False
            self.labelArgs.setEnabled(True)
            self.spinBoxArgs.setEnabled(True)
            self.add_quotes_ocr.setEnabled(True)
            self.wait_radio.setEnabled(True)
            self.wait_disapp_radio.setEnabled(True)
            self.lineEditText.setEnabled(True)
            
            if self.checkBoxEnablePerformance.isChecked():
                self.labelWarning.setEnabled(True)
                self.doubleSpinBoxWarning.setEnabled(True)
                self.labelCritical.setEnabled(True)
                self.doubleSpinBoxCritical.setEnabled(True)
            
            self.timeout_label.setEnabled(True)
            self.timeout_spinbox.setEnabled(True)
            self.listWidget.setEnabled(True)
            
            self.timeout_exception.setEnabled(True)
            self.checkBoxEnablePerformance.setEnabled(True)
            self.clickRadio.setEnabled(True)
            self.rightclickRadio.setEnabled(True)
            self.movemouseRadio.setEnabled(True)
            self.dontclickRadio.setEnabled(True)
            
            if self.clickRadio.isChecked() or self.rightclickRadio.isChecked() or self.movemouseRadio.isChecked() or self.holdreleaseRadio.isChecked(): 
                self.pushButtonXYoffset.setEnabled(True)
                
            if self.clickRadio.isChecked(): 
                self.labelClickNumber.setEnabled(True)
                self.clicknumber_spinbox.setEnabled(True)
                
            if self.clicknumber_spinbox.value() > 1 and self.clickRadio.isChecked():
                self.labelClickDelay.setEnabled(True)
                self.clickdelay_spinbox.setEnabled(True)

    
            self.holdreleaseRadio.setEnabled(True)
            
            if self.holdreleaseRadio.isChecked():
                self.holdreleaseComboBox.setEnabled(True)
                
            combo_index = self.holdreleaseComboBox.currentIndex()
            
            if combo_index != 0 and combo_index != 1 and self.holdreleaseRadio.isChecked():
                self.holdreleaseSpinBox.setEnabled(True)
                self.labelPixels.setEnabled(True)
            
            self.inserttext.setEnabled(True)
            self.add_quotes.setEnabled(True)
            self.text_encrypted.setEnabled(True)
            
            self.spinBoxSendKeysDuration.setEnabled(True)
            self.spinBoxSendKeysDelay.setEnabled(True)
            self.labelSendKeysDuration.setEnabled(True)
            self.labelSendKeysDelay.setEnabled(True)
        
        self.init_block_code() 

        #self.pushButtonOk.setFocus()            
        
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
            
            self.enable_scraper.setEnabled(False)
            
            
        if self.parent._main_text.enable_scrolls is True:
            self.scrollsLabel.setEnabled(True)
            self.labelDirectionScroll.setEnabled(True)
            self.comboBoxScrolls.setEnabled(True)
            self.spinBoxScrolls.setEnabled(True)
        else:
            self.scrollsLabel.setEnabled(False)
            self.labelDirectionScroll.setEnabled(False)
            self.comboBoxScrolls.setEnabled(False)
            self.spinBoxScrolls.setEnabled(False)
            
        self.comboBoxScrolls.setCurrentIndex(self.parent._main_text.scrolls_direction)
            
        self.spinBoxScrolls.setValue(self.parent._main_text.scrolls_value)
            
        """
        if self.parent._main_text.red_channel is True:
            self.checkBoxRedChannel.setChecked(True)
        else:
            self.checkBoxRedChannel.setChecked(False)
            
        if self.parent._main_text.green_channel is True:
            self.checkBoxGreenChannel.setChecked(True)
        else:
            self.checkBoxGreenChannel.setChecked(False)
        
        if self.parent._main_text.blue_channel is True:
            self.checkBoxBlueChannel.setChecked(True)
        else:
            self.checkBoxBlueChannel.setChecked(False)
          
        self.connect(self.checkBoxRedChannel, SIGNAL('stateChanged(int)'), self.red_channel_event)
        self.connect(self.checkBoxGreenChannel, SIGNAL('stateChanged(int)'), self.green_channel_event)
        self.connect(self.checkBoxBlueChannel, SIGNAL('stateChanged(int)'), self.blue_channel_event)
        """  
        self.spinBoxSendKeysDelay.setValue(self.parent._main_text.sendkeys_delay)
        self.spinBoxSendKeysDuration.setValue(self.parent._main_text.sendkeys_duration)
           
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
        
        self.connect(self.add_quotes_ocr, SIGNAL('stateChanged(int)'), self.add_quotes_ocr_event)
        
        self.connect(self.enable_scraper, SIGNAL('stateChanged(int)'), self.enable_scraper_event)
        
        self.connect(self.clickRadio, SIGNAL('toggled(bool)'), self.clickRadio_event)
        #self.connect(self.doubleclickRadio, SIGNAL('toggled(bool)'), self.doubleclickRadio_event)
        self.connect(self.rightclickRadio, SIGNAL('toggled(bool)'), self.rightclickRadio_event)
        self.connect(self.movemouseRadio, SIGNAL('toggled(bool)'), self.movemouseRadio_event)
        self.connect(self.dontclickRadio, SIGNAL('toggled(bool)'), self.dontclickRadio_event)
        
        self.connect(self.holdreleaseRadio, SIGNAL('toggled(bool)'), self.holdreleaseRadio_event)
        self.connect(self.holdreleaseComboBox, SIGNAL("currentIndexChanged(int)"), self.holdreleaseComboBox_event)
        self.connect(self.holdreleaseSpinBox, SIGNAL('valueChanged(int)'), self.holdreleaseSpinBox_event)
        
        self.connect(self.spinBoxScrolls, SIGNAL('valueChanged(int)'), self.spinbox_scrolls_event)          
        self.connect(self.comboBoxScrolls, SIGNAL("currentIndexChanged(int)"), self.combobox_scrolls_event)
        
        self.connect(self.pushButtonXYoffset, SIGNAL('clicked()'), self.pushButtonXYoffset_event)
        
        self.connect(self.clicknumber_spinbox, SIGNAL('valueChanged(int)'), self.clicknumber_spinbox_change_event)    
        self.connect(self.clickdelay_spinbox, SIGNAL('valueChanged(int)'), self.clickdelay_spinbox_change_event) 
        
        self.connect(self.pushButtonCheck, SIGNAL('clicked()'), self.check_text)
        
        self.connect(self.inserttext, SIGNAL("textChanged(QString)"), self, SLOT("inserttext_event(QString)"))
        
        self.connect(self.spinBoxSendKeysDelay, SIGNAL('valueChanged(int)'), self.sendKeysDelay_spinbox_change_event)  
        self.connect(self.spinBoxSendKeysDuration, SIGNAL('valueChanged(int)'), self.sendKeysDuration_spinbox_change_event)  
        
        self.connect(self.namelineedit, SIGNAL("textChanged(QString)"), self, SLOT("namelineedit_event(QString)"))
        #self.connect(self.inserttext, SIGNAL('cursorPositionChanged ( int, int)'), self.inserttext_textchanged_event)
        self.connect(self.pushButtonAddBlock, SIGNAL('clicked()'), self.add_block_code)
        self.connect(self.pushButtonRemoveBlock, SIGNAL('clicked()'), self.remove_block_code)
        self.connect(self.listWidgetBlocks, SIGNAL('itemSelectionChanged()'), self.listWidgetBlocks_selection_changed)
        #self.connect(self.textEditCustomLines, SIGNAL("textChanged(QString)"), self, SLOT("custom_lines_text_changed(QString)"))
        self.connect(self.lineEditText, SIGNAL("textChanged(QString)"), self, SLOT("lineEditText_event(QString)"))
        #self.connect(self.lineEditLang, SIGNAL("textChanged(QString)"), self, SLOT("lineEditLang_event(QString)"))
        self.comboBoxLang.currentIndexChanged.connect(self.combolang_event)
        self.connect(self.lineEditWhiteList, SIGNAL("textChanged(QString)"), self, SLOT("lineEditWhiteList_event(QString)"))
        
        
        #self.inserttext.viewport().installEventFilter(self)
        self.inserttext.installEventFilter(self)
        
                
        self.connect(self.spinBoxSendKeysDelay, SIGNAL('valueChanged(int)'), self.sendKeysDelay_spinbox_change_event)  
        self.connect(self.spinBoxSendKeysDuration, SIGNAL('valueChanged(int)'), self.sendKeysDuration_spinbox_change_event)  
        
        self.connect(self.add_quotes, SIGNAL('stateChanged(int)'), self.add_quotes_event)
        self.connect(self.text_encrypted, SIGNAL('stateChanged(int)'), self.text_encrypted_event)
        
        self.namelineedit.installEventFilter(self)
        
        #self.connect(self.tabWidget, SIGNAL('currentChanged(int)'), self.tab_changed_event)
        
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
        
        """ 
        self.connect(self.checkBoxRedChannel_2, SIGNAL('stateChanged(int)'), self.red_channel_event_2)
        self.connect(self.checkBoxGreenChannel_2, SIGNAL('stateChanged(int)'), self.green_channel_event_2)
        self.connect(self.checkBoxBlueChannel_2, SIGNAL('stateChanged(int)'), self.blue_channel_event_2)
        """ 
        
        self.connect(self.roi_x_spinbox, SIGNAL('valueChanged(int)'), self.roi_x_spinbox_event)
        self.connect(self.roi_y_spinbox, SIGNAL('valueChanged(int)'), self.roi_y_spinbox_event)
        self.connect(self.roi_height_spinbox, SIGNAL('valueChanged(int)'), self.roi_height_spinbox_event)
        self.connect(self.roi_width_spinbox, SIGNAL('valueChanged(int)'), self.roi_width_spinbox_event)
        
        self.connect(self.pushButtonCheck_2, SIGNAL('clicked()'), self.check_text_2)
        
        self.connect(self.clickRadio_2, SIGNAL('toggled(bool)'), self.clickRadio_event_2)
        #self.connect(self.doubleclickRadio_2, SIGNAL('toggled(bool)'), self.doubleclickRadio_event_2)
        self.connect(self.movemouseRadio_2, SIGNAL('toggled(bool)'), self.movemouseRadio_event_2)
        self.connect(self.rightclickRadio_2, SIGNAL('toggled(bool)'), self.rightclickRadio_event_2)
        self.connect(self.dontclickRadio_2, SIGNAL('toggled(bool)'), self.dontclickRadio_event_2)
        
        self.connect(self.holdreleaseRadio_2, SIGNAL('toggled(bool)'), self.holdreleaseRadio_event_2)
        
        self.connect(self.holdreleaseComboBox_2, SIGNAL("currentIndexChanged(int)"), self.holdreleaseComboBox_event_2)

        self.connect(self.holdreleaseSpinBox_2, SIGNAL('valueChanged(int)'), self.holdreleaseSpinBox_event_2)
        
        self.connect(self.spinBoxScrolls_2, SIGNAL('valueChanged(int)'), self.spinbox_scrolls_event_2)          
        self.connect(self.comboBoxScrolls_2, SIGNAL("currentIndexChanged(int)"), self.combobox_scrolls_event_2)
        
        self.connect(self.pushButtonXYoffset_2, SIGNAL('clicked()'), self.pushButtonXYoffset_event_2)
        
        self.connect(self.clicknumber_spinbox_2, SIGNAL('valueChanged(int)'), self.clicknumber_spinbox_change_event_2)    
        self.connect(self.clickdelay_spinbox_2, SIGNAL('valueChanged(int)'), self.clickdelay_spinbox_change_event_2) 
        
        self.connect(self.inserttext_2, SIGNAL("textChanged(QString)"), self, SLOT("inserttext_event_2(QString)"))
        
        self.connect(self.spinBoxSendKeysDelay_2, SIGNAL('valueChanged(int)'), self.sendKeysDelay_spinbox_change_event_2) 
        self.connect(self.spinBoxSendKeysDuration_2, SIGNAL('valueChanged(int)'), self.sendKeysDuration_spinbox_change_event_2) 
        
        #self.connect(self.inserttext, SIGNAL('cursorPositionChanged ( int, int)'), self.inserttext_textchanged_event)
        self.connect(self.lineEditText_2, SIGNAL("textChanged(QString)"), self, SLOT("lineEditText_2_event(QString)"))
        #self.connect(self.lineEditLang_2, SIGNAL("textChanged(QString)"), self, SLOT("lineEditLang2_event(QString)"))
        self.comboBoxLang_2.currentIndexChanged.connect(self.combolang_event_2)
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
        
        if self.parent.last_view_index != 0 and len(self.parent._sub_texts_finder) > 0:
            
            self.listWidget.setCurrentRow(self.parent.last_view_index)
        else:
            self.parent.last_view_index = 0

    def moveEvent(self, event):
        self.parent._last_pos = (self.frameGeometry().x(), self.frameGeometry().y())
    
    def get_lang_list(self):
        langs = []
        lang_dir = get_python_lib() + os.sep + "alyvix\\extra\\Tesseract-OCR\\tessdata"
        dirList=os.listdir(lang_dir)
        
        for file in dirList:
            if file.endswith(".traineddata"):
                langs.append(file.replace(".traineddata",""))
                
        return langs
    
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
        
        if self.enable_scraper.isChecked() is True:
            self.parent.args_number = 0
            self.spinBoxArgs.setValue(0)
        
        arg_list = []       
        args_range = range(1, self.parent.args_number + 1)
        
        for arg_num in args_range:
            arg_list.append("arg" + str(arg_num))
        
        if self.parent._main_text.sendkeys_quotes is False and self.parent.scraper is False:
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
                
        if self.parent._main_text.quotes_ocr is False and self.parent.scraper is False:
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
                
        if not os.path.exists(get_python_lib() + os.sep + "alyvix\\extra\\Tesseract-OCR\\tessdata" + os.sep + self.parent._main_text.lang + ".traineddata"):
            QMessageBox.critical(self, "Error", "Invalid language on main component")
            return True
                
        cnt = 1
        for sub_text in self.parent._sub_texts_finder:
            if sub_text.sendkeys_quotes is False and self.parent.scraper is False:
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
                    
            if sub_text.quotes_ocr is False and self.parent.scraper is False:
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
            if not os.path.exists(get_python_lib() + os.sep + "alyvix\\extra\\Tesseract-OCR\\tessdata" + os.sep + sub_text.lang + ".traineddata"):
                QMessageBox.critical(self, "Error", "Invalid language on sub component " + str(cnt))
                return True
                
            cnt += 1
            
        
        if str(self.namelineedit.text().toUtf8()) == "" or str(self.namelineedit.text().toUtf8()) == "Type the keyword name":
            answer = QMessageBox.warning(self, "Warning", "The object name is empty. Do you want to create it automatically?", QMessageBox.Yes, QMessageBox.No)
        elif self.is_valid_variable_name(self.namelineedit.text()) is False or "#" in self.namelineedit.text():
            QMessageBox.critical(self, "Error", "Keyword name is invalid!")
            return
        elif os.path.isfile(filename) and self.parent.action == "new":
            
            python_file = open(filename).read()
            
            #print filename
            
            obj_name = str(self.parent.object_name).lower()
            
            #print "obj_name:", obj_name
            
            if "def " + obj_name + "_mouse_keyboard(" in python_file or "def " + obj_name + "_build_object(" in python_file or "def " + obj_name + "(" in python_file:
                QMessageBox.critical(self, "Error", "Keyword name already exists!")

                return
        
        if answer == QMessageBox.Yes:
            #print "return"
            self.close()
            self.parent.save_all()
  
    def check_text(self):
        if not os.path.exists(get_python_lib() + os.sep + "alyvix\\extra\\Tesseract-OCR\\tessdata" + os.sep + self.comboBoxLang.currentText().toUtf8() + ".traineddata"):
            QMessageBox.critical(self, "Error", "Language does not exist")
            return

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
        
        self.check_window = AlyvixTextCheck(text, result_flag, self.parent)
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
    
    def red_channel_event(self, event):
        #print event
        if self.checkBoxRedChannel.isChecked() is True:
            self.parent._main_text.red_channel = True
        elif self.checkBoxGreenChannel.isChecked() is False and self.checkBoxBlueChannel.isChecked() is False:
            self.checkBoxRedChannel.setCheckState(Qt.Checked)
        else:
            self.parent._main_text.red_channel = False
            
    def green_channel_event(self, event):
        if self.checkBoxGreenChannel.isChecked() is True:
            self.parent._main_text.green_channel = True
        elif self.checkBoxRedChannel.isChecked() is False and self.checkBoxBlueChannel.isChecked() is False:
            self.checkBoxGreenChannel.setCheckState(Qt.Checked)
        else:
            self.parent._main_text.green_channel = False
            
    def blue_channel_event(self, event):
        if self.checkBoxBlueChannel.isChecked() is True:
            self.parent._main_text.blue_channel = True
        elif self.checkBoxRedChannel.isChecked() is False and self.checkBoxGreenChannel.isChecked() is False:
            self.checkBoxBlueChannel.setCheckState(Qt.Checked)
        else:
            self.parent._main_text.blue_channel = False
    
        
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
            self.sub_text_index = selected_index - 1
            self.update_sub_text_view()

        #print self.listWidget.currentItem().text()

    def sel_all_event(self):
  
        #print "count",self.listWidget.count()
        for row_index in range(self.listWidget.count()):
        
            self.listWidget.item(row_index).setCheckState(Qt.Checked)
            
       
    def des_all_event(self):

        for row_index in range(self.listWidget.count()):
        
            self.listWidget.item(row_index).setCheckState(Qt.Unchecked)
        
    def delete_event(self):
    
        index_to_remove = []
        #print self.parent._sub_texts_finder
        for row_index in range(self.listWidget.count()):
                if row_index != 0 and self.listWidget.item(row_index).checkState() == 2:
                    #print row_index - 1
                    #del self.parent._sub_texts_finder[row_index-1]
                    index_to_remove.append(row_index-1)
                    
        if len(index_to_remove) > 0:
                
            answer = QMessageBox.No

            answer = QMessageBox.warning(self, "Warning", "Are you sure you want to delete selected items?", QMessageBox.Yes, QMessageBox.No)
              
            if answer == QMessageBox.No:
                return
        
        self.parent._sub_texts_finder = [i for j, i in enumerate(self.parent._sub_texts_finder) if j not in index_to_remove]
        
        self.listWidget.clear()
        
        item = QListWidgetItem()
        item.setText("main_component")
        self.listWidget.addItem(item)
        
        cnt = 1
        for sub_template in self.parent._sub_texts_finder:
        
            if sub_template.x == 0 and sub_template.y == 0:
                continue
            item = QListWidgetItem()
            if sub_template.show is True:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            item.setText("sub_component_" + str(cnt))
            self.listWidget.addItem(item)
            cnt = cnt + 1
            
        if self.parent._main_text.show is True:
            self.listWidget.item(0).setCheckState(Qt.Checked)
        else:
            self.listWidget.item(0).setCheckState(Qt.Unchecked)
        
        self.listWidget.item(0).setSelected(True)  
        
        self.widget_2.hide()
        self.widget.show()
        #self.widget.setGeometry(QRect(168, 9, 413, 433))
        self.widget.setGeometry(QRect(self.widget.geometry().x(), self.widget.geometry().y(),
                                self.widget.geometry().width(), self.widget.geometry().height()))        
        self.parent.update()        
        
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
        
        if self.parent._sub_texts_finder[index].x_offset != None or self.parent._sub_texts_finder[index].y_offset != None:
            self.pushButtonXYoffset_2.setText("Reset\nPoint")
        else:
            self.pushButtonXYoffset_2.setText("Interaction\nPoint")
        
        if self.parent._sub_texts_finder[index].sendkeys == "":
            self.inserttext_2.setText("Type text strings and shortcuts")
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
        #self.lineEditLang_2.setText(self.parent._sub_texts_finder[self.sub_text_index].lang)
        
        self.comboBoxLang_2.blockSignals(True)
        #print "init combo"
        
        list1 = self.get_lang_list()
        self.comboBoxLang_2.clear()
        
        #print "add items"
        self.comboBoxLang_2.addItems(list1)
        
        #print "fidn text"
        
        index_combo = self.comboBoxLang_2.findText(self.parent._sub_texts_finder[index].lang)
        
        #print "subtextlang:", unicode(self.parent._sub_texts_finder[index].lang, 'utf-8')
        
        #print index_combo
        if index_combo == -1:
            index_combo = self.comboBoxLang_2.findText("eng")
            self.comboBoxLang_2.setCurrentIndex(index_combo)
        else:
            self.comboBoxLang_2.setCurrentIndex(index_combo)
        self.comboBoxLang_2.blockSignals(False)
        
        self.lineEditWhiteList_2.setText(unicode(self.parent._sub_texts_finder[self.sub_text_index].whitelist, 'utf-8'))
            
        self.roi_x_spinbox.setValue(self.parent._sub_texts_finder[self.sub_text_index].roi_x)
        self.roi_y_spinbox.setValue(self.parent._sub_texts_finder[self.sub_text_index].roi_y)
        self.roi_width_spinbox.setValue(self.parent._sub_texts_finder[self.sub_text_index].roi_width)
        self.roi_height_spinbox.setValue(self.parent._sub_texts_finder[self.sub_text_index].roi_height)
            
        if self.parent._sub_texts_finder[self.sub_text_index].click is True:
            self.clickRadio_2.setChecked(True)
            self.pushButtonXYoffset_2.setEnabled(True)
            self.clicknumber_spinbox_2.setEnabled(True)
            self.labelClickNumber_2.setEnabled(True)
            if self.parent._sub_texts_finder[self.sub_text_index].number_of_clicks > 1:
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
            
        self.clicknumber_spinbox_2.setValue(self.parent._sub_texts_finder[self.sub_text_index].number_of_clicks)
        self.clickdelay_spinbox_2.setValue(self.parent._sub_texts_finder[self.sub_text_index].click_delay)
        
        self.spinBoxSendKeysDelay_2.setValue(self.parent._sub_texts_finder[self.sub_text_index].sendkeys_delay)
        self.spinBoxSendKeysDuration_2.setValue(self.parent._sub_texts_finder[self.sub_text_index].sendkeys_duration)
            
        """
        if self.parent._sub_texts_finder[self.sub_text_index].doubleclick is True:
            self.doubleclickRadio_2.setChecked(True)
            self.pushButtonXYoffset_2.setEnabled(True)
        else:
            self.doubleclickRadio_2.setChecked(False)
        """
            
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
            and self.parent._sub_texts_finder[self.sub_text_index].rightclick is False \
            and self.parent._sub_texts_finder[self.sub_text_index].hold_and_release is None \
            and self.parent._sub_texts_finder[self.sub_text_index].mousemove is False:
            self.dontclickRadio_2.setChecked(True)
            self.pushButtonXYoffset_2.setEnabled(False)
        else:
            self.dontclickRadio_2.setChecked(False)
            
        if self.parent._sub_texts_finder[self.sub_text_index].hold_and_release is not None:
            self.holdreleaseComboBox_2.setCurrentIndex(self.parent._sub_texts_finder[self.sub_text_index].hold_and_release)
            self.holdreleaseRadio_2.setChecked(True)
            self.holdreleaseComboBox_2.setEnabled(True)
            self.pushButtonXYoffset_2.setEnabled(True)
            
            if self.parent._sub_texts_finder[self.sub_text_index].hold_and_release == 0 or self.parent._sub_texts_finder[self.sub_text_index].hold_and_release == 1:
                self.holdreleaseSpinBox_2.setEnabled(False)
                self.labelPixels_2.setEnabled(False)
                self.holdreleaseSpinBox_2.setValue(self.parent._sub_texts_finder[self.sub_text_index].release_pixel)
            else: 
                self.holdreleaseSpinBox_2.setEnabled(True)
                self.labelPixels_2.setEnabled(True)
                self.holdreleaseSpinBox_2.setValue(self.parent._sub_texts_finder[self.sub_text_index].release_pixel)
                
        else:
            self.holdreleaseRadio_2.setChecked(False)
            self.holdreleaseComboBox_2.setEnabled(False)
            self.holdreleaseSpinBox_2.setEnabled(False)
            self.labelPixels_2.setEnabled(False)
        
        """
        if self.parent._sub_texts_finder[self.sub_text_index].red_channel is True:
            self.checkBoxRedChannel_2.setChecked(True)
        else:
            self.checkBoxRedChannel_2.setChecked(False)
            
        if self.parent._sub_texts_finder[self.sub_text_index].green_channel is True:
            self.checkBoxGreenChannel_2.setChecked(True)
        else:
            self.checkBoxGreenChannel_2.setChecked(False)
        
        if self.parent._sub_texts_finder[self.sub_text_index].blue_channel is True:
            self.checkBoxBlueChannel_2.setChecked(True)
        else:
            self.checkBoxBlueChannel_2.setChecked(False)
        """
        
        if self.parent._sub_texts_finder[self.sub_text_index].enable_scrolls is True:
            self.scrollsLabel_2.setEnabled(True)
            self.labelDirectionScroll_2.setEnabled(True)
            self.comboBoxScrolls_2.setEnabled(True)
            self.spinBoxScrolls_2.setEnabled(True)
        else:
            self.scrollsLabel_2.setEnabled(False)
            self.labelDirectionScroll_2.setEnabled(False)
            self.comboBoxScrolls_2.setEnabled(False)
            self.spinBoxScrolls_2.setEnabled(False)
            
        
        self.comboBoxScrolls_2.setCurrentIndex(self.parent._sub_texts_finder[self.sub_text_index].scrolls_direction)
            
        self.spinBoxScrolls_2.setValue(self.parent._sub_texts_finder[self.sub_text_index].scrolls_value)
            
            
    def clickRadio_event(self, event):
        if event is False:
            self.parent._main_text.click = False
        else:
            self.parent._main_text.click = True
            self.pushButtonXYoffset.setEnabled(True) 
            self.labelClickNumber.setEnabled(True)
            self.clicknumber_spinbox.setEnabled(True)
            
            self.parent._main_text.enable_scrolls = True
            self.scrollsLabel.setEnabled(True)
            self.labelDirectionScroll.setEnabled(True)
            self.comboBoxScrolls.setEnabled(True)
            self.spinBoxScrolls.setEnabled(True)
            
            if self.clicknumber_spinbox.value() > 1:
                self.labelClickDelay.setEnabled(True)
                self.clickdelay_spinbox.setEnabled(True)
            else:
                self.labelClickDelay.setEnabled(False)
                self.clickdelay_spinbox.setEnabled(False)
                
            self.holdreleaseComboBox.setEnabled(False)
            self.holdreleaseSpinBox.setEnabled(False)
            self.labelPixels.setEnabled(False)
            
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
            
            self.parent._main_text.enable_scrolls = True
            self.scrollsLabel.setEnabled(True)
            self.labelDirectionScroll.setEnabled(True)
            self.comboBoxScrolls.setEnabled(True)
            self.spinBoxScrolls.setEnabled(True)
            
            self.labelClickNumber.setEnabled(False)
            self.clicknumber_spinbox.setEnabled(False)
            self.labelClickDelay.setEnabled(False)
            self.clickdelay_spinbox.setEnabled(False)
            self.holdreleaseComboBox.setEnabled(False)
            self.holdreleaseSpinBox.setEnabled(False)
            self.labelPixels.setEnabled(False)
            
        self.parent.update()
            
    def movemouseRadio_event(self, event):
        if event is False:
            self.parent._main_text.mousemove = False
        else:
            self.parent._main_text.mousemove = True 
            self.pushButtonXYoffset.setEnabled(True) 
            
            self.parent._main_text.enable_scrolls = True
            self.scrollsLabel.setEnabled(True)
            self.labelDirectionScroll.setEnabled(True)
            self.comboBoxScrolls.setEnabled(True)
            self.spinBoxScrolls.setEnabled(True)
            
            self.labelClickNumber.setEnabled(False)
            self.clicknumber_spinbox.setEnabled(False)
            self.labelClickDelay.setEnabled(False)
            self.clickdelay_spinbox.setEnabled(False)
            self.holdreleaseComboBox.setEnabled(False)
            self.holdreleaseSpinBox.setEnabled(False)
            self.labelPixels.setEnabled(False)
            
        self.parent.update()
             
    def dontclickRadio_event(self, event):
        if event is True:
            self.parent._main_text.click = False
            self.parent._main_text.doubleclick = False
            self.parent._main_text.rightclick = False
            self.parent._main_text.mousemove = False
            self.parent._main_text.hold_and_release = None
            self.pushButtonXYoffset.setEnabled(False) 
            self.labelClickNumber.setEnabled(False)
            self.clicknumber_spinbox.setEnabled(False)
            self.labelClickDelay.setEnabled(False)
            self.clickdelay_spinbox.setEnabled(False)
            self.holdreleaseComboBox.setEnabled(False)
            self.holdreleaseSpinBox.setEnabled(False)
            self.labelPixels.setEnabled(False)
            
            self.parent._main_text.enable_scrolls = False
            self.scrollsLabel.setEnabled(False)
            self.labelDirectionScroll.setEnabled(False)
            self.comboBoxScrolls.setEnabled(False)
            self.spinBoxScrolls.setEnabled(False)
            
        self.parent.update()
            
    def pushButtonXYoffset_event(self):
        if str(self.pushButtonXYoffset.text()) != "Reset\nPoint":
            self.parent.set_xy_offset = -1  #-1 for main, other int for sub index
            self.hide()
        else:
            self.parent._main_text.x_offset = None
            self.parent._main_text.y_offset = None
            self.pushButtonXYoffset.setText("Interaction\nPoint")
            self.parent.update()
        
    def holdreleaseRadio_event(self, event):  
        if event is False:
            self.parent._main_text.hold_and_release = None
        else:
            self.parent._main_text.click = False
            self.parent._main_text.doubleclick = False
            self.parent._main_text.mousemove = False 
            self.parent._main_text.rightclick = False
            self.pushButtonXYoffset.setEnabled(True)  
            self.labelClickNumber.setEnabled(False)
            self.clicknumber_spinbox.setEnabled(False)
            self.labelClickDelay.setEnabled(False)
            self.clickdelay_spinbox.setEnabled(False)
            self.holdreleaseComboBox.setEnabled(True)
            
            combo_index = self.holdreleaseComboBox.currentIndex()
            
            if combo_index == 0 or combo_index == 1:
                self.holdreleaseSpinBox.setEnabled(False)
                self.labelPixels.setEnabled(False)
            else: 
                self.holdreleaseSpinBox.setEnabled(True)
                self.labelPixels.setEnabled(True)
                
            self.parent._main_text.hold_and_release = combo_index
            
            self.parent._main_text.enable_scrolls = False
            self.scrollsLabel.setEnabled(False)
            self.labelDirectionScroll.setEnabled(False)
            self.comboBoxScrolls.setEnabled(False)
            self.spinBoxScrolls.setEnabled(False)
                
    def holdreleaseComboBox_event(self, event):
        if event == 0 or event == 1:
            self.holdreleaseSpinBox.setEnabled(False)
            self.labelPixels.setEnabled(False)
        else: 
            self.holdreleaseSpinBox.setEnabled(True)
            self.labelPixels.setEnabled(True)
            
        self.parent._main_text.hold_and_release = event
        
    def holdreleaseSpinBox_event(self, event):
        self.parent._main_text.release_pixel = self.holdreleaseSpinBox.value()
        
    def combobox_scrolls_event(self, event):

        self.parent._main_text.scrolls_direction = event
        
    def spinbox_scrolls_event(self, event):
        self.parent._main_text.scrolls_value = self.spinBoxScrolls.value()
        
        
    def clickdelay_spinbox_change_event (self, event):
        self.parent._main_text.click_delay = self.clickdelay_spinbox.value()
        self.parent.build_code_array()
        
    def clicknumber_spinbox_change_event (self, event):
        self.parent._main_text.number_of_clicks = self.clicknumber_spinbox.value()
        
        if self.clicknumber_spinbox.value() > 1 and self.parent._main_text.click is True:
            self.labelClickDelay.setEnabled(True)
            self.clickdelay_spinbox.setEnabled(True)
        else:
            self.labelClickDelay.setEnabled(False)
            self.clickdelay_spinbox.setEnabled(False)
        
        self.parent.build_code_array()
    
            
    @pyqtSlot(QString)
    def inserttext_event(self, text):
        if self.inserttext.text() == "Type text strings and shortcuts": #or self.inserttext.text() == "#k.send('Type here the key')":
            self.parent._main_text.sendkeys = "".encode('utf-8')
        else:
            self.parent._main_text.sendkeys = str(text.toUtf8()) #str(self.inserttext.text().toUtf8())
            
    def sendKeysDelay_spinbox_change_event(self, event):
        self.parent._main_text.sendkeys_delay = self.spinBoxSendKeysDelay.value()
        
    def sendKeysDuration_spinbox_change_event(self, event):
        self.parent._main_text.sendkeys_duration = self.spinBoxSendKeysDuration.value()
            
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
            
    def enable_scraper_event(self, event):
        if self.enable_scraper.isChecked() is True:
            #self.parent._main_text.quotes_ocr = True
            self.labelArgs.setEnabled(False)
            self.spinBoxArgs.setEnabled(False)
            self.add_quotes_ocr.setEnabled(False)
            self.wait_radio.setEnabled(False)
            self.wait_disapp_radio.setEnabled(False)
            self.labelWarning.setEnabled(False)
            self.doubleSpinBoxWarning.setEnabled(False)
            self.labelCritical.setEnabled(False)
            self.doubleSpinBoxCritical.setEnabled(False)
            self.timeout_label.setEnabled(False)
            self.timeout_spinbox.setEnabled(False)
            self.listWidget.setEnabled(False)
            self.lineEditText.setEnabled(False)
            
            
            self.timeout_exception.setEnabled(False)
            self.checkBoxEnablePerformance.setEnabled(False)
            self.clickRadio.setEnabled(False)
            self.rightclickRadio.setEnabled(False)
            self.movemouseRadio.setEnabled(False)
            self.dontclickRadio.setEnabled(False)
            self.pushButtonXYoffset.setEnabled(False)
            self.labelClickNumber.setEnabled(False)
            self.clicknumber_spinbox.setEnabled(False)
            self.labelClickDelay.setEnabled(False)
            self.clickdelay_spinbox.setEnabled(False)
            self.holdreleaseRadio.setEnabled(False)
            self.holdreleaseComboBox.setEnabled(False)
            self.holdreleaseSpinBox.setEnabled(False)
            self.labelPixels.setEnabled(False)
            self.inserttext.setEnabled(False)
            self.add_quotes.setEnabled(False)
            self.text_encrypted.setEnabled(False)
            
            self.spinBoxSendKeysDuration.setEnabled(False)
            self.spinBoxSendKeysDelay.setEnabled(False)
            self.labelSendKeysDuration.setEnabled(False)
            self.labelSendKeysDelay.setEnabled(False)
            
            self.parent.scraper = True
        else:
            #self.parent._main_text.quotes_ocr = False
            self.labelArgs.setEnabled(True)
            self.spinBoxArgs.setEnabled(True)
            self.add_quotes_ocr.setEnabled(True)
            self.wait_radio.setEnabled(True)
            self.wait_disapp_radio.setEnabled(True)
            self.lineEditText.setEnabled(True)
            
            if self.checkBoxEnablePerformance.isChecked():
                self.labelWarning.setEnabled(True)
                self.doubleSpinBoxWarning.setEnabled(True)
                self.labelCritical.setEnabled(True)
                self.doubleSpinBoxCritical.setEnabled(True)
            
            self.timeout_label.setEnabled(True)
            self.timeout_spinbox.setEnabled(True)
            self.listWidget.setEnabled(True)
            
            self.timeout_exception.setEnabled(True)
            self.checkBoxEnablePerformance.setEnabled(True)
            self.clickRadio.setEnabled(True)
            self.rightclickRadio.setEnabled(True)
            self.movemouseRadio.setEnabled(True)
            self.dontclickRadio.setEnabled(True)
            
            if self.clickRadio.isChecked() or self.rightclickRadio.isChecked() or self.movemouseRadio.isChecked() or self.holdreleaseRadio.isChecked(): 
                self.pushButtonXYoffset.setEnabled(True)
                
            if self.clickRadio.isChecked(): 
                self.labelClickNumber.setEnabled(True)
                self.clicknumber_spinbox.setEnabled(True)
                
            if self.clicknumber_spinbox.value() > 1 and self.clickRadio.isChecked():
                self.labelClickDelay.setEnabled(True)
                self.clickdelay_spinbox.setEnabled(True)

    
            self.holdreleaseRadio.setEnabled(True)
            
            if self.holdreleaseRadio.isChecked():
                self.holdreleaseComboBox.setEnabled(True)
                
            combo_index = self.holdreleaseComboBox.currentIndex()
            
            if combo_index != 0 and combo_index != 1 and self.holdreleaseRadio.isChecked():
                self.holdreleaseSpinBox.setEnabled(True)
                self.labelPixels.setEnabled(True)
            
            self.inserttext.setEnabled(True)
            self.add_quotes.setEnabled(True)
            self.text_encrypted.setEnabled(True)
            
            self.spinBoxSendKeysDuration.setEnabled(True)
            self.spinBoxSendKeysDelay.setEnabled(True)
            self.labelSendKeysDuration.setEnabled(True)
            self.labelSendKeysDelay.setEnabled(True)
            
            self.parent.scraper = False
    
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
            
    def combolang_event(self):
        self.parent._main_text.lang = str(self.comboBoxLang.currentText().toUtf8())
            
    @pyqtSlot(QString)    
    def lineEditWhiteList_event(self, text):
        if text == "Type here the Text to find":
            self.parent._main_text.whitelist = "".encode('utf-8')
        else:
            self.parent._main_text.whitelist = str(text.toUtf8())
            #print "type:", type(self.parent._main_text.whitelist), "value:", unicode(self.parent._main_text.whitelist, "utf8")
        
    @pyqtSlot(QString)
    def namelineedit_event(self, text):
        if text == "Type the keyword name":
            self.parent.object_name = "".encode('utf-8')
        else:
            self.parent.object_name = str(text.toUtf8()).replace(" ", "_")
        
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
                
        if event.type() == event.KeyPress and obj.objectName() == "namelineedit" and (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter):
            pass #self.pushButtonOk_event()
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

    def red_channel_event_2(self, event):
        #print event
        if self.checkBoxRedChannel_2.isChecked() is True:
            self.parent._sub_texts_finder[self.sub_text_index].red_channel = True
        elif self.checkBoxGreenChannel_2.isChecked() is False and self.checkBoxBlueChannel_2.isChecked() is False:
            self.checkBoxRedChannel_2.setCheckState(Qt.Checked)
        else:
            self.parent._sub_texts_finder[self.sub_text_index].red_channel = False
            
    def green_channel_event_2(self, event):
        if self.checkBoxGreenChannel_2.isChecked() is True:
            self.parent._sub_texts_finder[self.sub_text_index].green_channel = True
        elif self.checkBoxRedChannel_2.isChecked() is False and self.checkBoxBlueChannel_2.isChecked() is False:
            self.checkBoxGreenChannel_2.setCheckState(Qt.Checked)
        else:
            self.parent._sub_texts_finder[self.sub_text_index].green_channel = False
            
    def blue_channel_event_2(self, event):
        if self.checkBoxBlueChannel_2.isChecked() is True:
            self.parent._sub_texts_finder[self.sub_text_index].blue_channel = True
        elif self.checkBoxRedChannel_2.isChecked() is False and self.checkBoxGreenChannel_2.isChecked() is False:
            self.checkBoxBlueChannel_2.setCheckState(Qt.Checked)
        else:
            self.parent._sub_texts_finder[self.sub_text_index].blue_channel = False


    def text_encrypted_event_2(self, event):
        if self.text_encrypted_2.isChecked() is True:
            self.parent._sub_rects_finder[self.sub_rect_index].text_encrypted = True
        else:
            self.parent._sub_rects_finder[self.sub_rect_index].text_encrypted = False


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
    
        if not os.path.exists(get_python_lib() + os.sep + "alyvix\\extra\\Tesseract-OCR\\tessdata" + os.sep + self.comboBoxLang_2.currentText().toUtf8() + ".traineddata"):
            QMessageBox.critical(self, "Error", "Language does not exist")
            return

            
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
        
        self.check_window = AlyvixTextCheck(text, result_flag, self.parent)
        self.check_window.show()
        
    @pyqtSlot(QString)
    def inserttext_event_2(self, text):
        if self.inserttext_2.text() == "Type text strings and shortcuts":
            self.parent._sub_texts_finder[self.sub_text_index].sendkeys = "".encode('utf-8')
        else:
            self.parent._sub_texts_finder[self.sub_text_index].sendkeys = str(text.toUtf8())
            
    def sendKeysDelay_spinbox_change_event_2(self, event):
        self.parent._sub_texts_finder[self.sub_text_index].sendkeys_delay = self.spinBoxSendKeysDelay_2.value()
        
    def sendKeysDuration_spinbox_change_event_2(self, event):
        self.parent._sub_texts_finder[self.sub_text_index].sendkeys_duration = self.spinBoxSendKeysDuration_2.value()
        
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
            
    def combolang_event_2(self):
        self.parent._sub_texts_finder[self.sub_text_index].lang = str(self.comboBoxLang_2.currentText().toUtf8())
        #print "comboevent"
            
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
            self.labelClickNumber_2.setEnabled(True)
            self.clicknumber_spinbox_2.setEnabled(True)
            if self.clicknumber_spinbox_2.value() > 1: # and self.parent._sub_texts_finder[self.sub_text_index].click is True:
                self.labelClickDelay_2.setEnabled(True)
                self.clickdelay_spinbox_2.setEnabled(True)
            else:
                self.labelClickDelay_2.setEnabled(False)
                self.clickdelay_spinbox_2.setEnabled(False)
            self.holdreleaseComboBox_2.setEnabled(False)
            self.holdreleaseSpinBox_2.setEnabled(False)
            self.labelPixels_2.setEnabled(False)
            
            self.parent._sub_texts_finder[self.sub_text_index].enable_scrolls = True
            self.scrollsLabel_2.setEnabled(True)
            self.labelDirectionScroll_2.setEnabled(True)
            self.comboBoxScrolls_2.setEnabled(True)
            self.spinBoxScrolls_2.setEnabled(True)
            
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
            self.labelClickNumber_2.setEnabled(False)
            self.clicknumber_spinbox_2.setEnabled(False)
            self.labelClickDelay_2.setEnabled(False)
            self.clickdelay_spinbox_2.setEnabled(False)
            self.holdreleaseComboBox_2.setEnabled(False)
            self.holdreleaseSpinBox_2.setEnabled(False)
            self.labelPixels_2.setEnabled(False)
            
            self.parent._sub_texts_finder[self.sub_text_index].enable_scrolls = True
            self.scrollsLabel_2.setEnabled(True)
            self.labelDirectionScroll_2.setEnabled(True)
            self.comboBoxScrolls_2.setEnabled(True)
            self.spinBoxScrolls_2.setEnabled(True)
            
        self.parent.update()
            
    def rightclickRadio_event_2(self, event):
        if event is False:
            self.parent._sub_texts_finder[self.sub_text_index].rightclick = False
        else:
            self.parent._sub_texts_finder[self.sub_text_index].rightclick = True 
            self.pushButtonXYoffset_2.setEnabled(True)
            self.labelClickNumber_2.setEnabled(False)
            self.clicknumber_spinbox_2.setEnabled(False)
            self.labelClickDelay_2.setEnabled(False)
            self.clickdelay_spinbox_2.setEnabled(False)
            self.holdreleaseComboBox_2.setEnabled(False)
            self.holdreleaseSpinBox_2.setEnabled(False)
            self.labelPixels_2.setEnabled(False)
            
            self.parent._sub_texts_finder[self.sub_text_index].enable_scrolls = True
            self.scrollsLabel_2.setEnabled(True)
            self.labelDirectionScroll_2.setEnabled(True)
            self.comboBoxScrolls_2.setEnabled(True)
            self.spinBoxScrolls_2.setEnabled(True)
            
        self.parent.update()
             
    def dontclickRadio_event_2(self, event):
        if event is True:
            self.parent._sub_texts_finder[self.sub_text_index].click = False
            self.parent._sub_texts_finder[self.sub_text_index].doubleclick = False
            self.parent._sub_texts_finder[self.sub_text_index].rightclick = False
            self.parent._sub_texts_finder[self.sub_text_index].mousemove = False
            self.pushButtonXYoffset_2.setEnabled(False)
            self.labelClickNumber_2.setEnabled(False)
            self.clicknumber_spinbox_2.setEnabled(False)
            self.labelClickDelay_2.setEnabled(False)
            self.clickdelay_spinbox_2.setEnabled(False)
            self.holdreleaseComboBox_2.setEnabled(False)
            self.holdreleaseSpinBox_2.setEnabled(False)
            self.labelPixels_2.setEnabled(False)
            
            self.parent._sub_texts_finder[self.sub_text_index].enable_scrolls = False
            self.scrollsLabel_2.setEnabled(False)
            self.labelDirectionScroll_2.setEnabled(False)
            self.comboBoxScrolls_2.setEnabled(False)
            self.spinBoxScrolls_2.setEnabled(False)
            
        self.parent.update()
            
    def pushButtonXYoffset_event_2(self):
        if str(self.pushButtonXYoffset_2.text()) != "Reset\nPoint":
            self.parent.set_xy_offset = self.sub_text_index  #-1 for main, other int for sub index
            self.hide()
        else:
            self.parent._sub_texts_finder[self.sub_text_index].x_offset = None
            self.parent._sub_texts_finder[self.sub_text_index].y_offset = None
            self.pushButtonXYoffset_2.setText("Interaction\nPoint")
            self.parent.update()
        
    def holdreleaseRadio_event_2(self, event):  
        if event is False:
            self.parent._sub_texts_finder[self.sub_text_index].hold_and_release = None
        else:
            self.parent._sub_texts_finder[self.sub_text_index].click = False
            self.parent._sub_texts_finder[self.sub_text_index].doubleclick = False
            self.parent._sub_texts_finder[self.sub_text_index].mousemove = False 
            self.parent._sub_texts_finder[self.sub_text_index].rightclick = False
            self.pushButtonXYoffset_2.setEnabled(True)  
            self.labelClickNumber_2.setEnabled(False)
            self.clicknumber_spinbox_2.setEnabled(False)
            self.labelClickDelay_2.setEnabled(False)
            self.clickdelay_spinbox_2.setEnabled(False)
            self.holdreleaseComboBox_2.setEnabled(True)
            
            self.parent._sub_texts_finder[self.sub_text_index].enable_scrolls = False
            self.scrollsLabel_2.setEnabled(False)
            self.labelDirectionScroll_2.setEnabled(False)
            self.comboBoxScrolls_2.setEnabled(False)
            self.spinBoxScrolls_2.setEnabled(False)
            
            combo_index = self.holdreleaseComboBox_2.currentIndex()
            
            if combo_index == 0 or combo_index == 1:
                self.holdreleaseSpinBox_2.setEnabled(False)
                self.labelPixels_2.setEnabled(False)
            else: 
                self.holdreleaseSpinBox_2.setEnabled(True)
                self.labelPixels_2.setEnabled(True)
            
            self.parent._sub_texts_finder[self.sub_text_index].hold_and_release = combo_index
            
    def holdreleaseComboBox_event_2(self, event):
        if event == 0 or event == 1:
            self.holdreleaseSpinBox_2.setEnabled(False)
            self.labelPixels_2.setEnabled(False)
        else: 
            self.holdreleaseSpinBox_2.setEnabled(True)
            self.labelPixels_2.setEnabled(True)
            
        self.parent._sub_texts_finder[self.sub_text_index].hold_and_release = event
        
    def holdreleaseSpinBox_event_2(self, event):
        self.parent._sub_texts_finder[self.sub_text_index].release_pixel = self.holdreleaseSpinBox_2.value()
        
        
    def clickdelay_spinbox_change_event_2 (self, event):
        self.parent._sub_texts_finder[self.sub_text_index].click_delay = self.clickdelay_spinbox_2.value()
        self.parent.build_code_array()
        
    def combobox_scrolls_event_2(self, event):

        self.parent._sub_texts_finder[self.sub_text_index].scrolls_direction = event
        
    def spinbox_scrolls_event_2(self, event):
        self.parent._sub_texts_finder[self.sub_text_index].scrolls_value = self.spinBoxScrolls_2.value()
        
    def clicknumber_spinbox_change_event_2 (self, event):
        self.parent._sub_texts_finder[self.sub_text_index].number_of_clicks = self.clicknumber_spinbox_2.value()
        
        if self.clicknumber_spinbox_2.value() > 1 and self.parent._sub_texts_finder[self.sub_text_index].click is True:
            self.labelClickDelay_2.setEnabled(True)
            self.clickdelay_spinbox_2.setEnabled(True)
        else:
            self.labelClickDelay_2.setEnabled(False)
            self.clickdelay_spinbox_2.setEnabled(False)
            
        self.parent.build_code_array()
        
    def closeEvent(self, event):
        try:
            self.check_window.close()
            #print "this closing"
        except:
            pass
        #print "this closing"
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
        
class AlyvixTextCheck(QDialog, Ui_Form_Text):
    def __init__(self, text, check_result, parent):
        QDialog.__init__(self)
        
        self.parent = parent

        # Set up the user interface from Designer.
        self.setupUi(self)
        
        self.scaling_factor = self.parent.parent.scaling_factor
        
        #self.setFixedSize(self.size())
        self.setFixedSize(int(self.frameGeometry().width() * self.scaling_factor), int(self.frameGeometry().height() * self.scaling_factor))
        
        self.labelHeader.setGeometry(QRect(int(self.labelHeader.geometry().x() * self.scaling_factor), int(self.labelHeader.geometry().y() * self.scaling_factor),
                                int(self.labelHeader.geometry().width() * self.scaling_factor), int(self.labelHeader.geometry().height() * self.scaling_factor)))
                        
        
        self.plainTextEdit.setGeometry(QRect(int(self.plainTextEdit.geometry().x() * self.scaling_factor), int(self.plainTextEdit.geometry().y() * self.scaling_factor),
                                int(self.plainTextEdit.geometry().width() * self.scaling_factor), int(self.plainTextEdit.geometry().height() * self.scaling_factor)))
                        
        self.labelCheckResult.setGeometry(QRect(int(self.labelCheckResult.geometry().x() * self.scaling_factor), int(self.labelCheckResult.geometry().y() * self.scaling_factor),
                                int(self.labelCheckResult.geometry().width() * self.scaling_factor), int(self.labelCheckResult.geometry().height() * self.scaling_factor)))
                        
        
        self.pushButtonOk.setGeometry(QRect(int(self.pushButtonOk.geometry().x() * self.scaling_factor), int(self.pushButtonOk.geometry().y() * self.scaling_factor),
                                          int(self.pushButtonOk.geometry().width() * self.scaling_factor), int(self.pushButtonOk.geometry().height() * self.scaling_factor)))
                                          
        
        #self.text = text
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        if self.parent.scraper is True:
            self.labelCheckResult.setText("")   
        elif check_result is False:
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