# Alyvix allows you to automate and monitor all types of applications
# Copyright (C) 2020 Alan Pipitone
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

import re
import base64
from alyvix.tools.crypto import CryptoManager


class ArgsManager:

    def __init__(self):
        super(ArgsManager, self).__init__()

    def get_string(self, input_string, arguments, performances, maps, crypto_manager):

        # output_string = "sadfasfdasf asfdf {arg1} dfdfdfd {arg2}"
        
        output_string = input_string

        # args_in_string = re.findall("\\{arg[0-9]+\\}", output_string,re.IGNORECASE)
        args_in_string = re.findall(r"\{[1-9]\d*\}|\{[1-9]\d*[^\}]+\}", output_string, re.IGNORECASE)

        for arg_pattern in args_in_string:

            str_value = ""

            pattern = arg_pattern.replace("{", "").replace("}", "")

            if "," in pattern:

                index, default_arg = pattern.split(",", 1)
                str_value = default_arg
            else:
                index = pattern

            try:
                i = int(index)

                # self._result.arguments.append(arguments[i-1])
                str_value = arguments[i - 1]
            except:
                pass

            if crypto_manager.get_key() is not None and crypto_manager.get_iv() is not None:
                try:
                    unenc_string = base64.b64decode(str_value)
                    decrypted_str = crypto_manager.decrypt(str_value)
                    if decrypted_str != "":  # wrong password
                        str_value = decrypted_str
                except:  # string is not base 64
                    pass

            output_string = output_string.replace(arg_pattern, str_value)

        # args_in_string = re.findall("\\{arg[0-9]+\\}", output_string,re.IGNORECASE)
        extract_args = re.findall(r"(\{[\w]+\.extract\}|{[\w]+\.extract,[^\}]+\})", output_string,
                                  re.IGNORECASE | re.UNICODE)
        # re.findall("\\{.*\\.extract\\}", output_string, re.IGNORECASE)

        for arg_pattern in extract_args:

            extract_value = ""

            pattern = arg_pattern.replace("{", "").replace("}", "")

            if "," in pattern:

                obj_name, default_arg = pattern.split(",", 1)
                obj_name = obj_name.split(".")[0]
                extract_value = default_arg
            else:
                obj_name = pattern.split(".")[0]

            for perf in reversed(performances):

                try:
                    if perf.object_name == obj_name:

                        for series in perf.series:
                            if series["exit"] == "not_executed":
                                continue
                            else:
                                extract_value = series["records"]["extract"]
                                break
                except:
                    pass  # not enought arguments

            if crypto_manager.get_key() is not None and crypto_manager.get_iv() is not None:
                try:
                    unenc_string = base64.b64decode(extract_value)
                    decrypted_str = crypto_manager.decrypt(extract_value)
                    if decrypted_str != "":  # wrong password
                        extract_value = decrypted_str
                except:  # string is not base 64
                    pass

            output_string = output_string.replace(arg_pattern, extract_value)
            # self._result.arguments.append(extract_value)

        # [ ^\}] all that is not parentesdi graffa
        text_args = re.findall(r"(\{[\w]+\.text\}|{[\w]+\.text,[^\}]+\})", output_string, re.IGNORECASE | re.UNICODE)

        # a = output_string[output_string.find("{")+1:output_string.find("}")]

        for arg_pattern in text_args:

            text_value = ""

            pattern = arg_pattern.replace("{", "").replace("}", "")

            if "," in pattern:

                obj_name, default_arg = pattern.split(",", 1)
                obj_name = obj_name.split(".")[0]
                text_value = default_arg
            else:
                obj_name = pattern.split(".")[0]

            for perf in reversed(performances):

                try:

                    if perf.object_name == obj_name:

                        for series in perf.series:
                            if series["exit"] == "not_executed":
                                continue
                            else:
                                text_value = series["records"]["text"]
                                break
                except:
                    pass  # not enought arguments

            if crypto_manager.get_key() is not None and crypto_manager.get_iv() is not None:
                try:
                    unenc_string = base64.b64decode(text_value)
                    decrypted_str = crypto_manager.decrypt(text_value)
                    if decrypted_str != "":  # wrong password
                        text_value = decrypted_str
                except:  # string is not base 64
                    pass

            output_string = output_string.replace(arg_pattern, text_value)
            # self._result.arguments.append(text_value)

        check_args = re.findall(r"(\{[\w]+\.check\}|{[\w]+\.check,[^\}]+\})", output_string,
                                re.IGNORECASE | re.UNICODE)
        # re.findall("\\{.*\\.check\\}", output_string, re.IGNORECASE)

        for arg_pattern in check_args:

            check_value = ""

            pattern = arg_pattern.replace("{", "").replace("}", "")

            if "," in pattern:

                obj_name, default_arg = pattern.split(",", 1)
                obj_name = obj_name.split(".")[0]
                check_value = default_arg
            else:
                obj_name = pattern.split(".")[0]

            for perf in reversed(performances):
                try:

                    if perf.object_name == obj_name:

                        for series in perf.series:
                            if series["exit"] == "not_executed":
                                continue
                            else:
                                check_value = series["records"]["check"]
                                break
                except:
                    pass  # not enought arguments

            if crypto_manager.get_key() is not None and crypto_manager.get_iv() is not None:
                try:
                    unenc_string = base64.b64decode(check_value)
                    decrypted_str = crypto_manager.decrypt(check_value)
                    if decrypted_str != "":  # wrong password
                        check_value = decrypted_str
                except:  # string is not base 64
                    pass

            output_string = output_string.replace(arg_pattern, check_value)
            # self._result.arguments.append(text_value)

        maps_args = re.findall(r"(\{[\w]+\.[\w]+\}|{[\w]+\.[\w]+,[^\}]+\})", output_string,
                               re.IGNORECASE | re.UNICODE)
        # re.findall("\\{.*\\..*\\}", output_string, re.IGNORECASE)

        for arg_pattern in maps_args:

            str_value = ""

            pattern = arg_pattern.replace("{", "").replace("}", "")

            if "," in pattern:

                map_n_k, default_arg = pattern.split(",", 1)
                map_name = map_n_k.split(".")[0]
                map_key = map_n_k.split(".")[1]
                str_value = default_arg
            else:
                map_name = pattern.split(".")[0]
                map_key = pattern.split(".")[1]

            try:

                map_value = maps[map_name][map_key]

                if isinstance(map_value, list):
                    str_value = ""
                    for obj in map_value:
                        str_value += str(obj) + " "

                    str_value = str_value[:-1]
                else:
                    str_value = str(map_value)

                if crypto_manager.get_key() is not None and crypto_manager.get_iv() is not None:
                    try:
                        unenc_string = base64.b64decode(str_value)
                        decrypted_str = crypto_manager.decrypt(str_value)
                        if decrypted_str != "":  # wrong password
                            str_value = decrypted_str
                    except:  # string is not base 64
                        pass

            except:
                pass  # not enought arguments

            output_string = output_string.replace(arg_pattern, str_value)
            # self._result.arguments.append(str_value)

        return output_string

