from backEnd.dbrequests import PyAnyWhereRequests as pr
from backEnd.encryption import Encrypt, Decrypt, Generate
from abc import ABC, abstractmethod
import random
import time

class PassInfo:
    def __init__(self, passID, title, manager, password, password_key, password_users, password_managers):
        self._passID = str(passID) #protected not private so can be accessed by child class
        self._title = title
        self._password_key = password_key
        self._password = password
        self._manager = manager
        self._lockdown = 0
        self._password_users = password_users
        self._password_managers = password_managers
        
    def get_summary(self):
        pass
    
    def get_passID(self):  
        return self._passID

    def get_manager(self):
        return self._manager

    
    def get_password(self,client_email=None,session_key=None,server_public_key=None,client_permanent_key=None):
        # checks if password is already downloaded so it doesn't need to be downloaded again
        if self._password:
            print("Full password already downloaded")
            return self._password
        else:
            print("Password doesn't exist in full, downloading")
            data = self._get_password_full(client_email=client_email,session_key=session_key,
                                           server_public_key=server_public_key,client_permanent_key=client_permanent_key)
            if data == "DOWNLOADED SUCCESSFULLY":
                return self._password
            else:
                return data   
            
    
    def get_password_key(self,client_email=None,session_key=None,server_public_key=None):
        if self._password_key:
            return self._password_key
        else:
            data = self._get_password_full(client_email=client_email,session_key=session_key,server_public_key=server_public_key)
            if data == "DOWNLOADED SUCCESSFULLY":
                return self._password_key
            elif data == "ERROR":
                return data 
    
    @abstractmethod
    def _get_password_full(self,client_email=None,session_key=None,server_public_key=None,client_permanent_key=None):
        pass
        
    # add additional functions
    def get_passID(self):
        return self._passID
    
    def delete_password(self,client_email,session_key,server_public_key):
        print("Deleting password...")
        if self._manager == 1: 
            data = pr.delete_password(server_public_key=server_public_key,session_key=session_key,client_email=client_email,passID=self._passID)
            return data
        else:
            return "Not manager"
        
        
    def delete_password_instance(self,client_email,new_manager_email,session_key,server_public_key):
        print("Deleting password instance...")
        data = pr.delete_password_instance(server_public_key=server_public_key,session_key=session_key,client_email=client_email,passID=self._passID,new_manager_email=new_manager_email)
        return data
        
    def set_to_lockdown(self,client_email,session_key,server_public_key):
        print("Setting to lockdown...")
        data = pr.set_to_lockdown(server_public_key=server_public_key,session_key=session_key,client_email=client_email,passID=self._passID)
        if data == "SET TO LOCKDOWN":
            self._lockdown = 1
        return data


    def add_manager(self,client_email,new_manager_email,session_key,server_public_key):
        print("Adding manager...")
        if self._manager == 1:
            data = pr.add_manager(server_public_key=server_public_key,session_key=session_key,client_email=client_email,passID=self._passID,new_manager_email=new_manager_email)
            return data
        else:
            print("Not manager")
            return "NOT MANAGER"     
        
    def get_password_users(self,client_email,session_key,server_public_key):
        if self._password_users:
            return self._password_users
        else:
            print("Getting password users...")
            if self._manager == 1:
                data = pr.get_password_users(server_public_key=server_public_key,session_key=session_key,client_email=client_email,passID=self._passID,manager_only=False)
                if data not in ["NOT MANAGER","UNAUTHENTICATED","KEY EXPIRED","NO KEY"]:
                    self._password_users = data
                return data
            else:
                print("Not manager")
                return "NOT MANAGER"
        
    def get_password_managers(self,client_email,session_key,server_public_key):
        if self._password_managers:
            return self._password_managers
        else:
            print("Getting password managers...")
            if self._manager == 1:
                data = pr.get_password_users(server_public_key=server_public_key,session_key=session_key,client_email=client_email,passID=self._passID,manager_only=True)
                if data not in ["NOT MANAGER","UNAUTHENTICATED","KEY EXPIRED","NO KEY"]:
                    self._password_managers = data
                return data
            else:
                print("Not manager")
                return "NOT MANAGER"

    def update_password(self,client_email,session_key,server_public_key,new_info,type):
        print("Updating password...")
        if self._manager == 1:
            if type == "Password":
                if self._password_key:
                    encrypted_password = Encrypt.encrypt_password(new_info,self._password_key)
                    data = pr.update_password(server_public_key=server_public_key,session_key=session_key,client_email=client_email,passID=self._passID,new_info=encrypted_password,type=type)
                else:
                    self._get_password_full(client_email=client_email,session_key=session_key,server_public_key=server_public_key)
                    return self.update_password(client_email,session_key,server_public_key,new_info,type)
            elif type in ["URL","Username","Title","AdditionalInfo"]:
                data = pr.update_password(server_public_key=server_public_key,session_key=session_key,client_email=client_email,passID=self._passID,new_info=new_info,type=type)
            return data 
        else:
            print("Not manager")
            return "NOT MANAGER"
        
    def share_password(self,client_email,session_key,server_public_key,recipient_userID,manager,client_permanent_key):
        # already confirmed and downloaded user details
        print("Sharing password...")
        if self._manager == 1:
            if self._password_key:
                public_key = pr.get_public_key(server_public_key=server_public_key,session_key=session_key,recipient_UserID=recipient_userID)
                e, n = public_key.split('-')
                print(f"public_key: {public_key}")
                if public_key not in ["NOT MANAGER","UNAUTHENTICATED","KEY EXPIRED","NO KEY"]:
                    symmetric_key = Generate.generate_symmetric_key(21) #returns only integers
                    encrypted_symmetric_key = Encrypt.encrypt_symmetric_key_sharing(symmetric_key,e,n)
                    while not Generate.validate_symmetric_key(encrypted_symmetric_key,200000):
                        symmetric_key = Generate.generate_symmetric_key(21)
                        encrypted_symmetric_key = Encrypt.encrypt_symmetric_key_sharing(symmetric_key,e,n)
                    print(f"encrypted_symmetric_key: {encrypted_symmetric_key}")
                    print(f"symmetric_key: {symmetric_key}")
                    print(f"password_key: {self._password_key}")
                    encrypted_password_key = Encrypt.encrypt_password_key_to_share(self._password_key, symmetric_key)
                    print(f"encrypted_password_key: {encrypted_password_key}")
                    data = pr.share_password(server_public_key=server_public_key,session_key=session_key,client_email=client_email,
                        passID=self._passID,password_key=encrypted_password_key,recipient_UserID=recipient_userID,
                        manager=manager,encrypted_sharing_symmetric_key=encrypted_symmetric_key
                    )
                    return data
            else:
                self._get_password_full(client_email=client_email,session_key=session_key,server_public_key=server_public_key,client_permanent_key=client_permanent_key)
                return self.share_password(client_email,session_key,server_public_key,recipient_userID,manager,client_permanent_key)
        else:
            print("Not manager")
            return "NOT MANAGER"
        
    def remove_password_user(self,client_email,session_key,server_public_key,user_email):
        print("Removing password user...")
        if self._manager == 1:
            if user_email == client_email:
                return "CANNOT REMOVE SELF"
            data = pr.remove_password_user(server_public_key,session_key,client_email,self._passID,user_email)
            return data

