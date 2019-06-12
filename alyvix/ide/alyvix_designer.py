from alyvix.ide.server import ServerManager
from alyvix.ide.viewer import ViewerManager
from alyvix.ide.server.utilities.alyvixfile import AlyvixFileManager
from alyvix.tools.screen import ScreenManager
from alyvix.tools.library import LibraryManager
import socket
from multiprocessing import Process
import time
import os
import os.path
from datetime import datetime
import argparse
import base64
import cv2
import numpy as np

#os.environ["FLASK_ENV"] = "development"


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

# "alyvix-" + datetime.now().strftime("%H%M%S%Y") + ".json"

parser = argparse.ArgumentParser()

requiredNamed = parser.add_argument_group('required named arguments')
requiredNamed.add_argument('--filename', '-f', help="dummy description for help", type=str, default=None, required=True)
requiredNamed.add_argument('--object', '-o', help="dummy description for help", type=str, default=None, required=True)

parser.add_argument('--delay', '-d', help="dummy description for help", type=int, default=0)
parser.add_argument('--window', '-w', help="dummy description for help", type=str2bool, default=True)
parser.add_argument('--verbose', '-v', help="dummy description for help", type=int, default=0)


#print(parser.format_help())

args = parser.parse_args()



def run_server(port, background_image, scaling_factor, verbose):
    #screen_manager = ScreenManager()
    server_manager = ServerManager()


    server_manager.set_background(background_image, scaling_factor)
    server_manager.set_scaling_factor(scaling_factor)
    server_manager.set_object_name(args.object)
    server_manager.set_file_name(args.filename)

    server_manager.run(port, verbose)


if __name__ == '__main__':
    if args.filename is not None and args.object is not None:

        lm = LibraryManager()
        lm.load_file(args.filename)

        screen_manager = ScreenManager()

        if args.delay != 0 and lm.check_if_exist(args.object) is False:

            seconds = args.delay #// 1
            #milliseconds = args.delay - seconds

            print("Counting down")

            for i in range(seconds):
                print(str(seconds - i))
                time.sleep(1)

            print("Frame grabbing!")

            background_image = screen_manager.grab_desktop(screen_manager.get_color_mat)
        elif args.delay == 0 and lm.check_if_exist(args.object) is False:
            print("Frame grabbing!")

            background_image = screen_manager.grab_desktop(screen_manager.get_color_mat)
        elif lm.check_if_exist(args.object) == True:
            alyvix_file_dict = lm.build_objects_for_ide(args.object)

            np_array = np.fromstring(base64.b64decode(alyvix_file_dict["screen"]), np.uint8)

            background_image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

            print("Opening object")

        scaling_factor = screen_manager.get_scaling_factor()

        server_port = 5000

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        while True:
            result = sock.connect_ex(('127.0.0.1', server_port))

            if result != 0:
                break # the port doesn't exist
            else:
                server_port += 1


        sock.close()


        http_process = Process(target=run_server, args=(server_port, background_image, scaling_factor, args.verbose))
        http_process.start()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        while True:
            result = sock.connect_ex(('127.0.0.1', server_port))

            if result == 0:
                break # the port doesn't exist

        sock.close()

        #2 time.sleep(100)

        url = "http://127.0.0.1:" + str(server_port) + "/drawing"

        viewer_manager = ViewerManager()

        if args.window is True:
            # open 2 fds
            null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
            # save the current file descriptors to a tuple
            save = os.dup(1), os.dup(2)
            # put /dev/null fds on 1 and 2
            os.dup2(null_fds[0], 1)
            os.dup2(null_fds[1], 2)

            viewer_manager.run(url, fullscreen=True)

            # restore file descriptors so I can print the results
            os.dup2(save[0], 1)
            os.dup2(save[1], 2)
            # close the temporary fds
            os.close(null_fds[0])
            os.close(null_fds[1])

        else:
            while True:
                pass

        http_process.terminate()
        http_process.join()




