import requests
import json
import traceback
import time

class UserTest():
    def __init__(self, forename,names,client_email,password_hash,date_of_birth,phone_number,country,permanent_public_key,mac_address_hash):
        self.forename = forename
        self.names = names
        self.client_email = client_email
        self.password_hash = password_hash
        self.date_of_birth = date_of_birth
        self.phone_number = phone_number
        self.country = country
        self.permanent_public_key = permanent_public_key
        self.mac_address_hash = mac_address_hash
        self.server_key = self.__get_server_key()
        self.session_key = ""
        
    #DONE
    def __get_server_key(self):
        print("Getting Server Key")
        return_json = DBRequests.send_request("get_server_key")
        print(f"Error: {return_json['error']}")
        print(f"Data: {return_json['data']}")
        return return_json["data"]

    #DONE
    def add_user_to_database(self):
        print("Adding User")
        return_json = DBRequests.send_request("add_new_user",[self.forename,self.names,self.client_email,self.password_hash,self.date_of_birth,self.phone_number,self.country,self.permanent_public_key,self.mac_address_hash])
        print(f"Error: {return_json['error']}")
        print(f"Data: {return_json['data']}")
       
    #DONE 
    def add_new_device_request(self, new_mac_address):
        print("Entering New Device")
        return_json = DBRequests.send_request("add_new_device",[self.client_email,new_mac_address,self.password_hash])
        print(f"Error: {return_json['error']}")
        print(f"Data: {return_json['data']}")
        print("Request made - check inbox")
        code = input("Enter validation code: ")
        print("Confirming Device")
        return_json = DBRequests.send_request("confirm_device_code",[self.client_email,new_mac_address,code])
        print(f"Error: {return_json['error']}")
        print(f"Data: {return_json['data']}")

    #DONE
    def authenticate_password(self):
        print("Authenticating Password hash")
        return_json = DBRequests.send_request("authenticate_password",[self.client_email,self.mac_address_hash,self.password_hash])
        print(f"Error: {return_json['error']}")
        print(f"Data: {return_json['data']}")

    #DONE
    def get_session_key(self):
        print("Getting Session Key")
        return_json = DBRequests.send_request("authenticate_password",[self.client_email,self.mac_address_hash,self.password_hash])
        #print(return_json)
        print(f"Error: {return_json['error']}")
        print(f"Data: {return_json['data']}")
        return return_json["data"]

    #DONE
    def authenticate_password_newmac(self, new_ma_hash):
        print("Authenticating with new mac address")
        return_json = DBRequests.send_request("authenticate_password",[self.client_email,new_ma_hash,self.password_hash])
        print(f"Error: {return_json['error']}")
        print(f"Data: {return_json['data']}")

    #DONE
    def get_password_overview(self):
        print("Getting passwords overview")
        return_json = DBRequests.send_request("get_password_overview",[self.session_key])
        print(f"Error: {return_json['error']}")
        print(f"Data: {return_json['data']}")
    
    #DONE
    def get_password(self, url):
        print("Getting passwords")
        return_json = DBRequests.send_request("get_password",[self.session_key,self.client_email,url])
        print(f"Error: {return_json['error']}")
        print(f"Data: {return_json['data']}")

    def set_to_lockdown(self, url):
        print("Setting Password to Lockdown")
        return_json = DBRequests.send_request("set_to_lockdown",[self.session_key,self.client_email,url])
        print(f"Error: {return_json['error']}")
        print(f"Data: {return_json['data']}")

    def add_new_password(self, password, title, url, username, additional_info, password_key):
        print("Adding new password")
        return_json = DBRequests.send_request("add_new_password",[self.session_key,self.client_email,password,title,url,username,additional_info,password_key])
        print(f"Error: {return_json['error']}")
        print(f"Data: {return_json['data']}")

    def get_all_passwords(self):
        print("Getting all passwords")
        return_json = DBRequests.send_request("get_all_passwords",[self.session_key,self.client_email])
        print(f"Error: {return_json['error']}")
        print(f"Data: {return_json['data']}")
    
    def delete_password(self, url):
        print("Deleting password")
        return_json = DBRequests.send_request("delete_password",[self.session_key,self.client_email,url])
        print(f"Error: {return_json['error']}")
        print(f"Data: {return_json['data']}")

    def add_manager(self, new_manager_email, url):
        print("Adding new manager")
        return_json = DBRequests.send_request("add_manager",[self.session_key,self.client_email,new_manager_email,url])
        print(f"Error: {return_json['error']}")
        print(f"Data: {return_json['data']}")

    def get_password_users(self, url):
        print("Getting password users")
        return_json = DBRequests.send_request("get_password_users",[self.session_key,self.client_email,url])
        print(f"Error: {return_json['error']}")
        print(f"Data: {return_json['data']}")
        
    def delete_password_instance(self, url, new_manager_email):
        print("Deleting password instance")
        return_json = DBRequests.send_request("delete_password_instance",[self.session_key,self.client_email,url,new_manager_email])
        print(f"Error: {return_json['error']}")
        print(f"Data: {return_json['data']}")

    def update_password(self, url, password):
        print("Updating password")
        return_json = DBRequests.send_request("update_password",[self.session_key,self.client_email,url,password])
        print(f"Error: {return_json['error']}")
        print(f"Data: {return_json['data']}")

    def get_pending_passwordkeys(self):
        print("Getting pending password keys")
        return_json = DBRequests.send_request("get_pending_passwordkeys",[self.session_key,self.client_email])
        print(f"Error: {return_json['error']}")
        print(f"Data: {return_json['data']}")

    def get_emails_sharing(self, email):
        print("Getting emails sharing")
        return_json = DBRequests.send_request("get_emails_sharing",[self.session_key,email])
        print(f"Error: {return_json['error']}")
        print(f"Data: {return_json['data']}")

    def share_password(self, passID, password_key, recipient_UserID, manager):
        print("Sharing password")
        return_json = DBRequests.send_request("share_password",[self.session_key,self.client_email,passID,password_key,recipient_UserID,manager])
        print(f"Error: {return_json['error']}")
        print(f"Data: {return_json['data']}")

    def insert_pending_keys(self, password_key, manager):
        print("Inserting pending keys")
        return_json = DBRequests.send_request("insert_pending_keys",[self.session_key,self.client_email,password_key,manager])
        print(f"Error: {return_json['error']}")
        print(f"Data: {return_json['data']}")
    
    def get_public_key(self, recipient_UserID):
        print("Getting public key")
        return_json = DBRequests.send_request("get_public_key",[self.session_key,recipient_UserID])
        print(f"Error: {return_json['error']}")
        print(f"Data: {return_json['data']}")

    def reset_client_sharing_key(self, new_public_key):
        print("Resetting client sharing key")
        return_json = DBRequests.send_request("reset_client_sharing_key",[self.session_key,self.client_email,new_public_key])
        print(f"Error: {return_json['error']}")
        print(f"Data: {return_json['data']}")

    def get_server_key(self):
        print("Getting server key")
        return_json = DBRequests.send_request("get_server_key")
        print(f"Error: {return_json['error']}")
        print(f"Data: {return_json['data']}")

    def get_password_keys(self):
        print("Getting password keys")
        return_json = DBRequests.send_request("get_password_keys",[self.session_key,self.client_email])
        print(f"Error: {return_json['error']}")
        print(f"Data: {return_json['data']}")
    


