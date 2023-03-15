import os
import re
import zipfile
import datetime
from pathlib import Path
from playwright.sync_api import Playwright, sync_playwright, expect
from .parser import Performance
from alyvix.tools.screen import ScreenManager

class PlaywrightManager:

    def get_unique_flattern_performances(self, performances):

        executed_flattern_performances = []
        not_executed_flattern_performances = []

        #performances = self._performances #copy.deepcopy(self.get_performances())

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

    def run_script(self, filename):

        sm = ScreenManager()
        w, h = sm.get_resolution()
        scaling_factor = sm.get_scaling_factor()

        testcase = filename #"C:\\test\\playwright\\test_ori.py"

        start_read_testcase = False
        start_try_body = False
        python_code = ""

        indent_code_l1 = " " * 4
        indent_code_l2 = " " * 8

        defined_performances = []
        performances = []

        zip_name = ""

        with open(testcase, "r") as file_object:

            while True:
                line_object = file_object.readline()

                perf_string = line_object

                name = None
                if "page.goto" in perf_string:
                    name = perf_string.strip()
                    name = re.sub("^page\\.goto\\(\"", "", name, count=0, flags=0)
                    name = re.sub("\"\\)$", "", name, count=0, flags=0)
                    type = "goto"
                elif "page.locator" in perf_string:
                    name = perf_string.strip()
                    name = re.sub("^page\\.locator\\(\"", "", name, count=0, flags=0)
                    name = re.sub("\"\\)\\.?.*", "", name, count=0, flags=0)
                    type = "locator"
                elif "page.get_by_role" in perf_string:
                    name = perf_string.strip()
                    name = re.sub("^page\\.get_by_role\\(.*name=\"", "", name, count=0, flags=0)
                    name = re.sub("\".*\\)\\.?.*", "", name, count=0, flags=0)
                    type = "get_by_role"
                elif "page.get_by_placeholder" in perf_string:
                    name = perf_string.strip()
                    name = re.sub("^page\\.get_by_placeholder\\(\"", "", name, count=0, flags=0)
                    name = re.sub("\"\\)\\.?.*", "", name, count=0, flags=0)
                    type = "get_by_placeholder"

                if name is not None:
                    defined_performances.append({"name": name, "type": type})
                    name = None

                line_object = line_object.strip() + os.linesep

                if "def run(playwright:" in line_object:
                    start_read_testcase = True

                if start_read_testcase is True:
                    # python_code += line_object

                    if "browser = playwright.chromium.launch(headless=False)" in line_object:
                        python_code += indent_code_l1 + line_object
                        python_code += indent_code_l1 + "context = browser.new_context()" + os.linesep
                        python_code += indent_code_l1 + "context.tracing.start(screenshots=True, snapshots=True, sources=True)" + os.linesep
                        python_code += indent_code_l1 + "try:" + os.linesep
                        start_try_body = True
                        continue

                    if "context.close()" in line_object:  # and start_try_body is True:

                        python_code += indent_code_l1 + "except:" + os.linesep
                        python_code += indent_code_l1 + indent_code_l1 + "pass" + os.linesep

                        zip_name = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S") + "_trace"
                        python_code += indent_code_l1 + "context.tracing.stop(path = \"" + zip_name + ".zip\")" + os.linesep

                        python_code += indent_code_l1 + line_object

                        python_code += indent_code_l1 + "browser.close()"
                        break

                    if start_try_body is True:
                        if "context = browser.new_context()" in line_object:
                            continue
                        python_code += indent_code_l1 + indent_code_l1 + line_object

                # if line is empty
                # end of file is reached
                if not line_object:
                    break

        python_code = "with sync_playwright() as playwright:" + os.linesep + python_code

        line_object = "\"a358a147ec7fff\",\"wallTime\":1678830365590,\"startTime\":858587598.991,\"endTime\":858587982.651,\"type\":\"Frame\",\"method\":\"click\",\"para waiting for get_by_placeholder(\\\"Name, surname\\\")"

        exec(python_code)

        Path(zip_name).mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_name + ".zip", 'r') as zip_ref:
            zip_ref.extractall(zip_name)

        cnt = 0
        for performance in defined_performances:
            perf = Performance()
            perf.object_name = performance["name"]
            perf_series = {
                "object_name": performance["name"],
                "series_name": performance["name"],
                "performance_name": performance["name"],
                "detection_type": performance["type"],
                "group": None,
                "output": True,
                "thresholds": {},
                "performance_ms": -1,
                "accuracy_ms": -1,
                "timestamp": -1,
                "end_timestamp": -1,
                "initialize_cnt": cnt + 1,
                "records": {"text": "", "image": "", "extract": "", "check": "not_executed"},
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
            perf.series.append(perf_series)
            performances.append(perf)


        with open(zip_name + os.sep + "trace.trace", "r") as file_object:

            line = 1
            while True:
                line_object = file_object.readline()

                if line == 326:
                    a = None
                    pass

                for performance in performances:

                    name = performance.object_name

                    if "Name" in name:
                        a = ""

                    for char in ["\\", ".", "+", "*", "?", "^", "$", "(", ")", "[", "]", "{", "}", "|", "/"]:
                        name = name.replace(char, "\\" + char)

                    pattern = ".*" + performance.series[0]["detection_type"] + "\\(.*" + name + ".*"
                    match = re.match(pattern, line_object)

                    if match is None:
                        pattern = ".*" + performance.series[0]["detection_type"] + "\",\"params\".*" + name + ".*"
                        match = re.match(pattern, line_object)

                    if match is not None:
                        perf_value = -1
                        try:
                            starttime = re.sub(".*startTime\":", "", line_object, count=0, flags=0)
                            starttime = re.sub(",.*", "", starttime, count=0, flags=0)
                            starttime = float(starttime)

                            endtime = re.sub(".*endTime\":", "", line_object, count=0, flags=0)
                            endtime = re.sub(",.*", "", endtime, count=0, flags=0)
                            endtime = float(endtime)

                            wallTime = re.sub(".*wallTime\":", "", line_object, count=0, flags=0)
                            wallTime = re.sub(",.*", "", wallTime, count=0, flags=0)
                            wallTime = float(wallTime)/1000

                            perf_value = endtime - starttime


                        except:
                            pass
                        #performance["value"] = perf_value

                        if performance.series[0]["exit"] == "not_executed":
                            performance.series[0]["exit"] = "true"
                            performance.series[0]["state"] = 0
                            performance.series[0]["performance_ms"] = perf_value
                            performance.series[0]["timestamp"] = wallTime
                            performance.series[0]["end_timestamp"] = wallTime + perf_value
                        else:
                            perf_series = {
                                "object_name": performance.object_name,
                                "series_name": performance.object_name,
                                "performance_name": performance.object_name,
                                "detection_type": performance.series[0]["detection_type"],
                                "group": None,
                                "output": True,
                                "thresholds": {},
                                "performance_ms": perf_value,
                                "accuracy_ms": -1,
                                "timestamp": wallTime,
                                "end_timestamp": wallTime + perf_value,
                                "initialize_cnt": performance.series[0]["initialize_cnt"],
                                "records": {"text": "", "image": "", "extract": "", "check": "not_executed"},
                                "timeout": None,
                                "exit": "true",
                                "state": 0,
                                "resolution": {
                                    "width": w,
                                    "height": h
                                },
                                "scaling_factor": int(scaling_factor * 100),
                                "screenshot": None,
                                "annotation": None
                            }

                            performance.series.append(perf_series)


                        aa = ""

                line += 1

                if not line_object:
                    break

        return performances