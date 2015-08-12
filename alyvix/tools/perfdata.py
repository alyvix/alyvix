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


perfdata_list = []


class _PerfData:

    def __init__(self):
        self.name = None
        self.value = None
        self.warning_threshold = None
        self.critical_threshold = None
        self.exitcode = None


class PerfManager:

    def clear_perfdata(self):
        global perfdata_list
        perfdata_list = []

    def add_perfdata(self, name, value, warning_threshold=None, critical_threshold=None, exitcode=None):

        global perfdata_list

        perf_data = _PerfData()
        perf_data.name = name
        perf_data.value = value
        perf_data.warning_threshold = warning_threshold
        perf_data.critical_threshold = critical_threshold
        perf_data.exitcode = exitcode

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