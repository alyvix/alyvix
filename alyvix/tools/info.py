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

from alyvix.tools.configreader import ConfigReader
from alyvix.tools.screen import ScreenManager
from alyvix.bridge.robot import RobotManager

config_reader = ConfigReader()
robot_manager = RobotManager()
screen_manager = ScreenManager()

_log_folder = None

_dict = {}

class InfoManager():

    def update(self):
        """
        updates all info.
        """

        float_scaling_factor = screen_manager.get_scaling_factor()
        int_scaling_factor = int(round(float_scaling_factor))

        self.set_info('SCALING FACTOR FLOAT', float_scaling_factor)
        self.set_info('SCALING FACTOR INT', int_scaling_factor)

        robot_context = robot_manager.context_is_set()
        self.set_info('ROBOT CONTEXT', robot_context)

        if robot_context:
            self.set_info('SUITE NAME', robot_manager.get_suite_name())
            self.set_info('SUITE SOURCE', robot_manager.get_suite_source())
            self.set_info('TEST CASE NAME', robot_manager.get_testcase_name())
            self.set_info('OUTPUT DIR', robot_manager.get_output_directory())
            self.set_info('LOG LEVEL', robot_manager.get_loglevel())
            self.set_info('LOG ENABLED', True)
        else:
            self.set_info('OUTPUT DIR', config_reader.get_log_folder())
            self.set_info('LOG LEVEL', config_reader.get_loglevel())
            self.set_info('LOG ENABLED', config_reader.get_log_enable_value())

    def tiny_update(self):
        """
        updates only a few necessary info.
        """

        robot_context = self.get_info('ROBOT CONTEXT')

        if robot_context:
            self.set_info('TEST CASE NAME', robot_manager.get_testcase_name())
            self.set_info('LOG LEVEL', robot_manager.get_loglevel())

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

