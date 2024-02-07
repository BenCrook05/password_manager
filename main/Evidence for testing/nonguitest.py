from backEnd.loginlogic import Application
from backEnd.basemanager import Manager
from datetime import date, datetime, timedelta
from backEnd.dbrequests import PyAnyWhereRequests as pr


#testing
pm = Application()
#forename,names,email,password,date_of_birth,phone_number,country
choice = input("Login or create new account? (login:l/create:c/login_new_device:n): ")
if choice == "reset":
    pr.reset()
    quit()
if choice == "ben":
    data = pm.create_new_account("Ben","Crook","crookbenj@gmail.com","password","09-12-2005","07754150325","UK")
    email = "crookbenj@gmail.com"
    if data == "CODE SENT":
        code = input("Enter code: ")
        data=pm.validate_new_account(email,code)
        print(data)
    else:
        print(data)
if choice == "l":
    email = input("Enter email: ")
    password = input("Enter password: ")
    data =pm.login(email,password)
    print(data)
elif choice == "c":
    forename = input("Enter forename: ")
    names = input("Enter names: ")
    email = input("Enter email: ")
    password = input("Enter password: ")
    date_of_birth = input("Enter date of birth: ")
    phone_number = input("Enter phone number: ")
    country = input("Enter country: ")
    data = pm.create_new_account(forename, names, email, password, date_of_birth, phone_number, country)
    if data == "CODE SENT":
        code = input("Enter code: ")
        data = (pm.validate_new_account(email,code))
        print(data)
    else:
        print(data)
elif choice == "n":
    email = input("Enter email: ")
    password = input("Enter password: ")
    data = pm.login_new_device_request(email,password)
    if data == "CODE SENT":
        code = input("Enter code: ")
        data = pm.login_new_device_confirm(email,code)
        print(data)
    else:
        print(data)
del pm
if data != "UNAUTHENTICATED":
    m = Manager(email,password)
    #("crookbenj@gmail.com","password1234")
    i = input("Enter action: ")
    while i != "end":
        
        if i == "import":
            print(m.import_passwords())
            
        elif i == "add":
            title = input("Enter title: ")
            url = input("Enter url: ")
            username = input("Enter username: ")
            if username == "":
                username = None
            elif username == "email":
                username = "crookbenj@gmail.com"
            additional_info = input("Enter additional info: ")
            password = input("Enter password: ")
            print(m.add_new_password(title,url,username,additional_info,password))
            
        elif i == "get":
            passID = input("Enter passID: ")
            print(m.get_specific_password_info(passID))
            
        elif i == "getpass":
            print(m.get_passwords())
            
        elif i == "getinfo":
            print(m.get_infos())
            
        elif i == "getall":
            print(m.get_all())
            
        elif i == "delete":
            passID = input("Enter passID: ")
            decision = input("Delete entire password or just this instance? (entire:e/instance:i): ")
            if decision == "e":
                print(m.delete_password(passID))
            elif decision == "i":
                data = m.delete_password_instance(passID)
                if data == "New manager email required":
                    print(data)
                    new_manager_email = input("Enter new manager email: ")
                    print(m.delete_password_instance(passID,new_manager_email))

        elif i == "update":
            passID = input("Enter passID: ")
            title = input("Enter title: ")
            url = input("Enter url: ")
            username = input("Enter username: ")  
            additional_info = input("Enter additional info: ")
            password = input("Enter password: ")
            if title:
                print(m.update_password(passID,title,"Title"))
            if url:
                print(m.update_password(passID,url,"URL"))
            if username:
                print(m.update_password(passID,username,"Username"))
            if additional_info:
                print(m.update_password(passID,additional_info,"AdditionalInfo"))
            if password:
                print(m.update_password(passID,password,"Password"))
            
        elif i == "share":
            passID = input("Enter passID: ")
            email = input("Enter email: ")
            manager = input("Manager? (1/0): ")
            print(m.share_password_check(passID,email,int(manager))) 
            confirm = input("Confirm? (y/n): ")
            if confirm == "y":
                print(m.share_password_confirm(passID,email,int(manager)))
            else:
                print("Cancelled")
        
        elif i == "get shared":
            data = m.get_pending_shares()
            if data == "NO PENDING PASSWORDS":
                print("No pending passwords")
            else:
                for password in data:
                    print(password)
                    confirm_download = input("Confirm download? (y/n): ")
                    if confirm_download == "y":
                        passID = password[0]
                        print(m.accept_pending_share(passID))
                print("All pending passwords downloaded")
                
                
        
        i = input("Enter action: ")
else:
    print("Login failed")
    quit()