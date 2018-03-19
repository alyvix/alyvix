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

import os
import time
import copy
import tempfile
import datetime
from alyvix.tools.info import InfoManager

perfdata_list = []
last_timeout_value = (None, None) #we need this for back compatibility
deleted_on_rename_list = []
timedout_finders = []
perf_counter = 0
declaration_counter = 0


class _PerfData:

    def __init__(self):
        self.name = None
        self.value = None
        self.warning_threshold = None
        self.critical_threshold = None
        self.timeout_threshold = None
        self.counter = -1
        self.state = 0
        self.timestamp = None
        self.end_timestamp_only_for_summed_perf = None
        self.extra = None
        self.custom_tags = {}
        self.custom_fields = {}


class PerfManager:

    def __init__(self):
        self.performance_desc_string = ""
        self._info_manager = InfoManager()
        self._info_manager.tiny_update()

        self._last_filled_perf = None
        self.not_ok_perfdata = 0

    def clear_perfdata(self):
        global perfdata_list
        perfdata_list = []


    def add_perfdata(self, name, value=None, warning_threshold=None, critical_threshold=None, state=None, inittimestamp=False):

        global perfdata_list
        global perf_counter
        global declaration_counter

        declaration_counter = declaration_counter + 1

        perf_data = _PerfData()
        perf_data.name = str(name)

        try:
            perf_data.value = float(value)
            if perf_data.counter == -1:
                perf_data.counter = perf_counter
                perf_counter = perf_counter + 1
        except:
            perf_data.value = ""

        try:
            perf_data.warning_threshold = float(warning_threshold)
        except:
            perf_data.warning_threshold = ""

        try:
            perf_data.critical_threshold = float(critical_threshold)
        except:
             perf_data.critical_threshold = ""


        if state is not None:
            try:
                perf_data.state = int(state)
            except:
                perf_data.state = 2 #3
        else:
            try:
                perf_data.state = int(os.getenv("exitcode"))
            except:
                perf_data.state = 2 #3

        if perf_data.value != "" and perf_data.critical_threshold != "" and perf_data.value >= perf_data.critical_threshold:
            perf_data.state = 2
        elif perf_data.value != "" and perf_data.warning_threshold != "" and perf_data.value >= perf_data.warning_threshold:
            perf_data.state = 1
        elif perf_data.value != "":
            perf_data.state = 0

        initts = False

        if inittimestamp == True:
            initts = True

        try:
            if str(inittimestamp).lower() == "true":
                initts = True
        except:
            pass

        if  initts == True:
            perf_data.timestamp = int(time.time() * 1000)

            current_keyword_timestamp_array = self._info_manager.get_info('KEYWORD TIMESTAMP')

            # current_keyword_timestamp_array_copy = copy.deepcopy(current_keyword_timestamp_array)

            timestamp_modified = False
            for cnt_kts in xrange(len(current_keyword_timestamp_array)):
                if current_keyword_timestamp_array[cnt_kts][0] == name:
                    timestamp_modified = True
                    current_keyword_timestamp_array[cnt_kts] = (name, perf_data.timestamp)
                    break

            if timestamp_modified is False:
                current_keyword_timestamp_array.append((name, perf_data.timestamp))

            self._info_manager.set_info('KEYWORD TIMESTAMP',
                                        current_keyword_timestamp_array)

        else:
            perf_data.timestamp = None

        keywords_timestamp_array = self._info_manager.get_info('KEYWORD TIMESTAMP')

        for cnt_kts in xrange(len(keywords_timestamp_array)):
            if keywords_timestamp_array[cnt_kts][0] == name:
                perf_data.timestamp = keywords_timestamp_array[cnt_kts][1]
                break

        perf_data.timeout_threshold = None

        keywords_timeout_array = self._info_manager.get_info('KEYWORD TIMEOUT')

        for cnt_ktout in xrange(len(keywords_timeout_array)):
            if keywords_timeout_array[cnt_ktout][0] == name:
                perf_data.timeout_threshold = keywords_timeout_array[cnt_ktout][1]
                break

        cnt = 0

        for perf_data_in_list in perfdata_list:
            if perf_data_in_list.name == perf_data.name:
                perf_data.custom_tags = perfdata_list[cnt].custom_tags
                perf_data.custom_fields = perfdata_list[cnt].custom_fields

                perfdata_list[cnt] = perf_data
                return

            cnt = cnt + 1

        perfdata_list.append(perf_data)

    def rename_perfdata(self, old_name, new_name, warning_threshold="", critical_threshold=""):

        global perfdata_list

        perfdata_list_copy = copy.deepcopy(perfdata_list)

        for perf_data_in_list in perfdata_list:
            if perf_data_in_list.name == str(old_name):
                if perf_data_in_list.value == "":
                    raise Exception("The Keyword value is None")

        keywords_timestamp_array = copy.deepcopy(self._info_manager.get_info('KEYWORD TIMESTAMP'))

        cnt = 0

        for cnt_kts in xrange(len(keywords_timestamp_array)):
            if keywords_timestamp_array[cnt_kts][0] == str(new_name):
                del keywords_timestamp_array[cnt_kts]

        old_name_exists = False
        for perf_data_in_list in perfdata_list:

            for cnt_kts in xrange(len(keywords_timestamp_array)):
                if keywords_timestamp_array[cnt_kts][0] == str(old_name):
                    keywords_timestamp_array[cnt_kts] = (new_name, keywords_timestamp_array[cnt_kts][1])

            self._info_manager.set_info('KEYWORD TIMESTAMP', keywords_timestamp_array)

            if perf_data_in_list.name == str(new_name):
                deleted_on_rename_list.append(copy.deepcopy(perfdata_list_copy[cnt]))
                del perfdata_list_copy[cnt]
                cnt = cnt - 1
            elif perf_data_in_list.name == str(old_name):

                old_name_exists = True

                perfdata_list_copy[cnt].name = str(new_name)

                try:
                    new_warning_threshold = float(warning_threshold)
                    perfdata_list_copy[cnt].warning_threshold = new_warning_threshold
                except:
                    pass

                try:
                    new_critical_threshold = float(critical_threshold)
                    perfdata_list_copy[cnt].critical_threshold = new_critical_threshold
                except:
                    pass

            cnt = cnt + 1

        if old_name_exists is False:
            raise Exception("The keyword name does not exist")

        perfdata_list = copy.deepcopy(perfdata_list_copy)



        cnt = 0
        scraper_list_copy = copy.deepcopy(self._info_manager.get_info('SCRAPER COLLECTION'))

        for sc_in_list in self._info_manager.get_info('SCRAPER COLLECTION'):

            name = sc_in_list[0]

            if name == old_name:
                scraper_list_copy[cnt] = (new_name, sc_in_list[1], sc_in_list[2])

            cnt += 1

        self._info_manager.set_info('SCRAPER COLLECTION', copy.deepcopy(scraper_list_copy))


    def set_perfdata_extra(self, name, extra):

        global perfdata_list

        for perf_data_in_list in perfdata_list:
            if perf_data_in_list.name == str(name):
                perf_data_in_list.extra = str(extra)

    def add_perfdata_tag(self, perf_name, tag_name, tag_value):

        global perfdata_list

        keyword_exist = False

        for perf_data_in_list in perfdata_list:
            if perf_data_in_list.name == str(perf_name) or str(perf_name) == "all":
                perf_data_in_list.custom_tags[str(tag_name)] = str(tag_value)
                keyword_exist = True

        if keyword_exist is False:
            raise Exception("The keyword name does not exist")

    def add_perfdata_field(self, perf_name, field_name, field_value):

        global perfdata_list

        keyword_exist = False

        for perf_data_in_list in perfdata_list:
            if perf_data_in_list.name == str(perf_name) or str(perf_name) == "all":
                perf_data_in_list.custom_fields[str(field_name)] = str(field_value)
                keyword_exist = True

        if keyword_exist is False:
            raise Exception("The keyword name does not exist")

    def get_perfdata(self, name, delete_perfdata=False):

        keyword_exist = False

        global perfdata_list
        ret_val = None
        perfdata_list_copy = copy.deepcopy(perfdata_list)

        cnt = 0
        for perf_data_in_list in perfdata_list:
            if perf_data_in_list.name == name:

                keyword_exist = True

                if perf_data_in_list.value == "" or perf_data_in_list.value is None:
                    raise Exception('The performance measure is None')

                if delete_perfdata is True:
                    del perfdata_list_copy[cnt]

                ret_val = perf_data_in_list.value
            cnt = cnt + 1

        perfdata_list = copy.deepcopy(perfdata_list_copy)
        perfdata_list_copy = []

        if keyword_exist is False:
            raise Exception("The keyword name does not exist")

        return ret_val

    def get_all_perfdata(self):
        global perfdata_list
        return copy.deepcopy(perfdata_list)

    def delete_perfdata(self, name):

        global perfdata_list

        perfdata_list_copy = copy.deepcopy(perfdata_list)

        cnt = 0
        for perf_data_in_list in perfdata_list:
            if perf_data_in_list.name == name:

                del perfdata_list_copy[cnt]

            cnt = cnt + 1

        perfdata_list = copy.deepcopy(perfdata_list_copy)
        perfdata_list_copy = []

    def sum_perfdata(self, *names, **kwargs):

        global perfdata_list

        sum = None

        value_to_sum = []
        index_to_delete = []
        perfdata_list_copy = []

        delete_perf = False
        perf_name = ""
        warning_threshold  = None
        critical_threshold = None

        try:
            delete_perf = kwargs['delete_perfdata']
        except:
            pass

        try:
            perf_name = kwargs['name']
        except:
            pass

        try:
            warning_threshold = float(kwargs['warning_threshold'])
        except:
            pass

        try:
            critical_threshold = float(kwargs['critical_threshold'])
        except:
            pass

        biggest_timestamp = 0
        smallest_timestamp = 10413792000000 #2300/01/01
        value_of_last_perf = None
        timeout_of_last_perf = None

        all_name_exist = True




        for name in names:
            name_exists = False
            for perf_data_in_list in perfdata_list:
                if perf_data_in_list.name == name:
                    name_exists = True

            if name_exists is False:
                raise Exception("The keyword name (" + name + ") does not exist")

        cnt = 0
        for perf_data_in_list in perfdata_list:

            for name in names:

                if perf_data_in_list.name == name and perf_data_in_list.value != ""\
                        and perf_data_in_list.value is not None:
                    value_to_sum.append(perf_data_in_list.value)
                    sum = 0 #init sum

                    if perf_data_in_list.timestamp is None:
                        raise Exception(name + ": The performance timestamp is None")

                    if perf_data_in_list.timestamp < smallest_timestamp:
                        smallest_timestamp = perf_data_in_list.timestamp

                    if perf_data_in_list.timestamp > biggest_timestamp:
                        biggest_timestamp = perf_data_in_list.timestamp
                        value_of_last_perf = perf_data_in_list.value
                        timeout_of_last_perf = perf_data_in_list.timeout_threshold

                    if delete_perf is True:
                        index_to_delete.append(cnt)

                elif perf_data_in_list.name == name and (perf_data_in_list.value == ""\
                        or perf_data_in_list.value is None):
                    raise Exception("The performance measure (" + name + ") is None")

            cnt = cnt + 1

        cnt = 0
        for perf in perfdata_list:

            if cnt not in index_to_delete:
                perfdata_list_copy.append(perf)

            cnt = cnt + 1

        perfdata_list = copy.deepcopy(perfdata_list_copy)
        perfdata_list_copy = []

        for perf in value_to_sum:

            sum = sum + perf

        if perf_name != "":

            self.add_perfdata(perf_name, sum, warning_threshold, critical_threshold)

            for perf in perfdata_list:
                if perf.name == perf_name:

                    perf.timestamp = smallest_timestamp

                    current_keyword_timestamp_array = self._info_manager.get_info('KEYWORD TIMESTAMP')

                    # current_keyword_timestamp_array_copy = copy.deepcopy(current_keyword_timestamp_array)

                    timestamp_modified = False
                    for cnt_kts in xrange(len(current_keyword_timestamp_array)):
                        if current_keyword_timestamp_array[cnt_kts][0] == perf_name:
                            timestamp_modified = True
                            current_keyword_timestamp_array[cnt_kts] = (perf_name, smallest_timestamp)
                            break

                    if timestamp_modified is False:
                        current_keyword_timestamp_array.append((perf_name, smallest_timestamp))

                    self._info_manager.set_info('KEYWORD TIMESTAMP',
                                                current_keyword_timestamp_array)

                    try:
                        end_timestamp_only_for_summed_perf = (float(biggest_timestamp)/1000) + value_of_last_perf
                        perf.end_timestamp_only_for_summed_perf = int(end_timestamp_only_for_summed_perf*1000)
                    except:
                        try:
                            end_timestamp_only_for_summed_perf = (float(biggest_timestamp)/1000) + timeout_of_last_perf
                            perf.end_timestamp_only_for_summed_perf = int(end_timestamp_only_for_summed_perf*1000)
                        except:
                            perf.end_timestamp_only_for_summed_perf = biggest_timestamp

        return sum

    def get_last_filled(self):
        #self.order_perfdata()
        return self._last_filled_perf

    def order_perfdata(self):
        global perfdata_list
        perfdata_ok_list = []
        perfdata_notok_list = []

        for perf_data_in_list in perfdata_list:

            if perf_data_in_list.counter != -1:
                perfdata_ok_list.append(copy.deepcopy(perf_data_in_list))
            else:
                perfdata_notok_list.append(copy.deepcopy(perf_data_in_list))
                self.not_ok_perfdata = self.not_ok_perfdata + 1

        perfdata_ok_list.sort(key=lambda x: x.counter, reverse=False)

        if len(perfdata_ok_list) > 0:
            self._last_filled_perf = perfdata_ok_list[-1].name

        perfdata_list = []
        perfdata_list = perfdata_ok_list + perfdata_notok_list

    def get_perfdata_string(self):

        global perfdata_list

        ret_string = ""
        cnt = 0
        for perfdata in perfdata_list:

            name = perfdata.name

            if perfdata.value == '' or perfdata.value is None:
                value = ''
            else:
                value = ("%.3f" % perfdata.value)

            if perfdata.warning_threshold == '' or perfdata.warning_threshold is None:
                warning = ''
            else:
                warning = ("%.3f" % perfdata.warning_threshold)

            if perfdata.critical_threshold == '' or perfdata.critical_threshold is None:
                critical = ''
            else:
                critical = ("%.3f" % perfdata.critical_threshold)

            if cnt == 0:
                ret_string = ret_string + name + "=" + value + "s;" + warning + ";" + critical + ";;"
            else:
                ret_string = ret_string + " " + name + "=" + value + "s;" + warning + ";" + critical + ";;"

            cnt = cnt + 1

        return ret_string.replace("=s;;;;","=;;;;")

    def get_output(self, message=None, print_output=True):

        prefix_robot_framework = ""

        global perf_counter
        global declaration_counter
        global perfdata_list
        global timedout_finders

        self.order_perfdata()

        exitcode = self.get_exitcode()
        performanceData = self.get_perfdata_string()

        if performanceData is not "":
            performanceData = "|" + performanceData
        else:
            performanceData = ""

        if self._info_manager.get_info("RESOLUTION BGS OK") is False:
            self.performance_desc_string = self.performance_desc_string + \
               "Alyvix Background Service is installed but the screen resolution doesn't match with the config file"\
               + performanceData + os.linesep

        elif message is not None:
            self.performance_desc_string = self.performance_desc_string + message + performanceData + os.linesep
        elif exitcode == 3 and self.not_ok_perfdata == len(perfdata_list):
            self.performance_desc_string = self.performance_desc_string + \
                                           "UNKNOWN: some error occurred, no measure was taken" + \
                                           performanceData + os.linesep
            prefix_robot_framework = "*WARN*"
        elif exitcode == 3 and self.not_ok_perfdata > 0:
            self.performance_desc_string = self.performance_desc_string + \
                                           "UNKNOWN: one transaction breaks the test case, the last received measure is " + \
                                           self._last_filled_perf + " " + performanceData + os.linesep
            prefix_robot_framework = "*WARN*"
        elif exitcode == 2 and self.not_ok_perfdata == len(perfdata_list):
            self.performance_desc_string = self.performance_desc_string + \
                                           "CRITICAL: some error occurred, no measure was taken" + \
                                           performanceData + os.linesep
            prefix_robot_framework = "*WARN*"
        elif exitcode == 2 and self.not_ok_perfdata > 0:
            self.performance_desc_string = self.performance_desc_string +\
                                               "CRITICAL: one transaction breaks the test case, the last received measure is " +\
                                               self._last_filled_perf + " " + performanceData + os.linesep
            prefix_robot_framework = "*WARN*"
        elif exitcode == 2:
            self.performance_desc_string = self.performance_desc_string +\
                                           "CRITICAL: one or more transactions run critical" +\
                                           performanceData + os.linesep
            prefix_robot_framework = "*WARN*"
        elif exitcode == 1 and self.not_ok_perfdata == len(perfdata_list):
            self.performance_desc_string = self.performance_desc_string + \
                                           "WARNING: some error occurred, no measure was taken" + \
                                           performanceData + os.linesep
            prefix_robot_framework = "*WARN*"
        elif exitcode == 1 and self.not_ok_perfdata > 0:
            self.performance_desc_string = self.performance_desc_string +\
                                               "WARNING: one transaction breaks the test case, the last received measure is " +\
                                               self._last_filled_perf + " " + performanceData + os.linesep
            prefix_robot_framework = "*WARN*"
        elif exitcode == 1:
            self.performance_desc_string = self.performance_desc_string +\
                                           "WARNING: one or more transactions run in warning" +\
                                           performanceData + os.linesep
            prefix_robot_framework = "*WARN*"
        elif exitcode == 0 and self.not_ok_perfdata == len(perfdata_list):
            self.performance_desc_string = self.performance_desc_string + \
                                           "Ok: some error occurred, no measure was taken" + \
                                           performanceData + os.linesep
        elif exitcode == 0 and self.not_ok_perfdata > 0:
            self.performance_desc_string = self.performance_desc_string +\
                                               "OK: one transaction breaks the test case, the last received measure is " +\
                                               self._last_filled_perf + " " + performanceData + os.linesep
        else:
            self.performance_desc_string = self.performance_desc_string +\
                                           "OK: all transactions run ok" +\
                                           performanceData + os.linesep

        if declaration_counter == 0 and perf_counter == 0:
            self.performance_desc_string = self.performance_desc_string.replace("some error occurred, no measure was taken",
                                                                                "no transaction is declared")

        for perfdata in perfdata_list:

            name = perfdata.name

            if perfdata.value != "" and perfdata.critical_threshold != "" and perfdata.value >= perfdata.critical_threshold:
                perfdata.state = 2
            elif perfdata.value != "" and perfdata.warning_threshold != "" and perfdata.value >= perfdata.warning_threshold:
                perfdata.state = 1
            elif perfdata.value != "":
                perfdata.state = 0

            state = perfdata.state

            if perfdata.value == '' or perfdata.value is None:
                value = perfdata.value
            else:
                value = ("%.3f" % perfdata.value)


            if state == 0 and value == "":
                self.performance_desc_string = self.performance_desc_string +\
                                               "OK: " + name + " measures None" + os.linesep
            elif state == 0:
                self.performance_desc_string = self.performance_desc_string +\
                                               "OK: " + name + " measures " + value + "s" + os.linesep
            elif state == 1 and value == "":
                self.performance_desc_string = self.performance_desc_string +\
                                               "WARNING: " + name + " measures None" + os.linesep
            elif state == 1:
                self.performance_desc_string = self.performance_desc_string +\
                                               "WARNING: " + name + " measures " + value + "s" + os.linesep
            elif state == 2 and value == "":
                self.performance_desc_string = self.performance_desc_string +\
                                               "CRITICAL: " + name + " measures None" + os.linesep
            elif state == 2:
                self.performance_desc_string = self.performance_desc_string + \
                                               "CRITICAL: " + name + " measures " + value + "s" + \
                                               os.linesep
            else:
                self.performance_desc_string = self.performance_desc_string +\
                                                   "UNKNOWN: " + name + " time is null." + os.linesep


        if self._info_manager.get_info("ROBOT CONTEXT") is True:

            suite_source = self._info_manager.get_info("SUITE SOURCE")

            file_name = suite_source.split(os.sep)[-1].split(".")[0]

            result_dir = tempfile.gettempdir() + os.sep + "alyvix_pybot" + os.sep + file_name + os.sep + "result"
        else:
            result_dir = "."

        if not os.path.exists(result_dir):
            os.makedirs(result_dir)

        text_file = open(result_dir + os.sep + "message.txt", "w")
        text_file.write(self.performance_desc_string)
        text_file.close()

        text_file = open(result_dir + os.sep + "exitcode.txt", "w")
        text_file.write(str(exitcode))
        text_file.close()

        if print_output is True:
            print prefix_robot_framework + self.performance_desc_string
        return exitcode

    def get_exitcode(self):

        global perfdata_list

        exitcode = 0

        not_ok_exitcode = None

        for perfdata in perfdata_list:

            if perfdata.value is None or perfdata.value == "":
                if not_ok_exitcode is None:
                    not_ok_exitcode = perfdata.state
                elif perfdata.state > not_ok_exitcode:
                    not_ok_exitcode = perfdata.state


        if len(perfdata_list) == 0 and len(deleted_on_rename_list) != 0:
            perfdata_list = copy.deepcopy(deleted_on_rename_list)

        for perfdata in perfdata_list:

            if perfdata.value is None or perfdata.value == "":
                if perfdata.state > exitcode:
                    exitcode = perfdata.state
            if perfdata.critical_threshold is not None and perfdata.critical_threshold != "":
                if perfdata.value >= int(perfdata.critical_threshold):
                    if 2 > exitcode:
                        exitcode = 2
            if perfdata.warning_threshold is not None and perfdata.warning_threshold != "":
                if perfdata.value >= int(perfdata.warning_threshold):
                    if 1 > exitcode:
                        exitcode = 1

            """
            state = perfdata.state

            if state == 0 and self.not_ok_perfdata == 0:
                #we are in the init step
                if exitcode == 2: #3
                    exitcode = 0
            elif state == 1 or state == 2:
                if exitcode == 2: #3
                    exitcode = state
                elif state > exitcode:
                    exitcode = state

            if exitcode == 2:
                break
            """

        if not_ok_exitcode != None and self.not_ok_perfdata > 0:
            exitcode = not_ok_exitcode

        if self.not_ok_perfdata > 0:
            try:
                exitcode = int(os.getenv("exitcode"))
            except:
                pass

        return exitcode

