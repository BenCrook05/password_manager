from flet import *
import pycountry
from datetime import datetime
from assets.colours import Colours
BACKGROUND_COLOUR, THEME_COLOUR, TEXT_COLOUR, BACKGROUND_COLOUR_2= Colours().get_colours()
from ipwhois import IPWhois
import socket


class Input(UserControl):
    def __init__(self, icon_name="PERSON",hint="",hide=False,on_press_function=None,focus=False,reveal_option=False,max_length=32,width=300,default_value=""):
        super().__init__()
        self.__icon_name = icon_name
        self.__hint = hint
        self.__hide = hide
        self.__on_press_function = on_press_function
        self.__focus = focus
        self.__reveal_button = reveal_option
        self.__max_length = max_length
        self.__width = width
        self.__default_value = default_value
        self.__textfield = TextField()
        self.__container = Container()
        
        
    
    def set_error_text(self, text):
        self.__textfield.error_text = text
        
        self.__container.height = 80
        self.__textfield.height = 75
        self.__container.update()
        self.__textfield.update()
    
    def update(self):
        self.__textfield.update()
    
    def set_value(self, value):
        self.__textfield.value = value
        
    def get_value(self):
        return self.__textfield.value
        
    def on_submit(self):
        if self.__on_press_function:
            self.__on_press_function()

    def change_disabled(self):
        self.__textfield.read_only=not(self.__textfield.read_only)

    def _check_length(self,e):
        if self.__textfield.error_text:
            self.__textfield.error_text = ""
            self._reset_height()
            self.__textfield.update()
            
        if len(self.__textfield.value) > self.__max_length:
            self.__textfield.value = self.__textfield.value[:self.__max_length]
            self.__textfield.update()
            
        if self.__hint == "Date of Birth":
            self.__validate_date(e)
            
    def __validate_date(self,e): #only called if hint is "Date of Birth"
        date = self.__textfield.value
        if len(date) >= 3:
            if date[2] != "-":
                self.__textfield.value = date[:2] + "-" + date[2:]
                self.__textfield.update()
        if len(date) >= 6:
            if date[5] != "-":
                self.__textfield.value = date[:5] + "-" + date[5:]
                self.__textfield.update()
        if len(date) > 10:
            self.__textfield.value = date[:10]
            self.__textfield.update()
        if len(date) == 10:
            try:
                max_year = datetime.now().year
                min_year = max_year - 120
                day, month, year = date.split("-")
                day = int(day)
                month = int(month)
                year = int(year)
                if day > 31 or day < 1:
                    self.__create_date_error()
                    return
                if month > 12 or month < 1:
                    self.__create_date_error()
                    return
                if year > 2021 or year < 1900:
                    self.__create_date_error()
                    return
            except:
                self.__textfield.value = ""
                self.__textfield.update()
                self.__textfield.error_text = "Invalid date"
                self.__textfield.update()
                return
        self.__textfield.error_text = None
        self.__textfield.update()
        
    def __create_date_error(self):
        self.__textfield.error_text = "Invalid date"
        self._change_height(50)
        self.__textfield.update()
        
    def _clear_field(self):
        self.__textfield.value = ""
        self.__textfield.update()

    def show_input(self):
        self.__textfield.password = False

    def hide_input(self):
        self.__textfield.password = True
        
    def _change_height(self, new_height):
        self.__textfield.height = new_height
        self.__textfield.update()
    
    def _reset_height(self):
        self.__textfield.height = 30
        self.__textfield.update()

    def build(self):
        self.__textfield = TextField(
            can_reveal_password = self.__reveal_button,
            autofocus = self.__focus,
            border_color = 'transparent',
            bgcolor = 'transparent',
            height = 30,
            width = self.__width,
            text_size = 12,
            content_padding = 5,
            cursor_color = TEXT_COLOUR,
            hint_text = self.__hint,
            hint_style = TextStyle(size=11),
            password = self.__hide,
            on_change = self._check_length,
            on_blur = None,
            disabled=False,
            read_only=False,
            error_style=TextStyle(size=9),
        )
        if self.__default_value != "":
            self.__textfield.value = self.__default_value
        if self.__hint == "Date of Birth":
            self.__textfield.hint_text += " (dd-mm-yyyy)"

            
        self.__container = Container(
            width = 320,
            height = 50,
            border = border.only(bottom=border.BorderSide(1,TEXT_COLOUR)),
            content = Row(
                spacing = 10,
                vertical_alignment = CrossAxisAlignment.CENTER,
                controls=[
                    Icon(
                        name = self.__icon_name,
                        size = 18,
                        opacity = 0.5,
                    ),
                    self.__textfield,
                ]
            )
        )
        return self.__container

class CountryInput(UserControl):
    def __init__(self):
        super().__init__()
        self.__dropdown = Dropdown()
    
    
    def set_error_text(self, text):
        self.__dropdown.error_text = text
        self.__dropdown.update()
    
    def get_value(self):
        return self.__dropdown.value
    
    def update(self):
        self.__dropdown.update()
    
    def change_disabled(self):
        self.__dropdown.disabled=not(self.__dropdown.disabled)
    
    def __get_location(self):
        try:
            ip_address = socket.gethostbyname(socket.gethostname())
            obj = IPWhois(ip_address)
            result = obj.lookup_rdap()        
            country = result.get("network", {}).get("country", "Unknown")
            return country
        except Exception as e:
            return "United Kingdom"
        
        
    def build(self):
        countries = [country.name for country in pycountry.countries]
        countries = sorted(countries)
        options = []
        for country in countries:
            options.append(dropdown.Option(key=country))

            
        self.__dropdown = Dropdown(
            options=options,
            bgcolor='transparent',
            border_color='transparent',
            content_padding=1,
            height=30,
            width=300,
            text_size=12,
            hint_text="Country",
            hint_style=TextStyle(size=11),
            on_change=None,
            on_blur=None,
            disabled=False,
        )
        
        current_country = self.__get_location()
        self.__dropdown.value = current_country

        return Container(
            width=320,
            height=50,
            border = border.only(bottom=border.BorderSide(1,TEXT_COLOUR)),
            content=Row(
                spacing=10,
                vertical_alignment=CrossAxisAlignment.CENTER,
                controls=[
                    Icon(
                        name="FLAG_ROUNDED",
                        size=18,
                        opacity=0.5,
                    ),
                    self.__dropdown,
                ]
            ) 
        )