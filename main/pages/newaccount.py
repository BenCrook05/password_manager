from flet import *
from backEnd.loginlogic import Application
import time
from pages.components.inputs import Input, CountryInput
import re
from pages.receive_code import Receivecode
from pages.components.pro_ring import ProRing
from assets.colours import Colours
BACKGROUND_COLOUR, THEME_COLOUR, TEXT_COLOUR, BACKGROUND_COLOUR_2= Colours().get_colours()


class Newaccount(UserControl):
    def __init__(self,page,data):
        super().__init__()
        self.__page = page
        self.__data = data
        self.__processing = False

    def __try_again(self):
        self.__first_name_input.change_disabled()
        self.__last_name_input.change_disabled()
        self.__email_input.change_disabled()
        self.__date_of_birth_input.change_disabled()
        self.__phone_number_input.change_disabled()
        self.__country_input.change_disabled()
        self.__confirm_button.disabled = False
        self.__first_name_input.update()
        self.__last_name_input.update()
        self.__email_input.update()
        self.__date_of_birth_input.update()
        self.__phone_number_input.update()
        self.__country_input.update()
        
        self.__stack.controls.pop()
        self.__stack.update()
        self.__processing = False

    def __confirm_password(self,e):
        if self.__processing == False:
            self.__processing = True
            password = self.__password_input.get_value()
            confirm_password = self.__confirm_password_input.get_value()
            if password == confirm_password:
                if Application.check_password_is_suitable(password):
                    self.__stack.controls.append(ProRing())
                    self.__stack.update()
                    data = Application.create_new_account(self.__first_name,self.__last_name,self.__email,password,self.__date_of_birth,self.__phone_number,self.__country,self.__data)
                    if data == "CODE SENT":
                        self.__data["email"] = self.__email
                        self.__data["password"] = password
                        self.__stack.controls.clear()
                        self.__stack.controls.append(Receivecode(self.__page,self.__data,self.__email,"account"))
                        self.__stack.update()
                    elif data == "EMAIL ALREADY USED":
                        self.__page.snack_bar = SnackBar(
                            content=Text("Email already linked to an account",color=TEXT_COLOUR),
                            bgcolor=BACKGROUND_COLOUR_2,
                            elevation=5,
                            margin=5,
                            duration=3000,
                        )
                        self.__page.snack_bar.open = True
                        self.__data.empty()
                        self.__page.go('/')

                        self.__stack.controls.pop()
                        self.__stack.update()
                        self.__page.dialog = self.__dlg
                        self.__dlg.open = True
                        self.__page.update()
                    else:
                        self.__page.snack_bar = SnackBar(
                            content=Text("Failed to add account",color=TEXT_COLOUR),
                            bgcolor=BACKGROUND_COLOUR_2,
                            elevation=5,
                            margin=5,
                            duration=3000,
                        )
                        self.__page.snack_bar.open = True
                        self.__data.empty()
                        self.__page.go('/')
                else:
                    self.__password_input.set_error_text("")
                    self.__password_input.update()
                    time.sleep(1)
                    self.__password_input.set_error_text("Password not strong enough")
                    self.__password_input.set_value("")
                    self.__confirm_password_input.set_value("")
                    self.__password_input.update()
                    self.__confirm_password_input.update()
                    self.__stack.controls.pop()
            else:
                self.__password_input.set_error_text("")
                self.__password_input.update()
                time.sleep(1)
                self.__password_input.set_error_text("Passwords do not match")
                self.__password_input.set_value("")
                self.__confirm_password_input.set_value("")
                self.__password_input.update()
                self.__confirm_password_input.update()
                self.__stack.controls.pop()

    
    def __attempt_add_account(self,e):
        #check all data
        if self.__processing == False:
            self.__processing = True
            
            self.__first_name_input.change_disabled()
            self.__last_name_input.change_disabled()
            self.__email_input.change_disabled()
            self.__date_of_birth_input.change_disabled()
            self.__phone_number_input.change_disabled()
            self.__country_input.change_disabled()
            self.__confirm_button.disabled = True
            self.__first_name_input.update()
            self.__last_name_input.update()
            self.__email_input.update()
            self.__date_of_birth_input.update()
            self.__phone_number_input.update()
            self.__country_input.update()
            
            self.__stack.controls.append(ProRing())
           
            self.__container_info.update()
            self.__stack.update()
            
            self.__first_name = self.__first_name_input.get_value()
            self.__last_name = self.__last_name_input.get_value()
            self.__email = self.__email_input.get_value()
            self.__date_of_birth = self.__date_of_birth_input.get_value()
            self.__phone_number = self.__phone_number_input.get_value()
            self.__country = self.__country_input.get_value()
            
            failed = False
            if self.__first_name == "":
                self.__first_name_input.set_error_text("Required")
                failed = True
                
            if self.__last_name == "":
                self.__last_name_input.set_error_text("Required")
                failed = True
            if self.__email == "":
                self.__email_input.set_error_text("Required")
                failed = True
            if self.__date_of_birth == "":
                self.__date_of_birth_input.set_error_text("Required")
                failed = True
            if self.__phone_number == "":
                self.__phone_number_input.set_error_text("Required")
                failed = True
            if self.__country == "":
                self.__country_input.set_error_text("Required")
                failed = True
            
            if failed:
                self.__try_again()
                return
            
            valid_email = re.search(r'\A[\d|a-z]\w*@[\d|a-z]\w*(.[a-z]{2,3}){1,2}\Z',self.__email.lower())    
            if not valid_email:
                self.__email_input.set_error_text("Invalid Email")
                failed = True
            valid_date_of_birth = re.search(r'\d{2}-\d{2}-\d{4}',self.__date_of_birth)
            if not valid_date_of_birth:
                self.__date_of_birth_input.set_error_text("Date format must be dd-mm-yyyy")
                failed = True
            valid_phone_number = re.search(r'[\+\d{1,2}]?\d{10,12}',self.__phone_number)
            if not valid_phone_number:
                self.__phone_number_input.set_error_text("Invalid Phone Number")
                failed = True
            
            if failed:
                self.__try_again()
                return
            
            self.__password_input = Input("LOCK_OPEN_ROUNDED","Password",True,reveal_option=True,max_length=64)
            self.__confirm_password_input = Input("LOCK_OPEN_ROUNDED","Re-enter Password",True,reveal_option=True,max_length=64)
            self.__confirm_button_passwords = ElevatedButton(
                icon = icons.PERSON_ADD_ALT_1_ROUNDED,
                text="Confirm",
                width=200,
                elevation=10,
                on_click=self.__confirm_password
            )
            self.__container_passwords = Container(
                padding=30,
                bgcolor=BACKGROUND_COLOUR,
                blur=0,
                border_radius=10,
                content=Column(
                    horizontal_alignment=CrossAxisAlignment.CENTER,
                    controls=[
                        Row(
                            controls=[
                                IconButton(icon=icons.BACK_ROUNDED, on_click=lambda: self.__page.go('/Newaccount')),
                                VerticalDivider(width=10, color="transparent"),
                            ],
                            alignment=MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=CrossAxisAlignment.CENTER,  
                        ),
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
                                Text(value="Create a Password",size=23, weight=FontWeight.BOLD, color=BACKGROUND_COLOUR),
                                Divider(height=5, color="transparent"),
                                Text(value=f"You won't ever be able to reset this password,\nso make sure you remember it!", 
                                        size=13, color=BACKGROUND_COLOUR),
                            ]
                        ),
                        Divider(height=10,color="transparent"),
                        self.__password_input,
                        Divider(height=10,color="transparent"),
                        self.__confirm_password_input,
                        Divider(height=10,color="transparent"),
                        self.__confirm_button_passwords,
                    ]
                )
            )
            self.__stack.controls.clear()
            self.__stack.controls.append(self.__container_passwords)
            self.__stack.update()
            self.__processing = False

    def build(self):
        self.__back_button = Container(
            padding=5,
            content=IconButton(icon = icons.ARROW_BACK_IOS_NEW_ROUNDED, on_click=lambda _: self.__page.go('/'))
        )
        self.__first_name_input = Input("PERSON_ROUNDED","First Name",focus=True)
        self.__last_name_input = Input("PERSON_ROUNDED","Other Names")
        self.__email_input = Input("EMAIL_ROUNDED","Email",max_length=64)
        self.__date_of_birth_input = Input("DATE_RANGE_ROUNDED","Date of Birth")
        self.__phone_number_input = Input("LOCAL_PHONE_ROUNDED","Phone Number")
        self.__country_input = CountryInput()
 
        
        self.__confirm_button = ElevatedButton(
            icon = icons.PERSON_ADD_ALT_1_ROUNDED,
            text="Confirm",
            width=200,
            elevation=10,
            on_click=self.__attempt_add_account
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
                                r"gui\assets\Images\png\logo-no-background.png", #need to use raw string to avoid syntax warning
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
                            Text(value="Create New Account",size=23, weight=FontWeight.BOLD, color=TEXT_COLOUR),
                            Divider(height=5, color="transparent"),
                            Text(value="Sign up for a new SecureNet account", 
                                    size=13, color=TEXT_COLOUR),
                        ]
                    ),
                    Divider(height=5,color="transparent"),
                    self.__first_name_input,
                    Divider(height=4, color="transparent"),
                    self.__last_name_input,
                    Divider(height=4, color="transparent"),
                    self.__email_input,
                    Divider(height=4, color="transparent"),
                    self.__date_of_birth_input,
                    Divider(height=4, color="transparent"),
                    self.__phone_number_input,
                    Divider(height=4, color="transparent"),
                    self.__country_input,
                    Divider(height=4, color="transparent"),
                    self.__confirm_button,
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