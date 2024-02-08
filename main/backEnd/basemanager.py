import sqlite3
from datetime import datetime, date, timedelta
from backEnd.dbrequests import PyAnyWhereRequests as pr
import uuid
import socket
import traceback
import backEnd.passwords as Pw
from backEnd.encryption import Encrypt, Decrypt, Generate
from backEnd.AsymmetricEncryption.endToEnd_encryption import AsyncRSA as rsa
from backEnd.hasher import Hash
from backEnd.scan import PasswordChecker, PasswordGenerator
import random
import re
from threading import Thread

# object created after user logged in to run actual password manager function
class Manager():
    def __init__(self, email, password, datastore, session_key=None, server_public_key=None):
        self.__password = password
        self.__datastore = datastore
        self.__mac_address_hash = Hash.create_hash(str(uuid.getnode()).encode("utf-8"), "default")
        self.__email = email
        self.__userID = None
        self.__passwords = []
        self.__pending_passwords = [] #passwords awaiting approval from user
        self.__scanned_passwords = None
        self.__client_permanent_key = self.__get_client_permanent_key()
        if session_key and server_public_key: #reduces number of requests to server
            self.__session_key = session_key
            self.__server_public_key = server_public_key
        else:
            self.__session_key = ""
            self.__set_session_key()

        
        
    def __get_client_permanent_key(self):
        return Hash.create_client_permanent_key(self.__password, self.__email)
    
    
    def __get_client_sharing_keys(self):
        #derive from client_password and the month.
        client_permanent_key = str(self.__client_permanent_key)
        current_date = str(datetime.now().strftime("/%m/%Y"))
        permanent_key_integer_list = list(map(ord,(client_permanent_key)))
        permanent_key_string_list = list(map(str, permanent_key_integer_list))
        permanent_key_string = ''.join(permanent_key_string_list)
        permanent_key_integer = int(permanent_key_string)
        date_no_characters = re.sub(r'\D', '', current_date)
        date_integer = int(date_no_characters)
        data_string = str(permanent_key_integer % date_integer)
        data_integer_list = list(map(ord, data_string))
        data_integer_string = ''.join(list(map(str, data_integer_list)))
        e, d, n = rsa.generate_keys(random=False, seed=data_integer_string)
        return e, d, n
    
    def save_initial_data(self,code,session_key,client_permanent_key):
        db = sqlite3.connect(rf"extensionAPI\infoapi.db")
        curs = db.cursor()
        curs.execute("CREATE TABLE IF NOT EXISTS Keys (SessionKey VARCHAR(256), ClientPermanentKey VARCHAR(256), ClientEmail VARCHAR(128))")
        fernet_key = Generate.generate_fernet(extra=code)
        encrypted_session_key = fernet_key.encrypt(session_key.encode('utf-8')).decode('utf-8')
        encrypted_permanent_key = fernet_key.encrypt(client_permanent_key).decode('utf-8')
        encrypted_client_email = fernet_key.encrypt(self.__email.encode('utf-8')).decode('utf-8')        
        curs.execute("DELETE FROM Keys")
        curs.execute(f"INSERT INTO Keys (SessionKey, ClientPermanentKey, ClientEmail) VALUES ('{encrypted_session_key}','{encrypted_permanent_key}','{encrypted_client_email}')")
        curs.close()
        db.commit()
        db.close()  
            
                    
    def clear_api_db(self):
        db = sqlite3.connect(rf"extensionAPI\infoapi.db")
        curs = db.cursor()
        curs.execute("DELETE FROM Keys")
        curs.execute("DELETE FROM UrlPassID")
        curs.close()
        db.commit()
        db.close()
    
    def __set_session_key(self):
        self.__set_server_key() #outdated server key could be cause of unauthenticated session key
        stored_password_hash = Hash.create_hash(self.__password.encode('utf-8'), salt_type=self.__email)
        print(f"Stored password hash: {stored_password_hash}")
        comparitive_password_hash = Hash.create_hash(stored_password_hash.encode('utf-8'))
        print(f"Comparitive password hash: {comparitive_password_hash}")
        data = pr.authenticate_password(self.__server_public_key,self.__email,self.__mac_address_hash, comparitive_password_hash)
        if data not in ["UNAUTHENTICATED","ERROR","TOO MANY ATTEMPTS"]:
            self.__session_key = data
            try:
                code = self.__datastore.get_data("extensioncode")
                
                db = sqlite3.connect(rf"extensionAPI\infoapi.db")
                curs = db.cursor()
                curs.execute("CREATE TABLE IF NOT EXISTS Keys (SessionKey VARCHAR(256), ClientPermanentKey VARCHAR(256), ClientEmail VARCHAR(128))")
                
                fernet_key = Generate.generate_fernet(extra=code)
                encrypted_session_key = fernet_key.encrypt(self.__session_key.encode('utf-8')).decode('utf-8')
                encrypted_permanent_key = fernet_key.encrypt(self.__client_permanent_key).decode('utf-8')
                encrypted_client_email = fernet_key.encrypt(self.__email.encode('utf-8')).decode('utf-8')

                curs.execute("DELETE FROM Keys")
                curs.execute(f"INSERT INTO Keys (SessionKey, ClientPermanentKey, ClientEmail) VALUES ('{encrypted_session_key}','{encrypted_permanent_key}','{encrypted_client_email}')")
                curs.close()
                db.commit()
                db.close()
            except Exception as e:
                print(traceback.format_exc())
                pass
            return data
        else:
            return "UNAUTHENTICATED"
        
    def reset_client_password(self, new_password):
        passwords = self.export_all()

    def __reset_client_sharing_keys(self):
        e, d, n = self.__get_client_sharing_keys()
        new_public_key = f"{e}-{n}"
        data = pr.reset_client_sharing_keys(self.__server_public_key,self.__session_key,new_public_key, self.__email)
        print(data)

    def validate_client_public_key(self):
        try:
            if not self.__userID:
                self.__userID = pr.get_emails_sharing(self.__server_public_key,self.__session_key,self.__email)[0]
            client_public_key = pr.get_public_key(self.__server_public_key,self.__session_key,self.__userID)
            server_e, server_n = client_public_key.split('-')
            e, d, n = self.__get_client_sharing_keys()
            print(f"Server public key: {server_e}-{server_n}")
            print(f"Client public key: {e}-{n}")
            if str(server_e) != str(e) or str(server_n) != str(n):
                self.__reset_client_sharing_keys()
        except Exception as e:
            self.__reset_client_sharing_keys()
        
    def get_all_passwords_full(self):
        passId_list = list(map(lambda x: x.get_passID(), self.__passwords))
        threads = [Thread(target=self.get_specific_password_info, args=(obj,)) for obj in passId_list]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
            
    def get_all_managers_users(self):
        passId_list = list(map(lambda x: x.get_passID(), self.__passwords))
        threads = [Thread(target=self.get_password_users, args=(obj,)) for obj in passId_list]
        threads += [Thread(target=self.get_password_users, args=(obj, True)) for obj in passId_list]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        
    def refresh(self):
        for password in self.__passwords:
            del password
        
    def create_random_password(self,length=16):
        return PasswordGenerator.create_random_password(length)
            
    def __set_server_key(self):
        server_public_key = pr.get_server_key()
        self.__server_public_key = list(map(int, server_public_key))
            
            
    def get_pending_shares(self, iterations=0):
        print("Downloading pending password overviews")
        data = pr.get_pending_passwordkeys(self.__server_public_key,self.__session_key,self.__email)
        if data == "NO PENDING PASSWORDS":
            return data
        if data in ["UNAUTHENTICATED","KEY EXPIRED", "NO KEY"]:
            if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                return self.get_pending_shares(iterations=1)
        else:
            data_to_return = []
            for password_info in data:
                self.__pending_passwords.append(password_info)
                data_to_return.append(password_info[0:2] + password_info[4:7]) #returns passID, title, sender_email, sender_name, sender_surname
            return data_to_return #in form of 2d array
        
    def accept_pending_share(self,passID,accept):
        #check passID matches that in pending passwords
        for element in self.__pending_passwords:
            if element[0] == passID:
                encrypted_password_key = element[2]
                encrypted_symmetric_key = element[7]
                print(f"Encrypted symmetric key from accept pending share: {encrypted_symmetric_key}")
                e, d, n = self.__get_client_sharing_keys()
                symmetric_key = Decrypt.decrypt_symmetric_key_sharing(encrypted_symmetric_key, d, n)
                print(f"Decrypted symmetric key from accept pending share: {symmetric_key}")
                if len(symmetric_key) > 21:
                    break
                print(f"Encrypted password key from accept pending share: {encrypted_password_key}")
                password_key = Decrypt.decrypt_password_key_to_share(encrypted_password_key, symmetric_key)
                print(f"Decrypted password key from accept pending share: {password_key}")
                print("Inserting pending password into database")
                password_key = Encrypt.encrypt_password_key(password_key, self.__client_permanent_key)
                data = pr.insert_pending_keys(self.__server_public_key,self.__session_key,self.__email,passID,password_key,accept)
                self.__pending_passwords.remove(element)
                return data
            
    def check_no_pending(self):
        if len(self.__pending_passwords) == 0:
            return True
        else:
            return False
            
            
    def import_passwords(self, iterations=0):
        print("Downloading password overviews...")
        start_time = datetime.now()
        self.__passwords = []
        self.__scanned_passwords = None
        password_data = pr.get_password_overview(self.__server_public_key,self.__session_key,self.__email)
        if password_data in ["UNAUTHENTICATED","KEY EXPIRED", "NO KEY"]:
            if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                return self.import_passwords(iterations=1) #returns so anything below this doesn't run
        elif password_data == "ERROR":
            return password_data
        for single_password in password_data:
            # print(single_password)
            url, title, username, passID, manager = single_password
            if url == "": #if no url therefore not a login password
                self.__passwords.append(Pw.Info(passID, title, manager))
            else:
                self.__passwords.append(Pw.Password(passID, title, url, username, manager))
                
        db = sqlite3.connect(rf"extensionAPI\infoapi.db")
        curs = db.cursor()
        curs.execute("CREATE TABLE IF NOT EXISTS UrlPassID (URL VARCHAR(128), PassID VARCHAR(128), Username VARCHAR(128))")
        curs.execute("DELETE FROM UrlPassID")
        print("created UrlPassID table")
        for password in self.__passwords:
            if type(password) == Pw.Password:
                curs.execute(f"INSERT INTO UrlPassID (URL, PassID, Username) VALUES ('{password.get_url()}','{password.get_passID()}','{password.get_username()}')")
        curs.close()
        db.commit()
        db.close()
        end_time = datetime.now()
        print(f"Time taken to download password overviews: {end_time-start_time}")
        
    def get_passwords(self):
        data_to_return = []
        for password in self.__passwords:
            if type(password) == Pw.Password:
                data_to_return.append(password.get_summary_inc_passID())
        return data_to_return
    
    def get_infos(self):
        data_to_return = []
        for password in self.__passwords:
            if type(password) == Pw.Info:
                data_to_return.append(password.get_summary_inc_passID())
        return data_to_return
                
    def get_all(self):
        return [password.get_summary_inc_passID() for password in self.__passwords]

    def export_all(self, iterations=0):
        data = pr.get_all_passwords(self.__server_public_key,self.__session_key,self.__email)
        if data in ["UNAUTHENTICATED","KEY EXPIRED", "NO KEY"]:
            if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                return self.export_all(iterations=1)
            else:
                return None
        else:
            for element in data:
                encrypted_password = element[1]
                encrypted_password_key = element[2]
                password_key = Decrypt.decrypt_password_key(encrypted_password_key, self.__client_permanent_key)
                # print(element[5])
                # print(f"Decrypted password key from getall: {password_key}")
                # print(f"Encrypted password from getall: {element[1]}")
                password = Decrypt.decrypt_password(encrypted_password, password_key)
                element[1] = password
                element[2] = password_key
            return data
        
    def get_manager_info(self, passID):
        for password in self.__passwords:
            if str(password.get_passID()) == passID:
                return password.get_manager()
    
    def add_new_password(self,title,url,username,additional_info,password, iterations=0):
        password_key = Generate.generate_password_key()
        encrypted_password = Encrypt.encrypt_password(password, password_key)
        encrypted_password_key = Encrypt.encrypt_password_key(password_key, self.__client_permanent_key)
        data = pr.add_new_password(self.__server_public_key,self.__session_key,self.__email,
                            encrypted_password,title,url,username,additional_info,encrypted_password_key)
        if data in ["UNAUTHENTICATED","KEY EXPIRED", "NO KEY"]:
            if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                return self.add_new_password(title,url,username,additional_info,password, iterations=1)
        if data in ["PASSWORD ALRAEDY EXISTS", "ERROR"]:
            return data
        else:
            self.import_passwords()
            return data
            
    def get_specific_password_info(self,passID, iterations=0):
        #can use a for loop as operation in each loop is very quick
        #not likely to be more than 100 passwords
        #password list is not ordered
        #so would require sort and more operations to use other search
        #therefore linear search is efficient enough
        for password in self.__passwords:
            if str(password.get_passID()) == str(passID): #only allows user to request passwords which they have access to
                data = password.get_password(client_email=self.__email,session_key=self.__session_key,
                                             server_public_key=self.__server_public_key,client_permanent_key=self.__client_permanent_key)  
                if data in ["UNAUTHENTICATED","KEY EXPIRED", "NO KEY"]:
                    if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                        return self.get_specific_password_info(passID,iterations=1)
                extra = password.get_summary()
                if type(password) == Pw.Password:
                    add_info = password.get_additional_info()
                    extra.append(add_info)
                return [data]+extra #data could be ERROR in error senario
            
            
    def get_password_additonal_info(self,passID, iterations=0):
        for password in self.__passwords:
            if str(password.get_passID()) == str(passID):
                data = password.get_additional_info(client_email=self.__email,session_key=self.__session_key,server_public_key=self.__server_public_key)
                if data in ["UNAUTHENTICATED","KEY EXPIRED", "NO KEY"]:
                    if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                        return self.get_password_additonal_info(passID,iterations=1)
                return data
            
    def delete_password(self,passID, iterations=0):
        for password in self.__passwords:
            if str(password.get_passID()) == str(passID):
                data = password.delete_password(client_email=self.__email,session_key=self.__session_key,server_public_key=self.__server_public_key)
                if data in ["UNAUTHENTICATED","KEY EXPIRED", "NO KEY"]:
                    if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                        return self.delete_password(passID,iterations=1)
                return data

    
    def delete_password_instance(self,passID,new_manager_email=None, iterations=0):
        for password in self.__passwords:
            if str(password.get_passID()) == str(passID):
                managers = password.get_password_managers(client_email=self.__email,session_key=self.__session_key,server_public_key=self.__server_public_key)
                print(managers)
                if managers in ["UNAUTHENTICATED","KEY EXPIRED", "NO KEY"]:
                    if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                        return self.delete_password_instance(passID,new_manager_email,iterations=1)
                elif managers == "NOT MANAGER":
                    data = password.delete_password_instance(client_email=self.__email,new_manager_email=None,session_key=self.__session_key,server_public_key=self.__server_public_key)
                    return data[0:25]
                else:
                    if len(managers) > 1:   #will cause exception if no managers because NoneType
                        data = password.delete_password_instance(client_email=self.__email,new_manager_email=None,session_key=self.__session_key,server_public_key=self.__server_public_key)
                        return data[0:25]
                    elif new_manager_email:
                        data = password.delete_password_instance(client_email=self.__email,new_manager_email=new_manager_email,session_key=self.__session_key,server_public_key=self.__server_public_key)
                        return data[0:25]
                    else:
                        return "New manager email required"
               
                   
               
    def get_password_users(self,passID, manager=False, iterations=0):
        for password in self.__passwords:
            if str(password.get_passID()) == str(passID):
                if manager:
                    data = password.get_password_managers(client_email=self.__email,session_key=self.__session_key,server_public_key=self.__server_public_key)
                else:
                    data = password.get_password_users(client_email=self.__email,session_key=self.__session_key,server_public_key=self.__server_public_key)
                if data in ["UNAUTHENTICATED","KEY EXPIRED", "NO KEY"]:
                    if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                        return self.get_password_users(passID,iterations=1)
                return data

                
    def set_to_lockdown(self,passID, iterations=0):
        for password in self.__passwords:
            if str(password.get_passID()) == str(passID):
                data = password.set_to_lockdown(client_email=self.__email,session_key=self.__session_key,server_public_key=self.__server_public_key)
                if data in ["UNAUTHENTICATED","KEY EXPIRED", "NO KEY"]:
                    if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                        return self.set_to_lockdown(passID,iterations=1)
                if data == "SET TO LOCKDOWN":
                    db = sqlite3.connect(rf"assets\assetdata.db") #stores locked down passwords locally so can only unlock on same device
                    curs = db.cursor()
                    curs.execute("CREATE TABLE IF NOT EXISTS Lockdown(PassID VARCHAR(64) primary key)")
                    curs.execute(f"INSERT INTO Lockdown VALUES('{passID}')") # passID is unique, so will unlock all passwords locked on this device
                    curs.close()                                                  # but on server side it only allows to unlock your passwords, so no verification needed
                    db.commit()
                    db.close()
                return data
                
    def __remove_from_lockdown(self,passID, iterations=0):
        data = pr.remove_lockdown(server_public_key=self.__server_public_key,session_key=self.__session_key,client_email=self.__email,passID=passID)
        if data in ["UNAUTHENTICATED","KEY EXPIRED", "NO KEY"]:
            if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                return self.remove_from_lockdown(passID,iterations=1)
        return data
    
    def remove_password_user(self, passID, user_email, iterations=0):
        for password in self.__passwords:
            if str(password.get_passID()) == str(passID):
                data = password.remove_password_user(client_email=self.__email,session_key=self.__session_key,server_public_key=self.__server_public_key, user_emai=user_email)
                if data in ["UNAUTHENTICATED","KEY EXPIRED", "NO KEY"]:
                    if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                        return self.remove_password_user(passID,iterations=1)
                elif data == "REMOVED USER":
                    threads = [
                        Thread(target=self.get_password_users, args=(self.__email, self.__session_key, self.__server_public_key)),
                        Thread(target=self.get_password_managers, args=(self.__email, self.__session_key, self.__server_public_key))
                    ]
                    for thread in threads:
                        thread.start()
                    for thread in threads:
                        thread.join()
                    #runs reqeusts in parallel
                return data
              
                
    def remove_all_locked_down_passwords(self, online=False):
        if online:
            data = self.__remove_from_lockdown("all")
            if data == "REMOVED LOCKDOWN":
                success = "True"
            else:
                success = "Failed"
        else:
            try:
                success = "True"
                db = sqlite3.connect(rf"assets\assetdata.db")
                curs = db.cursor()
                curs.execute("SELECT * FROM Lockdown")
                locked_passwords = curs.fetchall()
                for password in locked_passwords:
                    print("removing from lockdown")
                    print(f"password id: {password[0]}")
                    data = self.__remove_from_lockdown(password[0])
                    if data != "REMOVED LOCKDOWN":
                        success = "Failed"
                curs.execute(f"DELETE FROM Lockdown")
                curs.close()
                db.commit()
                db.close()
            except Exception as e:
                success = "No lockdown"
        return success
                    
                
    def add_manager(self,passID,new_manager_email, iterations=0):
        for password in self.__passwords:
            if str(password.get_passID()) == str(passID):
                data = password.add_manager(client_email=self.__email,new_manager_email=new_manager_email,session_key=self.__session_key,server_public_key=self.__server_public_key)
                if data in ["UNAUTHENTICATED","KEY EXPIRED", "NO KEY"]:
                    if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                        return self.add_manager(passID,new_manager_email,iterations=1)
                return data

            
    def update_password(self,passID,new_info,type, iterations=0):
        for password in self.__passwords:
            if str(password.get_passID()) == str(passID):
                print(f"Updating password: PassID = {passID}, new_info = {new_info}, type = {type}")
                data = password.update_password(client_email=self.__email,new_info=new_info,type=type,session_key=self.__session_key,server_public_key=self.__server_public_key)
                if data in ["UNAUTHENTICATED","KEY EXPIRED", "NO KEY"]:
                    if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                        return self.update_password(passID,new_info,type,iterations=1)
                print(data)
                return data
            
            
            
    def share_password_check(self,passID,new_manager_email, iterations=0): #give manager as 1 or 0
        for password in self.__passwords:
            if str(password.get_passID()) == str(passID):
                user_info = pr.get_emails_sharing(server_public_key=self.__server_public_key,session_key=self.__session_key,requested_email=new_manager_email)
                print(f"manager user info = {user_info}")
                if user_info in ["UNAUTHENTICATED","KEY EXPIRED", "NO KEY"]:
                    if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                        return self.share_password_check(passID,new_manager_email,iterations=1)
                return user_info

    
    def share_password_confirm(self,passID,new_manager_email,manager, iterations=0): #give manager as 1 or 0
        for password in self.__passwords:
            if str(password.get_passID()) == str(passID):
                user_info = pr.get_emails_sharing(server_public_key=self.__server_public_key,session_key=self.__session_key,requested_email=new_manager_email)
                if user_info in ["UNAUTHENTICATED","KEY EXPIRED", "NO KEY"]:
                    if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                        return self.share_password_confirm(passID,new_manager_email,manager,iterations=1)
                elif user_info == "FAILED":
                    return "FAILED"
                recipient_UserID = user_info[0]
                data = password.share_password(client_email=self.__email,session_key=self.__session_key,server_public_key=self.__server_public_key,
                    recipient_userID=recipient_UserID,manager=manager,client_permanent_key=self.__client_permanent_key)
                return data
        
    
    def scan_passwords(self): #can't run as a function of password class because all passwords are required from cross evaluation
        if self.__scanned_passwords:
            return self.__scanned_passwords
        else:
            passwords_data = self.export_all()
            if passwords_data == None: 
                return None
            else:
                passwords_data.sort(key=lambda x: x[5])
                password_list_of_dicts = []
                #[temp_PassID,password,password_key,additional_info,url,title,username] format of data returned from server
                print(f"PW data: {passwords_data}")
                for element in passwords_data:
                    if element[7] == 0:  #password not set to lockdown
                        password_list_of_dicts.append(
                            {
                                "password": element[1],
                                "username": element[6],
                                "passID": element[0],
                                "url": element[4],
                                "title": element[5],
                            }
                        )
                p = PasswordChecker(password_list_of_dicts)
                evaluated_passwords = p.scan_all_passwords()
                self.__scanned_passwords = evaluated_passwords
                return evaluated_passwords
    
    def validate_client_password(self, password):
        return self.__password == password
    
    def reset_client_password(self, new_password, iterations=0):
        passwords = self.export_all()
        new_permanent_key = Hash.create_client_permanent_key(new_password, self.__email)
        new_password_keys = {}
        for password in passwords:
            passID = password[0]
            password_key = password[2]
            new_password_key = Encrypt.encrypt_password_key(password_key, new_permanent_key)
            new_password_keys[passID] = new_password_key
        new_password_hash = Hash.create_hash(new_password.encode('utf-8'), salt_type=self.__email)
        data = pr.reset_client_password(self.__server_public_key,self.__session_key,self.__email,new_password_hash,self.__password,new_password_keys)
        if data in ["UNAUTHENTICATED","KEY EXPIRED", "NO KEY"]:
            if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                return self.reset_client_password(new_password,iterations=1)
        if data == "RESET":
            self.__clear_api_db()
            #will automatically logout after this
            return data
        