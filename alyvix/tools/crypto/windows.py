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

from .base import CryptoManagerBase

import os
from ctypes import *
from ctypes.wintypes import DWORD
from win32com.shell import shellcon, shell
import binascii

class _DATA_BLOB(Structure):
    _fields_ = [("cbData", DWORD), ("pbData", POINTER(c_char))]

class CryptoManager(CryptoManagerBase):

    def __init__(self):
        self._CRYPTPROTECT_UI_FORBIDDEN = 0x01

    def _get_data(self, blob_out):
        cb_data = int(blob_out.cbData)
        pb_data = blob_out.pbData
        buffer = c_buffer(cb_data)
        cdll.msvcrt.memcpy(buffer, pb_data, cb_data)
        windll.kernel32.LocalFree(pb_data)
        return buffer.raw

    def _win32_crypt_protect_data(self, plain_text):
        buffer_in = c_buffer(plain_text, len(plain_text))
        blob_in = _DATA_BLOB(len(plain_text), buffer_in)
        blob_out = _DATA_BLOB()

        if windll.crypt32.CryptProtectData(byref(blob_in), None, None,
                                           None, None, self._CRYPTPROTECT_UI_FORBIDDEN, byref(blob_out)):
            return self._get_data(blob_out)
        else:
            return ""

    def _win32_crypt_unprotect_data(self, cipher_text):
        buffer_in = c_buffer(cipher_text, len(cipher_text))
        blob_in = _DATA_BLOB(len(cipher_text), buffer_in)
        blob_out = _DATA_BLOB()

        if windll.crypt32.CryptUnprotectData(byref(blob_in), None, None, None, None,
                                             self._CRYPTPROTECT_UI_FORBIDDEN, byref(blob_out)):
            return self._get_data(blob_out)
        else:
            return ""

    def _get_user_app_data_local(self):
        app_data_folder = shell.SHGetFolderPath(0, shellcon.CSIDL_LOCAL_APPDATA, 0, 0)
        return app_data_folder

    def set_key(self, private_key):
        private_key_protected = self._win32_crypt_protect_data(private_key)
        private_key_protected_hex = str(binascii.hexlify(private_key_protected)).upper()

        app_data_folder = self._get_user_app_data_local()
        alyvix_app_data_folder = app_data_folder + os.sep + "alyvix"
        hex_file_name = alyvix_app_data_folder + os.sep + "master.hex"

        if not os.path.exists(alyvix_app_data_folder):
            os.makedirs(alyvix_app_data_folder)

        with open(hex_file_name, "w") as text_file:
            text_file.write(private_key_protected_hex)

    def get_key(self):

        private_key_protected_hex = ""

        app_data_folder = self._get_user_app_data_local()
        alyvix_app_data_folder = app_data_folder + os.sep + "alyvix"
        hex_file_name = alyvix_app_data_folder + os.sep + "master.hex"

        if os.path.exists(hex_file_name):
            with open(hex_file_name, "r") as text_file:
                private_key_protected_hex = text_file.read()

            private_key_protected = str(binascii.unhexlify(private_key_protected_hex.lower()))

            private_key_unprotected = self._win32_crypt_unprotect_data(private_key_protected)

            return private_key_unprotected

        return ""