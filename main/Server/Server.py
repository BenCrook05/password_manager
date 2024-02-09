import sys
sys.path.append('/home/BenCrook/mysite/')

from flask import Flask, request, jsonify

import endToEnd_encryption as rsa

import XorEncryption as xor

import MySQLdb
import json
import requests

from datetime import datetime, timedelta, date

from cryptography.fernet import Fernet
import hashlib
import binascii
import base64
import random
import string
from argon2 import PasswordHasher

import ssl
from email.message import EmailMessage
import smtplib
import traceback

app=Flask(__name__)
app.config['DEBUG']=True

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
    def reset_client_sharing_keys(data):
        session_key=data["session_key"]
        client_email=data["client_email"]
        new_public_key=data["new_public_key"]
        authenticated = authenticate_session_key(session_key)
        if authenticated == True:
            db = connect_to_db()
            curs = db.cursor()
            curs.execute(f"UPDATE Users SET PermanentClientPublicKey='{new_public_key}' WHERE Email='{client_email}'")
            curs.close()
            db.commit()
            db.close()
            return "RESET"

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
        db = connect_to_db()
        curs = db.cursor()
        curs.execute(f"DELETE FROM AsymmetricKeys")
        today = str(date.today())
        curs.execute(f"INSERT INTO AsymmetricKeys(e,d,n,date) VALUES('{ciphertext_public_key_str}','{ciphertext_private_key_str}','{ciphertext_public_n_str}','{today}')")
        curs.close()
        db.commit()
        db.close()
        # with open("/home/BenCrook/mysite/key.txt","w") as file:
        #     file.write(f"{ciphertext_private_key_str}\n{ciphertext_public_key_str}\n{ciphertext_public_n_str}\n{date.today()}")

    @staticmethod
    def get_cipher_suite(include_day = False):
        '''
        Master key is a constant
        Uses datetime so that the key changes daily
        Used to store private key and store passwords on database
        Using fernet encryption included with cryptography
        '''
        MASTERKEY = "748358A4B33C47299475E7F573FFEB67C374632AC342BC3537"
        if include_day:
            current_date = str(date.today())
            combined_string = (MASTERKEY + current_date).encode()
        else:
            combined_string = MASTERKEY.encode()
        hashed_key = hashlib.sha256(combined_string).digest()
        fernet_key = base64.urlsafe_b64encode(hashed_key)
        cipher_suite = Fernet(fernet_key)
        return cipher_suite


    ### get functions for private/public keys for asymmetric encryption

    @staticmethod
    def get_server_key(key = 1):  #1 for public, 0 for private -(corresponds to index)
        # with open("/home/BenCrook/mysite/key.txt","r") as file:
        #     data = file.read()
        try:
            db = connect_to_db()
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
            return encryptor.encryptdecrypt(data, str(symmetric_key))
        else:
            return data #doesn't encrypt if not a string (as can't encrypt int and boolean function etc)

    @staticmethod
    def generate_symmetric_key():
        encryptor = xor.XorEncryption()
        return encryptor.generate_key(24)

    @staticmethod
    def encrypt_key_to_client(data, client_public_key):
        e, n = client_public_key
        encrypted_key = rsa.AsyncRSA.encrypt_symmetric_key(data, e, n)
        return encrypted_key

    @staticmethod
    def encrypt_data_to_client(data, symmetric_key):
        encryptor = xor.XorEncryption()
        encrypted_data = Encryption.encryptdecrypt_directory(data, symmetric_key, encryptor)
        return encrypted_data

    @staticmethod
    def decrypt_key_from_client(data):
        d, n = Encryption.get_server_key(0)
        #print(f"Encrypted key: {data}")
        decrypted_key = rsa.AsyncRSA.decrypt_symmetric_key(data, d, n)
        return decrypted_key

    @staticmethod
    def decrypt_data_from_client(data, symmetric_key):
        encryptor = xor.XorEncryption()
        decrypted_data = Encryption.encryptdecrypt_directory(data, symmetric_key, encryptor)
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



def connect_to_db():
    try:
        db = MySQLdb.connect('BenCrook.mysql.eu.pythonanywhere-services.com',
                              'BenCrook', 'abE3kDD93ijkds9Ke', 'BenCrook$PI_manager')
        return db
    except Exception as e:
        write_errors(traceback.format_exc(),"Connecting")
        return "FAILED TO CONNECT"

def write_errors(error_code="None",function_name="None"):
    with open("/home/BenCrook/mysite/error.txt", "a") as file:
        file.write(f"\n\nFunction attempt: {function_name}\nError code: {str(error_code)}\nTime: {datetime.now().replace(second=0, microsecond=0)}")

def send_email(subject, content, recipient_address):
    try:
        email_sender = "securenetNEA@gmail.com"
        email_password = "anlq nmyl ubtu xlxm"
        email_receiver = recipient_address
        subject = subject
        #created in my strypo email editor
        email_template = f"""
        <html>
            <head>
                <style>
                    body {{
                        font-family: 'Arial', sans-serif;
                        background-color: #f4f4f4;
                        padding: 20px;
                        text-align: center;
                    }}
                    h2 {{
                        color: #3498db;
                    }}
                    p {{
                        font-size: 35px;
                        color: #555;
                    }}
                </style>
            </head>
            <body>
                <h2>{subject}</h2>
                <p>{content}</p>
            </body>
        </html>
        """
        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['Subject'] = subject
        em.add_alternative(email_template, subtype='html')

        # to improve security using ssl
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
            smtp.login(email_sender, email_password)
            return smtp.sendmail(email_sender, email_receiver, em.as_string())
    except Exception as e:
        write_errors(traceback.format_exc(),"Sending email")
        return ["FAILED",traceback.format_exc()]

