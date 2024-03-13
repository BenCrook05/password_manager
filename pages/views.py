from flet import *
from pages.frames.login import Login
from pages.frames.newdevice import Newdevice
from pages.components.navbar import Navbar
from pages.frames.newaccount import Newaccount
from pages.frames.frameComponents.receive_code import Receivecode
from pages.frames.homepage import Home
from assets.colours import Colours
BACKGROUND_COLOUR, THEME_COLOUR, TEXT_COLOUR, BACKGROUND_COLOUR_2= Colours().get_colours()



def views_handler(page, data):
    return {
        '/':View(
            route='/',
            horizontal_alignment='center',
            controls=[
                Navbar(page),
                Login(page, data),
            ],
            padding=0,
        ),
        '/Home':View(
            route='/Home',
            bgcolor=BACKGROUND_COLOUR,
            controls=[
                Navbar(page),
                Home(page, data)
            ],
            padding=0,
            spacing=0,
        ),
        '/Newdevice':View(
            route='/Newdevice',
            horizontal_alignment='center',
            controls=[
                Navbar(page),
                Newdevice(page, data)
            ],
            padding=0,
        ),
        '/Newaccount':View(
            route='/Newaccount',
            horizontal_alignment='center',
            controls=[
                Navbar(page),
                Newaccount(page, data)
            ],
            padding=0,
        ),
        
    }