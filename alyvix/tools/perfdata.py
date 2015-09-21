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

perfdata_list = []
timedout_finders = []


class _PerfData:

    def __init__(self):
        self.name = None
        self.value = None
        self.warning_threshold = None
        self.critical_threshold = None
        self.state = 0


class PerfManager:

    def __init__(self):
        self.performance_desc_string = ""

    def clear_perfdata(self):
        global perfdata_list
        perfdata_list = []

    def add_perfdata(self, name, value=None, warning_threshold=None, critical_threshold=None, state=0):

        global perfdata_list

        perf_data = _PerfData()
        perf_data.name = name

        try:
            perf_data.value = float(value)
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

        try:
            perf_data.state = int(state)
        except:
             perf_data.state = 3

        cnt = 0
        for perf_data_in_list in perfdata_list:
            if perf_data_in_list.name == perf_data.name:

                perfdata_list[cnt] = perf_data
                return

            cnt = cnt + 1

        perfdata_list.append(perf_data)

    def get_perfdata_string(self):

        global perfdata_list

        ret_string = ""
        cnt = 0
        for perfdata in perfdata_list:

            name = perfdata.name
            value = perfdata.value
            warning = perfdata.warning_threshold
            critical = perfdata.critical_threshold

            if cnt == 0:
                ret_string = ret_string + name + "=" + str(value) + "s;" + str(warning) + ";" + str(critical) + ";;"
            else:
                ret_string = ret_string + " " + name + "=" + str(value) + "s;" + str(warning) + ";" + str(critical) + ";;"

            cnt = cnt + 1

        return ret_string

    def get_output(self, message=None, print_output=True):

        prefix_robot_framework = ""

        global perfdata_list
        global timedout_finders

        exitcode = self.get_exitcode()
        performanceData = self.get_perfdata_string()

        if performanceData is not "":
            performanceData = "|" + performanceData
        else:
            performanceData = ""

        if message is not None:
            self.performance_desc_string = self.performance_desc_string + message + performanceData + os.linesep
        elif exitcode == 2:
            self.performance_desc_string = self.performance_desc_string +\
                                           "CRITICAL: one or more steps are in critical state" +\
                                           performanceData + os.linesep
            prefix_robot_framework = "*WARN*"
        elif exitcode == 1:
            self.performance_desc_string = self.performance_desc_string +\
                                           "WARNING: one or more steps are in warning state" +\
                                           performanceData + os.linesep
            prefix_robot_framework = "*WARN*"
        elif exitcode == 3:
            self.performance_desc_string = self.performance_desc_string +\
                                           "UNKNOWN: some unknown error occurred" +\
                                           performanceData + os.linesep
            prefix_robot_framework = "*WARN*"
        elif len(timedout_finders) > 0:
            self.performance_desc_string = self.performance_desc_string +\
                                           "CRITICAL: one or more steps are in timeout state" +\
                                           performanceData + os.linesep
            prefix_robot_framework = "*WARN*"
        else:
            self.performance_desc_string = self.performance_desc_string +\
                                           "OK: all steps are ok" +\
                                           performanceData + os.linesep

        for perfdata in perfdata_list:

            name = perfdata.name
            value = perfdata.value
            warning = perfdata.warning_threshold
            critical = perfdata.critical_threshold
            #state = perfdata.state

            #only for Alyvix
            state = 3
            if value != "" and critical != "" and value >= critical:
                state = 2
            elif value != "" and warning != "" and value >= warning:
                state = 1
            elif value != "":
                state = 0
            elif value == "" and warning == "" and critical == "" and state == 0:
                state = 3

            if state == 0:
                self.performance_desc_string = self.performance_desc_string +\
                                               "OK: " + name + " time is " + str(value) + " sec." + os.linesep
            elif state == 1:
                self.performance_desc_string = self.performance_desc_string +\
                                               "WARNING: " + name + " time is " + str(value) + " sec." + os.linesep
            elif state == 2:
                self.performance_desc_string = self.performance_desc_string +\
                                               "CRITICAL: " + name + " time is " + str(value) + " sec." +\
                                               os.linesep
            else:
                if value != "":
                    self.performance_desc_string = self.performance_desc_string +\
                                                   "UNKNOWN: " + name + " time is " + str(value) + " sec." + os.linesep
                elif value == "":
                    self.performance_desc_string = self.performance_desc_string +\
                                                   "UNKNOWN: " + name + " time is null." + os.linesep


        os.environ["alyvix_exitcode"] = str(exitcode)
        os.environ["alyvix_std_output"] = self.performance_desc_string

        if print_output is True:
            print prefix_robot_framework + self.performance_desc_string
        return exitcode

    def get_exitcode(self):

        global perfdata_list
        exitcode = 0

        for perfdata in perfdata_list:

            name = perfdata.name
            value = perfdata.value
            warning = perfdata.warning_threshold
            critical = perfdata.critical_threshold
            state = perfdata.state

            #only for Alyvix
            if value != "" and critical != "" and value >= critical:
                state = 2
            elif value != "" and warning != "" and value >= warning:
                state = 1
            elif value == "" and warning == "" and critical == "" and state == 0:
                state = 3

            if state > exitcode:
                exitcode = state

            if exitcode == 2:
                break

        return exitcode

