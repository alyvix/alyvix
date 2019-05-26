from alyvix.ide.server import ServerManager
from alyvix.ide.viewer import ViewerManager
from alyvix.ide.server.utilities.alyvixfile import AlyvixFileManager
from alyvix.tools.screen import ScreenManager
import socket
from multiprocessing import Process
import time
import os.path
from datetime import datetime
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
parser.add_argument('--delay', '-d', help="dummy description for help", type=int, default=0)
parser.add_argument('--object', '-o', help="dummy description for help", type=str, default=None)
parser.add_argument('--window', '-w', help="dummy description for help", type=str2bool, default=True)

#print(parser.format_help())

args = parser.parse_args()



def run_server(port, background_image, scaling_factor):
    #screen_manager = ScreenManager()
    server_manager = ServerManager()


    server_manager.set_background(background_image, scaling_factor)
    server_manager.set_scaling_factor(scaling_factor)
    server_manager.set_object_name(args.object)
    server_manager.set_file_name(args.filename)

    server_manager.run(port)


if __name__ == '__main__':
    if args.filename is not None and args.object is not None:

        if args.delay != 0:

            seconds = args.delay #// 1
            #milliseconds = args.delay - seconds

            print("delay:")

            for i in range(seconds):
                print(str(seconds - i))
                time.sleep(1)

        print("grab desktop")

        screen_manager = ScreenManager()

        background_image = screen_manager.grab_desktop(screen_manager.get_color_mat)
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


        http_process = Process(target=run_server, args=(server_port, background_image, scaling_factor))
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
            viewer_manager.run(url, fullscreen=True)
        else:
            while True:
                pass

        http_process.terminate()
        http_process.join()




