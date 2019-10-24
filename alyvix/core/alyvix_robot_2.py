import time
import sys
import copy
import os.path
from datetime import datetime
from socket import gethostname
from alyvix.core.engine import Result
from core.output import OutputManager
from core.utilities.parser import ParserManager
from alyvix.tools.library import LibraryManager

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

help_main_string = '''
usage: alyvix_robot.py [-h] --filename FILENAME --object OBJECT
                          [--args ARGUMENTS]
'''

def print_help():

    print(help_main_string)

    help_info = '''
    optional arguments:
      -h, --help            show this help message and exit
      --args ARGUMENTS, -a ARGUMENTS
                            dummy description for help
    
    required named arguments:
      --filename FILENAME, -f FILENAME
                            dummy description for help
    '''
    print(help_info)

    sys.exit(0)

def print_error_help(string):
    eprint(help_main_string)
    eprint(string)
    sys.exit(2)

index_filename_arg = -1
index_arguments_arg = -1
index_verbose_arg = -1

engine_arguments = []
verbose = 0

for i in range(0, len(sys.argv)):
    if sys.argv[i] == "-f" or sys.argv[i] == "--filename":
        filename = sys.argv[i+1]
        index_filename_arg = i
    elif sys.argv[i] == "-a" or sys.argv == "--args":
        index_arguments_arg = i
    elif sys.argv[i] == "-v" or sys.argv == "--verbose":
        index_verbose_arg = i
    elif sys.argv[i] == "-h" or sys.argv == "--help":
        print_help()

if index_filename_arg == -1:
    python_name = os.path.basename(__file__)
    if index_filename_arg == -1:
        help_info = python_name + ": error: the following arguments are required: --filename/-f"

    print_error_help(help_info)

if index_arguments_arg != -1:
    for i in range(index_arguments_arg+1, len(sys.argv)):
            if sys.argv[i] == "-f" or sys.argv[i] == "-filename":
                break
            engine_arguments.append(sys.argv[i])

if index_verbose_arg != -1:
    try:
        verbose = int(sys.argv[index_verbose_arg + 1])
    except:
        pass

if filename is not None:
    lm = LibraryManager()

    filename = lm.get_correct_filename(filename)

    invalid_chars = lm.get_invalid_filename_chars()

    filename_invalid_chars = []

    filename_path = os.path.dirname(filename)
    filename_no_path = os.path.basename(filename)
    filename_no_extension = os.path.splitext(filename_no_path)[0]
    file_extension = os.path.splitext(filename_no_path)[1]

    for char in filename_no_extension:
        for invalid_char in invalid_chars:
            if char == str(invalid_char):
                filename_invalid_chars.append(char)

    if len(filename_invalid_chars) > 0:
        invalid_char_str = filename_invalid_chars[0]
        for char in filename_invalid_chars[1:]:
            invalid_char_str = invalid_char_str + " " + char
        print("Invalid file name (" + filename_no_extension + "), the following characters are not valid: " +
              invalid_char_str)
        sys.exit(2)


    if os.path.isfile(filename) is False:
        print(filename + " does NOT exist")
        sys.exit(2)

    lm.load_file(filename)

    library_json = lm.get_json()


    print(filename_no_extension + " starts")

    username = os.environ['username']

    hostname = gethostname()

    objects_result = []

    code = ""

    timestamp = time.time()

    #< host > _ < user > _ < test > _ < YYYYMMDD_hhmmss_lll >

    date_from_ts = datetime.fromtimestamp(timestamp)
    try:
        millis_from_ts = date_from_ts.strftime("%f")[: -3]
    except:
        millis_from_ts = "000"
    date_formatted = date_from_ts.strftime("%Y%m%d_%H%M%S") + "_" + str(millis_from_ts) + "_UTC" + time.strftime("%z")

    code = hostname + "_" + username + "_" + filename_no_extension + "_" + date_formatted

    chunk = {"host": hostname, "user": username, "test": filename_no_extension, "code": code}

    state=0


    pm = ParserManager(library_json=library_json, chunk= chunk, engine_arguments=engine_arguments, verbose=verbose)

    pm.execute_script()

    objects_result = pm.get_results()

    not_executed_ts = time.time()

    timed_out_objects = []

    #OBJECT RUNNED OR IN TIMEDOUT
    for result in objects_result:
        date_from_ts = datetime.fromtimestamp(result.timestamp)
        # millis_from_ts = int(round(float(date_from_ts.strftime("0.%f")), 3) * 1000)
        try:
            millis_from_ts = date_from_ts.strftime("%f")[: -3]
        except:
            millis_from_ts = "000"

        date_formatted = date_from_ts.strftime("%Y/%m/%d %H:%M:%S") + "." + str(millis_from_ts)

        if result.performance_ms != -1:
            performance = round(result.performance_ms / 1000, 3)
            accuracy = round(result.accuracy_ms / 1000, 3)
            if result.output is True:
                print(date_formatted + ": " + result.object_name + " measures " + str(performance) + "s " +
                      "(+/-" + '{:.3f}'.format(accuracy) + ") OK")
            result.exit = True
        else:
            if result.output is True:
                print(date_formatted + ": " + result.object_name + " TIMED OUT after " + str(result.timeout) + "s")
            result.exit = False

    all_objects = pm.get_all_objects()

    executed_object = pm.get_executed_objects()

    for object in all_objects:
        if object in executed_object:
            continue
        else:

            dummy_result = Result()

            dummy_result.object_name = object
            dummy_result.timestamp = -1
            dummy_result.performance_ms = -1
            dummy_result.accuracy_ms = -1
            dummy_result.exit = True

            objects_result.append(dummy_result)

            print(object + " NOT EXECUTED")

    if state == 0:
        print (filename_no_extension + " ends ok")
    else:
        print (filename_no_extension + " TIMED OUT")

    om = OutputManager()
    #json_output = om.build_json(chunk, objects_result)

    if verbose >= 2:
        om.save_screenshots(filename_path, objects_result, prefix=filename_no_extension)


    date_from_ts = datetime.fromtimestamp(timestamp)
    date_formatted = date_from_ts.strftime("%Y%m%d_%H%M%S") + "_UTC" + time.strftime("%z")

    filename = filename_path + os.sep + filename_no_extension + "_" + date_formatted + ".alyvix"
    om.save(filename, lm.get_json(), chunk, objects_result)
