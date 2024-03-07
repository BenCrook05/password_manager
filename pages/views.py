from flet import *
from pages.login import Login
from pages.newdevice import Newdevice
from pages.navbar import Navbar
from pages.newaccount import Newaccount
from pages.receive_code import Receivecode
from pages.homepage import Home
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