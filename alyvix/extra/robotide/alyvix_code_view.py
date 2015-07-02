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

from PyQt4.QtGui import QApplication, QWidget, QCursor, QImage, QPainter, QPainter, QPen, QColor, QPixmap, QBrush, QPainterPath, QDialog, QListWidgetItem , QTextEdit, QHBoxLayout, QTextCharFormat, QMessageBox, QFont, QFontMetrics, QTextCursor
from PyQt4.QtCore import Qt, QThread, SIGNAL, QTimer, QUrl, QPoint, QRect, QModelIndex, SLOT, pyqtSlot, QString, QChar
from PyQt4.Qt import QFrame

from PyQt4.QtWebKit import QWebSettings

from alyvix_rect_finder_view import AlyvixRectFinderView
from alyvix_image_finder_view import AlyvixImageFinderView
from alyvix_text_finder_view import AlyvixTextFinderView
#from alyvix_object_selection_controller import AlyvixMainMenuController

from alyvix_code_properties_view import Ui_Form

from alyvix.tools.screenmanager import ScreenManager

from stat import S_ISREG, ST_CTIME, ST_MODE

import shutil

import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET

import codecs

from distutils.sysconfig import get_python_lib


class AlyvixCustomCodeView(QDialog, Ui_Form):
    def __init__(self, parent):
        QDialog.__init__(self)

        # Set up the user interface from Designer.
        self.setupUi(self)
        
        self.setFixedSize(self.size())
        
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)
        
        self.parent = parent
        self._path = self.parent.path
        self.action = self.parent.action
        self._xml_name = self.parent.xml_name
        
        self.esc_pressed = False
        
        self.name = ""
        self.args_number = 0
        
        self.code_lines = []
        
        self.pykeyboard_declared = False
        self.pymouse_declared = False
        self.winmanager_declared = False
        self.procmanager_declared = False
        
        self.textEdit = LineTextWidget(self)
        self.textEdit.setGeometry(QRect(198, 40, 350, 206))
        #self.textEdit.setText(self.build_code_string())
        
                        
        self.build_objects()
        
        self.__old_code = self.get_old_code()
        #self.__alyvix_proxy_path = os.getenv("ALYVIX_HOME") + os.sep + "robotproxy"
        self.__alyvix_proxy_path = get_python_lib() + os.sep + "alyvix" + os.sep + "robotproxy"
        self._robot_file_name = self.parent.robot_file_name

        self.set_textedit_text()
        #print self._main_object_finder.xml_path
        
        if self.name != "":
            self.namelineedit.setText(self.name)
        
        self.connect(self.pushButtonTapKey, SIGNAL('clicked()'), self.pushbutton_tap_key_event)
        self.connect(self.pushButtonPressKey, SIGNAL('clicked()'), self.pushbutton_press_key_event)
        self.connect(self.pushButtonReleaseKey, SIGNAL('clicked()'), self.pushbutton_release_key_event)
        self.connect(self.pushButtonPressKeys, SIGNAL('clicked()'), self.pushbutton_press_keys_event)
        self.connect(self.pushButtonTypeString, SIGNAL('clicked()'), self.pushbutton_type_string_event)
        
        self.connect(self.pushButtonMousePress, SIGNAL('clicked()'), self.pushbutton_mouse_press_event)
        self.connect(self.pushButtonMouseRelease, SIGNAL('clicked()'), self.pushbutton_mouse_release_event)
        self.connect(self.pushButtonMouseClick, SIGNAL('clicked()'), self.pushbutton_mouse_click_event)
        self.connect(self.pushButtonMouseDoubleClick, SIGNAL('clicked()'), self.pushbutton_mouse_doubleclick_event)
        self.connect(self.pushButtonMouseMove, SIGNAL('clicked()'), self.pushbutton_mouse_move_event)
        self.connect(self.pushButtonMouseScroll, SIGNAL('clicked()'), self.pushbutton_mouse_scroll_event)
        self.connect(self.pushButtonMouseDrag, SIGNAL('clicked()'), self.pushbutton_mouse_drag_event)
        
        self.connect(self.pushButtonProcCreate, SIGNAL('clicked()'), self.pushbutton_proc_create_event)
        self.connect(self.pushButtonProcKill, SIGNAL('clicked()'), self.pushbutton_proc_kill_event)
        
        self.connect(self.pushButtonWinShow, SIGNAL('clicked()'), self.pushbutton_win_show_event)
        self.connect(self.pushButtonWinMaximize, SIGNAL('clicked()'), self.pushbutton_win_maximize_event)
        self.connect(self.pushButtonWinCheck, SIGNAL('clicked()'), self.pushbutton_win_check)
        self.connect(self.pushButtonWinClose, SIGNAL('clicked()'), self.pushbutton_win_close_event)
        
        self.connect(self.spinBoxArgs, SIGNAL('valueChanged(int)'), self.args_spinbox_change_event)
        
        self.textEdit.setFocus()
        
        self.connect(self.namelineedit, SIGNAL("textChanged(QString)"), self, SLOT("namelineedit_event(QString)"))
        self.namelineedit.installEventFilter(self)
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            if self.esc_pressed is False and self.textEdit.toPlainText() != "":
                self.esc_pressed = True
                self.build_code_array()
                self.build_xml()
                self.save_python_file()
                if self.action == "new":
                    self.parent.add_new_item_on_list()
                
            self.parent.show()
            self.close()
 
    def set_textedit_text(self):
        old_code_lines = []
        old_code_lines = self.__old_code.split('\n')
        old_code_lines.pop(0)
        
        string = ""
        for line in old_code_lines:
        
            string = string + line.lstrip('    ') + '\n'
            
    
        self.textEdit.setText(unicode(string, 'utf-8'))      
    
    def build_objects(self):
        
        #filename = open(self._path + os.sep + self._xml_name,"r")
        #print filename
        
        try:
            filehandler = open(self._path + os.sep + self._xml_name,"r")
        except:
            return

        doc = minidom.parse(filehandler)
        
        main_obj_xml_path = "xml_path"
        
        root_node = doc.getElementsByTagName("custom_code")[0]
        #main_obj_node = doc.getElementsByTagName("name")[0]

        self.name = root_node.attributes["name"].value
        
    def build_code_string(self):
    
        last_block_line = 0
        lines = 0
        
        string = ""
        
        line_cnt = 1
        for element in self._code_lines:

            string = string + element + os.linesep
            line_cnt = line_cnt + 1

        #string = string[:-1]
        return string.encode('UTF-8')
        
    def build_code_array(self):
            
        self._code_lines = []
        self._code_lines_for_object_finder = []
            
        name = self.name
        
        if name == "":
            name = time.strftime("custom_code_%d_%m_%y_%H_%M_%S")
            self.name = name
            
        #self._code_lines.append("def " + name + "():")
        
        string_function_args = "def " + name + "("
        
        args_range = range(1, self.args_number + 1)
        
        for arg_num in args_range:
            string_function_args = string_function_args + "arg" + str(arg_num) + ", " 
        
        if string_function_args.endswith(", "):
            string_function_args = string_function_args[:-2]
        string_function_args = string_function_args + "):"
        self._code_lines.append(string_function_args)
        
        tmp_str_array = []
        tmp_str_array = unicode(self.textEdit.toPlainText().toUtf8(), 'utf-8').split('\n')
        
        
        for string in tmp_str_array:
            self._code_lines.append('    ' + string)
        
        self._code_lines.append("")
        self._code_lines.append("") 
        
        for string in self._code_lines:
            print string
        
    def get_old_code(self):
        file_code_string = ""
        filename = self._path + os.sep + self.name + "_old_code.txt"
        
        if os.path.exists(filename):
            file = codecs.open(filename, encoding="utf-8")  
            lines = file.readlines()
            
            for line in lines:
                file_code_string = file_code_string + line   
                
        return file_code_string.encode('utf-8')
    
    def save_python_file(self):
    
        file_code_string = ""
        filename = self.__alyvix_proxy_path + os.sep + "AlyvixProxy" + self._robot_file_name + ".py"
        
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
            file_code_string = file_code_string + "import os" + os.linesep
            file_code_string = file_code_string + "import time" + os.linesep
            file_code_string = file_code_string + "from pykeyboard import PyKeyboard" + os.linesep
            file_code_string = file_code_string + "from pymouse import PyMouse" + os.linesep
            file_code_string = file_code_string + "from alyvix.tools.procmanager import ProcManager" + os.linesep
            file_code_string = file_code_string + "from alyvix.tools.winmanager import WinManager" + os.linesep
            file_code_string = file_code_string + "from alyvix.core.rectfinder import RectFinder" + os.linesep
            file_code_string = file_code_string + "from alyvix.core.imagefinder import ImageFinder" + os.linesep
            file_code_string = file_code_string + "from alyvix.core.textfinder import TextFinder" + os.linesep
            file_code_string = file_code_string + "from alyvix.core.objectfinder import ObjectFinder" + os.linesep
            file_code_string = file_code_string + os.linesep
            file_code_string = file_code_string + os.linesep
            file_code_string = file_code_string + "os.environ[\"alyvix_test_case_name\"] = os.path.basename(__file__).split('.')[0]" + os.linesep
            file_code_string = file_code_string + os.linesep
            file_code_string = file_code_string + current_code_string
        elif self.action == "new":
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
        
        filename = self._path + os.sep + self.name + "_old_code.txt"
        file = codecs.open(filename, 'w', 'utf-8')
        file.write(unicode(string, 'utf-8'))
        file.close()

    
    def remove_code_from_py_file(self):
    
        file_code_string = ""
        filename = self.__alyvix_proxy_path + os.sep + "AlyvixProxy" + self._robot_file_name + ".py"
        
        if os.path.exists(filename):
            file = codecs.open(filename, encoding="utf-8")  
            lines = file.readlines()
            
            for line in lines:
                file_code_string = file_code_string + line
            
        self.build_code_array()
        current_code_string = unicode(self.build_code_string(), 'utf-8')
        #current_code_string = current_code_string.replace(os.linesep + os.linesep, os.linesep)
        
        print "old_code:", self.__old_code
        file_code_string = file_code_string.replace(unicode(self.__old_code, 'utf-8'), "")
        
        string = file_code_string
        string = string.encode('utf-8')

        file = codecs.open(filename, 'w', 'utf-8')
        file.write(unicode(string, 'utf-8'))
        file.close()    
 
        
    def build_xml(self):

        name = str(self.name)
        
        if name == "":
            name = time.strftime("custom_code_%d_%m_%y_%H_%M_%S")
            self.name = name
        
        root = ET.Element("custom_code")
        root.set("name", name)
            
        tree = ET.ElementTree(root)
        
        if not os.path.exists(self._path):
            os.makedirs(self._path)
            
        python_file = open(self._path + os.sep + self.name + "_CustomCode.xml", 'w')
        tree.write(python_file, encoding='utf-8', xml_declaration=True) 
        #python_file.write(rough_string)        
        python_file.close()
    
    @pyqtSlot(QString)
    def namelineedit_event(self, text):
        if text == "Type here the name of the object":
            self.name = "".encode('utf-8')
        else:
            self.name = str(text.toUtf8()).replace(" ", "_")
            
    def eventFilter(self, obj, event):
        if event.type() == event.MouseButtonPress:
        
            if self.namelineedit.text() == "Type here the name of the object" and obj.objectName() == "namelineedit":
                self.namelineedit.setText("")
                return True
                
        if event.type()== event.FocusOut:

            if self.namelineedit.text() == "" and obj.objectName() == "namelineedit":
                self.namelineedit.setText("Type here the name of the object")
                return True
            elif obj.objectName() == "namelineedit":
                self.namelineedit.setText(self.name)
                return True
            
        return False  
        
    def pushbutton_tap_key_event(self):
    
        if self.pykeyboard_declared is False:
            self.textEdit.append("k = PyKeyboard()")
            self.textEdit.append("")
            self.pykeyboard_declared = True
        
        self.textEdit.append("k.tap_key(insert here the key)")
        self.textEdit.append("")
        
    def pushbutton_press_key_event(self):
        if self.pykeyboard_declared is False:
            self.textEdit.append("k = PyKeyboard()")
            self.textEdit.append("")
            self.pykeyboard_declared = True
            
        self.textEdit.append("k.press_key(insert here the key)")
        self.textEdit.append("")

        
    def pushbutton_release_key_event(self):
        if self.pykeyboard_declared is False:
            self.textEdit.append("k = PyKeyboard()")
            self.textEdit.append("")
            self.pykeyboard_declared = True
            
        self.textEdit.append("k.release_key(insert here the key)")
        self.textEdit.append("")
        
    def pushbutton_press_keys_event(self):
        if self.pykeyboard_declared is False:
            self.textEdit.append("k = PyKeyboard()")
            self.textEdit.append("")
            self.pykeyboard_declared = True
            
        self.textEdit.append("k.press_keys(['insert', 'here', 'the', 'keys'])")
        self.textEdit.append("")
        
    def pushbutton_type_string_event(self):
        if self.pykeyboard_declared is False:
            self.textEdit.append("k = PyKeyboard()")
            self.textEdit.append("")
            self.pykeyboard_declared = True
        
        self.textEdit.append("k.type_string('insert here the string')")
        self.textEdit.append("")
        
        
        
    def pushbutton_mouse_press_event(self):
        if self.pymouse_declared is False:
            self.textEdit.append("m = PyMouse()")
            self.textEdit.append("")
            self.pymouse_declared = True
        
        self.textEdit.append("m.press(x=0, y=0, button=1)")
        self.textEdit.append("")
        
    def pushbutton_mouse_release_event(self):
        if self.pymouse_declared is False:
            self.textEdit.append("m = PyMouse()")
            self.textEdit.append("")
            self.pymouse_declared = True
        
        self.textEdit.append("m.release(x=0, y=0, button=1)")
        self.textEdit.append("")
        
    def pushbutton_mouse_click_event(self):
        if self.pymouse_declared is False:
            self.textEdit.append("m = PyMouse()")
            self.textEdit.append("")
            self.pymouse_declared = True
        
        self.textEdit.append("m.click(x=0, y=0, button=1, n=1)")
        self.textEdit.append("")
        
    def pushbutton_mouse_doubleclick_event(self):
        if self.pymouse_declared is False:
            self.textEdit.append("m = PyMouse()")
            self.textEdit.append("")
            self.pymouse_declared = True
        
        self.textEdit.append("m.click(x=0, y=0, button=1, n=2)")
        self.textEdit.append("")
        
    def pushbutton_mouse_move_event(self):
        if self.pymouse_declared is False:
            self.textEdit.append("m = PyMouse()")
            self.textEdit.append("")
            self.pymouse_declared = True
        
        self.textEdit.append("m.move(x=0, y=0)")
        self.textEdit.append("")
        
    def pushbutton_mouse_scroll_event(self):
        if self.pymouse_declared is False:
            self.textEdit.append("m = PyMouse()")
            self.textEdit.append("")
            self.pymouse_declared = True
        
        self.textEdit.append("m.scroll(vertical=None, horizontal=None, depth=None)")
        self.textEdit.append("")
        
    def pushbutton_mouse_drag_event(self):
        if self.pymouse_declared is False:
            self.textEdit.append("m = PyMouse()")
            self.textEdit.append("")
            self.pymouse_declared = True
        
        self.textEdit.append("m.drag(x=0, y=0)")
        self.textEdit.append("")

    def pushbutton_proc_create_event(self):
        if self.procmanager_declared is False:
            self.textEdit.append("pm = ProcManager()")
            self.textEdit.append("")
            self.procmanager_declared = True
        
        self.textEdit.append("pm.create_process(popenargs, kwargs)")
        self.textEdit.append("")
        
    def pushbutton_proc_kill_event(self):
        if self.procmanager_declared is False:
            self.textEdit.append("pm = ProcManager()")
            self.textEdit.append("")
            self.procmanager_declared = True
        
        self.textEdit.append("pm.kill_process('insert here the process name')")
        self.textEdit.append("")
        
        
        
    
    def pushbutton_win_show_event(self):
        pass
        
    def pushbutton_win_maximize_event(self):
        pass
        
    def pushbutton_win_check(self):
        pass
        
    def pushbutton_win_close_event(self):
        pass
        
    def args_spinbox_change_event(self, event):
        self.args_number = self.spinBoxArgs.value()
        self.build_code_array()


class MainCodeForGui:
    
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
        self.find = False
        self.args_number = 0
        self.timeout = 60
        self.sendkeys = ""
        self.enable_performance = True
        self.warning = 15.00
        self.critical = 40.00
        
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
        self.show = True
        self.xml_path = ""
        self.click = False
        self.doubleclick = False
        self.sendkeys = ""

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
        #self.edit.setReadOnly(True)
 
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
        
    def toPlainText(self):
        return self.edit.toPlainText()
        
    def setFocus(self):
        self.edit.setFocus()
        
    def append(self, text):
        self.edit.append(text)
 
    def eventFilter(self, object, event):
        # Update the line numbers for all events on the text edit and the viewport.
        # This is easier than connecting all necessary singals.
        if object in (self.edit, self.edit.viewport()):
            self.number_bar.update()
            return False
        return QFrame.eventFilter(object, event)

 
    def getTextEdit(self):
        return self.edit