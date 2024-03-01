from flet import *
from backEnd.loginlogic import Application
import time
from pages.components.inputs import Input
from pages.receive_code import Receivecode
from pages.components.pro_ring import ProRing
from assets.colours import Colours
BACKGROUND_COLOUR, THEME_COLOUR, TEXT_COLOUR, BACKGROUND_COLOUR_2= Colours().get_colours()




class Newdevice(UserControl):
    def __init__(self,page,data):
        super().__init__()
        self.__page = page
        self.__data = data
        self.__processing = False
        self.__back_button = IconButton()
        self.__email_input = Input()
        self.__password_input = Input()
        self.__send_code_button = ElevatedButton()
        self.__login_success = Text()
        self.__container_info = Container()
        self.__stack = Stack()
        self.__card = Card()
    
    def __return_to_login(self,e):
        self.__page.go('/')
        


    def __attempt_add_device(self,e):
        if self.__processing == False:
            self.__processing = True
            
            self.__email_input.change_disabled()
            self.__password_input.change_disabled()
            self.__send_code_button.disabled = True
            self.__email_input.update()
            self.__password_input.update()
            self.__send_code_button.update()
            
            email = self.__email_input.get_value()
            password = self.__password_input.get_value()
            
            self.__stack.controls.append(ProRing())
   
            self.__container_info.update()
            self.__stack.update()
            
            data = Application.login_new_device_request(email, password, self.__data)
            if data == "CODE SENT":
                self.__data["email"] = email
                self.__data["password"] = password
                self.__stack.controls.clear()
                self.__stack.update()
                self.__stack.controls.append(
                    Receivecode(self.__page,self.__data,email,"device")
                )
                self.__stack.update()
                
            elif data == "DEVICE ALREADY USED":
                self.__page.snack_bar = SnackBar(
                    content=Text("Device is already verified",color=TEXT_COLOUR),
                    bgcolor=BACKGROUND_COLOUR_2,
                    elevation=5,
                    margin=5,
                    duration=3000,
                )
                self.__page.snack_bar.open = True
                #device already used so user can just login using normal login page
                self.__page.go('/')
                self.__page.update()
                
            else:
                self.__email_input.change_disabled()
                self.__password_input.change_disabled()
                self.__send_code_button.disabled = False
                self.__email_input.update()
                self.__password_input.update()
                self.__send_code_button.update()
                self.__login_success.value = "Incorrect Email or Password"
                self.__login_success.update()
                self.__password_input.set_value("")
                self.__password_input.update()
                self.__stack.controls.pop()
                self.__stack.update()
                self.__container_info.update()
                self.__processing = False
                
                

    def build(self):
        self.__back_button = Container(
            padding=5,
            content=IconButton(icon = icons.ARROW_BACK_IOS_NEW_ROUNDED, on_click=self.__return_to_login)
        )
        self.__email_input = Input("PERSON_ROUNDED","Email",focus=True)
        self.__password_input = Input("LOCK_OPEN_ROUNDED","Password",True,reveal_option=True)
        self.__send_code_button = ElevatedButton(
            icon = icons.SEND_ROUNDED,
            text="Send Code",
            width=200,
            elevation=10,
            on_click=self.__attempt_add_device
        )
        self.__login_success = Text(value="", color="red", size=13)
        self.__container_info = Container(
            padding=30,
            bgcolor=BACKGROUND_COLOUR_2,
            blur=0,
            border_radius=10,
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
                            Text(value="Verify Device",size=23, weight=FontWeight.BOLD, color=TEXT_COLOUR),
                            Divider(height=5, color="transparent"),
                            Text(value="Sign into a pre-existing account from a new device", 
                                    size=13, color=TEXT_COLOUR),
                        ]
                    ),
                    Divider(height=10,color="transparent"),
                    self.__login_success,
                    Divider(height=5,color="transparent"),
                    self.__email_input,
                    Divider(height=4, color="transparent"),
                    self.__password_input,
                    Divider(height=10, color="transparent"),
                    self.__send_code_button,
                    Divider(height=5, color="transparent"),
                ]
            )
        )
        self.__stack = Stack(controls=[self.__container_info,self.__back_button])
        self.__card = Card(
            width=408,
            elevation=50,
            content=self.__stack
        )
        return self.__card