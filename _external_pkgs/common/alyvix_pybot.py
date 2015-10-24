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
import sys
import argparse
from robot import run

save = os.dup(1), os.dup(2)

null_fds = [os.open(os.devnull, os.O_RDWR) for x in xrange(2)]

parser = argparse.ArgumentParser()
parser.add_argument("testsuite", help="the file containing the testcase(s)")
parser.add_argument("--outputdir", help="robot framework output directory") #, default=None)
parser.add_argument("--test", help="the test case to run")

#parse arguments
args = parser.parse_args()

#disable console output
os.dup2(null_fds[0], 1)
os.dup2(null_fds[1], 2)

if args.outputdir:
    output_dir = args.outputdir
    output_file = "output.xml"
    log_file = "log.html"
    report_file = "report.html"
else:
    output_dir = "NONE"
    output_file = "NONE"
    log_file = "NONE"
    report_file = "NONE"

if args.test:
    #run testsuite with only one testcase
    run(args.testsuite, outputdir=output_dir, output=output_file, log=log_file, report=report_file, test=args.test)
else:
    #run testsuite with all testcases
    run(args.testsuite, outputdir=output_dir, output=output_file, log=log_file, report=report_file)

#enable console output
os.dup2(save[0], 1)
os.dup2(save[1], 2)
os.close(null_fds[0])
os.close(null_fds[1])

try:
    #print the output
    print os.getenv("alyvix_std_output")
    #exit with alyvix exit code
    sys.exit(int(os.getenv("alyvix_exitcode")))
except:
    pass