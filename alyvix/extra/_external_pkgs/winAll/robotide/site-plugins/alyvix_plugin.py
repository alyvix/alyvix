import wx
import os
import sys
import site


import win32gui
import re

import win32con
import win32com.client
        
from distutils.sysconfig import get_python_lib

#import subprocess
from robotide.pluginapi import Plugin
from robotide.pluginapi import ActionInfo, SeparatorInfo
from threading import Thread

#per i messaggi:
from robotide.pluginapi import RideTreeSelection, RideSaved, RideItem, RideSelectResource, RideClosing, RideOpenSuite, RideNewProject, RideUserKeyword

from PyQt4 import QtCore, QtGui

from Queue import Queue, Empty
from subprocess import PIPE, Popen
from threading  import Thread

started = False

class AlyvixRidePlugin(Plugin):

    def __init__(self, *args):
        Plugin.__init__(self, *args)
        self._full_file_name = None
        self._test_case_path = None

    def OnTreeSelection(self, message):
        #message ['node', 'item', 'text']
        pass
        """
        print "---"
        print message.node.GetText()
        print message.node.GetData()._datalist
        print message.topic
        """
        
    def OnProjectLoad(self, message):
        self._full_file_name = message.path
        print message.path
        self._update_path()
        
    def OnNewProjectCreation(self, message):
        self._full_file_name = message.path
        print message.path
        self._update_path()
        
    def enable(self):
        self._create_menu()
        #self.subscribe(self.close_popen, RideClosing)
        self.subscribe(self.OnProjectLoad, RideOpenSuite)
        self.subscribe(self.OnNewProjectCreation, RideNewProject)
        self.subscribe(self.OnTreeSelection, RideTreeSelection)
        #self.subscribe(self._log_message, RideLog)

    def disable(self):
        self.unsubscribe_all()
        self.unregister_actions()
        if self._window:
            self._window.close(self.notebook)

    def _create_menu(self):
        self.unregister_actions()
        #sep_info = SeparatorInfo("Tools")
        #print site.getsitepackages()
        
        logo_fullname = get_python_lib() + os.sep + "alyvix" + os.sep + "extra" + os.sep + "robotide" + os.sep +"images" + os.sep + "logo.png"
        #action_info =  ActionInfo('Alyvix', 'Alyvix Drawing Tools', self.OnViewLog, icon=self._load_image("alyvix_data\\aly_logo.png"))
        action_info =  ActionInfo('Alyvix', 'Alyvix Drawing Tools', self.OnViewLog, icon = self._load_image(logo_fullname))
        #self.register_action(sep_info)
        self.register_action(action_info)

                                        
    def _load_image(self, name):
        #path = self._get_img_path(name)
        print name
        return wx.Image(name, wx.BITMAP_TYPE_PNG).ConvertToBitmap()

    def _get_img_path(self, name):
        return os.path.join(os.path.dirname(__file__), name)
        
    def _update_path(self):
        pass
        """
        lines = self._full_file_name.split(os.sep)
        self._test_case_path = ""
        
        cnt = 0
        for line in lines:
        
            if cnt == len(lines) - 1:
                break
            self._test_case_path = self._test_case_path + line + os.sep
            cnt = cnt + 1
        
        self._test_case_path = self._test_case_path[:-1]
        print self._test_case_path
        """
        
    def enqueue_output(self, out, queue):
        for line in iter(out.readline, b''):
            #print line
            queue.put(line)
        out.close()
        global started
        started = False

                                        
    def OnViewLog(self, event):
        #self.window = ImageDialog()
        #self.window.show()
        global started
        if started is False:
            ON_POSIX = 'posix' in sys.builtin_module_names
            obj_selection_fullname = get_python_lib() + os.sep + "alyvix" + os.sep + "extra" + os.sep + "robotide" + os.sep + "alyvix_object_selection_controller.py"
            self.p = Popen(['pythonw', obj_selection_fullname, self._full_file_name], stdout=PIPE, bufsize=1, close_fds=ON_POSIX)
            q = Queue()
            t = Thread(target=self.enqueue_output, args=(self.p.stdout, q))
            t.daemon = True # thread dies with the program
            t.start()
            started = True
            """
            a = subprocess.Popen("python c:\\alan\\startqt4.py")
            started = True
            """
        else:
            #hwnd_found_list = self._get_hwnd("Alyvix - Selector")
            
            #print "select list", hwnd_found_list
            
            hwnd_found_list = self._get_hwnd("Alyvix - Object Selector")
            
            print "of list", hwnd_found_list
            
            if len(hwnd_found_list) > 0:
                return
            
            self._show_window("Alyvix - Selector")
        #worker = Thread(target=self.notepad)
        #worker.setDaemon(True)
        #worker.start()
        
    def close_popen(self, event):
        print "close"
        #os.killpg(self.p.pid, signal.SIGTERM)  # Send the signal to all the process groups
        self.p.kill()
        
    def _get_hwnd(self, window_title):
        windows_found = []
        hwnd_list = []
        win32gui.EnumWindows(self.__window_enumeration_handler, windows_found)
        self._win_found = None
        for hwnd_found, title_found in windows_found:
            if re.match(window_title, title_found, re.DOTALL) is not None and \
                    (win32gui.IsWindowVisible(hwnd_found) != 0 or win32gui.GetWindowTextLength(hwnd_found) > 0):
                hwnd_list.append(hwnd_found)

                try:
                    rect = win32gui.GetWindowRect(hwnd_found)
                    x = rect[0]
                    y = rect[1]
                    w = rect[2] - x
                    h = rect[3] - y


                    self._win_found = title_found + ", is visible: x=" + str(x) + ", y=" + str(y) + ", width=" + str(w) + ", height=" + str(h)
                except:
                    self._win_found = "nothing to show, window doesn't exist anymore"

        return hwnd_list

    def __window_enumeration_handler(self, hwnd, windows):
        windows.append((hwnd, win32gui.GetWindowText(hwnd)))
        
    def _show_window(self, window_title):

        hwnd_found_list = self._get_hwnd(window_title)
        for hwnd_found in hwnd_found_list:

            win32gui.SetWindowPos(hwnd_found,win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)
            win32gui.SetWindowPos(hwnd_found,win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)
            win32gui.SetWindowPos(hwnd_found,win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_SHOWWINDOW + win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)

            if win32gui.IsIconic(hwnd_found) != 0: #restore first
                win32gui.ShowWindow(hwnd_found, win32con.SW_RESTORE)
                
            win32gui.SetForegroundWindow(hwnd_found)