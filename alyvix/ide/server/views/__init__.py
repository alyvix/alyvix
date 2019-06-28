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
import time
import hmac
import json
import re
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
from alyvix.core.contouring import ContouringManager
from alyvix.core.engine import Roi
from alyvix.core.engine.text import TextManager
from operator import itemgetter

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
win32_window = None
server_process = None

@app.route("/table", methods=['GET', 'POST'])
def index():
    return render_template('table.html', variables={})
    
@app.route("/drawing", methods=['GET', 'POST'])
def drawing():
    text = en.drawing

    return render_template('drawing.html', base64url = "data:image/png;base64," + base64png, img_h=img_h, img_w=img_w,
                           autocontoured_rects=autocontoured_rects, text=en.drawing,
                           object_name=current_objectname,
                           loaded_boxes=current_boxes)

@app.route("/selector", methods=['GET', 'POST'])
def selector():
    text = en.drawing

    return render_template('selector.html')

@app.route("/load_objects", methods=['GET'])
def load_objects():
    lm = LibraryManager()

    lm.load_file(current_filename)

    alyvix_file_dict = lm.build_objects_for_ide(current_objectname)

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

        return jsonify(return_dict)

    else:
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

@app.route("/cancel_event", methods=['GET'])
def cancel_event():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is not None:
        func()
    else:
        #raise RuntimeError('Not running with the Werkzeug Server')
        server_process.close()


    windows_found = []

    win32gui.EnumWindows(__window_enumeration_handler, windows_found)


    for hwnd_found, title_found in windows_found:

        if re.match(".*Alyvix Editor.*", title_found, re.DOTALL | re.IGNORECASE) is not None and \
                (win32gui.IsWindowVisible(hwnd_found) != 0 or win32gui.GetWindowTextLength(hwnd_found) > 0):

            try:
                win32gui.PostMessage(hwnd_found, win32con.WM_CLOSE, 0, 0)
            except:
                pass


    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@app.route("/save_json", methods=['GET', 'POST'])
def save_json():
    if request.method == 'POST':

        current_json = {}

        try:
            with open(current_filename) as f:
                current_json = json.load(f)
        except:
            pass

        json_data = json.loads(request.data)
        object_name = json_data['object_name']

        detection = json_data['detection']

        background = json_data['background']

        box_list = json_data['box_list']


        curr_script = current_json.get("script", {})

        curr_object_list_dict = current_json.get("objects", {})

        curr_object_dict = curr_object_list_dict.get(object_name, {})

        curr_object_dict["detection"] = detection

        curr_components = curr_object_dict.get("components", {})

        resolution_string = str(int(img_w*scaling_factor)) + "*" + str(int(img_h*scaling_factor)) + "@" + str(int(scaling_factor*100))

        curr_components[resolution_string] = {}

        curr_components[resolution_string]["screen"] = background.replace("data:image/png;base64,","")

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

        current_json["objects"] = curr_object_list_dict

        current_json["objects"][object_name] = curr_object_dict

        current_json["objects"][object_name]["components"] = curr_components


        if object_name != current_objectname:
            del current_json["objects"][current_objectname]

        current_json["objects"][object_name]["date-modified"] = \
            datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S") + " UTC" + time.strftime("%z")



        with open(current_filename, 'w') as f:
            json.dump(current_json, f, indent=4, sort_keys=True, ensure_ascii=False)

        aaa = "asas"
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@app.route("/get_scraped_txt", methods=['GET', 'POST'])
def get_scraped_txt():
    if request.method == 'POST':

        json_data = json.loads(request.data)

        roi = Roi()
        roi.x = json_data["roi_x"]
        roi.y = json_data["roi_y"]
        roi.w = json_data["roi_w"]
        roi.h = json_data["roi_h"]
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

        ret_dict = {'scraped_text': scraped_text}

        return jsonify(ret_dict)

@app.route("/test_txt_regexp", methods=['GET', 'POST'])
def test_txt_regexp():
    if request.method == 'POST':

        json_data = json.loads(request.data)

        regexp = json_data["regexp"]
        scraped_text = json_data["scraped_text"]

        result = re.match(".*" + regexp + ".*", scraped_text, re.DOTALL | re.IGNORECASE)

        if result is  None:

            ret_dict = {'match': False}
        else:
            ret_dict = {'match': True}

        return jsonify(ret_dict)


@app.route("/create_thumbnail", methods=['POST'])
def create_thumbnail():
    if request.method == 'POST':

        #thumbnail_fixed_height = int(30 * scaling_factor)
        #border = int(4*scaling_factor)

        thumbnail_fixed_height = 30
        border = 4

        json_data = json.loads(request.data)

        dict_list = json_data['box_list']
        last_dict = dict_list[-1]  #get last dict of the array
        background_string = json_data["background"]
        background_string = background_string[22:]

        np_array = np.frombuffer(base64.b64decode(background_string), np.uint8)

        ori_background_image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        new_width = int(ori_background_image.shape[1] /scaling_factor)
        new_height = int(ori_background_image.shape[0]/ scaling_factor)
        dim = (new_width, new_height)

        # resize image
        background_image = cv2.resize(ori_background_image, dim, interpolation=cv2.INTER_CUBIC)

        background_h = background_image.shape[0]
        background_w = background_image.shape[1]

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


            if thumbnail_x + thumbnail_w > background_w:
                offset = (thumbnail_x + thumbnail_w) - background_w
                thumbnail_x = thumbnail_x - offset
                new_x = x + offset

            if thumbnail_x < 0:
                offset = x + thumbnail_x
                thumbnail_x = 0
                new_x = offset

            if thumbnail_y + thumbnail_h > background_h:
                offset = (thumbnail_y + thumbnail_h) - background_h
                thumbnail_y = thumbnail_y - offset
                new_y = -offset

            if thumbnail_y < 0:
                offset = y + thumbnail_y
                thumbnail_y = 0
                new_y = offset

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

            cv2.imwrite("D:\\screenshot\\" + str(cnt) + "_thumbnail.png", resized)

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

        return jsonify(thumbnails_dict)

    pass



@app.route("/build_screen", methods=['GET', 'POST'])
def build_screen():
    return render_template('build_screen.html')

def __window_enumeration_handler(hwnd, windows):
    windows.append((hwnd, win32gui.GetWindowText(hwnd)))

class ViewerManager():
    pass
