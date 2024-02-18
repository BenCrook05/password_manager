from flet import *
import requests
import sqlite3
import socket
import base64
from assets.colours import Colours

BACKGROUND_COLOUR, THEME_COLOUR, TEXT_COLOUR, BACKGROUND_COLOUR_2= Colours().get_colours()

def fetch_favicon(url):
    print("Loading favicon")
    size=64
    favicon_url = f"https://www.google.com/s2/favicons?sz={size}&domain={url}"
    try:
        response = requests.get(favicon_url)
        if response.status_code == 200: #checks request was good
            return response.content  
        else:
            raise requests.RequestException
    except requests.RequestException as e:
        print(f"Request failed for URL {url}: {e}")
        return None

class PasswordCard(UserControl):
    def __init__(self, homepage, title, passID, username, url):
        super().__init__()
        self.__homepage = homepage
        self.__data = self.__homepage.get_data()
        self.__title = title
        self.__passID = passID
        self.__username = username
        self.__url = url
        self.__img = None
    
    def get_title(self):
        return self.__title
    
    def get_username(self):
        return self.__username
    
    def get_url(self):
        return self.__url
    
    def show(self):
        self.__card.visible = True
        self.__card.update()
        
    def hide(self):
        self.__card.visible = False
        self.__card.update()
        
    def download_icon(self):
        print("Downloading icon")
        #prevents loading favicon multiple times for same card
        self.__card.content.content.controls[0].controls.remove(self.__img)
        try:  # first tries to get icon data from data object
            self.__img = self.__data["self.__url"]
        except Exception as e:
            #not stored in local dictionary
            try:  # then tries to get icon data from file
                db = sqlite3.connect(rf"assets\assetdata.db")
                curs = db.cursor()
                curs.execute(f"SELECT Icon FROM Icons where URL='{self.__url}'")
                image_content = curs.fetchone()[0]
                curs.close()
                db.close()
                self.__img = Image(src_base64=image_content, height=32, width=32)
                self.__data[self.__url] =  self.__img
                    
            except Exception as e:  # if no icon data on the computer yet, uses API
                # print(e)
                favicon_content = fetch_favicon(self.__url)
                if favicon_content:
                    favicon_content = base64.b64encode(favicon_content).decode("utf-8")
                    self.__img = Image(src_base64=favicon_content, height=32, width=32)
                    
                    db = sqlite3.connect(rf"assets\assetdata.db")
                    curs = db.cursor()
                    curs.execute('CREATE TABLE IF NOT EXISTS Icons(URL VARCHAR(128) primary key, Icon VARCHAR(8192))')
                    curs.execute(f'INSERT INTO Icons VALUES("{self.__url}","{favicon_content}")')
                    curs.close()
                    db.commit()
                    db.close()

                    self.__data[self.__url] =  self.__img
                else:
                    self.__img = Icon(icons.PERSON, color=TEXT_COLOUR, size=32)
                    self.__data[self.__url] =  self.__img
        self.__card.content.content.controls[0].controls.insert(1,self.__img)
        self.__card.update()
        
    def build(self):
        if len(self.__title) > 20:
            self.__showing_title = self.__title[:20] + "..."
        else:
            self.__showing_title = self.__title
        if len(self.__username) > 25:
            self.__showing_username = self.__username[:25] + "..."
        else:
            self.__showing_username = self.__username
            
        self.__card = Card(
                elevation=4,
                margin=5,
                height=70,
                content=Container(
                    # using id=passID binds passID to the lambda function so when called it uses the correct passID
                    # otherwise it will call passID from latest card_container
                    on_click=lambda _, id=self.__passID: self.__homepage.view_password(_,id,"password"), 
                    bgcolor=BACKGROUND_COLOUR_2,
                    padding=0,
                    border_radius=10,
                    content=Row(
                        controls=[
                            Row(
                                controls=[
                                    VerticalDivider(color="transparent",width=1),
                                    VerticalDivider(color="transparent",width=6),
                                    Column(
                                        controls=[
                                            Text(self.__showing_title,size=19,weight=FontWeight.BOLD,font_family="Afacad"),
                                            Text(self.__showing_username,size=13, opacity=0.7),
                                        ],
                                        alignment=MainAxisAlignment.CENTER,
                                        horizontal_alignment=CrossAxisAlignment.START,
                                        spacing=1,
                                    ),
                                ],
                                alignment=MainAxisAlignment.START,
                                vertical_alignment=CrossAxisAlignment.CENTER,
                                spacing=9,
                            ),
                            
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=CrossAxisAlignment.CENTER,
                    )
                )
            )
        self.__img = Icon(icons.PERSON, color=TEXT_COLOUR, size=32)
        self.__card.content.content.controls[0].controls.insert(1,self.__img)
        return self.__card


class InfoCard(UserControl):
    def __init__(self, homepage, title, passID):
        super().__init__()
        self.__homepage = homepage
        self.__title = title
        self.__passID = passID
        
    def get_title(self):
        return self.__title
    
    def show(self):
        self.__card.visible = True
        self.__card.update()
        
    def hide(self):
        self.__card.visible = False
        self.__card.update()

    def build(self):
        if len(self.__title) > 20:
            self.__showing_title = self.__title[:20] + "..."
        else:
            self.__showing_title = self.__title
            
        self.__card = Card(
            elevation=4,
            margin=5,
            height=60,
            content=Container(
                on_click=lambda _, id=self.__passID: self.__homepage.view_password(_,id,"info"),
                bgcolor=BACKGROUND_COLOUR_2,
                padding=10,
                border_radius=10,
                content=Row(
                    controls=[
                        Text(self.__showing_title,size=20,weight=FontWeight.BOLD,font_family="Afacad"),
                        Text("")
                    ],
                    alignment=MainAxisAlignment.START,
                    vertical_alignment=CrossAxisAlignment.CENTER,
                )
            ),
        )
        
        self.__img = Icon(icons.PERSON, color=TEXT_COLOUR, size=32)
        self.__card.content.content.controls.insert(0,self.__img)
        return self.__card