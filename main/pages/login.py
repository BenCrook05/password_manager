from flet import *
from backEnd.loginlogic import Application
import sqlite3
from cryptography.fernet import Fernet
from pages.components.inputs import Input
from pages.components.pro_ring import ProRing
from backEnd.encryption import Generate
from assets.colours import Colours
BACKGROUND_COLOUR, THEME_COLOUR, TEXT_COLOUR, BACKGROUND_COLOUR_2= Colours().get_colours()
import traceback
import socket
from datetime import datetime

class Login(UserControl):
    def __init__(self,page,data):
        super().__init__()
        self.__page = page
        self.__data = data
        self.__processing = False
    

    def attempt_auto_login(self):
        self.__stack.controls.append(ProRing())
        self.__stack.update()
        saved_data = Application.attempt_get_saved_data()
        try:
            if saved_data:
                print(f"saved data: {saved_data}")
                email, password = saved_data
                self.__stack.controls.pop()
                self.__stack.update()
                
                self.__stay_signed_in.value = True
                self.__email_input.set_value(email)
                self.__password_input.set_value(password)
                
                self.__stay_signed_in.update()
                self.__email_input.update()
                self.__password_input.update()
                
                self.__stack.controls.append(ProRing())
                self.__stack.update()
                data = Application.login(email, password, self.__data)
                if data in ["UNAUTHENTICATED","ERROR","TOO MANY ATTEMPTS"]:
                    raise ValueError
                
                self.__data["email"] = email
                self.__data["password"] = password
                self.__data["session_key"] = data

                self.__page.go('/Home')
            else:
                self.__data["server_public_key"] = Application.get_server_key()
                self.__data["server_key_day"] = datetime.now().day
                raise ValueError
            
        except Exception as e:
            self.__stay_signed_in.value = False    
            self.__email_input.set_value("")
            self.__password_input.set_value("")
            
            self.__stay_signed_in.update()
            self.__email_input.update()
            self.__password_input.update()
            
            self.__stack.controls.pop()
            self.__stack.update()

    def __add_account(self,e):
        self.__page.go('/Newaccount')
        
    def __add_device(self,e):
        self.__page.go('/Newdevice')
    
    def __attempt_login(self,e):
        if self.__processing == False:
            self.__processing = True
            
            self.__email_input.change_disabled()
            self.__password_input.change_disabled()
     
            self.__sign_in_button.disabled = True
            self.__email_input.update()
            self.__password_input.update()
            self.__sign_in_button.update()
            
            email = self.__email_input.get_value()
            password = self.__password_input.get_value()
            
            self.__stack.controls.append(ProRing())
            self.__container_info.update()
            self.__stack.update()
            data = Application.login(email, password, self.__data)
            if data not in ["UNAUTHENTICATED","ERROR","TOO MANY ATTEMPTS"]:
                ### successful logging in due to no error
                #update data dictionary
                if len(data) == 64:  #definitely a session key
                    self.__data["email"] = email
                    self.__data["password"] = password
                    self.__data["session_key"] = data
                    self.__page.update()
                    
                    if self.__stay_signed_in.value:
                        Application.save_login_data(email,password)
                    else:
                        try:
                            Application.delete_saved_login_data()
                        except:
                            pass
                    self.__page.go('/Home')
            else:
                if data == "TOO MANY ATTEMPTS":
                    self.__login_success.value = "Account associated with this email\nhas been locked for 1 hour"
                else:
                    self.__login_success.value = "Incorrect Email or Password"
                try:
                    Application.delete_saved_login_data()
                except Exception as e:
                    pass
                
                self.__email_input.change_disabled()
                self.__password_input.change_disabled()
                self.__sign_in_button.disabled = False
                self.__email_input.update()
                self.__password_input.update()
                self.__sign_in_button.update()
                self.__password_input.set_value("")
                self.__password_input.update()
                self.__login_success.update()
                self.__container_info.update()
                
                self.__stack.controls.pop()
                self.__stack.update()
        
                self.__processing = False

    def build(self):
        self.__email_input = Input("PERSON_ROUNDED","Email",focus=True,max_length=64)
        self.__password_input = Input("LOCK_OPEN_ROUNDED","Password",True,reveal_option=True,max_length=64)
        self.__stay_signed_in = Checkbox(label="Stay signed in on this device?",value=False)
        self.__sign_in_button = ElevatedButton(
            icon = icons.LOGIN_ROUNDED,
            text="Sign In",
            width=200,
            elevation=10,
            on_click=self.__attempt_login
        )
        self.__login_success = Text(value="", color="red", size=13)
        self.__container_info = Container(
            padding=30,
            blur=0,
            border_radius=10,
            bgcolor=BACKGROUND_COLOUR_2,
            content=Column(
                horizontal_alignment=CrossAxisAlignment.CENTER,
                controls=[
                    Divider(height=20, color="transparent"),
                    Column(
                        controls=[
                            Image(
                                r"assets\Images\png\logo-no-background.png", #need to use raw string to avoid syntax warning
                                width=300, 
                                fit=ImageFit.CONTAIN,
                            )
                        ]
                    ),
                    Divider(height=20, color="transparent"),
                    Column(
                        alignment=MainAxisAlignment.CENTER,
                        horizontal_alignment=CrossAxisAlignment.CENTER,
                        spacing=5,
                        controls = [
                            Text(value="Sign In",size=23, weight=FontWeight.BOLD, color=TEXT_COLOUR),
                            Divider(height=5, color="transparent"),
                            Text(value="Sign into a Pre-Existing Account on this Device", 
                                    size=13, color=TEXT_COLOUR),
                        ]
                    ),
                    Divider(height=10,color="transparent"),
                    self.__login_success,
                    Divider(height=5,color="transparent"),
                    self.__email_input,
                    Divider(height=4, color="transparent"),
                    self.__password_input,
                    Divider(height=5, color="transparent"),
                    self.__sign_in_button,
                    Divider(height=2, color="transparent"),
                    self.__stay_signed_in,
                    Divider(height=5, color="transparent"),
                    Column(
                        alignment=MainAxisAlignment.CENTER,
                        horizontal_alignment=CrossAxisAlignment.CENTER,
                        controls=[
                            Text(value="Or"),
                        ]
                    ),
                    Divider(height=2, color="transparent"),
                    ElevatedButton(
                        icon=icons.COMPUTER_ROUNDED,
                        text="Verify Device",
                        width=200,
                        elevation=10,
                        on_click=self.__add_device,
                    ),
                   
                    Divider(height=2, color="transparent"),
                    ElevatedButton(
                        icon=icons.PERSON_ADD_ALT_1_ROUNDED,
                        text="Create Account",
                        width=200,
                        elevation=10,
                        on_click=self.__add_account,
                    )  
                ]
            )
        )
        self.__stack = Stack(controls=[self.__container_info])
        self.__card = Card(
            width=408,
            elevation=50,
            content=self.__stack
        )
        return self.__card