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

from .base import KeyboardManagerBase
#from alyvix.tools.crypto import CryptoManager
from ctypes import *
import time
import sys
import os


class KeyboardManager(KeyboardManagerBase):

    def __init__(self):
        self.ahk = None
        self.load_module()

    def load_module(self, delay=10, duration=-1):
        #print "mouse manager"
        #python_path = os.path.split(sys.executable)[0]
        autohotkey_dll_fullname = os.path.dirname(os.path.dirname(__file__))\
                                  + os.sep + "ahkdll_x64w" + os.sep + "AutoHotkey.dll"

        self.ahk = CDLL(autohotkey_dll_fullname) #load AutoHotkey
        self.ahk.ahktextdll("") #start script in persistent mode (wait for action)

        while not self.ahk.ahkReady(): #Wait for the end of the empty script
            time.sleep(0.01)

        self.ahk.ahkExec("SetKeyDelay \"" + str(delay) + " " + str(duration) + "\"")

    def send(self, keys, encrypted=False, delay=10, duration=-1):

        self.ahk.ahkExec("SetKeyDelay \"" + str(delay) + " " + str(duration) + "\"")

        text = keys.replace("!", "{!}").replace("^", "{^}").replace("#", "{#}").replace("+", "{+}")

        if encrypted == False:
            self.ahk.ahkExec("SendEvent \"" + text + "\"")
        else:
            pass
            #cm = CryptoManager()
            #plain_keys = cm.decrypt_data(keys)
            #self.ahk.ahkExec("SendEvent " + plain_keys)
