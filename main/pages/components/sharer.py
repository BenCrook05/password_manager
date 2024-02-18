from flet import *
import sqlite3
from assets.colours import Colours
from pages.components.pro_ring import ProRing
from pages.components.inputs import Input

BACKGROUND_COLOUR, THEME_COLOUR, TEXT_COLOUR, BACKGROUND_COLOUR_2= Colours().get_colours()


class Sharer(UserControl):
    def __init__(self, homepage, data, passID, type):
        super().__init__(self)
        self.__homepage = homepage
        self.__data = data
        self.__page = homepage.get_page() #required for alert dialog
        self.__passID = passID
        self.__type = type
        self.__processing = False

    def __reset_user_boxes(self,e):
        self.__forename_box.value=self.__recipient_forename
        self.__forename_box.update()
        self.__surname_box.value=self.__recipient_name
        self.__surname_box.update()
        self.__email_box.value=self.__recipient_email
        self.__email_box.update()

    def __show_user_to_share(self,e):
        if not self.__processing:
            self.__processing = True
            self.__stack.controls.append(ProRing())
            self.__stack.update()
            temp_email = self.__user_input.get_value()
            if temp_email != self.__data["email"]:
                data = self.__homepage.get_manager().share_password_check(self.__passID, temp_email)
                if data == "NO USER":
                    self.__stack.controls.pop()
                    self.__stack.update()
                    self.__user_input.error_text = "No user associated with  email"
                    self.__user_input.update()
                    self.__col.update()
                    self.__processing = False
                else:
                    print(data)
                    self.__recipient_userID, self.__recipient_forename, self.__recipient_name, self.__recipient_email = data
                    self.__col.controls = self.__col.controls[:4]  #remove unwanted controls from the column keeping the image and buttons
                    self.__confirm_button = ElevatedButton("Confirm", on_click=self.__confirm_access_rights)
                    self.__return_button = ElevatedButton("Return", on_click=self.__back)
                    self.__forename_box = TextField(
                        label="Recipient's Forename",
                        value=self.__recipient_forename,
                        width=300,
                        border_radius=10,
                        border_color=TEXT_COLOUR,
                        on_change=self.__reset_user_boxes,
                    )
                    self.__surname_box = TextField(
                        label="Recipient's Surname",
                        value=self.__recipient_name,
                        width=300,
                        border_radius=10,
                        border_color=TEXT_COLOUR,
                        on_change=self.__reset_user_boxes,
                    )
                    self.__email_box = TextField(
                        label="Recipient's Email",
                        value=self.__recipient_email,
                        width=300,
                        border_radius=10,
                        border_color=TEXT_COLOUR,
                        on_change=self.__reset_user_boxes,
                    )
                    self.__col.controls.extend([
                        self.__forename_box,
                        Divider(height=10,color="transparent"),
                        self.__surname_box,
                        Divider(height=10,color="transparent"),
                        self.__email_box,
                        Divider(height=20,color="transparent"),
                        Text("Correct User?",size=15,weight=FontWeight.BOLD,font_family="Afacad",color=TEXT_COLOUR),
                        Divider(height=10,color="transparent"),
                        Row(
                            controls=[
                                VerticalDivider(color="transparent", width=1),
                                self.__return_button,
                                self.__confirm_button,
                                VerticalDivider(color="transparent", width=1),
                            ],
                            spacing=20,
                            alignment=MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=CrossAxisAlignment.CENTER,
                        )
                    ])
                    self.__col.update()
                    self.__stack.controls.pop()
                    self.__stack.update()
            else:
                self.__stack.controls.pop()
                self.__stack.update()
                self.__user_input.error_text = "Cannot share password with yourself"
                self.__user_input.update()
                self.__col.update()
                self.__processing = False
          
    def __confirm_access_rights(self,e):
        ##check manager choice then confirm share
        self.__col.controls = self.__col.controls[:4]
        self.__confirm_send_button = ElevatedButton("Confirm", on_click=self.__confirm_to_send)
        self.__manager_checkbox = Checkbox(value=False)
        self.__col.controls.extend([
            Divider(height=40,color="transparent"),
            Row(
                controls=[
                    VerticalDivider(color="transparent", width=100),
                    Text("Allow User to make changes?"),
                    self.__manager_checkbox,
                    VerticalDivider(color="transparent", width=100),
                ],
                spacing=20,
                alignment=MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=CrossAxisAlignment.CENTER,  
            ),
            Row(
                controls=[
                    VerticalDivider(color="transparent", width=1),
                    self.__return_button,
                    self.__confirm_send_button,
                    VerticalDivider(color="transparent", width=1),
                ],
                spacing=20,
                alignment=MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=CrossAxisAlignment.CENTER,
            )
        ])
        self.__col.update()
          
            
    def __confirm_to_send(self,e):
        self.__final_confirm_button = ElevatedButton("Confirm", on_click=self.__final_send_password)
        self.__recipient_is_manager = 1 if self.__manager_checkbox.value else 0
        self.__col.controls = self.__col.controls[:4]
        self.__col.controls.extend([
            Text(
                f"Are you sure you want to share this password with {self.__recipient_forename}, {self.__recipient_name}?",
                size=15,
                weight=FontWeight.BOLD,
                font_family="Afacad",
                color=TEXT_COLOUR,
            ),
            Divider(height=10,color="transparent"),
            Row(
                controls=[
                    VerticalDivider(color="transparent", width=1),
                    self.__return_button,
                    self.__final_confirm_button,
                    VerticalDivider(color="transparent", width=1),
                ],
                spacing=20,
                alignment=MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=CrossAxisAlignment.CENTER,
            )
            ])
        self.__col.update()
        
        
    def __final_send_password(self, e):
        # self.__alert.close()
        self.__stack.controls.append(ProRing())
        self.__stack.update()
        data = self.__homepage.get_manager().share_password_confirm(self.__passID, self.__recipient_email, self.__recipient_is_manager)
        data = data[0].upper() + data[1:].lower()
        self.__homepage.get_page().snack_bar = SnackBar(
            content=Text(data,color=TEXT_COLOUR),
            bgcolor=BACKGROUND_COLOUR_2,
            elevation=5,
            margin=5,
            duration=3000,
        )
        self.__homepage.get_page().snack_bar.open = True
        self.__homepage.get_page().update()
        self.__homepage.refresh()
        


    def __back(self,e):
        self.__homepage.view_password(None,self.__passID,self.__type)


    def build(self):
        self.__user_input = Input(icons.PERSON_ROUNDED, hint="Recipient Email")
        self.__back_button = IconButton(icon=icons.ARROW_BACK,on_click=self.__back)
        self.__find_user_button = ElevatedButton("Find User", on_click=self.__show_user_to_share)        
        self.__col = Column(
            controls=[
                Row(
                    controls=[
                        self.__back_button,
                        Icon(icons.SEND_ROUNDED, color=TEXT_COLOUR, size=50),
                        VerticalDivider(color="transparent", width=38),
                    ],
                    spacing = 20,
                    alignment = MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment = CrossAxisAlignment.CENTER,
                ),
                Divider(height=35,color="transparent"),
                self.__user_input,
                Divider(height=40,color="transparent"),
                Row(
                    controls=[
                        VerticalDivider(color="transparent", width=1),
                        self.__find_user_button,
                        VerticalDivider(color="transparent", width=1),
                    ],
                    spacing = 20,
                    alignment = MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment = CrossAxisAlignment.CENTER,
                )
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