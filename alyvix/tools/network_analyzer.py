#! /usr/bin/python

"""
    Analysis of running processes over network connections on Windows
    Copyright (C) 2018 Francesco Melchiori <https://www.francescomelchiori.com/>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import subprocess
import json


class NetManager:

    def __init__(self, customer_name='test', exec_name='mstsc.exe', path_json=''):
        self.customer_name = customer_name
        self.exec_name = exec_name
        self.ip_hostname_map = {}
        self.name_pid_map = {}
        self.pid_ip_port_map = {}
        self.execname_hostname_ip_port = {}
        self.known_hostnames = []
        if customer_name == 'test':
            self.store_json_ip_hostname_map()
        self.load_json_ip_hostname_map(path_json)
        self.get_name_pid_tl()
        self.get_pid_ip_port_ns()
        self.get_ip_port_hostname()

    def print_ip_hostname_map(self):
        print(self.ip_hostname_map)

    def print_ip_port_hostname_map(self):
        print(self.execname_hostname_ip_port)

    def print_known_hostnames(self, first=False):
        if first:
            print(self.known_hostnames[0])
        else:
            print(self.known_hostnames)

    def store_json_ip_hostname_map(self):
        ip_hostname_map = {'192.168.0.1': 'hostname_1',
                           '192.168.0.2': 'hostname_2'}
        json.dump(ip_hostname_map,
                  fp=open('{0}_ip_hostname_map.json'.format(self.customer_name), 'w'),
                  indent=4)

    def load_json_ip_hostname_map(self, path_json=''):
        filename_json = '{0}_ip_hostname_map.json'.format(self.customer_name)
        path_json_ip_hostname_map = '{0}{1}'.format(path_json, filename_json)
        try:
            self.ip_hostname_map = json.load(open(path_json_ip_hostname_map))
        except IOError:
            print('{0}_ip_hostname_map.json does not exist'.format(self.customer_name))
            return False
        return True

    def map_ip_hostname(self, ip=''):
        if ip in self.ip_hostname_map:
            hostname = self.ip_hostname_map[ip]
        else:
            hostname = 'no ip hostname map'
        return hostname

    def get_name_pid_tl(self, verbose=False):
        tasklist_output = subprocess.check_output(['tasklist',
                                                   '/FI', 'IMAGENAME eq {0}'.format(self.exec_name),
                                                   '/FI', 'STATUS eq RUNNING',
                                                   '/FO', 'CSV'])
        if 'no tasks' in tasklist_output.lower():
            print('tasklist empty')
            return False
        if verbose:
            print('running processes:')
        tasklist_output_valid = False
        for row_raw in tasklist_output.splitlines():
            if not tasklist_output_valid:
                if 'PID' in row_raw:
                    tasklist_output_valid = True
                    continue
                else:
                    print('tasklist issue')
            name = row_raw.replace('"', '').split(',')[:2][0]
            pid = int(row_raw.replace('"', '').split(',')[:2][1])
            if name in self.name_pid_map:
                self.name_pid_map[name].append(pid)
            else:
                self.name_pid_map[name] = [pid]
            if verbose:
                print('exec:{0} | pid:{1}'.format(name, pid))
        return True

    def get_pid_ip_port_ns(self, verbose=False):
        netstat_output = subprocess.check_output(['netstat', '-anop', 'tcp'])
        if 'tcp' not in netstat_output.lower():
            print('netstat empty')
            return False
        if verbose:
            print('active tcp connections:')
        for row_raw in netstat_output.splitlines():
            if 'tcp' in row_raw.lower():
                pid = int(row_raw.split()[4])
                ip = row_raw.split()[2].split(':')[0]
                port = int(row_raw.split()[2].split(':')[1])
                if pid in self.pid_ip_port_map:
                    self.pid_ip_port_map[pid].append([ip, port])
                else:
                    self.pid_ip_port_map[pid] = [[ip, port]]
                if verbose:
                    print('pid:{0} | ip:{1} | port:{2}'.format(pid, ip, port))
        return True

    def get_ip_port_hostname(self):
        if self.exec_name in self.name_pid_map:
            for pid in self.name_pid_map[self.exec_name]:
                if pid in self.pid_ip_port_map:
                    for ip_port in self.pid_ip_port_map[pid]:
                        hostname = self.map_ip_hostname(ip_port[0])
                        if hostname != 'no ip hostname map':
                            self.known_hostnames.append(hostname)
                        ip_port.append(hostname)
                        if self.exec_name in self.execname_hostname_ip_port:
                            self.execname_hostname_ip_port[self.exec_name].append(ip_port)
                        else:
                            self.execname_hostname_ip_port[self.exec_name] = [ip_port]
                else:
                    return False
        else:
            return False
        return True


def get_mstsc_hostname(customer_name='test', path_json=''):
    nm = NetManager(customer_name=customer_name, path_json=path_json)
    if nm.known_hostnames:
        first_known_hostname = nm.known_hostnames[0]
        return first_known_hostname
    else:
        return False


if __name__ == '__main__':

    #path_json = 'C:\\folder_json_ip_hostname_map\\'
    #path_json = os.getcwd() + '\\'
    print(get_mstsc_hostname(customer_name='wp'))  # , path_json=path_json))

    while False:
        command = raw_input('enter command: ')

        if command == 'run_mstsc':
            mstsc_path = 'C:\Windows\System32\mstsc.exe'
            rdp_server = '/v:10.62.4.70'
            rdp_width = '/w:1280'
            rdp_heigh = '/h:800'
            mstsc_args = ['mstsc', rdp_server, rdp_width, rdp_heigh]
            os.execv(mstsc_path, mstsc_args)

        if command == 'run_ps':
            ps_command_mstsc_3389 = ("Get-NetTCPConnection -RemotePort 3389 | "
                                     "select @{n='ProcessName'; e={(Get-Process -id $_.OwningProcess).ProcessName}}, "
                                     "RemoteAddress, "
                                     "RemotePort | "
                                     "where-Object {$_.ProcessName -eq 'mstsc'}")
            ps_output = subprocess.check_output(['powershell', ps_command_mstsc_3389])
            print(ps_output)

        if command == 'get_mstsc':
            get_mstsc_hostname('wp')

        if command == 'exit':
            break
