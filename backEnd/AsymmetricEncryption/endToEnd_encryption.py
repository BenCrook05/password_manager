# import backEnd.AsymmetricEncryption.RSAEncryption as rsa
import RSAEncryption as rsa
import re
import traceback

class AsyncRSA:
    @staticmethod
    def generate_keys(random = True, seed = "0"):
        encryptor = rsa.KeyGeneration()
        return encryptor.generateKeys(random, seed)
        
        
    @staticmethod
    def encrypt(x,e,n,encryptor):
        encrypted_x = str(encryptor.encrypt(x,e,n))
        encrypted_x += '-'
        return encrypted_x
            
    @staticmethod
    def encrypt_symmetric_key(key, e, n, increments=4):
        try:
            key = str(key)
            e = int(e)
            n = int(n)
            keys = [key[i:i+increments] for i in range(0, len(key),increments)]
            encrypted_chunks = []
            encryptor = rsa.KeyGeneration()
            encrypted_chunks = list(
                map(lambda x: AsyncRSA.encrypt(x,e,n,encryptor), map(int,keys))
            )
            encrypted_key =''.join(encrypted_chunks)
            return encrypted_key
        
        except Exception as e:
            print(traceback.format_exc())
            return None
        
    @staticmethod
    def decrypt_symmetric_key(encrypted_key, d, n, increments=4):
        try:
            encrypted_key = str(encrypted_key)
            d = int(d)
            n = int(n)
            numbers_list = encrypted_key.split('-')
            numbers_list.remove('')
            numbers_list = list(map(int, numbers_list))
            decrypted_chunks = []
            encryptor = rsa.KeyGeneration()
            decrypted_chunks = list(
                map(lambda x: str(encryptor.decrypt(int(x), d, n)).zfill(increments), numbers_list)
            )
            decrypted_key =''.join(decrypted_chunks)
            return decrypted_key
        
        except Exception as e:
            print(traceback.format_exc())
            return None
   
   
import time     
keys = []
for i in range(10):
    time.sleep(1)
    new_key = AsyncRSA.generate_keys()
    keys.append(new_key)
    print(new_key)
    
print(keys)
i = input("Continue? ")
ciphertext = []
for key in keys:
    new_ciphertext = AsyncRSA.encrypt_symmetric_key("12345678", key[1], key[2], increments=4)
    ciphertext.append(new_ciphertext)
    print(new_ciphertext)

i = input("Continue? ")
plaintext = []
for i in range(len(ciphertext)):
    new_plaintext = AsyncRSA.decrypt_symmetric_key(ciphertext[i], keys[i][0], keys[i][2],increments=4)
    plaintext.append(new_plaintext)
    print(new_plaintext)

i = input("Continue? ")
seed = "BenCrook"
for i in range(10):
    print(AsyncRSA.generate_keys(random=False, seed=seed))
    
    
import random
import string

i = input("Continue? ")
for i in range(10):
    seed = ''.join(random.choices(string.ascii_letters + string.digits, k=25))
    print(AsyncRSA.generate_keys(random=False, seed=seed))
