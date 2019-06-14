
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

from alyvix.tools.screen import ScreenManager

class MouseManagerBase(object):

    def __init__(self):
        self.left_button = 1
        self.right_button = 2
        self.middle_button = 3
        self.wheel_up = 4
        self.wheel_down = 5
        self.wheel_left = 6
        self.wheel_right = 7

        sm = ScreenManager()

        self._scaling_factor = sm.get_scaling_factor()

    def click(self, x, y, button=1, n=1):
        raise NotImplementedError

    def move(self, x, y):
        raise NotImplementedError

    def scroll(self, step, direction):
        raise NotImplementedError

    def drag(self, x1, y1, x2, y2, button=1):
        raise NotImplementedError