import cv2
import json
import base64
import copy
import os
from datetime import datetime
from alyvix.tools.screen import ScreenManager

class OutputManager:
    def __init__(self):
        pass

    def _build_json(self, json_object, chunk, object_list):


        objects = []

        sm = ScreenManager()
        w, h = sm.get_resolution()
        scaling_factor = sm.get_scaling_factor()

        for object in object_list:



            resolution_string = str(w) + "*" + str(h) + "@" + str(int(scaling_factor * 100))

            object_dict = json_object["objects"][object.object_name]["components"][resolution_string]

            object_dict["measurement"] = {"perfomance_ms": int(object.performance_ms),
                                          "accuracy_ms": int(object.accuracy_ms),
                                          "timestamp": object.timestamp, "records": object.records}

            if object.screenshot is not None:
                png_image = cv2.imencode('.png', object.screenshot)

                object_dict["measurement"]["screenshot"] = base64.b64encode(png_image[1]).decode('ascii')

            else:
                object_dict["measurement"]["screenshot"] = None

            if object.annotation is not None:
                png_image = cv2.imencode('.png', object.annotation)

                object_dict["measurement"]["annotation"] = base64.b64encode(png_image[1]).decode('ascii')
            else:
                object_dict["measurement"]["annotation"] = None

            json_object["objects"][object.object_name]["components"][resolution_string] = object_dict
            json_object["run"] = {"host": chunk["host"], "user": chunk["user"],
                                  "test": chunk["test"], "code": chunk["code"]}

        return json_object

    def save_screenshots(self, file_path, object_list, prefix=None):
        for object in object_list:


            if object.screenshot is not None:
                date_from_ts = datetime.fromtimestamp(object.timestamp)
                date_formatted = date_from_ts.strftime("%Y%m%d_%H%M%S")

                if prefix is not None:
                    filename =  date_formatted + "_" + prefix + "_" + object.object_name + "_screenshot.png"
                else:
                    filename = date_formatted + "_" + object.object_name + "_screenshot.png"

                cv2.imwrite(file_path + os.sep + filename, object.screenshot)

            if object.annotation is not None:
                date_from_ts = datetime.fromtimestamp(object.timestamp)
                date_formatted = date_from_ts.strftime("%Y%m%d_%H%M%S")


                if prefix is not None:
                    filename =  date_formatted + "_" + prefix + "_" + object.object_name + "_annotation.png"
                else:
                    filename = date_formatted + "_" + object.object_name + "_annotation.png"

                cv2.imwrite(file_path + os.sep + filename, object.annotation)


    def save(self, filename, json_object, chunk, object_list):

        with open(filename, 'w') as f:
            json.dump(self._build_json(json_object, chunk, object_list), f, indent=4,
                      sort_keys=True, ensure_ascii=False)
