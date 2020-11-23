import time
import sys
import shlex
import copy
import os.path
import re
import cv2
import base64
from datetime import datetime
from socket import gethostname
from alyvix.core.output import OutputManager
from alyvix.core.engine import EngineManager, Result
from alyvix.core.utilities.parser import ParserManager
from alyvix.tools.library import LibraryManager
from alyvix.tools.screen import ScreenManager
from alyvix.tools.nats import NatsManager
from alyvix.tools.crypto import CryptoManager

class ResultForOutput():

    def __init__(self):
        self.object_name = None

        self.measures = []

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

help_main_string = '''usage: alyvix_robot.py [-h] --filename FILENAME [--object OBJECT]
                          [--args ARGUMENTS] [--mode MODE]
                          [--screenshot-recording RECORDING]
                          [--screenshot-compression COMPRESSION]
                          [--pseudonym PSEUDONYM]
                          [--verbose VERBOSE]
                          [--key KEY]'''

def print_help():
    print("\r\nAlyvix Robot runs an existing .alyvix file and reports the resulting measures.\r\n")

    print(help_main_string)

    help_info = '''
Required arguments:
  --filename FILENAME, -f FILENAME
                 Specify a filename or path pointing to an Alyvix file.
                 The .alyvix extension will be automatically added.
                 
Optional arguments:
  -h, --help     Show this help message and exit
  --args ARGUMENTS, -a ARGUMENTS
                 Supply one or more strings to use as values in the String
                 field template of a test case object.
  --key KEY, -k KEY
                 Supply a private key for use with encryption
  --mode MODE, -m MODE
                 Specify the output mode (alyvix, nagios, or nats-influxdb)
  --object OBJECT,  -o OBJECT
                 Execute a specific test case object within the test case, or
                 multiple objects by inserting each in a quoted string with a
                 space separating them.
  --pseudonym PSEUDONYM, -p PSEUDONYM
                 Set an additional test case name that allows you to
                 differentiate several runs with different sets of arguments
                 each.
  --screenshot-recording RECORDING, -sr RECORDING
                 any-output
                     [default] For any test case output (true or false) Alyvix
                     records screenshots and annotations of all test case
                     objects.
                 broken-output-only
                     Just in case of a broken execution Alyvix records
                     screenshots and annotations of all test case objects.
                 none
                     For any test case output (true or false) Alyvix does not
                     record screenshots and annotations at all; in this case
                     the --screenshot-compression option will not be
                     considered.
  --screenshot-compression COMPRESSION, -sc COMPRESSION
                 lossless
                     [default] Alyvix records screenshots and annotations in
                     PNG format.
                 compressed
                     Alyvix records screenshots and annotations in JPG 30%
                     format.
  --verbose VERBOSE, -v VERBOSE
                 Set the verbosity level for debugging output:
                 0
                     [default] Log start/stop timestamps, state and time
                     measures for each object (with measure option enabled).
                 1
                     Log Alyvix actions too.
                 2
                     Save screenshot and annotation files in the same
                     directory too.'''
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

is_foride = False
ide_sub_path = None

engine_arguments = []
engine_arguments_text = ""
objects_names = []
objects_name_for_nagios = []
verbose = 0
sys_exit = 0
output_mode = "alyvix"
encrypt_pwd = None
cipher_key = None
cipher_iv = None
alias = None

publish_nats = False
nats_server = ""
nats_db = ""
nats_measure = ""

not_executed_cnt = 0

screen_recording = "any-output"
screen_compression = "lossless"

cli_map = {}

