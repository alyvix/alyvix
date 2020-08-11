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

    def _build_json(self, json_object, chunk, object_list, engine_arguments_text, exit, state, duration,
                    compression, recording):

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

            for series in object.series:
                del series["series_name"]
                del series["object_name"]
                del series["performance_name"]
                del series["timeout"]
                del series["group"]
                del series["thresholds"]
                del series["output"]
                del series["end_timestamp"]
                del series["initialize_cnt"]
                del series["detection_type"]

                series["performance_ms"] = int(series["performance_ms"])
                series["accuracy_ms"] = int(series["accuracy_ms"])

                if series["maps"] == None:
                    series["maps"] = []

                try:
                    if series["screenshot"] is not None:
                        if (recording=="broken-output-only" and exit == "false") or recording == "any-output":
                            if compression == "compressed":
                                jpg_image = cv2.imencode('.jpg', series["screenshot"], [int(cv2.IMWRITE_JPEG_QUALITY), 30])
                                base64png = base64.b64encode(jpg_image[1]).decode('ascii')
                            else:
                                png_image = cv2.imencode('.png', series["screenshot"])
                                base64png = base64.b64encode(png_image[1]).decode('ascii')
                            series["screenshot"] = base64png
                            #np_array = np.frombuffer(base64.b64decode(base64png), np.uint8)
                            #np_array = cv2.imdecode(np_array, 1)
                            #cv2.imwrite("D:\\alyvix_testcase\\"+str(time.time()).replace(".","")+".jpg", np_array, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
                        else:
                            series["screenshot"] = None
                except:
                    pass

                try:
                    if series["annotation"] is not None:
                        if (recording == "broken-output-only" and exit == "false") or recording == "any-output":
                            if compression == "compressed":
                                jpg_image = cv2.imencode('.jpg', series["annotation"], [int(cv2.IMWRITE_JPEG_QUALITY), 30])
                                base64png = base64.b64encode(jpg_image[1]).decode('ascii')
                            else:
                                png_image = cv2.imencode('.png', series["annotation"])
                                base64png = base64.b64encode(png_image[1]).decode('ascii')
                            series["annotation"] = base64png
                            #np_array = np.frombuffer(base64.b64decode(base64png), np.uint8)
                            #np_array = cv2.imdecode(np_array, 1)
                            #cv2.imwrite("D:\\alyvix_testcase\\"+str(time.time()).replace(".","")+".jpg", np_array,[int(cv2.IMWRITE_JPEG_QUALITY), 100])
                        else:
                            series["annotation"] = None
                except:
                    pass

            object_dict["measure"]["series"] = object.series


            json_object["objects"][object.object_name] = object_dict

        alias = ""

        if chunk["alias"] is not None:
            alias = chunk["alias"]

        json_object["run"] = {"host": chunk["host"], "user": chunk["user"],
                              "test": chunk["test"], "code": chunk["code"],
                              "alias": alias, "duration_s": round(duration,3),
                              "arguments": engine_arguments_text,
                              "exit": exit, "state": state}

        return json_object

    def save_screenshots(self, file_path, performances, prefix=None, compression="lossless"):
        for perf in performances:

            object_name = perf["performance_name"]

            #for measure in object.measures:

            #object_name = measure["name_for_screen"]
            try:

                date_from_ts = datetime.fromtimestamp(perf["timestamp"])
            except:
                continue
            try:
                millis_from_ts = date_from_ts.strftime("%f")[: -3]
            except:
                millis_from_ts = "000"


            try:
                #np_array = np.frombuffer(base64.b64decode(perf["screenshot"]),np.uint8)
                #img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

                date_formatted = date_from_ts.strftime("%Y%m%d_%H%M%S") + "_" + str(millis_from_ts) \
                                 + "_UTC" + time.strftime("%z")


                if compression == "compressed":
                    if prefix is not None:
                        filename = date_formatted + "_" + prefix + "_" + object_name + "_screenshot.jpg"
                    else:
                        filename = date_formatted + "_" + object_name + "_screenshot.jpg"


                    cv2.imwrite(file_path + os.sep + filename, perf["screenshot"], [int(cv2.IMWRITE_JPEG_QUALITY), 30])
                else:
                    if prefix is not None:
                        filename = date_formatted + "_" + prefix + "_" + object_name + "_screenshot.png"
                    else:
                        filename = date_formatted + "_" + object_name + "_screenshot.png"


                    cv2.imwrite(file_path + os.sep + filename, perf["screenshot"])

            except:
                pass

            try:

                #np_array = np.frombuffer(base64.b64decode(perf["annotation"]),np.uint8)
                #img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

                date_formatted = date_from_ts.strftime("%Y%m%d_%H%M%S") + "_" + str(millis_from_ts) \
                                 + "_UTC" + time.strftime("%z")

                if compression == "compressed":

                    if prefix is not None:
                        filename = date_formatted + "_" + prefix + "_" + object_name + "_annotation.jpg"
                    else:
                        filename = date_formatted + "_" + prefix + "_" + object_name + "_annotation.jpg"


                    cv2.imwrite(file_path + os.sep + filename, perf["annotation"], [int(cv2.IMWRITE_JPEG_QUALITY), 30])
                else:

                    if prefix is not None:
                        filename = date_formatted + "_" + prefix + "_" + object_name + "_annotation.png"
                    else:
                        filename = date_formatted + "_" + prefix + "_" + object_name + "_annotation.png"

                    cv2.imwrite(file_path + os.sep + filename, perf["annotation"])

            except:
                pass

    def save(self, filename, json_object, chunk, object_list, engine_arguments_text, exit, state, duration, compression, recording):

        with open(filename, 'w') as f:
            json.dump(self._build_json(json_object, chunk, object_list, engine_arguments_text, exit, state, duration,
                                       compression, recording), f, indent=4,
                      sort_keys=True, ensure_ascii=False)
