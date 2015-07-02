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

import cv2
import numpy
import time
import sys

from alyvix.core.cache import CacheManagement
from alyvix.tools.screenmanager import ScreenManager

# System modules
from Queue import Queue
from threading import Thread

class PerfCounter():

    __cacheManagement = None
    __min_different_pixel = 5000
    __queue = Queue()

    __time_elapsed = 0
    __time_of_last_change = 0
    __time_found = 0

    __flag_thread_started = False
    __flag_thread_have_to_exit = False

    def __init__(self):
        self.__cacheManagement = CacheManagement()

    def Init(self, name, timeout=15, min_different_pixel=5000):
        self.__min_different_pixel = min_different_pixel

    def StartThread(self, q):
        while True:
            print q.get()
            if self.__flag_thread_have_to_exit is True:
                print "Trhead exit1111111111111111111111111111111111111111111111111111111111111"
                self.__flag_thread_have_to_exit = False
                self.__flag_thread_started = False
                break

    def GetValue(self, callback_function):

        self.__queue.put("a")
        self.__queue.put("b")

        screenCapture = ScreenManager()

        img1 = self.__cacheManagement.GetLastObjFoundFullImg()

        if img1 is None:
            img1 = screenCapture.grab_desktop(screenCapture.getGrayMat)

        thread_started_time = time.time()
        while True:
            loop_time_t0 = time.time()

            img2 = screenCapture.grab_desktop(screenCapture.getGrayMat)

            fgbg = cv2.BackgroundSubtractorMOG()


            if time.time() - thread_started_time >= 2:
                thread_started_time = time.time()
                #self.__queue.put(False)
                print "passati 2 sec. !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
                if self.__flag_thread_started is False:
                    self.__flag_thread_started = True
                    print "Worker Started-------------------------------------------------------------------------"
                    worker = Thread(target=self.StartThread, args=(self.__queue,))
                    worker.setDaemon(True)
                    worker.start()

            t0 = time.time()

            fgbg.apply(img1)

            fgmask = fgbg.apply(img2)

            n_white = cv2.countNonZero(fgmask)
            print "white", n_white

            tempo_trascorso = time.time() - t0

            if n_white >= self.__min_different_pixel:
                self.__queue.put(True)
                print "diversi++++++++++++++++++++++++++++++++++++++++++++++++"
                img1 = img2.copy()
                self.__time_of_last_change = self.__time_elapsed
                self.__flag_thread_have_to_exit = True

            print "tempo", tempo_trascorso

            cv2.imwrite('mask.png',fgmask)

            time_sleep = 0.1 - tempo_trascorso
            if time_sleep < 0:
                time_sleep = 0
            print "time sleep", time_sleep

            time.sleep(time_sleep)

            loop_time = time.time() - loop_time_t0

            self.__time_elapsed = self.__time_elapsed + loop_time
            print self.__time_elapsed