for i in range(0, len(sys.argv)):
    if sys.argv[i] == "-f" or sys.argv[i] == "--filename":
        filename = sys.argv[i+1]
    elif sys.argv[i] == "-o" or sys.argv[i] == "--object":
        objects_names = sys.argv[i + 1]
        objects_names = shlex.split(objects_names)
    elif sys.argv[i] == "-a" or sys.argv[i] == "--args":
        engine_arguments = sys.argv[i + 1]
        engine_arguments_text = engine_arguments

        engine_arguments = engine_arguments.replace("\\'", "<alyvix_escp_quote>")

        cnt_sq = engine_arguments.count("'")

        if (cnt_sq % 2) != 0:
            print ("Error on -a: odd single quotes!")
            sys.exit(2)

        single_quote_args = re.findall(r"'[^'][^\\']*'", engine_arguments, re.IGNORECASE | re.UNICODE)


        for sq_arg in single_quote_args:

            engine_arguments = engine_arguments.replace(sq_arg, sq_arg.replace(" ", "<alyvix_repl_space>"))

        engine_arguments = engine_arguments.replace("'", "")

        engine_arguments = engine_arguments.split(" ")

        for i, v in enumerate(engine_arguments):
            engine_arguments[i] = engine_arguments[i].replace("<alyvix_repl_space>", " ").replace("<alyvix_escp_quote>", "'")

        cnt_arg = 0

        for earg in engine_arguments:
            cnt_arg += 1

            cli_map["arg" + str(cnt_arg)] = earg


    elif sys.argv[i] == "-v" or sys.argv[i] == "--verbose":
        try:
            verbose = int(sys.argv[i + 1])
        except:
            pass
    elif sys.argv[i] == "-sr" or sys.argv[i] == "--screenshot-recording":

        sr_arg = sys.argv[i + 1].lower()
        if sr_arg == "any-output":
            screen_recording = sr_arg
        elif sr_arg == "broken-output-only":
            screen_recording = sr_arg
        elif sr_arg == "none":
            screen_recording = sr_arg

    elif sys.argv[i] == "-sc" or sys.argv[i] == "--screenshot-compression":

        screen_compression = sys.argv[i + 1].lower()


    elif sys.argv[i] == "-h" or sys.argv[i] == "--help":
        print_help()
        exit(0)
    elif sys.argv[i] == "--is_foride":
        is_foride = True
    elif sys.argv[i] == "-m" or sys.argv[i] == "--mode":
        output_mode = sys.argv[i + 1]
    elif sys.argv[i] == "-p" or sys.argv[i] == "--pseudonym":
        alias = sys.argv[i + 1]
    elif sys.argv[i] == "-k" or sys.argv[i] == "--key":
        encrypt_pwd = sys.argv[i + 1]
        if len(encrypt_pwd) < 8:
            print("the encryption key must be at least eight characters long")
            exit(2)


cm = CryptoManager()

if encrypt_pwd is not None:
    cm.create_key(encrypt_pwd)

    cipher_key = cm.get_key()
    cipher_iv = cm.get_iv()

#aaaaaa = cm.decrypt(encrypt)


