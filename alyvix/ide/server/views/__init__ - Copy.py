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

# -*- coding: utf-8 -*-
import os
#import boto3
import time
import hmac
import json
from flask import jsonify

import shutil
import datetime
import mimetypes
from threading import Thread
from hashlib import sha1
#import requests, zipfile, io
from flask import Flask, request, redirect, make_response, render_template, current_app, Markup, g, send_file
from alyvix.ide.server import app
import logging
import urllib
import time
import re
import io
import base64
import numpy as np
import cv2

autocontoured_rects = []
base64png = None
img_h = 0
img_w = 0

@app.route("/table", methods=['GET', 'POST'])
def index():
    return render_template('table.html', variables={})
    
@app.route("/drawing", methods=['GET', 'POST'])
def drawing():
    return render_template('drawing.html', base64url = "data:image/png;base64," + base64png, img_h=img_h, img_w=img_w,
                           autocontoured_rects=autocontoured_rects)

@app.route("/create_thumbnail", methods=['POST'])
def create_thumbnail():
    if request.method == 'POST':

        thumbnail_fixed_height = 40

        json_data = json.loads(request.data)

        dict_list = json_data['box_list']
        last_dict = dict_list[-1]  #get last dict of the array
        background_string = json_data["background"]
        background_string = background_string[22:]

        np_array = np.fromstring(base64.b64decode(background_string), np.uint8)

        background_image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        background_h = background_image.shape[0]
        background_w = background_image.shape[1]

        thumbnail_fixed_width = int((background_w * thumbnail_fixed_height)/background_h)

        left_right_border_five_px =int(5 * (background_w/thumbnail_fixed_width))

        top_bottom_border_five_px = 5 * (background_h / thumbnail_fixed_height)

        w_h_factor = thumbnail_fixed_width/thumbnail_fixed_height


        result_list = []

        #del(dict_list[-1])

        thumbnail_list = []

        cnt = 0
        for element in dict_list:
            x = element["x"]
            y = element["y"]
            w = element["w"]
            h = element["h"]

            if w > h:
                #border = int((5 / thumbnail_fixed_height) * h)
                border = h + 4 #int(4 * w_h_factor) #h + 4

                thumbnail_w = w + (border * 2)

                thumbnail_h = int(thumbnail_w / w_h_factor)
                thumbnail_x = x - border
                offset_x = left_right_border_five_px
                thumbnail_y = y - int((thumbnail_h - h)/2)
                offset_y = int((thumbnail_h - h)/2)

            elif w < h:
                border = w + 4 #int(4 * w_h_factor) #w + 4

                thumbnail_h = h + (border * 2)

                thumbnail_w = int(thumbnail_h * w_h_factor)
                thumbnail_y = y - border
                offset_y = border
                thumbnail_x = x - int((thumbnail_w - w)/2)
                offset_x = int((thumbnail_w - w)/2)

            else:  # h is equals to w, so we increase w
                border = int(h/ 4) #int(4 * w_h_factor) #h + 4

                thumbnail_w = w + (border * 4)

                thumbnail_h = int(thumbnail_w / w_h_factor)
                thumbnail_x = x - (border * 2)
                offset_x = (border * 2)
                thumbnail_y = y - int((thumbnail_h - h) / 2)
                offset_y = int((thumbnail_h - h) / 2)


            if thumbnail_h < thumbnail_fixed_height:

                offset = thumbnail_fixed_height - thumbnail_h

                thumbnail_h = thumbnail_h + int((offset + 8)/2)
                thumbnail_y = thumbnail_y - int((offset + 4)/2)
                offset_y = offset_y + int((offset + 4)/2)

                thumbnail_w = thumbnail_w + int(((offset + 8)/2) * w_h_factor)
                thumbnail_x = thumbnail_x - int(((offset + 4)/2) * w_h_factor)
                offset_x = offset_x + int(((offset + 4)/2) * w_h_factor)


            if thumbnail_x + thumbnail_w > background_w:
                offset = (thumbnail_x + thumbnail_w) - background_w
                thumbnail_x = thumbnail_x - offset
                offset_x = offset_x + offset

            if thumbnail_x < 0:
                thumbnail_x = 0
                offset_x = x + thumbnail_x

            if thumbnail_y + thumbnail_h > background_h:
                offset = (thumbnail_y + thumbnail_h) - background_h
                thumbnail_y = thumbnail_y - offset
                offset_y = offset_y + offset

            if thumbnail_y < 0:
                thumbnail_y = 0
                offset_y = y + thumbnail_y

            thumbnail = background_image[thumbnail_y:thumbnail_y + thumbnail_h, thumbnail_x:thumbnail_x + thumbnail_w]

            #cv2.rectangle(thumbnail, (offset_x, offset_y), (offset_x + w, offset_y + h), (0, 255, 0), 1)

            dim = (thumbnail_fixed_width, thumbnail_fixed_height)

            # resize image
            resized = cv2.resize(thumbnail, dim, interpolation=cv2.INTER_CUBIC)

            png_image = cv2.imencode('.png', resized)

            base64png = base64.b64encode(png_image[1]).decode('ascii')

            x_factor = thumbnail_w / thumbnail_fixed_width
            y_factor = thumbnail_h / thumbnail_fixed_height

            x = int(offset_x/x_factor)
            y = int(offset_y / y_factor)
            w = int(w/x_factor)
            h = int(h / x_factor)

            thumbnail_dict = {'image':base64png, 'x': x, 'y': y, 'w': w, 'h': h}

            result_list.append(thumbnail_dict)

            cv2.rectangle(resized, (x, y), (x + w, y + h), (0, 0, 255), 1)

            cv2.imwrite("D:\\screenshot\\" + str(cnt) + "_thumbnail.png", resized)

            cnt += 1

        thumbnails_dict = {'thumbnails': result_list}

        return jsonify(thumbnails_dict)

    pass



@app.route("/build_screen", methods=['GET', 'POST'])
def build_screen():
    return render_template('build_screen.html')

class ViewerManager():
    pass
