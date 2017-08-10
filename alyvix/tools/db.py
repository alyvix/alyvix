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

import os
import csv
import sys
import time
import sqlite3
import datetime
import ConfigParser
import win32service
from alyvix.tools.info import InfoManager
from alyvix.tools.perfdata import PerfManager
from distutils.sysconfig import get_python_lib
from .natsmanager import NatsManager

_db_file_name = None

_dict = {}

class DbManager():

    def __init__(self):

        self._perf_manager = PerfManager()
        self._info_manager = InfoManager()
        self._db_home = os.path.split(sys.executable)[0] + os.sep + "share" + os.sep + "alyvix"
        self._db_name = "alyvix_data"

        if self._info_manager.get_info("ROBOT CONTEXT") is True:

            self._db_home = os.path.dirname(os.path.abspath(self._info_manager.get_info("SUITE SOURCE")))

            self._db_name = self._info_manager.get_info("SUITE NAME").lower().replace(" ","_")

            """
            if self._info_manager.get_info("TEST CASE NAME") is not None:
                self._db_name = self._db_name + "_" + self._info_manager.get_info("TEST CASE NAME").replace(" ", "_")
            """

        self._db_name = self._db_name + ".db"

        #self._info_manager.set_info("DB FILE", self._db_home + os.sep + self._db_name)

        self._connection = None
        self._cursor = None
        self._db_is_new = False

    def connect(self):
        self._connection = sqlite3.connect(self._db_home + os.sep + self._db_name)
        self._connection.row_factory = sqlite3.Row
        self._cursor = self._connection.cursor()

    def close(self):
        self._connection.commit()
        self._connection.close()

    def _create_scraper_tables(self):

        sc_collection = self._info_manager.get_info('SCRAPER COLLECTION')

        for scraper in sc_collection:
            s_name = scraper[0]
            s_timestamp = scraper[1]
            s_text = scraper[2]

            query = "CREATE TABLE IF NOT EXISTS " + s_name + " (transaction_timestamp integer primary key, scraped_text TEXT)"
            self._cursor.execute(query)

            #"<transaction_bla02_timestamp>, <scraped_text>"

    def _insert_scraper(self):
        sc_collection = self._info_manager.get_info('SCRAPER COLLECTION')

        for scraper in sc_collection:
            s_name = scraper[0]
            s_timestamp = scraper[1]
            s_text = scraper[2].replace("'","''")

            query = "INSERT INTO " + s_name + " (transaction_timestamp, scraped_text) VALUES (" + str(s_timestamp)\
                    + ", '" + s_text + "')"

            self._cursor.execute(query)

    def _create_tables(self):
        self._create_runs_table()
        self._create_thresholds_table()
        self._create_sorting_table()
        self._create_timestamp_table()


    def _create_runs_table(self):
        query = "CREATE TABLE IF NOT EXISTS runs (start_time integer primary key"
        for perf in self._perf_manager.get_all_perfdata():
            query = query + ", " + perf.name + " integer"
        query += ")"
        self._cursor.execute(query)

    def _create_thresholds_table(self):
        query = "CREATE TABLE IF NOT EXISTS thresholds (start_time integer primary key"
        for perf in self._perf_manager.get_all_perfdata():
            query = query + ", " + perf.name + "_warn integer, " + perf.name + "_crit integer, " \
                    + perf.name + "_tout integer"
        query += ", FOREIGN KEY (start_time) REFERENCES runs(start_time) ON DELETE CASCADE)"
        self._cursor.execute(query)

    def _create_sorting_table(self):
        query = "CREATE TABLE IF NOT EXISTS sorting (start_time integer primary key"
        for perf in self._perf_manager.get_all_perfdata():
            query = query + ", " + perf.name + "_index integer"
        query += ", FOREIGN KEY (start_time) REFERENCES runs(start_time) ON DELETE CASCADE)"
        self._cursor.execute(query)

    def _create_timestamp_table(self):
        query = "CREATE TABLE IF NOT EXISTS timestamp (start_time integer primary key"
        for perf in self._perf_manager.get_all_perfdata():
            query = query + ", " + perf.name + "_time integer"
        query += ", FOREIGN KEY (start_time) REFERENCES runs(start_time) ON DELETE CASCADE)"
        self._cursor.execute(query)

    def _check_runs_columns(self):
        query = "PRAGMA table_info(runs);"
        rows = self._cursor.execute(query).fetchall()

        for perf in self._perf_manager.get_all_perfdata():

            perf_name_present = False

            for row in rows:

                if row[1] == perf.name:
                    perf_name_present = True
                    break

            #check and add new columns
            if perf_name_present is False:

                query = "ALTER TABLE runs ADD COLUMN " + perf.name + " integer;"
                self._cursor.execute(query)

    def _check_thresholds_columns(self):
        query = "PRAGMA table_info(thresholds);"
        rows = self._cursor.execute(query).fetchall()

        for perf in self._perf_manager.get_all_perfdata():

            perf_warn_present = False
            perf_crit_present = False
            perf_timeout_present = False

            for row in rows:

                if row[1] == perf.name + "_warn":
                    perf_warn_present = True

                if row[1] == perf.name + "_crit":
                    perf_crit_present = True

                if row[1] == perf.name + "_tout":
                    perf_timeout_present = True

            #check and add new columns
            if perf_warn_present is False:

                query = "ALTER TABLE thresholds ADD COLUMN " + perf.name + "_warn integer;"
                self._cursor.execute(query)

            #check and add new columns
            if perf_crit_present is False:

                query = "ALTER TABLE thresholds ADD COLUMN " + perf.name + "_crit integer;"
                self._cursor.execute(query)

            #check and add new columns
            if perf_timeout_present is False:

                query = "ALTER TABLE thresholds ADD COLUMN " + perf.name + "_tout integer;"
                self._cursor.execute(query)

    def _check_sorting_columns(self):
        query = "PRAGMA table_info(sorting);"
        rows = self._cursor.execute(query).fetchall()

        for perf in self._perf_manager.get_all_perfdata():

            perf_name_present = False

            for row in rows:

                if row[1] == perf.name + "_index":
                    perf_name_present = True
                    break

            #check and add new columns
            if perf_name_present is False:

                query = "ALTER TABLE sorting ADD COLUMN " + perf.name + "_index integer;"
                self._cursor.execute(query)

    def _check_timestamp_columns(self):
        query = "PRAGMA table_info(timestamp);"
        rows = self._cursor.execute(query).fetchall()

        for perf in self._perf_manager.get_all_perfdata():

            perf_name_present = False

            for row in rows:

                if row[1] == perf.name + "_time":
                    perf_name_present = True
                    break

            #check and add new columns
            if perf_name_present is False:

                query = "ALTER TABLE timestamp ADD COLUMN " + perf.name + "_time integer;"
                self._cursor.execute(query)

    def _insert_runs(self):

        #check and add new columns
        self._check_runs_columns()

        start_time = self._info_manager.get_info("START TIME")
        query = "INSERT INTO runs (start_time"
        for perf in self._perf_manager.get_all_perfdata():
            query = query + ", " + perf.name
        query = query + ") VALUES (" + str(start_time)

        for perf in self._perf_manager.get_all_perfdata():
            if perf.value is not None and perf.value != "":
                query = query + ", " + str(int(perf.value * 1000))
            else:
                query = query + ", null"

        query += ")"
        self._cursor.execute(query)

    def _insert_thresholds(self):

        #check and add new columns
        self._check_thresholds_columns()

        #get last row of thresholds table
        query = "select * from thresholds where start_time ORDER BY start_time DESC LIMIT 1"
        last_rows = self._cursor.execute(query).fetchone()

        total_null = 0

        #count null values
        if last_rows is not None:
            for row in last_rows:
                if row is None:
                    total_null += 1

        #get perfdata of current run
        current_perfdata = self._perf_manager.get_all_perfdata()

        for perf in current_perfdata:

            #if warning or critical or timeout are empty, then we dont have to compare warning or critical column
            if perf.warning_threshold == "" or perf.warning_threshold is None and total_null > 0:
                total_null -= 1

            if perf.critical_threshold == "" or perf.critical_threshold is None and total_null > 0:
                total_null -= 1

            if perf.timeout_threshold == "" or perf.timeout_threshold is None and total_null > 0:
                total_null -= 1

        if last_rows is not None:
            total_columns = len(last_rows) - 1
        else:
            total_columns = 0

        start_time = self._info_manager.get_info("START TIME")
        query = "INSERT INTO thresholds (start_time"

        for perf in current_perfdata:
            query = query + ", " + perf.name + "_warn, " + perf.name + "_crit, " + perf.name + "_tout"
        query = query + ") VALUES (" + str(start_time)

        different_from_last = self._db_is_new

        #check if perfdata items of current run are > (or <) than last row columns
        if len(current_perfdata) * 3 != (total_columns - total_null):
            different_from_last = True

        for perf in self._perf_manager.get_all_perfdata():

            if perf.warning_threshold is not None and perf.warning_threshold != "":
                query = query + ", " + str(int(perf.warning_threshold * 1000))
                if last_rows is not None and last_rows[perf.name + "_warn"] != int(perf.warning_threshold * 1000):
                    different_from_last = True
            else:
                query = query + ", null"
                if last_rows is not None and last_rows[perf.name + "_warn"] is not None:
                    different_from_last = True

            if perf.critical_threshold is not None and perf.critical_threshold != "":
                query = query + ", " + str(int(perf.critical_threshold * 1000))
                if last_rows is not None and last_rows[perf.name + "_crit"] != int(perf.critical_threshold * 1000):
                    different_from_last = True
            else:
                query = query + ", null"
                if last_rows is not None and last_rows[perf.name + "_crit"] is not None:
                    different_from_last = True

            if perf.timeout_threshold is not None and perf.timeout_threshold != "":
                query = query + ", " + str(int(perf.timeout_threshold * 1000))
                if last_rows is not None and last_rows[perf.name + "_tout"] != int(perf.timeout_threshold * 1000):
                    different_from_last = True
            else:
                query = query + ", null"
                if last_rows is not None and last_rows[perf.name + "_tout"] is not None:
                    different_from_last = True

        if different_from_last is True:

            query = query + ")"
            self._cursor.execute(query)

    def _insert_sorting(self):

        #check and add new columns
        self._check_sorting_columns()

        #get last row of sorting table
        query = "select * from sorting where start_time ORDER BY start_time DESC LIMIT 1"
        last_rows = self._cursor.execute(query).fetchone()

        total_null = 0

        #count null values
        if last_rows is not None:
            for row in last_rows:
                if row is None:
                    total_null += 1

        if last_rows is not None:
            total_columns = len(last_rows) - 1
        else:
            total_columns = 0

        start_time = self._info_manager.get_info("START TIME")

        query = "INSERT INTO sorting (start_time"
        for perf in self._perf_manager.get_all_perfdata():
            query = query + ", " + perf.name + "_index"
        query = query + ") VALUES (" + str(start_time)

        different_from_last = self._db_is_new

        #check if perfdata items of current run are > (or <) than last row columns
        if len(self._perf_manager.get_all_perfdata()) != (total_columns - total_null):
            different_from_last = True

        for perf in self._perf_manager.get_all_perfdata():
            query = query + ", " + str(perf.counter)

            if last_rows is not None and last_rows[perf.name + "_index"] != perf.counter:
                different_from_last = True

        if different_from_last is True:
            query = query + ")"
            self._cursor.execute(query)

    def _insert_timestamp(self):

        # check and add new columns
        self._check_timestamp_columns()

        start_time = self._info_manager.get_info("START TIME")
        query = "INSERT INTO timestamp (start_time"
        for perf in self._perf_manager.get_all_perfdata():
            query = query + ", " + perf.name + "_time"
        query = query + ") VALUES (" + str(start_time)

        for perf in self._perf_manager.get_all_perfdata():
            if perf.timestamp is not None and perf.timestamp != "":
                query = query + ", " + str(perf.timestamp)
            else:
                query = query + ", null"

        query += ")"
        self._cursor.execute(query)

    def store_perfdata(self, dbname=None):

        if dbname != None and dbname != "":
            self._db_home = os.path.split(str(dbname))[0]

            if os.path.split(str(dbname))[1] != "":
                self._db_name = os.path.split(str(dbname))[1]

            name, file_extension = os.path.splitext(self._db_name)

            if file_extension != "":
                if file_extension != ".db" and file_extension != ".db3" and file_extension != ".sqlite"\
                        and file_extension != ".sqlite3":
                    raise Exception('The file extension must be .db or .sqlite')
            else:
                file_extension = ".db"

                self._db_name = self._db_name + file_extension

            if self._db_home == "" and self._info_manager.get_info("ROBOT CONTEXT") is True:
                self._db_home = os.path.dirname(os.path.abspath(self._info_manager.get_info("SUITE SOURCE")))
            elif self._db_home == "":
                self._db_home = os.path.split(sys.executable)[0] + os.sep + "share" + os.sep + "alyvix"

        self._info_manager.set_info("DB FILE", self._db_home + os.sep + self._db_name)

        #if not os.path.isfile(self._db_home + os.sep + self._db_name):
        if not os.path.isdir(self._db_home):
            os.makedirs(self._db_home)
            self.connect()
            self._create_tables()
            self._db_is_new = True
        elif not os.path.isfile(self._db_home + os.sep + self._db_name):
            self.connect()
            self._create_tables()
            self._db_is_new = True
        else:
            self.connect()
            self._create_tables()

        self._insert_runs()
        self._insert_thresholds()
        self._insert_sorting()
        self._insert_timestamp()

        self.close()

    def store_scrapdata(self, dbname=None):

        sc_collection = self._info_manager.get_info('SCRAPER COLLECTION')
        if len(sc_collection) == 0:
            return

        db_name_ori = self._db_name

        if dbname != None and dbname != "":
            self._db_home = os.path.split(str(dbname))[0]

            if os.path.split(str(dbname))[1] != "":
                self._db_name = os.path.split(str(dbname))[1]

            name, file_extension = os.path.splitext(self._db_name)

            if file_extension != "":
                if file_extension != ".db" and file_extension != ".db3" and file_extension != ".sqlite" \
                        and file_extension != ".sqlite3":
                    raise Exception('The file extension must be .db or .sqlite')
            else:
                file_extension = "_scrapdata.db"

                self._db_name = self._db_name + file_extension

            if self._db_home == "" and self._info_manager.get_info("ROBOT CONTEXT") is True:
                self._db_home = os.path.dirname(os.path.abspath(self._info_manager.get_info("SUITE SOURCE")))
            elif self._db_home == "":
                self._db_home = os.path.split(sys.executable)[0] + os.sep + "share" + os.sep + "alyvix"

        self._info_manager.set_info("DB FILE SCRAPER", self._db_home + os.sep + self._db_name)

        #self._db_name = self._db_name.replace(".db", "_scrapdata.db")
        #self._db_name = self._db_name.replace(".db3", "_scrapdata.db3")
        #self._db_name = self._db_name.replace(".sqlite", "_scrapdata.sqlite")
        #self._db_name = self._db_name.replace(".sqlite3", "_scrapdata.sqlite3")

        # if not os.path.isfile(self._db_home + os.sep + self._db_name):
        if not os.path.isdir(self._db_home):
            os.makedirs(self._db_home)
            self.connect()
            self._create_scraper_tables()
            self._db_is_new = True
        elif not os.path.isfile(self._db_home + os.sep + self._db_name):
            self.connect()
            self._create_scraper_tables()
            self._db_is_new = True
        else:
            self.connect()
            self._create_scraper_tables()

        self._insert_scraper()

        self.close()

        self._db_name = db_name_ori


    def publish_perfdata(self, type="csv", start_date=None, end_date=None, filename=None,
                         testcase_name=None, max_age=24, suffix=None, subject=None, server=None, port=None,
                         measurement="alyvix", max_reconnect_attempts=5, reconnect_time_wait=2):

        if type.lower() == "perfmon":
            try:
                scm = win32service.OpenSCManager('localhost', None, win32service.SC_MANAGER_CONNECT)

                win32service.OpenService(scm, 'Alyvix Wpm Service', win32service.SERVICE_QUERY_CONFIG)
            except:
                raise Exception(
                    "Alyvix WPM service is not installed")

            try:
                full_file_name = get_python_lib() + os.sep + "alyvix" + os.sep + "extra" + os.sep + "alyvixservice.ini"

                config = ConfigParser.ConfigParser()
                config.read(full_file_name)

                db_file = self._info_manager.get_info("DB FILE")

                if db_file is not None:

                    self._db_home = os.path.split( self._info_manager.get_info("DB FILE"))[0]
                    self._db_name = os.path.split( self._info_manager.get_info("DB FILE"))[1]

                if testcase_name is None or testcase_name == "":
                    testcase_name = self._info_manager.get_info('TEST CASE NAME')

                if testcase_name is None or testcase_name == "":
                    testcase_name = self._info_manager.get_info('SUITE NAME')

                try:
                    if not config.has_section('db_path'):
                        config.add_section('db_path')
                except:
                    pass

                try:
                    if not config.has_section('db_max_age'):
                        config.add_section('db_max_age')
                except:
                    pass

                try:
                    config.get('general', "polling_frequency")
                except:
                    try:
                        config.add_section('general')
                    except:
                        config.set('general', 'polling_frequency', '500')

                try:
                    config.get('general', "push_frequency")
                except:
                    try:
                        config.add_section('general')
                    except:
                        config.set('general', 'push_frequency', '2')

                config.set('db_path', testcase_name, self._db_home + os.sep + self._db_name)

                config.set('db_max_age', testcase_name, str(max_age))

                with open(full_file_name, 'w') as configfile:
                    config.write(configfile)
            except:
                pass

        elif type.lower() == "csv":

            start_date_dt = None
            end_date_dt = None

            for fmt in ('%Y-%m-%d', '%Y-%m-%d %H:%M' , '%Y-%m-%d %H:%M:%S'):
                try:
                    start_date_dt = datetime.datetime.strptime(start_date, fmt)
                except ValueError:
                    pass

            for fmt in ('%Y-%m-%d', '%Y-%m-%d %H:%M' , '%Y-%m-%d %H:%M:%S'):
                try:
                    end_date_dt = datetime.datetime.strptime(end_date, fmt)
                except ValueError:
                    pass

            if end_date_dt is None:
                try:
                    if end_date.lower() == "now":
                        end_date_dt = datetime.datetime.now()
                except:
                    pass

            if start_date_dt is None:

                if "days" in start_date:

                    try:
                        d_start_day = start_date.replace("days", "")
                        d_start_day = d_start_day.replace(" ", "")
                        d_start_day = int(d_start_day)

                        delta_date = datetime.datetime.today() - datetime.timedelta(days=d_start_day)
                        start_date_dt = delta_date
                    except:
                        pass
                elif "hours" in start_date:
                    try:
                        h_start_day = start_date.replace("hours", "")
                        h_start_day = h_start_day.replace(" ", "")
                        h_start_day = int(h_start_day)

                        delta_date = datetime.datetime.today() - datetime.timedelta(hours=h_start_day)
                        start_date_dt = delta_date
                    except:
                        pass

            if start_date_dt is None:
                raise Exception('The start date is not valid')

            if end_date_dt is None:
                raise Exception('The end date is not valid')

            if start_date_dt >= end_date_dt:
                raise Exception('The end date must be greater than start date')

            db_file = self._info_manager.get_info("DB FILE")

            if db_file is not None:

                self._db_home = os.path.split( self._info_manager.get_info("DB FILE"))[0]
                self._db_name = os.path.split( self._info_manager.get_info("DB FILE"))[1]

            try:
                if os.path.isfile(db_file) is False:
                    return
            except:
                return

            if self._info_manager.get_info("ROBOT CONTEXT") is True:
                csv_default_home = os.path.dirname(os.path.abspath(self._info_manager.get_info("SUITE SOURCE")))
                csv_default_name = self._info_manager.get_info("SUITE NAME").lower().replace(" ","_") + ".csv"
            else:
                csv_default_home = os.path.split(sys.executable)[0] + os.sep + "share" + os.sep + "alyvix"
                csv_default_name = "alyvix_data.csv"

            csv_name = filename

            if csv_name is None or filename == "":

                csv_name = csv_default_home + os.sep + csv_default_name

            else:

                path_and_name, file_extension = os.path.splitext(csv_name)

                if file_extension != "":
                    if file_extension != ".csv":
                        raise Exception('The file extension must be .csv')
                else:
                    file_extension = ".csv"

                path = os.path.dirname(path_and_name)

                if path == "":
                    path = csv_default_home
                    path_and_name = path + os.sep + path_and_name
                    csv_name = path_and_name + file_extension
                elif path + os.sep == path_and_name:
                    csv_name = path_and_name + csv_default_name
                else:
                    csv_name = path_and_name + file_extension

            if suffix is not None and suffix != 'None':
                if suffix.lower() == "timestamp":
                    csv_name = csv_name.replace(".csv", "_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".csv")
                else:
                    raise Exception('The suffix type is not valid')

            self.connect()

            #get last row of sorting table
            query = "select * from sorting ORDER BY start_time DESC LIMIT 1"
            last_sorting_rows = self._cursor.execute(query).fetchone()

            #print self._cursor.description

            perf_to_query = []

            for key in last_sorting_rows.keys():

                if key == "start_time":
                    continue

                value = last_sorting_rows[key]

                if value is not None:
                    new_value = 999999
                    if value != -1:
                        new_value = value

                    perf_to_query.append((key.replace("_index", ""), new_value))

            perf_to_query = sorted(perf_to_query, key=lambda x: x[1])

            query = "select datetime(start_time, 'unixepoch','localtime') as start_time"

            for column in perf_to_query:
                query = query + ", " + column[0]

            query = query + " from runs where CAST(strftime('%s', datetime(start_time, 'unixepoch', 'localtime')) AS INT) between CAST(strftime('%s', '" + start_date_dt.strftime("%Y-%m-%d %H:%M:%S") + "') AS INT) and CAST(strftime('%s', '" + end_date_dt.strftime("%Y-%m-%d %H:%M:%S") + "') AS INT)"

            rows = self._cursor.execute(query).fetchall()

            csv_header = []
            csv_header.append("start_time")

            for perf_column in perf_to_query:
                csv_header.append(perf_column[0])

            csv_file = open(csv_name, 'w')
            csv_writer = csv.writer(csv_file, lineterminator='\n')

            csv_writer.writerow(csv_header)

            for row in rows:

                csv_row = []

                #start_date_dt = datetime.datetime.utcfromtimestamp(row["start_time"])

                #start_date_str = start_date_dt.strftime("%Y-%m-%d %H:%M:%S")

                csv_row.append(row["start_time"])

                for perf_column in perf_to_query:
                    csv_row.append(row[perf_column[0]])

                csv_writer.writerow(csv_row)

            self.close()

            csv_file.close()
        elif type.lower() == "nats":
            nm = NatsManager()

            #perfdata_list = self._perf_manager.get_all_perfdata()

            if server is None or server == 'None' or server == "":
                raise Exception('The server value cannot be empty')

            if port is None or port == 'None' or port == "":
                port = 4222

            if subject is None or subject == 'None' or subject == "":
                raise Exception('The subject value cannot be empty')

            if testcase_name is None or testcase_name == "None" or testcase_name == "":
                testcase_name = self._info_manager.get_info('TEST CASE NAME')

            if testcase_name is None or testcase_name == 'None' or testcase_name == "":
                testcase_name = self._info_manager.get_info('SUITE NAME')

            if testcase_name is None or testcase_name == 'None' or testcase_name == "":
                raise Exception('The test case name is not valid')

            nm.publish(testcase_name, subject, server, str(port), measurement=measurement,
                max_reconnect_attempts=max_reconnect_attempts, reconnect_time_wait=reconnect_time_wait)
        else:
            raise Exception('The publish output type is not valid')
