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
#from alyvix.tools.crypto import CryptoManager
from ctypes import *
import time
import sys
import os


class MouseManager(MouseManagerBase):

    def __init__(self):
        super(MouseManager, self).__init__()
        self.ahk = None

        self._coordmode = "CoordMode \"Mouse\", \"Screen\""

        autohotkey_dll_fullname = os.path.dirname(os.path.dirname(__file__)) +\
                                  os.sep + "ahkdll_x64w" + os.sep + "AutoHotkey.dll"

        self.ahk = CDLL(autohotkey_dll_fullname) #load AutoHotkey
        self.ahk.ahktextdll("") #start script in persistent mode (wait for action)

        while not self.ahk.ahkReady(): #Wait for the end of the empty script
            time.sleep(0.01)

        self._scaling_factor = 1


    def click(self, x, y, button=1, n_clicks=1, click_delay=10):

        xs = int(x / self._scaling_factor)
        ys = int(y / self._scaling_factor)

        self.move(xs, ys)

        #self.load_module()
        for cnt_click in range(n_clicks):


            if button == self.left_button:
                self.ahk.ahkExec(self._coordmode + "\nClick \"" + str(xs) + " " + str(ys) + "\"")

            elif button == self.right_button:
                self.ahk.ahkExec(self._coordmode + "\nClick \"right " + str(xs) + " " + str(ys) + "\"")
            elif button == self.middle_button:
                self.ahk.ahkExec(self._coordmode + "\nClick \"middle " + str(xs) + " " + str(ys) + "\"")

            time.sleep(click_delay / 1000)

    def move(self, x, y):

        xs = int(x/self._scaling_factor)
        ys = int(y/self._scaling_factor)

        #self.load_module()

        self.ahk.ahkExec(self._coordmode + "\nClick \"" + str(xs) + " " + str(ys+5) + " 0\"")
        time.sleep(0.25)
        self.ahk.ahkExec(self._coordmode + "\nClick \"" + str(xs) + " " + str(ys) + " 0\"")

    def scroll(self,x, y, steps, direction, scroll_delay):

        #self.load_module()

        xs = int(x/self._scaling_factor)
        ys = int(y/self._scaling_factor)

        self.move(xs, ys)

        cnt = 0
        if direction == self.wheel_down or direction == self.wheel_up:
            for step in range(0, steps, 1):
                if direction == self.wheel_down:
                    self.ahk.ahkExec(self._coordmode + "\nClick \"WheelDown\"")
                elif direction == self.wheel_up:
                    self.ahk.ahkExec(self._coordmode + "\nClick \"WheelUp\"")

                time.sleep(scroll_delay / 1000)

        elif direction == self.wheel_left or direction == self.wheel_right:
            if direction == self.wheel_left:
                self.ahk.ahkExec(self._coordmode + "\nClick \"middle\"")
                time.sleep(0.5)
                self.ahk.ahkExec(self._coordmode + "\nClick \"" + str(xs - steps) + " " + str(ys) + " 0\"")
                time.sleep(scroll_delay / 1000)
                self.ahk.ahkExec(self._coordmode + "\nClick \"middle\"")
            elif direction == self.wheel_right:
                self.ahk.ahkExec(self._coordmode + "\nClick \"middle\"")
                time.sleep(0.5)
                self.ahk.ahkExec(self._coordmode + "\nClick \"" + str(xs + steps) + " " + str(ys) + " 0\"")
                time.sleep(scroll_delay / 1000)
                self.ahk.ahkExec(self._coordmode + "\nClick \"middle\"")


    def hold(self, x, y):

        xs = int(x/self._scaling_factor)
        ys = int(y/self._scaling_factor)

        self.ahk.ahkExec(self._coordmode + "\nClick \"" + str(xs) + " " + str(ys) + " 0\"")
        time.sleep(0.25)
        self.ahk.ahkExec(self._coordmode + "\nClick \"down\"")
        time.sleep(0.25)
        self.ahk.ahkExec(self._coordmode + "\nClick \"" + str(xs) + " " + str(ys+5) + " 0\"")
        time.sleep(0.25)

    def release(self, x, y):

        xs = int(x/self._scaling_factor)
        ys = int(y/self._scaling_factor)

        self.ahk.ahkExec(self._coordmode + "\nClick \"" + str(xs) + " " + str(ys) + " 0\"")
        time.sleep(0.25)
        self.ahk.ahkExec(self._coordmode + "\nClick \"up\"")

    def drag(self, x1, y1, x2, y2, button=1):

        x1s = int(x1/self._scaling_factor)
        y1s = int(y1/self._scaling_factor)
        x2s = int(x2/self._scaling_factor)
        y2s = int(y2/self._scaling_factor)

        if button == self.left_button:

            self.ahk.ahkExec(self._coordmode + "\nClick \"" + str(x1s) + " " + str(y1s) + " 0\"")
            time.sleep(0.5)

            self.ahk.ahkExec(self._coordmode + "\nClick \"down\"")
            time.sleep(0.5)

            self.ahk.ahkExec(self._coordmode + "\nClick \"" + str(x2s) + " " + str(y2s) + " 0\"")
            time.sleep(0.5)

            self.ahk.ahkExec(self._coordmode + "\nClick \"up\"")
        elif button == self.right_button:

            self.ahk.ahkExec(self._coordmode + "\nClick \"" + str(x1s) + " " + str(y1s) + " 0\"")
            time.sleep(0.5)

            self.ahk.ahkExec(self._coordmode + "\nClick \"right down\"")
            time.sleep(0.5)

            self.ahk.ahkExec(self._coordmode + "\nClick \"" + str(x2s) + " " + str(y2s) + " 0\"")
            time.sleep(0.5)

            self.ahk.ahkExec(self._coordmode + "\nClick \"right up\"")
