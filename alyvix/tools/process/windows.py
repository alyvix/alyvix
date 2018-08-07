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

import time
import subprocess
import win32com.client
from .base import ProcManagerBase


class ProcManager(ProcManagerBase):

    def kill_process(self, process_name):
        """
        kill a process.

        :type process_name: string
        :param process_name: the name of the process to kill
        """
        proc = subprocess.Popen("C:\\Windows\\System32\\taskkill.exe /im " +  process_name + " /f", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc_out, proc_err = proc.communicate()

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
        wmi = win32com.client.GetObject('winmgmts:')
        process_time = 0

        t0 = time.time()

        while True:
            process_exist = False
            for p in wmi.InstancesOf('win32_process'):

                if p.Name == process_name:

                    if pid is not None:

                        if p.Properties_('ProcessId').Value == pid:
                            process_exist = True
                            break
                    else:
                        process_exist = True
                        break

                # print p.Name, p.Properties_('ProcessId'), \
                #    int(p.Properties_('UserModeTime').Value)+int(p.Properties_('KernelModeTime').Value)


                """
                children=wmi.ExecQuery('Select * from win32_process where ParentProcessId=%s' %p.Properties_('ProcessId'))
                for child in children:
                    print '\t',child.Name,child.Properties_('ProcessId'), \
                        int(child.Properties_('UserModeTime').Value)+int(child.Properties_('KernelModeTime').Value)
                """

            if process_exist is False:
                return process_time

            if process_time >= timeout:
                return -1

            process_time = time.time() - t0