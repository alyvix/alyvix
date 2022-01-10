# Alyvix allows you to automate and monitor all types of applications
# Copyright (C) 2018 Alan Pipitone
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Developer: Alan Pipitone (Violet Atom) - http://www.violetatom.com/
# Supporter: Wuerth Phoenix - http://www.wuerth-phoenix.com/
# Official website: http://www.alyvix.com/

import cv2
import base64
from flask import Flask, request
import logging
import threading
from multiprocessing import Process
from alyvix.core.contouring import ContouringManager
from gevent.pywsgi import WSGIServer
#from geventwebsocket.handler import WebSocketHandler

def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    if request.method == 'OPTIONS':
        response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT'
        headers = request.headers.get('Access-Control-Request-Headers')
        if headers:
            response.headers['Access-Control-Allow-Headers'] = headers
    return response

app = Flask(__name__)
app.after_request(add_cors_headers)

from .views import *

class ServerManager():

    def __init__(self):
        super(ServerManager, self).__init__()

    def run(self, port, log_level=0):
        global app

        if log_level == 0:
            #app.logger.disabled = True

            #log = logging.getLogger('werkzeug')

            #log.disabled = True

            server_log = None

        elif log_level > 0:
            server_log = 'default'

            #logging.basicConfig(level=logging.INFO)

            print("Serving on http://127.0.0.1:" + str(port))

        views.current_port = port

        #app.run(port=port)
        views.loglevel = log_level
        http_server = WSGIServer(('127.0.0.1', port), app, log=server_log)
        views.server_process = http_server
        http_server.serve_forever()


    def set_window(self, window):
        views.win32_window = window

    def set_browser_class(self, browser_class):
        views.browser_class = browser_class

    def set_background(self, background_image, scaling_factor):

        # cv2.imwrite("aaaaaa.png",old_screen)
        png_image = cv2.imencode('.png', background_image)

        views.base64png = base64.b64encode(png_image[1]).decode('ascii')
        views.img_h = int(background_image.shape[0] / scaling_factor)
        views.img_w = int(background_image.shape[1] / scaling_factor)

        views.background_image = background_image

        views.autocontoured_rects = self.auto_contouring(background_image, scaling_factor)
        #cv2.imwrite("d:\\autocc.png",autocimg)

    def set_scaling_factor(self, scaling_factor):
        views.scaling_factor = scaling_factor

    def set_file_name(self, filename):

        views.current_filename = filename

    def set_object_name(self, objectname):

        views.current_objectname = objectname

    def set_json(self, json_dict):
        views.library_dict = json_dict
        views.original_library_dict = copy.deepcopy(json_dict)

    def auto_contouring(self, image, scaling_factor=1):
        contouring_manager = ContouringManager(
            canny_threshold1=250*0.2,
            canny_threshold2=250*0.3,
            canny_apertureSize=3,
            hough_threshold=10,
            hough_minLineLength=30,
            hough_maxLineGap=1,
            line_angle_tolerance=0,
            ellipse_width=2,
            ellipse_height=2,
            text_roi_emptiness=0.45,
            text_roi_proportion=1.3,
            image_roi_emptiness=0.1,
            vline_hw_proportion=2,
            vline_w_maxsize=10,
            hline_wh_proportion=2,
            hline_h_maxsize=10,
            rect_w_minsize=5,
            rect_h_minsize=5,
            rect_w_maxsize_01=800,
            rect_h_maxsize_01=100,
            rect_w_maxsize_02=100,
            rect_h_maxsize_02=800,
            rect_hw_proportion=2,
            rect_hw_w_maxsize=10,
            rect_wh_proportion=2,
            rect_wh_h_maxsize=10,
            hrect_proximity=10,
            vrect_proximity=10,
            vrect_others_proximity=40,
            hrect_others_proximity=80)

        contouring_manager.auto_contouring(image, scaling_factor)

        autocontoured_rects = []
        autocontoured_rects.extend(contouring_manager.getImageBoxes())
        autocontoured_rects.extend(contouring_manager.getRectBoxes())
        autocontoured_rects.extend(contouring_manager.getTextBoxes())

        return autocontoured_rects #contouring_manager.get_debug_image()

    def set_boxes(self, boxes):
        views.current_boxes = boxes

    def set_output_pipeline(self, output_pipeline):
        views.output_pipeline = output_pipeline

