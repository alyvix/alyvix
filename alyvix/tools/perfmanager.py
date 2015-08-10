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

import cv2
import numpy
import time
import sys

from alyvix.core.cache import CacheManagement
from alyvix.tools.screenmanager import ScreenManager

# System modules
from Queue import Queue
from threading import Thread

perf_data_list = []
perf_data_collected = []


class _PerfData:

    def __init__(self):
        self.name = None
        self.value = None
        self.warning_threshold = None
        self.critical_threshold = None
        self.exitcode = None


class PerfManager:

    def init_perfdata(self, name, value, warning_threshold=None, critical_threshold=None, exitcode=None):
        global perf_data_list

        perf_data = _PerfData()
        perf_data.name = name
        perf_data.value = value
        perf_data.warning_threshold = warning_threshold
        perf_data.critical_threshold = critical_threshold
        perf_data.exitcode = exitcode

        perf_data_list.append(perf_data)

    def add_perfdata_collected(self, name, value, warning_threshold=None, critical_threshold=None, exitcode=None):
        global perf_data_collected

        perf_data = _PerfData()
        perf_data.name = name
        perf_data.value = value
        perf_data.warning_threshold = warning_threshold
        perf_data.critical_threshold = critical_threshold
        perf_data.exitcode = exitcode

        perf_data_collected.append(perf_data)

    def print_perfdata(self, perfdata):
        global perf_data_list
        perf_data_list.append(perfdata)