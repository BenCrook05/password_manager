from flet import *
from assets.colours import Colours
from pages.components.pro_ring import ProRing
from pages.components.inputs import Input
import sqlite3
import socket
BACKGROUND_COLOUR, THEME_COLOUR, TEXT_COLOUR, BACKGROUND_COLOUR_2= Colours().get_colours()


class ViewUsers(UserControl):
    def __init__(self, homepage, data, passID, type):
        super().__init__()
        self.__homepage = homepage
        self.__data = data
        self.__passID = passID
        self.__type = type
        self.__processing = False

    def __back(self,e):
        self.__homepage.view_password(None,self.__passID,self.__type)

    def __add_manager(self,e):
        manager_email = self.__new_manager_text_field.value
        if manager_email == "":
            return
        if not self.__processing:
            self.__processing = True
            data = self.__homepage.get_manager().add_manager(self.__passID,manager_email)
            print(f"passid: {self.__passID}")
            print(data)
            if data == "ADDED MANAGER":
                self.__homepage.get_page().snack_bar = SnackBar(
                    content=Text("Manager added",color=TEXT_COLOUR),
                    bgcolor=BACKGROUND_COLOUR_2,
                    elevation=5,
                    margin=5,
                    duration=3000,
                )
                self.__homepage.get_page().snack_bar.open = True
                self.__homepage.get_page().update()
                self.__homepage.refresh()
            else:
                self.__new_manager_text_field.error_text = data[0].upper() + data[1:].lower()
                self.__new_manager_text_field.update()
            self.__processing = False
            
    def __remove_user(self,e):
        user_email = self.__remove_user_text_field.value
        if user_email == "":
            return
        if not self.__processing:
            self.__processing = True
            self.__stack.controls.append(ProRing())
            self.__stack.update()
            data = self.__homepage.get_manager().remove_password_user(self.__passID,user_email)
            if data == "REMOVED USER":
                self.__homepage.get_page().snack_bar = SnackBar(
                    content=Text("User removed",color=TEXT_COLOUR),
                    bgcolor=BACKGROUND_COLOUR_2,
                    elevation=5,
                    margin=5,
                    duration=3000,
                )
                self.__homepage.get_page().snack_bar.open = True
                self.__homepage.get_page().update()
            self.__stack.controls.pop()
            self.__stack.update()
            self.__processing = False

    def build(self):
        self.__back_button = IconButton(icon=icons.ARROW_BACK,on_click=self.__back)
        self.__managers_container = Container(
            width=400,
            height=200,
            bgcolor=BACKGROUND_COLOUR_2,
            padding=20,
            margin=20,
            border_radius=10,
            border=border.all(3,TEXT_COLOUR),
            content=Column(
                controls=[],
                spacing=8,
                alignment=MainAxisAlignment.START,
                horizontal_alignment=CrossAxisAlignment.START,
                scroll=ScrollMode.AUTO,
            )
        )
        self.__users_container = Container(
            width=400,
            height=200,
            bgcolor=BACKGROUND_COLOUR_2,
            padding=20,
            margin=20,
            border_radius=10,
            border=border.all(3,TEXT_COLOUR),
            content=Column(
                controls=[],
                spacing=8,
                alignment=MainAxisAlignment.START,
                horizontal_alignment=CrossAxisAlignment.START,
                scroll=ScrollMode.AUTO,
            )
        )
        managers = self.__homepage.get_manager().get_password_users(self.__passID, manager=True)
        users = self.__homepage.get_manager().get_password_users(self.__passID)
        texts = list(map(
            lambda manager: Text(value=f"{manager[1]} {manager[2]}: {manager[0]}", size=13, font_family="Afacad", color=TEXT_COLOUR),
            managers
        ))
        self.__managers_container.content.controls.extend(texts)
        
        texts = list(map(
            lambda user: Text(value=f"{user[1]} {user[2]}: {user[0]}", size=13, font_family="Afacad", color=TEXT_COLOUR),
            users
        ))
        self.__users_container.content.controls.extend(texts)
        
        self.__new_manager_text_field = Input(
            icon_name=icons.EMAIL,
            hint="New manager email",
        )
        self.__remove_user_text_field = Input(
            icon_name=icons.EMAIL,
            hint="Remove user email",
        )
        
        self.__img = Icon(icons.PEOPLE_ALT, color=TEXT_COLOUR, size=50)
        self.__col = Column(
            controls=[
                Row(
                    controls=[
                        self.__back_button,
                        self.__img,
                        VerticalDivider(color="transparent",width=1),
                    ],
                    spacing=20,
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=CrossAxisAlignment.CENTER,
                ),
                Row(
                    controls=[
                        self.__new_manager_text_field,
                        ElevatedButton(
                            on_click = self.__add_manager,
                            icon=icons.ADD_ROUNDED,
                            text="Add manager",
                        )
                    ]
                ),
                Text("Managers", size=16, weight=FontWeight.BOLD, font_family="Afacad", color=TEXT_COLOUR),
                self.__managers_container,
                Divider(height=10,color="transparent"),
                Row(
                    controls=[
                        self.__remove_user_text_field,
                        ElevatedButton(
                            on_click = self.__remove_user,
                            icon=icons.ADD_ROUNDED,
                            text="Remove user",
                        )
                    ]
                ),
                Text("All Users", size=16, weight=FontWeight.BOLD, font_family="Afacad", color=TEXT_COLOUR),
                self.__users_container,
            ],
            spacing=20,
            alignment=MainAxisAlignment.START,
            horizontal_alignment=CrossAxisAlignment.CENTER,
        )
        self.__stack = Stack(
            controls=[
                self.__col,
            ],
        )
        return self.__stack