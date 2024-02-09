from flet import *
import sqlite3
import random
import traceback
import socket
from backEnd.hasher import Hash
from backEnd.encryption import Generate
from backEnd.basemanager import Manager
from pages.components.password_cards import PasswordCard, InfoCard
from pages.components.pro_ring import ProRing
from pages.components.nav_rail import NavSideRail
from pages.components.password_viewer import PasswordViewer, InfoViewer
from pages.components.adder import PasswordAdder
from pages.components.updater import Updater
from pages.components.sharer import Sharer
from pages.components.receiver import ReceiveShared
from pages.components.deleter import Deleter
from pages.components.viewusers import ViewUsers
from pages.components.lockdown import Lockdown
from pages.components.settings import Settings
from pages.components.codesharer import CodeSharer
from pages.components.scanner import Scanner
from assets.colours import Colours
BACKGROUND_COLOUR, THEME_COLOUR, TEXT_COLOUR, BACKGROUND_COLOUR_2= Colours().get_colours()
import pyperclip
import threading



class Home(UserControl):
    def __init__(self, page, data):
        super().__init__()
        self.__page = page
        self.__data = data
        self.__password_list = []
        self.__info_list = []
        self.__manager = None
        self.__on_home = False
        self.__passwords_hidden = False
        self.__infos_hidden = False
        self.__processing = False  #used to prevent multiple requests simultaneously
        self.__email = None
        self.__password = None
        self.__code = None
        self.__current_passID = None
        self.__current_password = None
        self.__current_title = None
        self.__current_username = None
        self.__current_manager = None
        self.__current_url = None
        self.__current_additional_info = None
        self.__navrail = None
        self.__main_container = None
        self.__password_list_container = None
        self.__height = None
        self.__unable_to_logout = False
        #other attributes created in build() don't need referencing before build() is called        
        self.__setup()
        
        
    def __setup(self):
        try:
            self.__email = self.__data.get_data('email') #will fail when first run from view due to no data
            self.__password = self.__data.get_data('password')
            self.__on_home = True
            self.__code = str(random.randint(10000,99999))
            self.__data.add_data("extensioncode",str(self.__code))
            try:
                server_public_key = self.__data.get_data("server_public_key")
                session_key = self.__data.get_data("session_key")
                
                client_permanent_key = Hash.create_client_permanent_key(self.__password, self.__email)
                self.__manager = Manager(self.__email, self.__password, self.__data, session_key=session_key, server_public_key=server_public_key)
                code = self.__data.get_data("extensioncode")
                self.__manager.save_initial_data(code,session_key,client_permanent_key)
                print("setup complete")
                
            except Exception as e:
                print(traceback.format_exc())
                self.__manager = Manager(self.__email, self.__password, self.__data)
                
            self.__manager.import_passwords()
            
        except Exception as e:
            pass
        
    def get_navrail(self):
        return self.__navrail
        
    def get_main_container_width(self):
        return self.__main_container.width
    
    def get_main_container_height(self):
        return self.__main_container.height
        
    def get_page(self):
        return self.__page
        
    def get_manager(self):
        return self.__manager
    
    def get_data(self):
        return self.__data
    
    def get_password(self):
        return self.__password
    
    def __download_full_passwords(self):
        threads = [threading.Thread(target=password_card.download_icon) for password_card in self.__password_list] #get any icons for passwords
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.__manager.get_all_passwords_full()
        self.__manager.get_all_managers_users()
        self.__manager.scan_passwords()
        
    def run_background_tasks(self):
        self.__unable_to_logout = True
        self.__download_full_passwords()
        self.__manager.validate_client_public_key()
        self.__unable_to_logout = False
    
    def destination_change(self,e):
        ###edit destination depending on the selected option
        if self.__navrail.get_selected_index() == 0:
            self.__main_container.content = self.__initial_icon
            self.__main_container.update()
            
        elif self.__navrail.get_selected_index() == 1:
            self.refresh()
            self.__navrail.set_selected_index(0)
            self.__navrail.update()
            self.__download_full_passwords()
            
        elif self.__navrail.get_selected_index() == 2:
            self.__get_pending_passwords()
            
        elif self.__navrail.get_selected_index() == 3:
            self.__share_extension_code()
            
        elif self.__navrail.get_selected_index() == 4:
            self.__scan_passwords()

        elif self.__navrail.get_selected_index() == 5:
            self.__main_container.content = Settings(self,self.__data)
            self.__main_container.update()
            
        elif self.__navrail.get_selected_index() == 6:
            self.logout()
    
    def logout(self):
        if self.__unable_to_logout:
            self.__main_container.content = ProRing()
            self.__main_container.update()
        while self.__unable_to_logout:
            pass
        self.__data.empty()
        db=sqlite3.connect(rf"assets\assetdata.db")
        curs = db.cursor()
        curs.execute("DELETE FROM CurrentUser")
        curs.close()
        db.commit()
        db.close()
        self.__page.go('/')
    
    def copy_to_clipboard(self,data):
        pyperclip.copy(data)
        print("Copied to clipboard")
        self.__page.snack_bar = SnackBar(
            content=Text("Copied to clipboard",color=TEXT_COLOUR),
            bgcolor=BACKGROUND_COLOUR_2,
            elevation=5,
            margin=5,
            duration=3000,
        )
        self.__page.snack_bar.open = True
        self.__page.update()
    
    def help(self, e=None):
        self.go_to_url("https://youtu.be/2Q_ZzBGPdqE?si=4USxl1xyyCRNrStO")
        
    def __scan_passwords(self):
        self.__main_container.content = Column(
            controls=[
                Text("Evaluating password strength...",color=TEXT_COLOUR,size=25,weight=FontWeight.BOLD,font_family="Afacad"),
                ProRing(255),
                Divider(height=1,color="transparent"),
            ],
            alignment=MainAxisAlignment.SPACE_BETWEEN,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            spacing=20,
        )
        self.__main_container.update()
        self.__main_container.content = Scanner(self,self.__data)
        self.__main_container.update()


    def __share_extension_code(self):
        self.__main_container.content = CodeSharer(self,self.__code)
        self.__main_container.update()

    def share_password(self,passID, type):
        self.__main_container.content = Sharer(self,self.__data,passID,type)
        self.__main_container.update()

    def edit_password(self,passID, current_type):
        self.__main_container.content = Updater(self,passID,current_type)
        self.__main_container.update()
    
    def __get_pending_passwords(self):
        self.__main_container.content = ProRing()
        self.__main_container.update()
        self.__main_container.content = ReceiveShared(self, self.__data)
        self.__main_container.update()
    
    def set_lockdown(self,passID,type):
        self.__main_container.content = Lockdown(self,passID,type)
        self.__main_container.update()
    
    def delete_password(self,passID,pass_type,manager):
        self.__main_container.content = Deleter(self,self.__data,passID,pass_type,manager)
        self.__main_container.update()
    
    def go_to_url(self,url):
        self.__page.launch_url(url)
        print("Launched url")
    
    def __search(self,e):
        search_content = self.__search_box.value
        if search_content != "":
            for element in self.__password_list_container.content.controls[0].controls:
                if type(element) == PasswordCard or type(element) == InfoCard:
                    password_data = [
                        element.get_title().lower(), 
                        element.get_username().lower() if type(element) == PasswordCard else "", 
                        element.get_url().lower() if type(element) == PasswordCard else "",
                    ]
                    if any(search_content.lower() in s for s in password_data):
                        element.show()
                    else:
                        element.hide()
            self.__password_list_container.update()
            
        else:
            for element in self.__password_list_container.content.controls[0].controls:
                if type(element) == PasswordCard or type(element) == InfoCard:
                    element.show()
            self.__password_list_container.update()
        # pass
            
            
    def manage_users(self,passID,type):
        self.__main_container.content = ProRing()
        self.__main_container.update()
        self.__main_container.content = ViewUsers(self,self.__data,passID,type)
        self.__main_container.update()
    
    def view_password(self,e,passID,type):
        if self.__processing == False:
            self.__processing = True
            self.__navrail.set_selected_index(0)
            self.__navrail.get_nav().update()
            self.__main_container.content = ProRing()
            self.__main_container.update()
            self.__main_container.alignment = alignment.top_left
            self.__main_container.content = self.__initial_icon
            data = self.__manager.get_specific_password_info(passID)
            print(passID)
            print(data)
            print(type)
            if type == "info":
                self.__current_passID = passID
                self.__current_password = data[0]
                self.__current_title = data[1]
                self.__current_manager = data[2]
                self.__container_col = InfoViewer(self,self.__current_title,self.__current_passID,self.__current_password,self.__current_manager)
           
            elif type == "password":
                self.__current_passID = passID
                self.__current_password = data[0]
                self.__current_title = data[1]
                self.__current_username = data[2]
                self.__current_manager = data[3]
                self.__current_url = data[4]
                self.__current_additional_info = data[5]
                self.__container_col = PasswordViewer(self,self.__current_passID,self.__current_title,self.__current_password,self.__current_username,self.__current_url,self.__current_manager,self.__current_additional_info)
                
            self.__main_container.content = self.__container_col
            self.__main_container.update()
            self.__processing = False

    
    def __add_infos_passwords(self): #adds the info and passwords to columns (as can't run when class if first called from views as not part of page yet)
        for element in self.__password_list_container.content.controls[0].controls:
            if type(element) == PasswordCard or type(element) == InfoCard:
                self.__password_list_container.content.controls[0].controls.remove(element)
        temp_passwords = reversed(self.__password_list) #so in correct order
        for card in temp_passwords:
            self.__password_list_container.content.controls[0].controls.insert(5,card) #always in position 5 due to no variation before
        for card in self.__info_list:
            self.__password_list_container.content.controls[0].controls.append(card) #always go to back
        print("updated list")
        self.__password_list_container.update()
        
    
    def __create_list(self):
        ###create a list of passwords
        self.__password_list = list(
            map(
                lambda password: PasswordCard(
                    self, title=password[0], passID=password[4], username=password[1], url=password[2]
                ),
                self.__manager.get_passwords(),
            ))
            
            
        self.__info_list = list(
            map(
                lambda info: InfoCard(
                    self, title=info[0], passID=info[2]
                ),
                self.__manager.get_infos(),
            ))
        self.__password_list.sort(key=lambda x: x.get_title().lower()) #sorts list alphabetically
        self.__info_list.sort(key=lambda x: x.get_title().lower())
        
    
    def __initialise(self):
        if self.__on_home:
            try:
                self.__create_list()
                self.__add_infos_passwords()
            except Exception as e:
                pass
            
    def add_password(self, e):
        self.__main_container.content = PasswordAdder(self)
        self.__main_container.update()
    
    
    def refresh(self):
        if not self.__processing:
            self.__processing = True
            self.__password_list_container.content.controls.append(ProRing(255))
            self.__password_list_container.update()
            self.__navrail.set_selected_index(0)
            self.__search_box.value = ""
            self.__main_container.content=self.__initial_icon
            self.__main_container.update()
    
            ###refresh password list
            #first remove all passwords and infos from list
            for i in range (len(self.__password_list_container.content.controls[0].controls)):
                try: #will fail when i goes out of range which is inevitable if removing elements from list
                    element = self.__password_list_container.content.controls[0].controls[i]
                    while type(element) == PasswordCard or type(element) == InfoCard:
                        self.__password_list_container.content.controls[0].controls.remove(element)
                        element = self.__password_list_container.content.controls[0].controls[i]
                except Exception as e:
                    break
           
            #import and create new list
            self.__passwords_hidden = False
            self.__infos_hidden = False
            self.__manager.import_passwords()
            self.__create_list()
            self.__add_infos_passwords()
            self.__password_list_container.content.controls.pop()
            self.__password_list_container.update()
            self.__processing = False
            self.__download_full_passwords()
            
    
    def __show_hide_passwords(self,e):
        if not self.__processing:
            self.__processing = True
            ###show or hide passwords
            if self.__passwords_hidden == False:
                for password in self.__password_list:
                    password.hide()
                self.__passwords_hidden = True
                self.__raise_passwords_button.icon = icons.KEYBOARD_ARROW_UP
            else:
                temp_passwords = reversed(self.__password_list)
                for password in temp_passwords:
                    password.show()
                self.__passwords_hidden = False
                self.__raise_passwords_button.icon = icons.KEYBOARD_ARROW_DOWN
            self.__password_list_container.update()
            self.__processing = False
            
    
    def __show_hide_infos(self,e):
        if not self.__processing:
            self.__processing = True
            ###show or hide infos
            if self.__infos_hidden == False:
                for info in self.__info_list:
                    info.hide()
                self.__infos_hidden = True
                self.__raise_infos_button.icon = icons.KEYBOARD_ARROW_UP
            else:
                for info in self.__info_list:
                    info.show()
                self.__infos_hidden = False
                self.__raise_infos_button.icon = icons.KEYBOARD_ARROW_DOWN
            self.__password_list_container.update()
            self.__processing = False
            
    def build(self):
        self.__height = self.__page.window_height - 80
        self.__navrail = NavSideRail(self)
        self.__raise_passwords_button = ElevatedButton(
            icon=icons.KEYBOARD_ARROW_DOWN,
            text="Passwords",
            disabled=False,
            width=330,
            height=30,
            on_click=self.__show_hide_passwords,
        )
        self.__raise_infos_button = ElevatedButton(
            icon = icons.KEYBOARD_ARROW_DOWN,
            text="Credentials",  #credentials refers to info but more user friendly
            disabled=False,
            width=330,
            height=30,
            on_click=self.__show_hide_infos,
        )
        self.__search_box = TextField(
            label="Search",
            width=330,
            height=50,
            text_size=14,
            on_change=self.__search,
        )
        self.__password_list_container = Container( #will contain scrollable list of passwords and info
            width=350,
            margin=5,
            height=self.__height,
            padding=15,
            alignment=alignment.top_center,
            border=border.all(2,TEXT_COLOUR),
            border_radius=border_radius.all(15),
                        
            content=Stack(
                controls=[
                    Column(
                        horizontal_alignment=CrossAxisAlignment.CENTER,
                        alignment=MainAxisAlignment.CENTER,
                        scroll=ScrollMode.AUTO,
                        controls=[
                            Divider(height=10,color="transparent"),
                            self.__search_box,
                            Divider(height=10,color="transparent"),
                            self.__raise_passwords_button,
                            Divider(height=10,color="transparent"),
                            Divider(height=10,color="transparent"),
                            self.__raise_infos_button,
                            Divider(height=10,color="transparent"),
                        ],
                        spacing=0,
                    ),
                    Column(
                        controls=[
                            Row(
                                controls=[
                                    IconButton(
                                        icon=icons.ADD_ROUNDED,
                                        on_click=self.add_password,
                                        bgcolor=THEME_COLOUR,
                                        icon_size=50,
                                        opacity=0.8,
                                    ),
                                ],
                                alignment=MainAxisAlignment.END,
                                vertical_alignment=CrossAxisAlignment.CENTER,
                            ),
                        ],
                        horizontal_alignment=CrossAxisAlignment.START,
                        alignment=MainAxisAlignment.END,
                    ),
                ],
            ),
        )
        
        self.__initial_icon = Stack(
            controls=[
                Column(
                    controls=[
                        Row(
                            controls=[
                                VerticalDivider(color="transparent",width=20),
                                Icon(
                                    icons.KEY,
                                    size=250,
                                    opacity=0.1,
                                )
                            ],
                            alignment=MainAxisAlignment.CENTER,
                            vertical_alignment=CrossAxisAlignment.CENTER,
                        ),
                    ],
                    alignment=MainAxisAlignment.CENTER,
                    horizontal_alignment=CrossAxisAlignment.CENTER,
                ),
                Column(
                    controls=[
                        Row(
                            controls=[
                                Icon(
                                    icons.CIRCLE_OUTLINED,
                                    size=500,
                                    opacity=0.1,
                                )
                            ],
                            alignment=MainAxisAlignment.CENTER,
                            vertical_alignment=CrossAxisAlignment.CENTER,
                        )
                    ],
                    alignment=MainAxisAlignment.CENTER,
                    horizontal_alignment=CrossAxisAlignment.CENTER,
                ),
            ]
        )
            
        self.__main_container = Container(
            width=550,
            margin=5,
            padding=1,
            height=self.__height,
            alignment=alignment.center,
            border_radius=border_radius.all(15),
            content=self.__initial_icon,
        )
        
        
        self.__initialise()            
        
        self.__row = Row(
            controls=[
                self.__navrail,
                VerticalDivider(color=TEXT_COLOUR,width=3),
                self.__password_list_container,
                self.__main_container,
            ],
            height=self.__height,
            alignment=MainAxisAlignment.START,
            vertical_alignment=CrossAxisAlignment.START,
        )
        return self.__row