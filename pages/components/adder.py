from flet import *
from pages.components.inputs import Input
from pages.components.pro_ring import ProRing
from assets.colours import Colours

BACKGROUND_COLOUR, THEME_COLOUR, TEXT_COLOUR, BACKGROUND_COLOUR_2= Colours().get_colours()


class PasswordAdder(UserControl):
    def __init__(self, homepage):
        super().__init__()
        self.__homepage = homepage
        self.__current_state = "password"
        self.__processing = False 
        self.__back_button = IconButton()
        self.__switch_button = ElevatedButton()
        self.__confirm_buton = ElevatedButton()
        self.__title_input = Input()
        self.__url_input = Input()
        self.__username = Input()
        self.__password = Input()
        self.__additional_info = Input()
        self.__generate_password_button = ElevatedButton()
        self.__col = Column()
        self.__stack = Stack()
        
    def __add_password(self,e):
        if not self.__processing:
            self.__stack.controls.append(ProRing())
            self.__stack.update()
            self.__processing = True
            title = self.__title_input.get_value()
            url = self.__url_input.get_value()
            username = self.__username.get_value()
            password = self.__password.get_value()
            additional_info = self.__additional_info.get_value()
            try:
                if title == "":
                    self.__title_input.set_error_text("Title required")
                    self.__title_input.update()
                    raise Exception("Title required") 
                elif password == "":
                    self.__password.set_error_text("Password required")
                    self.__password.update()
                    raise Exception("Password required") 
                
                if self.__current_state == "password": #elements only required for passwords not infos
                    if url == "":
                        self.__url_input.set_error_text("URL required")
                        self.__url_input.update()
                        raise Exception("URL required") 
                    if username == "":
                        self.__username.set_error_text("Username required")
                        self.__username.update()
                        raise Exception("Username required") 
            except:
                self.__stack.controls.pop()
                self.__stack.update()
                self.__processing = False
                return
                
            self.__homepage.get_manager().add_new_password(title,url,
                                                           username,additional_info,
                                                           password)
            self.__homepage.get_page().snack_bar = SnackBar(
                content=Text("New Password Added",color=TEXT_COLOUR),
                bgcolor=BACKGROUND_COLOUR_2,
                elevation=5,
                margin=5,
                duration=3000,
            )
            self.__stack.controls.pop()
            self.__stack.update()
            self.__processing = False
            self.__homepage.get_page().snack_bar.open = True
            self.__homepage.get_page().update()
            self.__homepage.refresh()    
    
    def __back(self,e):
        self.__homepage.destination_change(None)
    
    def __insert_random_password(self,e):
        random_password = self.__homepage.get_manager().create_random_password()
        self.__password.set_value(random_password)
        self.__password.update()
        self.__homepage.copy_to_clipboard(random_password)


    def __switch(self,e):
        if self.__current_state == "password":
            self.__col.controls.remove(self.__url_input)
            self.__col.controls.remove(self.__username)
            self.__col.controls.remove(self.__additional_info)
            self.__col.update()
            self.__current_state = "info"
            self.__switch_button.icon = icons.SWITCH_LEFT_ROUNDED
            self.__switch_button.text = "Switch To Password"
        else:
            self.__col.controls.insert(3,self.__url_input)
            self.__col.controls.insert(4,self.__username)
            self.__col.controls.insert(6,self.__additional_info)
            self.__current_state = "password"
            self.__switch_button.icon = icons.SWITCH_RIGHT_ROUNDED
            self.__switch_button.text = "Switch To Credential"
        self.__col.update()
    
    def build(self):
        self.__back_button = IconButton(
            icon=icons.ARROW_BACK,
            on_click=self.__back
        )
        self.__switch_button = ElevatedButton(
            icon=icons.SWITCH_RIGHT_ROUNDED, 
            text="Switch To Credential",
            on_click=self.__switch
        )
        self.__confirm_buton = ElevatedButton(
            icon=icons.ADD_ROUNDED, 
            text="Add Password",
            on_click=self.__add_password
        )
        self.__title_input = Input("TITLE_ROUNDED","Title")
        self.__url_input = Input("CAST_CONNECTED_ROUNDED","URL",max_length=128)
        self.__username = Input("PERSON_ROUNDED","Username",max_length=64, 
                                default_value=self.__homepage.get_manager().get_email())
        self.__password = Input("LOCK_ROUNDED","Password",hide=True,reveal_option=True)
        self.__additional_info = Input("INFO_ROUNDED","Additional Info",max_length=256)

        self.__generate_password_button = ElevatedButton(
            text="Generate password",
            icon=icons.CREATE_ROUNDED,
            on_click=self.__insert_random_password
        )

        self.__col = Column(
            controls=[
                Row(
                    controls=[
                        self.__back_button,
                        Icon(icons.CREATE_ROUNDED,size=50,color=TEXT_COLOUR),
                        VerticalDivider(color="transparent",width=25),
                    ],
                    spacing=20,
                    vertical_alignment=CrossAxisAlignment.CENTER,
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                ),
                self.__switch_button,
                self.__title_input,
                self.__url_input,
                self.__username,
                self.__password,
                self.__additional_info,
                Divider(height=10,color="transparent"),
                Row(
                    controls=[
                        VerticalDivider(color="transparent",width=1),
                        self.__confirm_buton,
                        VerticalDivider(color="transparent",width=1),
                    ],
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=CrossAxisAlignment.CENTER,
                ),
                Divider(height=10,color="transparent"),
                Row(
                    controls=[
                        VerticalDivider(color="transparent",width=1),
                        self.__generate_password_button,
                        VerticalDivider(color="transparent",width=1),
                    ],
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=CrossAxisAlignment.CENTER,
                )
            ],
            spacing=20,
            alignment=MainAxisAlignment.START,
            horizontal_alignment=CrossAxisAlignment.CENTER,
        )
        self.__stack = Stack(
            controls=[
                self.__col
            ],
        )
        return self.__stack