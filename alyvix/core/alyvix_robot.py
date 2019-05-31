import json
import time
import sys
import os.path
from datetime import datetime
from socket import gethostname
from alyvix.core.engine import EngineManager, Result
from alyvix.core.output import OutputManager
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
      --object OBJECT, -o OBJECT
                            dummy description for help
    '''
    print(help_info)

    sys.exit(0)

def print_error_help(string):
    eprint(help_main_string)
    eprint(string)
    sys.exit(2)

index_filename_arg = -1
index_object_name_arg = -1
index_arguments_arg = -1

engine_arguments = []

for i in range(0, len(sys.argv)):
    if sys.argv[i] == "-f" or sys.argv[i] == "--filename":
        filename = sys.argv[i+1]
        index_filename_arg = i
    elif sys.argv[i] == "-o" or sys.argv[i] == "--object":
        objects_names = sys.argv[i+1].split(' ')
        index_object_name_arg = i
    elif sys.argv[i] == "-a" or sys.argv == "--args":
        index_arguments_arg = i
    elif sys.argv[i] == "-h" or sys.argv == "--help":
        print_help()

if index_filename_arg == -1 or index_object_name_arg == -1:
    python_name = os.path.basename(__file__)
    if index_filename_arg == -1 and index_object_name_arg == -1:
        help_info = python_name + ": error: the following arguments are required: --filename/-f, --object/-o"
    elif index_filename_arg == -1:
        help_info = python_name + ": error: the following arguments are required: --filename/-f"
    elif index_object_name_arg == -1:
        help_info = python_name + ": error: the following arguments are required: --object/-o"

    print_error_help(help_info)

if index_arguments_arg != -1:
    for i in range(index_arguments_arg+1, len(sys.argv)):
            if sys.argv[i] == "-o" or sys.argv[i] == "--object" or sys.argv[i] == "-f" or sys.argv[i] == "-filename":
                break
            engine_arguments.append(sys.argv[i])


if filename is not None:
    lm = LibraryManager()

    lm.load_file(filename)

    filename_path = os.path.dirname(filename)
    filename_no_extension = os.path.basename(filename)
    filename_no_extension = os.path.splitext(filename_no_extension)[0]

    if filename_path == '':
        filename_path = os.getcwd()

    username = os.environ['username']

    hostname = gethostname()

    objects_result = []

    code = ""

    """
    try:
        code += hostname[0]
        code += hostname[1]
        code += hostname[-2]
        code += hostname[-1]
    except:
        pass

    try:
        code += username[0]
        code += username[1]
        code += username[-2]
        code += username[-1]
    except:
        pass

    try:
        code += filename_no_extension[0]
        code += filename_no_extension[1]
        code += filename_no_extension[-2]
        code += filename_no_extension[-1]
    except:
        pass
    """

    timestamp = time.time()

    #< host > _ < user > _ < test > _ < YYYYMMDD_hhmmss_lll >

    date_from_ts = datetime.fromtimestamp(timestamp)
    millis_from_ts = int(round(float(date_from_ts.strftime("0.%f")), 3) * 1000)
    date_formatted = date_from_ts.strftime("%Y%m%d_%H%M%S") + "_" + str(millis_from_ts)

    code = hostname + "_" + username + "_" + filename_no_extension + "_" + date_formatted

    chunk = {"host": hostname, "user": username, "test": filename_no_extension, "code": code}

    state=0

    for object_name in objects_names:

        object_json = lm.add_chunk(object_name, chunk)

        engine_manager = EngineManager(object_json, args=engine_arguments)
        result = engine_manager.execute()

        objects_result.append(result)

        if result.performance_ms == -1 and result.has_to_break is True:
            break


    if len(objects_result) < len(objects_names):

        state = 2

        cnt = 1
        for object_name in objects_names:

            if cnt > len(objects_result):
                result = Result()
                result.object_name = object_name
                result.timestamp = -1
                result.performance_ms = -1
                result.accuracy_ms = -1

                objects_result.append(result)
            cnt+=1
    elif len(objects_result) == len(objects_names) and objects_result[0].performance_ms == -1:
        state = 2

    om = OutputManager()
    #json_output = om.build_json(chunk, objects_result)

    om.save_screenshots(filename_path, objects_result, prefix=filename_no_extension)

    date_from_ts = datetime.fromtimestamp(timestamp)
    date_formatted = date_from_ts.strftime("%Y%m%d_%H%M%S")

    filename = filename_path + os.sep + date_formatted + "_" + filename_no_extension + ".alyvix"
    om.save(filename, lm.get_json(), chunk, objects_result)


    if state == 0:
        print ("All transactions are ok.")
    else:
        print("One or more transactions are in critical state.")

    not_executed_ts = time.time()
    for result in objects_result:
        #YYYYMMDD_hhmmss_lll : <object_name> measures <performance_ms> (+/-<accuracy>)
        if result.timestamp != -1:
            date_from_ts = datetime.fromtimestamp(result.timestamp)
            millis_from_ts = int(round(float(date_from_ts.strftime("0.%f")), 3) * 1000)
            date_formatted = date_from_ts.strftime("%Y%m%d_%H%M%S") + "_" + str(millis_from_ts)
        else:
            date_formatted = "not executed"


        if result.performance_ms != -1:

            performance = round(result.performance_ms/1000, 3)
            accuracy = round(result.accuracy_ms/1000, 3)

            print(date_formatted + ": " + result.object_name + " measures " + str(performance) + "s " +
                  "(+/-" + str(accuracy) + ")")
        else:
            print(date_formatted + ": " + result.object_name + " measures null")

    aaa = None