def increase_login_attempts(client_email):
    try:
        db = connect_to_db()
        curs = db.cursor()
        curs.execute(f"SELECT UserID FROM Users WHERE Email='{client_email}'")
        temp_UserID = curs.fetchone()[0]
        curs.execute(f"SELECT LoginAttempts FROM Users WHERE UserID='{temp_UserID}'")
        temp_login_attempts = curs.fetchone()[0]
        curs.execute(f"SELECT FailedAttemptDate FROM Users WHERE UserID='{temp_UserID}'")
        temp_failed_attempt_date = curs.fetchone()[0]
        temp_failed_attempt_date = datetime.strptime(temp_failed_attempt_date, "%Y-%m-%d %H:%M:%S.%f")
        if temp_failed_attempt_date > datetime.now()-timedelta(hours=1): #failed attempt within last hour
            write_errors("INCREASING LOGIN ATTEMPTS","Increasing login attempts")
            temp_login_attempts += 1
            curs.execute(f"UPDATE Users SET LoginAttempts='{temp_login_attempts}' WHERE UserID='{temp_UserID}'")
            curs.execute(f"UPDATE Users SET FailedAttemptDate='{datetime.now()}' WHERE UserID='{temp_UserID}'")
            curs.close()
            db.commit()
            db.close()
        else:
            write_errors("RESETTING LOGIN ATTEMPTS","Increasing login attempts")
            curs.execute(f"UPDATE Users SET LoginAttempts=1 WHERE UserID='{temp_UserID}'")
            curs.execute(f"UPDATE Users SET FailedAttemptDate='{datetime.now()}' WHERE UserID='{temp_UserID}'")
            curs.close()
            db.commit()
            db.close()
    except Exception as e:
        write_errors(traceback.format_exc(),"Increasing login attempts")
        return ["FAILED",traceback.format_exc()]


def create_new_user(data):
    forename=data["forename"]
    names=data["names"]
    client_email=data["client_email"]
    password_hash=data["password_hash"]
    date_of_birth=data["date_of_birth"]
    phone_number=data["phone_number"]
    country=data["country"]
    permanent_public_key=data["permanent_public_key"]
    mac_address_hash=data["mac_address_hash"]
    try:
        db = connect_to_db()
        curs = db.cursor()
        curs.execute(f"SELECT Email FROM Users")
        emails = curs.fetchall()
        for email in emails:
            if client_email == email[0]:
                return "EMAIL ALREADY USED"
        query = "INSERT INTO Users(Forename, Names, Email, PasswordHash, DateOfBirth, PhoneNumber, Country, OpenDate, PermanentClientPublicKey) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (forename, names, client_email, password_hash, date_of_birth, phone_number, country, date.today(), permanent_public_key)
        curs.execute(query, values)
        curs.execute(f"SELECT UserID FROM Users WHERE Email='{client_email}'")
        temp_UserID = curs.fetchone()[0]
        new_device_code = ''.join(str(random.randint(0, 9)) for _ in range(6))
        curs.execute(f"UPDATE Users SET NewDeviceCode='{new_device_code}' WHERE UserID='{temp_UserID}'")
        curs.close()
        db.commit()
        db.close()
        send_email("SecureNet: Authenticated Account", new_device_code, client_email)
        return "CODE SENT"
    except Exception as e:
        write_errors(traceback.format_exc(),"Creating new user")
        return ["FAILED",traceback.format_exc()]

def confirm_new_user(data):
    client_email=data["client_email"]
    mac_address_hash=data["mac_address_hash"]
    code=data["code"]
    try:
        db = connect_to_db()
        curs = db.cursor()
        curs.execute(f"SELECT NewDeviceCode FROM Users WHERE Email='{client_email}'")
        server_code = curs.fetchone()[0]
        curs.close()
        db.close()
        if str(server_code) == str(code) and len(str(server_code))>0:
            # add new device to database
            db = connect_to_db()
            curs = db.cursor()
            curs.execute(f"SELECT UserID FROM Users WHERE Email='{client_email}'")
            temp_UserID = curs.fetchone()[0]
            curs.execute(f"INSERT INTO Devices(MacAddressHash, LoginDate, UserID) VALUES('{mac_address_hash}','{date.today()}','{temp_UserID}')")
            curs.execute(f"UPDATE Users SET NewDeviceCode=NULL WHERE UserID='{temp_UserID}'")
            curs.close()
            db.commit()
            db.close()
            send_email("SecureNet: Welcome to SecureNet", "Your account has been authenticated", client_email)
            return "ADDED USER"
        else:
            #incorrect code therefore no email validation therefore user account immediately deleted
            curs.execute(f"SELECT UserID FROM Users WHERE Email='{client_email}'")
            temp_UserID = curs.fetchone()[0]
            curs.execute(f"DELETE FROM Users WHERE UserID='{temp_UserID}'")
            curs.close()
            db.commit()
            db.close()
    except Exception as e:
        write_errors(traceback.format_exc(),"Confirming new user")
        return ["FAILED",traceback.format_exc()]


def create_new_device(data):
    client_email=data["client_email"]
    mac_address_hash=data["mac_address_hash"]
    password=data["password"]
    try:
        db = connect_to_db()
        curs = db.cursor()
        curs.execute(f"SELECT UserID FROM Users WHERE Email='{client_email}'")
        temp_UserID = curs.fetchone()[0]
        curs.execute(f"SELECT PasswordHash FROM Users WHERE UserID='{temp_UserID}'")
        db_password_hash = curs.fetchone()[0]
        curs.execute(f"SELECT DeviceID FROM Devices WHERE UserID='{temp_UserID}' AND MacAddressHash='{mac_address_hash}'")
        temp_deviceID = curs.fetchall()
        if len(temp_deviceID)>0:
            curs.close()
            db.close()
            return "DEVICE ALREADY EXISTS"
        else:
            hasher = PasswordHasher()
            if hasher.verify(db_password_hash, password.encode('utf-8')):
                new_device_code = ''.join(str(random.randint(0, 9)) for _ in range(6))
                curs.execute(f"UPDATE Users SET NewDeviceCode='{new_device_code}' WHERE UserID='{temp_UserID}'")
                curs.close()
                db.commit()
                db.close()
                send_email("SecureNet: Authenticated New Device", new_device_code, client_email)
                return "CODE SENT"
            else:
                increase_login_attempts(client_email)
                return "UNAUTHENTICATED"
    except Exception as e:
        write_errors(traceback.format_exc(),"Creating new device")
        return "UNAUTHENTICATED"


