import json
import time
import sys
import os.path
from datetime import datetime
from socket import gethostname
from alyvix.core.engine import EngineManager
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

    filename = os.path.basename(filename)
    filename = os.path.splitext(filename)[0]

    username = os.environ['username']

    hostname = gethostname()

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
        code += filename[0]
        code += filename[1]
        code += filename[-2]
        code += filename[-1]
    except:
        pass

    engine_manager = EngineManager()

    for object_name in objects_names:
        object_json = lm.add_chunk(object_name, {"host": hostname, "user": username, "test": filename, "code": code})
        engine_manager.execute(object_json, args=engine_arguments)

    aaa = None