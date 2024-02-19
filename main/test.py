import os
import base64
import hashlib
from cryptography.fernet import Fernet
from datetime import date

class Encryption:
    @staticmethod
    def get_cipher_suite(include_day = False):
        '''
        Master key is a constant
        Uses datetime so that the key changes daily
        Used to store private key and store passwords on database
        Using fernet encryption included with cryptography
        '''
        master_key = "748358A4B33C47299475E7F573FFEB67C374632AC342BC3537"
        if include_day:
            current_date = str(date.today())
            combined_string = (master_key + current_date).encode()
        else:
            combined_string = master_key.encode()
        hashed_key = hashlib.sha256(combined_string).digest()
        fernet_key = base64.urlsafe_b64encode(hashed_key)
        cipher_suite = Fernet(fernet_key)
        return cipher_suite



    @staticmethod
    def encrypt_for_db(plaintext_data):
        plaintext_data_bytes = bytes(plaintext_data, encoding='utf-8')
        cipher_suite = Encryption.get_cipher_suite()
        encrypted_data = cipher_suite.encrypt(plaintext_data_bytes)
        encrypted_data_str = base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
        return encrypted_data_str

    # decrypts data from database using permanent key
    @staticmethod
    def decrypt_from_db(encrypted_data):
        cipher_suite = Encryption.get_cipher_suite()
        encrypted_data_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
        plaintext_data = cipher_suite.decrypt(encrypted_data_bytes)
        plaintext_data_str = plaintext_data.decode('utf-8')
        return plaintext_data_str
    
    
print(Encryption.decrypt_from_db("Z0FBQUFBQmwwN3Y0TG5Gb2FJLUkyMDh1MGNIQXBKM2tHX2NEdHZ0bkpLT2k2R1N5Y18tSVY4YW1MRWRIUDNrdnYtTG1WekVrR1NsOXBwWlNCd0lpcVZsVkxwOTFLUU1seTVad09OUEZNUWVzc3l3VlRTOEZlcWpzcEx2WGhyZnN0eVM1d2JQbmg0TzRac1R6S2NxZGMxUThqVTBDeFhXZXc0Z0NybFBjZzJOLXc5VU1PaHNOeVd3PQ=="))
