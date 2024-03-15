import sys
sys.path.append('/home/BenCrook/mysite/')
import importlib.util

import RSAEncryption as rsa
import re
import traceback
from datetime import datetime
import connect

class AsyncRSA:
    @staticmethod
    def generate_keys():
        encryptor = rsa.KeyGeneration()
        return encryptor.generateKeys()

    @staticmethod
    def encrypt(x,e,n,encryptor):
        encrypted_x = str(encryptor.encrypt(x,e,n))
        encrypted_x += '-'
        return encrypted_x

    @staticmethod
    def encrypt_symmetric_key(key, e, n):
        try:
            key = str(key)
            e = int(e)
            n = int(n)
            keys = [key[i:i+4] for i in range(0, len(key),4)]
            encrypted_chunks = []
            encryptor = rsa.KeyGeneration()
            encrypted_chunks = list(
                map(lambda x: AsyncRSA.encrypt(x,e,n,encryptor), map(int,keys))
            )

            encrypted_key =''.join(encrypted_chunks)
            return encrypted_key

        except Exception as e:
            connect.write_errors(traceback.format_exc(),"encrypt_symmetric_key")
            return None

    @staticmethod
    def decrypt_symmetric_key(encrypted_key, d, n):
        try:
            encrypted_key = str(encrypted_key)
            d = int(d)
            n = int(n)
            numbers_list = encrypted_key.split('-')
            numbers_list.remove('')
            decrypted_chunks = []
            connect.write_errors(numbers_list,"decrypt_symmetric_key, numbers_list")
            encryptor = rsa.KeyGeneration()
            decrypted_chunks = list(
                map(lambda x: str(encryptor.decrypt(int(x), d, n)).zfill(4), numbers_list)
            )
            connect.write_errors(decrypted_chunks,"decrypt_symmetric_key, decrypted_chunks")
            decrypted_key =''.join(decrypted_chunks)
            return decrypted_key

        except Exception as e:
            connect.write_errors(traceback.format_exc(),"decrypt_symmetric_key")
            return None