def confirm_device_code(data):
    client_email=data["client_email"]
    mac_address_hash=data["mac_address_hash"]
    code=data["code"]
    try:
        db = connect_to_db()
        curs = db.cursor()
        curs.execute(f"SELECT NewDeviceCode FROM Users WHERE Email='{client_email}'")
        server_code = curs.fetchone()[0]
        curs.close()
        db.close()
        if str(server_code) == str(code) and len(str(server_code))>0:
            # add new device to database
            db = connect_to_db()
            curs = db.cursor()
            curs.execute(f"SELECT UserID FROM Users WHERE Email='{client_email}'")
            temp_UserID = curs.fetchone()[0]
            curs.execute(f"INSERT INTO Devices(MacAddressHash, LoginDate, UserID) VALUES('{mac_address_hash}','{date.today()}','{temp_UserID}')")
            curs.execute(f"UPDATE Users SET NewDeviceCode=NULL WHERE UserID={temp_UserID}")
            curs.close()
            db.commit()
            db.close()
            send_email("SecureNet: Authenticated Device", "Your device has been authenticated", client_email)
            send_email("SecureNet: New Device", "A new device has been added to your account.\nIf this wasn't you, login to secure your account", client_email)
            return "ADDED DEVICE"
        else:
            send_email("SecureNet: Attempted Device Authentication", "An attempt was made to authenticate a new device.\nIf this wasn't you, login to secure your account", client_email)
            return "INCORRECT CODE"
    except Exception as e:
        write_errors(traceback.format_exc(),"Confirming device code")
        return ["FAILED",traceback.format_exc()]


def authenticate_password(data):
    #checks the user password when logging in to a device used before
    client_email=data["client_email"]
    mac_address_hash=data["mac_address_hash"]
    password=data["password"]
    try:
        db = connect_to_db()
        curs = db.cursor()
        query = "SELECT UserID FROM Users WHERE Email = %s"
        curs.execute(query, (client_email,))
        temp_UserID = curs.fetchone()[0]
        curs.execute(f"SELECT PasswordHash FROM Users WHERE UserID='{temp_UserID}'")
        db_password_hash = curs.fetchone()[0]
        curs.execute(f"SELECT LoginAttempts FROM Users WHERE UserID='{temp_UserID}'")
        temp_login_attempts = curs.fetchone()[0]
        curs.execute(f"SELECT FailedAttemptDate FROM Users WHERE UserID='{temp_UserID}'")
        temp_failed_attempt_date = curs.fetchone()[0]
        temp_failed_attempt_date = datetime.strptime(temp_failed_attempt_date, "%Y-%m-%d %H:%M:%S.%f")
        if temp_failed_attempt_date > datetime.now()-timedelta(hours=1): #failed attempt within last hour
            if temp_login_attempts >= 3: #failed third attempt within last hour, regardless of device
                write_errors("TOO MANY ATTEMPTS","Full authentication")
                curs.close()
                db.close()
                return "TOO MANY ATTEMPTS"
        try:
            curs.execute(f"SELECT DeviceID FROM Devices WHERE UserID='{temp_UserID}' and MacAddressHash='{mac_address_hash}'")
            temp_DeviceID = curs.fetchone()[0] #will cause Exception if no device
            curs.close()
            db.close()
            hasher = PasswordHasher()
            try:
                hasher.verify(password, db_password_hash.encode('utf-8')) #causes error if no match
                return new_session_key(temp_DeviceID)
            except Exception as e:  #catch error and increase login attempts due to incorrect password
                send_email("SecureNet: Attempted Login", "An attempt was made to login to your account.\nIf this wasn't you, login to secure your account", client_email)
                increase_login_attempts(client_email)
                return "UNAUTHENTICATED"
        except Exception as e:
            curs.close()
            db.close()
            return "UNAUTHENTICATED"

    except Exception as e:
        write_errors(traceback.format_exc(),"Full authentication")
        return "UNAUTHENTICATED"



def authenticate_session_key(client_session_key):
    try:
        db = connect_to_db()
        curs = db.cursor()
        curs.execute(f"SELECT SessionKey, CreationDate FROM Sessions")
        keys_dates = curs.fetchall()
        curs.close()
        db.close()
        for key_date in keys_dates:
            key, date = key_date
            if str(key) == str(client_session_key):
                # confirms session key hasn't expired an hour
                # creates a datetime object from the date in string format from db
                # adds 1 hour to this time using timedelta
                # compares to the current datetime
                date_time_format = '%Y-%m-%d %H:%M:%S.%f'
                current_datetime = datetime.now()
                db_datetime = datetime.strptime(date, date_time_format)
                db_datetime_plus = db_datetime + timedelta(hours=1)
                if db_datetime_plus > current_datetime:
                    return True
                else:
                    return "KEY EXPIRED"
        return "NO KEY"
    except Exception as e:
        write_errors(traceback.format_exc(),"Session Key auth")
        return "UNAUTHENTICATED"

def new_session_key(temp_deviceID):
    ###create session key###
    letters = string.ascii_lowercase
    session_key = ''.join(random.choice(letters) for i in range(64))
    db=connect_to_db()
    curs=db.cursor()
    date_time = datetime.now()
    curs.execute(f"DELETE FROM Sessions WHERE DeviceID='{temp_deviceID}'")
    curs.execute(f"INSERT INTO Sessions(DeviceID, SessionKey, CreationDate) values('{temp_deviceID}','{session_key}','{date_time}')")
    curs.close()
    db.commit()
    db.close()
    return session_key

def get_password_overview(data):
    session_key=data["session_key"]
    client_email=data["client_email"]
    authenticated = authenticate_session_key(session_key)
    if authenticated == True:
        try:
            db = connect_to_db()
            curs = db.cursor()
            curs.execute(f"SELECT UserID FROM Users WHERE Email='{client_email}'")
            temp_UserID = curs.fetchone()[0]
            curs.execute(f"""
                SELECT URL, Title, Username, Passwords.PassID, Manager
                FROM Passwords
                JOIN PasswordKeys ON PasswordKeys.PassID = Passwords.PassID
                WHERE PasswordKeys.UserID = '{temp_UserID}' AND Lockdown = 0
            """) # only gets passwords not in lockdown
            temp_passwords = curs.fetchall()
            passwords = []
            curs.close()
            db.close()
            for db_password in temp_passwords:
                URL, Title, Username, PassID, Manager = db_password
                passwords.append([URL, Title, Username, PassID, Manager])
            return passwords
        except Exception as e:
            write_errors(traceback.format_exc(),"Getting password overview")
            return ["FAILED",traceback.format_exc()]
    else:
        return authenticated

def get_username(data):
    session_key=data["session_key"]
    client_email=data["client_email"]
    temp_PassID=data["passID"]
    authenticated = authenticate_session_key(session_key)
    if authenticated == True:
        try:
            db = connect_to_db()
            curs = db.cursor()
            curs.execute(f"SELECT Username FROM Passwords WHERE PassID='{temp_PassID}'")
            temp_username = curs.fetchone()[0]
            curs.close()
            db.close()
            return temp_username
        except Exception as e:
            write_errors(traceback.format_exc(),"Getting username")
            return ["FAILED",traceback.format_exc()]

