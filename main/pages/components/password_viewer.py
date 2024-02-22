from flet import *
import sqlite3
import socket
from assets.colours import Colours

BACKGROUND_COLOUR, THEME_COLOUR, TEXT_COLOUR, BACKGROUND_COLOUR_2= Colours().get_colours()




class Viewer(UserControl):
    def __init__(self, homepage, passID, password, manager,type):
        super().__init__()
        self._type = type
        self._homepage = homepage
        self._passID = passID
        self._current_password = password
        self._current_manager = manager
        self._current_password_viewing = TextButton(content=Text(' '.join(['•'] * len(self._current_password)),size=20,weight=FontWeight.BOLD),disabled=True)
        self._visibility_icon = IconButton(icons.VISIBILITY_OFF,icon_size=25,on_click=self._unhide_password_viewing)
        self._manager_checkbox = Checkbox(value = True if self._current_manager == 1 else False,disabled=False,on_change=self._return_to_on)
        self._help_button = IconButton(icons.HELP_OUTLINE_ROUNDED,icon_size=25,on_click=self._homepage.help)

    def _unhide_password_viewing(self,e):
        if self._current_password_viewing.content.value == ' '.join(['•'] * len(self._current_password)):
            self._current_password_viewing.content.value = self._current_password
            self._current_password_viewing.disabled=False
            self._visibility_icon.icon = icons.VISIBILITY
        else:
            self._current_password_viewing.content.value = ' '.join(['•'] * len(self._current_password))
            self._current_password_viewing.disabled=True
            self._visibility_icon.icon = icons.VISIBILITY_OFF
        self._container_col.update()

    def _return_to_on(self,e):
        self._manager_checkbox.value = True if self._current_manager == 1 else False
        self._container_col.update()

    

    def build_full(self, col, img):
        self._col = col
        self._img = img
        self._share_button = ElevatedButton(
            icon=icons.SHARE,
            text="Share",
            disabled=True,
            on_click=lambda _: self._homepage.share_password(self._passID, self._type)
        )
        self._edit_button = ElevatedButton(
            icon=icons.EDIT,
            text="Edit",
            disabled=True,
            on_click=lambda _: self._homepage.edit_password(self._passID, self._type)
        )
        self._set_lockdown_button = IconButton(
            icon=icons.LOCK,
            on_click=lambda _: self._homepage.set_lockdown(self._passID,self._type), 
            icon_color="red"
        )
        self._delete_divider = Divider(
            height=50,
            color="transparent"
        )
        self._delete_button = ElevatedButton(
            icon=icons.DELETE,
            text="Delete",
            on_click=lambda _: self._homepage.delete_password(self._passID,self._type,self._current_manager),
            color="red"
        )
        self._manage_users_button = ElevatedButton(
            icon=icons.PEOPLE,
            text="Manage Users",
            disabled=True,
            on_click=lambda _: self._homepage.manage_users(self._passID,self._type)
        )
        
        if self._current_manager == 1:  #disabled if not manager
            self._share_button.disabled = False
            self._edit_button.disabled = False
            self._manage_users_button.disabled = False
            
        self._container_col = Column(controls=[
            Row(
                controls=[
                    self._edit_button,
                    self._share_button,
                    self._manage_users_button,
                    self._set_lockdown_button,
                ],spacing=30,
            ),
            Divider(height=10,color="transparent"),
            Row(
                controls=[
                    VerticalDivider(color="transparent",width=1),
                    self._img,
                    VerticalDivider(color="transparent",width=1),
                ],
                alignment=MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=CrossAxisAlignment.CENTER,
            ),
            Divider(height=10,color="transparent"),
            self._col,
            self._delete_divider,
            Row(
                controls=[
                    self._delete_button,
                ],alignment=MainAxisAlignment.CENTER,width=self._homepage.get_main_container_width()-30,
            ),
        ])
        
        return self._container_col