if "nats-influxdb" in output_mode:

    nats_args = output_mode.split(" ")
    nats_args.pop(0)

    nats_server = nats_args[0]
    nats_db = nats_args[1]

    try:
        nats_measure = nats_args[2]
    except:
        nats_measure = "alyvix"

    publish_nats = True
    output_mode = "nats"


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

    library_json["maps"] = lm.get_map()

    library_json["maps"]["cli"] = cli_map

    old_script = copy.deepcopy(lm.get_script())

    if len(objects_names) > 0:
        lib = lm.get_script()
        lib["case"] = []
        lib["sections"] = {}

        for obj in objects_names:
            lib["case"].append(obj)

    """
    if is_foride is True:
        os.remove(filename)
    """

    timestamp = time.time()
    start_time = timestamp

    date_from_ts = datetime.fromtimestamp(timestamp)
    try:
        millis_from_ts = date_from_ts.strftime("%f")[: -3]
    except:
        millis_from_ts = "000"
    date_formatted = date_from_ts.strftime("%Y%m%d_%H%M%S") + "_" + str(millis_from_ts) + "_UTC" + time.strftime("%z")

    if output_mode != "nagios":
        print(date_from_ts.strftime("%Y/%m/%d %H:%M:%S") + "." + str(millis_from_ts) + ": " + filename_no_extension + " starts")

    username = os.environ['username']

    hostname = gethostname()

    failed_objects = []


    code = ""


    #< host > _ < user > _ < test > _ < YYYYMMDD_hhmmss_lll >

    if alias is None:
        test_name = filename_no_extension
    else:
        test_name = alias
    code = hostname + "_" + username + "_" + test_name + "_" + date_formatted

    chunk = {"host": hostname, "user": username, "test": filename_no_extension, "code": code, "alias": alias}

    state=0

    t_start = time.time()

    sm = ScreenManager()
    w, h = sm.get_resolution()
    scaling_factor = sm.get_scaling_factor()


    pm = ParserManager(library_json=library_json, chunk= chunk, engine_arguments=engine_arguments,
                       verbose=verbose, output_mode=output_mode, cipher_key=cipher_key, cipher_iv=cipher_iv)

    pm.execute_script()

    performances = pm.get_unique_flattern_performances()

    #performances = pm.get_flattern_performances()


    not_executed_ts = time.time()

    performance_string = ""
    # OBJECT RUNNED OR IN TIMEDOUT
    for perf in performances:

        if perf["exit"] == "not_executed":
            not_executed_cnt += 1
            continue

        date_from_ts = datetime.fromtimestamp(perf["end_timestamp"])
        # millis_from_ts = int(round(float(date_from_ts.strftime("0.%f")), 3) * 1000)
        try:
            millis_from_ts = date_from_ts.strftime("%f")[: -3]
        except:
            millis_from_ts = "000"

        date_formatted = date_from_ts.strftime("%Y/%m/%d %H:%M:%S") + "." + str(millis_from_ts)

        warning_s = lm.get_warning_thresholds(perf["object_name"])
        critical_s = lm.get_critical_thresholds(perf["object_name"])

        curr_perf_string = ""

        if perf["performance_ms"] != -1:
            performance = round(int(perf["performance_ms"]) / 1000, 3)
            accuracy = round(int(perf["accuracy_ms"]) / 1000, 3)

            if output_mode == "nagios" and lm.measure_is_enable(perf["object_name"]) is True:
                curr_perf_string = perf["performance_name"].replace(" ", "_") + "=" + str(int(perf["performance_ms"] )) + "ms"
                if warning_s is not None:
                    curr_perf_string += ";" + str(warning_s*1000)
                    if perf["state"] == 1 and sys_exit < 1:
                        sys_exit = 1
                else:
                    curr_perf_string += ";"

                if critical_s is not None:
                    curr_perf_string += ";" + str(critical_s*1000)
                    if perf["state"] == 2 and sys_exit < 2:
                        sys_exit = 2
                else:
                    curr_perf_string += ";"
                curr_perf_string += ";; "

            elif output_mode != "nagios":

                if lm.measure_is_enable(perf["object_name"]) is True:
                    print(date_formatted + ": " + perf["performance_name"] + " DETECTED in " + '{:.3f}'.format(performance) + "s " +
                          "(+/-" + '{:.3f}'.format(accuracy) + ")")
                sys_exit = 0

        else:

            if lm.measure_is_enable(perf["object_name"]) is True and lm.break_is_enable(perf["object_name"]) is True:
                if output_mode == "nagios":
                    curr_perf_string = perf["performance_name"].replace(" ", "_") + "=ms"
                else:
                    print(date_formatted + ": " + perf["performance_name"] + " FAILED after " +
                          str(lm.get_timeout(perf["object_name"])) + "s")
                failed_objects.append(perf["performance_name"])
                sys_exit = 2
            elif lm.measure_is_enable(perf["object_name"]) is True and lm.break_is_enable(perf["object_name"]) is False:
                if output_mode == "nagios":
                    curr_perf_string = perf["performance_name"].replace(" ", "_") + "=" +\
                                       str(lm.get_timeout(perf["object_name"])*1000) + "ms"
                else:
                    print(date_formatted + ": " + perf["performance_name"] + " SKIPPED after " +
                          str(lm.get_timeout(perf["object_name"])) + "s")

            elif lm.measure_is_enable(perf["object_name"]) is False and lm.break_is_enable(perf["object_name"]) is True:
                failed_objects.append(perf["performance_name"])
                sys_exit = 2
            """
            elif result.output is False and result.has_to_break is False:
                result.exit = "false"
                #state = 2
            """
            if output_mode == "nagios" and lm.measure_is_enable(perf["object_name"]) is True:
                if warning_s is not None:
                    curr_perf_string += ";" + str(warning_s*1000)
                else:
                    curr_perf_string += ";"

                if critical_s is not None:
                    curr_perf_string += ";" + str(critical_s*1000)
                else:
                    curr_perf_string += ";"

                curr_perf_string += ";; "

        performance_string += curr_perf_string

    t_end = time.time() - t_start

    library_json["script"] = old_script


    message_to_print = ""
    not_exec_print = "NOT EXECUTED transactions: "
    if output_mode == "nagios":
        if sys_exit == 0:
            message_to_print = "OK"
        elif sys_exit == 1:
            message_to_print = "WARNING"
        elif sys_exit == 2 and len(failed_objects) == 0:
            message_to_print = "CRITICAL"
        elif sys_exit == 2 and len(failed_objects) > 0:
            message_to_print = "CRITICAL: " +  failed_objects[0].replace(" ", "_") + " FAILED"

        #print(message_to_print + performance_string)

    else:

        if sys_exit == 0:
            print (get_timestamp_formatted() + ": " + filename_no_extension + " ends OK, taking " + '{:.3f}'.format(t_end) + "s.")
            exit = "true"
        else:
            print (get_timestamp_formatted() + ": " + filename_no_extension + " ends FAILED because of " + failed_objects[0] +", it takes " + '{:.3f}'.format(t_end) + "s.")
            exit = "false"

    om = OutputManager()
    #json_output = om.build_json(chunk, objects_result)

    if verbose >= 2 and output_mode == "alyvix": #or is_foride is True:
        om.save_screenshots(filename_path, pm.get_flattern_performances(), prefix=filename_no_extension,
                            compression=screen_compression)

    if not_executed_cnt > 0:
        if output_mode != "nagios":
            print("    NOT EXECUTED objects:")
        for perf in performances:
            if perf["exit"] == "not_executed":

                if output_mode == "nagios":
                    if lm.measure_is_enable(perf["object_name"]) is True:
                        warning_s = None
                        critical_s = None

                        curr_perf_string = ""

                        warning_s = lm.get_warning_thresholds(perf["object_name"])
                        critical_s = lm.get_critical_thresholds(perf["object_name"])


                        curr_perf_string = perf["performance_name"].replace(" ", "_") + "=ms"

                        if warning_s is not None:
                            curr_perf_string += ";" + str(warning_s*1000)
                        else:
                            curr_perf_string += ";"

                        if critical_s is not None:
                            curr_perf_string += ";" + str(critical_s*1000)
                        else:
                            curr_perf_string += ";"

                        curr_perf_string += ";; "

                        performance_string += curr_perf_string

                    not_exec_print += perf["performance_name"].replace(" ", "_") + "; "
                else:
                    print("        " + perf["performance_name"])

        performance_string = performance_string[:-1]

    if output_mode == "nagios":
        if performance_string != "":
            print(message_to_print + "|" + performance_string)
        else:
            print(message_to_print)
        if len(failed_objects) > 0:
            failed_to_print = ""
            for obj in failed_objects:
                failed_to_print += obj.replace(" ", "_") + "; "
            print("FAILED transactions (from first to last): " + failed_to_print[:-2])

        if not_executed_cnt > 0:
            print(not_exec_print[:-2])

    date_from_ts = datetime.fromtimestamp(timestamp)
    date_formatted = date_from_ts.strftime("%Y%m%d_%H%M%S") + "_UTC" + time.strftime("%z")

    if output_mode == "alyvix":
        filename = filename_path + os.sep + filename_no_extension + "_" + date_formatted + ".alyvix"

        #if is_foride is False:
        om.save(filename, lm.get_json(), chunk, pm.get_performances(),engine_arguments_text, exit, sys_exit, t_end,
                screen_compression, screen_recording)

    if publish_nats is True:
        nats_manager = NatsManager()
        nats_manager.publish_message(performances, start_time=start_time,
                                     server=nats_server,db=nats_db,measure=nats_measure, filename=filename_no_extension)
    sys.exit(sys_exit)
