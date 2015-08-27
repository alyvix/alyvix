import os
import sys
from robot import run
from StringIO import StringIO

testcase_name = sys.argv[1]

run(testcase_name, stdout=StringIO())
sys.exit(int(os.getenv("alyvix_exitcode")))