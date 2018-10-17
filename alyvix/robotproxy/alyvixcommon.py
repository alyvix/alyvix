# -*- coding: utf-8 -*-
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
from distutils.sysconfig import get_python_lib
from alyvix.devices.keyboard import KeyboardManager
from alyvix.devices.mouse import MouseManager
from alyvix.finders.cv.rectfinder import RectFinder
from alyvix.finders.cv.imagefinder import ImageFinder
from alyvix.finders.cv.textfinder import TextFinder
from alyvix.finders.cv.objectfinder import ObjectFinder
from alyvix.tools.perfdata import PerfManager
from alyvix.tools.process import ProcManager
from alyvix.tools.window import WinManager
from alyvix.tools.info import InfoManager
from alyvix.tools.screen import ScreenManager
from alyvix.tools.db import DbManager
from alyvix.tools.network_analyzer import NetManager
from alyvix.tools.scraped_strings import JSONManager
from alyvix.tools.scraped_strings import StringManager
from alyvix.tools.scraped_strings import CalendarWatchManager