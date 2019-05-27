import json
import time
import sys
import os.path
from datetime import datetime
from socket import gethostname
from alyvix.core.engine import EngineManager, Result
from alyvix.core.output import OutputManager
from alyvix.tools.library import LibraryManager


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

    username = os.environ['username']

    hostname = gethostname()

    objects_result = []

    code = ""

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

    timestamp = time.time()

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
    json_string = om.build_json(chunk, objects_result)

    om.save_screenshots(filename_path, objects_result, prefix=filename_no_extension)

    filename = filename_path + os.sep + filename_no_extension + "_" + str(timestamp) + ".alyvix"
    om.save(json_string, filename)


    if state == 0:
        print ("All transactions are ok.")
    else:
        print("One or more transactions are in critical state.")

    for result in objects_result:

        if result.performance_ms != -1:
            print(result.object_name + " perf: " + str(round(result.performance_ms/1000,2)) + "s  +/-" +
                  str(round(result.accuracy_ms/1000,2)) + "s" )
        else:
            print(result.object_name + " perf: null")

    aaa = None