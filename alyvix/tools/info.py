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

from .configreader import ConfigReader
from .screen import ScreenManager
import time

config_reader = ConfigReader()
screen_manager = ScreenManager()

_log_folder = None

_dict = {}

robot_log_deleted = False

class InfoManager():

    def update(self):
        """
        updates all info.
        """

        self.set_info('START TIME', int(time.time()))

        self.set_info('WAIT FINISH', None)
        self.set_info('DISAPP START', None)

        self.set_info('KEYWORD TIMESTAMP', [])

        self.set_info('KEYWORD TIMEOUT', [])

        self.set_info('channel', 'all')

        float_scaling_factor = screen_manager.get_scaling_factor()
        int_scaling_factor = int(round(float_scaling_factor))

        self.set_info('SCALING FACTOR FLOAT', float_scaling_factor)
        self.set_info('SCALING FACTOR INT', int_scaling_factor)

        if self.get_info("SCALING FACTOR ONE TIME") is None:
            self.set_info('SCALING FACTOR ONE TIME', float_scaling_factor)

        self.set_info('FINDER THREAD INTERVAL', config_reader.get_finder_thread_interval())
        self.set_info('FINDER THREAD INTERVAL DISAPPEAR', config_reader.get_finder_thread_interval_disappear())
        self.set_info('CHECK DIFF INTERVAL', config_reader.get_finder_diff_interval())
        self.set_info('CHECK DIFF INTERVAL DISAPPEAR', config_reader.get_finder_diff_interval_disappear())

        self.set_info("OVERWRITE LOG IMAGES", False)

        self.set_info('OVERLAPPING TOLERANCE FACTOR', 10)

        self.set_info('ACTIONS DELAY', 0.5)

        self.set_info('last log image order', 0)

        self.set_info('LOG OBJ FINDER FILL COLOR',
                              [(0, 0, 255), (0, 255, 255), (0, 255, 0), (255, 255, 0), (255, 0, 0), (255, 0, 255)])

        self.set_info('LOG OBJ FINDER BORDER COLOR',
                              [(0, 0, 255), (0, 255, 255), (0, 255, 0), (255, 255, 0), (255, 0, 0), (255, 0, 255)])

        self.set_info('LOG OBJ FINDER COLOR COUNTER', 0)

        self.set_info('LOG OBJ FINDER TYPE', None)

        self.set_info('LOG OBJ IS FOUND', False)

        self.set_info('GIF FRAME TIMING', 2)

        self.set_info('CHECK BG', config_reader.get_bg_res_check())

        self.set_info('RESOLUTION BGS OK', True)

        self.set_info('TS NAME', [])

        self.set_info('SCRAPER COLLECTION', [])

        self.set_info("DISABLE REPORTS", False)

        self.set_info("RESOLUTION", screen_manager.get_resolution())

        #self.set_info("INTERACTION", [])


        self.set_info('OUTPUT DIR', config_reader.get_log_folder())
        self.set_info('LOG LEVEL', config_reader.get_loglevel())
        self.set_info('LOG ENABLED', config_reader.get_log_enable_value())

    def tiny_update(self):
        pass

    def set_info(self, name, value):
        """
        set an info.

        :type name: string
        :param name: the name of the info
        :type value: all kind
        :param value: the value of the info
        """
        global _dict
        _dict[name] = value

    def get_info(self, name):
        """
        get an info.

        :type name: string
        :param name: the name of the info
        :type value: all kind
        :param value: the value of the info
        """
        global _dict

        try:
            return _dict[name]
        except:
            return None

    def set_robot_log_deleted_flag(self, value):
        global robot_log_deleted
        robot_log_deleted = value


    def get_robot_log_deleted_flag(self):
        global robot_log_deleted
        return robot_log_deleted
