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
import subprocess


class ProcManagerBase(object):

    def __init__(self):
        self.process = None

    def create_process(self, *popenargs, **kwargs):
        """
        create and run new process.
        The arguments are the same as for the Popen constructor.

        :rtype: subprocess.Popen
        :return: an istance of Popen object
        """
        proc = subprocess.Popen(*popenargs, **kwargs)
        return proc

    def kill_process(self, process_name):
        """
        kill a process.

        :type process_name: string
        :param process_name: the name of the process to kill
        """
        raise NotImplementedError

    def wait_process_close(self, process_name, pid=None, timeout=60):
        """
        wait process(es) till exists.

        :type process_name: string
        :param process_name: name of the process
        :type pid: int
        :param pid: the process id
        :type timeout: int
        :param timeout: timeout (seconds), default value is 60 seconds
        """
        raise NotImplementedError
