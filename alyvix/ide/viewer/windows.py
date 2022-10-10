# Alyvix allows you to automate and monitor all types of applications
# Copyright (C) 2018 Alan Pipitone
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


from cefpython3 import cefpython as cef
from .base import ViewerManagerBase
import tempfile

import distutils.sysconfig
import math
import os
import re
import platform
import sys

import time
import json
import ctypes

import win32api
import win32con
import win32gui
import win32com.client
from alyvix.tools.screen import ScreenManager

from multiprocessing import Process

import urllib.request
import threading

# Globals
#cef.DpiAware.EnableHighDpiSupport()
WindowUtils = cef.WindowUtils()
g_multi_threaded = False



def set_foreground(window_handle):

    #time.sleep(1)

    """
    shell = win32com.client.Dispatch('WScript.Shell')
    shell.Run(
        "python.exe -c \"import win32gui; win32gui.SetForegroundWindow(" + str(window_handle) + "); win32gui.SetFocus(" + str(window_handle) + ")\"", 1, 1)

    """

    if win32gui.IsIconic(window_handle) != 0:  # restore first
        win32gui.ShowWindow(window_handle, win32con.SW_RESTORE)

    #win32gui.SetWindowPos(window_handle, win32con.HWND_TOPMOST, 0, 0, 0, 0,
    win32gui.SetWindowPos(window_handle, win32con.HWND_TOP, 0, 0, 0, 0,
                          win32con.SWP_SHOWWINDOW + win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)

    win32gui.SetActiveWindow(window_handle)


