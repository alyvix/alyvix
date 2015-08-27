import os
import sys
from robot import run
from StringIO import StringIO


testcase_name = sys.argv[1]

save = os.dup(1), os.dup(2)
null_fds = [os.open(os.devnull, os.O_RDWR) for x in xrange(2)]
        
def disable_console_output():
    # open 2 fds
    null_fds = [os.open(os.devnull, os.O_RDWR) for x in xrange(2)]

    save = os.dup(1), os.dup(2)

    os.dup2(null_fds[0], 1)
    os.dup2(null_fds[1], 2)


def enable_console_output():
    os.dup2(save[0], 1)
    os.dup2(save[1], 2)

    os.close(null_fds[0])
    os.close(null_fds[1])


disable_console_output()  
run(testcase_name, stdout=StringIO())
enable_console_output()

print os.getenv("alyvix_std_output")
sys.exit(int(os.getenv("alyvix_exitcode")))