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
import re
import subprocess

from tools.window.base import WinManagerBase


class WinManager(WinManagerBase):

    def __init__(self):
        pass

    def show_window(self, window_title):
        """
        show window.

        :type window_title: string
        :param window_title: regular expression for the window title
        """
        hwnd_found_list = self._get_hwnd(window_title)
        for hwnd_found in hwnd_found_list:
            subprocess.Popen(["wmctrl", "-i", "-a", hwnd_found], stdout=subprocess.PIPE)

    def maximize_window(self, window_title):
        """
        maximize window(s).

        :type window_title: string
        :param window_title: regular expression for the window(s) title
        """
        hwnd_found_list = self._get_hwnd(window_title)
        for hwnd_found in hwnd_found_list:
            subprocess.Popen(["wmctrl", "-i", "-r", hwnd_found, "-b", "add,maximized_vert,maximized_horz"], stdout=subprocess.PIPE)
            subprocess.Popen(["wmctrl", "-i", "-a", hwnd_found], stdout=subprocess.PIPE)

    def maximize_foreground_window(self):
        """
        maximize foreground window.
        """
        proc = subprocess.Popen(["xprop", "-root", "_NET_ACTIVE_WINDOW"], stdout=subprocess.PIPE)
        out, err = proc.communicate()
        foreground_id = out.split(' ')[-1]
        subprocess.Popen(["wmctrl", "-i", "-r", foreground_id, "-b", "add,maximized_vert,maximized_horz"], stdout=subprocess.PIPE)

    def check_if_window_exists(self, window_title):
        """
        check if window(s) exist.

        :type window_title: string
        :param window_title: regular expression for the window(s) title
        """
        hwnd_found_list = self._get_hwnd(window_title)
        if len(hwnd_found_list) > 0:
            return True
        else:
            return False

    def close_window(self, window_title):
        """
        close window(s).

        :type window_title: string
        :param window_title: regular expression for the window(s) title
        """
        hwnd_found_list = self._get_hwnd(window_title)
        for hwnd_found in hwnd_found_list:
            subprocess.Popen(["wmctrl", "-i", "-c", hwnd_found], stdout=subprocess.PIPE)

    def _get_hwnd(self, window_title):

        hwnd_list = []

        proc = subprocess.Popen(["wmctrl", "-l"], stdout=subprocess.PIPE)
        out, err = proc.communicate()

        lines = out.split(os.linesep)

        for line in lines:
            if re.match(".*" + window_title + ".*", line, re.DOTALL | re.IGNORECASE) is not None:
                hwnd_list.append(line.split(' ')[0])

        return hwnd_list