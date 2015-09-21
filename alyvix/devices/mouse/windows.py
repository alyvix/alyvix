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

from .base import MouseManagerBase
from alyvix.tools.crypto import CryptoManager
from ctypes import *
import time
import sys
import os


class MouseManager(MouseManagerBase):

    def __init__(self):
        super(MouseManager, self).__init__()
        #print "mouse manager"
        python_path = os.path.split(sys.executable)[0]
        autohotkey_dll_fullname = python_path + os.sep + "DLLs" + os.sep + "AutoHotkey.dll"

        self.ahk = CDLL(autohotkey_dll_fullname) #load AutoHotkey
        self.ahk.ahktextdll(unicode("","utf-8")) #start script in persistent mode (wait for action)

        while not self.ahk.ahkReady(): #Wait for the end of the empty script
            time.sleep(0.01)

    def click(self, x, y, button=1, n=1):

        self.ahk.ahkExec("CoordMode, mouse, screen".decode("utf-8"))

        if button == self.left_button:
            self.ahk.ahkExec("Click " + str(x).decode("utf-8") + ", " + str(y).decode("utf-8") + ", " +
                             str(n).decode("utf-8"))
        elif button == self.right_button:
            self.ahk.ahkExec("Click " + str(x).decode("utf-8") + ", " + str(y).decode("utf-8") + ", right")
        elif button == self.middle_button:
            self.ahk.ahkExec("Click " + str(x).decode("utf-8") + ", " + str(y).decode("utf-8") + ", middle")

    def move(self, x, y):
        self.ahk.ahkExec("CoordMode, mouse, screen".decode("utf-8"))
        self.ahk.ahkExec("Click " + str(x).decode("utf-8") + ", " + str(y).decode("utf-8") + ", 0")

    def scroll(self, steps, direction):

        self.ahk.ahkExec("CoordMode, mouse, screen".decode("utf-8"))

        cnt = 0
        for step in range(0, steps, 1):
            if direction == self.wheel_down:
                self.ahk.ahkExec("Click WheelDown".decode("utf-8"))
            elif direction == self.wheel_up:
                self.ahk.ahkExec("Click WheelUp".decode("utf-8"))

    def drag(self, x1, y1, x2, y2, button=1):
        self.ahk.ahkExec("CoordMode, mouse, screen".decode("utf-8"))

        if button == self.left_button:
            self.ahk.ahkExec("Click " + str(x1).decode("utf-8") + ", " + str(y1).decode("utf-8") + ", 0")
            time.sleep(1)
            self.ahk.ahkExec("Click down".decode("utf-8"))
            time.sleep(1)
            self.ahk.ahkExec("Click " + str(x2).decode("utf-8") + ", " + str(y2).decode("utf-8") + ", 0")
            time.sleep(1)
            self.ahk.ahkExec("Click up".decode("utf-8"))
        elif button == self.right_button:
            self.ahk.ahkExec("Click " + str(x1).decode("utf-8") + ", " + str(y1).decode("utf-8") + ", 0")
            self.ahk.ahkExec("Click right down".decode("utf-8"))
            self.ahk.ahkExec("Click " + str(x2).decode("utf-8") + ", " + str(y2).decode("utf-8") + ", 0")
            self.ahk.ahkExec("Click right up".decode("utf-8"))
