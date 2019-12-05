# Alyvix allows you to automate and monitor all types of applications
# Copyright (C) 2019 Alan Pipitone
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

# -*- coding: utf-8 -*-
import os
import sys
import time
import hmac
import json
import re
import copy
from flask import jsonify

import shutil
import datetime
import mimetypes
from threading import Thread
from hashlib import sha1
#import requests, zipfile, io
from flask import Flask, request, redirect, make_response, render_template, current_app, Markup, g, send_file
from alyvix.ide.server import app
from alyvix.ide.server.lang import en
#from alyvix.ide.server.utilities.alyvixfile import AlyvixFileManager
from alyvix.tools.library import LibraryManager
import logging
import urllib
import time
import re
import io
import base64
import numpy as np
import cv2
from alyvix.ide.viewer import ViewerManager
from alyvix.core.contouring import ContouringManager
from alyvix.core.engine import Roi
from alyvix.core.engine.text import TextManager
from alyvix.tools.screen import ScreenManager
from alyvix.tools.library import LibraryManager
from operator import itemgetter
import threading
import subprocess
import psutil

import tkinter as tk
from tkinter import filedialog
from tkinter import PhotoImage

from PIL import Image

import win32gui
import win32con
import win32com.client

autocontoured_rects = []
base64png = None
background_image = None
scaling_factor = 1
img_h = 0
img_w = 0
current_objectname = None
current_filename = None
#current_json = {}
current_boxes = []
measure = {}
call = {}

original_screens = {}

library_dict = None
library_dict_in_editing = None

win32_window = None
server_process = None
viewer_handler_selector = None
viewer_handler_designer = None
popen_process = None
current_port = None


viewer_manager = None

viewer_process = None

default_object_name = "VisualObject"

browser_class = None

output_pipeline = None

loglevel=None

def detachedProcessFunction(wait_time):
    i=0
    while i<wait_time:
        i = i+1
        print("loop running %d" % i)
        time.sleep(1)


@app.route("/table", methods=['GET', 'POST'])
def index():
    return render_template('table.html', variables={})

@app.route("/panel2", methods=['GET', 'POST'])
def panel2():
    return render_template('panel.html', variables={})

@app.route("/drawing", methods=['GET', 'POST'])
def drawing():
    global library_dict
    text = en.drawing


    lm = LibraryManager()
    lm.set_json(library_dict)
    curr_call = lm.get_call(current_objectname)
    curr_measure = lm.get_measure(current_objectname)
    map_dict = lm.get_map()
    script = lm.get_script()
    win_mouse_x, win_mouse_y = browser_class.get_mouse_pos(browser_class._hwnd_1)
    return render_template('drawing.html', base64url = "data:image/png;base64," + base64png, img_h=img_h, img_w=img_w,
                           autocontoured_rects=autocontoured_rects, text=en.drawing,
                           object_name=current_objectname,
                           measure=curr_measure,
                           call=curr_call,
                           maps=map_dict,
                           script=script,
                           loaded_boxes=current_boxes,
                           win_mouse_x=win_mouse_x,win_mouse_y=win_mouse_y)



@app.route("/panel", methods=['GET', 'POST'])
def panel():

    text = en.drawing

    sm = ScreenManager()
    resolution = sm.get_resolution()
    res_w = resolution[0]
    res_h = resolution[1]
    resolution_string = str(res_w) + "*" + str(res_h) + "@" + str(int(scaling_factor * 100))

    filename_path = os.path.dirname(current_filename)
    filename_no_path = os.path.basename(current_filename)
    filename_no_extension = os.path.splitext(filename_no_path)[0]

    #ide_button_edit_api quando nel selector si cambia selezione

    return render_template('panel.html', res_w=res_w, res_h=res_h, scaling_factor=int(scaling_factor * 100),
                           res_string=resolution_string, current_library_name=filename_no_extension)


@app.route("/ide_selector_index_changed_api", methods=['GET', 'POST'])
def ide_selector_index_changed_api():

    global library_dict
    global library_dict_in_editing
    global current_objectname
    global background_image
    global base64png
    global img_h
    global img_w
    global autocontoured_rects
    global measure


    object_name = request.args.get('object_name')
    current_objectname = object_name
    resolution = request.args.get('resolution')

    lm = LibraryManager()

    lm.set_json(library_dict)

    alyvix_file_dict = lm.build_objects_for_ide(current_objectname, resolution=resolution)

    if bool(alyvix_file_dict):

        np_array = np.frombuffer(base64.b64decode(alyvix_file_dict["screen"]), np.uint8)

        background_image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        contouring_manager = ContouringManager(
            canny_threshold1=250 * 0.2,
            canny_threshold2=250 * 0.3,
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

        contouring_manager.auto_contouring(background_image, scaling_factor)

        autocontoured_rects = []
        autocontoured_rects.extend(contouring_manager.getImageBoxes())
        autocontoured_rects.extend(contouring_manager.getRectBoxes())
        autocontoured_rects.extend(contouring_manager.getTextBoxes())

        object_res = copy.deepcopy(library_dict["objects"][object_name]["components"][resolution])

        library_dict_in_editing = {"objects": {}}
        library_dict_in_editing["objects"][object_name] = {"components": {}}
        library_dict_in_editing["objects"][object_name]["components"][resolution] = object_res
        # library_dict_in_editing["objects"][object_name]["measure"] = copy.deepcopy(library_dict["objects"][object_name]["measure"])
        library_dict_in_editing["objects"][object_name]["detection"] = copy.deepcopy(
            library_dict["objects"][object_name]["detection"])
        library_dict_in_editing["objects"][object_name]["date_modified"] = copy.deepcopy(
            library_dict["objects"][object_name]["date_modified"])
        library_dict_in_editing["objects"][object_name]["call"] = copy.deepcopy(
            library_dict["objects"][object_name]["call"])
        measure = copy.deepcopy(library_dict["objects"][object_name]["measure"])


        #url = "http://127.0.0.1:" + str(current_port) + "/create_thumbnail"

        thumbnail_dict = get_thumbnail(alyvix_file_dict["boxes"], alyvix_file_dict["screen"])


        return_dict = {"background": alyvix_file_dict["screen"], "file_dict":alyvix_file_dict,
                       "autocontoured_rects": autocontoured_rects,
                       "thumbnails": thumbnail_dict}

        return jsonify(return_dict)
    else:
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}



    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

@app.route("/draaawing", methods=['GET', 'POST'])
def draaawing():
    global library_dict
    text = en.drawing


    lm = LibraryManager()
    lm.set_json(library_dict)
    curr_call = lm.get_call(current_objectname)
    curr_measure = lm.get_measure(current_objectname)
    map_dict = lm.get_map()
    script = lm.get_script()
    return render_template('drawing.html', base64url = "data:image/png;base64," + base64png, img_h=img_h, img_w=img_w,
                           autocontoured_rects=autocontoured_rects, text=en.drawing,
                           object_name=current_objectname,
                           measure=curr_measure,
                           call=curr_call,
                           maps=map_dict,
                           script=script,
                           loaded_boxes=current_boxes)