def get_password(data):
    session_key=data["session_key"]
    client_email=data["client_email"]
    temp_PassID=data["passID"]
    authenticated = authenticate_session_key(session_key)
    if authenticated == True:
        try:
            db = connect_to_db()
            curs = db.cursor()
            curs.execute(f"SELECT UserID FROM Users WHERE Email='{client_email}'")
            temp_UserID = curs.fetchone()[0]
            curs.execute(f"SELECT Lockdown FROM Passwords WHERE PassID='{temp_PassID}'")
            temp_Lockdown = curs.fetchone()[0]
            if temp_Lockdown == 1:
                curs.close()
                db.close()
                return "LOCKDOWN"
            curs.execute(f"""
                SELECT URL, Title, Username, Passwords.PassID, Manager
                FROM Passwords
                JOIN PasswordKeys ON PasswordKeys.PassID = Passwords.PassID
                WHERE PasswordKeys.UserID = '{temp_UserID}' AND Lockdown = 0
            """)
            password, additional_info, password_key, manager = curs.fetchone()
            curs.close()
            db.close()
            return [password, additional_info, password_key, manager]
        except Exception as e:
            write_errors(traceback.format_exc(), "Getting 1 password")
            return ["FAILED",traceback.format_exc()]
    else:
        return authenticated

def reset_client_password(data):
    session_key = data["session_key"]
    client_email=data["client_email"]
    new_password_hash=data["new_password_hash"]
    raw_password=data["raw_password"]
    new_password_keys=data["new_password_keys"] #dictionary containing password keys with key as passID
    authenticated = authenticate_session_key(session_key)
    if authenticated == True:
        try:
            db = connect_to_db()
            curs = db.cursor()
            #verify user knows their raw password
            curs.execute(f"SELECT PasswordHash FROM Users WHERE Email='{client_email}'")
            original_password_hash = curs.fetchone()[0]
            try:
                hasher = PasswordHasher()
                original_password_hash = "$argon2id$v=19$m=65536,t=2,p=4" + original_password_hash
                if hasher.verify(original_password_hash.encode('utf-8'), raw_password.encode('utf-8')):
                    curs.execute(f"UPDATE Users SET PasswordHash='{new_password_hash}' WHERE Email='{client_email}'")
                    curs.execute(f"SELECT UserID FROM Users WHERE Email='{client_email}'")
                    temp_UserID = curs.fetchone()[0]
                    for passID, password_key in new_password_keys.items():
                        curs.execute(f"UPDATE PasswordKeys SET PasswordKey='{password_key}' WHERE PassID='{passID}' AND UserID='{temp_UserID}'")
                    curs.close()
                    db.commit()
                    db.close()
                    send_email("SecureNet: Password Reset", "Your password has been reset", client_email)
                    return "RESET PASSWORD"
            except Exception as e:
                write_errors(traceback.format_exc(),"Resetting client password - failed to match original password")
                send_email("SecureNet: Attempted Password Reset", "An attempt was made to reset your password.\nIf this wasn't you, login to secure your account", client_email)
                return "UNAUTHENTICATED"
        except Exception as e:
            write_errors(traceback.format_exc(),"Resetting client password")
            return ["FAILED",traceback.format_exc()]
    else:
        return authenticated

def get_all_passwords(data):
    session_key=data["session_key"]
    client_email=data["client_email"]
    authenticated = authenticate_session_key(session_key)
    if authenticated == True:
        try:
            db = connect_to_db()
            curs = db.cursor()
            curs.execute(f"SELECT UserID FROM Users WHERE Email='{client_email}'")
            temp_UserID = curs.fetchone()[0]
            curs.execute(f"""
                SELECT Password, AdditionalInfo, PasswordKey, Manager
                FROM Passwords
                JOIN PasswordKeys ON Passwords.PassID = PasswordKeys.PassID
                WHERE Passwords.PassID = '{temp_PassID}' AND PasswordKeys.UserID = '{temp_UserID}'
            """)
            all_PassID = curs.fetchall()
            pass_info = []
            for ID in all_PassID:
                temp_PassID = ID[0]
                curs.execute(f"SELECT Passwords.PassID, Password, PasswordKey, AdditionalInfo, URL, Title, Username, Lockdown FROM Passwords, PasswordKeys WHERE Passwords.PassID='{temp_PassID}' AND PasswordKeys.PassID='{temp_PassID}' AND PasswordKeys.UserID='{temp_UserID}'")
                temp_PassID, password, password_key, additional_info, url, title, username, lockdown = curs.fetchone()
                pass_info.append([temp_PassID,password,password_key,additional_info,url,title,username,lockdown])
            return pass_info
        except Exception as e:
            write_errors(traceback.format_exc(),"Get all passwords")
            return ["FAILED",traceback.format_exc()]
    else:
        return authenticated

def set_to_lockdown(data):
    """
    Sets a password to lockdown mode.

    Parameters:
    - data (dict): A dictionary containing the following keys:
        - session_key (str): The session key for authentication.
        - client_email (str): The email of the client.
        - passID (str): The ID of the password to set to lockdown mode.

    Returns:
    - str: "SET TO LOCKDOWN" if the password was successfully set to lockdown mode.
    - list: ["FAILED", traceback] if an error occurred during the process.
    - bool: False if the session key is not authenticated.
    """
    session_key=data["session_key"]
    client_email=data["client_email"]
    temp_PassID=data["passID"]
    authenticated = authenticate_session_key(session_key)
    if authenticated == True:
        try:
            db = connect_to_db()
            curs = db.cursor()
            curs.execute(f"SELECT UserID FROM Users WHERE Email='{client_email}'")
            temp_UserID = curs.fetchone()[0]
            #check user has password
            curs.execute(f"SELECT PassID FROM PasswordKeys WHERE UserID='{temp_UserID}'")
            all_PassID = curs.fetchall()
            if (temp_PassID,) not in all_PassID:
                return "NO PASSWORD"
            curs.execute(f"UPDATE Passwords SET Lockdown=1 WHERE PassID='{temp_PassID}'")
            curs.close()
            db.commit()
            db.close()
            send_email("SecureNet: Set to Lockdown", "The lockdown status on a password has been set", client_email)
            return "SET TO LOCKDOWN"
        except Exception as e:
            write_errors(traceback.format_exc(),"Setting to lockdown")
            return ["FAILED",traceback.format_exc()]
    else:
        return authenticated