class Info(PassInfo):
    def __init__(self, passID, title, manager, password, password_key, password_users, password_managers):
        super().__init__(passID, title, manager, password, password_key, password_users, password_managers)
        
    def get_summary(self):
        if self._lockdown == 0:
            return [self._title,self._manager]
    
    def get_summary_inc_passID(self):
        if self._lockdown == 0:
            return [self._title, self._manager, self._passID]
    
    def _get_password_full(self,client_email=None,session_key=None,server_public_key=None,client_permanent_key=None):
        if self._password:
            return "DOWNLOADED SUCCESSFULLY"
        elif session_key and server_public_key:
            data = pr.get_password(server_public_key=server_public_key,session_key=session_key,client_email=client_email,passID=self._passID)
            if data in ["UNAUTHENTICATED","KEY EXPIRED","NO KEY","LOCKDOWN"]:
                return data
            else:
                encrypted_password = data[0]
                encrypted_password_key = data[2]
                decrypted_password_key = Decrypt.decrypt_password_key(encrypted_password_key,client_permanent_key)
                print(f"decrypted_password_key: {decrypted_password_key}")
                decrypted_password = Decrypt.decrypt_password(encrypted_password, decrypted_password_key)
                self._password = decrypted_password
                self._password_key = decrypted_password_key
                return "DOWNLOADED SUCCESSFULLY"   
        else:
            return "SESSION KEY REQUIRED"
    
    
class Password(PassInfo):
    def __init__(self, passID, title, url, username, manager, password, password_key, additional_info, password_users, password_managers):
        super().__init__(passID, title, manager, password, password_key, password_users, password_managers)
        self.__url = url
        self.__username = username
        self.__additional_info = additional_info

    def get_summary(self):
        if self._lockdown == 0:
            return [self._title, self.__username, self._manager, self.__url]
    
    def get_summary_inc_passID(self):
        if self._lockdown == 0:
            return [self._title, self.__username, self.__url, self._manager, self._passID]

    def get_url(self):
        return self.__url
    
    def get_username(self):
        return self.__username
        
    def get_additional_info(self):
        return self.__additional_info
    
    # also needs to create the additional_info attribute therefore polymorphism required
    def _get_password_full(self,client_email=None,session_key=None,server_public_key=None,client_permanent_key=None):
        if self._password:
            print("Already exists in full - missing passage")
            return "DOWNLOADED SUCCESSFULLY"
        else:
            print("Downloading...")
            data = pr.get_password(server_public_key=server_public_key,session_key=session_key,client_email=client_email,passID=self._passID)
            if data in ["UNAUTHENTICATED","KEY EXPIRED","NO KEY","LOCKDOWN"]:
                return data
            else:
                print("Data received, decrypting...")
                encrypted_password = data[0]
                encrypted_password_key = data[2]
                self.__additional_info = data[1]
                print(f"encrypted password_key: {encrypted_password_key}")
                print(f"client_permanent_key: {client_permanent_key}")
                print(f"encrypted_password: {encrypted_password}")
                decrypted_password_key = Decrypt.decrypt_password_key(encrypted_password_key,client_permanent_key)
                print(f"decrypted_password_key: {decrypted_password_key}")
                decrypted_password = Decrypt.decrypt_password(encrypted_password,decrypted_password_key)
                self._password = decrypted_password
                self._password_key = decrypted_password_key
                print("Data decrypted")
                return "DOWNLOADED SUCCESSFULLY"   
    
    