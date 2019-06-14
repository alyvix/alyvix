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

        thumbnail_fixed_top_bottom_border = 3
        thumbnail_fixed_left_right_border = 3

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

            thumbnail_w = w
            thumbnail_h = h
            thumbnail_x = x
            thumbnail_y = y

            new_x = 0
            new_y = 0

            do_resize = True

            if thumbnail_h < thumbnail_fixed_height and thumbnail_w < thumbnail_fixed_width:
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

                    if bounding_box_w < thumbnail_w or bounding_box_h < thumbnail_h : # in case height will be truncated
                        # incrementiamo di 10 pixel a step per velocizzare la creazione del thumbnailS
                        bounding_box_w += 10
                        bounding_box_h = int(bounding_box_w / w_h_factor)
                    elif bounding_box_w >= thumbnail_w and bounding_box_h >= thumbnail_h:
                        thumbnail_w = bounding_box_w
                        thumbnail_h = bounding_box_h
                        break


            #ora calcoliamo i bordi in proporzione all'aspect ratio dello screen e quindi del thumbnail finale
            top_bottom_border = ((thumbnail_fixed_top_bottom_border/thumbnail_fixed_height) * thumbnail_h)
            left_right_border = ((thumbnail_fixed_left_right_border / thumbnail_fixed_width) * thumbnail_w)

            #controlliamo se lo spazio tra la fine del'oggetto e la fine del thumbnail è sufficiente a contenere il
            # margine che ci serve
            top_bottom_border_offset = 0
            if thumbnail_h - h < top_bottom_border*2:

                top_bottom_border_offset = (top_bottom_border*2) - (thumbnail_h - h)

            elif thumbnail_h > thumbnail_fixed_height:
                top_bottom_border_offset = top_bottom_border * 2

            left_right_border_offset = 0
            if thumbnail_w - w < left_right_border*2:

                left_right_border_offset = (left_right_border*2) - (thumbnail_w - w)
            elif thumbnail_w > thumbnail_fixed_width:
                left_right_border_offset = left_right_border * 2

            if left_right_border_offset >= top_bottom_border_offset:
                # in questo caso l'oggetto è largo quanto tutto il thumbnail
                # allora umentiamo la larghezza del thumbnail e mantiamo l'altezza in proporzione
                thumbnail_h = int(thumbnail_h + top_bottom_border_offset)
                thumbnail_w = int(thumbnail_h * w_h_factor)


            else:
                thumbnail_w = int(thumbnail_w + left_right_border_offset)
                thumbnail_h = int(thumbnail_w/w_h_factor)

            if thumbnail_h > thumbnail_fixed_height or thumbnail_w > thumbnail_fixed_width:
                do_resize = True

            #ora dobbiamo centrare l'oggetto nel thumbnail
            offset_x = thumbnail_w - w
            offset_y = thumbnail_h - h

            #thumbnail_x -= int(offset_x/2)
            #thumbnail_y -= int(offset_y / 2)

            #new_x += int(offset_x/2)
            #new_y += int(offset_y/2)



            x_factor = thumbnail_w / thumbnail_fixed_width
            y_factor = thumbnail_h / thumbnail_fixed_height






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
            if do_resize:
                resized = cv2.resize(thumbnail, dim, interpolation=cv2.INTER_CUBIC)
            else:
                resized = thumbnail.copy()

            png_image = cv2.imencode('.png', resized)

            base64png = base64.b64encode(png_image[1]).decode('ascii')

            thumbnail_dict = {'image':base64png, 'x': x, 'y': y, 'w': w, 'h': h}

            result_list.append(thumbnail_dict)

            x = int(new_x/x_factor)
            y = int(new_y/y_factor)
            h = int(h/y_factor)
            w = int(w/x_factor)

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
