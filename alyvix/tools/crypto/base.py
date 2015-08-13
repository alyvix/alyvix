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

import pyaes
import binascii

class CryptoManagerBase(object):

    def set_key(self, private_key):
        raise NotImplementedError

    def get_key(self):
        raise NotImplementedError

    def crypt_data(self, plaintext):
        key = self.get_key()
        if key == "":
            return ""
        aes = pyaes.AESModeOfOperationCTR(key)
        ciphertext = aes.encrypt(plaintext)
        ciphertext_base64 = str(binascii.b2a_base64(ciphertext))
        return ciphertext_base64

    def decrypt_data(self, ciphertext_base64):
        key = self.get_key()
        if key == "":
            return ""
        aes = pyaes.AESModeOfOperationCTR(key)
        ciphertext = str(binascii.a2b_base64(ciphertext_base64))
        decrypted = aes.decrypt(ciphertext).decode('utf-8')
        return decrypted