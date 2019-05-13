import json
import time
import os.path
from datetime import datetime
from socket import gethostname
from alyvix.core.engine import EngineManager
from alyvix.tools.library import LibraryManager

import argparse


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

# "alyvix-" + datetime.now().strftime("%H%M%S%Y") + ".json"

parser = argparse.ArgumentParser()
parser.add_argument('--filename', '-f', help="dummy description for help", type=str, default=None)
parser.add_argument('--object', '-o', help="dummy description for help", type=str, default=None)
parser.add_argument('--args', '-a', help="dummy description for help", type=str, default=None)

args = parser.parse_args()
arguments =  args.args

if args.filename is not None:
    lm = LibraryManager()

    lm.load_file(args.filename)

    filename = os.path.basename(args.filename)
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

    json_plus = lm.add_chunk(args.object, {"host": hostname, "user": username, "test": filename, "code": code})

    em = EngineManager(json_plus)

    em.find()

    aaa = None