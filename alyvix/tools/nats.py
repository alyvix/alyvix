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

from pynats import NATSClient
from pynats.exceptions import NATSReadSocketError

import math
from sys import platform as _platform



class NatsManager:

    def __init__(self):
        super(NatsManager, self).__init__()


    def publish_message(self, objects, start_time, server, db, measure, filename):

        current_timestamp = str(int(time.time() * 1000 * 1000 * 1000))

        client = NATSClient("nats://" + server, socket_timeout=8)

        client.connect()

        cumsum_value = 0

        for object in objects:

            if object["output"] is False:
                continue

            timed_out = False
            not_executed = False

            warning_threshold = None
            critical_threshold = None

            group_msg = ""

            if object["group"] is not None:
                group_msg = ",transaction_group=" + object["group"].replace(" ", "\ ")

            curr_perf_string = ""

            try:
                warning_threshold = object["thresholds"]["warning_s"]
            except:
                pass

            try:
                critical_threshold = object["thresholds"]["critical_s"]
            except:
                pass

            msg_warning = ""

            if warning_threshold is not None:
                msg_warning = ",warning_threshold=" + str(int(warning_threshold * 1000))

            msg_critical = ""

            if critical_threshold is not None:
                msg_critical = ",critical_threshold=" + str(int(critical_threshold * 1000))

            #if object.timeout != None:
            msg_timeout = ",timeout_threshold=" + str(int(object["timeout"] * 1000))

            if object["timestamp"] != -1:

                perf_timestamp = str(int(object["timestamp"] * 1000 * 1000 * 1000))

            else:

                perf_timestamp = current_timestamp

                not_executed = True

            msg_perf = ""

            if object["performance_ms"] != -1:

                msg_perf = ",performance=" + str(int(object["performance_ms"]))

            elif not_executed is False:

                msg_perf = ",performance=" + str(int(object["timeout"] * 1000))

                timed_out = True

            accuracy_msg = ""

            if object["accuracy_ms"] != -1 and object["accuracy_ms"] is not None:
                accuracy_msg = ",accuracy=" + str(int(object["accuracy_ms"]))

            msg_cumsum = ""

            msg_cumsumpre = ",cumulative=" + str(cumsum_value)

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

            records_msg=""

            if object["records"]["extract"] != "":
                records_msg = ",records=\"" + object["records"]["extract"].replace("\\", "\\\\").replace("\"", "\\\"") + "\""


            user_msg = ",username=" + os.environ['username']
            host_msg = ",host=" +str(gethostname())

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

            unique_tag_msg = ",run_code=\"" + unique_tag_msg + str(int(start_time)) + "\""


            message= str(measure) + user_msg + host_msg + ",test_name=" +filename + ",transaction_name=" + \
                object["performance_name"].replace(" ", "\ ") + group_msg + \
                ",state=" + object["exit"] + \
                 " " + \
                 msg_warning + msg_critical + msg_timeout + msg_perf + accuracy_msg + msg_cumsum + \
                ",error_level=" + str(object["state"]) + unique_tag_msg

            message = message.replace(" ,"," ")

            message += records_msg + " " + perf_timestamp

            #.replace(" ", "\ ").replace(",", "\,").replace("=", "\=")


            #print(message)

            client.publish(db, payload=message)

            msg = ""

        client.close()

