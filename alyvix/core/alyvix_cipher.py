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

import sys
import base64
from alyvix.tools.crypto import CryptoManager

help_main_string = '''usage: alyvix_robot.py [-h] --key FILENAME 
                            --encrypt TEXT_TO_ENCRYPT [or --decrypt TEXT_TO_DECRYPT]'''


def print_help():
    print("""\r\nAlyvix Cipher protects sensitive information like credentials by encrypting
it with a private key.  The encrypted key can then be used in an Alyvix test
case even though it has an open format.\r\n""")

    print(help_main_string)

    help_info = '''
Optional arguments:
  -h, --help     Show this help message and exit
  
Required arguments:
  --key KEY, -k KEY
                 Specify the private key to use for encryption
  --encrypt TEXT_TO_ENCRYPT, -e TEXT_TO_ENCRYPT
    [or --decrypt TEXT_TO_DECRYPT, -d TEXT_TO_DECRYPT]
                 Specify the information to be encrypted (e.g. credentials)'''
    print(help_info)

    sys.exit(0)

key = None
text_to_encrypt = None
text_to_decrypt = None

for i in range(0, len(sys.argv)):
    if sys.argv[i] == "-k" or sys.argv[i] == "--key":
        key = sys.argv[i+1]
        if len(key) < 8:
            print("the encryption key must be at least eight characters long")
            exit(2)
    elif sys.argv[i] == "-d" or sys.argv[i] == "--decrypt":
        text_to_decrypt = sys.argv[i + 1]
    elif sys.argv[i] == "-e" or sys.argv[i] == "--encrypt":
        text_to_encrypt = sys.argv[i + 1]
    elif sys.argv[i] == "-h" or sys.argv == "--help":
        print_help()
        exit(0)

if key is None:
    print_help()
    exit(0)

if text_to_decrypt is None and text_to_encrypt is None:
    print_help()
    exit(0)

cm = CryptoManager()
cm.create_key(key)

if key is not None:
    try:
        if text_to_encrypt is not None:
            encrypted_txt = cm.encrypt(text_to_encrypt)
            print(encrypted_txt)
        elif text_to_decrypt is not None:
            decrypted_txt = cm.decrypt(text_to_decrypt)
            print(decrypted_txt)
    except:
        pass