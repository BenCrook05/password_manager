from flet import *
from backEnd.loginlogic import Application
from pages.components.pro_ring import ProRing
import re
from assets.colours import Colours
BACKGROUND_COLOUR, THEME_COLOUR, TEXT_COLOUR, BACKGROUND_COLOUR_2= Colours().get_colours()

class Receivecode(UserControl):
    def __init__(self,page,data,email,type):
        super().__init__()
        self.__page = page
        self.__data = data
        self.__processing = False
        self.__email = email
        if type == "account":
            self.__function = self.__attempt_verify_account
        elif type == "device":
            self.__function = self.__attempt_add_device
        
    def __check_data(self, e):
        values = self.__code_input.value
        for value in values:
            if not re.match(r'^[0-9]+$', value):
                self.__code_input.value = self.__code_input.value.replace(value,"")
                self.__code_input.update()
        
    def __attempt_verify_account(self,e):
        if len(self.__code_input.value) == 6:
            self.__stack.controls.append(ProRing())
            
            self.__container_info.update()
            self.__stack.update()
            
            data = Application.validate_new_account(self.__email, self.__code_input.value, self.__data)
            print(data)
            if data not in ["UNAUTHENTICATED","ERROR","TOO MANY ATTEMPTS"]:
                self.__page.go('/Home')
            else:
                self.__page.snack_bar = SnackBar(
                    content=Text("Unauthenticated",color=TEXT_COLOUR),
                    bgcolor=BACKGROUND_COLOUR_2,
                    elevation=5,
                    margin=5,
                    duration=3000,
                )
                self.__page.snack_bar.open = True
                self.__data = {}
                self.__page.go('/')
                
        
    def __attempt_add_device(self,e):
        if len(self.__code_input.value) == 6:
            self.__stack.controls.append(ProRing())
            self.__container_info.update()
            self.__stack.update()
            
            data = Application.login_new_device_confirm(self.__email, self.__code_input.value, self.__data)
            print(data)
            if data not in ["UNAUTHENTICATED","ERROR","TOO MANY ATTEMPTS","INCORRECT CODE"]:
                self.__page.go('/Home')
            else:
                self.__page.snack_bar = SnackBar(
                    content=Text("Unauthenticated",color=TEXT_COLOUR),
                    bgcolor=BACKGROUND_COLOUR_2,
                    elevation=5,
                    margin=5,
                    duration=3000,
                )
                self.__page.snack_bar.open = True
                self.__data = {}
                self.__page.go('/')

    
    def __return_to_login(self,e):
        self.__page.go('/')
        self.__page.update()
    
    def build(self):
        self.__back_button = Container(
            padding=5,
            content=IconButton(icon = icons.ARROW_BACK_IOS_NEW_ROUNDED, on_click=self.__return_to_login)
        )
        self.__code_input = TextField(
            label="Enter code",
            width=300,
            bgcolor='transparent',
            border_color=TEXT_COLOUR,
            on_change=self.__check_data,
            content_padding=10,
            cursor_color = TEXT_COLOUR,
            max_length=6,
        )
        self.__send_code_button = ElevatedButton(
            icon = icons.SEND_ROUNDED,
            text="Confirm",
            width=200,
            elevation=10,
            on_click=self.__function
        )
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
                            Text(value="Enter Verification Code",size=23, weight=FontWeight.BOLD, color=TEXT_COLOUR),
                            Divider(height=5, color="transparent"),
                            Text(value=f"Verifcation code emailed to:\n{self.__email}", 
                                    size=13, color=TEXT_COLOUR),
                        ]
                    ),
                    Divider(height=10,color="transparent"),
                    self.__code_input,
                    Divider(height=10,color="transparent"),
                    self.__send_code_button,
                ]
            )
        )
        
        self.__stack = Stack(controls=[self.__container_info,self.__back_button])
        self.__card = Card(
            width=408,
            height=500,
            elevation=50,
            content=self.__stack
        )
        return self.__card