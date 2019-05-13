# Alyvix allows you to automate and monitor all types of applications
# Copyright (C) 2019 Alan Pipitone
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
import json
import time
import base64
import threading
import numpy as np
from alyvix.tools.screen import ScreenManager
from alyvix.tools.library import LibraryManager
from .image import ImageManager
from .rectangle import RectangleManager


class Roi:

    def __init__(self):
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        self.unlimited_left = 0
        self.unlimited_up = 0
        self.unlimited_right = 0
        self.unlimited_down = 0

class Result():
    def __init__(self):
        self.main = None
        self.subs = []
        self.group = None


class EngineManager(object):

    def __init__(self, object_json):
        lm = LibraryManager()
        self._object_json = object_json
        self._object_definition = lm.build_objects_from_string(object_json)

        np_array = np.fromstring(base64.b64decode(self._object_definition["screen"]), np.uint8)

        self._screen = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        self._group_0 = []
        self._group_1 = []
        self._group_2 = []

        for box in self._object_definition['boxes']:
            if box['group'] == 0:
                self._group_0.append(box)

            elif box['group'] == 1:
                self._group_1.append(box)

            elif box['group'] == 2:
                self._group_2.append(box)

        self._screens = []

        self._t0 = 0
        self.total_threads = 0
        self.stop_threads = False
        self._result = []
        self._last_screen = None

        self.lock = threading.Lock()

        aaa = None

    def _compress(self, current_color_screen):
        return cv2.imencode('.png', current_color_screen)[1]

    def _uncompress(self, compressed_img):
        return cv2.imdecode(compressed_img, cv2.IMREAD_COLOR)

    def _check_object_presence(self, color_screen):

        cnt_found = 0

        gray_screen = cv2.cvtColor(color_screen, cv2.COLOR_BGR2GRAY)

        for result_box in self._result:
            template = cv2.cvtColor(self._last_screen[result_box.y:result_box.y + result_box.h,
                                    result_box.x:result_box.x + result_box.w], cv2.COLOR_BGR2GRAY)

            src_x = result_box.x - 10
            src_y = result_box.y - 10
            src_w = result_box.w + 20
            src_h = result_box.h + 20

            if src_x < 0:
                src_x = 0

            if src_y < 0:
                src_y = 0

            if src_w > color_screen.shape[1]:
                src_w = color_screen.shape[1]

            if src_h > color_screen.shape[0]:
                src_h = color_screen.shape[0]

            source_image = gray_screen[src_y:src_y + src_h, src_x:src_x + src_w]

            cv2.imwrite("D:\\tmpl.png", template)
            cv2.imwrite("D:\\src.png", source_image)

            res = cv2.matchTemplate(source_image, template, cv2.TM_CCOEFF_NORMED)

            loc = np.where(res >= 0.8)

            points = list(zip(*loc[::-1]))

            if len(points) > 0:
                cnt_found += 1

        if cnt_found == len(self._result):
            return True
        else:
            return False

    def _get_appear_time(self):

        if self._check_object_presence(self._uncompress(self._screens[0][0])) is True:

            t0 = self._t0
            t1 = self._screens[0][1]

            tn = t0
            tn_1 = self._screens[0][1]

            time = tn + ((tn_1 - tn) / 2) - t0 - ((t1 - t0) / 2)
            accuracy = ((tn_1 - tn) / 2) + ((t1 - t0) / 2)

            """
            t0 = self._t0
            t1 = self._screens[0][1]

            time = t0 + ((t1 - t0) / 2) - t0 - ((t1 - t0) / 2)
            accuracy = ((t1 - t0) / 2) + ((t1 - t0) / 2)
            """
            return (time, accuracy)

        frame_step = 10
        loop_step = round(float(len(self._screens))/float(frame_step))
        loop_step = int(loop_step)

        if loop_step < 1:
            loop_step = 1

        last_found_index = len(self._screens) - 1
        last_notfound_index = 0

        for i in range(loop_step):

            if i == 0:
                continue

            index = (len(self._screens) - (frame_step * i))

            if self._check_object_presence(self._uncompress(self._screens[index][0])) is True:
                last_found_index = index
            else:
                last_notfound_index = index
                break

        for i in range(last_found_index):
            if i > last_notfound_index:
                if self._check_object_presence(self._uncompress(self._screens[i][0])) is True:
                    t0 = self._t0
                    t1 = self._screens[0][1]

                    tn = self._screens[i-1][1]
                    tn_1 = self._screens[i][1]


                    time = tn + ((tn_1-tn)/2) - t0 - ((t1 - t0)/2)
                    accuracy = ((tn_1 - tn)/2) +( (t1 - t0)/2)

                    return (time, accuracy)

        print("sadasdsd")


    def worker(self, current_color_screen, scaling_factor):
        current_gray_screen = cv2.cvtColor(current_color_screen, cv2.COLOR_BGR2GRAY)

        return_value = Result()
        return_group_0 = []
        return_group_1 = []
        return_group_2 = []
        mains_found = []

        for cnt_g in range(3):

            # main component g0
            box = None
            if cnt_g == 0:
                if len(self._group_0) == 0:
                    continue
                box = self._group_0[0]
            elif cnt_g == 1:
                if len(self._group_1) == 0:
                    continue
                box = self._group_1[0]
            elif cnt_g == 2:
                if len(self._group_2) == 0:
                    continue
                box = self._group_2[0]

            if box['type'] == 'I':
                # if box["is_main"] is True:
                im = ImageManager()

                template = self._screen[box["y"]:box["y"] + box["h"], box["x"]:box["x"] + box["w"]]

                im.set_template(template)

                im.set_color_screen(current_color_screen)
                im.set_gray_screen(current_gray_screen)
                im.set_scaling_factor(scaling_factor)

                mains_found = im.find(box["features"]["I"])

            elif box['type'] == 'R':
                rm = RectangleManager()

                rm.set_color_screen(current_color_screen)
                rm.set_gray_screen(current_gray_screen)
                rm.set_scaling_factor(scaling_factor)

                mains_found = rm.find(box["features"]["R"])

            elif box['type'] == 'T':
                pass

            subs_found = []

            sub_boxes = []
            if cnt_g == 0:
                sub_boxes = self._group_0[1:]
            elif cnt_g == 1:
                sub_boxes = self._group_1[1:]
            elif cnt_g == 2:
                sub_boxes = self._group_2[1:]

            if len(mains_found) > 0:
                for main_found in mains_found:
                    for box in sub_boxes:

                        roi = Roi()
                        roi.x = main_found.x + box["roi_x"]
                        roi.y = main_found.y + box["roi_y"]
                        roi.w = box["roi_w"]
                        roi.h = box["roi_h"]
                        roi.unlimited_left = box["roi_unlimited_left"]
                        roi.unlimited_up = box["roi_unlimited_up"]
                        roi.unlimited_right = box["roi_unlimited_right"]
                        roi.unlimited_down = box["roi_unlimited_down"]

                        if box['type'] == 'I':
                            # if box["is_main"] is True:
                            im = ImageManager()

                            template = self._screen[box["y"]:box["y"] + box["h"], box["x"]:box["x"] + box["w"]]


                            im.set_template(template, roi=roi)

                            im.set_color_screen(current_color_screen)
                            im.set_gray_screen(current_gray_screen)
                            im.set_scaling_factor(scaling_factor)

                            result = im.find(box["features"]["I"])
                            if len(result) > 0:
                                subs_found.append(result[0])

                        elif box['type'] == 'R':
                            rm = RectangleManager()

                            rm.set_color_screen(current_color_screen)
                            rm.set_gray_screen(current_gray_screen)
                            rm.set_scaling_factor(scaling_factor)

                            result = subs_found.append(rm.find(box["features"]["R"], roi=roi))

                            if len(result) > 0:
                                subs_found.append(result[0])


                        elif box['type'] == 'T':
                            pass

                    if len(subs_found) == len(sub_boxes):
                        if cnt_g == 0:
                            return_group_0.append(main_found)
                            return_group_0.extend(subs_found)
                        elif cnt_g == 1:
                            return_group_1.append(main_found)
                            return_group_1.extend(subs_found)
                        elif cnt_g == 2:
                            return_group_2.append(main_found)
                            return_group_2.extend(subs_found)
                        break


        self.lock.acquire()
        if self.stop_threads is False and (len(return_group_0) == len(self._group_0))\
                and (len(return_group_1) == len(self._group_1)) and (len(return_group_2) == len(self._group_2)):
            self.stop_threads = True
            self._result = []
            self._result.extend(return_group_0)
            self._result.extend(return_group_1)
            self._result.extend(return_group_2)
            self._last_screen = current_color_screen
        self.total_threads -= 1
        self.lock.release()

    def find(self):
        print("start")

        sm = ScreenManager()

        lock = threading.Lock()

        result = None

        MAX_THREADS = 1

        #time.sleep(5)

        scaling_factor = sm.get_scaling_factor()

        t_thread = time.time()

        self._t0 = time.time()

        self.total_threads = 0

        while True:

            #t_before_grab = time.time()
            current_color_screen = sm.grab_desktop(sm.get_color_mat)
            t_after_grab = time.time()

            #self._screens.append((t_before_grab, self._compress(current_color_screen), t_after_grab))
            self._screens.append((self._compress(current_color_screen), t_after_grab))

            self.lock.acquire()
            result = self._result
            stop_threads = self.stop_threads
            total_threads = self.total_threads
            self.lock.release()

            if len(result) > 0:
                appear_time = self._get_appear_time()
                return appear_time


            if time.time() - t_thread > 0.5 and total_threads < MAX_THREADS and stop_threads is False:
                thread = threading.Thread(target=self.worker, args=(current_color_screen,scaling_factor))
                thread.start()
                t_thread = time.time()
                self.lock.acquire()
                self.total_threads += 1
                self.lock.release()

            time.sleep(0.05) #delay 50 ms