def remove_lockdown(data):
    """
    Removes the lockdown status of a password or all passwords associated with a user.

    Args:
        data (dict): A dictionary containing the following keys:
            - session_key (str): The session key for authentication.
            - client_email (str): The email of the client.
            - passID (str): The ID of the password to remove lockdown from. Use "all" to remove lockdown from all passwords.

    Returns:
        str: If the lockdown is successfully removed, returns "REMOVED LOCKDOWN".
        list: If an error occurs, returns ["FAILED", traceback].

    """
    session_key=data["session_key"]
    client_email=data["client_email"]
    temp_PassID=data["passID"]
    authenticated = authenticate_session_key(session_key)
    if authenticated == True:
        try:
            db = connect_to_db()
            curs = db.cursor()
            curs.execute(f"SELECT UserID FROM Users WHERE Email='{client_email}'")
            temp_UserID = curs.fetchone()[0]
            if temp_PassID == "all":
                curs.execute("""UPDATE Passwords 
                    JOIN PasswordKeys ON Passwords.PassID = PasswordKeys.PassID 
                    SET Lockdown=0 WHERE PasswordKeys.UserID='{temp_UserID}' 
                    AND PasswordKeys.Manager = 1
                """)
            else:
                curs.execute(f"""UPDATE Passwords 
                    JOIN PasswordKeys ON Passwords.PassID = PasswordKeys.PassID 
                    SET Lockdown=0 
                    WHERE PasswordKeys.UserID='{temp_UserID}' AND Passwords.PassID='{temp_PassID}'
                """)
                #get users of passwords
                curs.execute(f"SELECT Email FROM Users JOIN PasswordKeys ON Users.UserID = PasswordKeys.UserID WHERE PasswordKeys.PassID='{temp_PassID}'")
                all_emails = curs.fetchall()
                for email in all_emails:
                    send_email("SecureNet: Removed Lockdown", "The lockdown status on a password has been removed", email)
            curs.close()
            db.commit()
            db.close()
            return "REMOVED LOCKDOWN"
        except Exception as e:
            write_errors(traceback.format_exc(),"Removing lockdown")
            return ["FAILED",traceback.format_exc()]


def add_new_password(data):
    session_key=data["session_key"]
    client_email=data["client_email"]
    password=data["password"],
    title=data["title"]
    url=data["url"]
    username=data["username"]
    additional_info=data["additional_info"]
    password_key=data["password_key"]
    authenticated = authenticate_session_key(session_key)
    if authenticated == True:
        try:
            db = connect_to_db()
            curs = db.cursor()
            curs.execute(f"SELECT UserID FROM Users WHERE Email='{client_email}'")
            temp_UserID = curs.fetchone()[0]
            curs.execute(f"SELECT URL, Title, Username FROM Passwords, PasswordKeys WHERE Passwords.PassID=PasswordKeys.PassID AND PasswordKeys.UserID='{temp_UserID}'")
            all_info = curs.fetchall()
            for info_group in all_info:
                db_url, db_title, db_username = info_group
                if db_url == url and db_title == title and db_username == username:
                    curs.close()
                    db.close()
                    return "PASSWORD ALREADY EXISTS"
            query = "INSERT INTO Passwords(Password, URL, Title, Username, AdditionalInfo) VALUES (%s, %s, %s, %s, %s)"  #avoid sql injection
            values = (password, url, title, username, additional_info)
            curs.execute(query, values)
            temp_PassID = curs.lastrowid
            curs.execute(f"INSERT INTO PasswordKeys(PassID, UserID, PasswordKey, Manager) VALUES ('{temp_PassID}','{temp_UserID}','{password_key}',1)")
            curs.close()
            db.commit()
            db.close()
            return "ADDED PASSWORD"
        except Exception as e:
            write_errors(traceback.format_exc(),"Adding new password")
            return ["FAILED",traceback.format_exc()]
    else:
        return authenticated

# deletes a password from all existance
def delete_password(data):
    session_key=data["session_key"]
    client_email=data["client_email"]
    temp_PassID=data["passID"]
    authenticated = authenticate_session_key(session_key)
    if authenticated == True:
        try:
            temp_UserID, manager = get_manager_password_info(client_email,temp_PassID)
            if manager == 0:
                return "NOT MANAGER"
            db = connect_to_db()
            curs = db.cursor()
            # deletes password and all instances of password keys
            curs.execute(f"DELETE FROM PasswordKeys WHERE PassID='{temp_PassID}'")
            curs.execute(f"SELECT Title FROM Passwords WHERE PassID='{temp_PassID}'")
            title = curs.fetchone()[0]
            curs.execute(f"DELETE FROM Passwords WHERE PassID='{temp_PassID}'")
            curs.close()
            db.commit()
            db.close()
            send_email("SecureNet: Deleted Password", f"Your password for {title} has been deleted.\n\nIf this wasn't you, login to secure your account.", client_email)
            return "DELETED PASSWORD"
        except Exception as e:
            write_errors(traceback.format_exc(),"Deleting password")
            return ["FAILED",traceback.format_exc()]
    else:
        return authenticated

def add_manager(data):
    session_key=data["session_key"]
    client_email=data["client_email"]
    new_manager_email=data["new_manager_email"]
    temp_PassID=data["passID"]
    authenticated = authenticate_session_key(session_key)
    if authenticated == True:
        try:
            temp_UserID, manager = get_manager_password_info(client_email,temp_PassID)
            if manager == 0:
                return "NOT MANAGER"
            db = connect_to_db()
            curs = db.cursor()
            query = "SELECT UserID FROM Users WHERE Email = %s"
            curs.execute(query, (new_manager_email,))
            try:
                manager_UserID = curs.fetchone()[0]
            except Exception as e:
                curs.close()
                db.close()
                return f"NO USER WITH EMAIL {new_manager_email}"
            try:
                curs.execute(f"UPDATE PasswordKeys SET Manager=1 WHERE UserID='{manager_UserID}' AND PassID='{temp_PassID}'")
                curs.execute(f"SELECT Title FROM Passwords WHERE PassID='{temp_PassID}'")
                title = curs.fetchone()[0]
                send_email("SecureNet: Added as Manager", f"You have ben added as a manager to a shared {title} password", new_manager_email)
                # will fail if given user is not already a password user
            except Exception as e:
                curs.close()
                db.close()
                return "NEW MANAGER NOT PASSWORD USER"
            curs.close()
            db.commit()
            db.close()
            return "ADDED MANAGER"
        except Exception as e:
            write_errors(traceback.format_exc(),"Adding manager")
            return ["FAILED",traceback.format_exc()]
    else:
        return authenticated

