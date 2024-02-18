from flet import *
from pages.components.pro_ring import ProRing
from pages.components.inputs import Input
from assets.colours import Colours

BACKGROUND_COLOUR, THEME_COLOUR, TEXT_COLOUR, BACKGROUND_COLOUR_2= Colours().get_colours()


class Deleter(UserControl):
    def __init__(self, homepage, data, passID, type, manager):
        super().__init__()
        self.__homepage = homepage
        self.__data = data
        self.__passID = passID
        self.__type = type
        self.__manager = manager
        self.__processing = False
        
    def __back(self,e):
        self.__homepage.view_password(None,self.__passID,self.__type)
        
    def __delete_instance(self,e):
        if not self.__processing:
            self.__processing = True
            self.__stack.controls.append(ProRing())
            self.__stack.update()
            try:
                new_manager_email = self.__new_manager_email_input.get_value()
                if new_manager_email != self.__data["email"]:
                    data = self.__homepage.get_manager().delete_password_instance(self.__passID, new_manager_email)
                    print(data)
                    if data == "DELETED PASSWORD INSTANCE":
                        self.__homepage.get_page().snack_bar = SnackBar(
                            content=Text("Password Instance Deleted",color=TEXT_COLOUR),
                            bgcolor=BACKGROUND_COLOUR_2,
                            elevation=5,
                            margin=5,
                            duration=3000,
                        )
                        self.__homepage.get_page().snack_bar.open = True
                        self.__homepage.get_page().update()
                        self.__homepage.refresh()
                else:
                    self.__homepage.get_page().snack_bar = SnackBar(
                        content=Text("Separate account required.",color=TEXT_COLOUR),
                        bgcolor=BACKGROUND_COLOUR_2,
                        elevation=5,
                        margin=5,
                    )
                    self.__homepage.get_page().snack_bar.open = True
                    self.__homepage.get_page().update()
                    self.__new_manager_email_input.set_value("")
                    self.__new_manager_email_input.update()
                    self.__stack.controls.pop()
                    self.__stack.update()
                    self.__processing = False
            except Exception as e:
                data = self.__homepage.get_manager().delete_password_instance(self.__passID)
                print(data)
                if data == "New manager email required":
                    self.__col.controls.insert(6,Text("New manager required or delete password entirely.", size=12, font_family="Afacad", color="red"))
                    self.__new_manager_email_input = Input(icons.EMAIL, hint="New Manager Email")
                    self.__col.controls.insert(7,self.__new_manager_email_input)
                    self.__stack.controls.pop()
                    self.__col.update()
                    self.__stack.update()
                    self.__processing = False
                elif "DELETED PASSWORD INSTANCE" in data:
                    self.__homepage.get_page().snack_bar = SnackBar(
                        content=Text("Password Instance Deleted",color=TEXT_COLOUR),
                        bgcolor=BACKGROUND_COLOUR_2,
                        elevation=5,
                        margin=5,
                        duration=3000,
                    )
                    self.__homepage.get_page().snack_bar.open = True
                    self.__homepage.get_page().update()
                    self.__homepage.refresh()
                elif data == "NEED TO SHARE":
                    print("need to share")
                    self.__homepage.get_page().snack_bar = SnackBar(
                        content=Text("Password must be already shared with new manager",color=TEXT_COLOUR),
                        bgcolor=BACKGROUND_COLOUR_2,
                        elevation=5,
                        margin=5,
                    )
                    self.__homepage.get_page().snack_bar.open = True
                    self.__homepage.get_page().update()
                    self.__homepage.view_password(None,self.__passID,self.__type)
                else:
                    self.__homepage.get_page().snack_bar = SnackBar(
                        content=Text("Password deletion failed",color=TEXT_COLOUR),
                        bgcolor=BACKGROUND_COLOUR_2,
                        elevation=5,
                        margin=5,
                        duration=3000,
                    )
                    self.__homepage.get_page().snack_bar.open = True
                    self.__homepage.get_page().update()
                    self.__homepage.refresh()
                    
                   
        
    def __delete(self,e):
        if not self.__processing:
            self.__processing = True
            self.__stack.controls.append(ProRing())
            self.__stack.update()
            data = self.__homepage.get_manager().delete_password(self.__passID)
            if data == "DELETED PASSWORD":
                self.__homepage.get_page().snack_bar = SnackBar(
                    content=Text("Password Deleted",color=TEXT_COLOUR),
                    bgcolor=BACKGROUND_COLOUR_2,
                    elevation=5,
                    margin=5,
                    duration=3000,
                )
                self.__homepage.get_page().snack_bar.open = True
                self.__homepage.get_page().update()
                self.__homepage.refresh()
            else:
                self.__homepage.get_page().snack_bar = SnackBar(
                    content=Text("Password deletion failed",color=TEXT_COLOUR),
                    bgcolor=BACKGROUND_COLOUR_2,
                    elevation=5,
                    margin=5,
                    duration=3000,
                )
                self.__homepage.get_page().snack_bar.open = True
                self.__homepage.get_page().update()
                self.__homepage.refresh()
        
    def build(self):
        self.__back_button = IconButton(icon=icons.ARROW_BACK,on_click=self.__back)

        self.__col = Column(
            controls=[
                Row(
                    controls=[
                        self.__back_button,
                        Icon(icons.DELETE_FOREVER_OUTLINED, size=50, color=TEXT_COLOUR),
                        VerticalDivider(color="transparent",width=1),
                    ],
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=CrossAxisAlignment.CENTER,
                ),
                Divider(height=10,color="transparent"),
                Divider(height=1,color=TEXT_COLOUR),
            ],
            spacing=20,
            alignment=MainAxisAlignment.START,
            horizontal_alignment=CrossAxisAlignment.CENTER,
        )
        
        self.__delete_instance_button = ElevatedButton(
            icon=icons.DELETE,
            text="Delete Instance",
            width=200,
            height=30,
            color="red",
            on_click=self.__delete_instance,
        )
    
        if self.__manager == 1:
            self.__delete_button = ElevatedButton(
                icon=icons.DELETE,
                text="Delete Password",
                width=200,
                height=30,
                color="red",
                on_click=self.__delete,
            )

            self.__col.controls.extend([
                Text("Delete all instances of password for all users?", size=15, font_family="Afacad", color=TEXT_COLOUR),
                self.__delete_button,
                Divider(height=10,color="transparent"),
                Text("Delete only your instance of password?", size=15, font_family="Afacad", color=TEXT_COLOUR),
                self.__delete_instance_button,
            ])
            
        else:
            self.__col.controls.extend([
                Text("Delete password from your account?", size=15, font_family="Afacad", color=TEXT_COLOUR),
                self.__delete_instance_button,
            ])
            
        self.__stack = Stack(
            controls=[
                self.__col,
            ],
        )
        return self.__stack