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

import json
import base64
import cv2
import re
import numpy as np
import os
import sys
import copy

import math
from sys import platform as _platform


from alyvix.tools.screen import ScreenManager


class Box:
    def __init__(self):
        super(Box, self).__init__()

        self.x = 0;
        self.y = 0;
        self.w = 0;
        self.h = 0;
        self.roi_x = 0;
        self.roi_y = 0;
        self.roi_w = 0;
        self.roi_h = 0;
        self.roi_unlimited_left = False;
        self.roi_unlimited_up = False;
        self.roi_unlimited_right = False;
        self.roi_unlimited_down = False;
        self.group = 0;
        self.is_main = False;

        self.thumbnail = {};

        self.type = "I";

        self.features = {"I": {},
                         "R": {},
                         "T": {}};

        self.mouse = {"type": None, "features": {}};

        self.keyboard = {"string": "", "delays_ms": 100, "durations_ms": 100};


class LibraryManager:

    def __init__(self):
        super(LibraryManager, self).__init__()

        self.screen = None
        self.boxes = []
        self._json_object = None

    def get_correct_filename(self, filename):

        filename_path = os.path.dirname(filename)
        filename_no_path = os.path.basename(filename)

        if filename_no_path.count(".") == 1 and filename_no_path.find(".") == 0:
            filename_no_extension = ""
            file_extension = os.path.splitext(filename_no_path)[0]
        else:
            filename_no_extension = os.path.splitext(filename_no_path)[0]
            file_extension = os.path.splitext(filename_no_path)[1]

        if filename_path == '':
            filename_path = os.getcwd()
            filename = filename_path + os.sep + filename_no_path

        if file_extension != ".alyvix":
            filename = filename_path + os.sep + filename_no_extension + ".alyvix"

        if filename_no_extension == "":
            print("A file name can't be empty")
            sys.exit(2)

        return filename

    def get_invalid_filename_chars(self):
        if _platform == "linux" or _platform == "linux2":
            # linux...
            pass
        elif _platform == "darwin":
            # mac...
            pass
        elif _platform == "win32":
            # window...
            #\ / : * ? " > < |
            invalid_char = ["\"", "/", ":", "*", "?", "<", ">", "\\", "|"]

            return invalid_char

    def check_valid_object_name(self, name):

        invalid_chars = re.findall(r'[^a-zA-Z-_ 0-9]', name)

        if len(invalid_chars) > 0:
            return False
        else:
            return True


    def load_file(self, filename):

        try:
            with open(filename) as f:
                self._json_object = json.load(f)
        except:
            self._json_object = {}
    def get_json(self):
        return self._json_object

    def set_json(self, json_dict):
        self._json_object = json_dict

    def check_if_exist(self, object_name):

        if object_name is None:
            return

        sm = ScreenManager()
        w, h = sm.get_resolution()
        scaling_factor = sm.get_scaling_factor()


        try:
            detection_dict = self._json_object["objects"][object_name]["detection"]
        except:
            return False

        resolution_string = str(w) + "*" + str(h) + "@" + str(int(scaling_factor * 100))

        try:
            object_dict = self._json_object["objects"][object_name]["components"][resolution_string]
        except:
            return False

        return True

    def check_if_detection_exist(self, object_name):

        if object_name is None:
            return

        try:
            detection_dict = self._json_object["objects"][object_name]["detection"]
        except:
            return False

        return True

    def check_if_any_res_exists(self, object_name):
        try:
            object_dict = self._json_object["objects"][object_name]["components"]
            return True
        except:
            return False

    def get_detection(self, object_name):

        if object_name is None:
            return {}

        try:
            detection_dict = self._json_object["objects"][object_name]["detection"]
        except:
            return {}

        return detection_dict

    def get_measure(self, object_name):

        if object_name is None:
            return {}

        try:
            measure_dict = self._json_object["objects"][object_name]["measure"]
        except:
            return {}

        return measure_dict

    def get_timeout(self, object_name):

        if object_name is None:
            return {}

        try:
            timeout = self._json_object["objects"][object_name]["detection"]["timeout_s"]
        except:
            return 10

        if timeout is None or timeout == "":
            timeout = 10

        return timeout

    def measure_is_enable(self, object_name):

        if object_name is None:
            return {}

        try:
            output = self._json_object["objects"][object_name]["measure"]["output"]
        except:
            return False

        return output

    def break_is_enable(self, object_name):

        if object_name is None:
            return {}

        try:
            break_is_enable = self._json_object["objects"][object_name]["detection"]["break"]
        except:
            return False

        return break_is_enable

    def get_warning_thresholds(self, object_name):


        try:
            warning = self._json_object["objects"][object_name]["measure"]["thresholds"]["warning_s"]
        except:
            return None

        return warning


    def get_critical_thresholds(self, object_name):

        try:
            critical = self._json_object["objects"][object_name]["measure"]["thresholds"]["critical_s"]
        except:
            return None

        return critical

    def get_map(self):

        try:
            map_dict = self._json_object["maps"]
        except:
            return {}

        return map_dict

    def get_script(self):

        try:
            script_dict = self._json_object["script"]
        except:
            return {
                        "case": [

                        ],
                        "sections": {
                            "exit": [],
                            "fail": []
                        }
                    }

        return script_dict

    def get_call(self, object_name):

        if object_name is None:
            return {}

        try:
            call_dict = self._json_object["objects"][object_name]["call"]
        except:
            return {
                "features": {},
                "type": "run"
            }

        return call_dict

    def add_chunk(self, object_name, chunk):

        if object_name is None:
            return

        detection_dict = {}

        sm = ScreenManager()
        w, h = sm.get_resolution()
        scaling_factor = sm.get_scaling_factor()

        resolution_string = str(w) + "*" + str(h) + "@" + str(int(scaling_factor * 100))

        try:
            #detection_dict[object_name] = alyvix_json["objects"][object_name]
            detection_dict = {object_name: {"components": {resolution_string:self._json_object["objects"][object_name]
                                                            ["components"][resolution_string]},
                                            "date_modified": self._json_object["objects"][object_name]["date_modified"],
                                            "detection": self._json_object["objects"][object_name]["detection"],
                                            "measure": self._json_object["objects"][object_name]["measure"],
                                            "call": self._json_object["objects"][object_name]["call"]}}
        except:
            return {}

        detection_dict[object_name]["run"] = chunk

        return detection_dict

    def build_objects_for_ide(self, object_name, library=None, resolution=None):

        self.boxes = []

        if self._json_object is None and library is None:
            return

        if object_name is None:
            return

        sm = ScreenManager()
        w, h = sm.get_resolution()
        scaling_factor = sm.get_scaling_factor()

        try:
            if library is None:
                detection_dict = self._json_object["objects"][object_name]["detection"]
            else:
                detection_dict = library["objects"][object_name]["detection"]
        except:
            return {}

        try:
            if library is None:
                call_dict = self._json_object["objects"][object_name]["call"]
            else:
                call_dict = library["objects"][object_name]["call"]
        except:
            call_dict = {}


        try:
            if library is None:
                measure_dict = self._json_object["objects"][object_name]["measure"]
            else:
                measure_dict = library["objects"][object_name]["measure"]
        except:
            measure_dict = {}

        if resolution is None:
            resolution_string = str(w) + "*" + str(h) + "@" + str(int(scaling_factor * 100))
        else:
            resolution_string = resolution

        try:
            if library is None:
                object_dict = self._json_object["objects"][object_name]["components"][resolution_string]
            else:
                object_dict = library["objects"][object_name]["components"][resolution_string]
        except:
            return {}

        group = 0
        for group_dict in object_dict["groups"]:

            main_dict = group_dict["main"]

            if main_dict != {}:

                box = {}

                box["x"] = int((main_dict["visuals"]["roi"]["screen_x"] + main_dict["visuals"]["selection"]["roi_dx"])/scaling_factor)
                box["y"] = int((main_dict["visuals"]["roi"]["screen_y"] + main_dict["visuals"]["selection"]["roi_dy"])/scaling_factor)
                box["w"] = int(main_dict["visuals"]["selection"]["width"]/scaling_factor)
                box["h"] = int(main_dict["visuals"]["selection"]["height"]/scaling_factor)

                box["roi_x"] = int(main_dict["visuals"]["roi"]["screen_x"]/scaling_factor)
                box["roi_y"] = int(main_dict["visuals"]["roi"]["screen_y"]/scaling_factor)
                box["roi_w"] = int(main_dict["visuals"]["roi"]["width"]/scaling_factor)
                box["roi_h"] = int(main_dict["visuals"]["roi"]["height"]/scaling_factor)

                box["roi_unlimited_left"] = main_dict["visuals"]["roi"]["unlimited_left"]
                box["roi_unlimited_up"] = main_dict["visuals"]["roi"]["unlimited_up"]
                box["roi_unlimited_right"] = main_dict["visuals"]["roi"]["unlimited_right"]
                box["roi_unlimited_down"] = main_dict["visuals"]["roi"]["unlimited_down"]

                box["group"] = group

                box_type = main_dict["detection"]["type"][0].upper()

                box["features"] = {"I": {}, "R": {}, "T": {}}

                box["features"][box_type] = copy.deepcopy(main_dict["detection"]["features"])

                box["type"] = box_type

                if box["type"] == "R":
                    box["features"]["R"]["width"]["min"] = \
                        int(box["features"]["R"]["width"]["min"] / scaling_factor)

                    box["features"]["R"]["width"]["max"] = \
                        int(box["features"]["R"]["width"]["max"] / scaling_factor)

                    box["features"]["R"]["height"]["min"] =\
                        int(box["features"]["R"]["height"]["min"]/scaling_factor)

                    box["features"]["R"]["height"]["max"] =\
                        int(box["features"]["R"]["height"]["max"]/scaling_factor)

                mouse_dict = copy.deepcopy(main_dict["interactions"]["mouse"])

                if mouse_dict["features"] == None:
                    mouse_dict["features"] = {"point": {"dx": 0, "dy": 0}}

                if mouse_dict["type"] == "none":
                    mouse_dict["type"] = None

                try:
                    if (mouse_dict["features"]["point"]["dx"] != 0 or
                            mouse_dict["features"]["point"]["dy"] != 0):

                        dx =  int(mouse_dict["features"]["point"]["dx"]/scaling_factor) + box["x"]
                        dy = int(mouse_dict["features"]["point"]["dy"]/scaling_factor) + box["y"]

                        mouse_dict["features"]["point"] = \
                            {"dx": dx,
                             "dy": dy}

                        box_x_middle = box["x"] + int(box["w"]/2);
                        box_y_middle = box["y"] + int(box["h"]/2);

                        angle_radiants = math.atan2(dy - box_y_middle, dx - box_x_middle)
                        angle_degree = math.degrees(angle_radiants)
                        angle_degree = (angle_degree + 360) % 360
                        mouse_dict["features"]["point"]["angle"]  = angle_degree
                except:
                    pass

                box["mouse"] = mouse_dict

                box["keyboard"] = main_dict["interactions"]["keyboard"]

                box["is_main"] = True

                try: #for ide
                    box["rect_type"] = main_dict["rect_type"]
                except:
                    pass

                self.boxes.append(box)



            for box_dict in group_dict["subs"]:

                if box_dict != {}:

                    sub_dict = box_dict

                    box = {}  # Box()

                    box["w"] = int(sub_dict["visuals"]["selection"]["width"]/scaling_factor)
                    box["h"] = int(sub_dict["visuals"]["selection"]["height"]/scaling_factor)

                    box["roi_x"] = int((main_dict["visuals"]["roi"]["screen_x"] + \
                                   main_dict["visuals"]["selection"]["roi_dx"] + \
                                   sub_dict["visuals"]["roi"]["main_dx"])/scaling_factor)

                    box["roi_y"] = int((main_dict["visuals"]["roi"]["screen_y"] + \
                                   main_dict["visuals"]["selection"]["roi_dy"] + \
                                   sub_dict["visuals"]["roi"]["main_dy"])/scaling_factor)

                    box["x"] = box["roi_x"] + int(sub_dict["visuals"]["selection"]["roi_dx"]/scaling_factor)
                    box["y"] = box["roi_y"] + int(sub_dict["visuals"]["selection"]["roi_dy"]/scaling_factor)

                    box["roi_w"] = int(sub_dict["visuals"]["roi"]["width"]/scaling_factor)
                    box["roi_h"] = int(sub_dict["visuals"]["roi"]["height"]/scaling_factor)

                    box["roi_unlimited_left"] = sub_dict["visuals"]["roi"]["unlimited_left"]
                    box["roi_unlimited_up"] = sub_dict["visuals"]["roi"]["unlimited_up"]
                    box["roi_unlimited_right"] = sub_dict["visuals"]["roi"]["unlimited_right"]
                    box["roi_unlimited_down"] = sub_dict["visuals"]["roi"]["unlimited_down"]

                    box["group"] = group

                    box_type = sub_dict["detection"]["type"][0].upper()

                    box["features"] = {"I": {}, "R": {}, "T": {}}
                    box["features"][box_type] = copy.deepcopy(sub_dict["detection"]["features"])

                    box["type"] = box_type

                    if box["type"] == "R":
                        box["features"]["R"]["width"]["min"] = \
                            int(box["features"]["R"]["width"]["min"] / scaling_factor)

                        box["features"]["R"]["width"]["max"] = \
                            int(box["features"]["R"]["width"]["max"] / scaling_factor)

                        box["features"]["R"]["height"]["min"] = \
                            int(box["features"]["R"]["height"]["min"] / scaling_factor)

                        box["features"]["R"]["height"]["max"] = \
                            int(box["features"]["R"]["height"]["max"] / scaling_factor)

                    mouse_dict = copy.deepcopy(sub_dict["interactions"]["mouse"])

                    if mouse_dict["features"] == None:
                        mouse_dict["features"] = {"point": {"dx": 0, "dy": 0}}

                    if mouse_dict["type"] == "none":
                        mouse_dict["type"] = None

                    try:
                        if (mouse_dict["features"]["point"]["dx"] != 0 or
                                mouse_dict["features"]["point"]["dy"] != 0):

                            dx = int(mouse_dict["features"]["point"]["dx"] / scaling_factor) + box["x"]
                            dy = int(mouse_dict["features"]["point"]["dy"] / scaling_factor) + box["y"]

                            mouse_dict["features"]["point"] = \
                                {"dx": dx,
                                 "dy": dy}

                            box_x_middle = box["x"] + int(box["w"] / 2);
                            box_y_middle = box["y"] + int(box["h"] / 2);

                            angle_radiants = math.atan2(dy - box_y_middle, dx - box_x_middle)
                            angle_degree = math.degrees(angle_radiants)
                            angle_degree = (angle_degree + 360) % 360
                            mouse_dict["features"]["point"]["angle"] = angle_degree

                    except Exception as ex:
                        pass #print(ex)

                    box["mouse"] = mouse_dict

                    box["keyboard"] = sub_dict["interactions"]["keyboard"]

                    box["is_main"] = False

                    try:  # for ide
                        box["rect_type"] = sub_dict["rect_type"]
                    except:
                        pass

                    self.boxes.append(box)

            group += 1

        # except:
        #    return None

        aaa = "dasfdasf"

        numpy_image = None

        background_string = object_dict["screen"]
        # np_array = np.fromstring(base64.b64decode(background_string), np.uint8)
        # background_image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        return {"call":call_dict, "detection": detection_dict, "measure": measure_dict,
                "boxes": self.boxes, "screen": background_string, "scaling_factor": scaling_factor,
                "img_h": int(h/scaling_factor), "img_w": int(w/scaling_factor),
                "object_name": object_name}



    def get_detection_from_string(self, json_string):
        self.boxes = []

        object_name = list(json_string.keys())[0]

        sm = ScreenManager()
        w, h = sm.get_resolution()
        scaling_factor = sm.get_scaling_factor()

        alyvix_json = json_string

        try:
            detection_dict = alyvix_json[object_name]["detection"]
            return detection_dict
        except:
            return {}


    def get_call_from_string(self, json_string):

        object_name = list(json_string.keys())[0]
        alyvix_json = json_string

        try:
            detection_dict = alyvix_json[object_name]["call"]
            return detection_dict
        except:
            return {
                "features": {},
                "type": "run"
            }

    def check_if_empty_from_string(self, json_string):

        object_name = list(json_string.keys())[0]
        alyvix_json = json_string

        sm = ScreenManager()
        w, h = sm.get_resolution()
        scaling_factor = sm.get_scaling_factor()

        resolution_string = str(w) + "*" + str(h) + "@" + str(int(scaling_factor * 100))


        try:
            groups = alyvix_json[object_name]["components"][resolution_string]["groups"]

            cnt_main_empty = 0
            for group in groups:
                if bool(group["main"]) is False:
                    cnt_main_empty += 1

            if cnt_main_empty == 3:
                return True
            else:
                return False
        except:
            return True

    def build_objects_for_scraper(self, main, subs):
        ret_subs = []
        ret_main = None


        box = {}

        box["x"] = main["visuals"]["roi"]["screen_x"] + main["visuals"]["selection"]["roi_dx"]
        box["y"] = main["visuals"]["roi"]["screen_y"] + main["visuals"]["selection"]["roi_dy"]
        box["w"] = main["visuals"]["selection"]["width"]
        box["h"] = main["visuals"]["selection"]["height"]

        box["roi_x"] = main["visuals"]["roi"]["screen_x"]
        box["roi_y"] = main["visuals"]["roi"]["screen_y"]
        box["roi_w"] = main["visuals"]["roi"]["width"]
        box["roi_h"] = main["visuals"]["roi"]["height"]

        box["roi_unlimited_left"] = main["visuals"]["roi"]["unlimited_left"]
        box["roi_unlimited_up"] = main["visuals"]["roi"]["unlimited_up"]
        box["roi_unlimited_right"] = main["visuals"]["roi"]["unlimited_right"]
        box["roi_unlimited_down"] = main["visuals"]["roi"]["unlimited_down"]

        box["group"] = main["group"]

        box_type = main["detection"]["type"][0].upper()

        box["features"] = {"I": {}, "R": {}, "T": {}}

        box["features"][box_type] = main["detection"]["features"]

        box["type"] = box_type

        mouse_dict = main["interactions"]["mouse"]

        if mouse_dict["features"] == None:
            mouse_dict["features"] = {"point": {"dx": 0, "dy": 0}}

        if mouse_dict["type"] == "none":
            mouse_dict["type"] = None

        try:
            if (mouse_dict["features"]["point"]["dx"] != 0 or
                    mouse_dict["features"]["point"]["dy"] != 0):
                mouse_dict["features"]["point"] = \
                    {"dx": mouse_dict["features"]["point"]["dx"],
                     "dy": mouse_dict["features"]["point"]["dy"]}
        except:
            pass

        box["mouse"] = mouse_dict

        box["keyboard"] = main["interactions"]["keyboard"]

        box["is_main"] = True

        box["index_in_tree"] = 0


        box["index_in_group"] = 0

        ret_main = box

        cnt = 0
        for box_dict in subs:

            sub_dict = box_dict

            box = {}  # Box()

            box["w"] = main["visuals"]["selection"]["width"]
            box["h"] = main["visuals"]["selection"]["height"]

            box["roi_x"] = main["visuals"]["roi"]["screen_x"] + \
                           main["visuals"]["selection"]["roi_dx"] + \
                           sub_dict["visuals"]["roi"]["main_dx"]

            box["roi_y"] = main["visuals"]["roi"]["screen_y"] + \
                           main["visuals"]["selection"]["roi_dy"] + \
                           sub_dict["visuals"]["roi"]["main_dy"]

            box["x"] = box["roi_x"] + sub_dict["visuals"]["selection"]["roi_dx"]
            box["y"] = box["roi_y"] + sub_dict["visuals"]["selection"]["roi_dy"]

            box["roi_x"] = sub_dict["visuals"]["roi"]["main_dx"]

            box["roi_y"] = sub_dict["visuals"]["roi"]["main_dy"]

            box["roi_w"] = sub_dict["visuals"]["roi"]["width"]
            box["roi_h"] = sub_dict["visuals"]["roi"]["height"]

            box["roi_unlimited_left"] = sub_dict["visuals"]["roi"]["unlimited_left"]
            box["roi_unlimited_up"] = sub_dict["visuals"]["roi"]["unlimited_up"]
            box["roi_unlimited_right"] = sub_dict["visuals"]["roi"]["unlimited_right"]
            box["roi_unlimited_down"] = sub_dict["visuals"]["roi"]["unlimited_down"]

            box["group"] = box_dict["group"]

            box_type = sub_dict["detection"]["type"][0].upper()

            box["features"] = {"I": {}, "R": {}, "T": {}}
            box["features"][box_type] = sub_dict["detection"]["features"]

            box["type"] = box_type

            mouse_dict = sub_dict["interactions"]["mouse"]

            if mouse_dict["features"] == None:
                mouse_dict["features"] = {"point": {"dx": 0, "dy": 0}}

            if mouse_dict["type"] == "none":
                mouse_dict["type"] = None

            try:
                if (mouse_dict["features"]["point"]["dx"] != 0 or
                        mouse_dict["features"]["point"]["dy"] != 0):
                    mouse_dict["features"]["point"] = \
                        {"dx": mouse_dict["features"]["point"]["dx"],
                         "dy": mouse_dict["features"]["point"]["dy"]}
            except Exception as ex:
                pass  # print(ex)

            box["mouse"] = mouse_dict

            box["keyboard"] = sub_dict["interactions"]["keyboard"]

            box["is_main"] = False
            box["is_main"] = False

            box["index_in_tree"] = cnt+1
            box["index_in_group"] = cnt+1

            cnt+=1

            ret_subs.append(box)

        return (ret_main, ret_subs)

    def build_objects_for_engine(self, json_string):

        self.boxes = []

        object_name = list(json_string.keys())[0]

        sm = ScreenManager()
        w, h = sm.get_resolution()
        scaling_factor = sm.get_scaling_factor()

        try:
            detection_dict = json_string[object_name]["detection"]
        except:
            return {}

        resolution_string = str(w) + "*" + str(h) + "@" + str(int(scaling_factor * 100))

        try:
            object_dict = json_string[object_name]["components"][resolution_string]
        except:
            return {}

        run_dict = json_string[object_name]["run"]

        index_in_tree = 0
        group = 0
        for group_dict in object_dict["groups"]:

            main_dict = group_dict["main"]

            if main_dict != {}:

                box = {}

                box["x"] = main_dict["visuals"]["roi"]["screen_x"] + main_dict["visuals"]["selection"]["roi_dx"]
                box["y"] = main_dict["visuals"]["roi"]["screen_y"] + main_dict["visuals"]["selection"]["roi_dy"]
                box["w"] = main_dict["visuals"]["selection"]["width"]
                box["h"] = main_dict["visuals"]["selection"]["height"]

                box["roi_x"] = main_dict["visuals"]["roi"]["screen_x"]
                box["roi_y"] = main_dict["visuals"]["roi"]["screen_y"]
                box["roi_w"] = main_dict["visuals"]["roi"]["width"]
                box["roi_h"] = main_dict["visuals"]["roi"]["height"]

                box["roi_unlimited_left"] = main_dict["visuals"]["roi"]["unlimited_left"]
                box["roi_unlimited_up"] = main_dict["visuals"]["roi"]["unlimited_up"]
                box["roi_unlimited_right"] = main_dict["visuals"]["roi"]["unlimited_right"]
                box["roi_unlimited_down"] = main_dict["visuals"]["roi"]["unlimited_down"]

                box["group"] = group

                box_type = main_dict["detection"]["type"][0].upper()

                box["features"] = {"I": {}, "R": {}, "T": {}}

                box["features"][box_type] = main_dict["detection"]["features"]

                box["type"] = box_type

                mouse_dict = main_dict["interactions"]["mouse"]

                if mouse_dict["features"] == None:
                    mouse_dict["features"] = {"point": {"dx": 0, "dy": 0}}

                if mouse_dict["type"] == "none":
                    mouse_dict["type"] = None

                try:
                    if (mouse_dict["features"]["point"]["dx"] != 0 or
                            mouse_dict["features"]["point"]["dy"] != 0):
                        mouse_dict["features"]["point"] = \
                            {"dx": mouse_dict["features"]["point"]["dx"],
                             "dy": mouse_dict["features"]["point"]["dy"]}
                except:
                    pass

                box["mouse"] = mouse_dict

                box["keyboard"] = main_dict["interactions"]["keyboard"]

                box["is_main"] = True


                box["index_in_tree"] = index_in_tree
                index_in_tree += 1

                box["index_in_group"] = 0

                self.boxes.append(box)

            index_in_group = 1
            for box_dict in group_dict["subs"]:

                if box_dict != {}:

                    sub_dict = box_dict

                    box = {}  # Box()

                    box["w"] = sub_dict["visuals"]["selection"]["width"]
                    box["h"] = sub_dict["visuals"]["selection"]["height"]

                    box["roi_x"] = main_dict["visuals"]["roi"]["screen_x"] + \
                                   main_dict["visuals"]["selection"]["roi_dx"] + \
                                   sub_dict["visuals"]["roi"]["main_dx"]

                    box["roi_y"] = main_dict["visuals"]["roi"]["screen_y"] + \
                                   main_dict["visuals"]["selection"]["roi_dy"] + \
                                   sub_dict["visuals"]["roi"]["main_dy"]

                    box["x"] = box["roi_x"] + sub_dict["visuals"]["selection"]["roi_dx"]
                    box["y"] = box["roi_y"] + sub_dict["visuals"]["selection"]["roi_dy"]


                    box["roi_x"] = sub_dict["visuals"]["roi"]["main_dx"]

                    box["roi_y"] = sub_dict["visuals"]["roi"]["main_dy"]

                    box["roi_w"] = sub_dict["visuals"]["roi"]["width"]
                    box["roi_h"] = sub_dict["visuals"]["roi"]["height"]

                    box["roi_unlimited_left"] = sub_dict["visuals"]["roi"]["unlimited_left"]
                    box["roi_unlimited_up"] = sub_dict["visuals"]["roi"]["unlimited_up"]
                    box["roi_unlimited_right"] = sub_dict["visuals"]["roi"]["unlimited_right"]
                    box["roi_unlimited_down"] = sub_dict["visuals"]["roi"]["unlimited_down"]

                    box["group"] = group

                    box_type = sub_dict["detection"]["type"][0].upper()

                    box["features"] = {"I": {}, "R": {}, "T": {}}
                    box["features"][box_type] = sub_dict["detection"]["features"]

                    box["type"] = box_type

                    mouse_dict = sub_dict["interactions"]["mouse"]

                    if mouse_dict["features"] == None:
                        mouse_dict["features"] = {"point": {"dx": 0, "dy": 0}}

                    if mouse_dict["type"] == "none":
                        mouse_dict["type"] = None

                    try:
                        if (mouse_dict["features"]["point"]["dx"] != 0 or
                                mouse_dict["features"]["point"]["dy"] != 0):
                            mouse_dict["features"]["point"] = \
                                {"dx": mouse_dict["features"]["point"]["dx"],
                                 "dy": mouse_dict["features"]["point"]["dy"]}
                    except Exception as ex:
                        pass #print(ex)

                    box["mouse"] = mouse_dict

                    box["keyboard"] = sub_dict["interactions"]["keyboard"]

                    box["is_main"] = False
                    box["is_main"] = False

                    box["index_in_tree"] = index_in_tree
                    box["index_in_group"] = index_in_group

                    index_in_group += 1
                    index_in_tree += 1



                    self.boxes.append(box)

            group += 1

        # except:
        #    return None

        aaa = "dasfdasf"

        numpy_image = None

        background_string = object_dict["screen"]
        # np_array = np.fromstring(base64.b64decode(background_string), np.uint8)
        # background_image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        return {"detection": detection_dict, "boxes": self.boxes, "screen": background_string,
                "scaling_factor": scaling_factor, "img_h": h, "img_w": w, "object_name": object_name, "run": run_dict}

    def save_object(self):
        pass
