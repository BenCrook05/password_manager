from flet import *
from pages.components.pro_ring import ProRing
import sqlite3
import socket
from assets.colours import Colours

BACKGROUND_COLOUR, THEME_COLOUR, TEXT_COLOUR, BACKGROUND_COLOUR_2= Colours().get_colours()


class Updater(UserControl):
    def __init__(self, homepage, passID, type):
        super().__init__()
        self.__homepage = homepage
        self.__passID = passID
        self.__type = type
        self.__processing = False
        
    def __update(self,e):
        if not self.__processing:
            self.__processing = True
            
            temp_title = self.__title_input_field.value
            temp_password = self.__password_input_field.value
            try:
                temp_username = self.__username_input_field.value
                temp_url = self.__url_input_field.value
                temp_additional_info = self.__additional_info_input_field.value
            except:
                temp_username = None
                temp_url = None
                temp_additional_info = None
            
            
            update_list = [] #uses list to store values before updating at end if no errors
            updated = False
            self.__title_input_field.error_text = None
            self.__password_input_field.error_text = None
            if self.__type == "password":
                self.__url_input_field.error_text = None
                self.__username_input_field.error_text = None
            
            if temp_title != self.__title:
                if temp_title == "":
                    self.__title_input_field.error_text = ("Title required")
                    self.__title_input_field.update()
                    self.__processing = False
                    return
                else:
                    update_list.append([self.__passID,temp_title,"Title"])
                    updated = True
                    
            if temp_password != self.__password:
                if temp_password == "":
                    self.__password_input_field.error_text = ("Password required")
                    self.__password_input_field.update()
                    self.__processing = False
                    return
                else:
                    update_list.append([self.__passID,temp_password,"Password"])
                    updated = True
                    
            
            if temp_username != self.__username:
                if temp_username == "":
                    self.__username_input_field.error_text = ("Username required")
                    self.__username_input_field.update()
                    self.__processing = False
                    return
                else:
                    update_list.append([self.__passID,temp_username,"Username"])
                    updated = True
                    
            if temp_url != self.__url:
                if temp_url == "":
                    self.__url_input_field.error_text = ("URL required")
                    self.__url_input_field.update()
                    self.__processing = False
                    return
                else:
                    update_list.append([self.__passID,temp_url,"URL"])
                    updated = True
                    
            if temp_additional_info != self.__additional_info:
                update_list.append([self.__passID,temp_additional_info,"AdditionalInfo"])
                updated = True
                
            if updated:
                for update_query in update_list:
                    print(f"updating {update_query[2]} to {update_query[1]} for {update_query[0]}")
                    self.__homepage.get_manager().update_password(update_query[0],update_query[1],update_query[2])
                self.__homepage.refresh()
    
    def __back(self,e):
        # self.__homepage.destination_change(None)
        self.__homepage.view_password(None,self.__passID,self.__type)
        
    def build(self):
        #able to call password again as it has already downloaded so is in the cache    
        data = self.__homepage.get_manager().get_specific_password_info(self.__passID)
        self.__password = data[0]
        self.__title = data[1]
        
        if self.__type == "password":
            self.__username = data[2]
            self.__url = data[4]
            self.__additional_info = data[5]
            
            self.__username_input_field = TextField(
                label="Username",
                value=self.__username,
                max_length=32,
                border_color=TEXT_COLOUR,
                width=350,
            )
            self.__url_input_field = TextField(
                label="URL",
                value=self.__url,
                max_length=128,
                border_color=TEXT_COLOUR,
                width=350,
            )
            self.__additional_info_input_field = TextField(
                label="Additional Info",
                value=self.__additional_info,
                max_length=256,
                border_color=TEXT_COLOUR,
                width=350,
            )
        
        elif self.__type == "info":
            self.__username = None
            self.__url = None
            self.__additional_info = None
            
            self.__username_input_field = None
            self.__url_input_field = None
            self.__additional_info_input_field = None
            
        try:
            db = sqlite3.connect(rf"assets\assetdata.db")
            curs = db.cursor()
            curs.execute(f"SELECT Icon FROM Icons where URL='{self.__url}'")
            image_content = curs.fetchone()[0]
            curs.close()
            db.close()
                
            self.__img = Image(src_base64=image_content, height=50, width=50)
            
        except Exception as e:
            print(e)
            self.__img = Icon(icons.PERSON_ROUNDED, color=TEXT_COLOUR, size=50)
        
        self.__title_input_field = TextField(
            label="Title",
            value=self.__title,
            max_length=32,
            border_color=TEXT_COLOUR,
            width=350,
        )
        self.__password_input_field = TextField(
            label="Password",
            value=self.__password,
            password=True,
            can_reveal_password=True,
            max_length=32,
            border_color=TEXT_COLOUR,
            width=350,
        )
   
        self.__back_button = IconButton(icon=icons.ARROW_BACK,on_click=self.__back)
        self.__update_button = ElevatedButton(icon=icons.UPDATE_ROUNDED, text="Update",on_click=self.__update)
        self.__col = Column(
            controls=[
                Row(
                    controls=[
                        self.__back_button,
                        Icon(icons.TIPS_AND_UPDATES_OUTLINED,size=50,color=TEXT_COLOUR),
                        VerticalDivider(color="transparent",width=33),
                    ],
                    spacing=20,
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=CrossAxisAlignment.CENTER,
                ),
                Divider(height=10,color="transparent"),
                self.__img,
                Divider(height=10,color="transparent"),
                self.__title_input_field,
                self.__password_input_field,
            ],
            spacing=20,
            alignment=MainAxisAlignment.START,
            horizontal_alignment=CrossAxisAlignment.CENTER,
        )
        if self.__type == "password":
            self.__col.controls.extend([
                self.__username_input_field,
                self.__url_input_field,
                self.__additional_info_input_field,
            ])
        self.__col.controls.extend([
            Divider(height=10,color="transparent"),
                Row(
                    controls=[
                        VerticalDivider(color="transparent",width=1),
                        self.__update_button,
                        VerticalDivider(color="transparent",width=1),
                    ],
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=CrossAxisAlignment.CENTER,
                )
        ])                                     

        return self.__col