@app.route("/designer_open_file_api")
def designer_open_file_api():
    import tempfile, base64, zlib

    ICON = zlib.decompress(base64.b64decode('eJxjYGAEQgEBBiDJwZDBy'
                                            'sAgxsDAoAHEQCEGBQaIOAg4sDIgACMUj4JRMApGwQgF/ykEAFXxQRc='))

    _, ICON_PATH = tempfile.mkstemp()
    with open(ICON_PATH, 'wb') as icon_file:
        icon_file.write(ICON)

    root = tk.Tk()
    root.withdraw()
    #icon = PhotoImage(height=16, width=16)
    #icon.blank()
    root.iconbitmap(default=ICON_PATH)
    #root.call('wm', 'iconphoto', root._w, PhotoImage(r'server\static\img\icons\transparent_ico.gif'))
    root.call('wm', 'attributes', '.', '-topmost', '1')
    #root.tk.call('wm', 'iconphoto', root._w, icon)
    file_path = filedialog.askopenfilename()
    #print(file_path)

    browser_class._browser_1.ExecuteJavascript("setExePath('" + file_path + "')")

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@app.route("/selector", methods=['GET', 'POST'])
def selector():
    text = en.drawing

    sm = ScreenManager()
    resolution = sm.get_resolution()
    res_w = resolution[0]
    res_h = resolution[1]
    resolution_string = str(res_w) + "*" + str(res_h) + "@" + str(int(scaling_factor * 100))

    filename_path = os.path.dirname(current_filename)
    filename_no_path = os.path.basename(current_filename)
    filename_no_extension = os.path.splitext(filename_no_path)[0]

    return render_template('selector.html', new_url_api='http://127.0.0.1:' + str(current_port) + '/selector_button_new_api',
                           close_url_api='http://127.0.0.1:' + str(
                               current_port) + '/selector_close_api',
                           close_and_shutdown_url_api='http://127.0.0.1:' + str(
                               current_port) + '/selector_shutdown_and_close_api',
                           selector_save_json_api='http://127.0.0.1:' + str(
                               current_port) + '/selector_save_json_api',
                           edit_url_api='http://127.0.0.1:' + str(
                               current_port) + '/selector_button_edit_api',
                           res_w=res_w, res_h=res_h, scaling_factor=int(scaling_factor * 100),
                           res_string=resolution_string, current_library_name=filename_no_extension)

@app.route("/selector_button_new_api", methods=['GET', 'POST'])
def selector_button_new_api():

    global current_objectname
    global background_image
    global base64png
    global img_h
    global img_w
    global popen_process
    global autocontoured_rects
    global measure

    browser_class.hide(browser_class._hwnd_2)

    while True:
        if browser_class.IsWindowVisible(browser_class._hwnd_2) is False \
                and browser_class.IsIconic(browser_class._hwnd_2) is False:
            break

    time.sleep(0.5)

    delay = int(request.args.get('delay'))

    screen_manager = ScreenManager()

    scaling_factor = screen_manager.get_scaling_factor()

    if loglevel == 0:
        os.dup2(output_pipeline[0], 1)
        os.dup2(output_pipeline[1], 2)

    if delay != 0: #and lm.check_if_exist(object) is False:

        seconds = delay #// 1
        #milliseconds = args.delay - seconds

        print("Counting down")

        for i in range(seconds):
            print(str(seconds - i))
            time.sleep(1)

        print("Frame grabbing!")

        background_image = screen_manager.grab_desktop(screen_manager.get_color_mat)
    elif delay == 0: #and lm.check_if_exist(object) is False:
        print("Frame grabbing!")

        background_image = screen_manager.grab_desktop(screen_manager.get_color_mat)

    png_image = cv2.imencode('.png', background_image)

    base64png = base64.b64encode(png_image[1]).decode('ascii')
    img_h = int(background_image.shape[0] / scaling_factor)
    img_w = int(background_image.shape[1] / scaling_factor)

    contouring_manager = ContouringManager(
        canny_threshold1=250 * 0.2,
        canny_threshold2=250 * 0.3,
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

    contouring_manager.auto_contouring(background_image, scaling_factor)

    autocontoured_rects = []
    autocontoured_rects.extend(contouring_manager.getImageBoxes())
    autocontoured_rects.extend(contouring_manager.getRectBoxes())
    autocontoured_rects.extend(contouring_manager.getTextBoxes())


    #viewer_process = threading.Thread(target=process_viewer, args=(current_port,))
    #viewer_process.start()

    object_start_index = 1
    object = default_object_name + str(object_start_index)

    lm = LibraryManager()
    lm.set_json(library_dict)
    while True:
        if lm.check_if_exist(object) is False:
            break

        object_start_index += 1
        object = default_object_name + str(object_start_index)

    current_objectname = object

    url = "http://127.0.0.1:" + str(current_port) + "/drawing"

    browser_class._browser_1.LoadUrl(url)

    browser_class.show(browser_class._hwnd_1)

    if loglevel == 0:
        null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
        os.dup2(null_fds[0], 1)
        os.dup2(null_fds[1], 2)

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@app.route("/selector_button_edit_api", methods=['GET', 'POST'])
def selector_edit_api():

    global library_dict
    global library_dict_in_editing

    global current_objectname
    global background_image
    global base64png
    global img_h
    global img_w
    global popen_process
    global autocontoured_rects
    global measure


    object_name = request.args.get('object_name')
    resolution = request.args.get('resolution')

    browser_class.hide(browser_class._hwnd_2)

    while True:
        if browser_class.IsWindowVisible(browser_class._hwnd_2) is False \
                and browser_class.IsIconic(browser_class._hwnd_2) is False:
            break



    screen_manager = ScreenManager()

    scaling_factor = screen_manager.get_scaling_factor()

    np_array = np.frombuffer(base64.b64decode(library_dict["objects"][object_name]["components"][resolution]["screen"]), np.uint8)

    background_image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)


    png_image = cv2.imencode('.png', background_image)

    base64png = base64.b64encode(png_image[1]).decode('ascii')
    img_h = int(background_image.shape[0] / scaling_factor)
    img_w = int(background_image.shape[1] / scaling_factor)


    object_res = copy.deepcopy(library_dict["objects"][object_name]["components"][resolution])

    library_dict_in_editing = {"objects":{}}
    library_dict_in_editing["objects"][object_name] = {"components": {}}
    library_dict_in_editing["objects"][object_name]["components"][resolution] = object_res
    #library_dict_in_editing["objects"][object_name]["measure"] = copy.deepcopy(library_dict["objects"][object_name]["measure"])
    library_dict_in_editing["objects"][object_name]["detection"] = copy.deepcopy(library_dict["objects"][object_name]["detection"])
    library_dict_in_editing["objects"][object_name]["date_modified"] = copy.deepcopy(library_dict["objects"][object_name]["date_modified"])
    library_dict_in_editing["objects"][object_name]["call"] = copy.deepcopy(library_dict["objects"][object_name]["call"])
    measure = copy.deepcopy(library_dict["objects"][object_name]["measure"])

    current_objectname = object_name

    url = "http://127.0.0.1:" + str(current_port) + "/drawing"

    browser_class.show(browser_class._hwnd_1)

    browser_class._browser_1.LoadUrl(url)


    #hwnd = win32gui.GetForegroundWindow()
    #print(hwnd)
    #print(win32gui.GetWindowText(browser_class._hwnd_1))


    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}



