# -*- coding: utf-8 -*-
# Alyvix allows you to automate and monitor all types of applications
# Copyright (C) 2015 Alan Pipitone
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

from alyvixcommon import *
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
import re


def overwrite_alyvix_screen(overwrite="true"):

    overwrite_value = overwrite

    if overwrite.lower() == "true":
        overwrite_value = True
    elif overwrite.lower()  == "false":
        overwrite_value = False
        
    info_manager = InfoManager()
    
    info_manager.set_info("OVERWRITE LOG IMAGES", overwrite_value)

def disable_report(var):

    if isinstance(var, basestring):

        if var.lower() == "true":
            info_manager = InfoManager()

            info_manager.set_info("DISABLE REPORTS", True)


        elif var.lower() == "false":
            info_manager = InfoManager()

            info_manager.set_info("DISABLE REPORTS", False)

    if isinstance(var, bool):
        if var == True:
            info_manager = InfoManager()

            info_manager.set_info("DISABLE REPORTS", True)


        elif var == False:
            info_manager = InfoManager()

            info_manager.set_info("DISABLE REPORTS", False)


def set_alyvix_info(name, value):

    info_manager = InfoManager()

    info_manager.set_info(name, value)
    
def alyvix_config(full_filename):
    os.environ["alyvix_testcase_config"] = full_filename

def send_keys(keys, encrypted="false", delay="10", duration = "-1"):

    encrypted_value = encrypted

    try:
        delay_value = int(delay)
    except:
        delay_value = 10

    try:
        duration_value = int(duration)
    except:
        duration_value = -1
    
    if encrypted.lower() == "true":
        encrypted_value = True
    elif encrypted.lower()  == "false":
        encrypted_value = False
        
    km = KeyboardManager()
    km.send(keys, encrypted_value, delay_value, duration_value)
    
def click(x, y, button="left", n=1):
    x_value = int(x)
    y_value = int(y)
    n_value = int(n)
    
    mm = MouseManager()
    
    button_value = mm.left_button
    
    if button.lower() == "right":
        button_value = mm.right_button
    
    mm.click(x_value, y_value, button_value, n_value)
    
def double_click(x, y):
    x_value = int(x)
    y_value = int(y)
    
    mm = MouseManager()
    mm.click(x_value, y_value, mm.left_button, 2)
    
def mouse_move(x, y):
    x_value = int(x)
    y_value = int(y)
    
    mm = MouseManager()
    mm.move(x_value, y_value)
    
def mouse_scroll(steps=2, direction="up"):
    steps_value = int(steps)
    
    mm = MouseManager()
        
    if direction.lower() == "up":
        direction = mm.wheel_up
    elif direction.lower()== "down":
        direction = mm.wheel_down
    
    mm.scroll(steps_value, direction)
    
def mouse_drag(x1, y1, x2, y2):

    mm = MouseManager()
    
    mm.drag(x1, y1, x2, y2)

def create_process(*popenargs, **kwargs):
    
    pm = ProcManager()
    proc = pm.create_process(popenargs)
    return proc.pid
    
def kill_process(process_name):
    
    pm = ProcManager()
    pm.kill_process(process_name)


def wait_process_close(process_name, pid=None, timeout="60", exception="True"):
    exception_value = exception

    try:
        if exception.lower() == "true":
            exception_value = True
        elif exception.lower() == "false":
            exception_value = False
    except:
        pass

    timeout_value = int(timeout)

    pid_value = None
    if pid is not None:
        try:
            pid_value = int(pid)
        except:
            pid_value = None
    else:
        pid_value = None

    pm = ProcManager()
    process_time = pm.wait_process_close(process_name, pid=pid_value, timeout=timeout_value)

    if exception_value is True and process_time == -1:
        raise Exception("Process " + process_name + " has timed out: " + str(timeout) + " s.")

    return process_time
    
def show_window(window_title, maximize="False"):

    try:
        if maximize.lower() == "true":
            maximize_value = True
        elif maximize.lower() == "false":
            maximize_value = False
    except:
        pass

    wm = WinManager()
    wm.show_window(window_title, maximize_value)
    
