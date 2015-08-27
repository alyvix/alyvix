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
        self.save = os.dup(1), os.dup(2)
        self.null_fds = [os.open(os.devnull, os.O_RDWR) for x in xrange(2)]
        self.performance_desc_string = ""


    def clear_perfdata(self):
        global perfdata_list
        perfdata_list = []

    def add_perfdata(self, name, value, warning_threshold=None, critical_threshold=None, state=0):

        global perfdata_list

        perf_data = _PerfData()
        perf_data.name = name
        perf_data.value = value
        perf_data.warning_threshold = warning_threshold
        perf_data.critical_threshold = critical_threshold

        if state is None:
            perf_data.state = 3
        else:
            perf_data.state = int(state)

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

    def get_output(self, message=None):

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
        elif exitcode == 1:
            self.performance_desc_string = self.performance_desc_string +\
                                           "WARNING: one or more steps are in warning state" +\
                                           performanceData + os.linesep
        elif exitcode == 3:
            self.performance_desc_string = self.performance_desc_string +\
                                           "UNKNOWN: some unknown error occured" +\
                                           performanceData + os.linesep
        elif len(timedout_finders) > 0:
            self.performance_desc_string = self.performance_desc_string +\
                                           "CRITICAL: one or more steps are in timeout state" +\
                                           performanceData + os.linesep
        else:
            self.performance_desc_string = self.performance_desc_string +\
                                           "OK: all steps are ok" +\
                                           performanceData + os.linesep

        for perfdata in perfdata_list:

            name = perfdata.name
            value = perfdata.value
            warning = perfdata.warning_threshold
            critical = perfdata.critical_threshold
            state = perfdata.state

            #only for Alyvix
            if critical is not None and perfdata.value >= critical:
                state = 2
            elif warning is not None and perfdata.value >= warning:
                state = 1

            if state == 0:
                self.performance_desc_string = self.performance_desc_string +\
                                               "OK: " + name + " time is " + str(value) + " sec." + os.linesep
            elif state == 1:
                self.performance_desc_string = self.performance_desc_string +\
                                               "WARNING: " + name + " time is " + str(value) + " sec." + os.linesep
            elif state == 2:
                if value is not None:
                    self.performance_desc_string = self.performance_desc_string +\
                                                   "CRITICAL: " + name + " time is " + str(value) + " sec." +\
                                                   os.linesep
                else:
                    self.performance_desc_string = self.performance_desc_string +\
                                                   "CRITICAL: " + name + " time is null." + os.linesep
            else:
                if value is not None:
                    self.performance_desc_string = self.performance_desc_string +\
                                                   "UNKNOWN: " + name + " time is " + str(value) + " sec." + os.linesep
                else:
                    self.performance_desc_string = self.performance_desc_string +\
                                                   "UNKNOWN: " + name + " time is null." + os.linesep


        os.environ["alyvix_exitcode"] = str(exitcode)
        os.environ["alyvix_std_output"] = self.performance_desc_string

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
            if critical is not None and perfdata.value >= critical:
                state = 2
            elif warning is not None and perfdata.value >= warning:
                state = 1

            if state > exitcode:
                exitcode = state

            if exitcode == 2:
                break

        return exitcode

    def disable_console_output(self):
        # open 2 fds
        self.null_fds = [os.open(os.devnull, os.O_RDWR) for x in xrange(2)]
        # save the current file descriptors to a tuple
        self.save = os.dup(1), os.dup(2)
        # put /dev/null fds on 1 and 2
        os.dup2(self.null_fds[0], 1)
        os.dup2(self.null_fds[1], 2)


    def enable_console_output(self):
        os.dup2(self.save[0], 1)
        os.dup2(self.save[1], 2)
        # close the temporary fds
        os.close(self.null_fds[0])
        os.close(self.null_fds[1])

