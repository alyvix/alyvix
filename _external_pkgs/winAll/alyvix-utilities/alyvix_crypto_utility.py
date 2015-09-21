from alyvix.tools.crypto import CryptoManager

cm = CryptoManager()

print ""
print "Alyvix crypto utility, by Alan Pipitone"
print "http://www.alyvix.com"
print ""
print "Press e to encrypt data, press d to decrypt data."
print "Press k to set the key to encrypt/decrypt data."
print "Press q to quit."
print ""

def encrypt():
    if cm.check_if_key_exists() is True:
        plaintext = raw_input('Type the text to encrypt: ')
        chipertext = cm.crypt_data(plaintext)
        print chipertext
    else:
        print "You have to set the private key!"
    
def decrypt():
    if cm.check_if_key_exists() is True:
        chiphertext = raw_input('Type the text to decrypt: ')
        plaintext = cm.decrypt_data(chiphertext)
        print plaintext
    else:
        print "You have to set the private key!"

def set_key():
    key = raw_input('Type the key: ')
    confirm = raw_input('Please confirm (y/n): ')
    if confirm.lower() == "y":
        cm.set_key(key)

while True:
    user_choice = raw_input('Type your choice: ')
    user_choice = user_choice.lower()

    if user_choice == "e":
        encrypt()
    elif user_choice == "d":
        decrypt()
    elif user_choice == "k":
        set_key()
    elif user_choice == "q":
        break
