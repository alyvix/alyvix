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

import os
import numpy
import win32gui
import win32ui
import win32api
import win32con
import ctypes
from ctypes.wintypes import HWND, LPCWSTR, UINT, DWORD
from PIL import Image
import cv2
import win32con
import win32service
from .base import ScreenManagerBase

exception_file = False
exception_file_name = None


class ScreenManager(ScreenManagerBase):

    def __init__(self):
        super(ScreenManager, self).__init__()

    def get_scaling_factor_before_start(self):
        scaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
        return scaleFactor

    def get_scaling_factor(self):
        """
        get the dpi scaling factor.

        :rtype: float
        :return: the dpi scaling factor
        """

        DPI100pc = 96  # DPI 96 is 100% scaling
        DPI_type = 0  # MDT_EFFECTIVE_DPI = 0, MDT_ANGULAR_DPI = 1, MDT_RAW_DPI = 2


        hwnd = win32gui.GetDesktopWindow()

        monitorhandle = ctypes.windll.user32.MonitorFromWindow(hwnd,DWORD(2))  # MONITOR_DEFAULTTONEAREST = 2
        X = UINT()
        Y = UINT()

        try:
            ctypes.windll.shcore.GetDpiForMonitor(monitorhandle, DPI_type, ctypes.pointer(X), ctypes.pointer(Y))
            dpi =(X.value, Y.value, (X.value + Y.value) / (2 * DPI100pc))
        except Exception:
            dpi=(96, 96, 1)  # Assume standard Windows DPI & scaling


        """
        96 DPI = 100% scaling
        
        120 DPI = 125% scaling
        
        144 DPI = 150% scaling
        
        192 DPI = 200% scaling
        """
        return dpi[2]


    def grab_desktop(self, return_type=0):
        """
        grab desktop screenshot.

        :type return_type: int
        :param return_type: 0 for pil image, 1 for color matrix, 2 for gray matrix
        :rtype: numpy.ndarray or Image.Image
        :return: the screenshot image
        """

        global exception_file
        global exception_file_name

        ret_image = None

        #we use pywin32 api instead of PIL ImageGrab.
        #ImageGrab is slower than pywin32
        #w = win32api.GetSystemMetrics(0)
        #h = win32api.GetSystemMetrics(1)
        hwnd = win32gui.GetDesktopWindow()
        wDC = win32gui.GetWindowDC(hwnd)
        dcObj=win32ui.CreateDCFromHandle(wDC)

        DESKTOPHORZRES = 118
        DESKTOPVERTRES = 117

        h = dcObj.GetDeviceCaps( DESKTOPVERTRES)
        w = dcObj.GetDeviceCaps( DESKTOPHORZRES)

        cDC=dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
        cDC.SelectObject(dataBitMap)
        try:
            cDC.BitBlt((0,0),(w, h) , dcObj, (0,0), win32con.SRCCOPY)

            #if screen is now ok and an error message was sent (but not yet processed) then delete the error message
            if exception_file is True:
                try:
                    os.remove(exception_file_name)
                except:
                    pass

                exception_file = False
                exception_file_name = None

        except:
            # if BitBlt fails, maybe the monitor is unavailable
            try:
                #if alyvix background service is intalled, we have to notify the service
                scm = win32service.OpenSCManager('localhost', None, win32service.SC_MANAGER_CONNECT)

                #if below method raises an exception then Alyvix Background Service is not installed
                win32service.OpenService(scm, 'Alyvix Background Service', win32service.SERVICE_QUERY_CONFIG)

                #if we are here then Alyvix Background Service is installed
                #save the exception file
                system_drive = os.environ['systemdrive']

                alyvix_bg_service_path = system_drive + os.sep + "ProgramData\\Alyvix\\exception\\screen"

                if not os.path.exists(alyvix_bg_service_path):
                    os.makedirs(alyvix_bg_service_path)

                filename = os.environ['username'] + ".txt"

                full_name = alyvix_bg_service_path + os.sep + filename

                if os.path.exists(full_name) is False:
                    text_file = open(full_name, "w")
                    text_file.write("BitBlt Error")
                    text_file.close()

                exception_file = True
                exception_file_name = full_name

            except:
                pass

            raise Exception("Windows does not provide frames")

        bmpinfo = dataBitMap.GetInfo()
        bmpstr = dataBitMap.GetBitmapBits(True)

        ret_image = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1)

        # Free Resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        if return_type == self.get_color_mat:
            return self._get_cv_color_mat(ret_image)
        if return_type == self.get_gray_mat:
            mat = self._get_cv_color_mat(ret_image)
            return self._get_cv_gray_mat(mat)
        else:
            return ret_image

    def is_resolution_ok(self):

        try:
            height = None
            width = None
            scm = win32service.OpenSCManager('localhost', None, win32service.SC_MANAGER_CONNECT)
            s = win32service.OpenService(scm, 'Alyvix Background Service', win32service.SERVICE_QUERY_CONFIG)
            cfg = win32service.QueryServiceConfig(s)
            config_file = os.path.dirname(str(cfg[3]).replace("\"","")) + os.sep + "AlyvixBackgroundService.exe.config"

            lines = []
            with open(str(config_file)) as f:
                lines = f.readlines()

            for line in lines:
                if "height" in line:
                    height = line.replace("<add key=\"height\" value=\"","")
                    height = height.replace("\"/>", "")
                    height = height.replace(" ","")
                    height = height.replace("\t","")
                    height = int(height)

                if "width" in line:
                    width = line.replace("<add key=\"width\" value=\"", "")
                    width = width.replace("\"/>", "")
                    width = width.replace(" ", "")
                    width = width.replace("\t", "")
                    width = int(width)

            if height is not None and width is not None:
                hwnd = win32gui.GetDesktopWindow()
                wDC = win32gui.GetWindowDC(hwnd)
                dcObj = win32ui.CreateDCFromHandle(wDC)

                HORZRES = 8
                VERTRES = 10

                DESKTOPHORZRES = 118
                DESKTOPVERTRES = 117

                v_HORZRES = dcObj.GetDeviceCaps(HORZRES)
                v_VERTRES = dcObj.GetDeviceCaps(VERTRES)

                v_DESKTOPHORZRES = dcObj.GetDeviceCaps(DESKTOPHORZRES)
                v_DESKTOPVERTRES = dcObj.GetDeviceCaps(DESKTOPVERTRES)

                dcObj.DeleteDC()

                scaling = round(float(v_DESKTOPVERTRES) / float(v_VERTRES), 2)  # two decimal

                #if scaling >= 1.0:
                #    return False

                if width == 1366: #fix for the windows 7 bug with rdp and 1366x768 res
                    if v_DESKTOPHORZRES >= 1364 and v_DESKTOPHORZRES <= 1368\
                            and height == v_DESKTOPVERTRES:
                        return True
                    else:
                        return False
                elif height != v_DESKTOPVERTRES or width != v_DESKTOPHORZRES:
                    return False
        except:
            pass

        return True

    def get_resolution(self):

        hwnd = win32gui.GetDesktopWindow()
        wDC = win32gui.GetWindowDC(hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)

        HORZRES = 8
        VERTRES = 10

        DESKTOPHORZRES = 118
        DESKTOPVERTRES = 117

        v_HORZRES = dcObj.GetDeviceCaps(HORZRES)
        v_VERTRES = dcObj.GetDeviceCaps(VERTRES)

        v_DESKTOPHORZRES = dcObj.GetDeviceCaps(DESKTOPHORZRES)
        v_DESKTOPVERTRES = dcObj.GetDeviceCaps(DESKTOPVERTRES)

        dcObj.DeleteDC()

        return (v_DESKTOPHORZRES,v_DESKTOPVERTRES)