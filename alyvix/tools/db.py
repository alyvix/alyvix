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
import sys
import time
import sqlite3
from alyvix.tools.info import InfoManager
from alyvix.tools.perfdata import PerfManager

_db_file_name = None

_dict = {}

class DbManager():

    def __init__(self):

        self._perf_manager = PerfManager()
        self._info_manager = InfoManager()
        self._db_home = os.path.split(sys.executable)[0] + os.sep + "share" + os.sep + "alyvix"

        if self._info_manager.get_info("ROBOT CONTEXT") is True:
            self._db_name = self._info_manager.get_info("SUITE NAME").replace(" ", "_")

            if self._info_manager.get_info("TEST CASE NAME") is not None:
                self._db_name = self._db_name + "_" + self._info_manager.get_info("TEST CASE NAME").replace(" ", "_")

        else:
            self._db_name = "alyvix_data"

        self._db_name = self._db_name + ".db"

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

    def _create_tables(self):
        self._create_runs_table()
        self._create_thresholds_table()
        self._create_sorting_table()

    def _create_runs_table(self):
        query = "CREATE TABLE runs (start_time integer primary key"
        for perf in self._perf_manager.get_all_perfdata():
            query = query + ", " + perf.name + " integer"
        query += ")"
        self._cursor.execute(query)

    def _create_thresholds_table(self):
        query = "CREATE TABLE thresholds (start_time integer primary key"
        for perf in self._perf_manager.get_all_perfdata():
            query = query + ", " + perf.name + "_warn integer, " + perf.name + "_crit integer"
        query += ")"
        self._cursor.execute(query)

    def _create_sorting_table(self):
        query = "CREATE TABLE sorting (start_time integer primary key"
        for perf in self._perf_manager.get_all_perfdata():
            query = query + ", " + perf.name + "_index integer"
        query += ")"
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

            for row in rows:

                if row[1] == perf.name + "_warn":
                    perf_warn_present = True

                if row[1] == perf.name + "_crit":
                    perf_crit_present = True

            #check and add new columns
            if perf_warn_present is False:

                query = "ALTER TABLE thresholds ADD COLUMN " + perf.name + "_warn integer;"
                self._cursor.execute(query)

            #check and add new columns
            if perf_crit_present is False:

                query = "ALTER TABLE thresholds ADD COLUMN " + perf.name + "_crit integer;"
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

            #if warning or critical are empty, then we dont have to compare warning or critical column
            if perf.warning_threshold == "" or perf.warning_threshold is None and total_null > 0:
                total_null -= 1

            if perf.critical_threshold == "" or perf.critical_threshold is None and total_null > 0:
                total_null -= 1

        if last_rows is not None:
            total_columns = len(last_rows) - 1
        else:
            total_columns = 0

        start_time = self._info_manager.get_info("START TIME")
        query = "INSERT INTO thresholds (start_time"

        for perf in current_perfdata:
            query = query + ", " + perf.name + "_warn, " + perf.name + "_crit"
        query = query + ") VALUES (" + str(start_time)

        different_from_last = self._db_is_new

        #check if perfdata items of current run are > (or <) than last row columns
        if len(current_perfdata) * 2 != (total_columns - total_null):
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

    def insert_perfdata(self, dbname=None):

        if dbname != None and dbname != "":
            self._db_home = os.path.split(dbname)[0]
            self._db_name = os.path.split(dbname)[1]

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

        self._insert_runs()
        self._insert_thresholds()
        self._insert_sorting()

        self.close()
