from flet import *
import sqlite3
import socket
from assets.colours import Colours
BACKGROUND_COLOUR, THEME_COLOUR, TEXT_COLOUR, BACKGROUND_COLOUR_2= Colours().get_colours()



class Navbar(UserControl):
    def __init__(self, page):
        super().__init__()
        self.__page = page
        
        

    def __close(self, e):
        # self.__page.window_visible = False
        # self.__page.update()
        self.__page.window_prevent_close = False
        self.__page.update()
        self.__page.window_close()
        
    def __minimise(self, e):
        self.__page.window_prevent_close = True
        self.__page.window_minimized = True
        self.__page.update()
        
        
    def build(self):
        return Card(elevation=0,content=
            WindowDragArea(
                content=Container(
                    width = self.__page.window_max_width,
                    height=45,
                    padding=5,
                    content=Row([
                        Image(r"assets\Images\png\logo-icon.png", width=20, height=20, fit=ImageFit.CONTAIN),
                        Container(
                            content=Row([
                                IconButton(icons.MINIMIZE, icon_size=15, on_click=self.__minimise),
                                IconButton(icons.CLOSE, icon_size=15, on_click=self.__close)
                            ])
                        )
                    ], alignment="spaceBetween",),
                    bgcolor = BACKGROUND_COLOUR,
                    border=Border(
                        bottom=BorderSide(2, TEXT_COLOUR),
                        top=BorderSide(1, "transparent"),
                        left=BorderSide(1, "transparent"),
                        right=BorderSide(1, "transparent"),
                    ),
                ),
                maximizable=False,
            ),
        )