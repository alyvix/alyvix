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

import re
import cv2
import json
import time
import copy
import base64
import shlex
import subprocess
import threading
import psutil
import os
import numpy as np
from datetime import datetime
from alyvix.tools.screen import ScreenManager
from alyvix.tools.library import LibraryManager
from alyvix.tools.crypto import CryptoManager
from alyvix.core.utilities.args import ArgsManager
from .image import ImageManager
from .rectangle import RectangleManager
from .text import TextManager
from alyvix.core.interaction.mouse import MouseManager
from alyvix.core.interaction.keyboard import KeyboardManager
from alyvix.core.utilities import common


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
        self.object_name = None
        self.detection_type = None
        self.has_to_break = None
        self.timestamp = None
        self.end_timestamp = None
        self.performance_ms = None
        self.accuracy_ms = None
        self.screenshot = None
        self.annotation = None
        self.timeout = None
        self.arguments = []
        self.records = {"text":"", "image":"", "extract":"", "check":"false"}

        self.group = None
        self.map_key = None
        self.thresholds = {"warning_s": None, "critical_s": None}
        self.output = True
        self.exit = "false"
        self.extended_name = None
        self.state = 0


class EngineManager(object):

    def __init__(self, object_json, args=None, maps={}, verbose=0, output_mode="alyvix", cipher_key=None, cipher_iv=None,
                 performances=None, map_names_map_keys=None, section_name=None):

        self._result = Result()

        #self._executed_objects = executed_objects
        self._executed_objects = []

        self._arguments_manager = ArgsManager()


        self._performances = performances

        self._map_names_map_keys = map_names_map_keys

        self.section_name = section_name

        self._output_mode = output_mode

        self._result.object_name = list(object_json.keys())[0]

        self._series_name = ""

        if map_names_map_keys is None:
            self._series_name  = self._result.object_name
        else:
            map_name_map_key = ""

            if map_names_map_keys is not None:
                for m_n_m_k in map_names_map_keys:
                    map_name_map_key += m_n_m_k["map_name"] + "-" + m_n_m_k["map_key"] + "_"
                map_name_map_key = map_name_map_key[:-1]
                self._series_name  = map_name_map_key

        if self._result.object_name != self._series_name:
            self._performance_name = self._result.object_name + "_" + self._series_name
        else:
            self._performance_name = self._result.object_name

        self._result.arguments = []

        self._first_attempt_finished = False

        self._crypto_manager = CryptoManager()
        self._crypto_manager.set_key(cipher_key)
        self._crypto_manager.set_iv(cipher_iv)

        try:
            self._result.group = object_json[self._result.object_name]["measure"]["group"]
        except:
            pass

        try:
            self._result.thresholds["warning_s"] = object_json[self._result.object_name]["measure"]["thresholds"]["warning_s"]
        except:
            del self._result.thresholds["warning_s"]

        try:
            self._result.thresholds["critical_s"] = object_json[self._result.object_name]["measure"]["thresholds"]["critical_s"]
        except:
            del self._result.thresholds["critical_s"]

        self._result.output = object_json[self._result.object_name]["measure"]["output"]

        self._verbose = verbose

        self._maps = maps
        self._result.map_key = None #map_key

        self._tmp_text_scraped = ""
        self._tmp_text_extracted = ""

        self._mouse_manager = MouseManager()
        self._keyboard_manager = KeyboardManager()

        self._library_manager = LibraryManager()

        self._screen_manager = ScreenManager()
        self._scaling_factor = self._screen_manager.get_scaling_factor()
        self._res_w, self._res_h = self._screen_manager.get_resolution()

        self._object_json = object_json
        self._object_definition = None
        self._detection = None

        self._object_definition = self._library_manager.build_objects_for_engine(self._object_json)
        self._detection = self._library_manager.get_detection_from_string(self._object_json)

        if self._detection["timeout_s"] == None:
            self._detection["timeout_s"] = 10

        self._call = self._library_manager.get_call_from_string(self._object_json)

        self._result.detection_type = self._detection["type"]
        self._result.has_to_break = self._detection["break"]

        np_screen_array = np.fromstring(base64.b64decode(self._object_definition["screen"]), np.uint8)

        self._screen = cv2.imdecode(np_screen_array, cv2.IMREAD_COLOR)

        self._group_0 = []
        self._group_1 = []
        self._group_2 = []

        self._g0_found = False
        self._g1_found = False
        self._g2_found = False

        self._cnt_text_components = 0
        self._arr_scraped_txt = []
        self._arr_extracted_txt = []


        for box in self._object_definition['boxes']:

            if box["type"] == "T":
                self._cnt_text_components += 1
                self._arr_scraped_txt.append({"text": "", "group": box["group"], "index_in_group": box["index_in_group"]})
                self._arr_extracted_txt.append({"text": "", "group": box["group"], "index_in_group": box["index_in_group"]})

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
        self._components_found = []
        self._components_appeared = []
        self._return_values = []
        self._timedout = False

        self._last_screen = None
        self._screen_with_objects = None
        self._annotation_screen = None

        self._appear_time = -1
        self._appear_accuracy = -1

        self._disappear_time = -1
        self._disappear_accuracy = -1

        self._disappear_mode = False

        self._objects_appeared = False
        self._objects_disappeared = False

        self._arguments = args

        self.lock = threading.Lock()

    def _get_timestamp_formatted(self):
        timestamp = time.time()
        date_from_ts = datetime.fromtimestamp(timestamp)
        # millis_from_ts = int(round(float(date_from_ts.strftime("0.%f")), 3) * 1000)
        try:
            millis_from_ts = date_from_ts.strftime("%f")[: -3]
        except:
            millis_from_ts = "000"

        date_formatted = date_from_ts.strftime("%Y/%m/%d %H:%M:%S") + "." + str(millis_from_ts)

        return date_formatted

    def _compress(self, current_color_screen):
        return cv2.imencode('.png', current_color_screen)[1]

    def _uncompress(self, compressed_img):
        return cv2.imdecode(compressed_img, cv2.IMREAD_COLOR)

    def _check_object_presence(self, color_screen):

        cnt_found = 0

        gray_screen = cv2.cvtColor(color_screen, cv2.COLOR_BGR2GRAY)

        for result_box in self._components_appeared:
            """
            if result_box.type == "T" and result_box.scraped_text is not None:
                cnt_found += 1
                continue
            """

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

            #cv2.imwrite("D:\\tmpl.png", template)
            #cv2.imwrite("D:\\src.png", source_image)

            res = cv2.matchTemplate(source_image, template, cv2.TM_CCOEFF_NORMED)

            loc = np.where(res >= 0.8)

            points = list(zip(*loc[::-1]))

            if len(points) > 0:
                cnt_found += 1

        if cnt_found == len(self._components_appeared):
            return True
        else:
            return False #cnt_found == len(self._components_found)

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
            return (time, accuracy, 0)

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
        #print("last_found_index" + str(last_found_index))
        #print("last_notfound_index" + str(last_notfound_index))
        #print("len screen" + str(len(self._screens)))

        for i in range(last_found_index+1):
            #cv2.imwrite("D:\\programdata\\log\\" + str(i) + "_searching.png", self._uncompress(self._screens[i][0]))

            if i > last_notfound_index and i < len(self._screens):
                if self._check_object_presence(self._uncompress(self._screens[i][0])) is True:

                    #cv2.imwrite("D:\\programdata\\log\\" + str(i) + "_searching.png", self._uncompress(self._screens[i][0]))

                    """
                       ###########################################
                       APPEAR
                       ###########################################
                       s = t0 + (t1 - t0)/2 +/- (t1 - t0)/2
                       A = t2 + (t3 - t2)/2 +/- (t3 - t2)/2
                       |   s   |   .   |   A   |
                       t0  *   t1      t2  *   t3
                           |<------------->| THIS ONE!
                       |<----------------->| NOT that one!!
                       Ap = t2 + (t3 - t2)/2 - t0 - (t1 - t0)/2
                       Aa = +/- ((t3 - t2)/2 + (t1 - t0)/2)
    
                    """
                    t0 = self._t0
                    t1 = self._screens[0][1]

                    tn = self._screens[i-1][1]
                    tn_1 = self._screens[i][1]


                    time = tn + ((tn_1-tn)/2) - t0 - ((t1 - t0)/2)
                    accuracy = ((tn_1 - tn)/2) +( (t1 - t0)/2)

                    return (time, accuracy, i)

    def _get_disappear_time(self, first_found_index, appear_disappear = True):

        #first found index need to calc A+D
        #last found index need to speedup loop

        frame_step = 10
        loop_step = round(float(len(self._screens)) / float(frame_step))
        loop_step = int(loop_step)

        if loop_step < 1:
            loop_step = 1

        #last_found_index = i
        last_found_index = first_found_index
        last_notfound_index = len(self._screens) - 1

        for i in range(loop_step):

            if i == 0:
                continue

            if i <= first_found_index:
                break

            index = (len(self._screens) - (frame_step * i))

            if self._check_object_presence(self._uncompress(self._screens[index][0])) is False:
                last_notfound_index = index
            else:
                last_found_index = index
                break

        if last_notfound_index <= last_found_index:
            last_notfound_index = last_found_index + 1

        #print("first_found_index " + str(first_found_index))
        #print("last_found_index " + str(last_found_index))
        #print("last_notfound_index " + str(last_notfound_index))

        for i in range(last_notfound_index+1):
            if i > last_found_index and i < len(self._screens):
                if self._check_object_presence(self._uncompress(self._screens[i][0])) is False:
                    """
    
                        ###########################################
                        APPEAR+DISAPPEAR
                        ###########################################
                        s = t0 + (t1 - t0)/2 +/- (t1 - t0)/2
                        D = t4 + (t5 - t4)/2 +/- (t5 - t4)/2
                        |   s   |   .   |   A   |   A   |   D   |
                        t0  *   t1      t2      t3      t4  *   t5
                            |<----------------------------->| THIS ONE!
                        Dp = t4 + (t5 - t4)/2 - t0 - (t1 - t0)/2
                        Da = +/- ((t5 - t4)/2 + (t1 - t0)/2)
    
    
                        ###########################################
                        DISAPPEAR
                        ###########################################
                        A = t2 + (t3 - t2)/2 +/- (t3 - t2)/2
                        D = t4 + (t5 - t4)/2 +/- (t5 - t4)/2
                        |   s   |   .   |   A   |   A   |   D   |
                        t0      t1      t2  *   t3      t4  *   t5
                                            |<------------->| THIS ONE!
                        ADp = t4 + (t5 - t4)/2 - t2 - (t3 - t2)/2
                        ADa = +/- ((t5 - t4)/2 + (t3 - t2)/2)
                    """
                    t0 = self._t0
                    t1 = self._screens[0][1]

                    tn = self._screens[i - 1][1]
                    tn_1 = self._screens[i][1]

                    if first_found_index == 0:
                        tn_a = t0
                        tn_a_1 = t1
                    else:
                        tn_a = self._screens[first_found_index - 1][1]
                        tn_a_1 = self._screens[first_found_index][1]

                    #dt = tn + ((tn_1 - tn) / 2)
                    #da = tn_a - ((tn_a_1 - tn_a) / 2)

                    if appear_disappear == True:
                        # t4 + (t5 - t4)/2 - t0 - (t1 - t0)/2
                        time = tn + ((tn_1 - tn) / 2) - t0 - ((t1 - t0) / 2)
                        accuracy = ((tn_1 - tn) / 2) + ((t1 - t0) / 2)

                    else:
                        time = tn + ((tn_1 - tn) / 2) - tn_a - ((tn_a_1 - tn_a) / 2)
                        accuracy = ((tn_1 - tn) / 2) + ((tn_a_1 - tn_a) / 2)

                    return (time, accuracy, i)

    def _exec_interactions(self):

        for component in self._components_appeared:

            #if component.type == "T" and component.scraped_text is not None:
            #    continue

            mouse_dict = component.mouse

            if mouse_dict["type"] is not None:


                time.sleep(0.2)

                point_dx = 0
                point_dy = 0

                try:
                    if (mouse_dict["features"]["point"]["dx"] != 0 or mouse_dict["features"]["point"]["dy"] != 0):
                        point_dx = mouse_dict["features"]["point"]["dx"]
                        point_dy = mouse_dict["features"]["point"]["dy"]
                except:
                    pass

                position_x = int(component.x + (component.w / 2))
                position_y = int(component.y + (component.h / 2))

                if point_dx != 0 or point_dy != 0:
                    position_x = component.x + point_dx
                    position_y = component.y + point_dy

                mouse_type = mouse_dict["type"]

                if mouse_type == "move":


                    self._mouse_manager.move(position_x, position_y)

                elif mouse_type == "click":
                    click_amount = mouse_dict["features"]["amount"]

                    click_button = self._mouse_manager.left_button

                    if mouse_dict["features"]["button"] == "right":
                        click_button = self._mouse_manager.right_button

                    self._mouse_manager.click(position_x, position_y, click_button, click_amount,
                                              mouse_dict["features"]["delays_ms"])

                elif mouse_type == "scroll":
                    scroll_amount = mouse_dict["features"]["amount"]

                    scroll_direction = mouse_dict["features"]["direction"]

                    if scroll_direction == "down":
                        self._mouse_manager.scroll(position_x, position_y, scroll_amount,
                                                   self._mouse_manager.wheel_down, mouse_dict["features"]["delays_ms"])
                    elif scroll_direction == "up":
                        self._mouse_manager.scroll(position_x, position_y, scroll_amount,
                                                   self._mouse_manager.wheel_up, mouse_dict["features"]["delays_ms"])
                    elif scroll_direction == "left":
                        self._mouse_manager.scroll(position_x, position_y, scroll_amount,
                                                   self._mouse_manager.wheel_left, mouse_dict["features"]["delays_ms"])
                    elif scroll_direction == "right":
                        self._mouse_manager.scroll(position_x, position_y, scroll_amount,
                                                   self._mouse_manager.wheel_right, mouse_dict["features"]["delays_ms"])

                elif mouse_type == "hold":
                    self._mouse_manager.hold(position_x, position_y)

                elif mouse_type == "release":

                    try:
                        release_direction = mouse_dict["features"]["direction"]
                        release_pixels = mouse_dict["features"]["pixels"]

                        x1 = position_x
                        y1 = position_y

                        if release_direction == "down":
                            x2 = x1
                            y2 = position_y + release_pixels
                        elif release_direction == "up":
                            x2 = x1
                            y2 = position_y - release_pixels
                        elif release_direction == "left":
                            x2 = position_x - release_pixels
                            y2 = y1
                        elif release_direction == "right":
                            x2 = position_x + release_pixels
                            y2 = y1
                        self._mouse_manager.drag(x1, y1, x2, y2, self._mouse_manager.left_button)
                    except:
                        self._mouse_manager.release(position_x, position_y)

            keyboard_dict = component.keyboard

            keyboard_string = keyboard_dict["string"]

            #try to decrypt all line
            if self._crypto_manager.get_key() is not None and self._crypto_manager.get_iv() is not None:
                try:
                    unenc_string = base64.b64decode(keyboard_string)
                    decrypted_str = self._crypto_manager.decrypt(keyboard_string)
                    if decrypted_str != "": #wrong password
                        keyboard_string = decrypted_str
                except: #string is not base 64
                    pass

            if keyboard_string != "":
                time.sleep(0.2)
                keyboard_duration = keyboard_dict["durations_ms"]
                keyboard_delay = keyboard_dict["delays_ms"]

                keyboard_string = self._arguments_manager.get_string(keyboard_string,self._arguments,
                                                self._performances, self._maps, self._crypto_manager)

                self._keyboard_manager.send(keyboard_string, False, keyboard_delay, keyboard_duration)



    def worker(self, current_color_screen, scaling_factor):
        current_gray_screen = cv2.cvtColor(current_color_screen, cv2.COLOR_BGR2GRAY)

        return_group_0 = []
        return_group_1 = []
        return_group_2 = []
        mains_found = []

        tmp_text_scraped = ""
        tmp_text_extracted = ""

        arr_scraped_txt = copy.deepcopy(self._arr_scraped_txt)
        arr_extracted_txt = copy.deepcopy(self._arr_extracted_txt)

        self.lock.acquire()
        break_flag = common.break_flag
        stop_flag = common.stop_flag
        section_name = self.section_name
        self.lock.release()

        if break_flag is True and section_name != "fail" and section_name != "exit":
            return

        if stop_flag is True:
            return

        for cnt_g in range(3):

            self.lock.acquire()
            break_flag = common.break_flag
            stop_flag = common.stop_flag
            section_name = self.section_name
            self.lock.release()

            if break_flag is True and section_name != "fail" and section_name != "exit":
                return

            if stop_flag is True:
                return


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

            for main in mains_found:
                main.index_in_tree = box["index_in_tree"]
                main.index_in_group = box["index_in_group"]
                main.mouse = box["mouse"]
                main.keyboard = box["keyboard"]
                main.group = box["group"]
                main.is_main = box["is_main"]


            sub_boxes = []
            if cnt_g == 0:
                sub_boxes = self._group_0[1:]
            elif cnt_g == 1:
                sub_boxes = self._group_1[1:]
            elif cnt_g == 2:
                sub_boxes = self._group_2[1:]

            if len(mains_found) > 0:
                for main_found in mains_found:
                    self.lock.acquire()
                    break_flag = common.break_flag
                    stop_flag = common.stop_flag
                    section_name = self.section_name
                    self.lock.release()

                    if break_flag is True and section_name != "fail" and section_name != "exit":
                        return

                    if stop_flag is True:
                        return

                    sub_results = []

                    main_and_subs = (main_found, []) #0-> main, 1-> subs, 2-> records

                    subs_found = 0
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

                            sub_results = im.find(box["features"]["I"])

                        elif box['type'] == 'R':
                            rm = RectangleManager()

                            rm.set_color_screen(current_color_screen)
                            rm.set_gray_screen(current_gray_screen)
                            rm.set_scaling_factor(scaling_factor)

                            sub_results = rm.find(box["features"]["R"], roi=roi)

                        elif box['type'] == 'T':
                            tm = TextManager(cipher_key=self._crypto_manager.get_key(),
                                             cipher_iv=self._crypto_manager.get_iv())

                            tm.set_color_screen(current_color_screen)
                            tm.set_gray_screen(current_gray_screen)
                            tm.set_scaling_factor(scaling_factor)

                            if box["features"]["T"]["type"] == "detect":

                                if box["features"]["T"]["detection"] == "date":
                                    logic = "date_" + box["features"]["T"]["logic"]

                                    sub_results = tm.scrape(roi=roi, logic=logic)
                                    scraped_text = sub_results[0].scraped_text
                                    tmp_text_scraped += scraped_text + ","

                                    scraped_text = sub_results[0].scraped_text

                                    scraper_dict = [s for s in arr_scraped_txt if s["group"] == box["group"] and s["index_in_group"] == box["index_in_group"]][0]
                                    scraper_dict["text"] = scraper_dict["text"] + scraped_text + ","

                                    if sub_results[0].extract_text is None:
                                        sub_results = []
                                        tmp_text_extracted += "" + ","
                                    else:
                                        extract_text = sub_results[0].extract_text
                                        tmp_text_extracted += extract_text + ","

                                        extracted_dict = [s for s in arr_extracted_txt if s["group"] == box["group"] and s["index_in_group"] == box["index_in_group"]][0]

                                        if extracted_dict["text"] == "":
                                            extracted_dict["text"] = extracted_dict["text"] + extract_text + ","

                                elif box["features"]["T"]["detection"] == "number":
                                    logic = "number_" + box["features"]["T"]["logic"]

                                    sub_results = tm.scrape(roi=roi, logic=logic)
                                    scraped_text = sub_results[0].scraped_text

                                    scraped_text = sub_results[0].scraped_text
                                    scraper_dict = [s for s in arr_scraped_txt if s["group"] == box["group"] and s["index_in_group"] == box["index_in_group"]][0]
                                    scraper_dict["text"] = scraper_dict["text"] + scraped_text + ","

                                    tmp_text_scraped += scraped_text + ","

                                    if sub_results[0].extract_text is None:
                                        sub_results = []
                                        tmp_text_extracted += "" + ","
                                    else:
                                        extract_text = sub_results[0].extract_text
                                        tmp_text_extracted += extract_text + ","

                                        extracted_dict = [s for s in arr_extracted_txt if s["group"] == box["group"] and s["index_in_group"] == box["index_in_group"]][0]

                                        if extracted_dict["text"] == "":
                                            extracted_dict["text"] = extracted_dict["text"] + extract_text + ","

                                else:
                                    tm.set_regexp(box["features"]["T"]["regexp"], self._arguments, maps=self._maps,
                                                  performances=self._performances)
                                    sub_results = tm.find(box["features"]["T"], roi=roi)

                                    scraped_text = sub_results[0].scraped_text
                                    scraper_dict = [s for s in arr_scraped_txt if s["group"] == box["group"] and s["index_in_group"] == box["index_in_group"]][0]
                                    scraper_dict["text"] = scraper_dict["text"] + scraped_text + ","

                                    tmp_text_scraped += scraped_text + ","

                                    if sub_results[0].extract_text is None:
                                        sub_results = []
                                        tmp_text_extracted += "" + ","
                                    else:
                                        extract_text = sub_results[0].extract_text
                                        tmp_text_extracted += extract_text + ","

                                        extracted_dict = [s for s in arr_extracted_txt if s["group"] == box["group"] and s["index_in_group"] == box["index_in_group"]][0]

                                        if extracted_dict["text"] == "":
                                            extracted_dict["text"] = extracted_dict["text"] + extract_text + ","

                            elif box["features"]["T"]["type"] == "map":

                                map_name = box["features"]["T"]["map"]

                                if map_name != "None":

                                    map_dict = self._maps[map_name]
                                    sub_results = tm.scrape(roi=roi, map_dict=map_dict)
                                    scraped_text = sub_results[0].scraped_text

                                    scraper_dict = [s for s in arr_scraped_txt if s["group"] == box["group"] and s["index_in_group"] == box["index_in_group"]][0]
                                    scraper_dict["text"] = scraper_dict["text"] + scraped_text + ","

                                    tmp_text_scraped += scraped_text + ","

                                    if sub_results[0].extract_text is None:
                                        sub_results = []
                                        tmp_text_extracted += "" + ","
                                    else:
                                        extract_text = sub_results[0].extract_text
                                        tmp_text_extracted += extract_text + ","

                                        extracted_dict = [s for s in arr_extracted_txt if s["group"] == box["group"] and s["index_in_group"] == box["index_in_group"]][0]

                                        if extracted_dict["text"] == "":
                                            extracted_dict["text"] = extracted_dict["text"] + extract_text + ","
                                else:
                                    sub_results = tm.scrape(roi=roi)
                                    scraped_text = sub_results[0].scraped_text
                                    tmp_text_scraped += scraped_text + ","
                                    tmp_text_extracted += scraped_text + ","

                                    scraper_dict = [s for s in arr_scraped_txt if s["group"] == box["group"] and s["index_in_group"] == box["index_in_group"]][0]
                                    scraper_dict["text"] = scraper_dict["text"] + scraped_text + ","

                                    extracted_dict = [s for s in arr_extracted_txt if s["group"] == box["group"] and s["index_in_group"] == box["index_in_group"]][0]
                                    extracted_dict["text"] = extracted_dict["text"] + scraped_text + ","



                        if len(sub_results) > 0:
                            sub_results[0].index_in_tree = box["index_in_tree"]
                            sub_results[0].index_in_group = box["index_in_group"]
                            sub_results[0].mouse = box["mouse"]
                            sub_results[0].keyboard = box["keyboard"]
                            sub_results[0].group = box["group"]
                            sub_results[0].is_main = box["is_main"]
                            sub_results[0].roi = roi

                            subs_found += 1

                            main_and_subs[1].append(sub_results[0])

                    if cnt_g == 0:
                        return_group_0.append(main_and_subs)
                    elif cnt_g == 1:
                        return_group_1.append(main_and_subs)
                    elif cnt_g == 2:
                        return_group_2.append(main_and_subs)

                    """
                    if len(subs_found) == len(sub_boxes):
                        a = "a"
                        break
                    """
            tmp_text_scraped = tmp_text_scraped[:-1]
            tmp_text_extracted = tmp_text_extracted[:-1]
            tmp_text_scraped += ";"
            tmp_text_extracted += ";"



        self.lock.acquire()

        #don't corrupt object if threads are running
        if self.stop_threads is False:
            self._components_found = []
            self._components_found.extend(return_group_0)
            self._components_found.extend(return_group_1)
            self._components_found.extend(return_group_2)


        len_g0_found_ok = False
        len_g1_found_ok = False
        len_g2_found_ok = False

        if len(self._group_0) == 0:
            len_g0_found_ok = True

        if len(self._group_1) == 0:
            len_g1_found_ok = True

        if len(self._group_2) == 0:
            len_g2_found_ok = True

        for main_subs_group_0 in return_group_0:

            subs_group_0 = main_subs_group_0[1]

            if 1 + len(subs_group_0) == len(self._group_0):
                len_g0_found_ok = True
                self._g0_found = True
                break

        for main_subs_group_1 in return_group_1:

            subs_group_1 = main_subs_group_1[1]

            if 1 + len(subs_group_1) == len(self._group_1):
                len_g1_found_ok = True
                self._g1_found = True
                break

        for main_subs_group_2 in return_group_2:

            subs_group_2 = main_subs_group_2[1]

            if 1 + len(subs_group_2) == len(self._group_2):
                len_g2_found_ok = True
                self._g2_found = True
                break

        if self._disappear_mode is False and self.stop_threads is False and\
                (len_g0_found_ok is True and len_g1_found_ok is True and len_g2_found_ok is True):

            self.stop_threads = True

            self._components_appeared = []

            self._components_appeared.append(main_subs_group_0[0])
            self._components_appeared.extend(subs_group_0)

            if len(self._group_1) != 0:
                self._components_appeared.append(main_subs_group_1[0])
                self._components_appeared.extend(subs_group_1)

            if len(self._group_2) != 0:
                self._components_appeared.append(main_subs_group_2[0])
                self._components_appeared.extend(subs_group_2)

            #self._components_appeared = copy.deepcopy(self._components_found)

            self._components_disappeared = []

            self._components_disappeared.append(main_subs_group_0)
            self._components_disappeared.extend(subs_group_0)

            if len(self._group_1) != 0:
                self._components_disappeared.append(main_subs_group_1)
                self._components_disappeared.extend(subs_group_1)

            if len(self._group_2) != 0:
                self._components_disappeared.append(main_subs_group_2)
                self._components_disappeared.extend(subs_group_2)

            #self._components_disappeared = copy.deepcopy(self._components_found)

            self._objects_appeared = True
            self._objects_disappeared = False

            self._last_screen = current_color_screen

            scraped_text = ""
            extract_text = ""
            check = "true"
            """
            try:
                for component in self._components_appeared:
                    if component.type == "T":

                        scraped_text += component.scraped_text + ","

                        if component.extract_text is None:
                            extract_text += ","
                        else:
                            extract_text += component.extract_text + ","
                        #check = 1
            except:
                pass
            """

            if self._cnt_text_components > 0:

                for scraped_element in arr_scraped_txt:
                    scraped_text += scraped_element["text"][:-1] + ";"

                for extracted_element in arr_extracted_txt:
                    extract_text += extracted_element["text"][:-1] + ";"

                if scraped_text != "":
                    scraped_text = scraped_text[:-1]

                if extract_text != "":
                    extract_text = extract_text[:-1]

            self._result.records["text"] = scraped_text
            self._result.records["extract"] = extract_text
            self._result.records["check"] = check

        elif self._disappear_mode is True and self.stop_threads is False and\
                (len_g0_found_ok is False or len_g1_found_ok is False or len_g2_found_ok is False):

            self._objects_disappeared = True
            self.stop_threads = True

        elif self.stop_threads is False: #timedout

            #self._tmp_text_scraped = tmp_text_scraped
            #self._tmp_text_extracted = tmp_text_extracted

            extract_text = ""
            scraped_text = ""

            if self._cnt_text_components > 0:

                for scraped_element in arr_scraped_txt:
                    scraped_text += scraped_element["text"][:-1] + ";"

                for extracted_element in arr_extracted_txt:
                    extract_text += extracted_element["text"][:-1] + ";"

                if scraped_text != "":
                    scraped_text = scraped_text[:-1]

                if extract_text != "":
                    extract_text = extract_text[:-1]

            self._tmp_text_scraped = scraped_text
            self._tmp_text_extracted = extract_text

        self.total_threads -= 1
        self._first_attempt_finished = True
        self.lock.release()

    def _get_annotation_screen(self, index=None):

        class DummyResult:
            def __init__(self):
                self.x = None
                self.y = None
                self.w = None
                self.h = None
                self.type = None
                self.scraped_text = None
                self.group = 0
                self.is_main = False
                self.index_in_tree = 0
                self.index_in_group = 0
                self.mouse = {}
                self.keyboard = {}
                self.roi = Roi()
                self.is_found = False

        if index is not None:
            last_screen = self._uncompress(self._screens[index][0])
        else:
            last_screen = self._uncompress(self._screens[-1][0])

        source_img_h, source_img_w, _ = last_screen.shape

        overlay = last_screen.copy()
        image = last_screen

        self.lock.acquire()
        components_found = copy.deepcopy(self._components_found)
        self.lock.release()


        #print("comp found:" + str(len(self._components_found)))
        #for component in components_found:
        m0_found = False
        m1_found = False
        m2_found = False

        has_to_find_m0 = False
        has_to_find_m1 = False
        has_to_find_m2 = False


        m0_xy = None
        m1_xy = None
        m2_xy = None

        mains_and_subs = []

        for box in self._object_definition['boxes']:

            if box["is_main"] is True:

                if box["group"] == 0:
                    has_to_find_m0 = True
                elif box["group"] == 1:
                    has_to_find_m1 = True
                elif box["group"] == 2:
                    has_to_find_m2 = True

        if self._objects_appeared:
            for component in self._components_appeared:
                if component.is_main is True:
                    mains_and_subs.append((component,[]))


            for main_and_sub in mains_and_subs:

                main = main_and_sub[0]

                for component in self._components_appeared:
                    if component.group == main.group and component.is_main is False:
                        main_and_sub[1].append(component)



        elif self._disappear_mode is False and self._timedout is True:
            for component in self._components_found:
                mains_and_subs.append(component)


            tmp_main_and_subs = []

            for main_and_sub in mains_and_subs:

                main = main_and_sub[0]
                add_tmp_main_and_subs = True
                subs = []

                for sub_def in self._object_definition['boxes']:

                    if sub_def["group"] == main.group and sub_def["is_main"] is False:

                        sub_found = False

                        for sub_in_comp_found in main_and_sub[1]:
                            if sub_in_comp_found.index_in_tree == sub_def["index_in_tree"]:
                                sub_found = True
                                subs.append(sub_in_comp_found)
                                break

                        if sub_found is False:

                            if sub_def["group"] == 0 and self._g0_found is True:
                                add_tmp_main_and_subs = False

                            if sub_def["group"] == 1 and self._g1_found is True:
                                add_tmp_main_and_subs = False

                            if sub_def["group"] == 2 and self._g2_found is True:
                                add_tmp_main_and_subs = False

                            dummy_sub = DummyResult()
                            dummy_sub.type = sub_def["type"]
                            dummy_sub.group = sub_def["group"]
                            dummy_sub.index_in_tree = sub_def["index_in_tree"]
                            dummy_sub.index_in_group = sub_def["index_in_group"]
                            dummy_sub.is_main = False
                            dummy_sub.roi.x = main.x + sub_def["roi_x"]
                            dummy_sub.roi.y = main.y + sub_def["roi_y"]
                            dummy_sub.roi.h = sub_def["roi_h"]
                            dummy_sub.roi.w = sub_def["roi_w"]
                            dummy_sub.roi.unlimited_left = sub_def["roi_unlimited_left"]
                            dummy_sub.roi.unlimited_right = sub_def["roi_unlimited_right"]
                            dummy_sub.roi.unlimited_up = sub_def["roi_unlimited_up"]
                            dummy_sub.roi.unlimited_down = sub_def["roi_unlimited_down"]
                            subs.append(dummy_sub)
                if add_tmp_main_and_subs:
                    tmp_main_and_subs.append((main, subs))

            mains_and_subs = tmp_main_and_subs

        elif self._disappear_mode is False and self._objects_appeared is False:
            pass

        for main_and_sub in mains_and_subs:

            component = main_and_sub[0]

            if component.group == 0:
                m0_found = True

            if component.group == 1:
                m1_found = True

            if component.group == 2:
                m2_found = True

            m_xy = (component.x, component.y)

            x1 = component.x
            y1 = component.y
            x2 = component.x + component.w
            y2 = component.y + component.h

            if component.group == 0:
                color_stroke = (0, 0, 255)
                color_fill = (255, 0, 255)
            elif component.group == 1:
                color_stroke = (0, 149, 0)
                color_fill = (0, 188, 0)
            elif component.group == 2:
                color_stroke = (255, 0, 0)
                color_fill = (255, 114, 0)

            cv2.rectangle(overlay, (x1, y1), (x2, y2), color_fill, -1)

            alpha = 0.5
            cv2.addWeighted(overlay[y1:y2, x1:x2], alpha, image[y1:y2, x1:x2], 1 - alpha,
                            0, image[y1:y2, x1:x2])

            cv2.rectangle(image, (x1, y1), (x2, y2), color_stroke, 1)

            if (self._disappear_mode is True and self._timedout is False) or (self._disappear_mode is False):

                text = "M_" + str(component.group + 1)
                cv2.putText(image, text, (x2 + 1, y1 - 1), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color_stroke, 1,
                            lineType=cv2.LINE_AA)

                scraped_text = None

                try:
                    scraped_text = component.scraped_text
                except:
                    pass

                if self._disappear_mode is False: #and scraped_text is None:

                    mouse_dict = component.mouse

                    if mouse_dict["type"] is not None and self._objects_appeared is True:

                        point_dx = 0
                        point_dy = 0

                        try:
                            if (mouse_dict["features"]["point"]["dx"] != 0 or
                                    mouse_dict["features"]["point"]["dy"] != 0):
                                point_dx = mouse_dict["features"]["point"]["dx"]
                                point_dy = mouse_dict["features"]["point"]["dy"]
                        except:
                            pass

                        position_x = int(component.x + (component.w / 2))
                        position_y = int(component.y + (component.h / 2))

                        if point_dx != 0 or point_dy != 0:
                            new_position_x = component.x + point_dx
                            new_position_y = component.y + point_dy

                            cv2.line(image, (position_x, position_y), (new_position_x, new_position_y),
                                     color_stroke,
                                     int(1 * self._scaling_factor), lineType=cv2.LINE_AA)
                        else:
                            new_position_x = position_x
                            new_position_y = position_y

                        cv2.circle(image, (new_position_x, new_position_y), int(4 * self._scaling_factor),
                                   color_stroke, -1,
                                   lineType=cv2.LINE_AA)
                            
            elif (self._disappear_mode is True and self._timedout is True):
                text = "M_" + str(component.group + 1) + "!"
                cv2.putText(image, text, (x2 + 1, y1 - 1), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color_stroke, 1,
                            lineType=cv2.LINE_AA)

                scale = 1  # this value can be from 0 to 1 (0,1] to change the size of the text relative to the image
                fontScale = min(component.w, component.h) / (25 / scale)

                text_box_size = cv2.getTextSize("!", cv2.FONT_HERSHEY_SIMPLEX, fontScale, 2)
                text_x = int(component.x + (component.w / 2)) - int(text_box_size[0][0] / 2)
                text_y = int(component.y + (component.h / 2)) + int(text_box_size[0][1] / 2)

                cv2.putText(image, "!", (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, fontScale, color_stroke, 2,
                            lineType=cv2.LINE_AA)


            for sub_component in main_and_sub[1]:
                sub_component_found = True

                try:
                    if sub_component.is_found is False:
                        sub_component_found = False
                except:
                    pass

                # object roi
                roi = sub_component.roi

                y1 = roi.y
                y2 = y1 + roi.h

                x1 = roi.x
                x2 = x1 + roi.w

                if roi.unlimited_up is True:
                    y1 = 0
                    y2 = roi.y + roi.h

                if roi.unlimited_down is True:
                    y2 = source_img_h

                if roi.unlimited_left is True:
                    x1 = 0
                    x2 = roi.x + roi.w

                if roi.unlimited_right is True:
                    x2 = source_img_w

                if y1 < 0:
                    y1 = 0
                elif y1 > source_img_h:
                    y1 = source_img_h

                if y2 < 0:
                    y2 = 0
                elif y2 > source_img_h:
                    y2 = source_img_h

                if x1 < 0:
                    x1 = 0
                elif x1 > source_img_w:
                    x1 = source_img_w

                if x2 < 0:
                    x2 = 0
                elif x2 > source_img_w:
                    x2 = source_img_w

                if sub_component_found is True:



                    cv2.rectangle(overlay, (x1, y1), (x2, y2), color_fill, -1)

                    alpha = 0.2
                    cv2.addWeighted(overlay[y1:y2, x1:x2], alpha, image[y1:y2, x1:x2], 1 - alpha,
                                    0, image[y1:y2, x1:x2])

                    cv2.rectangle(image, (x1, y1), (x2, y2), color_stroke, 1)

                    #object
                    x1 = sub_component.x
                    y1 = sub_component.y
                    x2 = sub_component.x + sub_component.w
                    y2 = sub_component.y + sub_component.h

                    cv2.rectangle(overlay, (x1, y1), (x2, y2), color_fill, -1)

                    alpha = 0.3
                    cv2.addWeighted(overlay[y1:y2, x1:x2], alpha, image[y1:y2, x1:x2], 1 - alpha,
                                    0, image[y1:y2, x1:x2])

                    cv2.rectangle(image, (x1, y1), (x2, y2), color_stroke, 1)

                    if (self._disappear_mode is True and self._timedout is False) or (self._disappear_mode is False):

                        text = "s_" + str(sub_component.group + 1) + "_" + str(sub_component.index_in_group)
                        cv2.putText(image, text, (x2 + 1, y1 - 1), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color_stroke, 1,
                                    lineType=cv2.LINE_AA)

                        scraped_text = None

                        try:
                            scraped_text = sub_component.scraped_text
                        except:
                            pass

                        if self._disappear_mode is False: #and scraped_text is None:

                            mouse_dict = sub_component.mouse

                            if mouse_dict["type"] is not None and self._objects_appeared is True:

                                point_dx = 0
                                point_dy = 0

                                try:
                                    if (mouse_dict["features"]["point"]["dx"] != 0 or
                                            mouse_dict["features"]["point"]["dy"] != 0):
                                        point_dx = mouse_dict["features"]["point"]["dx"]
                                        point_dy = mouse_dict["features"]["point"]["dy"]
                                except:
                                    pass

                                position_x = int(sub_component.x + (sub_component.w / 2))
                                position_y = int(sub_component.y + (sub_component.h / 2))

                                if point_dx != 0 or point_dy != 0:
                                    new_position_x = sub_component.x + point_dx
                                    new_position_y = sub_component.y + point_dy

                                    cv2.line(image, (position_x, position_y), (new_position_x, new_position_y),
                                             color_stroke,
                                             int(1 * self._scaling_factor), lineType=cv2.LINE_AA)
                                else:
                                    new_position_x = position_x
                                    new_position_y = position_y

                                cv2.circle(image, (new_position_x, new_position_y), int(4 * self._scaling_factor),
                                           color_stroke, -1,
                                           lineType=cv2.LINE_AA)

                    elif (self._disappear_mode is True and self._timedout is True):

                        text = "s_" + str(sub_component.group + 1) + "_" + str(sub_component.index_in_group) + "!"
                        cv2.putText(image, text, (x2 + 1, y1 - 1), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color_stroke, 1,
                                    lineType=cv2.LINE_AA)

                        scale = 1  # this value can be from 0 to 1 (0,1] to change the size of the text relative to the image
                        fontScale = min(sub_component.w, sub_component.h) / (25 / scale)

                        text_box_size = cv2.getTextSize("!", cv2.FONT_HERSHEY_SIMPLEX, fontScale, 2)
                        text_x = int(sub_component.x + (sub_component.w / 2)) - int(text_box_size[0][0] / 2)
                        text_y = int(sub_component.y + (sub_component.h / 2)) + int(text_box_size[0][1] / 2)

                        cv2.putText(image, "!", (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, fontScale, color_stroke, 2,
                                    lineType=cv2.LINE_AA)

                else:
                    cv2.rectangle(image, (x1, y1), (x2, y2), color_stroke, 1)

                    text = "s_" + str(sub_component.group + 1) + "_" + str(sub_component.index_in_group) + "!"
                    cv2.putText(image, text, (x2 + 1, y1 - 1), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color_stroke, 1,
                                lineType=cv2.LINE_AA)

                    scale = 1  # this value can be from 0 to 1 (0,1] to change the size of the text relative to the image
                    fontScale = min(roi.w, roi.h) / (25 / scale)

                    text_box_size = cv2.getTextSize("!", cv2.FONT_HERSHEY_SIMPLEX, fontScale, 2)
                    text_x = int(roi.x + (roi.w / 2)) - int(text_box_size[0][0] / 2)
                    text_y = int(roi.y + (roi.h / 2)) + int(text_box_size[0][1] / 2)

                    cv2.putText(image, "!", (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, fontScale, color_stroke, 2,
                                lineType=cv2.LINE_AA)


        main_notfound_banner_size = 0

        if m2_found is False and has_to_find_m2 is True:
            color_stroke = (255, 0, 0)

            text_box_size = cv2.getTextSize(" (M_3)", cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
            text_w = text_box_size[0][0]
            text_h = text_box_size[0][1]

            cv2.putText(image, " (M_3)", (image.shape[1] - text_w - 1, 2 + text_h), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                        color_stroke, 1,
                        lineType=cv2.LINE_AA)

            main_notfound_banner_size += text_box_size[0][0]

        if m1_found is False and has_to_find_m1 is True:
            color_stroke = (0, 149, 0)

            text_box_size = cv2.getTextSize(" (M_2)", cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
            text_w = text_box_size[0][0]
            text_h = text_box_size[0][1]

            cv2.putText(image, " (M_2)", (image.shape[1] - text_w - 1 - main_notfound_banner_size, 2 + text_h),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                        color_stroke, 1,
                        lineType=cv2.LINE_AA)

            main_notfound_banner_size += text_box_size[0][0]

        if m0_found is False and has_to_find_m0 is True:
            color_stroke = (0, 0, 255)

            text_box_size = cv2.getTextSize(" (M_1)", cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
            text_w = text_box_size[0][0]
            text_h = text_box_size[0][1]

            cv2.putText(image, " (M_1)", (image.shape[1] - text_w - 1 - main_notfound_banner_size, 2 + text_h),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                        color_stroke, 1,
                        lineType=cv2.LINE_AA)

            main_notfound_banner_size += text_box_size[0][0]
        return image

    def _get_output_json(self):
        pass

    def _insert_perf(self):
        for perf in self._performances:
            if perf.object_name == self._result.object_name:

                cur_series = {}
                cur_series["series_name"] = self._series_name
                cur_series["object_name"] = self._result.object_name
                cur_series["performance_name"] = self._performance_name
                cur_series["detection_type"] = self._result.detection_type
                cur_series["maps"] = self._map_names_map_keys
                cur_series["performance_ms"] = self._result.performance_ms
                cur_series["accuracy_ms"] = self._result.accuracy_ms
                cur_series["timestamp"] = self._result.timestamp
                cur_series["end_timestamp"] = self._result.end_timestamp
                cur_series["records"] = self._result.records
                cur_series["timeout"] = self._result.timeout
                cur_series["thresholds"] = self._result.thresholds
                cur_series["group"] = self._result.group
                cur_series["output"] = self._result.output
                cur_series["screenshot"] = self._result.screenshot
                cur_series["annotation"] = self._result.annotation
                cur_series["initialize_cnt"] = len(self._performances)

                cur_series["resolution"] = {
                    "width": self._res_w,
                    "height": self._res_h
                }

                cur_series["scaling_factor"] = int(self._scaling_factor * 100),


                cur_series["state"] = 2
                cur_series["exit"] = "fail"

                if self._result.performance_ms != -1:

                    self._result.state = 0
                    self._result.exit = "true"

                    cur_series["state"] = self._result.state
                    cur_series["exit"] = self._result.exit

                    try:
                        warning_ms = self._result.thresholds["warning_s"] * 1000

                        if self._result.performance_ms >= warning_ms:
                            self._result.state = 1
                            cur_series["state"] = self._result.state
                    except:
                        pass

                    try:
                        critical_ms = self._result.thresholds["critical_s"] * 1000

                        if self._result.performance_ms >= critical_ms:
                            self._result.state = 2
                            cur_series["state"] = self._result.state
                    except:
                        pass

                else:

                    if self._result.has_to_break is True:
                        self._result.state = 2
                        self._result.exit = "fail"

                        cur_series["state"] = self._result.state
                        cur_series["exit"] = self._result.exit

                    else:
                        self._result.state = 2
                        self._result.exit = "false"

                        cur_series["state"] = self._result.state
                        cur_series["exit"] = self._result.exit

                not_exec = False
                cnt = 0
                for series in perf.series:
                    if series["series_name"] == self._series_name and series["exit"] == "not_executed":

                        series["maps"]  = cur_series["maps"]
                        series["performance_ms"] = cur_series["performance_ms"]
                        series["accuracy_ms"] = cur_series["accuracy_ms"]
                        series["timestamp"] = cur_series["timestamp"]
                        series["end_timestamp"] = cur_series["end_timestamp"]
                        series["records"] = cur_series["records"]
                        series["timeout"] = cur_series["timeout"]
                        series["screenshot"] = cur_series["screenshot"]
                        series["annotation"] = cur_series["annotation"]
                        series["state"] = cur_series["state"]
                        series["output"] = cur_series["output"]
                        series["exit"]  = cur_series["exit"]
                        not_exec = True

                if not_exec is False:
                    perf.series.append(cur_series)







    def execute(self):

        self.lock.acquire()
        break_flag = common.break_flag
        stop_flag = common.stop_flag
        section_name = self.section_name
        self.lock.release()

        if break_flag is True and section_name != "fail" and section_name != "exit":
            return

        if stop_flag is True:
            return

        self._result.timestamp = time.time()

        while self.total_threads != 0:
            continue


        self._screens = []

        self._g0_found = False
        self._g1_found = False
        self._g2_found = False

        self._timedout = False

        self.stop_threads = False
        self._components_found = []
        self._components_appeared = []
        self._return_values = []

        self._objects_appeared = False
        self._objects_disappeared = False

        self._last_screen = None
        self._screen_with_objects = None
        self._annotation_screen = None

        self._appear_time = -1
        self._appear_accuracy = -1

        self._disappear_time = -1
        self._disappear_accuracy = -1


        self._disappear_mode = False


        #sm = ScreenManager()

        MAX_THREADS = 3 #3

        timeout = self._detection["timeout_s"]
        has_to_break = self._detection["break"]
        detection_type = self._detection["type"]
        self._result.timeout = timeout

        call = self._call


        add_t_call = False
        t_call = time.time()
        if call["type"] == "run":
            try:
                args = ""
                try:
                    args = call["features"]["arguments"]
                except:
                    pass

                args = self._arguments_manager.get_string(args, self._arguments,
                                                   self._performances, self._maps, self._crypto_manager)

                #args = args.replace("\\'", "<alyvix_escp_quote>")

                args = args.replace("'", "\"")

                #cnt_sq = args.count("'")

                """
                if (cnt_sq % 2) != 0:
                    print("Error on -a: odd single quotes!")
                    sys.exit(2)
                """

                double_quote_args = re.findall(r"\"[^\"]*\"", args, re.IGNORECASE | re.UNICODE)

                for dq_arg in double_quote_args:
                    args = args.replace(dq_arg, dq_arg.replace(" ", "<alyvix_repl_space>"))

                args = args.replace("\"", "")

                args = args.split(" ")

                for i, v in enumerate(args):
                    args[i] = args[i].replace("<alyvix_repl_space>", " ")

                exe = call["features"]["path"]

                if exe != "":

                    popen_input = []
                    popen_input.append(exe)

                    if len(args) == 1 and args[0] == '':
                        args = None

                    if args is not None:
                        popen_input.extend(args)
                    if self._verbose >= 1:
                        print(self._get_timestamp_formatted() + ": Alyvix calls " + exe)

                    proc = subprocess.Popen(popen_input)
                    add_t_call = True


            except:
                pass
        elif call["type"] == "kill":

            try:
                process_name = call["features"]["process"]

                if process_name != "":

                    logged_user = os.environ['userdomain'] + "\\" + os.environ.get("USERNAME")  # os.getlogin()

                    for proc in psutil.process_iter(attrs=['name', 'username']):
                        try:

                            if proc.name() == process_name and proc.username() == logged_user:
                                if self._verbose >= 1:
                                    print(self._get_timestamp_formatted() + ": Alyvix kills " + process_name)

                                p = psutil.Process(proc.pid)
                                p.kill()
                                add_t_call = True
                        except:
                            pass

            except:
                pass

        t_call = time.time() - t_call

        if self._library_manager.check_if_empty_from_string(self._object_json):
            self._screen_with_objects = self._screen_manager.grab_desktop(self._screen_manager.get_color_mat)

            self._annotation_screen = self._annotation_screen

            if add_t_call:
                self._result.performance_ms = t_call * 1000
            else:
                self._result.performance_ms = 0
            self._result.records["check"] = "true"
            self._result.accuracy_ms = 0
            self._result.screenshot = self._screen_with_objects
            self._result.annotation = self._annotation_screen
            self._result.end_timestamp = time.time()

            self._insert_perf()

            return self._result

        disappear_mode = False

        appear_time = 0
        appear_accuracy = 0

        disappear_time = 0
        disappear_accuracy = 0


        t_thread = time.time()

        self._t0 = time.time()

        self.total_threads = 0

        if self._verbose >= 1:

            print(self._get_timestamp_formatted() + ": Alyvix looks at " + self._performance_name)

        while True:

            self.lock.acquire()
            break_flag = common.break_flag
            stop_flag = common.stop_flag
            section_name = self.section_name
            self.lock.release()

            if break_flag is True and section_name != "fail" and section_name != "exit":
                return

            if stop_flag is True:
                return

            #t_before_grab = time.time()
            current_color_screen = self._screen_manager.grab_desktop(self._screen_manager.get_color_mat)

            t_after_grab = time.time()

            #self._screens.append((t_before_grab, self._compress(current_color_screen), t_after_grab))
            self._screens.append((self._compress(current_color_screen), t_after_grab))

            self.lock.acquire()
            components_appeared = self._components_appeared
            components_found = self._components_found
            stop_threads = self.stop_threads
            total_threads = self.total_threads
            self.lock.release()

            if self._objects_appeared is True and disappear_mode is False:

                if self._verbose >= 1:
                    print(self._get_timestamp_formatted() + ": Alyvix detected " + self._performance_name)

                if detection_type =='appear':
                    #cv2.imwrite("D:\\programdata\\log\\" + str(time.time()) + "_find.png", self._uncompress(self._screens[-2][0]))
                    self._appear_time, self._appear_accuracy, first_index_found = self._get_appear_time()

                    self._screen_with_objects = self._uncompress(self._screens[first_index_found][0])

                    self._annotation_screen = self._get_annotation_screen(first_index_found)

                    self._exec_interactions()

                    if add_t_call:
                        self._result.performance_ms = (self._appear_time+t_call) * 1000
                    else:
                        self._result.performance_ms = self._appear_time * 1000

                    #self._result.performance_ms = self._appear_time * 1000
                    self._result.accuracy_ms = self._appear_accuracy * 1000
                    self._result.screenshot = self._screen_with_objects
                    self._result.annotation = self._annotation_screen

                    if self._result.performance_ms < 0:
                        self._result.performance_ms *= -1

                    #self._result.timeout = timeout

                    self._result.end_timestamp = time.time()

                    self._insert_perf()

                    return self._result

                    #return (appear_time, appear_accuracy)
                else:

                    self.lock.acquire()

                    self.stop_threads = False
                    stop_threads = self.stop_threads

                    self._disappear_mode = True
                    disappear_mode = self._disappear_mode

                    self.lock.release()

                    self._appear_time, self._appear_accuracy, first_index_found = self._get_appear_time()
                    last_found_index = len(self._screens) -2

            elif self._objects_disappeared is True and disappear_mode is True:


                if detection_type == 'appear+disappear':
                    self._disappear_time, self._disappear_accuracy, first_index_not_found =\
                        self._get_disappear_time(first_index_found, appear_disappear=True)
                elif detection_type == 'disappear':
                    self._disappear_time, self._disappear_accuracy, first_index_not_found =\
                        self._get_disappear_time(first_index_found, appear_disappear=False)

                self._screen_with_objects = self._uncompress(self._screens[first_index_not_found][0])

                self._annotation_screen = self._get_annotation_screen(first_index_found)
                #self._annotation_screen  = self._get_annotation_screen(first_index_not_found)

                if add_t_call:
                    self._result.performance_ms = (self._disappear_time + t_call) * 1000
                else:
                    self._result.performance_ms = self._disappear_time * 1000

                #self._result.performance_ms = self._disappear_time * 1000
                self._result.accuracy_ms = self._disappear_accuracy * 1000
                self._result.screenshot = self._screen_with_objects
                self._result.annotation = self._annotation_screen

                if self._result.performance_ms < 0:
                    self._result.performance_ms *= -1

                #self._result.timeout = timeout

                self._result.end_timestamp = time.time()
                self._insert_perf()
                return self._result

            self.lock.acquire()
            first_attempt_finished = self._first_attempt_finished
            self.lock.release()

            if time.time() - self._t0 > timeout and first_attempt_finished is True:

                if self._verbose >= 1:
                    if has_to_break is True:
                        print(self._get_timestamp_formatted() + ": Alyvix failed at " + self._performance_name)
                    else:
                        print(self._get_timestamp_formatted() + ": Alyvix skipped " + self._performance_name)

                self._timedout = True

                self.lock.acquire()

                self.stop_threads = True
                self.lock.release()

                self._screen_with_objects = self._uncompress(self._screens[-1][0])
                self._annotation_screen = self._get_annotation_screen()

                self._result.records["text"] = self._tmp_text_scraped
                self._result.records["extract"] = self._tmp_text_extracted

                self._result.performance_ms = -1
                self._result.accuracy_ms = -1
                self._result.screenshot = self._screen_with_objects
                self._result.annotation = self._annotation_screen
                #self._result.timeout = timeout

                self._result.end_timestamp = time.time()
                self._insert_perf()
                return self._result


            if time.time() - t_thread > 0.5 and total_threads < MAX_THREADS and stop_threads is False:
                thread = threading.Thread(target=self.worker, args=(current_color_screen,self._scaling_factor))
                thread.start()
                t_thread = time.time()
                self.lock.acquire()
                self.total_threads += 1
                self.lock.release()

            time.sleep(0.01) #delay 10 ms