# gets UserID, PassID and whether the User is a manager based off client email and URL
# needed for base data since many functions require same initial queries
def get_manager_password_info(client_email, temp_PassID):
    try:
        db = connect_to_db()
        curs = db.cursor()
        curs.execute(f"SELECT UserID FROM Users WHERE Email='{client_email}'")
        temp_UserID = curs.fetchone()[0]
        curs.execute(f"SELECT Manager FROM PasswordKeys WHERE PassID='{temp_PassID}' AND UserID='{temp_UserID}'")
        manager = curs.fetchone()[0]
        curs.close()
        db.close()
        return [temp_UserID,manager]
    except Exception as e:
        write_errors(traceback.format_exc(),"Getting manager password info")
        return ["FAILED",traceback.format_exc()] #this won't get read anyway, but worth writing error to file

#only used by managers
def remove_password_user(data):
    session_key = data["session_key"]
    client_email = data["client_email"]
    temp_PassID = data["passID"]
    user_email = data["user_email"]
    authenticated = authenticate_session_key(session_key)
    if authenticated == True:
        try:
            temp_userID, manager = get_manager_password_info(client_email,temp_PassID)
            if manager == 0:
                return "NOT MANAGER"
            if client_email == user_email:
                return "CANNOT REMOVE SELF"
            other_userID, other_manager = get_manager_password_info(user_email,temp_PassID)
            if other_manager == 1:
                return "CANNOT REMOVE MANAGER"
            db = connect_to_db()
            curs = db.cursor()
            curs.execute(f"DELETE FROM PasswordKeys WHERE UserID='{other_userID}' AND PassID='{temp_PassID}'")
            curs.close()
            db.commit()
            db.close()
            send_email("SecureNet: Removed from Password", f"Your access to a shared password has been revoked.", user_email)
            send_email("SecureNet: Removed User", f"You have revoked access to a shared password for {user_email}.\nIf this wasn't you, login to secure your account.", client_email)
            return "REMOVED USER"
        except Exception as e:
            write_errors(traceback.format_exc(),"Removing password user")
            return ["FAILED",traceback.format_exc()]
    else:
        return authenticated
    

# only used by managers
def get_password_users(data):
    session_key=data["session_key"]
    client_email=data["client_email"]
    temp_PassID=data["passID"]
    try:
        manager_only=data["manager_only"]
    except Exception as e:
        manager_only=False

    authenticated = authenticate_session_key(session_key)
    if authenticated == True:
        try:
            temp_UserID, manager = get_manager_password_info(client_email,temp_PassID)
            if manager == 0:
                return "NOT MANAGER"
            db = connect_to_db()
            curs = db.cursor()
            if manager_only:  # only returns the users who are managers
                curs.execute(f"SELECT Email, Forename, Names FROM Users, PasswordKeys WHERE Users.UserID=PasswordKeys.UserID AND PasswordKeys.PassID='{temp_PassID}' AND Manager=1")
            else:  # returns all users
                curs.execute(f"SELECT Email, Forename, Names FROM Users, PasswordKeys WHERE Users.UserID=PasswordKeys.UserID AND PasswordKeys.PassID='{temp_PassID}'")
            all_users = curs.fetchall()
            user_info = []
            for info in all_users:
                email, forename, names = info
                user_info.append([email, forename, names])
            curs.close()
            db.close()
            return user_info
        except Exception as e:
            write_errors(traceback.format_exc(),"Getting password users")
            return ["FAILED",traceback.format_exc()]
    else:
        return authenticated

def delete_password_instance(data):
    session_key=data["session_key"]
    client_email=data["client_email"] 
    temp_PassID=data["passID"]
    new_manager_email=data["new_manager_email"]
    authenticated = authenticate_session_key(session_key)
    if authenticated == True:
        # check if user is only manager
        # doesn't matter if user is not a manager
        # or if there is more than one manager
        data["manager_only"]=True
        num_managers = get_password_users(data)
        if num_managers == "NOT MANAGER" or len(num_managers)>1:
            try:
                temp_UserID, manager = get_manager_password_info(client_email,temp_PassID)
                db = connect_to_db()
                curs = db.cursor()
                curs.execute(f"DELETE FROM PasswordKeys WHERE UserID='{temp_UserID}' AND PassID='{temp_PassID}'")
                curs.close()
                db.commit()
                db.close()
                send_email("SecureNet: Deleted Password Instance", f"One of your passwords has been deleted.\n\nIf this wasn't you, login to secure your account.", client_email)
                return "DELETED PASSWORD INSTANCE"
            except Exception as e:
                write_errors(traceback.format_exc(),"Deleting password instance")
                return ["FAILED",traceback.format_exc()]
        else:
            try:
                users = get_password_users(session_key=session_key, client_email=client_email, temp_PassID=temp_PassID, manager_only=False)
                is_user = False
                for user in users:
                    if user[0] == new_manager_email:
                        is_user = True
                if is_user == False:
                    return "NEED TO SHARE"
                else:
                    data = add_manager(session_key=session_key,client_email=client_email,new_manager_email=new_manager_email,temp_PassID=temp_PassID)
                    if data == "ADDED MANAGER":
                        db = connect_to_db()
                        curs = db.cursor()
                        temp_UserID, manager = get_manager_password_info(client_email,temp_PassID)
                        curs.execute(f"DELETE FROM PasswordKeys WHERE UserID='{temp_UserID}' AND PassID='{temp_PassID}'")
                        curs.close()
                        db.commit()
                        db.close()
                        send_email("SecureNet: Deleted Password Instance", f"One of your passwords has been deleted and a new manager has been added.\n\nIf this wasn't you, login to secure your account.", client_email)
                        return f"DELETED PASSWORD INSTANCE and ADDED MANAGER {new_manager_email}"
                    else:
                        return data
            except Exception as e:
                write_errors(traceback.format_exc(),"Deleting password instance and adding manager")
                return ["FAILED",traceback.format_exc()]
    else:
        return authenticated

