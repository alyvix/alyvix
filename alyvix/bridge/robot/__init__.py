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

import robot.api.logger


class RobotManager():

    def __init__(self):

        self._data = None

        if robot.api.logger.EXECUTION_CONTEXTS.current is not None:
            self._data = robot.api.logger.EXECUTION_CONTEXTS.current.variables.current.store.data

    def context_is_set(self):
        """
        check if Alyvix is running inside a robotframework session.

        :rtype: bool
        :return: returns True if robotframework has run this session, False otherwise
        """

        if robot.api.logger.EXECUTION_CONTEXTS.current is None:
            return False
        else:
            return True

    def get_output_directory(self):
        """
        get the output directory of robotframework logs.

        :rtype: string
        :return: the log directory of robotframework
        """

        if self._data is not None:
            output_directory = str(self._data["OUTPUT_DIR"])
        else:
            output_directory = None

        return output_directory

    def get_suite_name(self):
        """
        get the project name of current robotframework session.

        :rtype: string
        :return: the robotframework project name
        """

        if self._data is not None:
            suite_name = str(self._data["SUITE_NAME"])
        else:
            suite_name = None

        return suite_name

    def get_suite_source(self):
        """
        get the project name of current robotframework session.

        :rtype: string
        :return: the robotframework project name
        """

        if self._data is not None:
            suite_source = str(self._data["SUITE_SOURCE"])
        else:
            suite_source = None

        return suite_source

    def get_testcase_name(self):
        """
        get the testcase name of current robotframework session.

        :rtype: string
        :return: the robotframework project name
        """

        test_name = None

        if self._data is not None:
            try:
                test_name = str(self._data["TEST_NAME"])
            except:
                pass

        return test_name

    def get_loglevel(self):
        """
        get the log level of current robotframework session.

        :rtype: string
        :return: the log level
        """

        if self._data is not None:
            log_level = str(self._data["LOG_LEVEL"])
        else:
            log_level = None

        return log_level

    def write_log_message(self, message, level='INFO', html=False):
        """
        Writes the message to the log file using the given level.

        Valid log levels are ``TRACE``, ``DEBUG``, ``INFO`` and ``WARN``.

        :type message: string
        :param message: a string containing the message
        :type level: string
        :param level: a string containing the log level
        :type html: bool
        :param html: set it True if the message is an html string
        """

        robot.api.logger.write(message, level, html)

