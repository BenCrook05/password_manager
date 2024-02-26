from flet import *
import sqlite3
import socket
from pages.components.pro_ring import ProRing
from assets.colours import Colours
from pages.components.inputs import Input
from backEnd.loginlogic import Application
BACKGROUND_COLOUR, THEME_COLOUR, TEXT_COLOUR, BACKGROUND_COLOUR_2= Colours().get_colours()


class Settings(UserControl):
    def __init__(self, homepage, data):
        super().__init__()
        self.__homepage = homepage
        self.__data = data
        self.__processing = False
        
    def __back(self,e):
        self.__homepage.get_navrail().set_selected_index(0)
        self.__homepage.get_navrail().get_nav().update()
        self.__homepage.destination_change(None)
        
    def __change_theme(self,e):
        if not self.__processing:
            self.__processing = True
            self.__stack.controls.append(ProRing())
            self.__stack.update()   
            
            if self.__thememode_switch.value != self.__start_mode:
                if self.__thememode_switch.value:
                    Colours().set_dark_mode()
                else:
                    Colours().set_light_mode()
        
            self.__stack.controls.pop()
            self.__stack.update()
            self.__processing = False

        
    def __remove_lockdown(self,e):
        if not self.__processing:
            self.__processing = True
            self.__stack.controls.append(ProRing())
            self.__stack.update()   
            
             
            if self.__lockdown_switch.value:
                result = self.__homepage.get_manager().remove_all_locked_down_passwords()
                if result == "Failed":
                    self.__homepage.get_page().snack_bar = SnackBar(
                        content=Text(f"Failed to remove lockdown",color=TEXT_COLOUR),
                        bgcolor=BACKGROUND_COLOUR_2,
                        elevation=5,
                        margin=5,
                        duration=3000,
                    )
                    self.__homepage.get_page().snack_bar.open = True
                    self.__homepage.get_page().update()
                    
                elif result == "No lockdown":
                    self.__homepage.get_page().snack_bar = SnackBar(
                        content=Text("No passwords in lockdown",color=TEXT_COLOUR),
                        bgcolor=BACKGROUND_COLOUR_2,
                        elevation=5,
                        margin=5,
                        duration=3000,
                    )
                    self.__homepage.get_page().snack_bar.open = True
                    self.__homepage.get_page().update()

            self.__homepage.get_navrail().set_selected_index(0)
            self.__homepage.get_navrail().get_nav().update()
            self.__homepage.refresh()
            
    def __change_password(self,e):
        if not self.__processing:
            self.__processing = True
            self.__stack.controls.append(ProRing())
            self.__stack.update()               
            current_password_value = self.__current_password_input.get_value()
            new_password_value = self.__new_password_input.get_value()
            if self.__homepage.get_manager().validate_client_password(current_password_value):
                #checks password is strong enough before changing
                if new_password_value != "" and Application.check_password_is_suitable(new_password_value):
                    data = self.__homepage.get_manager().reset_client_password(new_password_value)
                    if data == "RESET PASSWORD":
                        self.__homepage.get_page().snack_bar = SnackBar(
                            content=Text("Password reset, please login again using your new password",color=TEXT_COLOUR),
                            bgcolor=BACKGROUND_COLOUR_2,
                            elevation=5,
                            margin=5,
                            duration=3000,
                        )
                        self.__homepage.get_page().snack_bar.open = True
                        self.__homepage.get_page().update()
                        #logout at this point to reset the password fully and reset sharing keys
                        self.__homepage.get_page().go('/')
                else:
                    self.__homepage.get_page().snack_bar = SnackBar(
                        content=Text("Please enter a suitably strong new password",color=TEXT_COLOUR),
                        bgcolor=BACKGROUND_COLOUR_2,
                        elevation=5,
                        margin=5,
                        duration=3000,
                    )
                    self.__homepage.get_page().snack_bar.open = True
                    self.__homepage.get_page().update()
                
            elif not (self.__homepage.get_manager().validate_client_password(self.__current_password_input.get_value())) and self.__current_password_input.get_value() != "":
                self.__homepage.get_page().snack_bar = SnackBar(
                    content=Text("Incorrect current password",color=TEXT_COLOUR),
                    bgcolor=BACKGROUND_COLOUR_2,
                    elevation=5,
                    margin=5,
                    duration=3000,
                )
                self.__homepage.get_page().snack_bar.open = True
                self.__homepage.get_page().update()
                #incorrect password, so log out as security measure
                self.__homepage.logout()
                
            else:         
                self.__homepage.get_page().snack_bar = SnackBar(
                    content=Text("Please enter a new password",color=TEXT_COLOUR),
                    bgcolor=BACKGROUND_COLOUR_2,
                    elevation=5,
                    margin=5,
                    duration=3000,
                )
                self.__homepage.get_page().snack_bar.open = True
                self.__homepage.get_page().update()
            try: #could fail if already redirected to login page
                self.__stack.controls.pop()
                self.__stack.update()
                self.__processing = False
            except:
                pass
    
    def build(self):
        self.__back_button = IconButton(icon=icons.ARROW_BACK,on_click=self.__back)
        self.__thememode_switch = Switch(
            value=True if Colours().get_theme() == ThemeMode.DARK else False,
            label="Dark Mode",
            on_change=self.__change_theme,
        )
        self.__current_password_input = Input(
            icon_name=icons.PERSON,
            hint="Current Password",
            hide=True,
            reveal_option=True,
        )
        self.__new_password_input = Input(
            icon_name=icons.PERSON,
            hint="New Password",
            hide=True,
            reveal_option=True,
        )
        
        thememode = Colours().get_theme()
        if thememode == ThemeMode.LIGHT:
            self.__start_mode = False
            self.__thememode_switch.value = False
        elif thememode == ThemeMode.DARK:
            self.__start_mode = True
            self.__thememode_switch.value = True
            
        self.__lockdown_switch = Switch(
            value=False,
            label="Unlock?",
            on_change=self.__remove_lockdown,
        )

        container_width = self.__homepage.get_main_container_width()
        container_height = self.__homepage.get_main_container_height() - 300
        self.__col = Column(
            controls=[
                Row(
                    controls=[
                        self.__back_button,
                        Icon(icons.SETTINGS, size=50, color=TEXT_COLOUR),
                        IconButton(on_click=self.__homepage.help, icon=icons.HELP),
                    ],
                    spacing=20,
                    vertical_alignment=CrossAxisAlignment.START,
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                ),
                Divider(color=TEXT_COLOUR, height=2),
                Container(
                    padding=20,
                    height=container_height,
                    width=container_width,
                    bgcolor=BACKGROUND_COLOUR_2,
                    border=border.all(2, TEXT_COLOUR),
                    border_radius=10,
                    content=Column(
                        controls=[
                            Text("Theme Mode", size=16, weight=FontWeight.BOLD, font_family="Afacad", color=TEXT_COLOUR),
                            self.__thememode_switch,
                            Text("Resart app for changes to apply", size=12, font_family="Afacad", color=TEXT_COLOUR),
                            Divider(height=20,color="transparent"),
                            Checkbox(label="Unlock any passwords you set to lockdown?", value=False),
                            Checkbox(label="Unlock all passwords that you manage?", value=False),
                            self.__lockdown_switch,
                            Divider(height=20,color="transparent"),
                            Text("Update password", size=15, weight=FontWeight.BOLD, font_family="Afacad", color=TEXT_COLOUR),
                            self.__current_password_input,
                            Row(
                                controls=[
                                    self.__new_password_input,
                                    VerticalDivider(width=20,color="transparent"),
                                    ElevatedButton("Confirm", on_click=self.__change_password),
                                ],
                                spacing=20,
                                alignment=MainAxisAlignment.START,
                                vertical_alignment=CrossAxisAlignment.CENTER,
                            ),
                            Divider(height=20,color="transparent"),
                        ],
                    ),
                ),
                Divider(height=2,color="transparent"),
            ],
            spacing=20,
            alignment=MainAxisAlignment.START,
            horizontal_alignment=CrossAxisAlignment.START,
            # scroll=ScrollMode.AUTO,
        )
        self.__stack = Stack(
            controls=[
                self.__col,
            ],
        )
        return self.__stack