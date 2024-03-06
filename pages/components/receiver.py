from flet import *
from assets.colours import Colours
from pages.components.pro_ring import ProRing

BACKGROUND_COLOUR, THEME_COLOUR, TEXT_COLOUR, BACKGROUND_COLOUR_2= Colours().get_colours()

class NewPassword(UserControl):
    def __init__(self, passID, title, sender_email, sender_name, sender_surname, homepage):
        super().__init__()
        self.__passID = passID
        self.__title = title
        self.__sender_email = sender_email
        self.__sender_name = sender_name
        self.__sender_surname = sender_surname
        self.__homepage = homepage
        self.__check_box = Checkbox()
        self.__delete_button = IconButton()
        self.__row = Row()
        
    def attempt_confirm(self):
        if self.__check_box.value == True:
            data = self.__homepage.get_manager().accept_pending_share(self.__passID, "Accept")
            self.__homepage.get_page().snack_bar = SnackBar(
                content=Text(f"Password uploaded with code: {data.lower() if data else 'None'}",color=TEXT_COLOUR),
                bgcolor=BACKGROUND_COLOUR_2,
                elevation=5,
                margin=5,
                duration=3000,
            )
        else:
            self.__homepage.get_manager().accept_pending_share(self.__passID, "no action") 
            
    def __delete(self,e):
        self.__homepage.get_manager().accept_pending_share(self.__passID, "Reject")
        self.__row.controls = []
        self.__row.update()
            
    def check_box_true(self):
        self.__check_box.value = True
        self.__check_box.update()
    
    def build(self):
        self.__check_box = Checkbox(value=False)
        self.__delete_button = IconButton(icon=icons.DELETE, on_click=self.__delete, bgcolor="red")
        self.__row = Row(
            controls=[
                Column(
                    controls=[
                        Text(self.__title, size=19, weight=FontWeight.BOLD, font_family="Afacad", color=TEXT_COLOUR),
                        Text(value=f"Sender: {self.__sender_name} {self.__sender_surname}: {self.__sender_email}", size=13, font_family="Afacad", color=TEXT_COLOUR),
                    ],
                    alignment=MainAxisAlignment.START,
                    horizontal_alignment=CrossAxisAlignment.START,
                ),
                Row(
                    controls=[
                        self.__check_box,
                        VerticalDivider(width=15,),
                        self.__delete_button,
                    ],
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=CrossAxisAlignment.CENTER,
                ),
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
        self.__back_button = IconButton()
        self.__col = Column()
        self.__stack = Stack()
        
         
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
                element.attempt_confirm()
            self.__homepage.get_page().snack_bar = SnackBar(
                content=Text("Accepted passwords have been added to your account",color=TEXT_COLOUR),
                bgcolor=BACKGROUND_COLOUR_2,
                elevation=5,
                margin=5,
                duration=3000,
            )
            self.__homepage.get_page().snack_bar.open = True
            self.__homepage.get_page().update()
            self.__homepage.refresh()
            
    
    def __back(self,e):
        self.__homepage.get_navrail().set_selected_index(0)
        self.__homepage.get_navrail().get_nav().update()
        self.__homepage.destination_change(None)
            
    def build(self):
        self.__back_button = IconButton(icon=icons.ARROW_BACK,on_click=self.__back)
        self.__col = Column(
            controls=[],
            spacing=10,
            alignment=MainAxisAlignment.START,
            horizontal_alignment=CrossAxisAlignment.CENTER,
        )
        self.__stack = Stack(
            controls=[
                self.__col,
            ],
        )
        
        data = self.__homepage.get_manager().get_pending_shares()

        if data == "NO PENDING PASSWORDS" or type(data) != list:
            raise Exception("No pending passwords")
        else:
            self.__col.controls = self.__col.controls[:4]
            self.__col.controls.extend([
                Divider(height=3, color="transparent"),
                Text("Select the passwords you would like to accept", size=15, weight=FontWeight.BOLD, font_family="Afacad", color=TEXT_COLOUR),
                Divider(height=40),
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
                self.__receiving_password_list.append(NewPassword(passID=element[0], title=element[1], sender_email=element[2], sender_name=element[3], sender_surname=element[4], homepage=self.__homepage))
                self.__col.controls.extend([
                    self.__receiving_password_list[-1], #add the last element of the list
                    Divider(height=2,color=BACKGROUND_COLOUR_2)
                ])
            self.__col.controls.extend([
                Divider(height=10,color="transparent"),
                ElevatedButton("Confirm", on_click=self.__upload)
            ])
        return self.__stack
