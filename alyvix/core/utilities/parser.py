import sys
import copy
import time
import threading
from datetime import datetime
from alyvix.core.engine import EngineManager
from alyvix.core.interaction.mouse import MouseManager
from alyvix.tools.library import LibraryManager
from alyvix.tools.screen import ScreenManager
from alyvix.core.utilities import common

class Performance():

    def __init__(self):
        self.object_name = None

        self.series = []

class ParserManager:

    def __init__(self, library_json=None, chunk= None, engine_arguments=None, verbose=0, output_mode="alyvix",
                 cipher_key=None, cipher_iv=None):
        self._verbose = verbose
        self._output_mode = output_mode
        self._lm = LibraryManager()

        self._lm.set_json(library_json)
        self._chunk = chunk
        self._engine_arguments = engine_arguments
        self._objects_result = []

        self._objects = []

        sm = ScreenManager()
        w, h = sm.get_resolution()
        scaling_factor = sm.get_scaling_factor()

        self._performances = []
        self._perf_series = {
            "object_name": None,
            "series_name": None,
            "performance_name": None,
            "detection_type": None,
            "group": None,
            "output": True,
            "thresholds": {},
            "performance_ms": -1,
            "accuracy_ms": -1,
            "timestamp": -1,
            "end_timestamp": -1,
            "initialize_cnt": 0,
            "records": {"text":"", "image":"", "extract":"", "check":"not_executed"},
            "timeout": None,
            "exit": "not_executed",
            "state": 2,
            "resolution": {
                "width": w,
                "height": h
            },
            "scaling_factor": int(scaling_factor * 100),
            "screenshot": None,
            "annotation": None
        }

        self._executed_object_name = []
        self._executed_object_instance = []

        self._key = cipher_key
        self._iv = cipher_iv

        self._script_case = copy.deepcopy(library_json["script"]["case"])
        self._script_sections = copy.deepcopy(library_json["script"]["sections"])

        try:
            self._script_maps = copy.deepcopy(library_json["maps"])
        except:
            self._script_maps = {}

        self.lock = threading.Lock()

    def get_performances(self):

        """
        for perf in self._performances:
            for series in perf.series:

                if series["exit"] == "not_executed":
                    series["timestamp"] = time.time()
                    series["end_timestamp"] = series["timestamp"]
        """

        return self._performances

    def get_flattern_performances(self):

        executed_flattern_performances = []
        not_executed_flattern_performances = []

        performances = self._performances #copy.deepcopy(self.get_performances())

        for perf in performances:
            for series in perf.series:

                if series["exit"] != "not_executed":
                    executed_flattern_performances.append(series)
                else:
                    not_executed_flattern_performances.append(series)

        executed_flattern_performances = sorted(executed_flattern_performances, key=lambda k: k['timestamp'])
        not_executed_flattern_performances = sorted(not_executed_flattern_performances, key=lambda k: k['initialize_cnt'])
        executed_flattern_performances.extend(not_executed_flattern_performances)

        return executed_flattern_performances

    def get_unique_flattern_performances(self):

        executed_flattern_performances = []
        not_executed_flattern_performances = []

        performances = self._performances #copy.deepcopy(self.get_performances())

        for perf in performances:
            for series in perf.series:

                if series["exit"] != "not_executed":
                    executed_flattern_performances.append(series)
                else:
                    not_executed_flattern_performances.append(series)

        executed_flattern_performances = sorted(executed_flattern_performances, key=lambda k: k['timestamp'], reverse=True)



        name_already_present = []

        unique_perf_performances = []

        for performance in executed_flattern_performances:

            if performance["performance_name"] not in name_already_present:
                unique_perf_performances.append(performance)
                name_already_present.append(performance["performance_name"])

        unique_perf_performances = sorted(unique_perf_performances, key=lambda k: k['timestamp'])

        not_executed_flattern_performances = sorted(not_executed_flattern_performances,
                                                    key=lambda k: k['initialize_cnt'])
        unique_perf_performances.extend(not_executed_flattern_performances)

        return unique_perf_performances

    def _get_timestamp_formatted(self):
        timestamp = time.time()
        date_from_ts = datetime.fromtimestamp(timestamp)
        # millis_from_ts = int(round(float(date_from_ts.strftime("0.%f")), 3) * 1000)
        try:
            millis_from_ts = date_from_ts.strftime("%f")[: -3]
        except:
            millis_from_ts = "000"

        date_formatted = date_from_ts.strftime("%Y/%m/%d %H:%M:%S") + "." + str(millis_from_ts)

        return date_formatted

    def _iter_on_sections(self, section_name = None):
        if section_name is not None:
            section = self._script_sections[section_name]
        else:
            section = self._script_case

        for key in section:
            if isinstance(key, dict):
                flow_key = key.get("flow", None)

                if_key_true = key.get("if_true", None)
                if_key_false = key.get("if_false", None)
                for_key = key.get("for", None)

                if if_key_true is not None:

                    self._objects.append(key["if_true"])

                    if flow_key in self._script_sections:
                        self._iter_on_sections(section_name=flow_key)
                    else:
                        self._objects.append(flow_key)

                elif if_key_false is not None:
                    self._objects.append(key["if_false"])

                    if flow_key in self._script_sections:
                        self._iter_on_sections(section_name=flow_key)
                    else:
                        self._objects.append(flow_key)
                elif for_key is not None:

                        if flow_key in self._script_sections:
                            self._iter_on_sections(section_name=flow_key)
                        else:
                            self._objects.append(flow_key)
            elif key in self._script_sections:
                self._iter_on_sections(section_name=key)
            else:
                if key[0] == "#":
                    continue
                self._objects.append(key)

        return self._objects


    def _iter_on_sections_v2_old(self, section_name = None, map_name = None, map_key = None, map_name_map_key=None):
        if section_name is not None:
            section = self._script_sections[section_name]
        else:
            section = self._script_case

        for key in section:

            perf = Performance()

            if isinstance(key, dict):
                object_name = ""

                flow_key = key.get("flow", None)

                if_key_true = key.get("if_true", None)
                if_key_false = key.get("if_false", None)
                for_key = key.get("for", None)

                if if_key_true is not None:

                    if map_key is not None and map_name is not None:
                        self._objects.append(key["if_true"] + "_" + map_name + "-" + map_key)
                    else:
                        self._objects.append(key["if_true"])

                    if flow_key in self._script_sections:
                        self._iter_on_sections_v2(section_name=flow_key, map_name=map_name, map_key=map_key)
                    else:
                        if map_key is not None and map_name is not None:
                            self._objects.append(flow_key + "_" + map_name + "-" + map_key)
                        else:
                            self._objects.append(flow_key)

                elif if_key_false is not None:
                    if map_key is not None and map_name is not None:
                        self._objects.append(key["if_false"] + "_" + map_name + "-" + map_key)
                    else:
                        self._objects.append(key["if_false"])

                    if flow_key in self._script_sections:
                        self._iter_on_sections_v2(section_name=flow_key, map_name=map_name, map_key=map_key)
                    else:
                        if map_key is not None and map_name is not None:
                            self._objects.append(flow_key + "_" + map_name + "-" + map_key)
                        else:
                            self._objects.append(flow_key)
                elif for_key is not None:

                    #map_definition = self._script_maps[for_key]

                    current_map_name = for_key

                    for current_map_key in self._script_maps[current_map_name]:


                        if flow_key in self._script_sections:
                            if map_key is not None and map_name is not None:
                                self._iter_on_sections_v2(section_name=flow_key, map_name=map_name + "-" + current_map_name, map_key=map_key + "-" + current_map_key)
                            else:
                                self._iter_on_sections_v2(section_name=flow_key, map_name=current_map_name, map_key=current_map_key)
                        else:
                            if map_key is not None and map_name is not None:
                                self._objects.append(flow_key + "_" + map_name + "-" + map_key + "_" + current_map_name + "-" + current_map_key)
                            else:
                                self._objects.append(flow_key + "_" + current_map_name + "-" + current_map_key)

            elif key in self._script_sections:
                self._iter_on_sections_v2(section_name=key, map_name=map_name, map_key=map_key)
            else:
                if key[0] == "#":
                    continue
                if map_key is not None and map_name is not None:
                    self._objects.append(key + "_" + map_name + "-" + map_key)
                else:
                    self._objects.append(key)

        return self._objects


    def _add_or_append_perf(self, performances, object_name, map_names_map_keys=None):

        series_dict = copy.copy(self._perf_series)

        if map_names_map_keys is None:
            series_name = object_name
        else:
            map_name_map_key = ""

            if map_names_map_keys is not None:
                for m_n_m_k in map_names_map_keys:
                    map_name_map_key += m_n_m_k["map_name"] + "-" + m_n_m_k["map_key"] + "_"
                map_name_map_key = map_name_map_key[:-1]
                series_name = map_name_map_key


        series_dict["series_name"] = series_name
        series_dict["object_name"] = object_name
        series_dict["detection_type"] = self._lm.get_detection(object_name)["type"]
        series_dict["timeout"] = self._lm.get_timeout(object_name)
        series_dict["output"] = self._lm.measure_is_enable(object_name)
        try:
            series_dict["group"] = self._lm.get_measure(object_name)["group"]
        except:
            pass
        series_dict["thresholds"] = self._lm.get_measure(object_name)["thresholds"]
        series_dict["object_name"] = object_name

        if series_dict["series_name"] != object_name:
            series_dict["performance_name"] = object_name + "_" + series_dict["series_name"]
        else:
            series_dict["performance_name"] = object_name

        series_dict["maps"] = copy.copy(map_names_map_keys)

        series_dict["initialize_cnt"] = len(performances)


        object_exists = False
        for perf in performances:
            if perf.object_name == object_name:
                object_exists = True
                if len(perf.series) == 0:
                    perf.series.append(series_dict)
                else:
                    series_exists = False

                    for perf_series in perf.series:
                        if perf_series["series_name"] == series_name:
                            series_exists = True


                    if series_exists is False:
                        perf.series.append(series_dict)

        if object_exists is False:
            perf = Performance()
            perf.object_name = object_name
            perf.series.append(series_dict)

            performances.append(perf)


    def _iter_on_sections_v2(self, section_name = None, map_names_map_keys=None):
        if section_name is not None:
            section = self._script_sections[section_name]
        else:
            section = self._script_case

        map_name_map_key = ""

        if map_names_map_keys is not None:
            for m_n_m_k in map_names_map_keys:
                map_name_map_key += m_n_m_k["map_name"] + "-" + m_n_m_k["map_key"] + "_"
            map_name_map_key = map_name_map_key[:-1]

        for key in section:
            if isinstance(key, dict):
                object_name = ""

                flow_key = key.get("flow", None)

                if_key_true = key.get("if_true", None)
                if_key_false = key.get("if_false", None)
                for_key = key.get("for", None)

                if if_key_true is not None:

                    #if self._lm.get_measure(key["if_true"])["output"]:
                    if map_names_map_keys is not None:
                        self._objects.append(key["if_true"] + "_" + map_name_map_key)
                    else:
                        self._objects.append(key["if_true"])

                    self._add_or_append_perf(self._performances, key["if_true"], map_names_map_keys)

                    if flow_key in self._script_sections:
                        self._iter_on_sections_v2(section_name=flow_key,map_names_map_keys=map_names_map_keys)
                    else:
                        #if self._lm.get_measure(flow_key)["output"]:
                        if map_names_map_keys is not None:
                            self._objects.append(flow_key + "_" + map_name_map_key)
                        else:
                            self._objects.append(flow_key)

                        self._add_or_append_perf(self._performances, flow_key, map_names_map_keys)

                elif if_key_false is not None:
                    #if self._lm.get_measure(key["if_false"])["output"]:
                    if map_names_map_keys is not None:
                        self._objects.append(key["if_false"] + "_" + map_name_map_key)
                    else:
                        self._objects.append(key["if_false"])

                    self._add_or_append_perf(self._performances, key["if_false"], map_names_map_keys)

                    if flow_key in self._script_sections:
                        self._iter_on_sections_v2(section_name=flow_key, map_names_map_keys=map_names_map_keys)
                    else:
                        #if self._lm.get_measure(flow_key)["output"]:
                        if map_names_map_keys is not None:
                            self._objects.append(flow_key + "_" + map_name_map_key)
                        else:
                            self._objects.append(flow_key)

                        self._add_or_append_perf(self._performances, flow_key, map_names_map_keys)

                elif for_key is not None:

                    #map_definition = self._script_maps[for_key]

                    current_map_name = for_key

                    for current_map_key in self._script_maps[current_map_name]:

                        current_map = {"map_name": current_map_name, "map_key": current_map_key}

                        if flow_key in self._script_sections:
                            if map_names_map_keys is not None:

                                map_n_map_k = copy.copy(map_names_map_keys)
                                map_n_map_k.append(current_map)

                                #map_names_map_keys.append(current_map)
                                self._iter_on_sections_v2(section_name=flow_key, map_names_map_keys=map_n_map_k)
                            else:
                                map_n_map_k = []
                                map_n_map_k.append(current_map)
                                self._iter_on_sections_v2(section_name=flow_key, map_names_map_keys=map_n_map_k)
                        else:
                            #if self._lm.get_measure(flow_key)["output"]:
                            if map_names_map_keys is not None:
                                map_n_map_k = copy.copy(map_names_map_keys)
                                map_n_map_k.append(current_map)
                                self._objects.append(flow_key + "_" + map_name_map_key + "_" + current_map_name + "-" + current_map_key)
                                self._add_or_append_perf(self._performances, flow_key, map_n_map_k)
                            else:
                                self._objects.append(flow_key + "_" + current_map_name + "-" + current_map_key)

                                map_n_map_k = []
                                map_n_map_k.append(current_map)
                                self._add_or_append_perf(self._performances, flow_key, map_n_map_k)

            elif key in self._script_sections:
                self._iter_on_sections_v2(section_name=key, map_names_map_keys=map_names_map_keys)
            else:
                if key[0] == "#":
                    continue
                if map_names_map_keys is not None:
                    self._objects.append(key + "_" + map_name_map_key)
                else:
                    self._objects.append(key)

                self._add_or_append_perf(self._performances, key, map_names_map_keys)

        return self._objects

    def get_all_objects(self):

        self._objects = []

        #self._iter_on_sections()

        self._iter_on_sections_v2()

        self._objects = list(dict.fromkeys(self._objects))

        return self._objects

    def get_executed_objects(self):
        return self._executed_object_name

    def execute_object(self, object_name, args=None, map_names_map_keys=None, section_name=None):
        if self._lm.check_if_exist(object_name) is False:
            print(object_name + " does NOT exist")
            if common.is_from_server is True:
                return
            else:
                sys.exit(2)

        object_json = self._lm.add_chunk(object_name, self._chunk)

        engine_manager = EngineManager(object_json, args=args, maps=self._script_maps,
                                       verbose=self._verbose, output_mode=self._output_mode, cipher_key=self._key,
                                       cipher_iv=self._iv, performances=self._performances,
                                       map_names_map_keys=map_names_map_keys,
                                       section_name=section_name)

        result = engine_manager.execute()

        #self._objects_result.append(result)
        #self._executed_object_name.append(object_name)

        #for server: stop or brake
        if result is None:
            raise ValueError('server')

        if result.performance_ms == -1 and result.has_to_break is True:
            raise ValueError()
        elif result.performance_ms == -1 and result.has_to_break is False:
            return False
        elif result.performance_ms != -1:
            return True

    def get_results(self):
        return self._objects_result

    def _execute_section(self, section_name=None, args=None, map_names_map_keys=None):

        self.lock.acquire()
        break_flag = common.break_flag
        stop_flag = common.stop_flag
        self.lock.release()

        if break_flag is True and section_name != "fail" and section_name != "exit":
            return

        if stop_flag is True:
            return

        if args is None:
            arguments = self._engine_arguments
        else:
            arguments = args

        if section_name is not None:
            section = self._script_sections[section_name]
        else:
            section = self._script_case

        map_name_map_key = ""

        if map_names_map_keys is not None:
            for m_n_m_k in map_names_map_keys:
                map_name_map_key += m_n_m_k["map_name"] + "-" + m_n_m_k["map_key"] + "_"
            map_name_map_key = map_name_map_key[:-1]

        for key in section:

            self.lock.acquire()
            break_flag = common.break_flag
            stop_flag = common.stop_flag
            self.lock.release()

            if break_flag is True and section_name != "fail" and section_name != "exit":
                return

            if stop_flag is True:
                return

            if isinstance(key, dict):
                flow_key = key.get("flow", None)

                if_key_true = key.get("if_true", None)
                if_key_false = key.get("if_false", None)
                for_key = key.get("for", None)

                if if_key_true is not None:

                    if self.execute_object(key["if_true"], section_name=section_name):

                        if flow_key in self._script_sections:
                            self._execute_section(section_name=flow_key, args=arguments, map_names_map_keys=map_names_map_keys)
                        else:
                            self.execute_object(flow_key, args=arguments, map_names_map_keys=map_names_map_keys,
                                                section_name=section_name)

                elif if_key_false is not None:
                    if not self.execute_object(key["if_false"], section_name=section_name):
                        if flow_key in self._script_sections:
                            self._execute_section(section_name=flow_key, args=arguments, map_names_map_keys=map_names_map_keys)
                        else:
                            self.execute_object(flow_key, args=arguments, map_names_map_keys=map_names_map_keys,
                                                section_name=section_name)

                elif for_key is not None:

                    #selected_map = key["for"]
                    current_map_name = for_key

                    for current_map_key in self._script_maps[current_map_name]:

                        self.lock.acquire()
                        break_flag = common.break_flag
                        stop_flag = common.stop_flag
                        self.lock.release()

                        if break_flag is True and section_name != "fail" and section_name != "exit":
                            return

                        if stop_flag is True:
                            return

                        current_map = {"map_name": current_map_name, "map_key": current_map_key}

                        current_map_value = self._script_maps[current_map_name][current_map_key]
                        arguments = []

                        if isinstance(current_map_value, list):
                            arguments.extend(current_map_value)
                        else:
                            arguments.append(current_map_value)

                        if flow_key in self._script_sections:
                            if map_names_map_keys is not None:
                                map_n_map_k = copy.copy(map_names_map_keys)
                                map_n_map_k.append(current_map)
                            else:
                                map_n_map_k = []
                                map_n_map_k.append(current_map)

                            self._execute_section(section_name=flow_key, args=arguments, map_names_map_keys=map_n_map_k)
                        else:
                            if map_names_map_keys is not None:
                                map_n_map_k = copy.copy(map_names_map_keys)
                                map_n_map_k.append(current_map)
                            else:
                                map_n_map_k = []
                                map_n_map_k.append(current_map)

                            self.execute_object(flow_key, args=arguments, map_names_map_keys=map_n_map_k,
                                                section_name=section_name)

            elif key in self._script_sections:
                self._execute_section(section_name=key, args=arguments, map_names_map_keys=map_names_map_keys)
            else:
                if key[0] == "#":
                    continue
                self.execute_object(key, args=arguments, map_names_map_keys=map_names_map_keys,
                                    section_name=section_name)

    def execute_script(self):

        aaa = self.get_all_objects()
        self._executed_object_name = []

        mm = MouseManager()
        mm.move(0, 0)

        try:
            self._execute_section()
        except ValueError as e:
            try:
                self._execute_section(section_name="fail")
            except:
                pass

        try:
            self._execute_section(section_name="exit")
        except:
            pass
