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
import numpy as np

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

    def load_file(self, filename):

        try:
            with open(filename) as f:
                self._json_object = json.load(f)
        except:
            self._json_object = {}
    def get_json(self):
        return self._json_object

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
                                            "date-modified": self._json_object["objects"][object_name]["date-modified"],
                                            "detection": self._json_object["objects"][object_name]["detection"]}}
        except:
            return {}

        detection_dict[object_name]["run"] = chunk

        return detection_dict

    def build_objects_for_ide(self, object_name):

        self.boxes = []

        if self._json_object is None:
            return

        if object_name is None:
            return

        sm = ScreenManager()
        w, h = sm.get_resolution()
        scaling_factor = sm.get_scaling_factor()

        try:
            detection_dict = self._json_object["objects"][object_name]["detection"]
        except:
            return {}

        resolution_string = str(w) + "*" + str(h) + "@" + str(int(scaling_factor * 100))

        try:
            object_dict = self._json_object["objects"][object_name]["components"][resolution_string]
        except:
            return {}

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
                            {"dx": mouse_dict["features"]["point"]["dx"] + box["x"],
                             "dy": mouse_dict["features"]["point"]["dy"] + box["y"]}
                except:
                    pass

                box["mouse"] = mouse_dict

                box["keyboard"] = main_dict["interactions"]["keyboard"]

                box["is_main"] = True

                self.boxes.append(box)

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
                                {"dx": mouse_dict["features"]["point"]["dx"] + box["x"],
                                 "dy": mouse_dict["features"]["point"]["dy"] + box["y"]}
                    except Exception as ex:
                        pass #print(ex)

                    box["mouse"] = mouse_dict

                    box["keyboard"] = sub_dict["interactions"]["keyboard"]

                    box["is_main"] = False

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
                "scaling_factor": scaling_factor, "img_h": int(h/scaling_factor), "img_w": int(w/scaling_factor), "object_name": object_name}



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
