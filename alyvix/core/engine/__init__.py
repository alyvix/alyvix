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
        self.main = None
        self.subs = []
        self.group = None
        self._scraped_text = None


class EngineManager(object):

    def __init__(self):

        self._mouse_manager = MouseManager()
        self._keyboard_manager = KeyboardManager()

        self._library_manager = LibraryManager()

        self._screen_manager = ScreenManager()
        self._scaling_factor = self._screen_manager.get_scaling_factor()

        self._object_json = None
        self._object_definition = None
        self._detection = None

        self._screen = None

        self._group_0 = []
        self._group_1 = []
        self._group_2 = []

        self._screens = []

        self._t0 = 0
        self.total_threads = 0
        self.stop_threads = False
        self._components_found = []
        self._components_to_return = []
        self._return_values = []

        self._last_screen = None
        self._screen_with_objects = None

        self._appear_time = -1
        self._appear_accuracy = -1

        self._disappear_time = -1
        self._disappear_accuracy = -1

        self._disappear_mode = False

        self._arguments = None

        self.lock = threading.Lock()


    def _compress(self, current_color_screen):
        return cv2.imencode('.png', current_color_screen)[1]

    def _uncompress(self, compressed_img):
        return cv2.imdecode(compressed_img, cv2.IMREAD_COLOR)

    def _check_object_presence(self, color_screen):

        cnt_found = 0

        gray_screen = cv2.cvtColor(color_screen, cv2.COLOR_BGR2GRAY)

        for result_box in self._components_found:
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

        if cnt_found == len(self._components_found):
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

        for i in range(last_found_index):
            if i > last_notfound_index:
                if self._check_object_presence(self._uncompress(self._screens[i][0])) is True:
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
                        
                        
                        ###########################################
                        APPEAR-DISAPPEAR
                        ###########################################
                        A = t2 + (t3 - t2)/2 +/- (t3 - t2)/2
                        D = t4 + (t5 - t4)/2 +/- (t5 - t4)/2
                        |   s   |   .   |   A   |   A   |   D   |
                        t0      t1      t2  *   t3      t4  *   t5
                                            |<------------->| THIS ONE!
                        ADp = t4 + (t5 - t4)/2 - t2 - (t3 - t2)/2
                        ADa = +/- ((t5 - t4)/2 + (t3 - t2)/2)
                        
                        
                        ###########################################
                        DISAPPEAR
                        ###########################################
                        s = t0 + (t1 - t0)/2 +/- (t1 - t0)/2
                        D = t4 + (t5 - t4)/2 +/- (t5 - t4)/2
                        |   s   |   .   |   A   |   A   |   D   |
                        t0  *   t1      t2      t3      t4  *   t5
                            |<----------------------------->| THIS ONE!
                        Dp = t4 + (t5 - t4)/2 - t0 - (t1 - t0)/2
                        Da = +/- ((t5 - t4)/2 + (t1 - t0)/2)
                    """
                    t0 = self._t0
                    t1 = self._screens[0][1]

                    tn = self._screens[i-1][1]
                    tn_1 = self._screens[i][1]


                    time = tn + ((tn_1-tn)/2) - t0 - ((t1 - t0)/2)
                    accuracy = ((tn_1 - tn)/2) +( (t1 - t0)/2)

                    return (time, accuracy, i)

    def _get_disappear_time(self, first_found_index, appear_disappear = False):

        #first found index need to calc A+D
        #last found index need to speedup loop

        frame_step = 10
        loop_step = round(float(len(self._screens)) / float(frame_step))
        loop_step = int(loop_step)

        if loop_step < 1:
            loop_step = 1

        #last_found_index = i
        last_found_index = 0
        last_notfound_index = len(self._screens) - 1

        for i in range(loop_step):

            if i == 0:
                continue

            index = (len(self._screens) - (frame_step * i))

            if self._check_object_presence(self._uncompress(self._screens[index][0])) is False:
                last_notfound_index = index
            else:
                last_found_index = index
                break

        for i in range(last_notfound_index):
            if i > last_found_index:
                if self._check_object_presence(self._uncompress(self._screens[i][0])) is False:
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
    
    
                        ###########################################
                        APPEAR-DISAPPEAR
                        ###########################################
                        A = t2 + (t3 - t2)/2 +/- (t3 - t2)/2
                        D = t4 + (t5 - t4)/2 +/- (t5 - t4)/2
                        |   s   |   .   |   A   |   A   |   D   |
                        t0      t1      t2  *   t3      t4  *   t5
                                            |<------------->| THIS ONE!
                        ADp = t4 + (t5 - t4)/2 - t2 - (t3 - t2)/2
                        ADa = +/- ((t5 - t4)/2 + (t3 - t2)/2)
    
    
                        ###########################################
                        DISAPPEAR
                        ###########################################
                        s = t0 + (t1 - t0)/2 +/- (t1 - t0)/2
                        D = t4 + (t5 - t4)/2 +/- (t5 - t4)/2
                        |   s   |   .   |   A   |   A   |   D   |
                        t0  *   t1      t2      t3      t4  *   t5
                            |<----------------------------->| THIS ONE!
                        Dp = t4 + (t5 - t4)/2 - t0 - (t1 - t0)/2
                        Da = +/- ((t5 - t4)/2 + (t1 - t0)/2)
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

                        time = tn + ((tn_1 - tn) / 2) - tn_a - ((tn_a_1 - tn_a) / 2)
                        accuracy = ((tn_1 - tn) / 2) + ((tn_a_1 - tn_a) / 2)
                    else:
                        # t4 + (t5 - t4)/2 - t0 - (t1 - t0)/2
                        time = tn + ((tn_1 - tn) / 2) - t0 - ((t1 - t0) / 2)
                        accuracy = ((tn_1 - tn) / 2) + ((t1 - t0) / 2)

                    return (time, accuracy)

    def _exec_interactions(self):

        for component in self._components_found:

            if component.type == "T" and component.scraped_text is not None:
                continue

            mouse_dict = component.mouse

            if mouse_dict["type"] is None:
                continue

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

            if mouse_type == "click":
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

            time.sleep(0.5)
            keyboard_dict = component.keyboard

            keyboard_string = keyboard_dict["string"]

            if keyboard_string != "":

                keyboard_duration = keyboard_dict["durations_ms"]
                keyboard_delay = keyboard_dict["delays_ms"]

                #keyboard_string = "sadfasfdasf asfdf {arg1} dfdfdfd {arg2}"

                args_in_string = re.findall("\\{arg[0-9]+\\}", keyboard_string,re.IGNORECASE)

                for arg_pattern in args_in_string:

                    try:
                        i = int(arg_pattern.lower().replace("{arg","").replace("}",""))

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

                        if len(sub_results) > 0:
                            sub_results[0].index_in_tree = box["index_in_tree"]
                            sub_results[0].index_in_group = box["index_in_group"]
                            sub_results[0].mouse = box["mouse"]
                            sub_results[0].keyboard = box["keyboard"]
                            sub_results[0].group = box["group"]

                            subs_found.append(sub_results[0])

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
        if self._disappear_mode is False and self.stop_threads is False and (len(return_group_0) == len(self._group_0))\
                and (len(return_group_1) == len(self._group_1)) and (len(return_group_2) == len(self._group_2)):

            self.stop_threads = True

            self._components_found = []
            self._components_found.extend(return_group_0)
            self._components_found.extend(return_group_1)
            self._components_found.extend(return_group_2)

            self._components_to_return = []
            self._components_to_return = copy.deepcopy(self._components_found)
            self._last_screen = current_color_screen

        elif self._disappear_mode is True and self.stop_threads is False and ((len(return_group_0) != len(self._group_0))\
            or (len(return_group_1) != len(self._group_1)) \
            or (len(return_group_2) != len(self._group_2))):

            self.stop_threads = True

            self._components_to_return = []
            self._components_to_return.extend(return_group_0)
            self._components_to_return.extend(return_group_1)
            self._components_to_return.extend(return_group_2)

        self.total_threads -= 1
        self.lock.release()

    def _get_annotation_screen(self):
        pass

    def _get_output_json(self):
        pass

    def execute(self, object_json, args=None):

        self._object_json = object_json
        self._object_definition = self._library_manager.build_objects_from_string(object_json)
        self._detection = self._library_manager.get_detection_from_string(object_json)

        np_screen_array = np.fromstring(base64.b64decode(self._object_definition["screen"]), np.uint8)

        self._screen = cv2.imdecode(np_screen_array, cv2.IMREAD_COLOR)

        self._arguments = args

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
        self._components_to_return = []
        self._return_values = []

        self._last_screen = None
        self._screen_with_objects = None

        self._appear_time = -1
        self._appear_accuracy = -1

        self._disappear_time = -1
        self._disappear_accuracy = -1


        self._disappear_mode = False

        print("start")

        #sm = ScreenManager()

        MAX_THREADS = 3

        timeout = 100 #self._detection["timeout_s"]
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
            result = self._components_to_return
            stop_threads = self.stop_threads
            total_threads = self.total_threads
            self.lock.release()

            if len(result) == (len(self._group_0) + len(self._group_1) + len(self._group_2)) \
                    and disappear_mode is False:
                if detection_type =='appear':
                    self._appear_time, self._appear_accuracy, first_index_found = self._get_appear_time()

                    self._screen_with_objects = self._uncompress(self._screens[first_index_found][0])

                    time.sleep(0.5)

                    self._exec_interactions()

                    return

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

            elif len(result) != (len(self._group_0) + len(self._group_1) + len(self._group_2)) \
                    and disappear_mode is True:

                if detection_type == 'appear+disappear':
                    self._disappear_time, self._disappear_accuracy =\
                        self._get_disappear_time(first_index_found, appear_disappear=True)
                elif detection_type == 'disappear':
                    self._disappear_time, self._disappear_accuracy =\
                        self._get_disappear_time(first_index_found, appear_disappear=False)

            if time.time() - self._t0 > timeout:
                if has_to_break:
                    raise Exception('timedout occurred')
                else:
                    return []


            if time.time() - t_thread > 0.5 and total_threads < MAX_THREADS and stop_threads is False:
                thread = threading.Thread(target=self.worker, args=(current_color_screen,self._scaling_factor))
                thread.start()
                t_thread = time.time()
                self.lock.acquire()
                self.total_threads += 1
                self.lock.release()

            time.sleep(0.1) #delay 100 ms

