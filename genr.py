from Crypto.Cipher import AES
import hashlib

from Crypto.Cipher import AES
def do_thing:
    password = 'kitty'.encode('utf-8')
    key = hashlib.sha256(password).digest()
    print(key)
    IV = 16 * '\x00'           # Initialization vector: discussed later
    mode = AES.MODE_CBC
    encryptor = AES.new(key, mode, IV=IV)

    ciphertext = encryptor.encrypt('l1lk1msayshello!')
    print(ciphertext)
    #d = b'\xbe\x13\xbf\x9f\xc5T\x1a8/\x93\xa1w$"\xc9\xe2z#\xder\xc8\x1c-\x03\x86\xd5x+6l\xc8Q'
    decryptor = AES.new(key, mode, IV=IV)
    plain = decryptor.decrypt(ciphertext)
    return(key,ciphertext)