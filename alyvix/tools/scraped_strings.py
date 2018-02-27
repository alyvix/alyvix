#! /usr/bin/python

"""
    Text processing of OCR scraped strings
    Copyright (C) 2018 Francesco Melchiori
    <https://www.francescomelchiori.com/>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import json
import re


class StringManager:

    def __init__(self, scraped_string, customer_name='test', path_json='',
                 map_norm=True):
        self.scraped_string = str(scraped_string)
        self.aos_scrap = 'no_aos_scrap'
        self.id_scrap = 'no_id_scrap'
        self.aos_name = 'no_aos_name'
        self.id_session = 'no_id_session'
        self.customer_name = str(customer_name)
        self.path_json = str(path_json)
        self.customer_settings = {}
        if customer_name == 'test':
            self.store_json_customer_settings()
        self.load_json_customer_settings(self.path_json)
        if 'aos_names' in self.customer_settings:
            self.aos_names = self.customer_settings['aos_names']
        self.map_norm = map_norm
        if self.map_norm:
            self.aos_patterns = {}
            self.generate_aos_pattern()
        self.extract_aos_name()
        self.extract_id_session()

    def __repr__(self):
        if self.map_norm:
            return 'AOS: {0} | ID: {1}'.format(self.aos_name, self.id_session)
        else:
            return 'AOS: {0} | ID: {1}'.format(self.aos_scrap, self.id_scrap)

    def store_json_customer_settings(self):
        customer_settings = {'aos_names': ['TEST1AOS_1',
                                           'TEST1AOS_2',
                                           'TEST2AOS_1',
                                           'TEST2AOS_2'],
                             'ax_title_marks': {'aos_start': 'Inc. [',
                                                'aos_stop': ': Session',
                                                'id_start': 'ID - ',
                                                'id_stop': '] - ['}}
        json.dump(customer_settings,
                  fp=open('{0}_customer_settings.json'.format(
                      self.customer_name), 'w'),
                  indent=4)
        return True

    def load_json_customer_settings(self, path_json=''):
        filename_json = '{0}_customer_settings.json'.format(self.customer_name)
        path_json_customer_settings = '{0}{1}'.format(path_json, filename_json)
        try:
            self.customer_settings = json.load(open(
                path_json_customer_settings))
        except IOError:
            print('{0}_customer_settings.json does not exist'.format(
                self.customer_name))
            return False
        return True

    def extract_text_scrap(self, mark_start='', mark_stop=''):
        if self.scraped_string != '':
            cut_start = self.scraped_string.find(mark_start)
            cut_stop = self.scraped_string.find(mark_stop)
            if cut_start != -1 and cut_stop != -1:
                cut_start += mark_start.__len__()
                text_scrap = self.scraped_string[cut_start:cut_stop].strip()
                return text_scrap
        return False

    def extract_aos_name(self):
        if 'ax_title_marks' in self.customer_settings:
            ax_title_marks = self.customer_settings['ax_title_marks']
            aos_start = ax_title_marks['aos_start']
            aos_stop = ax_title_marks['aos_stop']
            text_scrap = self.extract_text_scrap(mark_start=aos_start,
                                                 mark_stop=aos_stop)
            if text_scrap:
                self.aos_scrap = text_scrap
                if self.map_norm:
                    self.map_aos_scrap()
                return True
        return False

    def extract_id_session(self):
        if 'ax_title_marks' in self.customer_settings:
            ax_title_marks = self.customer_settings['ax_title_marks']
            id_start = ax_title_marks['id_start']
            id_stop = ax_title_marks['id_stop']
            text_scrap = self.extract_text_scrap(mark_start=id_start,
                                                 mark_stop=id_stop)
            if text_scrap:
                self.id_scrap = text_scrap
                if self.map_norm:
                    self.norm_id_session()
                return True
        return False

    def generate_aos_pattern(self):
        if self.aos_names:
            for aos_name in self.aos_names:
                aos_name_proc = ''.join(aos_name.lower().split())
                aos_root = aos_name_proc.rstrip(''.join(
                    [str(x) for x in range(10)]))
                aos_serial = aos_name_proc.split(aos_root, 1)[1]
                aos_pattern = '('
                for aos_char in aos_root:
                    if aos_char == 'b':
                        aos_pattern += '[b68]'
                    elif aos_char == 'b':
                        aos_pattern += '[b68]'
                    elif aos_char == 'd':
                        aos_pattern += '[d6o0]'
                    elif aos_char == 'e':
                        aos_pattern += '[e3]'
                    elif aos_char == 'f':
                        aos_pattern += '[f17]'
                    elif aos_char == 'h':
                        aos_pattern += '[hb6]'
                    elif aos_char == 'i':
                        aos_pattern += '[i1l]'
                    elif aos_char == 'l':
                        aos_pattern += '[li1]'
                    elif aos_char == 'o':
                        aos_pattern += '[o0]'
                    elif aos_char == 't':
                        aos_pattern += '[tfl1]'
                    elif aos_char == '0':
                        aos_pattern += '[0do]'
                    elif aos_char == '1':
                        aos_pattern += '[1filt]'
                    elif aos_char == '3':
                        aos_pattern += '[3e]'
                    elif aos_char == '6':
                        aos_pattern += '[6bdh]'
                    elif aos_char == '7':
                        aos_pattern += '[7ft]'
                    elif aos_char == '8':
                        aos_pattern += '[8b]'
                    else:
                        aos_pattern += aos_char
                aos_pattern += ')'
                if aos_pattern in self.aos_patterns:
                    self.aos_patterns[aos_pattern][aos_serial] = aos_name
                else:
                    self.aos_patterns[aos_pattern] = {aos_serial: aos_name}
            return True
        return False

    def map_aos_scrap(self):
        if self.aos_names:
            if self.aos_scrap in self.aos_names:
                self.aos_name = self.aos_scrap
                return True
            else:
                aos_scrap_name = ''.join(self.aos_scrap.lower().split())
                aos_scrap_root = self.aos_scrap.rstrip(''.join(
                    [str(x) for x in range(10)]))
                aos_scrap_serial = self.aos_scrap.split(aos_scrap_root, 1)[1]
                for aos_pattern in self.aos_patterns.keys():
                    if re.match(aos_pattern, aos_scrap_name):
                        try:
                            self.aos_name = self.aos_patterns[
                                aos_pattern][aos_scrap_serial]
                            return True
                        except KeyError:
                            return False
        return False

    def norm_id_session(self):
        try:
            norm_id_scrap = int(''.join(self.id_scrap.split()))
        except ValueError:
            return False
        if norm_id_scrap in range(2**16):
            self.id_session = norm_id_scrap
            return True
        return False


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


if __name__ == "__main__":

    scrap_example_us = "Inc. [t3stl a0 s_1: Session ID - 1 2] - [1 -"
    scrap_example_it = "S.p.A. [t3stl a0 s_1: ID sessione - 1 2] - [1 -"
    scrap_example_de = "GmbH [t3stl a0 s_1: Session ID - 1 2] - [1 -"

    get_aos_id(scraped_string=scrap_example_us,
               customer_name='test',
               map_norm=True,
               verbose=True)
