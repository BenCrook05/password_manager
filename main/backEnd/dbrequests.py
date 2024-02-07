# Description: contains all the requests to the database
import requests
import json
import traceback
from decouple import config
from backEnd.encryption import Encrypt, Decrypt, Generate
from datetime import datetime



class PyAnyWhereRequests:
    
    @staticmethod
    def get_server_key():
        client_public_key, client_private_key = Generate.generate_asymmetric_keys()
        data_to_return = PyAnyWhereRequests.send_request("get_server_key",client_public_key=client_public_key)
        try:
            formated_data = PyAnyWhereRequests.format_data(data_to_return, client_private_key)
            return formated_data
        except Exception as e:
            return PyAnyWhereRequests.get_server_key()
        
    @staticmethod
    def add_new_user(server_public_key, forename, names, client_email, password_hash, date_of_birth, phone_number, country, permanent_public_key, mac_address_hash):
        client_public_key, client_private_key, symmetric_key, encrypted_symmetric_key = PyAnyWhereRequests.create_encryption_keys(server_public_key)
        data = {
            "forename": forename,
            "names": names,
            "client_email": client_email,
            "password_hash": password_hash,
            "date_of_birth": date_of_birth,
            "phone_number": phone_number,
            "country": country,
            "permanent_public_key": permanent_public_key,
            "mac_address_hash": mac_address_hash,
            "error_check": Generate.create_error_check(),
        }
        encrypted_data = Encrypt.encrypt_data_to_server(data, symmetric_key) #encrypts data using symmetric key
        data_to_return = PyAnyWhereRequests.send_request("add_new_user", encrypted_data, client_public_key = client_public_key, encrypted_symmetric_key = encrypted_symmetric_key) #includes client public key so server can encrypt data using client public key
        try:
            formated_data = PyAnyWhereRequests.format_data(data_to_return, client_private_key)
            return formated_data
        except Exception as e:
            return PyAnyWhereRequests.add_new_user(server_public_key, forename, names, client_email, password_hash, date_of_birth, phone_number, country, permanent_public_key, mac_address_hash)
            
    @staticmethod
    def confirm_new_user(server_public_key, client_email, mac_address_hash, code):
        client_public_key, client_private_key, symmetric_key, encrypted_symmetric_key = PyAnyWhereRequests.create_encryption_keys(server_public_key)
        data = {
            "client_email": client_email,
            "mac_address_hash": mac_address_hash,
            "code": code,
            "error_check": Generate.create_error_check(),
        }
        encrypted_data = Encrypt.encrypt_data_to_server(data, symmetric_key)
        data_to_return = PyAnyWhereRequests.send_request("confirm_new_user", encrypted_data, client_public_key = client_public_key, encrypted_symmetric_key = encrypted_symmetric_key)
        try:
            formated_data = PyAnyWhereRequests.format_data(data_to_return, client_private_key)
            return formated_data
        except Exception as e:
            return PyAnyWhereRequests.confirm_new_user(server_public_key, client_email, mac_address_hash, code)
             
    @staticmethod
    def add_new_device_request(server_public_key, client_email, new_mac_address, password):
        client_public_key, client_private_key, symmetric_key, encrypted_symmetric_key = PyAnyWhereRequests.create_encryption_keys(server_public_key)
        data = {
            "client_email": client_email,
            "mac_address_hash": new_mac_address,
            "password": password,
            "error_check": Generate.create_error_check(),
        }
        encrypted_data = Encrypt.encrypt_data_to_server(data, symmetric_key)
        data_to_return = PyAnyWhereRequests.send_request("add_new_device", encrypted_data, client_public_key = client_public_key, encrypted_symmetric_key = encrypted_symmetric_key)
        try:
            formated_data = PyAnyWhereRequests.format_data(data_to_return, client_private_key)
            return formated_data
        except Exception as e:
            return PyAnyWhereRequests.add_new_device_request(server_public_key, client_email, new_mac_address, password)
            
    @staticmethod
    def confirm_device_code(server_public_key, client_email, mac_address_hash, code):
        client_public_key, client_private_key, symmetric_key, encrypted_symmetric_key = PyAnyWhereRequests.create_encryption_keys(server_public_key)
        data = {
            "client_email": client_email,
            "mac_address_hash": mac_address_hash,
            "code": code,
            "error_check": Generate.create_error_check(),
        }
        encrypted_data = Encrypt.encrypt_data_to_server(data, symmetric_key)
        data_to_return = PyAnyWhereRequests.send_request("confirm_device_code", encrypted_data, client_public_key = client_public_key, encrypted_symmetric_key = encrypted_symmetric_key)
        try:
            formated_data = PyAnyWhereRequests.format_data(data_to_return, client_private_key)
            return formated_data
        except Exception as e:
            return PyAnyWhereRequests.confirm_device_code(server_public_key, client_email, mac_address_hash, code)
               
    @staticmethod
    def authenticate_password(server_public_key, client_email, mac_address_hash, password):
        client_public_key, client_private_key, symmetric_key, encrypted_symmetric_key = PyAnyWhereRequests.create_encryption_keys(server_public_key)
        data = {
            "client_email": client_email,
            "mac_address_hash": mac_address_hash,
            "password": password,
            "error_check": Generate.create_error_check(),
        }
        encrypted_data = Encrypt.encrypt_data_to_server(data, symmetric_key)
        data_to_return = PyAnyWhereRequests.send_request("authenticate_password", encrypted_data, client_public_key=client_public_key, encrypted_symmetric_key=encrypted_symmetric_key)
        try:
            formated_data = PyAnyWhereRequests.format_data(data_to_return, client_private_key)
            return formated_data
        except Exception as e:
            return PyAnyWhereRequests.authenticate_password(server_public_key, client_email, mac_address_hash, password)    
    
    @staticmethod
    def confirm_new_device_password(server_public_key, client_email, mac_address_hash, password_confirmation):
        client_public_key, client_private_key, symmetric_key, encrypted_symmetric_key = PyAnyWhereRequests.create_encryption_keys(server_public_key)
        data = {
            "password_confirmation": password_confirmation,
            "mac_address_hash": mac_address_hash,
            "client_email": client_email,
            "error_check": Generate.create_error_check(),
        }
        encrypted_data = Encrypt.encrypt_data_to_server(data, symmetric_key)
        data_to_return = PyAnyWhereRequests.send_request("confirm_password_add_device", encrypted_data, client_public_key = client_public_key, encrypted_symmetric_key = encrypted_symmetric_key)
        try:
            formated_data = PyAnyWhereRequests.format_data(data_to_return, client_private_key)
            return formated_data
        except Exception as e:
            return PyAnyWhereRequests.confirm_new_device_password(server_public_key, client_email, mac_address_hash, password_confirmation)
            
    @staticmethod
    def reset_client_password(server_public_key, session_key, client_email, new_password_hash, raw_password, new_password_keys):
        client_public_key, client_private_key, symmetric_key, encrypted_symmetric_key = PyAnyWhereRequests.create_encryption_keys(server_public_key)
        data = {
            "session_key": session_key,
            "client_email": client_email,
            "new_password_hash": new_password_hash,
            "raw_password": raw_password,
            "new_password_keys": new_password_keys,
            "error_check": Generate.create_error_check(),
        }
        encrypted_data = Encrypt.encrypt_data_to_server(data, symmetric_key)
        data_to_return = PyAnyWhereRequests.send_request("reset_client_password", encrypted_data, client_public_key = client_public_key, encrypted_symmetric_key = encrypted_symmetric_key)
        try:
            formated_data = PyAnyWhereRequests.format_data(data_to_return, client_private_key)
            return formated_data
        except Exception as e:
            return PyAnyWhereRequests.reset_client_password(server_public_key, session_key, client_email, new_password_hash, raw_password, new_password_keys)
            
            
    @staticmethod
    def get_password_overview(server_public_key, session_key, client_email):
        client_public_key, client_private_key, symmetric_key, encrypted_symmetric_key = PyAnyWhereRequests.create_encryption_keys(server_public_key)
        data = {
            "session_key": session_key,
            "client_email": client_email,
            "error_check": Generate.create_error_check(),
        }
        encrypted_data = Encrypt.encrypt_data_to_server(data, symmetric_key)
        data_to_return = PyAnyWhereRequests.send_request("get_password_overview", encrypted_data, client_public_key = client_public_key, encrypted_symmetric_key = encrypted_symmetric_key)
        try:
            formated_data = PyAnyWhereRequests.format_data(data_to_return, client_private_key)
            return formated_data
        except Exception as e:
            return PyAnyWhereRequests.get_password_overview(server_public_key, session_key, client_email)
            
    @staticmethod
    def get_username(server_public_key, session_key, client_email, passID):
        client_public_key, client_private_key, symmetric_key, encrypted_symmetric_key = PyAnyWhereRequests.create_encryption_keys(server_public_key)
        data = {
            "session_key": session_key,
            "client_email": client_email,
            "passID": passID,
            "error_check": Generate.create_error_check(),
        }
        encrypted_data = Encrypt.encrypt_data_to_server(data, symmetric_key)
        data_to_return = PyAnyWhereRequests.send_request("get_username", encrypted_data, client_public_key = client_public_key, encrypted_symmetric_key = encrypted_symmetric_key)
        try:
            formated_data = PyAnyWhereRequests.format_data(data_to_return, client_private_key)
            return formated_data
        except Exception as e:
            return PyAnyWhereRequests.get_username(server_public_key, session_key, client_email, passID)
            
    @staticmethod
    def get_password(server_public_key, session_key, client_email, passID):
        client_public_key, client_private_key, symmetric_key, encrypted_symmetric_key = PyAnyWhereRequests.create_encryption_keys(server_public_key)
        data = {
            "session_key": session_key,
            "client_email": client_email,
            "passID": passID,
            "error_check": Generate.create_error_check(),
        }       
        encrypted_data = Encrypt.encrypt_data_to_server(data, symmetric_key)
        data_to_return = PyAnyWhereRequests.send_request("get_password", encrypted_data, client_public_key = client_public_key, encrypted_symmetric_key = encrypted_symmetric_key)
        try:
            formated_data = PyAnyWhereRequests.format_data(data_to_return, client_private_key)
            return formated_data
        except Exception as e:
            return PyAnyWhereRequests.get_password(server_public_key, session_key, client_email, passID)
            
    @staticmethod
    def get_all_passwords(server_public_key, session_key, client_email):
        client_public_key, client_private_key, symmetric_key, encrypted_symmetric_key = PyAnyWhereRequests.create_encryption_keys(server_public_key)
        data = {
            "session_key": session_key,
            "client_email": client_email,
            "error_check": Generate.create_error_check(),
        }
        encrypted_data = Encrypt.encrypt_data_to_server(data, symmetric_key)
        data_to_return = PyAnyWhereRequests.send_request("get_all_passwords", encrypted_data, client_public_key = client_public_key, encrypted_symmetric_key = encrypted_symmetric_key)
        try:
            formated_data = PyAnyWhereRequests.format_data(data_to_return, client_private_key)
            return formated_data
        except Exception as e:
            return PyAnyWhereRequests.get_all_passwords(server_public_key, session_key, client_email)
            
    @staticmethod
    def set_to_lockdown(server_public_key, session_key, client_email, passID):
        client_public_key, client_private_key, symmetric_key, encrypted_symmetric_key = PyAnyWhereRequests.create_encryption_keys(server_public_key)
        data = {
            "session_key": session_key,
            "client_email": client_email,
            "passID": passID,
            "error_check": Generate.create_error_check(),
        }
        encrypted_data = Encrypt.encrypt_data_to_server(data, symmetric_key)
        data_to_return = PyAnyWhereRequests.send_request("set_to_lockdown", encrypted_data, client_public_key = client_public_key, encrypted_symmetric_key = encrypted_symmetric_key)
        try:
            formated_data = PyAnyWhereRequests.format_data(data_to_return, client_private_key)
            return formated_data
        except Exception as e:
            return PyAnyWhereRequests.set_to_lockdown(server_public_key, session_key, client_email, passID)
            
    @staticmethod
    def remove_lockdown(server_public_key, session_key, client_email, passID):
        client_public_key, client_private_key, symmetric_key, encrypted_symmetric_key = PyAnyWhereRequests.create_encryption_keys(server_public_key)
        data = {
            "session_key": session_key,
            "client_email": client_email,
            "passID": passID,
            "error_check": Generate.create_error_check(),
        }
        encrypted_data = Encrypt.encrypt_data_to_server(data, symmetric_key)
        data_to_return = PyAnyWhereRequests.send_request("remove_lockdown", encrypted_data, client_public_key = client_public_key, encrypted_symmetric_key = encrypted_symmetric_key)
        try:
            formated_data = PyAnyWhereRequests.format_data(data_to_return, client_private_key)
            return formated_data
        except Exception as e:
            return PyAnyWhereRequests.remove_lockdown(server_public_key, session_key, client_email, passID)
            
    @staticmethod
    def add_new_password(server_public_key, session_key, client_email, password, title, url, username, additional_info, password_key):
        client_public_key, client_private_key, symmetric_key, encrypted_symmetric_key = PyAnyWhereRequests.create_encryption_keys(server_public_key)
        data = {
            "session_key": session_key,
            "client_email": client_email,
            "password": password,
            "title": title,
            "url": url,
            "username": username,
            "additional_info": additional_info,
            "password_key": password_key,
            "error_check": Generate.create_error_check(),
        }
        encrypted_data = Encrypt.encrypt_data_to_server(data, symmetric_key)
        data_to_return = PyAnyWhereRequests.send_request("add_new_password", encrypted_data, client_public_key = client_public_key, encrypted_symmetric_key = encrypted_symmetric_key)
        try:
            formated_data = PyAnyWhereRequests.format_data(data_to_return, client_private_key)
            return formated_data
        except Exception as e:
            return PyAnyWhereRequests.add_new_password(server_public_key, session_key, client_email, password, title, url, username, additional_info, password_key)
            
    @staticmethod
    def delete_password(server_public_key, session_key, client_email, passID):
        client_public_key, client_private_key, symmetric_key, encrypted_symmetric_key = PyAnyWhereRequests.create_encryption_keys(server_public_key)
        data = {
            "session_key": session_key,
            "client_email": client_email,
            "passID": passID,
            "error_check": Generate.create_error_check(),
        }
        encrypted_data = Encrypt.encrypt_data_to_server(data, symmetric_key)
        data_to_return = PyAnyWhereRequests.send_request("delete_password", encrypted_data, client_public_key = client_public_key, encrypted_symmetric_key = encrypted_symmetric_key)
        try:
            formated_data = PyAnyWhereRequests.format_data(data_to_return, client_private_key)
            return formated_data
        except Exception as e:
            return PyAnyWhereRequests.delete_password(server_public_key, session_key, client_email, passID)
            
    @staticmethod
    def add_manager(server_public_key, session_key, client_email, new_manager_email, passID):
        client_public_key, client_private_key, symmetric_key, encrypted_symmetric_key = PyAnyWhereRequests.create_encryption_keys(server_public_key)
        data = {
            "session_key": session_key,
            "client_email": client_email,
            "new_manager_email": new_manager_email,
            "passID": passID,
            "error_check": Generate.create_error_check(),
        }
        encrypted_data = Encrypt.encrypt_data_to_server(data, symmetric_key)
        data_to_return = PyAnyWhereRequests.send_request("add_manager", encrypted_data, client_public_key = client_public_key, encrypted_symmetric_key = encrypted_symmetric_key)
        try:
            formated_data = PyAnyWhereRequests.format_data(data_to_return, client_private_key)
            return formated_data
        except Exception as e:
            return PyAnyWhereRequests.add_manager(server_public_key, session_key, client_email, new_manager_email, passID)
            
    @staticmethod
    def get_password_users(server_public_key, session_key, client_email, passID, manager_only=False):
        client_public_key, client_private_key, symmetric_key, encrypted_symmetric_key = PyAnyWhereRequests.create_encryption_keys(server_public_key)
        data = {
            "session_key": session_key,
            "client_email": client_email,
            "passID": passID,
            "manager_only": manager_only,
            "error_check": Generate.create_error_check(),
        }
        encrypted_data = Encrypt.encrypt_data_to_server(data, symmetric_key)
        data_to_return = PyAnyWhereRequests.send_request("get_password_users", encrypted_data, client_public_key = client_public_key, encrypted_symmetric_key = encrypted_symmetric_key)
        try:
            formated_data = PyAnyWhereRequests.format_data(data_to_return, client_private_key)
            return formated_data
        except Exception as e:
            return PyAnyWhereRequests.get_password_users(server_public_key, session_key, client_email, passID, manager_only)
            
    @staticmethod
    def delete_password_instance(server_public_key, session_key, client_email, passID, new_manager_email):
        client_public_key, client_private_key, symmetric_key, encrypted_symmetric_key = PyAnyWhereRequests.create_encryption_keys(server_public_key)
        data = {
            "session_key": session_key,
            "client_email": client_email,
            "passID": passID,
            "new_manager_email": new_manager_email,
            "error_check": Generate.create_error_check(),
        }
        encrypted_data = Encrypt.encrypt_data_to_server(data, symmetric_key)
        data_to_return = PyAnyWhereRequests.send_request("delete_password_instance", encrypted_data, client_public_key = client_public_key, encrypted_symmetric_key = encrypted_symmetric_key)
        try:
            formated_data = PyAnyWhereRequests.format_data(data_to_return, client_private_key)
            return formated_data
        except Exception as e:
            print(traceback.format_exc())
            return PyAnyWhereRequests.delete_password_instance(server_public_key, session_key, client_email, passID, new_manager_email)
            
    @staticmethod
    def update_password(server_public_key, session_key, client_email, passID, new_info,type):
        client_public_key, client_private_key, symmetric_key, encrypted_symmetric_key = PyAnyWhereRequests.create_encryption_keys(server_public_key)
        data = {
            "session_key": session_key,
            "client_email": client_email,
            "passID": passID,
            "new_info": new_info,
            "type": type,
            "error_check": Generate.create_error_check(),
        }
        encrypted_data = Encrypt.encrypt_data_to_server(data, symmetric_key)
        data_to_return = PyAnyWhereRequests.send_request("update_password", encrypted_data, client_public_key = client_public_key, encrypted_symmetric_key = encrypted_symmetric_key)
        try:
            formated_data = PyAnyWhereRequests.format_data(data_to_return, client_private_key)
            return formated_data
        except Exception as e:
            return PyAnyWhereRequests.update_password(server_public_key, session_key, client_email, passID, new_info,type)    
        
    @staticmethod
    def get_pending_passwordkeys(server_public_key, session_key, client_email):
        client_public_key, client_private_key, symmetric_key, encrypted_symmetric_key = PyAnyWhereRequests.create_encryption_keys(server_public_key)
        data = {
            "session_key": session_key,
            "client_email": client_email,
            "error_check": Generate.create_error_check(),
        }
        encrypted_data = Encrypt.encrypt_data_to_server(data, symmetric_key)
        data_to_return = PyAnyWhereRequests.send_request("get_pending_passwordkeys", encrypted_data, client_public_key = client_public_key, encrypted_symmetric_key = encrypted_symmetric_key)
        try:
            formated_data = PyAnyWhereRequests.format_data(data_to_return, client_private_key)
            return formated_data
        except Exception as e:
            return PyAnyWhereRequests.get_pending_passwordkeys(server_public_key, session_key, client_email)
            
    @staticmethod
    def get_emails_sharing(server_public_key, session_key, requested_email):
        client_public_key, client_private_key, symmetric_key, encrypted_symmetric_key = PyAnyWhereRequests.create_encryption_keys(server_public_key)
        data = {
            "session_key": session_key,
            "email": requested_email,
            "error_check": Generate.create_error_check(),
        }
        encrypted_data = Encrypt.encrypt_data_to_server(data, symmetric_key)
        data_to_return = PyAnyWhereRequests.send_request("get_emails_sharing", encrypted_data, client_public_key = client_public_key, encrypted_symmetric_key = encrypted_symmetric_key)
        try:
            formated_data = PyAnyWhereRequests.format_data(data_to_return, client_private_key)
            return formated_data
        except Exception as e:
            return PyAnyWhereRequests.get_emails_sharing(server_public_key, session_key, requested_email)
            
    @staticmethod
    def share_password(server_public_key, session_key, client_email, passID, password_key, recipient_UserID, manager, encrypted_sharing_symmetric_key):
        client_public_key, client_private_key, symmetric_key, encrypted_symmetric_key = PyAnyWhereRequests.create_encryption_keys(server_public_key)
        data = {
            "session_key": session_key,
            "client_email": client_email,
            "passID": passID,
            "password_key": password_key,
            "recipient_UserID": recipient_UserID,
            "manager": manager,
            "encrypted_sharing_symmetric_key": encrypted_sharing_symmetric_key,
            "error_check": Generate.create_error_check(),
        }
        encrypted_data = Encrypt.encrypt_data_to_server(data, symmetric_key)
        data_to_return = PyAnyWhereRequests.send_request("share_password", encrypted_data, client_public_key = client_public_key, encrypted_symmetric_key = encrypted_symmetric_key)
        try:
            formated_data = PyAnyWhereRequests.format_data(data_to_return, client_private_key)
            return formated_data
        except Exception as e:
            return PyAnyWhereRequests.share_password(server_public_key, session_key, client_email, passID, password_key, recipient_UserID, manager, encrypted_sharing_symmetric_key)
            
    @staticmethod
    def insert_pending_keys(server_public_key, session_key, client_email, passID, password_key, manager):
        client_public_key, client_private_key, symmetric_key, encrypted_symmetric_key = PyAnyWhereRequests.create_encryption_keys(server_public_key)
        data = {
            "session_key": session_key,
            "client_email": client_email,
            "passID": passID,
            "password_key": password_key,
            "manager": manager,
            "error_check": Generate.create_error_check(),
        }
        encrypted_data = Encrypt.encrypt_data_to_server(data, symmetric_key)
        data_to_return = PyAnyWhereRequests.send_request("insert_pending_keys", encrypted_data, client_public_key = client_public_key, encrypted_symmetric_key = encrypted_symmetric_key)
        try:
            formated_data = PyAnyWhereRequests.format_data(data_to_return, client_private_key)
            return formated_data
        except Exception as e:
            return PyAnyWhereRequests.insert_pending_keys(server_public_key, session_key, client_email, passID, password_key, manager)
            
    @staticmethod
    def get_public_key(server_public_key, session_key, recipient_UserID):
        client_public_key, client_private_key, symmetric_key, encrypted_symmetric_key = PyAnyWhereRequests.create_encryption_keys(server_public_key)
        data = {
            "session_key": session_key,
            "recipient_UserID": recipient_UserID,
            "error_check": Generate.create_error_check(),
        }
        encrypted_data = Encrypt.encrypt_data_to_server(data, symmetric_key)
        data_to_return = PyAnyWhereRequests.send_request("get_public_key", encrypted_data, client_public_key = client_public_key, encrypted_symmetric_key = encrypted_symmetric_key)
        try:
            formated_data = PyAnyWhereRequests.format_data(data_to_return, client_private_key)
            return formated_data
        except Exception as e:
            return PyAnyWhereRequests.get_public_key(server_public_key, session_key, recipient_UserID)
            
    @staticmethod
    def reset_client_sharing_keys(server_public_key, session_key, new_key, client_email):
        client_public_key, client_private_key, symmetric_key, encrypted_symmetric_key = PyAnyWhereRequests.create_encryption_keys(server_public_key)
        data = {
            "session_key": session_key,
            "new_public_key": new_key,
            "client_email": client_email,
            "error_check": Generate.create_error_check(),
        }
        encrypted_data = Encrypt.encrypt_data_to_server(data, symmetric_key)
        data_to_return = PyAnyWhereRequests.send_request("update_public_keys", encrypted_data, client_public_key = client_public_key, encrypted_symmetric_key = encrypted_symmetric_key)
        try:
            formated_data = PyAnyWhereRequests.format_data(data_to_return, client_private_key)
            return formated_data
        except Exception as e:
            return PyAnyWhereRequests.reset_client_sharing_keys(server_public_key, session_key, new_key, client_email)
            
    @staticmethod
    def create_encryption_keys(server_public_key):
        client_public_key, client_private_key = Generate.generate_asymmetric_keys()
        symmetric_key = Generate.generate_symmetric_key()
        encrypted_symmetric_key = Encrypt.encrypt_key_to_server(symmetric_key, server_public_key)
        while not Generate.validate_symmetric_key(encrypted_symmetric_key):
            symmetric_key = Generate.generate_symmetric_key()
            encrypted_symmetric_key = Encrypt.encrypt_key_to_server(symmetric_key, server_public_key)
        return client_public_key, client_private_key, symmetric_key, encrypted_symmetric_key
        
  
    
    @staticmethod
    def format_data(data_to_return, client_private_key):
        encrypted_symmetric_key = data_to_return["encrypted_symmetric_key"]
        encrypted_data = data_to_return["data"]
        symmetric_key = Decrypt.decrypt_key_from_server(encrypted_symmetric_key, client_private_key)
        flag = data_to_return["flag"]
        if flag == "encryption fail":
            print("Encryption failed - Server end")
            raise Exception("KeyError")
        elif flag == "encryption success":
            if len(symmetric_key) != 24:
                print("Key too long, could cause error, retrying")
                raise Exception("KeyError")
            data = Decrypt.decrypt_data_from_server(encrypted_data, str(symmetric_key))
            error_check = data["error_check"]
            if Generate.validate_error_check(error_check):
                returned_data = data["data"]
                try:
                    if returned_data[0]=="FAILED":
                        print("FAILED")
                        return "FAILED"
                    else:
                        print(f"Data direct: {returned_data}")
                        return returned_data
                except:
                    return returned_data
            else:
                print("Error check failed - client end")
                raise Exception("KeyError")
        
        
        
    @staticmethod
    def send_request(request_header, data=[], client_public_key=[], encrypted_symmetric_key=""):
        url = "https://BenCrook.eu.pythonanywhere.com/post_endpoint"
        dic_to_send = {
            "request_header": request_header,
            "client_public_key": client_public_key,
            "request_data": data,
            "encrypted_symmetric_key": encrypted_symmetric_key
        }
        try:
            start_time = datetime.now()
            response = requests.post(url,json=dic_to_send) 
            if response.status_code == 200:
                print(f"\nSuccessful request: {request_header}, Duration: {datetime.now()-start_time}")
                response_data = response.json()  
                return response_data
                
         
            print(f"Unsuccessful request, status code: {response.status_code}, request: {request_header}")
        
        except Exception as e:
            return traceback.format_exc() + str(response.status_code)
    
