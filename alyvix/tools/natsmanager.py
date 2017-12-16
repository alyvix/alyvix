# Alyvix allows you to automate and monitor all types of applications
# Copyright (C) 2015 Alan Pipitone
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
import datetime
from socket import gethostname
from .perfdata import PerfManager
from .info import InfoManager
import argparse, sys
import tornado.ioloop
import tornado.gen
import time
import os
import copy

try:
    from nats.io.client import Client as NATS
except:
    pass

class NatsManager():

    def __init__(self):
        self._perf_manager = PerfManager()
        self._info_manager = InfoManager()

    @tornado.gen.coroutine
    def _pub(self, testcase_name, subject, server, port=4222, measurement="alyvix",
                max_reconnect_attempts=5, reconnect_time_wait=2):

        #self._perf_manager.order_perfdata()
        #last_filled_perf = self._perf_manager.get_last_filled()
        perfdata_list = self._perf_manager.get_all_perfdata()

        keywords_timestamp_array = self._info_manager.get_info('KEYWORD TIMESTAMP')

        keywords_timeout_array = self._info_manager.get_info('KEYWORD TIMEOUT')

        current_timestamp = str(int(time.time()*1000*1000*1000))

        message_lines = []

        testcase_name = testcase_name.replace(" ", "_")

        nc = NATS()
        options = {"servers": ["nats://" + str(server) + ":" + str(port)]}

        exception_occurred = False

        #if we cannot contact nats server then we have to save messages to cache file
        exception_file_name = "data.txt"

        system_drive = os.environ['systemdrive']

        alyvix_programdata_path = system_drive + os.sep + "ProgramData\\Alyvix\\exception\\nats"\
                                  + os.sep + os.environ['username'] + os.sep + testcase_name

        exception_file_full_name = alyvix_programdata_path + os.sep + exception_file_name

        try:
            yield nc.connect(**options)
        except:
            exception_occurred = True

        file_to_read = None
        biggest_cnt = 0
        #read previous messages from cache. last txt file contains all messages
        if os.path.exists(alyvix_programdata_path):

            for file in os.listdir(alyvix_programdata_path):
                if file.endswith(".txt"):

                    if file == "data.txt":
                        if 0 > biggest_cnt:
                            biggest_cnt = 0
                    else:
                        cnt_str = file.replace("data_","").replace(".txt","")
                        cnt_int = int(cnt_str)

                        if cnt_int > biggest_cnt:
                            biggest_cnt = cnt_int

            if biggest_cnt == 0:
                file_to_read = os.path.join(alyvix_programdata_path, "data.txt")
            else:
                file_to_read = os.path.join(alyvix_programdata_path, "data_" + str(biggest_cnt) + ".txt")

            #read cached messages
            if os.path.exists(file_to_read):
                with open(file_to_read) as f:
                    message_lines.extend(f.readlines())
                f.close()

            #delete all cache files
            for file in os.listdir(alyvix_programdata_path):
                if file.endswith(".txt"):
                    try:
                        os.remove(os.path.join(alyvix_programdata_path, file))
                    except:
                        pass


        tmp_message_lines = []
        for message in message_lines:

            message = message.replace("\r\n", "")
            message = message.replace("\r", "")
            message = message.replace("\n", "")

            if message == "":
                pass

            try:
                #try to publish cached messages
                yield nc.publish(subject, message)
            except:
                tmp_message_lines.append(message)
                exception_occurred = True

        message_lines = tmp_message_lines

        cumsum_value = 0

        #publish current performance data

        perf_with_timestamp = []
        perf_without_timestamp = []

        for perfdata in perfdata_list:

            #check if current perf has a timestamp
            for cnt_kts in xrange(len(keywords_timestamp_array)):
                if keywords_timestamp_array[cnt_kts][0] == perfdata.name:
                    perfdata.timestamp = keywords_timestamp_array[cnt_kts][1]
                    perf_with_timestamp.append(perfdata)
                    break

            if perfdata.timestamp == None:
                perf_without_timestamp.append(perfdata)

        perf_with_timestamp = sorted(perf_with_timestamp, key=lambda x: x.timestamp, reverse=False)

        perf_with_timestamp.extend(perf_without_timestamp)

        perfdata_list = perf_with_timestamp

        for perfdata in perfdata_list:

            #check if current perf has a timeout
            for cnt_ktout in xrange(len(keywords_timeout_array)):
                if keywords_timeout_array[cnt_ktout][0] == perfdata.name:
                    perfdata.timeout_threshold = keywords_timeout_array[cnt_ktout][1]
                    break

            timed_out = False
            not_executed = False

            msg_extra = ""

            if perfdata.extra != None and perfdata.extra != "":
                msg_extra = ",extra=" + perfdata.extra

            msg_warning = ""

            if perfdata.warning_threshold != None and perfdata.warning_threshold != "":
                msg_warning = ",warning_threshold=" + str(int(perfdata.warning_threshold * 1000))

            msg_critical = ""

            if perfdata.critical_threshold != None and perfdata.critical_threshold != "":
                msg_critical = ",critical_threshold=" + str(int(perfdata.critical_threshold * 1000))

            msg_timeout = ""

            if perfdata.timeout_threshold != None and perfdata.timeout_threshold != "":
                msg_timeout = ",timeout_threshold=" + str(int(perfdata.timeout_threshold * 1000))

            try:
                perf_timestamp = str(int(perfdata.timestamp*1000*1000))
            except:
                perf_timestamp = current_timestamp
                not_executed = True

            msg_perf = ""
            if perfdata.value != "" and perfdata.value is not None:
                msg_perf = ",performance=" + str(int(perfdata.value * 1000))
            elif not_executed is False:
                #msg_perf = ",performance=" + str(int(perfdata.timeout_threshold * 1000))
                timed_out = True

            msg_cumsum = ""
            msg_cumsumpre = ",cumulative=" + str(cumsum_value)
            if perfdata.value != "" and perfdata.value is not None:
                value = int(cumsum_value + (perfdata.value * 1000))
                msg_cumsum = ",cumulative=" + str(value)
                cumsum_value = value
            elif not_executed is False: #timedout
                value = int(cumsum_value + (perfdata.timeout_threshold * 1000))
                msg_cumsum = ",cumulative=" + str(value)
                cumsum_value = value
            else: #not_executed
                msg_cumsum = ",cumulative=" + str(cumsum_value)

            perfdata_state = "ok"

            if timed_out is True:
                perfdata_state = "timedout"
            elif not_executed is True:
                perfdata_state = "not_executed"
            elif perfdata.state == 1:
                perfdata_state = "warning"
            elif perfdata.state == 2:
                perfdata_state = "critical"
            elif perfdata.state == 3:
                perfdata_state = "unknown"

            msg_errorlevel = ",error_level=0"

            if perfdata.value == "" or perfdata.value is None:
                msg_errorlevel = ",error_level=3"
            elif perfdata.state == 1:
                msg_errorlevel = ",error_level=1"
            elif perfdata.state == 2:
                msg_errorlevel = ",error_level=2"
            elif perfdata.state == 3:
               msg_errorlevel = ",error_level=3"


            point_pre_msg = ""
            point_start_msg = ""
            if not_executed is False:
                point_pre_msg = ",point=pre"
                point_start_msg = ",point=start"

            msg_custom_tags = ""

            for tag in perfdata.custom_tags.keys():
                msg_custom_tags += "," + tag + "=" + perfdata.custom_tags[tag]

            msg_custom_fields = ""

            for field in perfdata.custom_fields.keys():

                is_string = False

                field_value = perfdata.custom_fields[field]

                try:
                    int(field_value)
                except:
                    field_value = "\"" + field_value +"\""

                msg_custom_fields += "," + field + "=" + field_value

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

            if self._info_manager.get_info('SUITE NAME') is not None:
                try:
                    unique_tag_msg = unique_tag_msg + self._info_manager.get_info('SUITE NAME')[0]
                    unique_tag_msg = unique_tag_msg + self._info_manager.get_info('SUITE NAME')[1]
                    unique_tag_msg = unique_tag_msg + self._info_manager.get_info('SUITE NAME')[-2]
                    unique_tag_msg = unique_tag_msg + self._info_manager.get_info('SUITE NAME')[-1]
                except:
                    pass

            unique_tag_msg = ",run_code=\"" + unique_tag_msg + str(self._info_manager.get_info('START TIME')) + "\""
            #unique_tag_msg = ""

            """
            if point_pre_msg != "":
                message = str(measurement) + user_msg + host_msg + ",test_name=" + str(testcase_name) \
                          + ",transaction_name=" + str(perfdata.name).replace(" ", "_") + ",state=" + perfdata_state + \
                          msg_extra + msg_custom_tags + point_pre_msg + unique_tag_msg +" " + msg_warning + msg_critical + \
                          msg_timeout + msg_perf + msg_cumsumpre + msg_errorlevel + " " + perf_timestamp

                message = message.replace(" ,", " ")

                try:
                    yield nc.publish(subject, message)
                except:
                    # store to cache list if we cannot publish messages
                    message_lines.append(message)
                    exception_occurred = True
            """
            message= str(measurement) + user_msg + host_msg + ",test_name=" +str(testcase_name)\
                     + ",transaction_name=" + str(perfdata.name).replace(" ", "_") + ",state=" + perfdata_state +\
                     msg_extra + msg_custom_tags + " " + msg_warning + msg_critical +\
                     msg_timeout + msg_perf + msg_cumsum + msg_errorlevel + msg_custom_fields + unique_tag_msg + " " + perf_timestamp

            message = message.replace(" ,"," ")


            try:
                yield nc.publish(subject, message)
            except:
                #store to cache list if we cannot publish messages
                message_lines.append(message)
                exception_occurred = True

            if not_executed is False:

                #alyvix saves timestamp in millisconds, so first of all we have to restore it in seconds interval, then
                #we have to add perfdata value
                if timed_out is True:
                    end_timestamp_in_seconds = (float(perfdata.timestamp)/1000) + perfdata.timeout_threshold
                else:
                    if perfdata.end_timestamp_only_for_summed_perf is None:
                        end_timestamp_in_seconds = (float(perfdata.timestamp) / 1000) + perfdata.value
                    else:
                        end_timestamp_in_seconds = (float(perfdata.end_timestamp_only_for_summed_perf) / 1000)
                #convert timestamp in seconds to timestamp in nanoseconds
                end_timestamp_in_nanoseconds = int(end_timestamp_in_seconds * 1000 * 1000 * 1000)


                """
                message = str(measurement) + user_msg + host_msg + ",test_name=" + str(testcase_name) \
                          + ",transaction_name=" + str(perfdata.name).replace(" ", "_") + ",state=" + perfdata_state + \
                          msg_extra + msg_custom_tags + ",point=end" + unique_tag_msg + " " + msg_warning + msg_critical + msg_timeout + \
                          msg_perf + msg_cumsum + msg_errorlevel + " " + str(end_timestamp_in_nanoseconds)

                message = message.replace(" ,", " ")

                try:
                    yield nc.publish(subject, message)
                except:
                    # store to cache list if we cannot publish messages
                    message_lines.append(message)
                    exception_occurred = True
                """
        try:
            yield nc.flush()
        except:
            exception_occurred = True

        #store cache list to cache file
        if exception_occurred is True:
            if not os.path.exists(alyvix_programdata_path):
                os.makedirs(alyvix_programdata_path)

            try:
                with open(exception_file_full_name, 'w') as f:

                    for item in message_lines:
                        f.write("%s\r\n" % item)

                f.close()
            except:
                filename = exception_file_full_name
                cnt = 0
                while True:
                    if not os.path.exists(filename):
                        with open(filename, 'w') as f:

                            for item in message_lines:
                                f.write("%s\r\n" % item)

                        f.close()
                        break

                    cnt += 1

                    if (cnt-1) == 0:
                        filename = filename.replace(".txt", "_" + str(cnt) + ".txt")
                    else:
                        filename = filename.replace(str(cnt-1) + ".txt", str(cnt) + ".txt")



    def publish(self, testcase_name, subject, server, port=4222, measurement="alyvix",
                max_reconnect_attempts=5, reconnect_time_wait=2):
        tornado.ioloop.IOLoop.instance().run_sync(lambda: self._pub(testcase_name, subject, server, port, measurement,
                max_reconnect_attempts, reconnect_time_wait))