def update_password(data):
    session_key=data["session_key"]
    client_email=data["client_email"]
    temp_PassID=data["passID"]
    new_info=data["new_info"]
    type=data["type"]       #type = "Password","URL","Title","Username","AdditionalInfo"
    authenticated = authenticate_session_key(session_key)
    if authenticated == True:
        try:
            temp_UserID, manager = get_manager_password_info(client_email,temp_PassID)
            if manager == 0:
                return "NOT MANAGER"
            db = connect_to_db()
            curs = db.cursor()
            query = f"UPDATE Passwords SET {type} = %s WHERE PassID = %s"
            curs.execute(query, (new_info, temp_PassID))
            curs.close()
            db.commit()
            db.close()
            return "UPDATED PASSWORD"
        except Exception as e:
            write_errors(traceback.format_exc(),"Updating password")
            return ["FAILED",traceback.format_exc()]
    else:
        return authenticated

def get_pending_passwordkeys(data):
    session_key=data["session_key"]
    client_email=data["client_email"]
    authenticated = authenticate_session_key(session_key)
    if authenticated == True:
        try:
            db = connect_to_db()
            curs = db.cursor()
            curs.execute(f"SELECT PendingDownload FROM Users WHERE Email='{client_email}'")
            pending = curs.fetchone()[0]
            if pending == 0:
                curs.close()
                db.close()
                return "NO PENDING PASSWORDS"
            curs.execute(f"SELECT UserID FROM Users WHERE Email='{client_email}'")
            temp_UserID = curs.fetchone()[0]
            curs.execute(f"SELECT PasswordKey, PassID, Manager, SenderUserID, SymmetricKey FROM PendingPasswords WHERE RecipientUserID='{temp_UserID}'")
            shared_info = curs.fetchall()
            info_to_return = []
            for info in shared_info:
                password_key, passID, manager, sender_UserID, symmetric_key = info
                password_key = password_key.decode('utf-8')
                password_key = password_key.replace("\\", r"\\")
                # gets additional information to accompany encrypted password info
                curs.execute(f"SELECT Email, Forename, Names FROM Users WHERE UserID='{sender_UserID}'")
                sharer_info = curs.fetchone()
                sender_email, sender_forename, sender_names = sharer_info
                curs.execute(f"SELECT Title FROM Passwords WHERE PassID='{passID}'")
                title = curs.fetchone()[0]
                info_to_return.append([passID, title, password_key, manager, sender_email, sender_forename, sender_names, symmetric_key])
            # curs.execute(f"UPDATE Users SET PendingDownload=0 WHERE UserID='{temp_UserID}'")
            # curs.execute(f"DELETE FROM PendingPasswords WHERE RecipientUserID='{temp_UserID}'")
            curs.close()
            db.commit()
            db.close()
            return info_to_return
        except Exception as e:
            write_errors(traceback.format_exc(),"Getting pending password keys")
            return ["FAILED",traceback.format_exc()]
    else:
        return authenticated

# gets emails and names for a user when they want to share a password
def get_emails_sharing(data):
    session_key=data["session_key"]
    email=data["email"]
    authenticated = authenticate_session_key(session_key)
    if authenticated == True:
        try:
            db = connect_to_db()
            curs = db.cursor()
            query = "SELECT UserID, Forename, Names, Email FROM Users WHERE Email = %s"
            curs.execute(query, (email,))
            try:
                user_info = curs.fetchone()
                userID, forename, name, user_email = user_info
                return [userID, forename, name, user_email]
            except Exception as e:
                return "NO USER"
        except Exception as e:
            write_errors(traceback.format_exc(),"Getting emails for sharing")
            return ["FAILED",traceback.format_exc()]
    else:
        return authenticated

def get_public_key(data):
    session_key=data["session_key"]
    recipient_UserID=data["recipient_UserID"]
    authenticated = authenticate_session_key(session_key)
    if authenticated == True:
        try:
            db = connect_to_db()
            curs = db.cursor()
            curs.execute(f"SELECT PermanentClientPublicKey FROM Users WHERE UserID='{recipient_UserID}'")
            public_key = curs.fetchone()[0]
            curs.close()
            db.close()
            return public_key
        except Exception as e:
            write_errors(traceback.format_exc(),"Getting public key")
            return ["FAILED",traceback.format_exc()]
    else:
        return authenticated

def share_password(data):
    session_key=data["session_key"]
    client_email=data["client_email"]
    passID=data["passID"]
    password_key=data["password_key"]
    recipient_UserID=data["recipient_UserID"]
    manager=data["manager"]
    encrypted_symmetric_key=data["encrypted_sharing_symmetric_key"]
    authenticated = authenticate_session_key(session_key)
    if authenticated == True:
        try:
            db = connect_to_db()
            curs = db.cursor()
            curs.execute(f"SELECT UserID FROM Users WHERE Email='{client_email}'")
            sender_UserID = curs.fetchone()[0]
            curs.execute(f"SELECT Manager FROM PasswordKeys WHERE UserID='{sender_UserID}' AND PassID='{passID}'")
            is_manager = curs.fetchone()[0]
            if is_manager == 0:
                curs.close()
                db.close()
                return "NOT MANAGER"
            try:
                curs.execute(f"SELECT Manager FROM PasswordKeys WHERE UserID='{recipient_UserID}' AND PassID='{passID}'")
                manager_recipient = curs.fetchone()[0] #will cause error if None returned
                curs.close()
                db.close()
                if manager_recipient == 1:
                    return "PASSWORD ALREADY SHARED MANAGER"
                else:
                    return "PASSWORD ALREADY SHARED NOT MANAGER"
            except Exception as e:
                password_key = password_key.replace(r"\\", "\\")
                password_key = password_key.encode('utf-8')
                query = """
                    INSERT INTO PendingPasswords (
                        PasswordKey, PassID, Manager, SenderUserID, RecipientUserID, SymmetricKey
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s
                    )
                """
                values = (
                    password_key, passID, manager, sender_UserID, recipient_UserID, encrypted_symmetric_key
                )
                curs.execute(query, values)
                curs.execute(f"UPDATE Users SET PendingDownload=1 WHERE UserID='{recipient_UserID}'")
                curs.execute(f"SELECT Email FROM Users WHERE UserID='{recipient_UserID}'")
                recipient_user_email = curs.fetchone()[0]
                send_email("SecureNet: Shared Password", f"{client_email} has shared a password with you.\n\nPlease log in to your account before the end of the month to download.", recipient_user_email)
                send_email("SecureNet: Shared Password", f"You have shared a password with {recipient_user_email}.\n\nNote: The share key will expire at the end of the month.", client_email)
                curs.close()
                db.commit()
                db.close()
                return "SHARED PASSWORD"
        except Exception as e:
            write_errors(traceback.format_exc(),"Sharing password")
            return ["FAILED",traceback.format_exc()]
    else:
        return authenticated


