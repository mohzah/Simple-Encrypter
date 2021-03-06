# -*- coding: utf-8 -*-

"""Copyright Mohammad Hassan Zahraee 2016
"""
import os
import random
import struct
import hashlib
from Crypto.Cipher import AES


class MyCipher():
    """ Encryption and decryption are done in chunksize to prevent running out
        of memory for large fales.
        For encryption AES (256bit) in CBC mode is used.
    """
    def __init__(self, password, infile):
        self.key = hashlib.sha256(password.encode('utf-8')).digest()
        self.infile = infile
        self.chunksize = 64*1024

    def encrypt(self):
        # 16 byte random IV
        iv = ''.join([chr(random.randint(0, 0xFF)) for i in range(16)])
        iv = iv.encode()[:16]
        encryptor = AES.new(self.key, AES.MODE_CBC, iv)
        tempfile = self.infile + ".tmp"
        filesize = os.path.getsize(tempfile)

        with open(tempfile, 'rb') as infile:
            with open(self.infile, 'wb') as outfile:
                outfile.write(struct.pack('<Q', filesize))
                outfile.write(iv)

                while True:
                    chunk = infile.read(self.chunksize)
                    if len(chunk) == 0:
                        break
                    elif len(chunk) % 16 != 0:
                        # padding to make data size divisible by 16
                        chunk += ' ' * (16 - len(chunk) % 16)

                    outfile.write(encryptor.encrypt(chunk))
        return True

    def decrypt(self):
        out_filename = os.path.splitext(self.infile)[0] + '.tar'
        with open(self.infile, 'rb') as infile:
            origsize = struct.unpack('<Q',
                                     infile.read(struct.calcsize('Q'))
                                     )[0]
            iv = infile.read(16)
            decryptor = AES.new(self.key, AES.MODE_CBC, iv)

            with open(out_filename, 'wb') as outfile:
                while True:
                    chunk = infile.read(self.chunksize)
                    if len(chunk) == 0:
                        break
                    outfile.write(decryptor.decrypt(chunk))

                outfile.truncate(origsize)
        return out_filename
