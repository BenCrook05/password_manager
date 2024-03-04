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
from backEnd.loginlogic import Application
import random
import re
from threading import Thread
import csv
import os
import subprocess
from sys import platform

class Manager():
    def __init__(self, email, password, datastore, session_key=None, server_public_key=None):
        self.__password = password
        self.__datastore = datastore
        self.__mac_address_hash = Hash.create_hash(str(uuid.getnode()).encode("utf-8"), "default")
        self.__email = email
        self.__userID = None
        self.__passwords = []
        self.__pending_passwords = [] #passwords awaiting approval from user
        self.__scanned_passwords = []
        self.__client_permanent_key = self.__get_client_permanent_key()
        if session_key and server_public_key: 
            #reduces number of requests to server by using same session key provided on login
            self.__session_key = session_key
            self.__server_public_key = server_public_key
        else:
            self.__session_key = ""
            check = self.__set_session_key()
            if check == "UNAUTHENTICATED":
                raise ValueError("UNAUTHENTICATED")
        
    def get_email(self):
        return self.__email
        
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
            
    
    def __set_session_key(self):
        #outdated server key could be cause of unauthenticated session key so reset server key too
        self.__set_server_key() 
        stored_password_hash = Hash.create_hash(self.__password.encode('utf-8'), salt_type=self.__email)
        comparitive_password_hash = Hash.create_hash(stored_password_hash.encode('utf-8'))
        data = pr.authenticate_password(self.__server_public_key,self.__email,self.__mac_address_hash, comparitive_password_hash)
        if data not in ["UNAUTHENTICATED","FAILED","ERROR","TOO MANY ATTEMPTS"]:
            self.__session_key = data
            return data
        else:
            return "UNAUTHENTICATED"
        

    def __reset_client_sharing_keys(self):
        #recreate sharing keys (for new month) and upload to server
        e, d, n = self.__get_client_sharing_keys()
        new_public_key = f"{e}-{n}"
        data = pr.reset_client_sharing_keys(self.__server_public_key,self.__session_key,new_public_key, self.__email)

    def validate_client_public_key(self):
        #checks public key isn't outdated
        #derives public key from current month and compares to public key retrieved from server
        try:
            if not self.__userID:
                self.__userID = pr.get_emails_sharing(self.__server_public_key,self.__session_key,self.__email)[0]
            client_public_key = pr.get_public_key(self.__server_public_key,self.__session_key,self.__userID)
            server_e, server_n = client_public_key.split('-')
            e, d, n = self.__get_client_sharing_keys()
            if str(server_e) != str(e) or str(server_n) != str(n):
                #public key outdated to upload up to date public key to server
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
        #downloads server public key and stores as attribute
        server_public_key = pr.get_server_key()
        self.__server_public_key = list(map(int, server_public_key))
            
            
    def get_pending_shares(self, iterations=0):
        #downloads passwords that have been shared with user 
        data = pr.get_pending_passwordkeys(self.__server_public_key,self.__session_key,self.__email)
        if data == "NO PENDING PASSWORDS":
            return data
        if data in ["UNAUTHENTICATED","FAILED","KEY EXPIRED", "NO KEY"]:
            if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                return self.get_pending_shares(iterations=1)
            else:
                return "UNAUTHENTICATED"
        else:
            data_to_return = []
            for password_info in data:
                self.__pending_passwords.append(password_info)
                data_to_return.append(password_info[0:2] + password_info[4:7]) #returns passID, title, sender_email, sender_name, sender_surname
            return data_to_return #in form of 2d array
        
    def accept_pending_share(self,passID,accept):
        for element in self.__pending_passwords:
            if element[0] == passID:
                encrypted_password_key = element[2]
                encrypted_symmetric_key = element[7]
                e, d, n = self.__get_client_sharing_keys()
                symmetric_key = Decrypt.decrypt_symmetric_key_sharing(encrypted_symmetric_key, d, n)
                print("Symmetric key decrypted: ", symmetric_key)
                #checks the decrypted symmetric key is valid
                #if not, cancel and instead reject pending share
                if len(symmetric_key) > 21:
                    pr.insert_pending_keys(self.__server_public_key,self.__session_key,self.__email,passID,encrypted_password_key,"Reject")
                #otherwise decrypt password key using symmetric key and re encrypt using client permanent key
                password_key = Decrypt.decrypt_password_key_to_share(encrypted_password_key, symmetric_key)
                print("Password key decrypted: ", password_key)
                password_key = Encrypt.encrypt_password_key(password_key, self.__client_permanent_key)
                data = pr.insert_pending_keys(self.__server_public_key,self.__session_key,self.__email,passID,password_key,accept)
                self.__pending_passwords.remove(element)
                return data
            
    def check_no_pending(self):
        if len(self.__pending_passwords) == 0:
            return True
        else:
            return False
            
            
    def import_passwords(self, full = False, iterations=0):
        #gets all passwords when user logs in
        #stores as list of password objects
        # self.__passwords = []
        new_passwords = []
        self.__scanned_passwords = None
        password_data = pr.get_password_overview(self.__server_public_key,self.__session_key,self.__email,full)
        if password_data in ["UNAUTHENTICATED","FAILED","KEY EXPIRED", "NO KEY"]:
            if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                return self.import_passwords(iterations=1) 
            else:
                return "UNAUTHENTICATED"
        elif password_data == "ERROR":
            return password_data
        success = True
        error = ""
        if full:
            for single_password in password_data:
                try:
                    URL, Title, Username, PassID, Manager, PasswordKey, AdditionalInfo, Password, users_list, managers_list = single_password
                    decrypted_password_key = Decrypt.decrypt_password_key(PasswordKey, self.__client_permanent_key)
                    decrypted_password = Decrypt.decrypt_password(Password, decrypted_password_key)
                    #infos don't have a url so check if exists to determine type of passinfo
                    if URL == "": 
                        new_passwords.append(Pw.Info(PassID,Title,Manager,decrypted_password,decrypted_password_key,users_list,managers_list))
                    else:
                        new_passwords.append(Pw.Password(PassID,Title,URL,Username,Manager,decrypted_password,decrypted_password_key,AdditionalInfo,users_list,managers_list))
                except Exception as e:
                    success = False
                    error = e
            if not success:
                self.__passwords = new_passwords
                #error has occured, but all other passwords are still downloaded (otherwise a single error would cause app to be unusable)     
                return f"ERROR: {error}"      
            else:
                self.__passwords = new_passwords
                return "SUCCESS"
        #only import overviews to reduce tranmission time and reduce load up time
        else:
            for single_password in password_data:
                try:
                    URL, Title, Username, PassID, Manager = single_password
                    if URL == "":
                        new_passwords.append(Pw.Info(PassID,Title,Manager))
                    else:
                        new_passwords.append(Pw.Password(PassID,Title,URL,Username,Manager))
                except Exception as e:
                    success = False
                    error = e
            if not success:
                self.__passwords = new_passwords
                return f"ERROR: {error}"
            else:
                self.__passwords = new_passwords
                return "SUCCESS"
                    
        
        
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

    def export_all(self, iterations=0, download_csv=False):
        #download basic password info from the server for scanning or exporting passwords
        data = pr.get_all_passwords(self.__server_public_key,self.__session_key,self.__email)
        if data in ["UNAUTHENTICATED","FAILED","KEY EXPIRED", "NO KEY"]:
            if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                return self.export_all(iterations=1)
            else:
                return "UNAUTHENTICATED"
        else:
            for element in data:
                encrypted_password = element[1]
                encrypted_password_key = element[2]
                password_key = Decrypt.decrypt_password_key(encrypted_password_key, self.__client_permanent_key)
                password = Decrypt.decrypt_password(encrypted_password, password_key)
                element[1] = password
                element[2] = password_key
            if not download_csv:
                return data
            else:
                return self.__generate_csv(data)
               
    def __generate_csv(self, password_list):
        try:
            print("password_list: ", password_list)
            password_list = list(map(lambda x: [x[4],x[1]], password_list))
            #removes passwords without a url (infos) 
            password_list = [password for password in password_list if password[0] != ""]
            
            #create a path to the downloads directory
            csv_file = "passwords.csv"
            downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            csv_file_path = os.path.join(downloads_dir, csv_file)
            #deletes password.csv if already exists
            if os.path.exists(csv_file_path):
                os.remove(csv_file_path)
                
            #writes password list to csv file
            with open(csv_file_path, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Website", "Password"])
                writer.writerows(password_list)
            #opens the downloads folder if on windows
            if platform == "win32":
                #https://docs.python.org/3/library/subprocess.html
                subprocess.Popen(["explorer", os.path.join(os.path.expanduser("~"), "Downloads")])
            return True
        except Exception as e:
            print(traceback.format_exc())
            return False
    
        
    def get_manager_info(self, passID):
        for password in self.__passwords:
            if password.get_passID() == passID:
                return password.get_manager()
    
    def add_new_password(self,title,url,username,additional_info,password, iterations=0):
        #generate random password key because new password then use to encrypt
        password_key = Generate.generate_password_key()
        encrypted_password = Encrypt.encrypt_password(password, password_key)
        encrypted_password_key = Encrypt.encrypt_password_key(password_key, self.__client_permanent_key)
        data = pr.add_new_password(self.__server_public_key,self.__session_key,self.__email,
                            encrypted_password,title,url,username,additional_info,encrypted_password_key)
        if data in ["UNAUTHENTICATED","FAILED","KEY EXPIRED", "NO KEY"]:
            if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                return self.add_new_password(title,url,username,additional_info,password, iterations=1)
            else:
                return "UNAUTHENTICATED"
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
                print("Getting specific password info")
                data = password.get_password(client_email=self.__email,session_key=self.__session_key,
                                             server_public_key=self.__server_public_key,client_permanent_key=self.__client_permanent_key)  
                print("Data: ", data)
                if data in ["UNAUTHENTICATED","FAILED","KEY EXPIRED", "NO KEY"]:
                    if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                        return self.get_specific_password_info(passID,iterations=1)
                    else:
                        return "UNAUTHENTICATED"
                extra = password.get_summary()
                if type(password) == Pw.Password:
                    add_info = password.get_additional_info()
                    extra.append(add_info)
                return [data]+extra #data could be ERROR in error senario
            
            
    def get_password_additonal_info(self,passID, iterations=0):
        for password in self.__passwords:
            if password.get_passID() == str(passID):
                data = password.get_additional_info(client_email=self.__email,session_key=self.__session_key,server_public_key=self.__server_public_key)
                if data in ["UNAUTHENTICATED","FAILED","KEY EXPIRED", "NO KEY"]:
                    if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                        return self.get_password_additonal_info(passID,iterations=1)
                    else:
                        return "UNAUTHENTICATED"
                return data
            
    def delete_password(self,passID, iterations=0):
        for password in self.__passwords:
            if password.get_passID() == str(passID):
                data = password.delete_password(client_email=self.__email,session_key=self.__session_key,server_public_key=self.__server_public_key)
                if data in ["UNAUTHENTICATED","FAILED","KEY EXPIRED", "NO KEY"]:
                    if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                        return self.delete_password(passID,iterations=1)
                    else:
                        return "UNAUTHENTICATED"
                return data

    
    def delete_password_instance(self,passID,new_manager_email=None, iterations=0):
        for password in self.__passwords:
            if password.get_passID() == str(passID):
                managers = password.get_password_managers(client_email=self.__email,session_key=self.__session_key,server_public_key=self.__server_public_key)
                if managers in ["UNAUTHENTICATED","FAILED","KEY EXPIRED", "NO KEY"]:
                    if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                        return self.delete_password_instance(passID,new_manager_email,iterations=1)
                    else:
                        return "UNAUTHENTICATED"
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
            if password.get_passID() == str(passID):
                if manager:
                    data = password.get_password_managers(client_email=self.__email,session_key=self.__session_key,server_public_key=self.__server_public_key)
                else:
                    data = password.get_password_users(client_email=self.__email,session_key=self.__session_key,server_public_key=self.__server_public_key)
                if data in ["UNAUTHENTICATED","FAILED","KEY EXPIRED", "NO KEY"]:
                    if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                        return self.get_password_users(passID,iterations=1)
                    else:
                        return "UNAUTHENTICATED"
                return data

                
    def set_to_lockdown(self,passID, iterations=0):
        for password in self.__passwords:
            if password.get_passID() == str(passID):
                data = password.set_to_lockdown(client_email=self.__email,session_key=self.__session_key,server_public_key=self.__server_public_key)
                if data in ["UNAUTHENTICATED","FAILED","KEY EXPIRED", "NO KEY"]:
                    if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                        return self.set_to_lockdown(passID,iterations=1)
                    else:
                        return "UNAUTHENTICATED"
                if data == "SET TO LOCKDOWN":
                    #locked passID stored on device so can be removed from lockdown by the user that set the password to lockdown initially
                    #only passID needs to be stored
                    db = sqlite3.connect(rf"assets\assetdata.db")
                    curs = db.cursor()
                    curs.execute("CREATE TABLE IF NOT EXISTS Lockdown(PassID VARCHAR(64) primary key)")
                    curs.execute(f"INSERT INTO Lockdown VALUES('{passID}')")
                    curs.close()                                             
                    db.commit()
                    db.close()
                return data
                
    def __remove_from_lockdown(self,passID, iterations=0):
        data = pr.remove_lockdown(server_public_key=self.__server_public_key,session_key=self.__session_key,client_email=self.__email,passID=passID)
        if data in ["UNAUTHENTICATED","FAILED","KEY EXPIRED", "NO KEY"]:
            if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                return self.remove_from_lockdown(passID,iterations=1)
            else:
                return "UNAUTHENTICATED"
        return data
    
    def remove_password_user(self, passID, user_email, iterations=0):
        for password in self.__passwords:
            if password.get_passID() == str(passID):
                data = password.remove_password_user(client_email=self.__email,session_key=self.__session_key,server_public_key=self.__server_public_key, user_email=user_email)
                if data in ["UNAUTHENTICATED","FAILED","KEY EXPIRED", "NO KEY"]:
                    if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                        return self.remove_password_user(passID,iterations=1)
                    else:
                        return "UNAUTHENTICATED"
                elif data == "REMOVED USER":
                    threads = [
                        Thread(target=password.get_password_users, args=(self.__email, self.__session_key, self.__server_public_key)),
                        Thread(target=password.get_password_managers, args=(self.__email, self.__session_key, self.__server_public_key))
                    ]
                    for thread in threads:
                        thread.start()
                    for thread in threads:
                        thread.join()
                    #runs reqeusts in parallel
                return data
              
                
    def remove_all_locked_down_passwords(self, online=False):
        if online:
            #unlock all passwords managed by user (handled by server)
            data = self.__remove_from_lockdown("all")
            if data == "REMOVED LOCKDOWN":
                success = "True"
            else:
                success = "Failed"
        else:
            try:
                #unlock all passwords stored locally 
                success = "True"
                db = sqlite3.connect(rf"assets\assetdata.db")
                curs = db.cursor()
                curs.execute("SELECT * FROM Lockdown")
                locked_passwords = curs.fetchall()
                for password in locked_passwords:
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
            if password.get_passID() == str(passID):
                data = password.add_manager(client_email=self.__email,new_manager_email=new_manager_email,session_key=self.__session_key,server_public_key=self.__server_public_key)
                if data in ["UNAUTHENTICATED","FAILED","KEY EXPIRED", "NO KEY"]:
                    if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                        return self.add_manager(passID,new_manager_email,iterations=1)
                    else:
                        return "UNAUTHENTICATED"
                return data

            
    def update_password(self,passID,new_info,type, iterations=0):
        for password in self.__passwords:
            if password.get_passID() == str(passID):
                data = password.update_password(client_email=self.__email,new_info=new_info,type=type,session_key=self.__session_key,server_public_key=self.__server_public_key)
                if data in ["UNAUTHENTICATED","FAILED","KEY EXPIRED", "NO KEY"]:
                    if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                        return self.update_password(passID,new_info,type,iterations=1)
                    else:
                        return "UNAUTHENTICATED"
                return data
            
            
            
    def share_password_check(self,passID,new_manager_email, iterations=0): #give manager as 1 or 0
        for password in self.__passwords:
            if password.get_passID() == str(passID):
                #get user info such as Name and public key
                user_info = pr.get_emails_sharing(server_public_key=self.__server_public_key,session_key=self.__session_key,requested_email=new_manager_email)
                if user_info in ["UNAUTHENTICATED","FAILED","KEY EXPIRED", "NO KEY"]:
                    if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                        return self.share_password_check(passID,new_manager_email,iterations=1)
                    else:
                        return "UNAUTHENTICATED"
                return user_info

    
    def share_password_confirm(self,passID,new_manager_email,manager, iterations=0): #give manager as 1 or 0
        for password in self.__passwords:
            if password.get_passID() == str(passID):
                user_info = pr.get_emails_sharing(server_public_key=self.__server_public_key,session_key=self.__session_key,requested_email=new_manager_email)
                if user_info in ["UNAUTHENTICATED","FAILED","KEY EXPIRED", "NO KEY"]:
                    if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                        return self.share_password_confirm(passID,new_manager_email,manager,iterations=1)
                    else:
                        return "UNAUTHENTICATED"
                recipient_UserID = user_info[0]
                data = password.share_password(client_email=self.__email,session_key=self.__session_key,server_public_key=self.__server_public_key,
                    recipient_userID=recipient_UserID,manager=manager,client_permanent_key=self.__client_permanent_key)
                return data
        
    
    def scan_passwords(self): #can't run as a function of password class because all passwords are required from cross evaluation
        if self.__scanned_passwords:
            return self.__scanned_passwords
        else:
            passwords_data = self.export_all()
            if passwords_data == "UNAUTHENTICATED": 
                return None
            else:
                passwords_data.sort(key=lambda x: x[5])
                password_list_of_dicts = []
                #[temp_PassID,password,password_key,additional_info,url,title,username] format of data returned from server
                for element in passwords_data:
                    if element[7] == 0:  #password not set to lockdown (shouldn't have been returned from server anyway)
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
        #download all passwords keys, decrypt using old password, then re-encrypt using new password
        for password in passwords:
            passID = password[0]
            password_key = password[2]
            new_password_key = Encrypt.encrypt_password_key(password_key, new_permanent_key)
            new_password_keys[passID] = new_password_key
        new_password_hash = Hash.create_hash(new_password.encode('utf-8'), salt_type=self.__email)
        data = pr.reset_client_password(self.__server_public_key,self.__session_key,self.__email,new_password_hash,self.__password,new_password_keys)
        if data in ["UNAUTHENTICATED","FAILED","KEY EXPIRED", "NO KEY"]:
            if iterations == 0 and self.__set_session_key() != "UNAUTHENTICATED":
                return self.reset_client_password(new_password,iterations=1)
        if data == "RESET PASSWORD":
            #will automatically logout after this
            #resave data if autologin is enabled
            login_data_is_saved = Application.attempt_get_saved_data()
            Application.delete_saved_login_data()
            if login_data_is_saved:
                Application.save_login_data(self.__email, new_password)
            return data
        