@app.route("/ide_button_new_api", methods=['GET', 'POST'])
def ide_button_new_api():

    global current_objectname
    global background_image
    global base64png
    global img_h
    global img_w
    global popen_process
    global autocontoured_rects
    global measure

    browser_class.hide(browser_class._hwnd_3)

    while True:
        if browser_class.IsWindowVisible(browser_class._hwnd_3) is False \
                and browser_class.IsIconic(browser_class._hwnd_3) is False:
            break

    time.sleep(0.5)

    delay = int(request.args.get('delay'))

    screen_manager = ScreenManager()

    scaling_factor = screen_manager.get_scaling_factor()

    if delay != 0: #and lm.check_if_exist(object) is False:

        seconds = delay #// 1
        #milliseconds = args.delay - seconds

        #print("Counting down")

        for i in range(seconds):
            #print(str(seconds - i))
            time.sleep(1)

        #print("Frame grabbing!")

        background_image = screen_manager.grab_desktop(screen_manager.get_color_mat)
    elif delay == 0: #and lm.check_if_exist(object) is False:
        #print("Frame grabbing!")

        background_image = screen_manager.grab_desktop(screen_manager.get_color_mat)

    png_image = cv2.imencode('.png', background_image)

    base64png = base64.b64encode(png_image[1]).decode('ascii')
    img_h = int(background_image.shape[0] / scaling_factor)
    img_w = int(background_image.shape[1] / scaling_factor)

    contouring_manager = ContouringManager(
        canny_threshold1=250 * 0.2,
        canny_threshold2=250 * 0.3,
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

    contouring_manager.auto_contouring(background_image, scaling_factor)

    autocontoured_rects = []
    autocontoured_rects.extend(contouring_manager.getImageBoxes())
    autocontoured_rects.extend(contouring_manager.getRectBoxes())
    autocontoured_rects.extend(contouring_manager.getTextBoxes())


    #viewer_process = threading.Thread(target=process_viewer, args=(current_port,))
    #viewer_process.start()

    object_start_index = 1
    object = default_object_name + str(object_start_index)

    lm = LibraryManager()
    lm.set_json(library_dict)
    while True:
        if lm.check_if_exist(object) is False:
            break

        object_start_index += 1
        object = default_object_name + str(object_start_index)

    current_objectname = object

    url = "http://127.0.0.1:" + str(current_port) + "/drawing?ide=true"

    browser_class._browser_1.LoadUrl(url)

    browser_class.show(browser_class._hwnd_1)

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@app.route("/ide_button_edit_api", methods=['GET', 'POST'])
def ide_edit_api():

    global library_dict
    global library_dict_in_editing

    global current_objectname
    global background_image
    global base64png
    global img_h
    global img_w
    global popen_process
    global autocontoured_rects
    global measure


    object_name = request.args.get('object_name')
    resolution = request.args.get('resolution')

    browser_class.hide(browser_class._hwnd_3)

    while True:
        if browser_class.IsWindowVisible(browser_class._hwnd_3) is False \
                and browser_class.IsIconic(browser_class._hwnd_3) is False:
            break



    screen_manager = ScreenManager()

    scaling_factor = screen_manager.get_scaling_factor()

    np_array = np.frombuffer(base64.b64decode(library_dict["objects"][object_name]["components"][resolution]["screen"]), np.uint8)

    background_image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)


    png_image = cv2.imencode('.png', background_image)

    base64png = base64.b64encode(png_image[1]).decode('ascii')
    img_h = int(background_image.shape[0] / scaling_factor)
    img_w = int(background_image.shape[1] / scaling_factor)


    object_res = copy.deepcopy(library_dict["objects"][object_name]["components"][resolution])

    library_dict_in_editing = {"objects":{}}
    library_dict_in_editing["objects"][object_name] = {"components": {}}
    library_dict_in_editing["objects"][object_name]["components"][resolution] = object_res
    #library_dict_in_editing["objects"][object_name]["measure"] = copy.deepcopy(library_dict["objects"][object_name]["measure"])
    library_dict_in_editing["objects"][object_name]["detection"] = copy.deepcopy(library_dict["objects"][object_name]["detection"])
    library_dict_in_editing["objects"][object_name]["date_modified"] = copy.deepcopy(library_dict["objects"][object_name]["date_modified"])
    library_dict_in_editing["objects"][object_name]["call"] = copy.deepcopy(library_dict["objects"][object_name]["call"])
    measure = copy.deepcopy(library_dict["objects"][object_name]["measure"])

    current_objectname = object_name

    qstring = str(request.query_string, 'utf-8')

    url = "http://127.0.0.1:" + str(current_port) + "/drawing?" + qstring

    browser_class.show(browser_class._hwnd_1)

    browser_class._browser_1.LoadUrl(url)


    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/selector_close_api", methods=['GET'])
def selector_close_api():

    func = request.environ.get('werkzeug.server.shutdown')
    if func is not None:
        func()
    else:
        # raise RuntimeError('Not running with the Werkzeug Server')
        server_process.close()

    #popen_process.kill()
    #import signal
    #os.killpg(os.getpgid(popen_process.pid), signal.SIGTERM)
    #os.kill(popen_process.pid, signal.CTRL_C_EVENT)


    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@app.route("/selector_shutdown_and_close_api", methods=['GET'])
def selector_shutdown_and_close_api():

    """
    func = request.environ.get('werkzeug.server.shutdown')
    if func is not None:
        func()
    else:
        # raise RuntimeError('Not running with the Werkzeug Server')
        server_process.close()
    """

    browser_class.close()

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


