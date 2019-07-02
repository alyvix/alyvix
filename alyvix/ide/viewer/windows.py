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

import distutils.sysconfig
import math
import os
import re
import platform
import sys

import time

import win32api
import win32con
import win32gui
import win32com.client

from multiprocessing import Process

import urllib.request


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

    def close(self):
        cef.Shutdown()
        win32gui.PostMessage(self.window_handle, win32con.WM_CLOSE, 0, 0)

    def hide(self):
        win32gui.ShowWindow(self.window_handle, win32con.SW_HIDE)

    def show(self):
        win32gui.ShowWindow(self.window_handle, win32con.SW_SHOW)

    def set_win_handler(self, handler):
        self.window_handle = handler

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

    def run(self, url, fullscreen=False, dimension=None, title=None):
        global WindowUtils
        global g_multi_threaded

        self.command_line_args()
        self.check_versions()
        sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error

        settings = {
            "multi_threaded_message_loop": g_multi_threaded,
            "log_severity":cef.LOGSEVERITY_DISABLE,

        }

        switches = {} #{"disable-extension":True,}
        cef.Initialize(settings=settings, switches=switches)

        window_proc = {
            win32con.WM_CLOSE: self.close_window,
            win32con.WM_DESTROY: self.exit_app,
            win32con.WM_SIZE: WindowUtils.OnSize,
            win32con.WM_SETFOCUS: WindowUtils.OnSetFocus,
            win32con.WM_ERASEBKGND: WindowUtils.OnEraseBackground
        }

        if dimension is not None:
            width = dimension[0]
            height = dimension[1]
        else:
            width = 450
            height = 600

        if title is not None:
            win_title = title
        else:
            win_title = "Alyvix Designer"

        window_handle = self.create_window(title=win_title,
                                      class_name="pywin32.example",
                                      width=width,
                                      height=height,
                                      window_proc=window_proc,
                                      icon="resources/chromium.ico",
                                      fullscreen=fullscreen)

        base_url = url.rsplit('/',1)[0]

        handler_type = None

        if win_title == "Alyvix Designer":
            handler_type = "designer"
        elif win_title == "Alyvix Selector":
            handler_type = "selector"

        aa = urllib.request.urlopen(base_url + "/set_viewer_handler_api?handler=" + str(window_handle) +
                                    "&type=" + handler_type).read()

        window_info = cef.WindowInfo()
        window_info.SetAsChild(window_handle)

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
            self.create_browser(window_info=window_info,
                           settings={"plugins_disabled":True},
                           url=url,
                           fullscreen=fullscreen)

            """
            if win32gui.IsIconic(window_handle) != 0: #restore first
                win32gui.ShowWindow(window_handle, win32con.SW_RESTORE)


            win32gui.SetWindowPos(window_handle,win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)
            win32gui.SetWindowPos(window_handle,win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)
            win32gui.SetWindowPos(window_handle,win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_SHOWWINDOW + win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)

            #win32gui.BringWindowToTop(window_handle)
            #win32gui.SetActiveWindow(window_handle)
            """

            """
            shell = win32com.client.Dispatch('WScript.Shell')
            shell.Run(
                "python.exe -c \"import time; import win32gui; time.sleep(1); win32gui.SetForegroundWindow(" + str(window_handle) + ")\"", 1, 1)
            """

            foreground_process = Process(target=set_foreground, args=(window_handle,))
            foreground_process.start()

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


    def create_browser(self, window_info, settings, url, fullscreen):
        assert (cef.IsThread(cef.TID_UI))
        browser = cef.CreateBrowserSync(window_info=window_info,
                                        settings=settings,
                                        url=url)

        """
        if fullscreen is True:
            browser.ToggleFullscreen()
        """

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

            window_handle = win32gui.CreateWindow(class_name, title, window_style,
                                              xpos, ypos, width, height,
                                              0, 0, wndclass.hInstance, None)


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
        browser = cef.GetBrowserByWindowHandle(window_handle)
        browser.CloseBrowser(True)
        # OFF: win32gui.DestroyWindow(window_handle)
        return win32gui.DefWindowProc(window_handle, message, wparam, lparam)


    def exit_app(self, *_):
        win32gui.PostQuitMessage(0)
        return 0