class ViewerManager(ViewerManagerBase):

    def __init__(self):
        super(ViewerManager, self).__init__()
        self.window_handle = None
        self._base_url = None
        self._title = None
        self._father = None
        self._browser_1 = None
        self._browser_2 = None
        self._browser_3 = None
        self._hwnd_1 = None
        self._hwnd_2 = None
        self._hwnd_3 = None
        self._sm = ScreenManager()

        self._ask_popup = False
        self._close_from_server = False

        self.shell = win32com.client.Dispatch("WScript.Shell")

    def close(self):

        try:
            win32gui.PostMessage(self._hwnd_1, win32con.WM_CLOSE, 0, 0)
        except:
            pass
        self._close_from_server = True

        try:
            #print("close_from_server")

            if self._father == "selector":
                win32gui.PostMessage(self._hwnd_2, win32con.WM_CLOSE, 0, 0)
            elif self._father == "ide":
                win32gui.PostMessage(self._hwnd_3, win32con.WM_CLOSE, 0, 0)
        except:
            pass

    def close_with_popup(self):
        MB_TOPMOST = 4096 #0x00040000

        MB_OK = 0
        MB_OKCANCEL = 1
        MB_YESNOCANCEL = 3
        MB_YESNO = 4

        IDOK = 0
        IDCANCEL = 2
        IDABORT = 3
        IDYES = 6
        IDNO = 7

        #result = win32api.MessageBoxW(None, "Are you sure you want to exit Alyvix Editor?", "Exit", 0 )
        result = ctypes.windll.user32.MessageBoxExW(0, "Are you sure you want to exit Alyvix Editor?", "Exit", MB_TOPMOST + MB_OKCANCEL)

        if result == 1:

            self._close_from_server = True
            self._ask_popup = False

            win32gui.PostMessage(self._hwnd_1, win32con.WM_CLOSE, 0, 0)

            win32gui.PostMessage(self._hwnd_3, win32con.WM_CLOSE, 0, 0)
        else:
            self._close_from_server = False
            self._ask_popup = False
            return

    def bring_last_window_on_top(self, source=1):
        enumerated_windows = []
        win32gui.EnumWindows(self._enum_handler, enumerated_windows)
        enumerated_windows = self._sort_windows(enumerated_windows)

        enumerated_windows = [s for s in enumerated_windows if s["visible"] is True and
                              s["title"] != "" and s["minimized"] is False and s["top_most"] is False]

        #print (enumerated_windows[0]["title"])
        #print(enumerated_windows[1]["title"])

        if (("python" and "alyvix_designer.py") in enumerated_windows[0]["title"]) or\
                (("python" and "alyvix_selector.py") in enumerated_windows[0]["title"]) or\
                (("python" and "alyvix_editor.py") in enumerated_windows[0]["title"]):
            hwnd_prev = enumerated_windows[1]["hwnd"]
        else:
            hwnd_prev = enumerated_windows[0]["hwnd"]

        #win32gui.SetActiveWindow(hwnd_prev)
        win32gui.SetForegroundWindow(hwnd_prev)

    def _sort_windows(self, windows):
        sorted_windows = []

        # Find the first entry
        for window in windows:
            if window["hwnd_above"] == 0:
                sorted_windows.append(window)
                break
        else:
            raise(IndexError("Could not find first entry"))

        # Follow the trail
        while True:
            for window in windows:
                if sorted_windows[-1]["hwnd"] == window["hwnd_above"]:
                    sorted_windows.append(window)
                    break
            else:
                break

        # Remove hwnd_above
        for window in windows:
            del(window["hwnd_above"])

        return sorted_windows


    def _enum_handler(self, hwnd, results):
        window_placement = win32gui.GetWindowPlacement(hwnd)

        rect = win32gui.GetWindowRect(hwnd)
        x, y, w, h = rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]

        styles = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)

        top_most = (styles & win32con.WS_EX_TOPMOST) == win32con.WS_EX_TOPMOST

        if top_most:
            tiotle = win32gui.GetWindowText(hwnd)
            a = "a"
            b = None

        results.append({
            "hwnd":hwnd,
            "hwnd_above":win32gui.GetWindow(hwnd, win32con.GW_HWNDPREV), # Window handle to above window
            "title":win32gui.GetWindowText(hwnd),
            "visible":win32gui.IsWindowVisible(hwnd) == 1,
            "minimized":window_placement[1] == win32con.SW_SHOWMINIMIZED,
            "maximized":window_placement[1] == win32con.SW_SHOWMAXIMIZED,
            "top_most": top_most,
            "x":x, "y": y, "w": w, "h": h
        })

    def change_title(self, hwnd, title):
        win32gui.SetWindowText(hwnd, title)

    def close_and_no_shutdown(self):
        win32gui.PostMessage(self._hwnd_2, win32con.WM_CLOSE, 0, 0)
        #print("close {}".format(self._hwnd_2))

    def hide(self, hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_HIDE)

    def show(self, hwnd):

        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)

        win32gui.SetActiveWindow(hwnd)
        #win32gui.BringWindowToTop(hwnd)

        # And SetAsForegroundWindow becomes
        self.shell.SendKeys('%')
        try:
            win32gui.SetForegroundWindow(hwnd)
        except:
            pass
        win32gui.BringWindowToTop(hwnd)
        self._browser_1.SetFocus(True)

        #self._browser_1.ExecuteJavascript("drawFromIde(" + str(x) + ", " + str(y) + ")")

    def get_mouse_pos(self, hwnd):
        h_x, h_y = win32api.GetCursorPos()
        x,y = win32gui.ScreenToClient(hwnd,(h_x, h_y))
        return x,y
        #print((h_x, h_y))
        #print((x,y))

    def resize_event(self):
        #print("resize")
        a = 10
        pass

    def load_url(self, url, window_handle):
        browser = cef.GetBrowserByWindowHandle(window_handle)
        browser.LoadUrl(url)

    def IsWindowVisible(self, handler):
        visible = win32gui.IsWindowVisible(handler)

        if visible == 1:
            return True
        elif visible == 0:
            return False

    def IsIconic(self, handler):
        iconic =  win32gui.IsIconic(handler)

        if iconic == 1:
            return True
        elif iconic == 0:
            return False

    def minimize(self, handler):
        win32gui.ShowWindow(handler, win32con.SW_MINIMIZE)

    def restore(self, handler):
        win32gui.ShowWindow(handler, win32con.SW_RESTORE)

    def run(self, url, father=None):
        global WindowUtils
        global g_multi_threaded

        base_url = url.rsplit('/', 1)[0]

        self._base_url = base_url
        
        scaling_factor = self._sm.get_scaling_factor()

        self._father = father

        self.command_line_args()
        self.check_versions()
        sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error

        settings = {
            "multi_threaded_message_loop": g_multi_threaded,
            "log_severity":cef.LOGSEVERITY_DISABLE,
            'cache_path': ''

        }

        switches = {} #{"disable-extension":True,}
        cef.Initialize(settings=settings, switches=switches)

        window_proc = {
            win32con.WM_CLOSE: self.close_window,
            win32con.WM_DESTROY: self.exit_app,
            win32con.WM_SIZE: WindowUtils.OnSize,
            #win32con.WM_DISPLAYCHANGE: self.resize_event,
            win32con.WM_SETFOCUS: WindowUtils.OnSetFocus,
            win32con.WM_ERASEBKGND: WindowUtils.OnEraseBackground
        }

        window_proc_2 = {
            win32con.WM_CLOSE: self.close_window_2,
            win32con.WM_DESTROY: self.exit_app,
            win32con.WM_SIZE: WindowUtils.OnSize,
            win32con.WM_SETFOCUS: WindowUtils.OnSetFocus,
            win32con.WM_ERASEBKGND: WindowUtils.OnEraseBackground
        }

        window_proc_3 = {
            win32con.WM_CLOSE: self.close_window_3,
            win32con.WM_DESTROY: self.exit_app,
            win32con.WM_SIZE: WindowUtils.OnSize,
            win32con.WM_SETFOCUS: WindowUtils.OnSetFocus,
            win32con.WM_ERASEBKGND: WindowUtils.OnEraseBackground
        }

        self._hwnd_1 = self.create_window(title="Alyvix Designer",
                                      class_name="alyvix.designer",
                                      width=800,
                                      height=800,
                                      window_proc=window_proc,
                                      icon="resources/chromium.ico",
                                      fullscreen=True)

        window_info = cef.WindowInfo()
        window_info.SetAsChild(self._hwnd_1)

        if father == "selector":
            self._hwnd_2 = self.create_window(title="Alyvix Selector",
                                          class_name="alyvix.selector",
                                          width=int(1300*scaling_factor),
                                          height=int(460*scaling_factor),
                                          window_proc=window_proc_2,
                                          icon="resources/chromium.ico",
                                          fullscreen=False)

            window_info_2 = cef.WindowInfo()
            window_info_2.SetAsChild(self._hwnd_2)

            self.hide(self._hwnd_1)


        elif father == "ide":

            self._hwnd_3 = self.create_window(title="Alyvix Editor",
                                              class_name="alyvix.editor",
                                              width=1000,
                                              height=600,
                                              window_proc=window_proc_3,
                                              icon="resources/chromium.ico",
                                              fullscreen=False)

            window_info_3 = cef.WindowInfo()
            window_info_3.SetAsChild(self._hwnd_3)

            self.hide(self._hwnd_1)


        if g_multi_threaded:
            # When using multi-threaded message loop, CEF's UI thread
            # is no more application's main thread. In such case browser
            # must be created using cef.PostTask function and CEF message
            # loop must not be run explicitilly.
            cef.PostTask(cef.TID_UI,
                         self.create_browser,
                         window_info,
                         {},
                         url)
            win32gui.PumpMessages()

        else:
            
            if father == "selector":
                self._browser_1 = self.create_browser(window_info=window_info,
                               settings={"plugins_disabled":True},
                               url=self._base_url + "/static/blank.html")


                self._browser_2 = self.create_browser(window_info=window_info_2,
                                                      settings={"plugins_disabled": True},
                                                      url=url)
                #time.sleep(0.5)
                self.show(self._hwnd_2)

            elif father == "ide":
                self._browser_1 = self.create_browser(window_info=window_info,
                               settings={"plugins_disabled":True},
                               url=self._base_url + "/static/blank.html")


                self._browser_3 = self.create_browser(window_info=window_info_3,
                                                      settings={"plugins_disabled": True},
                                                      url=url)

                #time.sleep(0.5)
                self.show(self._hwnd_3)
            else:
                self._browser_1 = self.create_browser(window_info=window_info,
                               settings={"plugins_disabled":True},
                               url=url)

                #time.sleep(0.5)
                self.show(self._hwnd_1)

            #foreground_process = Process(target=set_foreground, args=(window_handle,))
            #foreground_process.start()

            cef.MessageLoop()

        cef.Shutdown()


    def command_line_args(self):
        global g_multi_threaded
        if "--multi-threaded" in sys.argv:
            sys.argv.remove("--multi-threaded")
            #print("[pywin32.py] Message loop mode: CEF multi-threaded"
            #      " (best performance)")
            g_multi_threaded = True
        else:
            #print("[pywin32.py] Message loop mode: CEF single-threaded")
            pass

        """
        if len(sys.argv) > 1:
            print("ERROR: Invalid args passed."
                  " For usage see top comments in pywin32.py.")
            sys.exit(1)
        """


    def check_versions(self):
        if platform.system() != "Windows":
            #print("ERROR: This example is for Windows platform only")
            sys.exit(1)

        #print("[pywin32.py] CEF Python {ver}".format(ver=cef.__version__))
        #print("[pywin32.py] Python {ver} {arch}".format(
        #    ver=platform.python_version(), arch=platform.architecture()[0]))

        # PyWin32 version
        python_lib = distutils.sysconfig.get_python_lib(plat_specific=1)
        with open(os.path.join(python_lib, "pywin32.version.txt")) as fp:
            pywin32_version = fp.read().strip()
        #print("[pywin32.py] pywin32 {ver}".format(ver=pywin32_version))

        assert cef.__version__ >= "57.0", "CEF Python v57.0+ required to run this"


    def create_browser(self, window_info, settings, url):
        assert (cef.IsThread(cef.TID_UI))
        browser = cef.CreateBrowserSync(window_info=window_info,
                                        settings=settings,
                                        url=url)
        return browser


    def create_window(self, title, class_name, width, height, window_proc, icon, fullscreen):
        # Register window class
        wndclass = win32gui.WNDCLASS()
        wndclass.hInstance = win32api.GetModuleHandle(None)
        wndclass.lpszClassName = class_name
        wndclass.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW
        wndclass.hbrBackground = win32con.COLOR_WINDOW
        wndclass.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        wndclass.lpfnWndProc = window_proc

        atom_class = win32gui.RegisterClass(wndclass)
        assert (atom_class != 0)

        # Center window on screen.
        screenx = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        screeny = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        xpos = int(math.floor((screenx - width) / 2))
        ypos = int(math.floor((screeny - height) / 2))
        if xpos < 0:
            xpos = 0
        if ypos < 0:
            ypos = 0

        # Create window
        if fullscreen is True:
            window_style = (win32con.WS_CLIPCHILDREN | win32con.WS_POPUP | win32con.WS_VISIBLE)

            width = win32api.GetSystemMetrics(0)
            height = win32api.GetSystemMetrics(1)
            window_handle = win32gui.CreateWindow(class_name, title, window_style,
                                                  0, 0, width, height,
                                                  0, 0, wndclass.hInstance, None)

        else:
            window_style = (win32con.WS_OVERLAPPEDWINDOW | win32con.WS_CLIPCHILDREN
                        | win32con.WS_VISIBLE)

            width_s = win32api.GetSystemMetrics(0)
            height_s = win32api.GetSystemMetrics(1)

            if class_name == "alyvix.editor":
                xpos = 5
                ypos = 5
                width = width_s - 10
                height = height_s - 10
            window_handle = win32gui.CreateWindow(class_name, title, window_style,
                                              xpos, ypos, width, height,
                                              0, 0, wndclass.hInstance, None)


            if class_name == "alyvix.editor":
                win32gui.ShowWindow(window_handle, win32con.SW_MAXIMIZE)




        assert (window_handle != 0)

        # Window icon
        icon = os.path.abspath(icon)
        if not os.path.isfile(icon):
            icon = None
        if icon:
            # Load small and big icon.
            # WNDCLASSEX (along with hIconSm) is not supported by pywin32,
            # we need to use WM_SETICON message after window creation.
            # Ref:
            # 1. http://stackoverflow.com/questions/2234988
            # 2. http://blog.barthe.ph/2009/07/17/wmseticon/
            bigx = win32api.GetSystemMetrics(win32con.SM_CXICON)
            bigy = win32api.GetSystemMetrics(win32con.SM_CYICON)
            big_icon = win32gui.LoadImage(0, icon, win32con.IMAGE_ICON,
                                          bigx, bigy,
                                          win32con.LR_LOADFROMFILE)
            smallx = win32api.GetSystemMetrics(win32con.SM_CXSMICON)
            smally = win32api.GetSystemMetrics(win32con.SM_CYSMICON)
            small_icon = win32gui.LoadImage(0, icon, win32con.IMAGE_ICON,
                                            smallx, smally,
                                            win32con.LR_LOADFROMFILE)
            win32api.SendMessage(window_handle, win32con.WM_SETICON,
                                 win32con.ICON_BIG, big_icon)
            win32api.SendMessage(window_handle, win32con.WM_SETICON,
                                 win32con.ICON_SMALL, small_icon)

        return window_handle


    def close_window(self, window_handle, message, wparam, lparam):

        try:
            browser = cef.GetBrowserByWindowHandle(self._hwnd_1)
            browser.CloseBrowser(True)
        except:
            pass

        return win32gui.DefWindowProc(window_handle, message, wparam, lparam)

    def close_window_2(self, window_handle, message, wparam, lparam):

        try:
            browser2 = cef.GetBrowserByWindowHandle(self._hwnd_2)
            browser2.CloseBrowser(True)

            aa = urllib.request.urlopen(self._base_url + "/selector_close_api").read()
        except:
            pass

        return win32gui.DefWindowProc(window_handle, message, wparam, lparam)

    def close_window_3(self, window_handle, message, wparam, lparam):

        result = 1

        if self._close_from_server is False:

            self._ask_popup = True
            #print("force per libe")
            res = urllib.request.urlopen(self._base_url + "/force_set_lib").read()

            #print("force libe")

            #res = urllib.request.urlopen(self._base_url + "/is_lib_changed_api").read()

            #json_re = json.loads(res)

            #if json_re["success"] is True:
                #result = win32api.MessageBox(None, "Are you sure you want to exit Alyvix Editor?", "Exit", 1)
            #result = 2

        else:
            #print("close_from_Ser")
            try:
                browser3 = cef.GetBrowserByWindowHandle(self._hwnd_3)
                browser3.CloseBrowser(True)

                # selector_close_api close the web server without do anything else
                aa = urllib.request.urlopen(self._base_url + "/selector_close_api").read()
            except:
                pass

            return win32gui.DefWindowProc(window_handle, message, wparam, lparam)





    def exit_app(self, *_):
        win32gui.PostQuitMessage(0)
        return 0