def maximize_window(window_title, timeout="60", exception="True"):

    exception_value = exception

    try:    
        if exception.lower() == "true":
            exception_value = True
        elif exception.lower() == "false":
            exception_value = False
    except:
        pass

    timeout_value = int(timeout)
    
    wm = WinManager()
    window_time = wm.maximize_window(window_title, timeout_value)
    
    if exception_value is True and window_time == -1:
        raise Exception("Window " + window_title + " has timed out: " + str(timeout) + " s.")
    
    return window_time
    
def wait_window(window_title, timeout="60", exception="True"):

    exception_value = exception
    
    try:     
        if exception.lower() == "true":
            exception_value = True
        elif exception.lower() == "false":
            exception_value = False
    except:
        pass

    timeout_value = int(timeout)

    wm = WinManager()
    window_time = wm.wait_window(window_title, timeout_value)
        
    if exception_value is True and window_time == -1:
        raise Exception("Window " + window_title + " has timed out: " + str(timeout) + " s.")
        
    return window_time
    
def wait_window_close(window_title, timeout="60", exception="True"):

    exception_value = exception
    
    try:     
        if exception.lower() == "true":
            exception_value = True
        elif exception.lower() == "false":
            exception_value = False
    except:
        pass

    timeout_value = int(timeout)

    wm = WinManager()
    window_time = wm.wait_window_close(window_title, timeout_value)
    
    if exception_value is True and window_time == -1:
        raise Exception("Window " + window_title + " has timed out: " + str(timeout) + " s.")
        
    return window_time
    
def check_window(window_title):
    
    wm = WinManager()
    return wm.check_if_window_exists(window_title)

def get_window_title():

    wm = WinManager()
    return wm.get_window_title()
    
def close_window(window_title):
    wm = WinManager()
    wm.close_window(window_title)

def alyvix_screenshot(filename_arg):

    variables = BuiltIn().get_variables()
    outdir = variables['${OUTPUTDIR}']

    filename = filename_arg

    if "." not in filename:
        ext = ".png"
        filename = filename + ext

    sm = ScreenManager()
    img = sm.grab_desktop()
    img_name = outdir + os.sep + filename

    img.save(img_name)

    logger.info('<a href="' + filename + '"><img src="' + filename + '" width="800px"></a>', html=True)
    
def add_perfdata(name, value=None, warning_threshold=None, critical_threshold=None, state=None, timestamp=False):
    pm = PerfManager()
    #name_lower = str(name).lower().replace(" ", "_")
    pm.add_perfdata(name, value, warning_threshold, critical_threshold, state, timestamp)
    
def rename_perfdata(old_name, new_name, warning_threshold="", critical_threshold=""):
    
    #old_name_lower = str(old_name).lower().replace(" ", "_")
    #new_name_lower = str(new_name).lower().replace(" ", "_")

    pm = PerfManager()
    pm.rename_perfdata(old_name, new_name, warning_threshold, critical_threshold)

def get_perfdata(name, delete_perfdata="False"):
    delete_perfdata_value = delete_perfdata
    #name_lower = str(name).lower().replace(" ", "_")

    try:
        if delete_perfdata.lower() == "true":
            delete_perfdata_value = True
        elif delete_perfdata.lower() == "false":
            delete_perfdata_value = False
    except:
        pass

    pm = PerfManager()
    return pm.get_perfdata(name, delete_perfdata=delete_perfdata_value)

def delete_perfdata(name):
    #name_lower = str(name).lower().replace(" ", "_")

    pm = PerfManager()
    pm.delete_perfdata(name)

def sum_perfdata(*names, **kwargs):

    kwarglist = []

    for key in kwargs:
        if key == "delete_perfdata":

            try:
                if kwargs[key].lower() == "true":
                    value = True
                elif kwargs[key].lower()  == "false":
                    value = False

                kwargs[key] = value
            except:
                pass

        """
        if key == "name":
            kwargs[key] = str(kwargs[key]).lower().replace(" ", "_")
        """

    """
    new_names = []

    for name in names:
        new_names.append(str(name).lower().replace(" ", "_"))
    """

    pm = PerfManager()
    return pm.sum_perfdata(*names, **kwargs)

