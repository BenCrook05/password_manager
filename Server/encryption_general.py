import endToEnd_encryption as rsa
import base64
import os
from dotenv import load_dotenv
load_dotenv('/home/BenCrook/mysite/.env')
import hashlib
from cryptography.fernet import Fernet
import random
from datetime import date, datetime
import connect


class Encryption:
    @staticmethod
    def generate_asymmetric_keys():
        ### CREATE KEYS AS LIST ###
        e, d, n = rsa.AsyncRSA.generate_keys()
        e = int(e)
        d = int(d)
        n = int(n)
        public_key = [e, n]
        private_key = [d, n]
        return e, d, n

    @staticmethod
    def reset_server_key():
        keys = Encryption.generate_asymmetric_keys()
        server_private_key = keys[0]
        server_public_key = keys[1]
        server_public_n = keys[2]
        server_private_key = str(server_private_key)
        server_public_key = str(server_public_key)
        server_public_n = str(server_public_n)
        server_private_key_bytes=bytes(server_private_key, encoding='utf8')
        server_public_key_bytes=bytes(server_public_key, encoding='utf8')
        server_public_n_bytes=bytes(server_public_n, encoding='utf8')
        cipher_suite = Encryption.get_cipher_suite(True)
        ciphertext_private_key = cipher_suite.encrypt(server_private_key_bytes)
        ciphertext_public_key = cipher_suite.encrypt(server_public_key_bytes)
        ciphertext_public_n = cipher_suite.encrypt(server_public_n_bytes)
        ciphertext_private_key_str = base64.b64encode(ciphertext_private_key).decode('utf-8')
        ciphertext_public_key_str = base64.b64encode(ciphertext_public_key).decode('utf-8')
        ciphertext_public_n_str = base64.b64encode(ciphertext_public_n).decode('utf-8')
        db = connect.connect_to_db()
        curs = db.cursor()
        curs.execute(f"DELETE FROM AsymmetricKeys")
        today = str(date.today())
        curs.execute(f"INSERT INTO AsymmetricKeys(e,d,n,date) VALUES('{ciphertext_public_key_str}','{ciphertext_private_key_str}','{ciphertext_public_n_str}','{today}')")
        curs.close()
        db.commit()
        db.close()


    @staticmethod
    def get_cipher_suite(include_day = False):
        '''
        Master key is a constant
        Uses datetime so that the key changes daily
        Used to store private key and store passwords on database
        Using fernet encryption included with cryptography
        '''
        master_key = os.getenv('MASTERKEY')
        if include_day:
            current_date = str(date.today())
            combined_string = (master_key + current_date).encode()
        else:
            combined_string = master_key.encode()
        hashed_key = hashlib.sha256(combined_string).digest()
        fernet_key = base64.urlsafe_b64encode(hashed_key)
        cipher_suite = Fernet(fernet_key)
        return cipher_suite


    ### get functions for private/public keys for asymmetric encryption

    @staticmethod
    def get_server_key(key = 1):  #1 for public, 0 for private -(corresponds to index)

        try:
            db = connect.connect_to_db()
            curs = db.cursor()
            curs.execute(f"SELECT e,d,n,date FROM AsymmetricKeys")
            data = curs.fetchone()
            curs.close()
            db.close()
            cipher_suite = Encryption.get_cipher_suite(True)
            if key == 1:
                ciphertext_exp = data[0]
                ciphertext_n = data[2]
            elif key == 0:
                ciphertext_exp = data[1]
                ciphertext_n = data[2]

            ciphertext_exp_bytes = base64.b64decode(ciphertext_exp.encode('utf-8'))
            ciphertext_n_bytes = base64.b64decode(ciphertext_n.encode('utf-8'))
            if str(data[3]) == str(date.today()):
                try:
                    plaintext_exp = cipher_suite.decrypt(ciphertext_exp_bytes)
                    plaintext_n = cipher_suite.decrypt(ciphertext_n_bytes)
                    plaintext_exp_str = plaintext_exp.decode(encoding='utf-8')
                    plaintext_n_str = plaintext_n.decode(encoding='utf-8')
                    return [plaintext_exp_str, plaintext_n_str]
                except Exception as e:
                    return ["FAILED",str(e)]

            Encryption.reset_server_key()
            return Encryption.get_server_key(key)
        except Exception as e:
            Encryption.reset_server_key()
            return Encryption.get_server_key(key)


    # encrypts to store data on the database
    @staticmethod
    def encrypt_for_db(plaintext_data):
        if not isinstance(plaintext_data, str):
            plaintext_data = str(plaintext_data)
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

    @staticmethod
    def encryptdecrypt_directory(data, symmetric_key, encryptor, count=0):
        count += 1
        if isinstance(data, dict):
            for key, value in data.items():
                data[key] = Encryption.encryptdecrypt_directory(value, symmetric_key, encryptor) #has to treat dic differently as can't iterate through
            return data
        
        elif isinstance(data, (list, tuple, set)):
            encrypted_data = [Encryption.encryptdecrypt_directory(element, symmetric_key, encryptor) for element in data] #iterates through list and executes encryptdecrpt_directory on each element
            return type(data)(encrypted_data)
        
        elif isinstance(data, str):
            # length = (len(data) + count) % len(symmetric_key)
            # start_pos = int(symmetric_key[length])
            # symmetric_key = symmetric_key[start_pos:] + symmetric_key[:start_pos] 
            # return encryptor.encryptdecrypt(data, str(symmetric_key), encryptor)
            return Encryption.encryptdecrypt(data,str(symmetric_key),encryptor)
        else:
            return data #doesn't encrypt if not a string (as can't encrypt int and boolean function etc)

    @staticmethod
    def encryptdecrypt(data: str, key: str, encrypt: bool):
        cipher_suite = Encryption.generate_fernet(key)
        if encrypt:
            return cipher_suite.encrypt(data.encode('utf-8')).decode('utf-8')
        else:
            return cipher_suite.decrypt(data.encode('utf-8')).decode('utf-8')

    @staticmethod
    def generate_fernet(extra=""): #identical to client function
        ADDED_STRING = os.getenv("ADDED_STRING") #stored as environment variable
        ADDED_STRING += extra
        ADDED_STRING = ADDED_STRING[-50:]  #gets last 50 characters
        combined_string = ADDED_STRING.encode()
        hashed_key = hashlib.sha256(combined_string).digest()
        fernet_key_base64 = base64.urlsafe_b64encode(hashed_key)
        fernet_key = Fernet(fernet_key_base64)
        return fernet_key
    
    @staticmethod
    def generate_symmetric_key(length=24):
        key = ""
        for i in range(length):
            random_char = chr(random.randint(0, 9) + ord('0'))
            key += random_char
        return key

    @staticmethod
    def encrypt_key_to_client(data, client_public_key):
        e, n = client_public_key
        encrypted_key = rsa.AsyncRSA.encrypt_symmetric_key(data, e, n)
        return encrypted_key

    @staticmethod
    def encrypt_data_to_client(data, symmetric_key):
        # encryptor = xor.XorEncryption()
        # encrypted_data = Encryption.encryptdecrypt_directory(data, symmetric_key, encryptor)
        encrypted_data = Encryption.encryptdecrypt_directory(data, symmetric_key, True)
        return encrypted_data

    @staticmethod
    def decrypt_key_from_client(data):
        d, n = Encryption.get_server_key(0)
        #print(f"Encrypted key: {data}")
        decrypted_key = rsa.AsyncRSA.decrypt_symmetric_key(data, d, n)
        return decrypted_key

    @staticmethod
    def decrypt_data_from_client(data, symmetric_key):
        # encryptor = xor.XorEncryption()
        # decrypted_data = Encryption.encryptdecrypt_directory(data, symmetric_key, encryptor)
        decrypted_data = Encryption.encryptdecrypt_directory(data, symmetric_key, False)
        return decrypted_data

    @staticmethod
    def create_error_check(length=16):
        modulus = random.randint(100,999)
        divisor = random.randint(10**(length-3), 10**(length-2)-1)
        integer_div = divisor // modulus
        real_divisor = integer_div * modulus
        return str(modulus)+str(real_divisor)

    @staticmethod
    def validate_error_check(data):
        modulus = int(data[:3])
        real_divisor = int(data[3:])
        if real_divisor % modulus == 0:
            return True
        else:
            return False

