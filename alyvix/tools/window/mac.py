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
        pass

    def maximize_window(self, window_title):
        """
        maximize window(s).

        :type window_title: string
        :param window_title: regular expression for the window(s) title
        """

    def maximize_foreground_window(self):
        """
        maximize foreground window.
        """
        pass

    def check_if_window_exists(self, window_title):
        """
        check if window(s) exist.

        :type window_title: string
        :param window_title: regular expression for the window(s) title
        """
        pass

    def close_window(self, window_title):
        """
        close window(s).

        :type window_title: string
        :param window_title: regular expression for the window(s) title
        """
        pass

    def _get_hwnd(self, window_title):
        pass