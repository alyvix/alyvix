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
from os.path import expanduser
import xml.dom.minidom as minidom
from distutils.sysconfig import get_python_lib

class ConfigReader():

    def __init__(self):

        file_handler_global = None
        file_handler_user = None
        xml_doc_global = None
        xml_doc_user = None
        self.__global_root_node = None
        self.__user_root_node = None
        self.__testcase_root_node = None

        self.__global_config_filename = self.get_global_config_filename()
        self.__user_config_filename = self.get_user_config_filename()
        self.__testcase_config_filename = self.get_testcase_config_filename()

        try:
            file_handler_global = open(self.__global_config_filename, "r")
            xml_doc_global = minidom.parse(file_handler_global)
            self.__global_root_node = xml_doc_global.getElementsByTagName("config")[0]
        except:
            self.__global_root_node = None

        try:
            file_handler_user = open(self.__user_config_filename, "r")
            xml_doc_user = minidom.parse(file_handler_user)
            self.__user_root_node = xml_doc_user.getElementsByTagName("config")[0]
            #print self.__user_root_node
        except:
            #print Exception, err
            self.__user_root_node = None

        try:
            file_handler_testcase = open(self.__testcase_config_filename, "r")
            xml_doc_testcase = minidom.parse(file_handler_testcase)
            self.__testcase_root_node = xml_doc_testcase.getElementsByTagName("config")[0]
        except:
            self.__testcase_root_node = None

    def get_global_config_filename(self):
        """
        get the fullname of configuration file.

        :rtype: string
        :return: full filename
        """
        try:
            #global_config_file_name = os.getenv("ALYVIX_HOME") + os.sep + "config.xml"
            global_config_file_name = get_python_lib() + os.sep + "alyvix" + os.sep + "config.xml"
            return global_config_file_name
        except:
            return ""

    def get_user_config_filename(self):
        """
        get the fullname of configuration file inside user home dir.

        :rtype: string
        :return: full filename
        """
        user_config_filename = expanduser("~") + os.sep + "alyvix" + os.sep + "config.xml"
        return user_config_filename

    def get_testcase_config_filename(self):
        """
        get the fullname of configuration file inside testcase dir.

        :rtype: string
        :return: full filename
        """
        testcase_config_filename = os.getenv("alyvix_testcase_config")
        #print testcase_config_filename
        return testcase_config_filename

    def get_finder_thread_interval(self):
        """
        get the interval between finder threads.
        this value will be used by the wait method of a finder object.

        :rtype: float
        :return: thread interval
        """

        thread_interval = None

        try:
            finder_node = self.__testcase_root_node.getElementsByTagName("finder")[0]
            thread_interval = float(finder_node.getElementsByTagName("finder_thread_interval")[0].firstChild.nodeValue)
        except:
            thread_interval = None

        if thread_interval is None:
            try:
                finder_node = self.__user_root_node.getElementsByTagName("finder")[0]
                thread_interval = float(finder_node.getElementsByTagName("finder_thread_interval")[0].firstChild.nodeValue)
            except:
                thread_interval = None

        if thread_interval is None:
            try:
                finder_node = self.__global_root_node.getElementsByTagName("finder")[0]
                thread_interval = float(finder_node.getElementsByTagName("finder_thread_interval")[0].firstChild.nodeValue)
            except:
                thread_interval = 0.5 #2.0

        return thread_interval

    def get_finder_diff_interval(self):
        """
        get the interval between calls to the method that look for difference.
        this value indicates the time of each wait loop step.
        default value is 250ms.

        :rtype: float
        :return: time of a wait loop step
        """

        diff_interval = None

        try:
            finder_node = self.__testcase_root_node.getElementsByTagName("finder")[0]
            diff_interval = float(finder_node.getElementsByTagName("check_diff_interval")[0].firstChild.nodeValue)
        except:
            diff_interval = None

        if diff_interval is None:
            try:
                finder_node = self.__user_root_node.getElementsByTagName("finder")[0]
                diff_interval = float(finder_node.getElementsByTagName("check_diff_interval")[0].firstChild.nodeValue)
            except:
                diff_interval = None

        if diff_interval is None:
            try:
                finder_node = self.__global_root_node.getElementsByTagName("finder")[0]
                diff_interval = float(finder_node.getElementsByTagName("check_diff_interval")[0].firstChild.nodeValue)
            except:
                diff_interval = 0.1 #0.25

        return diff_interval

    def get_finder_thread_interval_disappear(self):
        """
        get the interval between finder threads.
        this value will be used by the wait method of a finder object.

        :rtype: float
        :return: thread interval
        """

        thread_interval = None

        try:
            finder_node = self.__testcase_root_node.getElementsByTagName("finder")[0]
            thread_interval = float(finder_node.getElementsByTagName("finder_thread_interval_disappear")[0].firstChild.nodeValue)
        except:
            thread_interval = None

        if thread_interval is None:
            try:
                finder_node = self.__user_root_node.getElementsByTagName("finder")[0]
                thread_interval = float(finder_node.getElementsByTagName("finder_thread_interval_disappear")[0].firstChild.nodeValue)
            except:
                thread_interval = None

        if thread_interval is None:
            try:
                finder_node = self.__global_root_node.getElementsByTagName("finder")[0]
                thread_interval = float(finder_node.getElementsByTagName("finder_thread_interval_disappear")[0].firstChild.nodeValue)
            except:
                thread_interval = 0.5 #2.0

        return thread_interval

    def get_finder_diff_interval_disappear(self):
        """
        get the interval between calls to the method that look for difference.
        this value indicates the time of each wait loop step.
        default value is 250ms.

        :rtype: float
        :return: time of a wait loop step
        """

        diff_interval = None

        try:
            finder_node = self.__testcase_root_node.getElementsByTagName("finder")[0]
            diff_interval = float(finder_node.getElementsByTagName("check_diff_interval_disappear")[0].firstChild.nodeValue)
        except:
            diff_interval = None

        if diff_interval is None:
            try:
                finder_node = self.__user_root_node.getElementsByTagName("finder")[0]
                diff_interval = float(finder_node.getElementsByTagName("check_diff_interval_disappear")[0].firstChild.nodeValue)
            except:
                diff_interval = None

        if diff_interval is None:
            try:
                finder_node = self.__global_root_node.getElementsByTagName("finder")[0]
                diff_interval = float(finder_node.getElementsByTagName("check_diff_interval_disappear")[0].firstChild.nodeValue)
            except:
                diff_interval = 0.1 #0.25

        return diff_interval
    
    def get_finder_wait_timeout(self):
        """
        get the timeout of the wait method.
        default value is 15 sec.

        :rtype: float
        :return: timeout value
        """

        timeout_value = None

        try:
            finder_node = self.__testcase_root_node.getElementsByTagName("finder")[0]
            timeout_value = float(finder_node.getElementsByTagName("wait_timeout")[0].firstChild.nodeValue)
        except:
            timeout_value = None

        if timeout_value is None:
            try:
                finder_node = self.__user_root_node.getElementsByTagName("finder")[0]
                timeout_value = float(finder_node.getElementsByTagName("wait_timeout")[0].firstChild.nodeValue)
            except:
                timeout_value = None

        if timeout_value is None:
            try:
                finder_node = self.__global_root_node.getElementsByTagName("finder")[0]
                timeout_value = float(finder_node.getElementsByTagName("wait_timeout")[0].firstChild.nodeValue)
            except:
                timeout_value = 20.0

        return timeout_value

    def get_bg_res_check(self):
        """
        get the value of alyvix background resolution check section
        default value is True.

        :rtype: bool
        :return: True or False
        """

        timeout_value = None

        try:
            finder_node = self.__testcase_root_node.getElementsByTagName("finder")[0]
            if finder_node.getElementsByTagName("bg_res_check")[0].firstChild.nodeValue.lower() == "false":
                bg_res_check_value = False
            elif finder_node.getElementsByTagName("bg_res_check")[0].firstChild.nodeValue.lower() == "true":
                bg_res_check_value = True
            else:
                bg_res_check_value = None
        except:
            bg_res_check_value = None

        if bg_res_check_value is None:
            try:
                finder_node = self.__user_root_node.getElementsByTagName("finder")[0]
                if finder_node.getElementsByTagName("bg_res_check")[0].firstChild.nodeValue.lower() == "false":
                    bg_res_check_value = False
                elif finder_node.getElementsByTagName("bg_res_check")[0].firstChild.nodeValue.lower() == "true":
                    bg_res_check_value = True
                else:
                    bg_res_check_value = None
            except:
                bg_res_check_value = None

        if bg_res_check_value is None:
            try:
                finder_node = self.__global_root_node.getElementsByTagName("finder")[0]
                if finder_node.getElementsByTagName("bg_res_check")[0].firstChild.nodeValue.lower() == "false":
                    bg_res_check_value = False
                elif finder_node.getElementsByTagName("bg_res_check")[0].firstChild.nodeValue.lower() == "true":
                    bg_res_check_value = True
                else:
                    bg_res_check_value = None
            except:
                bg_res_check_value = True

        return bg_res_check_value

    def get_log_folder(self):
        """
        get the log home folder.
        default value is a sub folder (log) inside current directory.

        :rtype: string
        :return: log home folder
        """

        log_folder = None

        try:
            log_node = self.__testcase_root_node.getElementsByTagName("log")[0]
            log_folder = str(log_node.getElementsByTagName("home")[0].firstChild.nodeValue)
        except:
            log_folder = None

        if log_folder is None:
            try:
                log_node = self.__user_root_node.getElementsByTagName("log")[0]
                log_folder = str(log_node.getElementsByTagName("home")[0].firstChild.nodeValue)
            except:
                log_folder = None

        if log_folder is None:
            try:
                log_node = self.__global_root_node.getElementsByTagName("log")[0]
                log_folder = str(log_node.getElementsByTagName("home")[0].firstChild.nodeValue)
            except:
                log_folder = "log"

        return log_folder

    def get_log_enable_value(self):
        """
        get the enable value node of log section inside the configuration file.
        default value is True.

        :rtype: bool
        :return: log enabled flag
        """

        log_enabled = None

        try:
            log_node = self.__testcase_root_node.getElementsByTagName("log")[0]
            log_enabled = str(log_node.getElementsByTagName("enable")[0].firstChild.nodeValue)
        except:
            log_enabled = None

        if log_enabled is None:
            try:
                log_node = self.__user_root_node.getElementsByTagName("log")[0]
                log_enabled = str(log_node.getElementsByTagName("enable")[0].firstChild.nodeValue)
            except:
                log_enabled = None

        if log_enabled is None:
            try:
                log_node = self.__global_root_node.getElementsByTagName("log")[0]
                log_enabled = str(log_node.getElementsByTagName("enable")[0].firstChild.nodeValue)
            except:
                log_enabled = "false"

        if log_enabled.lower() == "true":
            log_enabled = True
        elif log_enabled.lower() == "false":
            log_enabled = False

        return log_enabled

    def get_loglevel(self):
        """
        get the enable value node of log section inside the configuration file.
        default value is True.

        :rtype: bool
        :return: log enabled flag
        """

        log_level = None

        try:
            log_node = self.__testcase_root_node.getElementsByTagName("log")[0]
            log_level = str(log_node.getElementsByTagName("level")[0].firstChild.nodeValue)
        except:
            log_level = None

        if log_level is None:
            try:
                log_node = self.__user_root_node.getElementsByTagName("log")[0]
                log_level = str(log_node.getElementsByTagName("level")[0].firstChild.nodeValue)
            except:
                log_level = None

        if log_level is None:
            try:
                log_node = self.__global_root_node.getElementsByTagName("log")[0]
                log_level = str(log_node.getElementsByTagName("level")[0].firstChild.nodeValue)
            except:
                log_level = "ERROR"

        return log_level

    def get_log_max_retention_days(self):
        """
        get the log max retention days.
        default value is 7.

        :rtype: int
        :return: max retention days
        """

        log_enabled = None

        try:
            log_node = self.__testcase_root_node.getElementsByTagName("log")[0]
            retention_node = log_node.getElementsByTagName("retention")[0]
            max_retention_days = int(retention_node.getElementsByTagName("max_days")[0].firstChild.nodeValue)
        except:
            max_retention_days = None

        if max_retention_days is None:
            try:
                log_node = self.__user_root_node.getElementsByTagName("log")[0]
                max_retention_days = int(log_node.getElementsByTagName("max_days")[0].firstChild.nodeValue)
            except:
                max_retention_days = None

        if max_retention_days is None:
            try:
                log_node = self.__global_root_node.getElementsByTagName("log")[0]
                max_retention_days = int(log_node.getElementsByTagName("max_days")[0].firstChild.nodeValue)
            except:
                max_retention_days = 7

        return max_retention_days

    def get_log_hours_per_day(self):
        """
        get the log hours per day retention.
        default value is 24.

        :rtype: int
        :return: max retention days
        """

        log_enabled = None

        try:
            log_node = self.__testcase_root_node.getElementsByTagName("log")[0]
            hours_node = log_node.getElementsByTagName("retention")[0]
            hours_per_day = int(hours_node.getElementsByTagName("hours_per_day")[0].firstChild.nodeValue)
        except:
            hours_per_day = None

        if hours_per_day is None:
            try:
                log_node = self.__user_root_node.getElementsByTagName("log")[0]
                hours_per_day = int(log_node.getElementsByTagName("hours_per_day")[0].firstChild.nodeValue)
            except:
                hours_per_day = None

        if hours_per_day is None:
            try:
                log_node = self.__global_root_node.getElementsByTagName("log")[0]
                hours_per_day = int(log_node.getElementsByTagName("hours_per_day")[0].firstChild.nodeValue)
            except:
                hours_per_day = 24

        return hours_per_day