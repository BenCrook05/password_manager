from flet import *
import sqlite3
import socket
from assets.colours import Colours

BACKGROUND_COLOUR, THEME_COLOUR, TEXT_COLOUR, BACKGROUND_COLOUR_2= Colours().get_colours()


class PasswordRow(UserControl):
    def __init__(self, username, title, rating, repeated, passID, url, function):
        super().__init__()
        self.__username = username
        self.__title = title
        self.__rating = rating
        self.__repeated = repeated
        self.__passID = passID
        self.__function = function
        if url == "":
            self.__type = "info"
        else:
            self.__type = "password"
        self.__url = url
        self.__slider = Slider()
        self.__repeated_alert = Text()
        self.__img = Image()
        self.__container = Container()
        
            
    def get_type(self):
        return self.__type

    def __go_to_password(self,e):
        self.__function(self.__passID,self.__type)
    
    def __reset_slider(self,e):
        self.__slider.value = self.__rating
        self.__slider.update()
    
    def build(self):
        self.__slider = Slider(
            max=1,
            value=self.__rating,
            width=200,
            on_change=self.__reset_slider,
            inactive_color="grey",
        )
        red = 255 * (1 - self.__rating)
        green = 255 * self.__rating
        blue = 0  # Since it's a red-green gradient, blue will be 0
        hex_color = "#{:02X}{:02X}{:02X}".format(int(red), int(green), int(blue))
        self.__slider.thumb_color = hex_color
        self.__slider.active_color = hex_color
        self.__repeated_alert = Text(value="             ",color="#FF0000", 
                                     #needs filler if no repeat alert for alignment
                                     size=15,weight=FontWeight.BOLD,font_family="Afacad")
        
        try:
            db = sqlite3.connect(rf"assets\assetdata.db")  
            curs = db.cursor()
            curs.execute(f"SELECT Icon FROM Icons where URL='{self.__url}'")
            image_content = curs.fetchone()[0]
            curs.close()
            db.close()
            self.__img = Image(src_base64=image_content, height=20, width=20)
        except Exception as e:
            self.__img = Icon(icons.PERSON_ROUNDED,size=20,color=TEXT_COLOUR)
            
        if self.__repeated:
            self.__slider.thumb_color = "#FF0000"
            self.__slider.active_color = "#FF0000"
            self.__repeated_alert.value = "Repeat!"
            
        self.__container = Container(
            content=Row(
                controls=[
                    Row(
                        controls=[
                            self.__img,
                            Text(
                                value=self.__title[-20:], #only uses first 20 characters
                                size=20,
                                # weight=FontWeight.BOLD,
                                font_family="Afacad",
                                color=TEXT_COLOUR,
                            ),
                        ],
                        spacing=10,
                        alignment=MainAxisAlignment.START,
                        vertical_alignment=CrossAxisAlignment.CENTER,
                    ),
                    Row(
                        controls=[
                            VerticalDivider(width=1, color="transparent"),
                            self.__slider,
                            VerticalDivider(width=1, color="transparent"),
                            self.__repeated_alert,
                        ],
                        spacing=10,
                        alignment=MainAxisAlignment.END,
                        vertical_alignment=CrossAxisAlignment.CENTER,
                    ),
                ],
                spacing=10,
                alignment=MainAxisAlignment.SPACE_BETWEEN,
            ),
            on_click=self.__go_to_password,
            bgcolor="transparent",
            margin=5,
            height=40,
        )
        return self.__container
        


class Scanner(UserControl):
    def __init__(self, homepage, data):
        super().__init__()
        self.__homepage = homepage
        self.__data = data
        self.__back_button = IconButton()
        self.__col = Column()
        self.__password_row_list = []
        self.__rating_container = Column()
    
    def __view_password(self,passID,type):
        self.__homepage.view_password(None,passID,type)
    
   
    def __back(self,e):
        self.__homepage.get_navrail().set_selected_index(0)
        self.__homepage.get_navrail().get_nav().update()
        self.__homepage.destination_change(None)
            
    def build(self):
        data = self.__homepage.get_manager().scan_passwords()
        self.__password_row_list = list(
            map( #map to a password row for every password
                lambda password: PasswordRow(
                    username=password["username"],
                    title=password["title"],
                    rating=password["rating"],
                    repeated=password["repeated"],
                    passID=password["passID"],
                    url=password["url"],
                    function=self.__view_password,
                ), 
                data,
            )
        )
        container_width = self.__homepage.get_main_container_width() - 30
        container_height = self.__homepage.get_main_container_height() - 300
        self.__rating_container = Column(
            controls=[
            ],
            alignment=MainAxisAlignment.START,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            scroll=ScrollMode.AUTO,
            spacing=1,
        )
        
        
        self.__back_button = IconButton(icon=icons.ARROW_BACK,on_click=self.__back)
        self.__col = Column(
            controls=[
                Row(
                    controls=[
                        self.__back_button,
                        Icon(icons.SAFETY_CHECK_OUTLINED,size=50,color=TEXT_COLOUR),
                        VerticalDivider(width=30, color=TEXT_COLOUR),
                    ],
                    spacing=20,
                    vertical_alignment=CrossAxisAlignment.START,
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                ),
                Divider(height=35,color="transparent"),
                Container(
                    content=(
                        self.__rating_container
                    ),
                    bgcolor=BACKGROUND_COLOUR_2,
                    border=border.all(1, TEXT_COLOUR),
                    border_radius=10,
                    padding=20,
                    width=container_width,
                    height=container_height+150, 
                    margin=5,
                ),
            ],
            spacing=3,
            alignment=MainAxisAlignment.START,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            
        )

        for info_row in self.__password_row_list:
            if info_row.get_type() == "password":
                self.__rating_container.controls.append(info_row)
                self.__rating_container.controls.append(
                    Divider(height=2,color=TEXT_COLOUR)
                )
        
        return self.__col