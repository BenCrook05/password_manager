from flet import *
from assets.colours import Colours
from pages.components.pro_ring import ProRing

BACKGROUND_COLOUR, THEME_COLOUR, TEXT_COLOUR, BACKGROUND_COLOUR_2= Colours().get_colours()

class NewPassword(UserControl):
    def __init__(self, passID, title, sender_email, sender_name, sender_surname):
        super().__init__()
        self.__passID = passID
        self.__title = title
        self.__sender_email = sender_email
        self.__sender_name = sender_name
        self.__sender_surname = sender_surname
        
    def attempt_confirm(self, homepage):
        self.__homepage = homepage
        if self.__check_box.value == True:
            data = self.__homepage.get_manager().accept_pending_share(self.__passID)
            self.__homepage.get_page().snack_bar = SnackBar(
                content=Text(f"Password uploaded with code: {data.lower() if data else "None"}",color=TEXT_COLOUR),
                bgcolor=BACKGROUND_COLOUR_2,
                elevation=5,
                margin=5,
                duration=3000,
            )
            
    def check_box_true(self):
        self.__check_box.value = True
        self.__check_box.update()
    
    def build(self):
        self.__check_box = Checkbox(value=False)
        self.__row = Row(
            controls=[
                Column(
                    controls=[
                        Text(self.__title, size=19, weight=FontWeight.BOLD, font_family="Afacad", color=TEXT_COLOUR),
                        Text(value=f"Sender: {self.__sender_name} {self.__sender_surname}: {self.__sender_email}", size=13, weight=FontWeight.BOLD, font_family="Afacad", color=TEXT_COLOUR),
                    ],
                    alignment=MainAxisAlignment.START,
                    horizontal_alignment=CrossAxisAlignment.START,
                ),
                self.__check_box,
            ],
            spacing=20,
            alignment=MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=CrossAxisAlignment.CENTER,
        )
        return self.__row


class ReceiveShared(UserControl):
    def __init__(self, homepage, data):
        super().__init__()
        self.__homepage = homepage
        self.__data = data
        self.__processing = False
        self.__receiving_password_list = []
        
        
    def __download(self,e):
        if not self.__processing:
            self.__processing = True
            self.__stack.controls.append(ProRing())
            self.__stack.update()
            data = self.__homepage.get_manager().get_pending_shares()
            if data == "NO PENDING PASSWORDS":
                self.__homepage.get_page().snack_bar = SnackBar(
                    content=Text("No passwords have been shared with you",color=TEXT_COLOUR),
                    bgcolor=BACKGROUND_COLOUR_2,
                    elevation=5,
                    margin=5,
                    duration=3000,
                )
                self.__homepage.get_page().snack_bar.open = True
                self.__homepage.get_page().update()
                self.__homepage.get_navrail().set_selected_index(0)
                self.__homepage.get_navrail().get_nav().update()
                self.__homepage.destination_change(None)
            else:
                self.__col.controls = self.__col.controls[:4]
                self.__col.controls.extend([
                    Text("Select the passwords you would like to accept", size=15, weight=FontWeight.BOLD, font_family="Afacad", color=TEXT_COLOUR),
                    Row(
                        controls=[
                            VerticalDivider(color="transparent", width=1),
                            ElevatedButton("Select All", on_click=self.__select_all),
                        ],
                        spacing=20,
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=CrossAxisAlignment.CENTER,
                    )
                ])
                for element in data:
                    self.__receiving_password_list.append(NewPassword(passID=element[0], title=element[1], sender_email=element[2], sender_name=element[3], sender_surname=element[4]))
                    self.__col.controls.extend([
                        self.__receiving_password_list[-1], #add the last element of the list
                        Divider(height=2,color=BACKGROUND_COLOUR_2)
                    ])
                self.__col.controls.extend([
                    Divider(height=10,color="transparent"),
                    ElevatedButton("Confirm", on_click=self.__upload)
                ])
                self.__col.update()
                self.__stack.controls.pop()
                self.__stack.update()
                self.__processing = False
         
    def __select_all(self,e):
        if not self.__processing:
            for element in self.__receiving_password_list:
                element.check_box_true()
                
    def __upload(self,e):
        if not self.__processing:
            self.__processing = True
            self.__stack.controls.append(ProRing())
            self.__stack.update()
            for element in self.__receiving_password_list:
                element.attempt_confirm(self.__homepage)
            self.__homepage.get_page().snack_bar = SnackBar(
                content=Text("Accepted passwords have been added to your account",color=TEXT_COLOUR),
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
            
    
    def __back(self,e):
        self.__homepage.get_navrail().set_selected_index(0)
        self.__homepage.get_navrail().get_nav().update()
        self.__homepage.destination_change(None)
            
    def build(self):
        self.__back_button = IconButton(icon=icons.ARROW_BACK,on_click=self.__back)
        self.__col = Column(
            controls=[
                Row(
                    controls=[
                        self.__back_button,
                        Icon(icons.CLOUD_DOWNLOAD, size=50, color=TEXT_COLOUR),
                        VerticalDivider(color="transparent",width=25),
                    ],
                    spacing=20,
                    vertical_alignment=CrossAxisAlignment.START,
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                ),
                Divider(height=50,color="transparent"),
                Row(controls=[
                    VerticalDivider(width=1,color="transparent"),
                    Text("Would you like to download passwords that\nhave been shared with you now?", size=15, font_family="Afacad", color=TEXT_COLOUR),
                    VerticalDivider(width=1,color="transparent"),
                    ],
                    spacing=5,
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=CrossAxisAlignment.CENTER,
                ),
                Divider(height=20,color="transparent"),
                Row(
                    controls=[
                        VerticalDivider(width=2,color="transparent"),
                        ElevatedButton("Return", on_click=self.__back),
                        ElevatedButton("Continue", on_click=self.__download),
                        VerticalDivider(width=2,color="transparent"),
                    ],
                    spacing=20,
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=CrossAxisAlignment.CENTER,
                )
            ],
            spacing=20,
            alignment=MainAxisAlignment.START,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            # TODO sort out scroll causing page to center
            # scroll=ScrollMode.AUTO,
        )
        self.__stack = Stack(
            controls=[
                self.__col,
            ],
        )
        return self.__stack