class PasswordViewer(Viewer):
    def __init__(self, homepage, passID, title, password, username, url, manager, additional_info):
        super().__init__(homepage, passID, password, manager, type="password")
        self.__current_title = title
        self.__current_username = username
        self.__url = url
        self.__current_additional_info = additional_info
        
    def build(self):
        self._col = Column(
            controls=[
                Row(
                    controls=[
                        Row(alignment=MainAxisAlignment.CENTER, spacing=20,controls=[
                            IconButton(icons.CONTENT_COPY,icon_size=18,on_click=lambda _: self._homepage.copy_to_clipboard(self.__current_title)),
                            Text("Title:",size=15,),
                        ]),
                        Text(self.__current_title,size=20,weight=FontWeight.BOLD,color=TEXT_COLOUR),
                    ],
                    spacing=20,
                    vertical_alignment=CrossAxisAlignment.CENTER,
                    alignment = MainAxisAlignment.SPACE_BETWEEN,
                ),
                Divider(opacity=0.5, thickness=2, color=TEXT_COLOUR),
                Row(
                    controls=[
                        Row(alignment=MainAxisAlignment.CENTER, spacing=20,controls=[
                            IconButton(icons.CONTENT_COPY,icon_size=18,on_click=lambda _: self._homepage.copy_to_clipboard(self._current_password)),
                            Text("Secrets:",size=15,),
                        ]),
                        Row(alignment=MainAxisAlignment.CENTER, spacing=20,controls=[
                            self._current_password_viewing,
                            self._visibility_icon,
                        ]),
                    ],
                    spacing=20,
                    vertical_alignment=CrossAxisAlignment.CENTER,
                    alignment = MainAxisAlignment.SPACE_BETWEEN
                ),
                Divider(opacity=0.5, thickness=2, color=TEXT_COLOUR),
                Row(
                    controls=[
                        Row(alignment=MainAxisAlignment.CENTER, spacing=20,controls=[
                            IconButton(icons.CALL_MISSED_OUTGOING_ROUNDED,icon_size=18,on_click=lambda _: self._homepage.go_to_url("https:\\"+self.__url)),
                            Text("URL:",size=15,),
                        ]),
                        Text(self.__url,size=20,weight=FontWeight.BOLD,color=TEXT_COLOUR),
                    ],
                    spacing=20,
                    vertical_alignment=CrossAxisAlignment.CENTER,
                    alignment = MainAxisAlignment.SPACE_BETWEEN
                ),
                Divider(opacity=0.5, thickness=2, color=TEXT_COLOUR),
                Row(
                    controls=[
                        Row(alignment=MainAxisAlignment.CENTER, spacing=20,controls=[
                            IconButton(icons.CONTENT_COPY,icon_size=18,on_click=lambda _: self._homepage.copy_to_clipboard(self.__current_username)),
                            Text("Username:",size=15),
                        ]),
                        Text(self.__current_username,size=20,weight=FontWeight.BOLD,color=TEXT_COLOUR),
                    ],
                    spacing=20,
                    vertical_alignment=CrossAxisAlignment.CENTER,
                    alignment = MainAxisAlignment.SPACE_BETWEEN
                ),
                Divider(opacity=0.5, thickness=2, color=TEXT_COLOUR),
                Row(
                    controls=[
                        Row(alignment=MainAxisAlignment.CENTER, spacing=20,controls=[
                            self._help_button,
                            Text("Manager:",size=15,),
                        ]),
                        self._manager_checkbox,
                    ],
                    spacing=20,
                    vertical_alignment=CrossAxisAlignment.CENTER,
                    alignment = MainAxisAlignment.SPACE_BETWEEN
                ),
                Divider(opacity=0.5, thickness=2, color=TEXT_COLOUR),
                Row(
                    controls=[
                        IconButton(icons.CONTENT_COPY,icon_size=18,on_click=lambda _: self._homepage.copy_to_clipboard(self.__current_additional_info)),
                        Text("Additional Info:",size=15,),
                    ],
                    spacing=20,
                    vertical_alignment=CrossAxisAlignment.CENTER,
                    alignment = MainAxisAlignment.SPACE_BETWEEN
                ),
                Row(
                    controls=[
                        VerticalDivider(color="transparent",width=40),
                        Text(self.__current_additional_info,size=14,color=TEXT_COLOUR),
                    ],
                    spacing=20,
                    vertical_alignment=CrossAxisAlignment.CENTER,
                    alignment = MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            spacing=4,
            scroll=ScrollMode.AUTO,
        )
        #image stored in data is already used. Since this is only requesting one image it is quick enough to load from the db
        try:
            db = sqlite3.connect(rf"assets\assetdata.db")
            curs = db.cursor()
            curs.execute(f"SELECT Icon FROM Icons where URL='{self.__url}'")
            image_content = curs.fetchone()[0]
            curs.close()
            db.close()
                
            self._img = Image(src_base64=image_content, height=50, width=50)
                
        except Exception as e:
            print(e)
            self._img = Icon(icons.PERSON_ROUNDED, color=TEXT_COLOUR, size=50)
        
        return super().build_full(self._col, self._img)
       
    
class InfoViewer(Viewer):
    def __init__(self, homepage, title, passID, password, manager):
        super().__init__(homepage, passID, password, manager, type="info")
        self.__current_title = title
   
    def build(self):
        self._col = Column(
            controls=[
                Row(
                    controls=[
                        Row(alignment=MainAxisAlignment.CENTER, spacing=20,controls=[
                            IconButton(icons.CONTENT_COPY,icon_size=18,on_click=lambda _: self._homepage.copy_to_clipboard(self.__current_title)),
                            Text("Title:",size=15),
                        ]),
                        Text(self.__current_title,size=20,weight=FontWeight.BOLD),
                    ],
                    spacing=20,
                    vertical_alignment=CrossAxisAlignment.CENTER,
                    alignment = MainAxisAlignment.SPACE_BETWEEN
                ),
                Divider(opacity=0.5, thickness=2, color=TEXT_COLOUR),
                Row(
                    controls=[
                        Row(alignment=MainAxisAlignment.CENTER, spacing=20,controls=[
                            IconButton(icons.CONTENT_COPY,icon_size=18,on_click=lambda _: self._homepage.copy_to_clipboard(self._current_password)),
                            Text("Secrets:",size=15,),
                        ]),
                        Row(alignment=MainAxisAlignment.CENTER, spacing=20,controls=[
                            self._current_password_viewing,
                            self._visibility_icon,
                        ]),
                    ],
                    spacing=20,
                    vertical_alignment=CrossAxisAlignment.CENTER,
                    alignment = MainAxisAlignment.SPACE_BETWEEN
                ),
                Divider(opacity=0.5, thickness=2, color=TEXT_COLOUR),
                Row(
                    controls=[
                        Row(alignment=MainAxisAlignment.CENTER, spacing=20,controls=[
                            self._help_button,
                            Text("Manager: ",size=15,),
                        ]),
                        self._manager_checkbox,
                    ],
                    spacing=20,
                    vertical_alignment=CrossAxisAlignment.CENTER,
                    alignment = MainAxisAlignment.SPACE_BETWEEN
                ),
            ],
            spacing=10,
        )
        
        self._img = Icon(icons.PERSON_ROUNDED, color=TEXT_COLOUR, size=50)
        
        return super().build_full(self._col,self._img)