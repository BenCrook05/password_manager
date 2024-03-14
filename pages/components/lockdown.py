from flet import *
import sqlite3
import socket
from pages.components.pro_ring import ProRing
from assets.colours import Colours

BACKGROUND_COLOUR, THEME_COLOUR, TEXT_COLOUR, BACKGROUND_COLOUR_2= Colours().get_colours()

class Lockdown(UserControl):
    def __init__(self, homepage, passID, type):
        super().__init__()
        self.__homepage = homepage
        self.__passID = passID
        self.__type = type
        self.__processing = False
        self.__back_button = IconButton()
        self.__stack = Stack()
    
    def __set_to_lockdown(self,e):
        if not self.__processing:
            self.__processing = True
            self.__stack.controls.append(ProRing())
            self.__stack.update()
            data = self.__homepage.get_manager().set_to_lockdown(self.__passID)
            if data == "SET TO LOCKDOWN":
                self.__homepage.get_page().snack_bar = SnackBar(
                    content=Text("Password locked down",color=TEXT_COLOUR),
                    bgcolor=BACKGROUND_COLOUR_2,
                    elevation=5,
                    margin=5,
                    duration=3000,
                )
                
            else:
                self.__homepage.get_page().snack_bar = SnackBar(
                    content=Text("Failed to lockdown password",color=TEXT_COLOUR),
                    bgcolor=BACKGROUND_COLOUR_2,
                    elevation=5,
                    margin=5,
                    duration=3000,
                )
                
            self.__homepage.get_page().snack_bar.open = True
            self.__homepage.get_page().update()
            self.__homepage.refresh()
    
    def __back(self,e):
        self.__homepage.view_password(e,self.__passID,self.__type)
    
    def build(self):
        self.__back_button = IconButton(icon=icons.ARROW_BACK, on_click=self.__back)
        self.__stack = Stack(
            controls=[
                Column(
                    controls=[
                        Row(
                            controls=[
                                self.__back_button,
                                Icon(icons.VPN_LOCK_OUTLINED, size=50, color=TEXT_COLOUR),
                                VerticalDivider(width=27, color=TEXT_COLOUR),
                            ],
                            spacing=20,
                            alignment=MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=CrossAxisAlignment.CENTER,
                        ),
                        Divider(height=20, color="transparent"),
                        Divider(color=TEXT_COLOUR),
                        Container(
                            height=200,
                            width=400,
                            padding=20,
                            margin=20,
                            border_radius=10,
                            bgcolor="#F39E9C",
                            border=border.all(2,"red"),
                            content=Column(
                                controls=[
                                    Icon(
                                        icons.LOCK_ROUNDED,
                                        color=BACKGROUND_COLOUR,
                                        size=80,
                                        opacity=0.8,
                                    ),
                                    Text("You will only be able to recover the password from this device.", 
                                         size=14, weight=FontWeight.BOLD, font_family="Afacad", 
                                         color=TEXT_COLOUR, text_align=TextAlign.CENTER,),
                                    
                                    Text("Are you sure you want to lockdown this password?", 
                                         size=15, weight=FontWeight.BOLD, font_family="Afacad", 
                                         color=TEXT_COLOUR, text_align=TextAlign.CENTER,),
                                    
                                ],
                                height=200,
                                spacing=10,
                                alignment=MainAxisAlignment.SPACE_EVENLY,
                                horizontal_alignment=CrossAxisAlignment.CENTER,
                            ),
                        ),
                        Divider(height=10, color="transparent"),
                        ElevatedButton(
                            text="Yes",
                            on_click=self.__set_to_lockdown,
                        ),
                    ],
                    spacing=20,
                    alignment=MainAxisAlignment.START,
                    horizontal_alignment=CrossAxisAlignment.CENTER,
                ),
            ],
        )
        return self.__stack