import sys
import copy
import time
from datetime import datetime
from alyvix.core.engine import EngineManager
from alyvix.tools.library import LibraryManager

class ParserManager:

    def __init__(self, library_json=None, chunk= None, engine_arguments=None, verbose=0, cipher_key=None, cipher_iv=None):
        self._verbose = verbose
        self._lm = LibraryManager()

        self._lm.set_json(library_json)
        self._chunk = chunk
        self._engine_arguments = engine_arguments
        self._objects_result = []

        self._objects = []
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

    def get_all_objects(self):

        self._objects = []

        self._iter_on_sections()

        self._objects = list(dict.fromkeys(self._objects))

        return self._objects

    def get_executed_objects(self):
        return self._executed_object_name

    def execute_object(self, object_name, map_and_key=None, args=None):
        if self._lm.check_if_exist(object_name) is False:
            print(object_name + " does NOT exist")
            sys.exit(2)

        object_json = self._lm.add_chunk(object_name, self._chunk)

        engine_manager = EngineManager(object_json, args=args, maps=self._script_maps, map_key=map_and_key,
                                       executed_objects=self._objects_result, verbose=self._verbose,
                                       cipher_key=self._key, cipher_iv=self._iv)

        result = engine_manager.execute()

        self._objects_result.append(result)
        self._executed_object_name.append(object_name)

        if result.performance_ms == -1 and result.has_to_break is True:
            """
            if self._verbose >= 1:
                print(self._get_timestamp_formatted() + ": Alyvix breaks " + result.object_name + " after " + str(result.timeout) + "s")
            """
            raise ValueError()
        elif result.performance_ms == -1 and result.has_to_break is False:
            """
            if self._verbose >= 1:
                print(self._get_timestamp_formatted() + ": Alyvix skips " + result.object_name + " after " + str(result.timeout) + "s")
            """
            return False
        elif result.performance_ms != -1:
            return True

    def get_results(self):
        return self._objects_result

    def _execute_section(self, section_name=None, args=None, map_and_key=None):

        if args is None:
            arguments = self._engine_arguments
        else:
            arguments = args

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

                    if self.execute_object(key["if_true"]):

                        if flow_key in self._script_sections:
                            self._execute_section(section_name=flow_key, map_and_key=map_and_key, args=arguments)
                        else:
                            self.execute_object(flow_key, args=arguments)

                elif if_key_false is not None:
                    if not self.execute_object(key["if_false"]):
                        if flow_key in self._script_sections:
                            self._execute_section(section_name=flow_key, map_and_key=map_and_key, args=arguments)
                        else:
                            self.execute_object(flow_key, args=arguments)

                elif for_key is not None:

                    selected_map = key["for"]

                    for map_key in self._script_maps[selected_map]:

                        map_value = self._script_maps[selected_map][map_key]
                        arguments = []

                        if isinstance(map_value, list):
                            arguments.extend(self._script_maps[selected_map][map_key])
                        else:
                            arguments.append(self._script_maps[selected_map][map_key])

                        if flow_key in self._script_sections:
                            self._execute_section(map_and_key=(selected_map, map_key), section_name=flow_key, args=arguments)
                        else:
                            self.execute_object(flow_key, map_and_key=(selected_map, map_key), args=arguments)
            elif key in self._script_sections:
                self._execute_section(section_name=key, map_and_key=map_and_key)
            else:
                if key[0] == "#":
                    continue
                self.execute_object(key, args=arguments, map_and_key=map_and_key)

    def execute_script(self):
        aaa = self.get_all_objects()
        self._executed_object_name = []

        try:
            self._execute_section()
        except ValueError as e:
            try:
                self._execute_section(section_name="fail")
            except ValueError as e:
                pass
        try:
            self._execute_section(section_name="exit")
        except ValueError as e:
            pass