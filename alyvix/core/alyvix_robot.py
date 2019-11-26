import time
import sys
import shlex
import copy
import os.path
from datetime import datetime
from socket import gethostname
from alyvix.core.output import OutputManager
from alyvix.core.engine import EngineManager, Result
from alyvix.core.utilities.parser import ParserManager
from alyvix.tools.library import LibraryManager

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

help_main_string = '''
usage: alyvix_robot.py [-h] --filename FILENAME [--object OBJECT]
                          [--args ARGUMENTS]
'''

def print_help():

    print(help_main_string)

    help_info = '''
    optional arguments:
      -h, --help            show this help message and exit
      --object OBJECT,  -o OBJECT
                            dummy description for help
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

def get_timestamp_formatted():
    timestamp = time.time()
    date_from_ts = datetime.fromtimestamp(timestamp)
    # millis_from_ts = int(round(float(date_from_ts.strftime("0.%f")), 3) * 1000)
    try:
        millis_from_ts = date_from_ts.strftime("%f")[: -3]
    except:
        millis_from_ts = "000"

    date_formatted = date_from_ts.strftime("%Y/%m/%d %H:%M:%S") + "." + str(millis_from_ts)

    return date_formatted

filename = None

engine_arguments = []
objects_names = []
verbose = 0
sys_exit = 0

for i in range(0, len(sys.argv)):
    if sys.argv[i] == "-f" or sys.argv[i] == "--filename":
        filename = sys.argv[i+1]
    elif sys.argv[i] == "-o" or sys.argv[i] == "--object":
        objects_names = sys.argv[i + 1]
        objects_names = shlex.split(objects_names)
    elif sys.argv[i] == "-a" or sys.argv == "--args":
        engine_arguments = sys.argv[i + 1]
        lexer = shlex.shlex(engine_arguments, posix=True)
        lexer.escapedquotes = r"\'"
        engine_arguments = list(lexer)
    elif sys.argv[i] == "-v" or sys.argv == "--verbose":
        try:
            verbose = int(sys.argv[i + 1])
        except:
            pass
    elif sys.argv[i] == "-h" or sys.argv == "--help":
        print_help()

if filename is None:
    python_name = os.path.basename(__file__)
    help_info = python_name + ": error: the following arguments are required: --filename/-f"

    print_error_help(help_info)

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

    timestamp = time.time()
    start_time = timestamp

    date_from_ts = datetime.fromtimestamp(timestamp)
    try:
        millis_from_ts = date_from_ts.strftime("%f")[: -3]
    except:
        millis_from_ts = "000"
    date_formatted = date_from_ts.strftime("%Y%m%d_%H%M%S") + "_" + str(millis_from_ts) + "_UTC" + time.strftime("%z")

    print(date_from_ts.strftime("%Y/%m/%d %H:%M:%S") + "." + str(millis_from_ts) + ": " + filename_no_extension + " starts")

    username = os.environ['username']

    hostname = gethostname()

    objects_result = []

    timed_out_objects = []

    code = ""


    #< host > _ < user > _ < test > _ < YYYYMMDD_hhmmss_lll >


    code = hostname + "_" + username + "_" + filename_no_extension + "_" + date_formatted

    chunk = {"host": hostname, "user": username, "test": filename_no_extension, "code": code}

    state=0

    t_start = time.time()

    if len(objects_names) == 0:

        pm = ParserManager(library_json=library_json, chunk= chunk, engine_arguments=engine_arguments, verbose=verbose)

        pm.execute_script()

        objects_result = pm.get_results()

        not_executed_ts = time.time()


        # OBJECT RUNNED OR IN TIMEDOUT
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
                    print(date_formatted + ": " + result.object_name + " DETECTED in " + str(performance) + "s " +
                          "(+/-" + '{:.3f}'.format(accuracy) + ")")
                result.exit = "true"
            else:
                if result.output is True and result.has_to_break is True:
                    print(date_formatted + ": " + result.object_name + " FAILED after " + str(result.timeout) + "s")
                    timed_out_objects.append(result.object_name)
                    result.exit = "fail"
                    sys_exit = 2
                elif result.output is True and result.has_to_break is False:
                    print(date_formatted + ": " + result.object_name + " SKIPPED after " + str(result.timeout) + "s")
                    result.exit = "false"
                elif result.output is False and result.has_to_break is True:
                    timed_out_objects.append(result.object_name)
                    result.exit = "fail"
                    sys_exit = 2
                elif result.output is False and result.has_to_break is False:
                    result.exit = "false"
                    #state = 2




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
                dummy_result.exit = "not_executed"

                objects_result.append(dummy_result)

                #print(object + " NOT EXECUTED")


    else:
        maps = lm.get_map()

        for object_name in objects_names:

            """
            if lm.check_valid_object_name(object_name) is False:
                print(object_name + " contains invalid characters, only alphanumeric characters and -_' ' (space) are allowed.")
                sys.exit(2)
            """
            if lm.check_if_exist(object_name) is False:
                print(object_name + " does NOT exist")
                sys.exit(2)

        for object_name in objects_names:

            object_json = lm.add_chunk(object_name, chunk)

            engine_manager = EngineManager(object_json, args=engine_arguments,
                                           maps=maps, executed_objects=objects_result, verbose=verbose)
            result = engine_manager.execute()

            objects_result.append(result)

            if result.performance_ms == -1 and result.has_to_break is True:
                if verbose >= 1:
                    print(get_timestamp_formatted() + ": Alyvix breaks " + result.object_name + " after " + str(result.timeout) + "s")
                timed_out_objects.append(result.object_name)
                state = 2
                break
            elif result.performance_ms == -1 and result.has_to_break is False:
                if verbose >= 1:
                    print(get_timestamp_formatted() + ": Alyvix skips " + result.object_name + " after " + str(result.timeout) + "s")

        if len(objects_result) < len(objects_names):

            #state = 2

            cnt = 1
            for object_name in objects_names:

                if cnt > len(objects_result):
                    result = Result()
                    result.object_name = object_name
                    result.timestamp = -1
                    result.performance_ms = -1
                    result.accuracy_ms = -1
                    result.exit = "not_executed"
                    objects_result.append(result)
                cnt += 1
        """
        elif len(objects_result) == len(objects_names) and objects_result[0].performance_ms == -1:
            state = 2
        """

        not_executed_ts = time.time()
        for result in objects_result:
            # YYYYMMDD_hhmmss_lll : <object_name> measures <performance_ms> (+/-<accuracy>)
            if result.timestamp != -1:

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
                        print(date_formatted + ": " + result.object_name + " DETECTED in " + str(performance) + "s " +
                              "(+/-" + '{:.3f}'.format(accuracy) + ")")
                    result.exit = "true"
                else:
                    if result.output is True and result.has_to_break is True:
                        print(date_formatted + ": " + result.object_name + " FAILED after " + str(result.timeout) + "s")
                        result.exit = "fail"
                        sys_exit = 2
                    elif result.output is True and result.has_to_break is False:
                        print(date_formatted + ": " + result.object_name + " SKIPPED after " + str(result.timeout) + "s")
                        result.exit = "false"
                    elif result.output is False and result.has_to_break is True:
                        result.exit = "fail"
                        sys_exit = 2
                    elif result.output is False and result.has_to_break is False:
                        result.exit = "false"

            else:
                #print(result.object_name + " NOT EXECUTED")
                result.exit = "not_executed"

    t_end = time.time() - t_start


    if sys_exit == 0:
        print (get_timestamp_formatted() + ": " + filename_no_extension + " ends OK, it takes " + '{:.3f}'.format(t_end) + "s.")
        exit = "true"
    else:
        print (get_timestamp_formatted() + ": " + filename_no_extension + " ends FAILED because of " + timed_out_objects[0] +", it takes " + '{:.3f}'.format(t_end) + "s.")
        exit = "false"

    om = OutputManager()
    #json_output = om.build_json(chunk, objects_result)

    if verbose >= 2:
        om.save_screenshots(filename_path, objects_result, prefix=filename_no_extension)

    print("    NOT EXECUTED objects:")
    for result in objects_result:
        if result.timestamp == -1:
            print("        " + result.object_name)

    date_from_ts = datetime.fromtimestamp(timestamp)
    date_formatted = date_from_ts.strftime("%Y%m%d_%H%M%S") + "_UTC" + time.strftime("%z")

    filename = filename_path + os.sep + filename_no_extension + "_" + date_formatted + ".alyvix"
    om.save(filename, lm.get_json(), chunk, objects_result, exit, t_end)
