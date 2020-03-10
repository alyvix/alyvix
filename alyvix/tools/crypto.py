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

from Cryptodome.Protocol.KDF import PBKDF2
from Cryptodome.Hash import SHA512
import base64
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
import json

class CryptoManager:

    def __init__(self):
        super(CryptoManager, self).__init__()
        self._key = None
        self._iv = None

    def create_key(self, password):
        if len(password) < 8:
            print("the password must be at least eight characters long")
            return
        salt = password[-1] + password[int(len(password)/2) + 1] + password[int(len(password)/2) - 1] + password[0]
        salt_hex_str = salt.encode("utf-8").hex()
        salt_hex_int = int(salt_hex_str, 16)
        new_int = salt_hex_int + 0x2000
        salt_string = hex(new_int)[2:]
        bytes = PBKDF2(password, salt_string, 48, count=1000000, hmac_hash_module=SHA512)
        self._iv = bytes[0:16]
        self._key = bytes[16:48]

    def get_key(self):
        return self._key

    def get_iv(self):
        return self._iv

    def set_key(self, key):
        self._key = key

    def set_iv(self, iv):
        self._iv = iv

    def encrypt(self, text):

        encrypter = AES.new(self._key, AES.MODE_CBC, IV=self._iv)

        text_pad = self._pad(text)

        value = base64.b64encode(encrypter.encrypt(bytes(text_pad, encoding="utf-8")))

        return value.decode(encoding='UTF-8')

    def decrypt(self, text):
        #AES.key_size = 128
        data = base64.b64decode(text)

        crypt_object = AES.new(key=self._key, mode=AES.MODE_CBC, IV=self._iv)
        data = crypt_object.decrypt(data)

        data = data[:-data[-1]] #unpad

        return data.decode(encoding='UTF-8')

    def _pad(self, data):
        """
        Pad value with bytes (it has a multiple of 16)

        """

        len_bytes = len(bytes(data, encoding="utf-8"))

        length = 16 - (len_bytes % 16)
        data += chr(length)*length
        return data