def set_perfdata_extra(name, extra):
    pm = PerfManager()
    pm.set_perfdata_extra(name, extra)

def add_perfdata_tag(perf_name, tag_name, tag_value):
    pm = PerfManager()
    pm.add_perfdata_tag(perf_name, tag_name, tag_value)

def add_perfdata_field(perf_name, field_name, field_value):
    pm = PerfManager()
    pm.add_perfdata_field(perf_name, field_name, field_value)

def store_perfdata(dbname=None):
    db = DbManager()
    db.store_perfdata(dbname)

def store_scrapdata(dbname=None):
    db = DbManager()
    db.store_scrapdata(dbname)

def publish_perfdata(type="csv", start_date="", end_date="", filename="", testcase_name="", max_age=24, suffix=None,
                     subject=None, server=None, port=None, measurement="alyvix", max_reconnect_attempts=5,
                     reconnect_time_wait=2):
    db = DbManager()
    db.publish_perfdata(type=str(type), start_date=str(start_date), end_date=str(end_date), filename=str(filename),
                        testcase_name=str(testcase_name), max_age=int(max_age), suffix=str(suffix),
                        subject=str(subject), server=str(server), port=port, measurement=str(measurement),
                        max_reconnect_attempts=max_reconnect_attempts, reconnect_time_wait=reconnect_time_wait)

def print_perfdata(message=None, print_output="True"):

    message_value = None
    print_output_value = True
    
    try:
        if message.lower() != "":
            message_value = message
    except:
        pass
    
    try:    
        if print_output.lower() == "true":
            print_output_value = True
        elif print_output.lower() == "false":
            print_output_value = False
    except:
        pass

    pm = PerfManager()
    return pm.get_output(message_value, print_output_value)


def get_mstsc_hostname(customer_name='test', path_json=''):
    nm = NetManager(customer_name=customer_name, path_json=path_json)
    if nm.known_hostnames:
        first_known_hostname = nm.known_hostnames[0]
        return first_known_hostname
    else:
        return False


def get_dictionary_value(path_file_json='init', name_dict_json='dict_01',
                         name_key_json='key_01', verbose=False):
    jm = JSONManager(path_file_json=path_file_json)
    value_json = jm.get_json_value(name_dict_json=name_dict_json,
                                   name_key_json=name_key_json)
    if verbose:
        print(value_json)
    return value_json


def get_aos_id(scraped_string, customer_name='test', path_json='',
               map_norm=True, verbose=False):
    sm = StringManager(scraped_string=scraped_string,
                       customer_name=customer_name,
                       path_json=path_json,
                       map_norm=map_norm)
    if verbose:
        print(sm)
    if map_norm:
        return sm.aos_name, sm.id_session
    return sm.aos_scrap, sm.id_scrap


def check_number(scraped_string,
                 comparison_type='bigger',
                 comparison_number='0'):
    splitted_scrap = scraped_string.split()
    for snippet in splitted_scrap:
        number_pattern = '[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?'
        number_search = re.search(number_pattern, snippet)
        if number_search:
            number_searched = number_search.group()
            try:
                candidate_number = float(number_searched)
            except ValueError:
                continue
            if comparison_type == 'bigger':
                if candidate_number > float(comparison_number):
                    return True, candidate_number
                else:
                    return False, candidate_number
    return False, None


def get_date_today(date_format='dd/mm/yyyy'):
    cwm = CalendarWatchManager(date_format=date_format)
    return cwm.get_date_today()


def get_three_letter_days_previous_month():
    cwm = CalendarWatchManager()
    return cwm.get_three_letter_days_previous_month()


def check_dhms_totaltime_days_previous_month(scraped_string):
    cwm = CalendarWatchManager(scraped_string=scraped_string)
    return cwm.check_dhms_totaltime_days_previous_month()


def check_hms_time_proximity(scraped_string, proximity_minutes=60):
    cwm = CalendarWatchManager(scraped_string=scraped_string,
                               proximity_minutes=proximity_minutes)
    return cwm.check_hms_time_proximity()


def check_date_today(scraped_string):
    cwm = CalendarWatchManager(scraped_string)
    return cwm.check_date_today()