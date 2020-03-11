import cv2
import json
import base64
import numpy as np
import copy
import time
import os
from collections import MutableMapping
from contextlib import suppress
from datetime import datetime
from alyvix.tools.screen import ScreenManager

class OutputManager:
    def __init__(self, verbose=0):
        self._verbose = verbose

    def set_verbose(self, verbose):
        self._verbose = verbose


    def _delete_keys_from_dict(self, dictionary, keys):
        for key in keys:
            with suppress(KeyError):
                del dictionary[key]
        for value in dictionary.values():
            if isinstance(value, MutableMapping):
                self._delete_keys_from_dict(value, keys)

    def _build_json(self, json_object, chunk, object_list, exit, duration):

        for object in json_object["objects"]:
            try:
                del json_object["objects"][object]["measure"]["series"]
            except:
                pass

        objects = []

        sm = ScreenManager()
        w, h = sm.get_resolution()
        scaling_factor = sm.get_scaling_factor()

        json_exit = False

        for object in object_list:



            resolution_string = str(w) + "*" + str(h) + "@" + str(int(scaling_factor * 100))

            # json_object["objects"][object.object_name] ["components"][resolution_string]
            object_dict = json_object["objects"][object.object_name]

            for measure in object.measures:
                del measure["name_for_screen"]

            object_dict["measure"]["series"] = object.measures


            json_object["objects"][object.object_name] = object_dict

        json_object["run"] = {"host": chunk["host"], "user": chunk["user"],
                              "test": chunk["test"], "code": chunk["code"],
                              "duration_s": round(duration,3),
                              "exit": exit}

        return json_object

    def save_screenshots(self, file_path, object_list, prefix=None):
        for object in object_list:

            object_name = object.object_name

            for measure in object.measures:

                #object_name = measure["name_for_screen"]
                try:

                    date_from_ts = datetime.fromtimestamp(measure["timestamp"])
                except:
                    continue
                try:
                    millis_from_ts = date_from_ts.strftime("%f")[: -3]
                except:
                    millis_from_ts = "000"


                try:
                    np_array = np.frombuffer(base64.b64decode(measure["screenshot"]),np.uint8)

                    img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

                    date_formatted = date_from_ts.strftime("%Y%m%d_%H%M%S") + "_" + str(millis_from_ts) \
                                     + "_UTC" + time.strftime("%z")

                    if prefix is not None:
                        filename =  prefix + "_" + object_name + "_" + date_formatted + "_screenshot.png"
                    else:
                        filename = object_name + "_" + date_formatted + "_screenshot.png"

                    cv2.imwrite(file_path + os.sep + filename, img)

                except:
                    pass

                try:

                    np_array = np.frombuffer(base64.b64decode(measure["annotation"]),np.uint8)

                    img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

                    date_formatted = date_from_ts.strftime("%Y%m%d_%H%M%S") + "_" + str(millis_from_ts) \
                                     + "_UTC" + time.strftime("%z")

                    if prefix is not None:
                        filename =  prefix + "_" + object_name + "_" + date_formatted + "_annotation.png"
                    else:
                        filename = object_name + "_" + date_formatted + "_annotation.png"

                    cv2.imwrite(file_path + os.sep + filename, img)

                except:
                    pass

    def save(self, filename, json_object, chunk, object_list, exit, duration):

        with open(filename, 'w') as f:
            json.dump(self._build_json(json_object, chunk, object_list, exit, duration), f, indent=4,
                      sort_keys=True, ensure_ascii=False)