class DBRequests():
    def send_request(request_header, data=[], client_public_key=""):
        url = "https://BenCrook.eu.pythonanywhere.com/post_endpoint"
        dic_to_send = {}
        dic_to_send["request_header"]=request_header
        dic_to_send["client_public_key"]=client_public_key
        dic_to_send["request_data"]=data
        try:
            response = requests.post(url,json=dic_to_send) 
            response_data = response.json()       
            return response_data
        except Exception as e:
            return traceback.format_exc()
def reset():
    print("Resetting Database")
    request_header = "reset"
    DBRequests.send_request(request_header)

reset()
# forename,names,client_email,password_hash,date_of_birth,phone_number,country,permanent_public_key,mac_address_hash

Ben1 = UserTest("Ben","Crook","crookbenj@gmail.com","abcdefh","09-12-2005","07754 150325","UK","123456789","macaddress1234")
Ben1.add_user_to_database()
Ben1.session_key = Ben1.get_session_key()
Ben1.add_new_password("password123","Amazon","amazon.co.uk","crookbenj@gmail.com","NO INFO","passwordkey123")
Ben1.add_new_password("password123","Argos","argos.co.uk","crookbenj@gmail.com","NO INFO","password3key12345")
Ben1.add_new_password("password123","Apple","apple.co.uk","crookbenj@gmail.com","NO INFO","pa3")

Ben1.set_to_lockdown("amazon.co.uk")
Ben1.delete_password_instance("apple.co.uk")

Ben1.get_password_overview()

Ben1.get_all_passwords()