@app.route("/set_viewer_handler_api", methods=['GET'])
def set_viewer_handler_api():
    global viewer_handler_selector
    global viewer_handler_designer

    handler = request.args.get('handler')
    type = request.args.get('type')

    if type == 'designer':
        viewer_handler_designer = int(handler)
    elif type == 'selector':
        viewer_handler_selector = int(handler)

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@app.route("/load_objects", methods=['GET'])
def load_objects():
    global autocontoured_rects
    global library_dict_in_editing

    lm = LibraryManager()

    lm.set_json(library_dict)

    if library_dict_in_editing is None:
        alyvix_file_dict = lm.build_objects_for_ide(current_objectname)
    else:
        alyvix_file_dict = lm.build_objects_for_ide(current_objectname, library_dict_in_editing)

    if bool(alyvix_file_dict):

        np_array = np.frombuffer(base64.b64decode(alyvix_file_dict["screen"]), np.uint8)

        background_image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        contouring_manager = ContouringManager(
            canny_threshold1=250 * 0.2,
            canny_threshold2=250 * 0.3,
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

        contouring_manager.auto_contouring(background_image, scaling_factor)

        autocontoured_rects = []
        autocontoured_rects.extend(contouring_manager.getImageBoxes())
        autocontoured_rects.extend(contouring_manager.getRectBoxes())
        autocontoured_rects.extend(contouring_manager.getTextBoxes())


        return_dict = {"file_dict":alyvix_file_dict, "autocontoured_rects": autocontoured_rects}

        #print(alyvix_file_dict)

        return jsonify(return_dict)
    elif lm.check_if_detection_exist(current_objectname):
        alyvix_file_dict = lm.get_detection(current_objectname)
        return_dict = {"file_dict":alyvix_file_dict}
        return jsonify(return_dict)
    else:
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

@app.route("/cancel_event", methods=['GET'])
def cancel_event():

    if browser_class._hwnd_2 is None:
        func = request.environ.get('werkzeug.server.shutdown')
        if func is not None:
            func()
        else:
            #raise RuntimeError('Not running with the Werkzeug Server')
            server_process.close()



    if browser_class._hwnd_2 is not None:
        browser_class.hide(browser_class._hwnd_1)
        browser_class._browser_1.LoadUrl("http://127.0.0.1:" + str(current_port) + "/static/blank.html")

        browser_class.show(browser_class._hwnd_2)
    else:

        browser_class.close()

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@app.route("/save_json", methods=['GET', 'POST'])
def save_json():
    global library_dict
    global browser_class
    global library_dict_in_editing
    global img_h
    global img_w

    if request.method == 'POST':

        current_json = {}

        if browser_class._hwnd_2 is None and browser_class._hwnd_3 is None:
            try:
                with open(current_filename) as f:
                    current_json = json.load(f)
            except:
                pass
        else: #elif library_dict_in_editing is None:
            current_json = library_dict
        #elif library_dict_in_editing is not None:
        #    current_json = library_dict_in_editing

        json_data = json.loads(request.data)
        object_name = json_data['object_name']

        object_name = object_name.lstrip()
        object_name = object_name.rstrip()

        invalid_chars = re.findall("[^a-zA-Z0-9_\- ]+", object_name)

        if len(invalid_chars) > 0:
            return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

        detection = json_data['detection']

        background = json_data['background']

        box_list = json_data['box_list']


        curr_call = json_data.get("call", {})


        curr_measure = json_data.get("measure", {})
        curr_output = curr_measure.get("output", True)
        curr_thresholds = curr_measure.get("thresholds", {})

        curr_script = current_json.get("script",{
                        "case": [

                        ],
                        "sections": {
                            "exit": [],
                            "fail": []
                        }
                    })
        curr_maps = current_json.get("maps", {})

        curr_object_list_dict = current_json.get("objects", {})

        curr_object_dict = curr_object_list_dict.get(object_name, {})



        curr_object_dict["detection"] = detection

        curr_components = curr_object_dict.get("components", {})

        background = background.replace("data:image/png;base64,", "")

        #np_array = np.frombuffer(base64.b64decode(background), np.uint8)
        #background_image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        #img_h = background_image.shape[0]
        #img_w = background_image.shape[1]

        resolution_string = str(int(img_w*scaling_factor)) + "*" + str(int(img_h*scaling_factor)) + "@" + str(int(scaling_factor*100))

        curr_components[resolution_string] = {}

        curr_components[resolution_string]["screen"] = background

        main_0 = {}
        subs_0 = []
        main_1 = {}
        subs_1 = []
        main_2 = {}
        subs_2 = []

        groups_dict = []

        main = {}
        sub = {}

        for box in box_list:

            dict_box = {}


            if box["is_main"] == True:
                main = {}
                main["visuals"] = {}

                main["visuals"]["roi"] = \
                    {"screen_x": int(box["roi_x"]*scaling_factor), "screen_y": int(box["roi_y"]*scaling_factor),
                     "width": int(box["roi_w"]*scaling_factor), "height": int(box["roi_h"]*scaling_factor),
                     "unlimited_left": box["roi_unlimited_left"], "unlimited_up": box["roi_unlimited_up"],
                     "unlimited_right": box["roi_unlimited_right"], "unlimited_down": box["roi_unlimited_down"]}

                main["visuals"]["selection"] = \
                    {"roi_dx":  int((box["x"] - box["roi_x"])*scaling_factor),
                     "roi_dy": int((box["y"] - box["roi_y"])*scaling_factor),
                     "width": int(box["w"]*scaling_factor), "height": int(box["h"]*scaling_factor)}


                #main["visuals"]["detection"] = {}
                detection_dict = {}

                if box["type"] == "I":
                    detection_dict["type"] = "image"
                    detection_dict["features"] = box["features"]["I"]
                elif box["type"] == "R":
                    detection_dict["type"] = "rectangle"
                    detection_dict["features"] = box["features"]["R"]

                    detection_dict["features"]["width"]["min"] = \
                        int(detection_dict["features"]["width"]["min"] * scaling_factor)

                    detection_dict["features"]["width"]["max"] = \
                        int(detection_dict["features"]["width"]["max"] * scaling_factor)

                    detection_dict["features"]["height"]["min"] =\
                        int(detection_dict["features"]["height"]["min"]*scaling_factor)

                    detection_dict["features"]["height"]["max"] =\
                        int(detection_dict["features"]["height"]["max"]*scaling_factor)
                elif box["type"] == "T":
                    detection_dict["type"] = "text"
                    detection_dict["features"] = box["features"]["T"]

                main["detection"] = detection_dict

                interaction_dict = {}
                interaction_dict["mouse"] = {"features":{}}
                interaction_dict["keyboard"] = {}

                if box["mouse"]["type"] == None:
                    interaction_dict["mouse"]["type"] = "none"
                    interaction_dict["mouse"]["features"] = None
                elif box["mouse"]["type"] == "move":
                    interaction_dict["mouse"]["type"] = "move"

                    if box["mouse"]["features"]["point"]["dx"] != 0 or box["mouse"]["features"]["point"]["dy"] != 0:
                        interaction_dict["mouse"]["features"]["point"] = \
                            {"dx": int((box["mouse"]["features"]["point"]["dx"] - box["x"])*scaling_factor),
                             "dy": int((box["mouse"]["features"]["point"]["dy"] - box["y"])*scaling_factor)}
                    else:
                        interaction_dict["mouse"]["features"]["point"] = {"dx": 0, "dy": 0}

                elif box["mouse"]["type"] == "click":
                    interaction_dict["mouse"]["type"] = "click"

                    if box["mouse"]["features"]["point"]["dx"] != 0 or box["mouse"]["features"]["point"]["dy"] != 0:
                        interaction_dict["mouse"]["features"]["point"] = \
                            {"dx": int((box["mouse"]["features"]["point"]["dx"] - box["x"])*scaling_factor),
                             "dy": int((box["mouse"]["features"]["point"]["dy"] - box["y"])*scaling_factor)}
                    else:
                        interaction_dict["mouse"]["features"]["point"] = {"dx": 0, "dy": 0}

                    interaction_dict["mouse"]["features"]["button"] = box["mouse"]["features"]["button"]
                    interaction_dict["mouse"]["features"]["amount"] = box["mouse"]["features"]["amount"]
                    interaction_dict["mouse"]["features"]["delays_ms"] = box["mouse"]["features"]["delays_ms"]

                elif box["mouse"]["type"] == "scroll":
                    interaction_dict["mouse"]["type"] = "scroll"
                    if box["mouse"]["features"]["point"]["dx"] != 0 or box["mouse"]["features"]["point"]["dy"] != 0:
                        interaction_dict["mouse"]["features"]["point"] = \
                            {"dx": int((box["mouse"]["features"]["point"]["dx"] - box["x"])*scaling_factor),
                             "dy": int((box["mouse"]["features"]["point"]["dy"] - box["y"])*scaling_factor)}
                    else:
                        interaction_dict["mouse"]["features"]["point"] = {"dx": 0, "dy": 0}
                    interaction_dict["mouse"]["features"]["amount"] = box["mouse"]["features"]["amount"]
                    interaction_dict["mouse"]["features"]["delays_ms"] = box["mouse"]["features"]["delays_ms"]
                    interaction_dict["mouse"]["features"]["direction"] = box["mouse"]["features"]["direction"]

                elif box["mouse"]["type"] == "hold":
                    interaction_dict["mouse"]["type"] = "hold"
                    if box["mouse"]["features"]["point"]["dx"] != 0 or box["mouse"]["features"]["point"]["dy"] != 0:
                        interaction_dict["mouse"]["features"]["point"] = \
                            {"dx": int((box["mouse"]["features"]["point"]["dx"] - box["x"])*scaling_factor),
                             "dy": int((box["mouse"]["features"]["point"]["dy"] - box["y"])*scaling_factor)}
                    else:
                        interaction_dict["mouse"]["features"]["point"] = {"dx": 0, "dy": 0}
                    interaction_dict["mouse"]["features"]["button"] = "left" #box["mouse"]["features"]["button"]

                elif box["mouse"]["type"] == "release":
                    interaction_dict["mouse"]["type"] = "release"
                    if box["mouse"]["features"]["point"]["dx"] != 0 or box["mouse"]["features"]["point"]["dy"] != 0:
                        interaction_dict["mouse"]["features"]["point"] = \
                            {"dx": int((box["mouse"]["features"]["point"]["dx"] - box["x"])*scaling_factor),
                             "dy": int((box["mouse"]["features"]["point"]["dy"] - box["y"])*scaling_factor)}
                    else:
                        interaction_dict["mouse"]["features"]["point"] = {"dx": 0, "dy": 0}
                    interaction_dict["mouse"]["features"]["button"] = "left" #box["mouse"]["features"]["button"]
                    interaction_dict["mouse"]["features"]["direction"] = box["mouse"]["features"]["direction"]
                    interaction_dict["mouse"]["features"]["pixels"] = box["mouse"]["features"]["pixels"]

                interaction_dict["keyboard"] = box["keyboard"]

                #main["mouse"] = interaction_dict["mouse"]
                #main["keyboard"] = interaction_dict["keyboard"]

                main["interactions"] = interaction_dict

                if box["group"] == 0:
                    main_0 = main
                elif box["group"] == 1:
                    main_1 = main
                elif box["group"] == 2:
                    main_2 = main

            else:


                sub = {}
                sub["visuals"] = {}

                main_dx = 0
                main_dy = 0

                if box["group"] == 0:
                    main_dx = int(box["roi_x"]*scaling_factor) - (main_0["visuals"]["roi"]["screen_x"] +
                                              main_0["visuals"]["selection"]["roi_dx"])
                elif box["group"] == 1:
                    main_dx = int(box["roi_x"]*scaling_factor) - (main_1["visuals"]["roi"]["screen_x"] +
                                              main_1["visuals"]["selection"]["roi_dx"])
                elif box["group"] == 2:
                    main_dx = int(box["roi_x"]*scaling_factor) - (main_2["visuals"]["roi"]["screen_x"] +
                                              main_2["visuals"]["selection"]["roi_dx"])

                if box["group"] == 0:
                    main_dy = int(box["roi_y"]*scaling_factor) - (main_0["visuals"]["roi"]["screen_y"] +
                                              main_0["visuals"]["selection"]["roi_dy"])
                elif box["group"] == 1:
                    main_dy = int(box["roi_y"]*scaling_factor) - (main_1["visuals"]["roi"]["screen_y"] +
                                              main_1["visuals"]["selection"]["roi_dy"])
                elif box["group"] == 2:
                    main_dy = int(box["roi_y"]*scaling_factor) - (main_2["visuals"]["roi"]["screen_y"] +
                                              main_2["visuals"]["selection"]["roi_dy"])

                sub["visuals"]["roi"] = \
                    {"main_dx": main_dx, "main_dy": main_dy,
                     "width": int(box["roi_w"]*scaling_factor), "height": int(box["roi_h"]*scaling_factor),
                     "unlimited_left": box["roi_unlimited_left"], "unlimited_up": box["roi_unlimited_up"],
                     "unlimited_right": box["roi_unlimited_right"], "unlimited_down": box["roi_unlimited_down"]}

                sub["visuals"]["selection"] = \
                    {"roi_dx": int((box["x"] - box["roi_x"])*scaling_factor),
                     "roi_dy": int(box["y"]*scaling_factor) - int(box["roi_y"]*scaling_factor),
                     "width": int(box["w"]*scaling_factor), "height": int(box["h"]*scaling_factor)}

                # sub["visuals"]["detection"] = {}
                detection_dict = {}

                if box["type"] == "I":
                    detection_dict["type"] = "image"
                    detection_dict["features"] = box["features"]["I"]
                elif box["type"] == "R":
                    detection_dict["type"] = "rectangle"
                    detection_dict["features"] = box["features"]["R"]

                    detection_dict["features"]["width"]["min"] = \
                        int(detection_dict["features"]["width"]["min"] * scaling_factor)

                    detection_dict["features"]["width"]["max"] = \
                        int(detection_dict["features"]["width"]["max"] * scaling_factor)

                    detection_dict["features"]["height"]["min"] =\
                        int(detection_dict["features"]["height"]["min"]*scaling_factor)

                    detection_dict["features"]["height"]["max"] =\
                        int(detection_dict["features"]["height"]["max"]*scaling_factor)

                elif box["type"] == "T":
                    detection_dict["type"] = "text"
                    detection_dict["features"] = box["features"]["T"]

                sub["detection"] = detection_dict

                interaction_dict = {}
                interaction_dict["mouse"] = {"features": {}}
                interaction_dict["keyboard"] = {}

                aaa = box["mouse"]["type"]
                if box["mouse"]["type"] == None:
                    interaction_dict["mouse"]["type"] = "none"
                    interaction_dict["mouse"]["features"] = None
                elif box["mouse"]["type"] == "move":
                    interaction_dict["mouse"]["type"] = "move"
                    if box["mouse"]["features"]["point"]["dx"] != 0 or box["mouse"]["features"]["point"]["dy"] != 0:
                        interaction_dict["mouse"]["features"]["point"] = \
                            {"dx": int((box["mouse"]["features"]["point"]["dx"] - box["x"])*scaling_factor),
                             "dy": int((box["mouse"]["features"]["point"]["dy"] - box["y"])*scaling_factor)}
                    else:
                        interaction_dict["mouse"]["features"]["point"] = {"dx": 0, "dy": 0}

                elif box["mouse"]["type"] == "click":
                    interaction_dict["mouse"]["type"] = "click"
                    if box["mouse"]["features"]["point"]["dx"] != 0 or box["mouse"]["features"]["point"]["dy"] != 0:
                        interaction_dict["mouse"]["features"]["point"] = \
                            {"dx": int((box["mouse"]["features"]["point"]["dx"] - box["x"])*scaling_factor),
                             "dy": int((box["mouse"]["features"]["point"]["dy"] - box["y"])*scaling_factor)}
                    else:
                        interaction_dict["mouse"]["features"]["point"] = {"dx": 0, "dy": 0}
                    interaction_dict["mouse"]["features"]["button"] = box["mouse"]["features"]["button"]
                    interaction_dict["mouse"]["features"]["amount"] = box["mouse"]["features"]["amount"]
                    interaction_dict["mouse"]["features"]["delays_ms"] = box["mouse"]["features"]["delays_ms"]

                elif box["mouse"]["type"] == "scroll":
                    interaction_dict["mouse"]["type"] = "scroll"
                    if box["mouse"]["features"]["point"]["dx"] != 0 or box["mouse"]["features"]["point"]["dy"] != 0:
                        interaction_dict["mouse"]["features"]["point"] = \
                            {"dx": int((box["mouse"]["features"]["point"]["dx"] - box["x"])*scaling_factor),
                             "dy": int((box["mouse"]["features"]["point"]["dy"] - box["y"])*scaling_factor)}
                    else:
                        interaction_dict["mouse"]["features"]["point"] = {"dx": 0, "dy": 0}
                    interaction_dict["mouse"]["features"]["amount"] = box["mouse"]["features"]["amount"]
                    interaction_dict["mouse"]["features"]["delays_ms"] = box["mouse"]["features"]["delays_ms"]
                    interaction_dict["mouse"]["features"]["direction"] = box["mouse"]["features"]["direction"]

                elif box["mouse"]["type"] == "hold":
                    interaction_dict["mouse"]["type"] = "hold"
                    if box["mouse"]["features"]["point"]["dx"] != 0 or box["mouse"]["features"]["point"]["dy"] != 0:
                        interaction_dict["mouse"]["features"]["point"] = \
                            {"dx": int((box["mouse"]["features"]["point"]["dx"] - box["x"])*scaling_factor),
                             "dy": int((box["mouse"]["features"]["point"]["dy"] - box["y"])*scaling_factor)}
                    else:
                        interaction_dict["mouse"]["features"]["point"] = {"dx": 0, "dy": 0}
                    interaction_dict["mouse"]["features"]["button"] = "left" #box["mouse"]["features"]["button"]

                elif box["mouse"]["type"] == "release":
                    interaction_dict["mouse"]["type"] = "release"
                    if box["mouse"]["features"]["point"]["dx"] != 0 or box["mouse"]["features"]["point"]["dy"] != 0:
                        interaction_dict["mouse"]["features"]["point"] = \
                            {"dx": int((box["mouse"]["features"]["point"]["dx"] - box["x"])*scaling_factor),
                             "dy": int((box["mouse"]["features"]["point"]["dy"] - box["y"])*scaling_factor)}
                    else:
                        interaction_dict["mouse"]["features"]["point"] = {"dx": 0, "dy": 0}
                    interaction_dict["mouse"]["features"]["button"] = "left" #box["mouse"]["features"]["button"]
                    interaction_dict["mouse"]["features"]["direction"] = box["mouse"]["features"]["direction"]
                    interaction_dict["mouse"]["features"]["pixels"] = box["mouse"]["features"]["pixels"]

                interaction_dict["keyboard"] = box["keyboard"]

                #sub["mouse"] = interaction_dict["mouse"]
                #sub["keyboard"] = interaction_dict["keyboard"]

                sub["interactions"] = interaction_dict

                if box["group"] == 0:
                    subs_0.append(sub)
                elif box["group"] == 1:
                    subs_1.append(sub)
                elif box["group"] == 2:
                    subs_2.append(sub)

        curr_components[resolution_string]["groups"] = []


        if len(subs_0) < 4:
            for i in range(4 - len(subs_0)):
                subs_0.append({})

        if len(subs_1) < 4:
            for i in range(4 - len(subs_1)):
                subs_1.append({})

        if len(subs_2) < 4:
            for i in range(4 - len(subs_2)):
                subs_2.append({})

        curr_components[resolution_string]["groups"].append({"main": main_0, "subs": subs_0})
        curr_components[resolution_string]["groups"].append({"main": main_1, "subs": subs_1})
        curr_components[resolution_string]["groups"].append({"main": main_2, "subs": subs_2})

        current_json["script"] = curr_script
        current_json["maps"] = curr_maps

        current_json["objects"] = curr_object_list_dict

        current_json["objects"][object_name] = curr_object_dict
        current_json["objects"][object_name]["call"] = curr_call

        current_json["objects"][object_name]["measure"] = curr_measure
        current_json["objects"][object_name]["measure"]["output"] = curr_output
        current_json["objects"][object_name]["measure"]["thresholds"] = curr_thresholds

        current_json["objects"][object_name]["components"] = curr_components


        if object_name != current_objectname:
            if current_objectname in current_json["objects"]:
                del current_json["objects"][current_objectname]

        current_json["objects"][object_name]["date_modified"] = \
            datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S") + " UTC" + time.strftime("%z")


        if browser_class._browser_2 is not None:

            library_dict_in_editing = None

            browser_class._browser_2.ExecuteJavascript("reloadAlyvixSelector('" + object_name + "')")
            browser_class.show(browser_class._hwnd_2)

        elif browser_class._browser_3 is not None:
            library_dict_in_editing = None
            browser_class._browser_3.ExecuteJavascript("reloadAlyvixIde('" + object_name + "')")

            from_ide = None

            try:
                from_ide = json_data['designerFromEditor']
            except:
                pass

            if from_ide is None:

                browser_class.show(browser_class._hwnd_3)
                browser_class.hide(browser_class._hwnd_1)
        else:

            with open(current_filename, 'w') as f:
                json.dump(current_json, f, indent=4, sort_keys=True, ensure_ascii=False)

            browser_class.close()

        aaa = "asas"
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@app.route("/selector_save_json_api", methods=['GET', 'POST'])
def selector_save_json_api():

    global library_dict

    curr_script = library_dict.get("script", {
                        "case": [

                        ],
                        "sections": {
                            "exit": [],
                            "fail": []
                        }
                    })

    library_dict["script"] = curr_script

    with open(current_filename, 'w') as f:
        json.dump(library_dict, f, indent=4, sort_keys=True, ensure_ascii=False)

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

@app.route("/get_user_process_api")
def list_user_process_api():
    proc_list = []
    for proc in psutil.process_iter(attrs=['name', 'username']):

        try:
            logged_user = os.environ['userdomain'] + "\\" +  os.environ.get( "USERNAME" ) #os.getlogin()
            proc_user = proc.username()

            if proc_user == logged_user:
                proc_list.append(proc.name())
        except:
            pass

    return json.dumps({'object_exists': proc_list}), 200, {'ContentType': 'application/json'}

@app.route("/check_if_object_exists_api")
def check_if_object_exists_api():
    global library_dict
    obj_name = request.args.get("object_name")

    lm = LibraryManager()
    lm.set_json(library_dict)

    all_res_exists = False

    #if lm.check_if_any_res_exists(obj_name) is True:
    #    all_res_exists = True

    if lm.check_if_exist(obj_name) is True:
        all_res_exists = True

    return json.dumps({'object_exists': all_res_exists}), 200, {'ContentType': 'application/json'}

@app.route("/get_library_api", methods=['GET'])
def get_library_api():
    global library_dict
    global original_screens

    ret_dict = copy.deepcopy(library_dict)

    """
    #check if dict is empty
    if bool(ret_dict) == True:

        objects = ret_dict["objects"]

        original_screens = {}

        id = 0

        #REMOVE SCREEN
        for obj in objects:
            #object_name = list(obj.keys())[0]
            components = objects[obj]["components"]
            objects[obj]["id"] = id

            #original_screens[obj] = {}
            original_screens[id] = {}

            for cmp in components:
                original_screens[id][cmp] = {}
                original_screens[id][cmp]["screen"] = components[cmp]["screen"]

                #del(components[cmp]["screen"])

                base64_img = components[cmp]["screen"]
                np_array = np.frombuffer(base64.b64decode(base64_img), np.uint8)
                cv_image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
                background_w = cv_image.shape[1]
                background_h = cv_image.shape[0]
                thumbnail_fixed_height = 80
                thumbnail_fixed_width = int((background_w * thumbnail_fixed_height) / background_h)

                dim = (thumbnail_fixed_width, thumbnail_fixed_height)

                resized = cv2.resize(cv_image, dim, interpolation=cv2.INTER_CUBIC)
                png_image = cv2.imencode('.png', resized)
                base64png = base64.b64encode(png_image[1]).decode('ascii')

                components[cmp]["screen"] = base64png

            id += 1

    """
    return jsonify(ret_dict)


@app.route("/set_library_api", methods=['POST'])
def set_library_api():
    global library_dict
    global original_screens

    json_string = json.loads(request.data)

    objects = json_string["library"]["objects"]

    #reconstruct comp
    for obj in objects:

        components = objects[obj]["components"]

        for cmp in components:
            try:
                components[cmp]["screen"] = original_screens[objects[obj]["id"]][cmp]["screen"]
            except:
                pass #object was imported from other library

        try:
            del objects[obj]["id"]
        except:
            pass #object was imported from other library

        datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S") + " UTC" + time.strftime("%z")

        try:
            if objects[obj] != library_dict["objects"][obj]:
                objects[obj]["date_modified"] = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S") +\
                                                " UTC" + time.strftime("%z")
        except:
            objects[obj]["date_modified"] = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S") +\
                                            " UTC" + time.strftime("%z")

    curr_script = json_string["library"].get("script", {
                        "case": [

                        ],
                        "sections": {
                            "exit": [],
                            "fail": []
                        }
                    })
    curr_maps = json_string["library"].get("maps", {})

    json_string["library"]["script"] = curr_script
    json_string["library"]["maps"] = curr_maps

    library_dict = json_string["library"]

    if json_string["close_selector"] is True:
        with open(current_filename, 'w') as f:
            json.dump(library_dict, f, indent=4, sort_keys=True, ensure_ascii=False)

        selector_shutdown_and_close_api()

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@app.route("/get_scraped_txt", methods=['GET', 'POST'])
def get_scraped_txt():
    if request.method == 'POST':

        json_data = json.loads(request.data)

        roi = Roi()
        roi.x = int(json_data["roi_x"]*scaling_factor)
        roi.y = int(json_data["roi_y"]*scaling_factor)
        roi.w = int(json_data["roi_w"]*scaling_factor)
        roi.h = int(json_data["roi_h"]*scaling_factor)
        roi.unlimited_left = json_data["roi_unlimited_left"]
        roi.unlimited_up = json_data["roi_unlimited_up"]
        roi.unlimited_right = json_data["roi_unlimited_right"]
        roi.unlimited_down = json_data["roi_unlimited_down"]

        tm = TextManager()
        tm.set_color_screen(background_image)
        tm.set_gray_screen(cv2.cvtColor(background_image, cv2.COLOR_BGR2GRAY))
        tm.set_scaling_factor(scaling_factor)

        results = tm.scrape(roi=roi)
        scraped_text = results[0].scraped_text
        scraped_text = scraped_text.lstrip().rstrip()

        #white_list = 'abcdefghilmnopqrstuvzxyw1234567890'

        reg_exp = re.sub('[^A-Za-z0-9]+', '.*', scraped_text)


        ret_dict = {'scraped_text': scraped_text, 'reg_exp': reg_exp.lower()}

        return jsonify(ret_dict)

@app.route("/test_txt_regexp", methods=['GET', 'POST'])
def test_txt_regexp():
    if request.method == 'POST':

        json_data = json.loads(request.data)

        regexp = json_data["regexp"]
        scraped_text = json_data["scraped_text"]

        #args_in_string = re.findall("\\{[1-9]\d*\\}|\\{.*\\.extract\\}|\\{.*\\.text\\}|\\{.*\\.check\\}|\\{.*\\..*\\}",
        #                            regexp, re.IGNORECASE)

        args_in_string = re.findall("\\{[1-9]\d*\\}|\\{.*\\..*\\}", regexp, re.IGNORECASE)

        if len(args_in_string) > 0:
            ret_dict = {'match': 'yellow'}
        else:

            result = re.match(".*" + regexp + ".*", scraped_text, re.DOTALL | re.IGNORECASE)

            if result is None:

                ret_dict = {'match': 'red'}
            else:
                ret_dict = {'match': 'green'}

        return jsonify(ret_dict)

@app.route("/check_number_api", methods=['GET', 'POST'])
def check_number_api():

    ret_dict = {"result":False}

    if request.method == 'POST':
        json_data = json.loads(request.data)

        scraped_text = json_data["scraped_text"]
        logic = json_data["logic"]

        try:
            result = re.search(r'(-[ ]{0,}\d+|\d+)', scraped_text).group()

            int_result = int(result.replace(" ",""))

            if logic == "more_than_zero":
                if int_result > 0:
                    ret_dict = {"result": True}
                else:
                    ret_dict = {"result": False}
        except:
            pass


    return jsonify(ret_dict)

@app.route("/check_date_api", methods=['GET', 'POST'])
def check_date_api():

    ret_dict = {"result":False} #pass

    if request.method == 'POST':
        json_data = json.loads(request.data)

        scraped_text = json_data["scraped_text"]
        logic = json_data["logic"]


        tm = TextManager()

        scraped_text_one_space = re.sub(r'\s+', ' ', scraped_text.lower()).strip()

        date = tm._get_date_str(scraped_text_one_space)

        hour = tm._get_hour_str(scraped_text_one_space)

        date_time = None
        if date[0] != "" and hour[0] != "":
            date_time = datetime.datetime.strptime(date[0] + " " + hour[0], date[1] + " " + hour[1])

        elif date[0] != "" and hour[0] == "":
            date_time = datetime.datetime.strptime(date[0], date[1])

        elif date[0] == "" and hour[0] != "":
            date_time = datetime.datetime.strptime(hour[0], hour[1])
            date_now = datetime.datetime.now()
            date_now = date_now.replace(hour=date_time.hour, minute=date_time.minute, second=date_time.second)
            date_time = date_now

        ret_dict = {"result": False}

        if date_time is not None:

            date_now = datetime.datetime.now()
            if date_time.hour == 0 and date_time.minute == 0 and date_time.second == 0:
                date_time = date_time.replace(hour=date_now.hour, minute=date_now.minute, second=date_now.second,
                                              microsecond=date_now.microsecond)

            if logic == "last_hour":
                if date_time >= date_now - datetime.timedelta(hours=1):
                    ret_dict = {"result": True}
            elif logic == "last_day":
                if date_time >= date_now - datetime.timedelta(days=1):
                    ret_dict = {"result": True}
            elif logic == "last_week":
                if date_time >= date_now - datetime.timedelta(days=7):
                    ret_dict = {"result": True}
            elif logic == "last_month":
                if date_time >= date_now - datetime.timedelta(days=31):
                    ret_dict = {"result": True}


    return jsonify(ret_dict)

@app.route("/create_thumbnail", methods=['POST'])
def create_thumbnail():
    if request.method == 'POST':

        #thumbnail_fixed_height = int(30 * scaling_factor)
        #border = int(4*scaling_factor)


        json_data = json.loads(request.data)

        dict_list = json_data['box_list']

        if len(dict_list) > 0:
            last_dict = dict_list[-1]  #get last dict of the array
        background_string = json_data["background"]
        background_string = background_string[22:]

        return get_thumbnail(dict_list, background_string, from_url=True)


def get_thumbnail(dict_list, background_string, from_url=False):
    global img_h
    global img_w

    thumbnail_fixed_height = 30
    border = 4

    np_array = np.frombuffer(base64.b64decode(background_string), np.uint8)

    ori_background_image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)


    new_width = int(ori_background_image.shape[1] /scaling_factor)
    new_height = int(ori_background_image.shape[0]/ scaling_factor)

    img_h = new_height
    img_w = new_width

    dim = (new_width, new_height)

    # resize image
    #background_image = cv2.resize(ori_background_image, dim, interpolation=cv2.INTER_CUBIC)

    background_h = new_height #background_image.shape[0]
    background_w = new_width #background_image.shape[1]

    thumbnail_fixed_width = int((background_w * thumbnail_fixed_height)/background_h)

    w_h_factor = background_w/background_h #thumbnail_fixed_width/thumbnail_fixed_height


    result_list = []

    #del(dict_list[-1])

    thumbnail_list = []

    cnt = 0
    for element in dict_list:
        x = element["x"]
        y = element["y"]
        w = element["w"]
        h = element["h"]

        thumbnail_w = w
        thumbnail_h = h
        thumbnail_x = x
        thumbnail_y = y

        new_x = 0
        new_y = 0

        do_resize = True

        if thumbnail_h  + (border*2) <= thumbnail_fixed_height and thumbnail_w  + (border*2) <= thumbnail_fixed_width:
            thumbnail_w = thumbnail_fixed_width
            thumbnail_h = thumbnail_fixed_height
            x_factor = 1
            y_factor = 1

            do_resize = False

        else:

            #bounding_box_h = thumbnail_fixed_height
            #bounding_box_w = thumbnail_fixed_width

            if thumbnail_h >= thumbnail_w:
                bounding_box_h = thumbnail_h
                bounding_box_w = int(bounding_box_h * w_h_factor)
            else:
                bounding_box_w = thumbnail_w

                # l'altezza viene aggiustata proporzionalmente in base alla larghezza
                # però poi se l'altezza viene abbassata potrebbe troncare parte dell'oggetto
                bounding_box_h = int(thumbnail_w / w_h_factor)

            # nel seguente ciclo ci preoccupiamo di esser sicuri che le dimensioni del thumbnail contengano
            # l'oggetto, rispettando le proporzioni dello schermo

            while True:

                if bounding_box_w <= thumbnail_w or bounding_box_h <= thumbnail_h : # in case height will be truncated
                    # incrementiamo di 10 pixel a step per velocizzare la creazione del thumbnailS

                    top_bottom_border = border * (bounding_box_h / thumbnail_fixed_height)
                    left_right_border = border * (bounding_box_w / thumbnail_fixed_width)

                    if bounding_box_h - h < top_bottom_border * 2:

                        top_bottom_border = (top_bottom_border * 2) - (bounding_box_h - h)

                    else:
                        top_bottom_border = top_bottom_border * 2

                    if bounding_box_w - w < left_right_border * 2:

                        left_right_border = (left_right_border * 2) - (bounding_box_w - w)

                    else:
                        left_right_border = left_right_border * 2

                    bounding_box_w = bounding_box_w + left_right_border
                    bounding_box_h = bounding_box_h + top_bottom_border


                    if w >= h:

                        bounding_box_w += left_right_border
                        bounding_box_h = bounding_box_w / w_h_factor
                    else:
                        bounding_box_h += top_bottom_border
                        bounding_box_w = bounding_box_h* w_h_factor

                    if bounding_box_w > background_w or bounding_box_h > background_h:
                        bounding_box_w = background_w
                        bounding_box_h = background_h

                        thumbnail_w = bounding_box_w
                        thumbnail_h = bounding_box_h

                        do_resize = True
                        break

                elif bounding_box_w > thumbnail_w and bounding_box_h > thumbnail_h:

                    #thumbnail_w = bounding_box_w
                    #thumbnail_h = bounding_box_h


                    thumbnail_w = int(bounding_box_w)
                    thumbnail_h = int(bounding_box_h)

                    do_resize = True
                    break

        #ora dobbiamo centrare l'oggetto nel thumbnail
        offset_x = thumbnail_w - w
        offset_y = thumbnail_h - h

        thumbnail_x -= int(offset_x/2)
        thumbnail_y -= int(offset_y / 2)

        new_x += int(offset_x/2)
        new_y += int(offset_y/2)



        x_factor = thumbnail_w / thumbnail_fixed_width
        y_factor = thumbnail_h / thumbnail_fixed_height

        if thumbnail_x < 0 and thumbnail_x + thumbnail_w > background_w:
            offset = thumbnail_x
            thumbnail_x = 0
            new_x = new_x + offset


        elif thumbnail_x + thumbnail_w > background_w:
            offset = (thumbnail_x + thumbnail_w) - background_w
            thumbnail_x = thumbnail_x - offset
            new_x = new_x + offset

        elif thumbnail_x < 0:
            offset = thumbnail_x
            thumbnail_x = 0
            new_x = new_x + offset

        if thumbnail_y + thumbnail_h > background_h:
            offset = (thumbnail_y + thumbnail_h) - background_h
            thumbnail_y = thumbnail_y - offset
            new_y = new_y + offset

        if thumbnail_y < 0:
            offset = thumbnail_y
            thumbnail_y = 0
            new_y = new_y + offset

        thumbnail_x = int(thumbnail_x * scaling_factor)
        thumbnail_y = int(thumbnail_y * scaling_factor)
        thumbnail_w = int(thumbnail_w * scaling_factor)
        thumbnail_h = int(thumbnail_h * scaling_factor)

        thumbnail = ori_background_image[thumbnail_y:thumbnail_y + thumbnail_h,thumbnail_x:thumbnail_x + thumbnail_w]

        #dim = (int(thumbnail_fixed_width/scaling_factor), int(thumbnail_fixed_height/scaling_factor))
        dim = (int(thumbnail_fixed_width*scaling_factor), int(thumbnail_fixed_height*scaling_factor))

        # resize image
        if do_resize:
            resized = cv2.resize(thumbnail, dim, interpolation=cv2.INTER_CUBIC)
        else:
            resized = thumbnail.copy()


        x = int(new_x / x_factor)
        y = int(new_y / y_factor)
        h = int(h / y_factor)
        w = int(w / x_factor)

        #cv2.rectangle(resized, (x, y), (x + w, y + h), (0, 0, 255), 1)

        #cv2.imwrite("D:\\screenshot\\" + str(cnt) + "_thumbnail.png", resized)

        png_image = cv2.imencode('.png', resized)

        base64png = base64.b64encode(png_image[1]).decode('ascii')

        thumbnail_dict = {'image':base64png, 'image_w':int(thumbnail_fixed_width*scaling_factor),
                          'image_h': int(thumbnail_fixed_height*scaling_factor), 'x': x, 'y': y,
                          'w': w, 'h': h, 'group': element["group"],
                          'is_main': element["is_main"]}


        result_list.append(thumbnail_dict)

        cnt += 1

    #result_list = sorted(result_list, key=itemgetter('group'))

    resized = cv2.resize(ori_background_image, dim, interpolation=cv2.INTER_CUBIC)
    png_image = cv2.imencode('.png', resized)
    base64png = base64.b64encode(png_image[1]).decode('ascii')
    thumbnail_dict_screen = {'image': base64png, 'image_w': int(thumbnail_fixed_width*scaling_factor),
                             'image_h': int(thumbnail_fixed_height*scaling_factor)}

    thumbnails_dict = {'thumbnails': result_list, 'screen':  thumbnail_dict_screen}

    if from_url:
        return jsonify(thumbnails_dict)
    else:
        return thumbnails_dict

    pass



@app.route("/build_screen", methods=['GET', 'POST'])
def build_screen():
    return render_template('build_screen.html')

def __window_enumeration_handler(hwnd, windows):
    windows.append((hwnd, win32gui.GetWindowText(hwnd)))
