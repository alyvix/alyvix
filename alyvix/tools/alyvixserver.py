# Alyvix allows you to automate and monitor all types of applications
# Copyright (C) 2020 Alan Pipitone
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
import time
from socket import gethostname
import requests

from pynats import NATSClient
from pynats.exceptions import NATSReadSocketError

import math
from sys import platform as _platform



class AlyvixServerManager:

    def __init__(self):
        super(AlyvixServerManager, self).__init__()

    def publish_message(self, url, objects, start_time, filename, test_case_common, verify=False):

        current_timestamp = int(time.time() * 1000 * 1000 * 1000)

        cumsum_value = 0

        output_json = {}
        performances = []

        for object in objects:

            perf_dict = {}

            if object["output"] is False:
                continue

            timed_out = False
            not_executed = False

            warning_threshold = None
            critical_threshold = None

            perf_dict["transaction_name"] = object["object_name"]

            perf_dict["transaction_alias"] = object["series_name"]

            perf_dict["transaction_detection_type"] = object["detection_type"]

            perf_dict["transaction_exit"] = object["exit"]
            perf_dict["transaction_state"] = object["state"]

            if object["group"] is not None:
                perf_dict["transaction_group"] = object["group"]
            else:
                perf_dict["transaction_group"] = None

            try:
                warning_threshold = object["thresholds"]["warning_s"]
            except:
                pass

            try:
                critical_threshold = object["thresholds"]["critical_s"]
            except:
                pass

            if warning_threshold is not None:
                perf_dict["transaction_warning_ms"] = int(warning_threshold * 1000)
            else:
                perf_dict["transaction_warning_ms"] = None

            if critical_threshold is not None:
                perf_dict["transaction_critical_ms"] = int(critical_threshold * 1000)
            else:
                perf_dict["transaction_critical_ms"] = None

            # if object.timeout != None:
            perf_dict["transaction_timeout_ms"] = int(object["timeout"] * 1000)

            if object["timestamp"] != -1:

                perf_dict["timestamp_epoch"] = int(object["timestamp"] * 1000 * 1000 * 1000)

            else:

                perf_dict["timestamp_epoch"] = current_timestamp
                perf_dict["transaction_performance_ms"] = None

                not_executed = True

            if object["performance_ms"] != -1:

                perf_dict["transaction_performance_ms"] = int(object["performance_ms"])

            elif not_executed is False:

                perf_dict["transaction_performance_ms"] = int(object["timeout"] * 1000)

                timed_out = True

            if object["accuracy_ms"] != -1 and object["accuracy_ms"] is not None:
                perf_dict["transaction_accuracy_ms"] = int(object["accuracy_ms"])
            else:
                perf_dict["transaction_accuracy_ms"] = None

            """
            if object["performance_ms"] != -1:

                value = int(cumsum_value + object["performance_ms"])

                msg_cumsum = ",cumulative=" + str(value)

                cumsum_value = value

            elif not_executed is False: #timedout

                value = int(cumsum_value + (object["timeout"]*1000))

                msg_cumsum = ",cumulative=" + str(value)

                cumsum_value = value

            else: #not_executed

                msg_cumsum = ",cumulative=" + str(cumsum_value)
            """

            perf_dict["transaction_record_text"] = object["records"]["text"]
            perf_dict["transaction_record_extract"] = object["records"]["extract"]
            perf_dict["transaction_resolution_width"] = object["resolution"]["width"]
            perf_dict["transaction_resolution_height"] = object["resolution"]["height"]
            perf_dict["transaction_scaling_factor"] = object["scaling_factor"]

            perf_dict["transaction_screenshot"] = None

            try:
                if object["screenshot"] is not None:
                    if (test_case_common["screenshot_recording"] == "broken-output-only" and test_case_common[
                        "test_case_exit"] == "false") \
                            or test_case_common["screenshot_recording"] == "any-output":
                        if test_case_common["screenshot_compression"] == "compressed":
                            jpg_image = cv2.imencode('.jpg', object["screenshot"], [int(cv2.IMWRITE_JPEG_QUALITY), 30])
                            base64png = base64.b64encode(jpg_image[1]).decode('ascii')
                        else:
                            png_image = cv2.imencode('.png', object["screenshot"])
                            base64png = base64.b64encode(png_image[1]).decode('ascii')
                        perf_dict["transaction_screenshot"] = base64png

            except:
                pass

            perf_dict["transaction_annotation"] = None

            try:
                if object["annotation"] is not None:
                    if (test_case_common["screenshot_recording"] == "broken-output-only" and test_case_common[
                        "test_case_exit"] == "false") \
                            or test_case_common["screenshot_recording"] == "any-output":
                        if test_case_common["screenshot_compression"] == "compressed":
                            jpg_image = cv2.imencode('.jpg', object["annotation"], [int(cv2.IMWRITE_JPEG_QUALITY), 30])
                            base64png = base64.b64encode(jpg_image[1]).decode('ascii')
                        else:
                            png_image = cv2.imencode('.png', object["annotation"])
                            base64png = base64.b64encode(png_image[1]).decode('ascii')
                        perf_dict["transaction_annotation"] = base64png
            except:
                pass

            domain = os.environ['userdomain']
            username = domain + "\\" + os.environ['username']
            hostname = str(gethostname())
            if domain.lower() == hostname.lower():
                username = os.environ['username']

            perf_dict["domain_username"] = username

            perf_dict["hostname"] = str(gethostname())

            unique_tag_msg = ""

            try:
                unique_tag_msg = str(gethostname())[0]
                unique_tag_msg = unique_tag_msg + str(gethostname())[1]
                unique_tag_msg = unique_tag_msg + str(gethostname())[-2]
                unique_tag_msg = unique_tag_msg + str(gethostname())[-1]
            except:
                pass

            try:
                unique_tag_msg = unique_tag_msg + os.environ['username'][0]
                unique_tag_msg = unique_tag_msg + os.environ['username'][1]
                unique_tag_msg = unique_tag_msg + os.environ['username'][-2]
                unique_tag_msg = unique_tag_msg + os.environ['username'][-1]
            except:
                pass

            try:
                unique_tag_msg = unique_tag_msg + filename[0]
                unique_tag_msg = unique_tag_msg + filename[1]
                unique_tag_msg = unique_tag_msg + filename[-2]
                unique_tag_msg = unique_tag_msg + filename[-1]
            except:
                pass

            perf_dict["test_case_execution_code"] = unique_tag_msg + str(int(start_time))

            perf_dict["test_case_name"] = test_case_common["test_case_name"]
            perf_dict["test_case_alias"] = test_case_common["test_case_alias"]
            perf_dict["test_case_duration_ms"] = test_case_common["test_case_duration_ms"]
            perf_dict["test_case_arguments"] = test_case_common["test_case_arguments"]
            perf_dict["test_case_exit"] = test_case_common["test_case_exit"]
            perf_dict["test_case_state"] = test_case_common["test_case_state"]

            performances.append(perf_dict)

        output_json["performances"] = performances

        try:
            r = requests.post(url, json=output_json, timeout=10, verify=verify)
        except Exception as ex:
            pass

    def publish_message_v1(self, url, objects, start_time, filename, test_case_common, verify=False):

        current_timestamp = int(time.time() * 1000 * 1000 * 1000)

        cumsum_value = 0

        output_json = {}
        performances = []

        for object in objects:

            perf_dict = {}

            if object["output"] is False:
                continue

            timed_out = False
            not_executed = False

            warning_threshold = None
            critical_threshold = None

            perf_dict["transaction_name"] = object["object_name"]

            perf_dict["transaction_alias"] = object["series_name"]

            perf_dict["transaction_detection_type"] = object["detection_type"]

            perf_dict["transaction_exit"] = object["exit"]
            perf_dict["transaction_state"] = object["state"]

            if object["group"] is not None:
                perf_dict["transaction_group"] = object["group"]
            else:
                perf_dict["transaction_group"] = None

            try:
                warning_threshold = object["thresholds"]["warning_s"]
            except:
                pass

            try:
                critical_threshold = object["thresholds"]["critical_s"]
            except:
                pass

            if warning_threshold is not None:
                perf_dict["transaction_warning_ms"] = int(warning_threshold * 1000)
            else:
                perf_dict["transaction_warning_ms"] = None

            if critical_threshold is not None:
                perf_dict["transaction_critical_ms"] = int(critical_threshold * 1000)
            else:
                perf_dict["transaction_critical_ms"] = None

            # if object.timeout != None:
            perf_dict["transaction_timeout_ms"] = int(object["timeout"] * 1000)

            if object["timestamp"] != -1:

                perf_dict["timestamp_epoch"] = int(object["timestamp"] * 1000 * 1000 * 1000)

            else:

                perf_dict["timestamp_epoch"] = current_timestamp
                perf_dict["transaction_performance_ms"] = None

                not_executed = True

            if object["performance_ms"] != -1:

                perf_dict["transaction_performance_ms"] = int(object["performance_ms"])

            elif not_executed is False:

                perf_dict["transaction_performance_ms"] = int(object["timeout"] * 1000)

                timed_out = True

            if object["accuracy_ms"] != -1 and object["accuracy_ms"] is not None:
                perf_dict["transaction_accuracy_ms"] = int(object["accuracy_ms"])
            else:
                perf_dict["transaction_accuracy_ms"] = None

            perf_dict["transaction_record_text"] = object["records"]["text"]
            perf_dict["transaction_record_extract"] = object["records"]["extract"]
            perf_dict["transaction_resolution_width"] = object["resolution"]["width"]
            perf_dict["transaction_resolution_height"] = object["resolution"]["height"]
            perf_dict["transaction_scaling_factor"] = object["scaling_factor"]

            perf_dict["transaction_screenshot"] = None
            perf_dict["transaction_definition"] = None

            try:
                if object["screenshot"] is not None:
                    png_image = cv2.imencode('.png', object["screenshot"])
                    base64png = base64.b64encode(png_image[1]).decode('ascii')
                    perf_dict["transaction_screenshot"] = base64png

            except:
                pass

            perf_dict["transaction_annotation"] = None

            try:
                if object["annotation"] is not None:

                    base64png = base64.b64encode(object["annotation"]).decode('ascii')
                    perf_dict["transaction_annotation"] = base64png
            except:
                pass

            try:
                if object["definition"] is not None:

                    base64png = base64.b64encode(object["definition"]).decode('ascii')
                    perf_dict["transaction_definition"] = base64png
            except:
                pass

            domain = os.environ['userdomain']
            username = domain + "\\" + os.environ['username']
            hostname = str(gethostname())
            if domain.lower() == hostname.lower():
                username = os.environ['username']

            perf_dict["domain_username"] = username

            perf_dict["hostname"] = str(gethostname())

            unique_tag_msg = ""

            try:
                unique_tag_msg = str(gethostname())[0]
                unique_tag_msg = unique_tag_msg + str(gethostname())[1]
                unique_tag_msg = unique_tag_msg + str(gethostname())[-2]
                unique_tag_msg = unique_tag_msg + str(gethostname())[-1]
            except:
                pass

            try:
                unique_tag_msg = unique_tag_msg + os.environ['username'][0]
                unique_tag_msg = unique_tag_msg + os.environ['username'][1]
                unique_tag_msg = unique_tag_msg + os.environ['username'][-2]
                unique_tag_msg = unique_tag_msg + os.environ['username'][-1]
            except:
                pass

            try:
                unique_tag_msg = unique_tag_msg + filename[0]
                unique_tag_msg = unique_tag_msg + filename[1]
                unique_tag_msg = unique_tag_msg + filename[-2]
                unique_tag_msg = unique_tag_msg + filename[-1]
            except:
                pass

            perf_dict["test_case_execution_code"] = unique_tag_msg + str(int(start_time))

            perf_dict["test_case_name"] = test_case_common["test_case_name"]
            perf_dict["test_case_alias"] = test_case_common["test_case_alias"]
            perf_dict["test_case_duration_ms"] = test_case_common["test_case_duration_ms"]
            perf_dict["test_case_arguments"] = test_case_common["test_case_arguments"]
            perf_dict["test_case_exit"] = test_case_common["test_case_exit"]
            perf_dict["test_case_state"] = test_case_common["test_case_state"]

            performances.append(perf_dict)

        output_json["performances"] = performances

        try:
            r = requests.post(url, json=output_json, timeout=10, verify=verify)
        except Exception as ex:
            pass


    def publish_message_v2(self, url, objects, start_time, filename, test_case_common, verify=False):

        current_timestamp = int(time.time() * 1000 * 1000 * 1000)

        cumsum_value = 0

        output_json = {}
        performances = []

        for object in objects:

            perf_dict = {}

            if object["output"] is False:
                continue

            timed_out = False
            not_executed = False

            warning_threshold = None
            critical_threshold = None

            perf_dict["transaction_name"] = object["object_name"]

            perf_dict["transaction_alias"] = object["series_name"]

            perf_dict["transaction_detection_type"] = object["detection_type"]


            perf_dict["transaction_exit"] = object["exit"]
            perf_dict["transaction_state"] = object["state"]

            if object["group"] is not None:
                perf_dict["transaction_group"] = object["group"]
            else:
                perf_dict["transaction_group"] = None

            try:
                warning_threshold = object["thresholds"]["warning_s"]
            except:
                pass

            try:
                critical_threshold = object["thresholds"]["critical_s"]
            except:
                pass

            if warning_threshold is not None:
                perf_dict["transaction_warning_ms"] = int(warning_threshold * 1000)
            else:
                perf_dict["transaction_warning_ms"] = None

            if critical_threshold is not None:
                perf_dict["transaction_critical_ms"] = int(critical_threshold * 1000)
            else:
                perf_dict["transaction_critical_ms"] = None

            #if object.timeout != None:
            perf_dict["transaction_timeout_ms"] = int(object["timeout"] * 1000)

            if object["timestamp"] != -1:

                perf_dict["timestamp_epoch"] = int(object["timestamp"] * 1000 * 1000 * 1000)

            else:

                perf_dict["timestamp_epoch"] = current_timestamp
                perf_dict["transaction_performance_ms"] = None

                not_executed = True

            if object["performance_ms"] != -1:

                perf_dict["transaction_performance_ms"] = int(object["performance_ms"])

            elif not_executed is False:

                perf_dict["transaction_performance_ms"] = int(object["timeout"] * 1000)

                timed_out = True

            if object["accuracy_ms"] != -1 and object["accuracy_ms"] is not None:
                perf_dict["transaction_accuracy_ms"]  = int(object["accuracy_ms"])
            else:
                perf_dict["transaction_accuracy_ms"] = None

            """
            if object["performance_ms"] != -1:

                value = int(cumsum_value + object["performance_ms"])

                msg_cumsum = ",cumulative=" + str(value)

                cumsum_value = value

            elif not_executed is False: #timedout

                value = int(cumsum_value + (object["timeout"]*1000))

                msg_cumsum = ",cumulative=" + str(value)

                cumsum_value = value

            else: #not_executed

                msg_cumsum = ",cumulative=" + str(cumsum_value)
            """

            perf_dict["transaction_record_text"] = object["records"]["text"]
            perf_dict["transaction_record_extract"] = object["records"]["extract"]
            perf_dict["transaction_resolution_width"] = object["resolution"]["width"]
            perf_dict["transaction_resolution_height"] = object["resolution"]["height"]
            perf_dict["transaction_scaling_factor"] = object["scaling_factor"]

            
            perf_dict["transaction_screenshot"] = None
            perf_dict["transaction_definition"] = None

            try:
                if object["screenshot"] is not None:
                    png_image = cv2.imencode('.png', object["screenshot"])
                    base64png = base64.b64encode(png_image[1]).decode('ascii')
                    perf_dict["transaction_screenshot"] = base64png

            except:
                pass

            perf_dict["transaction_annotation"] = None

            try:
                if object["annotation"] is not None:

                    base64png = base64.b64encode(object["annotation"]).decode('ascii')
                    perf_dict["transaction_annotation"] = base64png
            except:
                pass
                
            try:
                if object["definition"] is not None:

                    base64png = base64.b64encode(object["definition"]).decode('ascii')
                    perf_dict["transaction_definition"] = base64png
            except:
                pass


            perf_dict["domain"] = os.environ['userdomain']
            perf_dict["username"] = os.environ['username']

            perf_dict["hostname"] = str(gethostname())

            unique_tag_msg = ""

            try:
                unique_tag_msg = str(gethostname())
            except:
                pass

            try:
                unique_tag_msg = unique_tag_msg + os.environ['userdomain']
            except:
                pass

            try:
                unique_tag_msg = unique_tag_msg + os.environ['username']
            except:
                pass


            try:
                unique_tag_msg = unique_tag_msg + filename
            except:
                pass

            perf_dict["test_case_execution_code"] = unique_tag_msg + str(int(start_time))

            #perf_dict["test_case_id"] = test_case_common["test_case_id"]
            perf_dict["test_case_name"] = test_case_common["test_case_name"]
            perf_dict["test_case_filename"] = test_case_common["test_case_filename"]
            perf_dict["test_case_duration_ms"] = test_case_common["test_case_duration_ms"]
            perf_dict["test_case_arguments"] = test_case_common["test_case_arguments"]
            perf_dict["test_case_exit"] = test_case_common["test_case_exit"]
            perf_dict["test_case_state"] = test_case_common["test_case_state"]

            performances.append(perf_dict)

        output_json["performances"] = performances


        try:
            r = requests.post(url, json=output_json, timeout=10, verify=verify)
        except Exception as ex:
            pass

