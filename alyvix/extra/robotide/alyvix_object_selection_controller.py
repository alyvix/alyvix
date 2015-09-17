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

from PyQt4.QtGui import QApplication, QDialog, QCursor, QImage, QPixmap, QListWidgetItem
from PyQt4.QtCore import Qt, QThread, SIGNAL, QTimer, QUrl, QString, QRect

from PyQt4.QtWebKit import QWebSettings

from alyvix_object_selection_view import Ui_Form
from alyvix_rect_finder_view import AlyvixRectFinderView
from alyvix_image_finder_view import AlyvixImageFinderView
from alyvix_text_finder_view import AlyvixTextFinderView
from alyvix_object_finder_view import AlyvixObjectFinderView
from alyvix_code_view import AlyvixCustomCodeView

from alyvix.tools.screen import ScreenManager

from stat import S_ISREG, ST_CTIME, ST_MODE

import shutil

class AlyvixMainMenuController(QDialog, Ui_Form):

    def __init__(self):
        QDialog.__init__(self)

        # Set up the user interface from Designer.
        self.setupUi(self)
        
        self.setFixedSize(self.size())

        #self.setWindowTitle('Application Object Properties')
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)
        
        self.connect(self.pushButtonNew, SIGNAL("clicked()"), self.add_item)
        self.connect(self.pushButtonEdit, SIGNAL("clicked()"), self.edit_item)
        self.connect(self.pushButtonRemove, SIGNAL("clicked()"), self.remove_item)
        self.connect(self.pushButtonCancel, SIGNAL("clicked()"), self.cancel_action)
        
        self.connect(self.pushButtonRF, SIGNAL("clicked()"), self.open_rectfinder_view)
        self.connect(self.pushButtonIF, SIGNAL("clicked()"), self.open_imagefinder_view)
        self.connect(self.pushButtonTF, SIGNAL("clicked()"), self.open_textfinder_view)
        self.connect(self.pushButtonOF, SIGNAL("clicked()"), self.open_objectfinder_controller)
        self.connect(self.pushButtonCC, SIGNAL("clicked()"), self.open_customcode_controller)
        
        self.window = None
        self.full_file_name = None
        self.path = None
        self.robot_file_name = None
        self.action = ""
        self.xml_name = ""
        
        if len(sys.argv) > 1:
            self.full_file_name = sys.argv[1]
            #print self.full_file_name
            
        self.update_path()
        self.update_list()
        
        self.gridLayoutWidget.hide()
        self.pushButtonCancel.hide()
        
    def update_path(self):
        lines = self.full_file_name.split(os.sep)
        self.path = ""
        
        cnt = 0
        for line in lines:
        
            if cnt == len(lines) - 1:
                break
            self.path = self.path + line + os.sep
            cnt = cnt + 1
        
        self.robot_file_name = lines[len(lines) - 1]
        self.robot_file_name = self.robot_file_name.split('.')[0]
        self.robot_file_name = self.robot_file_name
        
        self.path = self.path[:-1] + os.sep + "Alyvix" + lines[len(lines) - 1].split('.')[0] + "Objects"
        
        #print "path", self.path
    
    def remove_item(self):
        self.action = "remove"
        
        selected_index = self.listWidgetAlyObj.currentRow()
        #selected_text = self.listWidgetAlyObj.currentItem().text()
        selected_item_data = self.listWidgetAlyObj.currentItem().data(Qt.UserRole).toString()
        self.xml_name = str(selected_item_data)
        #self.xml_name = selected_text + ".xml"
        if self.xml_name.endswith("_RectFinder.xml"):
            self.alyvix_finder_controller = AlyvixRectFinderView(self)
        elif self.xml_name.endswith("_ImageFinder.xml"):
            self.alyvix_finder_controller = AlyvixImageFinderView(self)
        elif self.xml_name.endswith("_TextFinder.xml"):
            self.alyvix_finder_controller = AlyvixTextFinderView(self)
        elif self.xml_name.endswith("_ObjectFinder.xml"):
            self.alyvix_finder_controller = AlyvixObjectFinderView(self)
        elif self.xml_name.endswith("_CustomCode.xml"):
            self.alyvix_finder_controller = AlyvixCustomCodeView(self)
        
        self.alyvix_finder_controller.remove_code_from_py_file()
        
        
        if self.xml_name.endswith("_ObjectFinder.xml"):
            self.alyvix_finder_controller.delete_lock_list()
            os.remove(self.path + os.sep + str(self.xml_name).replace("_ObjectFinder.xml","_old_code.txt"))
        elif self.xml_name.endswith("_CustomCode.xml"):
            os.remove(self.path + os.sep + str(self.xml_name).replace("_CustomCode.xml","_old_code.txt"))
        else:
            os.remove(self.path + os.sep + str(self.xml_name).replace("xml","png"))
            
        """
        if not self.xml_name.endswith("_ObjectFinder.xml"):
            os.remove(self.path + os.sep + str(self.xml_name).replace("xml","png"))
        else:
            self.alyvix_finder_controller.delete_lock_list()
            os.remove(self.path + os.sep + str(self.xml_name).replace("_ObjectFinder.xml","_old_code.txt"))
        """

        os.remove(self.path + os.sep + str(self.xml_name))

        template_path = self.path + os.sep + str(self.xml_name).replace("_ImageFinder.xml","")
        
        if os.path.exists(template_path):
            shutil.rmtree(template_path)
        #self.update_list()
        
        item = self.listWidgetAlyObj.takeItem(selected_index)
        self.listWidgetAlyObj.removeItemWidget(item)
    
    def update_list(self):
        #dirs = os.listdir(self.full_file_name)
        #dirs = [d for d in os.listdir(self.path) if os.path.isdir(os.path.join(self.path, d))]
        
        # path to the directory (relative or absolute)
        dirpath = self.path

        try:
            # get all entries in the directory w/ stats
            entries = (os.path.join(dirpath, fn) for fn in os.listdir(dirpath))
            entries = ((os.stat(path), path) for path in entries)
        except:
            return

        # leave only regular files, insert creation date
        entries = ((stat[ST_CTIME], path)
                   for stat, path in entries if S_ISREG(stat[ST_MODE]))
        #NOTE: on Windows `ST_CTIME` is a creation date 
        #  but on Unix it could be something else
        #NOTE: use `ST_MTIME` to sort by a modification date
        
        if os.path.exists(self.path + os.sep + "lock_list.xml"):
            f = open(self.path + os.sep + "lock_list.xml")
            string = f.read()

        for cdate, path in sorted(entries):
            filename = os.path.basename(path)
            
            if os.path.exists(self.path + os.sep + "lock_list.xml"):
                if "<name>" + filename + "</name>" in string:
                    continue
            if filename.endswith('.xml') and not filename.endswith('list.xml') and not filename.endswith('data.xml'):
                item = QListWidgetItem()
                if filename.endswith('_RectFinder.xml'):
                    item.setText(filename[:-15] + " [RF]")
                elif filename.endswith('_ImageFinder.xml'):
                    item.setText(filename[:-16] + " [IF]")
                elif filename.endswith("_TextFinder.xml"):
                    item.setText(filename[:-15] + " [TF]")
                elif filename.endswith('_ObjectFinder.xml'):
                    item.setText(filename[:-17] + " [OF]")
                elif filename.endswith('_CustomCode.xml'):
                    item.setText(filename[:-15] + " [CC]")
                    
                item.setData(Qt.UserRole, filename)
                self.listWidgetAlyObj.addItem(item)
                
            #print time.ctime(cdate), os.path.basename(path)
    
        """
        files = []
        files += [each for each in os.listdir(self.path) if each.endswith('.xml')]
        
        for file in files:
            item = QListWidgetItem()
            #item.setCheckState(Qt.Checked)
            item.setText(file[:-4])
            self.listWidgetAlyObj.addItem(item)
            
        print self.listWidgetAlyObj.count() 
        """
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            #print "dummy"
            self.close()
            
    def closeEvent(self, event):
        if self.window is not None:
            self.window.close()
    
    def cancel_action(self):
        self.restore_view()
        
    def restore_view(self):
        self.gridLayoutWidget.hide()
        self.pushButtonCancel.hide()
        
        self.listWidgetAlyObj.setGeometry(QRect(8, 28, 218, 181))
        self.pushButtonEdit.show()
        self.pushButtonNew.show()
        self.pushButtonRemove.show()
        self.listWidgetAlyObj.show()
        self.label.show()

        self.gridLayoutWidget.setGeometry(QRect(8, 330, 218, 177))
        self.pushButtonCancel.setGeometry(QRect(62, 500, 111, 23))
    
    def add_item(self):
    
        self.action = "new"
        self.pushButtonEdit.hide()
        self.pushButtonNew.hide()
        self.pushButtonRemove.hide()
        self.listWidgetAlyObj.hide()
        self.label.hide()
        self.gridLayoutWidget.show()
        self.pushButtonCancel.show()
        self.gridLayoutWidget.setGeometry(QRect(8, 18, 218, 177))
        self.pushButtonCancel.setGeometry(QRect(62, 209, 111, 23))
        
                    
    def edit_item(self):
        self.action = "edit"
    
        if self.listWidgetAlyObj.currentRow() < 0:
            return
            
        #print self.listWidgetAlyObj.currentRow()
        
        selected_item_data = self.listWidgetAlyObj.currentItem().data(Qt.UserRole).toString()
        self.xml_name = str(selected_item_data)
        #print selected_item_data
        
        if self.xml_name.endswith("_ObjectFinder.xml"):
            self.hide()
            time.sleep(0.600)
            self.alyvix_finder_controller = AlyvixObjectFinderView(self)
            self.alyvix_finder_controller.show()
            return
            
        if self.xml_name.endswith("_CustomCode.xml"):
            self.hide()
            time.sleep(0.600)
            self.alyvix_finder_controller = AlyvixCustomCodeView(self)
            self.alyvix_finder_controller.show()
            return

        screen_manager = ScreenManager()
        self.hide()
        time.sleep(0.600)
        img_color = cv2.imread(str(self.xml_name).replace("xml","png")) #screen_manager.grab_desktop(screen_manager.get_color_mat)
        #print "imgggg", self.path + os.sep + self.xml_name
        image = QImage(self.path + os.sep + self.xml_name.replace("xml", "png"))
        #print self.path, self.robot_file_name, self.xml_name
        
        if self.xml_name.endswith("_RectFinder.xml"):
            self.alyvix_finder_controller = AlyvixRectFinderView(self)
        elif self.xml_name.endswith("_ImageFinder.xml"):
            self.alyvix_finder_controller = AlyvixImageFinderView(self)
        elif self.xml_name.endswith("_TextFinder.xml"):
            self.alyvix_finder_controller = AlyvixTextFinderView(self)
            
        #self.alyvix_rect_finder_controller.set_path(self.full_file_name)
        self.alyvix_finder_controller.set_bg_pixmap(image)
        self.alyvix_finder_controller.showFullScreen()
 
    def add_new_item_on_list(self): 
        dirpath = self.path

        # get all entries in the directory w/ stats
        entries = (os.path.join(dirpath, fn) for fn in os.listdir(dirpath))
        entries = ((os.stat(path), path) for path in entries)

        # leave only regular files, insert creation date
        entries = ((stat[ST_CTIME], path)
                   for stat, path in entries if S_ISREG(stat[ST_MODE]))
        #NOTE: on Windows `ST_CTIME` is a creation date 
        #  but on Unix it could be something else
        #NOTE: use `ST_MTIME` to sort by a modification date
        
        list_sorted = sorted(entries)
        cdate, path = list_sorted[-1]

        filename = os.path.basename(path)
        #print filename
        #print cdate
        
        item = QListWidgetItem()

        if filename.endswith('_RectFinder.xml'):
            item.setText(filename[:-15] + " [RF]")
        elif filename.endswith('_ImageFinder.xml'):
            item.setText(filename[:-16] + " [IF]")
        elif filename.endswith("_TextFinder.xml"):
            item.setText(filename[:-15] + " [TF]")
        elif filename.endswith('_old_code.txt'):
        
            cdate, path = list_sorted[-2]

            penultimate_name = os.path.basename(path)
        
            if penultimate_name.endswith('_ObjectFinder.xml'):
                item.setText(penultimate_name[:-17] + " [OF]")
                penultimate_name = penultimate_name.replace("_old_code.txt", "_ObjectFinder.xml")
                
            else:
                item.setText(penultimate_name[:-15] + " [CC]")
                penultimate_name = penultimate_name.replace("_old_code.txt", "_CustomCode.xml")

            item.setData(Qt.UserRole, penultimate_name)
            self.listWidgetAlyObj.addItem(item)
            return
        
        item.setData(Qt.UserRole, filename)
        self.listWidgetAlyObj.addItem(item)
        
    def open_rectfinder_view(self):
        self.xml_name = None
        self.restore_view()
        screen_manager = ScreenManager()
        self.hide()
        time.sleep(0.600)
        img_color = screen_manager.grab_desktop(screen_manager.get_color_mat)
        img_color = cv2.cvtColor(img_color, cv2.COLOR_BGR2RGB)
        image = QImage(img_color, img_color.shape[1], img_color.shape[0], img_color.strides[0], QImage.Format_RGB888)
        self.alyvix_rect_finder_controller = AlyvixRectFinderView(self)
        self.alyvix_rect_finder_controller.set_bg_pixmap(image)
        self.alyvix_rect_finder_controller.showFullScreen()
        
    def open_imagefinder_view(self):
        self.xml_name = None
        self.restore_view()
        screen_manager = ScreenManager()
        self.hide()
        time.sleep(0.600)
        img_color = screen_manager.grab_desktop(screen_manager.get_color_mat)
        img_color = cv2.cvtColor(img_color, cv2.COLOR_BGR2RGB)
        image = QImage(img_color, img_color.shape[1], img_color.shape[0], img_color.strides[0], QImage.Format_RGB888)
        self.alyvix_image_finder_controller = AlyvixImageFinderView(self)
        self.alyvix_image_finder_controller.set_bg_pixmap(image)
        self.alyvix_image_finder_controller.showFullScreen()
        
    def open_textfinder_view(self):
        self.xml_name = None
        self.restore_view()
        screen_manager = ScreenManager()
        self.hide()
        time.sleep(0.600)
        img_color = screen_manager.grab_desktop(screen_manager.get_color_mat)
        img_color = cv2.cvtColor(img_color, cv2.COLOR_BGR2RGB)
        image = QImage(img_color, img_color.shape[1], img_color.shape[0], img_color.strides[0], QImage.Format_RGB888)
        self.alyvix_text_finder_controller = AlyvixTextFinderView(self)
        self.alyvix_text_finder_controller.set_bg_pixmap(image)
        self.alyvix_text_finder_controller.showFullScreen()
        
    def open_objectfinder_controller(self):
        self.xml_name = None
        self.restore_view()
        #screen_manager = ScreenManager()
        self.hide()
        time.sleep(0.600)
        #img_color = screen_manager.grab_desktop(screen_manager.get_color_mat)
        #img_color = cv2.cvtColor(img_color, cv2.COLOR_BGR2RGB)
        #image = QImage(img_color, img_color.shape[1], img_color.shape[0], img_color.strides[0], QImage.Format_RGB888)
        self.alyvix_objectfinder_controller = AlyvixObjectFinderView(self)
        #self.alyvix_objectfinder_controller.set_bg_pixmap(image)
        self.alyvix_objectfinder_controller.show()
        
    def open_customcode_controller(self):
        self.xml_name = None
        self.restore_view()
        #screen_manager = ScreenManager()
        self.hide()
        time.sleep(0.600)
        #img_color = screen_manager.grab_desktop(screen_manager.get_color_mat)
        #img_color = cv2.cvtColor(img_color, cv2.COLOR_BGR2RGB)
        #image = QImage(img_color, img_color.shape[1], img_color.shape[0], img_color.strides[0], QImage.Format_RGB888)
        self.alyvix_custom_code_controller = AlyvixCustomCodeView(self)
        #self.alyvix_objectfinder_controller.set_bg_pixmap(image)
        self.alyvix_custom_code_controller.show()

if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = AlyvixMainMenuController()
    window.show()
    sys.exit(app.exec_())