from flet import *
import pycountry
from assets.colours import Colours
BACKGROUND_COLOUR, THEME_COLOUR, TEXT_COLOUR, BACKGROUND_COLOUR_2= Colours().get_colours()
from ipwhois import IPWhois
import socket


class Input(UserControl):
    def __init__(self, icon_name, hint, hide=False,on_press_function=None,focus=False,reveal_option=False,max_length=32,width=300):
        super().__init__()
        self._icon_name = icon_name
        self._hint = hint
        self._hide = hide
        self._on_press_function = on_press_function
        self._focus = focus
        self._reveal_button = reveal_option
        self._max_length = max_length
        self._width = width
        
    
    def set_error_text(self, text):
        self._textfield.error_text = text
        
        self._container.height = 80
        self._textfield.height = 75
        self._container.update()
        self._textfield.update()
    
    def update(self):
        self._textfield.update()
    
    def set_value(self, value):
        self._textfield.value = value
        
    def get_value(self):
        return self._textfield.value
        
    def on_submit(self):
        if self._on_press_function:
            self._on_press_function()

    def change_disabled(self):
        self._textfield.read_only=not(self._textfield.read_only)

    def _check_length(self,e):
        if self._textfield.error_text:
            self._textfield.error_text = ""
            self._reset_height()
            self._textfield.update()
            
        if len(self._textfield.value) > self._max_length:
            self._textfield.value = self._textfield.value[:self._max_length]
            self._textfield.update()
            
        if self._hint == "Date of Birth":
            self.__validate_date(e)
            
    def __validate_date(self,e):
        date = self._textfield.value
        if len(date) == 3:
            if date[2] != "-":
                self._textfield.value = date[:2] + "-" + date[2:]
                self._textfield.update()
        if len(date) == 6:
            if date[5] != "-":
                self._textfield.value = date[:5] + "-" + date[5:]
                self._textfield.update()
        if len(date) > 10:
            self._textfield.value = date[:10]
            self._textfield.update()
        if len(date) == 10:
            try:
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
                self._textfield.value = ""
                self._textfield.update()
                self._textfield.error_text = "Invalid date"
                self._textfield.update()
                return
        self._textfield.error_text = None
        self._textfield.update()
        
    def __create_date_error(self):
        self._textfield.error_text = "Invalid date"
        self._change_height(50)
        self._textfield.update()
        
    def _clear_field(self):
        self._textfield.value = ""
        self._textfield.update()

    def show_input(self):
        self._textfield.password = False

    def hide_input(self):
        self._textfield.password = True
        
    def _change_height(self, new_height):
        self._textfield.height = new_height
        self._textfield.update()
    
    def _reset_height(self):
        self._textfield.height = 30
        self._textfield.update()

    def build(self):
        self._textfield = TextField(
            can_reveal_password = self._reveal_button,
            autofocus = self._focus,
            border_color = 'transparent',
            bgcolor = 'transparent',
            height = 30,
            width = self._width,
            text_size = 12,
            content_padding = 5,
            cursor_color = TEXT_COLOUR,
            hint_text = self._hint,
            hint_style = TextStyle(size=11),
            password = self._hide,
            on_change = self._check_length,
            on_blur = None,
            disabled=False,
            read_only=False,
            error_style=TextStyle(size=9),
            #max_length=self._max_length,
        )
        if self._hint == "Date of Birth":
            # self._textfield.helper_text="dd-mm-yyyy"
            self._textfield.hint_text += " (dd-mm-yyyy)"
            # self._textfield.helper_text_style=TextStyle(size=,weight=FontWeight.W_100)
            # self._textfield.height = 50
            #self._textfield.update()
            
        self._container = Container(
            width = 320,
            height = 50,
            border = border.only(bottom=border.BorderSide(1,TEXT_COLOUR)),
            content = Row(
                spacing = 10,
                vertical_alignment = CrossAxisAlignment.CENTER,
                controls=[
                    Icon(
                        name = self._icon_name,
                        size = 18,
                        opacity = 0.5,
                    ),
                    self._textfield,
                ]
            )
        )
        return self._container

class CountryInput(UserControl):
    def __init__(self):
        super().__init__()
    
    def set_error_text(self, text):
        self._dropdown.error_text = text
        self._dropdown.update()
    
    def get_value(self):
        return self._dropdown.value
    
    def update(self):
        self._dropdown.update()
    
    def change_disabled(self):
        self._dropdown.disabled=not(self._dropdown.disabled)
    
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
        current_country = self.__get_location()
        for option in options:
            if option.key == current_country:
                option.selected = True
                break
            
        self._dropdown = Dropdown(
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
                    self._dropdown,
                ]
            ) 
        )