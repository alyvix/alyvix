import time
import sys
import shlex
import copy
import os.path
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

help_main_string = '''
usage: alyvix_robot.py [-h] --filename FILENAME [--object OBJECT]
                          [--args ARGUMENTS] [--mode MODE]
                          [--key KEY]
'''

def print_help():

    print(help_main_string)

    help_info = '''
    optional arguments:
      -h, --help            show this help message and exit
      --object OBJECT,  -o OBJECT
                            dummy description for help
      --args ARGUMENTS, -a ARGUMENTS
                            dummy description for args
      --mode MODE, -m MODE
                            dummy description for mode
      --key KEY, -k KEY
                            dummy description for key  
    
    required named arguments:
      --filename FILENAME, -f FILENAME
                            dummy description for filename
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

is_foride = False
ide_sub_path = None

engine_arguments = []
objects_names = []
objects_name_for_nagios = []
verbose = 0
sys_exit = 0
output_mode = "alyvix"
encrypt_pwd = None
cipher_key = None
cipher_iv = None

publish_nats = False
nats_server = ""
nats_db = ""
nats_measure = ""

not_executed_cnt = 0

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
        exit(0)
    elif sys.argv[i] == "--is_foride":
        is_foride = True
    elif sys.argv[i] == "-m" or sys.argv[i] == "--mode":
        output_mode = sys.argv[i + 1]
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
    output_mode = "nagios"


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

    objects_result = []

    timed_out_objects = []

    objects_for_output = []

    code = ""


    #< host > _ < user > _ < test > _ < YYYYMMDD_hhmmss_lll >


    code = hostname + "_" + username + "_" + filename_no_extension + "_" + date_formatted

    chunk = {"host": hostname, "user": username, "test": filename_no_extension, "code": code}

    state=0

    t_start = time.time()

    sm = ScreenManager()
    w, h = sm.get_resolution()
    scaling_factor = sm.get_scaling_factor()


    pm = ParserManager(library_json=library_json, chunk= chunk, engine_arguments=engine_arguments,
                       verbose=verbose, cipher_key=cipher_key, cipher_iv=cipher_iv)

    pm.execute_script()

    objects_result = pm.get_results()

    not_executed_ts = time.time()

    performance_string = ""
    # OBJECT RUNNED OR IN TIMEDOUT
    for result in objects_result:

        obj_name = result.object_name

        measure_dict = {"performance_ms": int(result.performance_ms),
                        "accuracy_ms": int(result.accuracy_ms),
                        "timestamp": result.timestamp,
                        "records": result.records,
                        #"group": result.group,
                        #"thresholds": result.thresholds,
                        #"output": result.output,
                        "exit": result.exit,
                        "resolution": {
                            "width": w,
                            "height": h
                        },
                        #"arguments":result.arguments,
                        "scaling_factor": int(scaling_factor * 100),
                        }

        if result.screenshot is not None:
            png_image = cv2.imencode('.png', result.screenshot)

            measure_dict["screenshot"] = base64.b64encode(png_image[1]).decode('ascii')

        else:
            measure_dict["screenshot"] = None

        if result.annotation is not None:
            png_image = cv2.imencode('.png', result.annotation)

            measure_dict["annotation"] = base64.b64encode(png_image[1]).decode('ascii')
        else:
            measure_dict["annotation"] = None


        if result.map_key is not None:
            measure_dict["map_name"] = result.map_key[0]
            measure_dict["map_key"] = result.map_key[1]

            if True: #output_mode == "nagios":
                obj_name = result.object_name + "_" + measure_dict["map_key"]

                start_index = 0

                cnt_obj = 0
                for exec_obj in objects_result:
                    if exec_obj.map_key is not None:
                        #measure_dict["map_name"] = exec_obj.map_key[0]
                        #measure_dict["map_key"] = exec_obj.map_key[1]

                        obj_name_2 = exec_obj.object_name + "_" + exec_obj.map_key[1]

                        if obj_name == obj_name_2:

                            cnt_obj += 1

                    if cnt_obj > 1:
                        start_index = 1
                        obj_name = obj_name + "_1"
                        break

        else:

            start_index = 0

            cnt_obj = 0
            for exec_obj in objects_result:
                if result.object_name == exec_obj.object_name:
                    cnt_obj += 1

                if cnt_obj > 1:
                    start_index = 1
                    obj_name = obj_name + "_1"
                    break

        if True: #output_mode == "nagios":
            if len(objects_name_for_nagios) == 0:
                objects_name_for_nagios.append(obj_name)
            else:
                cnt_obj_name = 2

                loop_name = obj_name

                while True:
                    exists = False
                    for obj_nagios_name in objects_name_for_nagios:
                        if obj_nagios_name == loop_name:
                            exists = True
                            loop_name = obj_name[:-2] + "_" + str(cnt_obj_name)
                            cnt_obj_name += 1
                            break

                    if exists is False:
                        obj_name = loop_name
                        objects_name_for_nagios.append(obj_name)
                        break

        measure_dict["name_for_screen"] = obj_name
        result.extended_name = obj_name


        warning_s = None
        critical_s = None

        curr_perf_string = ""

        try:
            warning_s = result.thresholds["warning_s"]
        except:
            pass

        try:
            critical_s = result.thresholds["critical_s"]
        except:
            pass


        date_from_ts = datetime.fromtimestamp(result.end_timestamp)
        # millis_from_ts = int(round(float(date_from_ts.strftime("0.%f")), 3) * 1000)
        try:
            millis_from_ts = date_from_ts.strftime("%f")[: -3]
        except:
            millis_from_ts = "000"

        date_formatted = date_from_ts.strftime("%Y/%m/%d %H:%M:%S") + "." + str(millis_from_ts)

        if result.performance_ms != -1:
            performance = round(result.performance_ms / 1000, 3)
            accuracy = round(result.accuracy_ms / 1000, 3)

            if output_mode == "nagios" and result.output is True:
                curr_perf_string = obj_name.replace(" ", "_") + "=" + str(int(result.performance_ms)) + "ms"
                if warning_s is not None:
                    curr_perf_string += ";" + str(warning_s) + "s"
                    if performance >= warning_s and sys_exit < 1:
                        sys_exit = 1
                        result.state = 1
                else:
                    curr_perf_string += ";"

                if critical_s is not None:
                    curr_perf_string += ";" + str(critical_s) + "s"
                    if performance >= critical_s and sys_exit < 2:
                        sys_exit = 2
                        result.state = 2
                else:
                    curr_perf_string += ";"
                curr_perf_string += ";; "

            elif output_mode != "nagios":

                if result.output is True:
                    print(date_formatted + ": " + obj_name + " DETECTED in " + str(performance) + "s " +
                          "(+/-" + '{:.3f}'.format(accuracy) + ")")
            result.exit = "true"
        else:

            if result.output is True and result.has_to_break is True:
                if output_mode == "nagios":
                    curr_perf_string = obj_name.replace(" ", "_") + "=ms"
                    result.state = 2
                else:
                    print(date_formatted + ": " + obj_name + " FAILED after " + str(result.timeout) + "s")
                timed_out_objects.append(obj_name)
                result.exit = "fail"
                sys_exit = 2
            elif result.output is True and result.has_to_break is False:
                if output_mode == "nagios":
                    curr_perf_string = obj_name.replace(" ", "_") + "=" + str(result.timeout*1000) + "ms"
                else:
                    print(date_formatted + ": " + obj_name + " SKIPPED after " + str(result.timeout) + "s")
                result.exit = "false"
            elif result.output is False and result.has_to_break is True:
                timed_out_objects.append(obj_name)
                result.exit = "fail"
                sys_exit = 2
            elif result.output is False and result.has_to_break is False:
                result.exit = "false"
                #state = 2

            if output_mode == "nagios" and result.output is True:
                if warning_s is not None:
                    curr_perf_string += ";" + str(warning_s) + "s"
                else:
                    curr_perf_string += ";"

                if critical_s is not None:
                    curr_perf_string += ";" + str(critical_s) + "s"
                else:
                    curr_perf_string += ";"

                curr_perf_string += ";; "

        performance_string += curr_perf_string

        obj = ResultForOutput()
        obj.object_name = result.object_name
        measure_dict["exit"] = result.exit
        obj.measures.append(measure_dict)

        exists = False

        for obj_for_output in objects_for_output:
            if obj_for_output.object_name == result.object_name:
                obj_for_output.measures.append(measure_dict)
                exists = True
                break

        if exists == False:
            objects_for_output.append(obj)

    #performance_string = performance_string[:-1]

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
            dummy_result.thresholds = library_json["objects"][object]["measure"]["thresholds"]
            dummy_result.timeout = library_json["objects"][object]["detection"]["timeout_s"]
            dummy_result.output = library_json["objects"][object]["measure"]["output"]
            dummy_result.extended_name = object
            dummy_result.state = 2
            dummy_result.exit = "not_executed"


            objects_result.append(dummy_result)

            measure_dict = {"performance_ms": -1,
                            "accuracy_ms": -1,
                            "timestamp": -1,
                            "records": dummy_result.records,
                            "exit": dummy_result.exit,
                            "resolution": {
                                "width": w,
                                "height": h
                            },
                            # "arguments":result.arguments,
                            "scaling_factor": int(scaling_factor * 100),
                            "name_for_screen": dummy_result.object_name
                            }

            obj = ResultForOutput()
            obj.object_name = dummy_result.object_name
            obj.measures.append(measure_dict)
            objects_for_output.append(obj)


            not_executed_cnt += 1


            #print(object + " NOT EXECUTED")




    t_end = time.time() - t_start

    library_json["script"] = old_script


    message_to_print = ""
    not_exec_print = "NOT EXECUTED transactions: "
    if output_mode == "nagios":
        if sys_exit == 0:
            message_to_print = "OK"
        elif sys_exit == 1:
            message_to_print = "WARNING"
        elif sys_exit == 2 and len(timed_out_objects) == 0:
            message_to_print = "CRITICAL"
        elif sys_exit == 2 and len(timed_out_objects[0]) > 0:
            message_to_print = "CRITICAL: " +  timed_out_objects[0].replace(" ", "_") + " FAILED"

        #print(message_to_print + performance_string)

    else:

        if sys_exit == 0:
            print (get_timestamp_formatted() + ": " + filename_no_extension + " ends OK, it takes " + '{:.3f}'.format(t_end) + "s.")
            exit = "true"
        else:
            print (get_timestamp_formatted() + ": " + filename_no_extension + " ends FAILED because of " + timed_out_objects[0] +", it takes " + '{:.3f}'.format(t_end) + "s.")
            exit = "false"

    om = OutputManager()
    #json_output = om.build_json(chunk, objects_result)

    if verbose >= 2: #or is_foride is True:
        om.save_screenshots(filename_path, objects_for_output, prefix=filename_no_extension)

    if not_executed_cnt > 0:
        if output_mode != "nagios":
            print("    NOT EXECUTED objects:")
        for result in objects_result:
            if result.timestamp == -1:

                if output_mode == "nagios":
                    if result.output is True:
                        warning_s = None
                        critical_s = None

                        curr_perf_string = ""

                        try:
                            warning_s = result.thresholds["warning_s"]
                        except:
                            pass

                        try:
                            critical_s = result.thresholds["critical_s"]
                        except:
                            pass

                        curr_perf_string = result.object_name.replace(" ", "_") + "=ms"

                        if warning_s is not None:
                            curr_perf_string += ";" + str(warning_s) + "s"
                        else:
                            curr_perf_string += ";"

                        if critical_s is not None:
                            curr_perf_string += ";" + str(critical_s) + "s"
                        else:
                            curr_perf_string += ";"

                        curr_perf_string += ";; "

                        performance_string += curr_perf_string

                    not_exec_print += result.object_name.replace(" ", "_") + "; "
                else:
                    print("        " + result.object_name)

        performance_string = performance_string[:-1]

    if output_mode == "nagios":
        if performance_string != "":
            print(message_to_print + "|" + performance_string)
        else:
            print(message_to_print)
        if len(timed_out_objects) > 0:
            failed_to_print = ""
            for obj in timed_out_objects:
                failed_to_print += obj.replace(" ", "_") + "; "
            print("FAILED transactions (from first to last): " + failed_to_print[:-2])

        if not_executed_cnt > 0:
            print(not_exec_print[:-2])

    date_from_ts = datetime.fromtimestamp(timestamp)
    date_formatted = date_from_ts.strftime("%Y%m%d_%H%M%S") + "_UTC" + time.strftime("%z")

    if output_mode != "nagios":
        filename = filename_path + os.sep + filename_no_extension + "_" + date_formatted + ".alyvix"

        #if is_foride is False:
        om.save(filename, lm.get_json(), chunk, objects_for_output, exit, t_end)

    if publish_nats is True:
        nats_manager = NatsManager()
        nats_manager.publish_message(objects_result, start_time=start_time,
                                     server=nats_server,db=nats_db,measure=nats_measure, filename=filename_no_extension)
    sys.exit(sys_exit)