def insert_pending_keys(data):
    session_key=data["session_key"]
    client_email=data["client_email"]
    passID=data["passID"]
    password_key=data["password_key"]
    accept = data["accept"]
    authenticated = authenticate_session_key(session_key)
    if authenticated == True:
        try:
            db = connect_to_db()
            curs = db.cursor()
            curs.execute(f"SELECT UserID FROM Users WHERE Email='{client_email}'")
            temp_UserID = curs.fetchone()[0]
            if accept == "Accept":
                #get manager (can't rely on client input)
                curs.execute(f"SELECT Manager FROM PendingPasswords WHERE RecipientUserID='{temp_UserID}' AND PassID='{passID}'")
                manager = curs.fetchone()[0]
                curs.execute(f"INSERT INTO PasswordKeys(PassID, UserID, PasswordKey, Manager) VALUES ('{passID}','{temp_UserID}','{password_key}','{manager}')")
                curs.execute(f"DELETE FROM PendingPasswords WHERE RecipientUserID='{temp_UserID}' AND PassID='{passID}'")
                curs.close()
                db.commit()
                db.close()
                return "PASSWORD ADDED"
            elif accept == "Reject":
                curs.execute(f"DELETE FROM PendingPasswords WHERE RecipientUserID='{temp_UserID}' AND PassID='{passID}'")
                curs.close()
                db.commit()
                db.close()
                return "PASSWORD DECLINED"
            else:
                curs.close()
                db.commit()
                db.close()
                return "NO ACTION"
        except Exception as e:
            write_errors(traceback.format_exc(),"Inserting pending keys")
            return ["FAILED",traceback.format_exc()]
    else:
        return authenticated


# Need to check each one. Can't run a request based
# on user input as that could call any function.

@app.route('/post_endpoint',methods=['POST'])
def receive_data():
    try:
        json_data = request.get_json()
        encrypted_symmetric_key = json_data["encrypted_symmetric_key"]
        
        ### DECRYPT SYMMETRIC KEY ###
        symmetric_key = Encryption.decrypt_key_from_client(encrypted_symmetric_key)
        ### DECRYPT DATA ###
        encrypted_data = json_data["request_data"]
        data = Encryption.decrypt_data_from_client(encrypted_data, symmetric_key)
        header = json_data["request_header"]
        
        if header == "get_server_key":
            data_to_return = Encryption.get_server_key() #no data do can't error check
            flag = "encryption success"
                
        elif Encryption.validate_error_check(data["error_check"]):
            if header == "reset_client_sharing_key":
                data_to_return = Encryption.reset_client_sharing_keys(data)

            elif header == "authenticate_password":
                data_to_return = authenticate_password(data)

            elif header == "add_new_device":
                data_to_return = create_new_device(data)

            elif header == "confirm_device_code":
                data_to_return = confirm_device_code(data)

            elif header == "add_new_user":
                data_to_return = create_new_user(data)

            elif header == "confirm_new_user":
                data_to_return = confirm_new_user(data)

            elif header == "reset_client_password":
                data_to_return = reset_client_password(data)

            elif header == "get_password_overview":
                data_to_return = get_password_overview(data)

            elif header == "get_username":
                data_to_return = get_username(data)

            elif header == "get_password":
                data_to_return = get_password(data)

            elif header == "get_all_passwords":
                data_to_return = get_all_passwords(data)

            elif header == "set_to_lockdown":
                data_to_return = set_to_lockdown(data)

            elif header == "remove_lockdown":
                data_to_return = remove_lockdown(data)

            elif header == "add_new_password":
                data_to_return = add_new_password(data)

            elif header == "delete_password":
                data_to_return = delete_password(data)

            elif header == "add_manager":
                data_to_return = add_manager(data)

            elif header == "get_password_users":
                data_to_return = get_password_users(data)

            elif header == "remove_password_user":
                data_to_return = remove_password_user(data)

            elif header == "delete_password_instance":
                data_to_return = delete_password_instance(data)

            elif header == "update_password":
                data_to_return = update_password(data)

            elif header == "get_pending_passwordkeys":
                data_to_return = get_pending_passwordkeys(data)

            elif header == "get_emails_sharing":
                data_to_return = get_emails_sharing(data)

            elif header == "share_password":
                data_to_return = share_password(data)

            elif header == "insert_pending_keys":
                data_to_return = insert_pending_keys(data)

            elif header == "get_public_key":  # get public key of client for password sharing
                data_to_return = get_public_key(data)

            elif header == "update_public_keys":
                data_to_return = Encryption.reset_client_sharing_keys(data)




            ### HARD RESET ONLY FOR TESTING
            elif header == "reset":
                try:
                    db = connect_to_db()
                    curs = db.cursor()
                    #print("resetting")
                    curs.execute("DELETE FROM PendingPasswords")
                    curs.execute("DELETE FROM Sessions")
                    curs.execute("DELETE FROM PasswordKeys")
                    curs.execute("DELETE FROM Passwords")
                    curs.execute("DELETE FROM Devices")
                    curs.execute("DELETE FROM Users")
                    curs.close()
                    db.commit()
                    db.close()
                    data_to_return = ""
                except Exception as e:
                    write_errors(traceback.format_exc(),"Resetting")
                    data_to_return = ["FAILED",traceback.format_exc()]
                    
            flag = "encryption success"
            
        else:
            flag = "encryption fail"
            data_to_return = None
            
        
        client_public_key = json_data["client_public_key"]
        symmetric_key = Encryption.generate_symmetric_key()
        dic_to_send = {
            "data": data_to_return,
            "error_check": Encryption.create_error_check(),
        }
        encrypted_data = Encryption.encrypt_data_to_client(dic_to_send, symmetric_key)
        encrypted_symmetric_key = Encryption.encrypt_key_to_client(symmetric_key, client_public_key)
        


        return jsonify({
            "data":encrypted_data,
            "encrypted_symmetric_key":encrypted_symmetric_key,
            "flag":flag,
        })

    except Exception as e:
        write_errors(traceback.format_exc(),"Handle")
        return jsonify({"data":["FAILED AT HANDLE",str(e)]})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc', debug=True)

