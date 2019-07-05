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
import threading
import numpy as np
from alyvix.tools.screen import ScreenManager
from alyvix.tools.library import LibraryManager
from .image import ImageManager
from .rectangle import RectangleManager
from .text import TextManager
from alyvix.core.interaction.mouse import MouseManager
from alyvix.core.interaction.keyboard import KeyboardManager


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
        self.performance_ms = None
        self.accuracy_ms = None
        self.screenshot = None
        self.annotation = None
        self.timeout = None
        self.records = {"text":"", "image":""}


class EngineManager(object):

    def __init__(self, object_json, args=None, verbose=0):

        self._result = Result()

        self._result.object_name = list(object_json.keys())[0]

        self._verbose = verbose

        self._mouse_manager = MouseManager()
        self._keyboard_manager = KeyboardManager()

        self._library_manager = LibraryManager()

        self._screen_manager = ScreenManager()
        self._scaling_factor = self._screen_manager.get_scaling_factor()

        self._object_json = object_json
        self._object_definition = None
        self._detection = None

        self._object_definition = self._library_manager.build_objects_for_engine(self._object_json)
        self._detection = self._library_manager.get_detection_from_string(self._object_json)

        self._result.detection_type = self._detection["type"]
        self._result.has_to_break = self._detection["break"]

        np_screen_array = np.fromstring(base64.b64decode(self._object_definition["screen"]), np.uint8)

        self._screen = cv2.imdecode(np_screen_array, cv2.IMREAD_COLOR)

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

        self._arguments = args

        self.lock = threading.Lock()


    def _compress(self, current_color_screen):
        return cv2.imencode('.png', current_color_screen)[1]

    def _uncompress(self, compressed_img):
        return cv2.imdecode(compressed_img, cv2.IMREAD_COLOR)

    def _check_object_presence(self, color_screen):

        cnt_found = 0

        gray_screen = cv2.cvtColor(color_screen, cv2.COLOR_BGR2GRAY)

        for result_box in self._components_appeared:
            if result_box.type == "T" and result_box.scraped_text is not None:
                cnt_found += 1
                continue

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

        for component in self._components_found:

            if component.type == "T" and component.scraped_text is not None:
                continue

            mouse_dict = component.mouse

            if mouse_dict["type"] is None:
                continue

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

            if keyboard_string != "":
                time.sleep(0.2)
                keyboard_duration = keyboard_dict["durations_ms"]
                keyboard_delay = keyboard_dict["delays_ms"]

                #keyboard_string = "sadfasfdasf asfdf {arg1} dfdfdfd {arg2}"

                #args_in_string = re.findall("\\{arg[0-9]+\\}", keyboard_string,re.IGNORECASE)
                args_in_string = re.findall("\\{[0-9]+\\}", keyboard_string, re.IGNORECASE)

                for arg_pattern in args_in_string:

                    try:
                        i = int(arg_pattern.lower().replace("{","").replace("}",""))

                        keyboard_string = keyboard_string.replace(arg_pattern, self._arguments[i-1])
                    except:
                        pass #not enought arguments


                self._keyboard_manager.send(keyboard_string, False, keyboard_delay, keyboard_duration)



    def worker(self, current_color_screen, scaling_factor):
        current_gray_screen = cv2.cvtColor(current_color_screen, cv2.COLOR_BGR2GRAY)

        return_group_0 = []
        return_group_1 = []
        return_group_2 = []
        mains_found = []
        scraped_text = ""

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
                tm = TextManager()

                tm.set_color_screen(current_color_screen)
                tm.set_gray_screen(current_gray_screen)
                tm.set_scaling_factor(scaling_factor)

                tm.set_regexp(box["features"]["T"]["regexp"], self._arguments)

                mains_found = tm.find()

            for main in mains_found:
                main.index_in_tree = box["index_in_tree"]
                main.index_in_group = box["index_in_group"]
                main.mouse = box["mouse"]
                main.keyboard = box["keyboard"]
                main.group = box["group"]
                main.is_main = box["is_main"]

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
                    sub_results = []

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
                            tm = TextManager()

                            tm.set_color_screen(current_color_screen)
                            tm.set_gray_screen(current_gray_screen)
                            tm.set_scaling_factor(scaling_factor)

                            if box["features"]["T"]["type"] == "detection":
                                tm.set_regexp(box["features"]["T"]["regexp"], self._arguments)

                                sub_results = tm.find(box["features"]["T"], roi=roi)
                            elif box["features"]["T"]["type"] == "scraper":
                                sub_results = tm.scrape(roi=roi)
                                scraped_text += sub_results[0].scraped_text + " "

                        if len(sub_results) > 0:
                            sub_results[0].index_in_tree = box["index_in_tree"]
                            sub_results[0].index_in_group = box["index_in_group"]
                            sub_results[0].mouse = box["mouse"]
                            sub_results[0].keyboard = box["keyboard"]
                            sub_results[0].group = box["group"]
                            sub_results[0].is_main = box["is_main"]
                            sub_results[0].roi = roi

                            subs_found.append(sub_results[0])

                    if cnt_g == 0:
                        return_group_0.append(main_found)
                        return_group_0.extend(subs_found)
                    elif cnt_g == 1:
                        return_group_1.append(main_found)
                        return_group_1.extend(subs_found)
                    elif cnt_g == 2:
                        return_group_2.append(main_found)
                        return_group_2.extend(subs_found)

                    if len(subs_found) == len(sub_boxes):
                        break



        self.lock.acquire()

        #don't corrupt object if threads are running
        if self.stop_threads is False:
            self._components_found = []
            self._components_found.extend(return_group_0)
            self._components_found.extend(return_group_1)
            self._components_found.extend(return_group_2)

        if self._disappear_mode is False and self.stop_threads is False and (len(return_group_0) == len(self._group_0))\
                and (len(return_group_1) == len(self._group_1)) and (len(return_group_2) == len(self._group_2)):

            self.stop_threads = True

            self._components_appeared = []
            self._components_appeared = copy.deepcopy(self._components_found)

            self._components_disappeared = []
            self._components_disappeared = copy.deepcopy(self._components_found)

            self._last_screen = current_color_screen
            self._result.records["text"] = scraped_text

        elif self._disappear_mode is True and self.stop_threads is False and ((len(return_group_0) != len(self._group_0))\
            or (len(return_group_1) != len(self._group_1)) \
            or (len(return_group_2) != len(self._group_2))):

            self.stop_threads = True

        self.total_threads -= 1
        self.lock.release()

    def _get_annotation_screen(self, index=None):
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

        for box in self._object_definition['boxes']:

            if box["group"] == 0:
                has_to_find_m0 = True
            elif box["group"] == 1:
                has_to_find_m1 = True
            elif box["group"] == 2:
                has_to_find_m2 = True

            component_found = False

            if self._disappear_mode is True and len(self._components_appeared) > 0:
                for component in self._components_appeared:
                    if component.index_in_tree == box["index_in_tree"]:
                        component_found = True
                        break
            else:
                for component in self._components_found:
                    if component.index_in_tree == box["index_in_tree"]:
                        component_found = True
                        break

            if component_found is False:

                if box["is_main"] == True:
                    continue

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
                        self.roi = None

                component = DummyResult()
                component.type = box["type"]
                component.group = box["group"]
                component.index_in_tree = box["index_in_tree"]
                component.index_in_group = box["index_in_group"]
                component.is_main = False

                if component.group == 0 and m0_found == False and component.is_main == False:
                    continue
                elif component.group == 1 and m1_found == False and component.is_main == False:
                    continue
                elif component.group == 2 and m2_found == False and component.is_main == False:
                    continue

                if component.group == 0:
                    m_xy = m0_xy
                elif component.group == 1:
                    m_xy = m1_xy
                elif component.group == 2:
                    m_xy = m2_xy

                roi = Roi()
                roi.x = box["roi_x"] + m_xy[0]
                roi.y = box["roi_y"] + m_xy[1]
                roi.w = box["roi_w"]
                roi.h = box["roi_h"]
                roi.unlimited_left = box["roi_unlimited_left"]
                roi.unlimited_up = box["roi_unlimited_up"]
                roi.unlimited_right = box["roi_unlimited_right"]
                roi.unlimited_down = box["roi_unlimited_down"]

                component.roi = roi

            else:
                if component.group == 0 and component.is_main == True:
                    m0_found = True
                    m0_xy = (component.x, component.y)
                elif component.group == 1 and component.is_main == True:
                    m1_found = True
                    m1_xy = (component.x, component.y)
                elif component.group == 2 and component.is_main == True:
                    m2_found = True
                    m2_xy = (component.x, component.y)

            if component.group == 0:
                color_stroke = (0, 0, 255)
                color_fill = (255, 0, 255)
            elif component.group == 1:
                color_stroke = (0, 149, 0)
                color_fill = (0, 188, 0)
            elif component.group == 2:
                color_stroke = (255, 0, 0)
                color_fill = (255, 114, 0)

            # if timeout is true and main is found than we are in disappear mode
            if component.is_main:
                x1 = component.x
                y1 = component.y
                x2 = component.x + component.w
                y2 = component.y + component.h

                cv2.rectangle(overlay, (x1, y1), (x2, y2), color_fill, -1)

                alpha = 0.5
                cv2.addWeighted(overlay[y1:y2, x1:x2], alpha, image[y1:y2, x1:x2], 1 - alpha,
                                0, image[y1:y2, x1:x2])

                cv2.rectangle(image, (x1, y1), (x2, y2), color_stroke, 1)

                if (self._disappear_mode is True and self._timedout is False) or (self._disappear_mode is False):



                    text = "M_" + str(component.group + 1)
                    cv2.putText(image, text, (x2+1, y1 - 1), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color_stroke, 1,
                                lineType=cv2.LINE_AA)
                elif (self._disappear_mode is True and self._timedout is True):
                    text = "M_" + str(component.group + 1) + "!"
                    cv2.putText(image, text, (x2+1, y1 - 1), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color_stroke, 1,
                                lineType=cv2.LINE_AA)

                    scale = 1  # this value can be from 0 to 1 (0,1] to change the size of the text relative to the image
                    fontScale = min(component.w, component.h) / (25 / scale)

                    text_box_size = cv2.getTextSize("!", cv2.FONT_HERSHEY_SIMPLEX, fontScale, 2)
                    text_x = int(component.x + (component.w / 2)) - int(text_box_size[0][0] / 2)
                    text_y = int(component.y + (component.h / 2)) + int(text_box_size[0][1] / 2)

                    cv2.putText(image, "!", (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, fontScale, color_stroke, 2,
                                lineType=cv2.LINE_AA)
            else:

                roi = component.roi

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

                cv2.rectangle(overlay, (x1, y1), (x2, y2), color_fill, -1)

                alpha = 0.2
                cv2.addWeighted(overlay[y1:y2, x1:x2], alpha, image[y1:y2, x1:x2], 1 - alpha,
                                0, image[y1:y2, x1:x2])

                cv2.rectangle(image, (x1, y1), (x2, y2), color_stroke, 1)



                if component_found:

                    x1 = component.x
                    y1 = component.y
                    x2 = component.x + component.w
                    y2 = component.y + component.h

                    cv2.rectangle(overlay, (x1, y1), (x2, y2), color_fill, -1)



                    alpha = 0.3
                    cv2.addWeighted(overlay[y1:y2, x1:x2], alpha, image[y1:y2, x1:x2], 1 - alpha,
                                    0, image[y1:y2, x1:x2])

                    cv2.rectangle(image, (x1, y1), (x2, y2), color_stroke, 1)

                    if (self._disappear_mode is True and self._timedout is False) or (self._disappear_mode is False):

                        text = "s_" + str(component.group + 1) + "_" + str(component.index_in_group)
                        cv2.putText(image, text, (x2 + 1, y1 - 1), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color_stroke, 1,
                                    lineType=cv2.LINE_AA)
                    elif (self._disappear_mode is True and self._timedout is True):

                        text = "s_" + str(component.group + 1) + "_" + str(component.index_in_group) + "!"
                        cv2.putText(image, text, (x2 + 1, y1 - 1), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color_stroke, 1,
                                    lineType=cv2.LINE_AA)

                        scale = 1  # this value can be from 0 to 1 (0,1] to change the size of the text relative to the image
                        fontScale = min(component.w, component.h) / (25 / scale)

                        text_box_size = cv2.getTextSize("!", cv2.FONT_HERSHEY_SIMPLEX, fontScale, 2)
                        text_x = int(component.x + (component.w / 2)) - int(text_box_size[0][0] / 2)
                        text_y = int(component.y + (component.h / 2)) + int(text_box_size[0][1] / 2)

                        cv2.putText(image, "!", (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, fontScale, color_stroke, 2,
                                    lineType=cv2.LINE_AA)
                else:

                    text = "s_" + str(component.group + 1) + "_" + str(component.index_in_group) + "!"
                    cv2.putText(image, text, (x2 + 1, y1 - 1), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color_stroke, 1,
                                lineType=cv2.LINE_AA)

                    scale = 1  # this value can be from 0 to 1 (0,1] to change the size of the text relative to the image
                    fontScale = min(roi.w, roi.h) / (25 / scale)

                    text_box_size = cv2.getTextSize("!", cv2.FONT_HERSHEY_SIMPLEX, fontScale, 2)
                    text_x = int(roi.x + (roi.w / 2)) - int(text_box_size[0][0]/2)
                    text_y = int(roi.y + (roi.h / 2)) + int(text_box_size[0][1]/2)


                    cv2.putText(image, "!", (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, fontScale, color_stroke, 2,
                                lineType=cv2.LINE_AA)

            if component_found is False:
                continue

            if component.type == "T" and component.scraped_text is not None:
                continue

            mouse_dict = component.mouse

            if mouse_dict["type"] is not None and self._disappear_mode is False and \
                    len(self._components_found) == (len(self._group_0) + len(self._group_1) + len(self._group_2)):

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
                    new_position_x = component.x + point_dx
                    new_position_y = component.y + point_dy

                    cv2.line(image, (position_x, position_y), (new_position_x, new_position_y), color_stroke,
                             int(1*self._scaling_factor), lineType=cv2.LINE_AA)
                else:
                    new_position_x = position_x
                    new_position_y = position_y

                cv2.circle(image, (new_position_x, new_position_y), int(4*self._scaling_factor), color_stroke,-1,
                           lineType=cv2.LINE_AA)


        """
        text = "s_" + str(component.index_in_group)
        cv2.putText(image, text, (x1, y1 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color_fill, 1,
                    lineType=cv2.LINE_AA)
        

        cv2.rectangle(image, (component.x, component.y), (component.x + component.w, component.y + component.h),
                      color_stroke, 1)
                      
                alpha = 0.7
                cv2.addWeighted(overlay, alpha, image, 1 - alpha,
                                0, image)
        """
        main_notfound_banner_size = 0

        if m2_found is False and has_to_find_m2 is True:

            color_stroke = (255, 0, 0)

            text_box_size = cv2.getTextSize(" (M_3)", cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
            text_w = text_box_size[0][0]
            text_h = text_box_size[0][1]

            cv2.putText(image, " (M_3)", (image.shape[1] - text_w - 1, 2 + text_h), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color_stroke, 1,
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

    def execute(self):

        self._result.timestamp = time.time()

        while self.total_threads != 0:
            continue


        self._screens = []

        self._timedout = False

        self._t0 = 0
        self.stop_threads = False
        self._components_found = []
        self._components_appeared = []
        self._return_values = []

        self._last_screen = None
        self._screen_with_objects = None
        self._annotation_screen = None

        self._appear_time = -1
        self._appear_accuracy = -1

        self._disappear_time = -1
        self._disappear_accuracy = -1


        self._disappear_mode = False

        if self._verbose >= 1:
            print("Alyvix looks for " + self._result.object_name)

        #sm = ScreenManager()

        MAX_THREADS = 3

        timeout = self._detection["timeout_s"]
        has_to_break = self._detection["break"]
        detection_type = self._detection["type"]

        disappear_mode = False

        appear_time = 0
        appear_accuracy = 0

        disappear_time = 0
        disappear_accuracy = 0

        t_thread = time.time()

        self._t0 = time.time()

        self.total_threads = 0


        while True:

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

            if len(components_appeared) == (len(self._group_0) + len(self._group_1) + len(self._group_2)) \
                    and disappear_mode is False:

                if self._verbose >= 1:
                    print("Alyvix detected " + self._result.object_name)

                if detection_type =='appear':
                    #cv2.imwrite("D:\\programdata\\log\\" + str(time.time()) + "_find.png", self._uncompress(self._screens[-2][0]))
                    self._appear_time, self._appear_accuracy, first_index_found = self._get_appear_time()

                    self._screen_with_objects = self._uncompress(self._screens[first_index_found][0])

                    self._annotation_screen = self._get_annotation_screen(first_index_found)

                    self._exec_interactions()

                    self._result.performance_ms = self._appear_time * 1000
                    self._result.accuracy_ms = self._appear_accuracy * 1000
                    self._result.screenshot = self._screen_with_objects
                    self._result.annotation = self._annotation_screen

                    if self._result.performance_ms < 0:
                        self._result.performance_ms *= -1

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

            elif len(components_found) != (len(self._group_0) + len(self._group_1) + len(self._group_2)) \
                    and disappear_mode is True:


                if detection_type == 'appear+disappear':
                    self._disappear_time, self._disappear_accuracy, first_index_not_found =\
                        self._get_disappear_time(first_index_found, appear_disappear=True)
                elif detection_type == 'disappear':
                    self._disappear_time, self._disappear_accuracy, first_index_not_found =\
                        self._get_disappear_time(first_index_found, appear_disappear=False)

                self._screen_with_objects = self._uncompress(self._screens[first_index_not_found][0])

                self._annotation_screen = self._get_annotation_screen(first_index_found)
                #self._annotation_screen  = self._get_annotation_screen(first_index_not_found)

                self._result.performance_ms = self._disappear_time * 1000
                self._result.accuracy_ms = self._disappear_accuracy * 1000
                self._result.screenshot = self._screen_with_objects
                self._result.annotation = self._annotation_screen

                if self._result.performance_ms < 0:
                    self._result.performance_ms *= -1

                return self._result

            if time.time() - self._t0 > timeout:

                self._timedout = True

                self.lock.acquire()

                self.stop_threads = True
                self.lock.release()

                self._screen_with_objects = self._uncompress(self._screens[-1][0])
                self._annotation_screen = self._get_annotation_screen()

                self._result.performance_ms = -1
                self._result.accuracy_ms = -1
                self._result.screenshot = self._screen_with_objects
                self._result.annotation = self._annotation_screen
                self._result.timeout = timeout

                return self._result


            if time.time() - t_thread > 0.5 and total_threads < MAX_THREADS and stop_threads is False:
                thread = threading.Thread(target=self.worker, args=(current_color_screen,self._scaling_factor))
                thread.start()
                t_thread = time.time()
                self.lock.acquire()
                self.total_threads += 1
                self.lock.release()

            time.sleep(0.01) #delay 10 ms

