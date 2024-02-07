from flet import *
from assets.colours import Colours

BACKGROUND_COLOUR, THEME_COLOUR, TEXT_COLOUR, BACKGROUND_COLOUR_2= Colours().get_colours()

class CodeSharer(UserControl):
    def __init__(self, homepage,code):
        super().__init__()
        self.__code = code
        self.__homepage = homepage
    
    def __back(self,e):
        self.__homepage.get_navrail().set_selected_index(0)
        self.__homepage.get_navrail().get_nav().update()
        self.__homepage.destination_change(None)

    def __download_extension(self,e):
        self.__homepage.go_to_url("https:\\www.google.com")

    def __copy_code(self,e):
        self.__homepage.copy_to_clipboard(self.__code)

    def build(self):
        self.__back_button = IconButton(icon=icons.ARROW_BACK,on_click=self.__back)
        self.__col = Column(
            controls=[
                Row(
                    controls=[
                        self.__back_button,
                        Text(
                            value="Link Browser Extension", 
                            size=30, weight=FontWeight.BOLD, font_family="Afacad", color=TEXT_COLOUR
                        ),
                        VerticalDivider(color="transparent",width=30),
                    ],
                    spacing=20,
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=CrossAxisAlignment.CENTER,
                ),
                Divider(height=20,color="transparent"),
                Icon(icons.PRIVATE_CONNECTIVITY_ROUNDED, color=TEXT_COLOUR, size=60),
                Divider(height=10,color="transparent"),
                Text(
                    value="Enter this code into your browser extension:",
                    size=20, font_family="Afacad", color=TEXT_COLOUR
                ),
                Divider(height=10,color="transparent"),
                # Divider(height=2,color=TEXT_COLOUR),
                Row(
                    controls=[
                        IconButton(icons.COPY, on_click=self.__copy_code),
                        Text(
                            value=self.__code, 
                            size=40,weight=FontWeight.BOLD, font_family="Afacad", color=TEXT_COLOUR
                        ),
                    ],
                    alignment=MainAxisAlignment.CENTER,
                    vertical_alignment=CrossAxisAlignment.CENTER,
                ),
                # Divider(height=2,color=TEXT_COLOUR),
                Divider(height=50,color="transparent"),
                ElevatedButton(
                    text="Download Extension",
                    icon=icons.CLOUD_DOWNLOAD,
                    on_click = self.__download_extension
                ),
            ],
            spacing=20,
            alignment=MainAxisAlignment.START,
            horizontal_alignment=CrossAxisAlignment.CENTER,
        )
        return self.__col
