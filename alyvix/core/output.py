import cv2
import json
import base64
import copy
import os

class OutputManager:
    def __init__(self):
        pass

    def build_json(self, chunk, object_list):


        objects = []

        for object in object_list:
            dict = {object.object_name:{}}

            dict[object.object_name]["perfomance_ms"] = int(object.performance_ms)
            dict[object.object_name]["accuracy_ms"] = int(object.accuracy_ms)
            dict[object.object_name]["timestamp"] = object.timestamp
            #dict[object.object_name]["screenshot"] = object.screenshot
            #dict[object.object_name]["annotation"] = object.annotation
            dict[object.object_name]["records"] = object.records

            if object.screenshot is not None:
                png_image = cv2.imencode('.png', object.screenshot)

                dict[object.object_name]["screenshot"] = base64.b64encode(png_image[1]).decode('ascii')

            else:
                dict[object.object_name]["screenshot"] = None

            if object.annotation is not None:
                png_image = cv2.imencode('.png', object.annotation)

                dict[object.object_name]["annotation"] = base64.b64encode(png_image[1]).decode('ascii')
            else:
                dict[object.object_name]["annotation"] = None

            objects.append(dict)

        return_dict = copy.deepcopy(chunk)
        return_dict["objects"] = objects

        return return_dict

    def save_screenshots(self, file_path, object_list, prefix=None):
        for object in object_list:


            if object.screenshot is not None:
                filename = object.object_name + "_" + str(object.timestamp) + "_screenshot.png"
                if prefix is not None:
                    filename = prefix + "_" + filename

                cv2.imwrite(file_path + os.sep + filename, object.screenshot)


            if object.annotation is not None:
                filename = object.object_name + "_" + str(object.timestamp) + "_annotation.png"
                if prefix is not None:
                    filename = prefix + "_" + filename

                cv2.imwrite(file_path + os.sep + filename, object.annotation)


    def save(self, json_string, filename):

        with open(filename, 'w') as f:
            json.dump(json_string, f, indent=4, sort_keys=True, ensure_ascii=False)
