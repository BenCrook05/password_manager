from flet import *
from assets.colours import Colours

BACKGROUND_COLOUR, THEME_COLOUR, TEXT_COLOUR, BACKGROUND_COLOUR_2= Colours().get_colours()

class NavSideRail(UserControl):
    def __init__(self, homepage):
        super().__init__()
        self.__homepage = homepage
        self.__height = self.__homepage.get_page().window_height
        self.__nav = Container()
        
    def get_nav(self):
        return self.__nav
            
    def get_selected_index(self):
        return self.__nav.content.selected_index
            
    def set_selected_index(self, index):
        self.__nav.content.selected_index = index
            
    def build(self):
        self.__nav = Container(
            NavigationRail(
                bgcolor="transparent",
                height=self.__height,
                label_type="all",
                selected_index=0,
                group_alignment=-1,
                destinations=[
                    NavigationRailDestination(
                        icon=icons.HOME_OUTLINED,
                        selected_icon=icons.HOME,
                        label_content=Text("Home",color=TEXT_COLOUR),
                    ),
                    NavigationRailDestination(
                        icon=icons.REFRESH,
                        selected_icon=icons.REFRESH,
                        label_content=Text("Refresh",color=TEXT_COLOUR),
                        
                    ),
                    NavigationRailDestination(
                        icon=icons.GROUPS_OUTLINED,
                        selected_icon=icons.GROUPS,
                        label_content=Text("Shared with you",color=TEXT_COLOUR),
                    ),
                    NavigationRailDestination(
                        icon=icons.DOWNLOAD_OUTLINED,
                        selected_icon = icons.DOWNLOAD,
                        label_content=Text("Export",color=TEXT_COLOUR),
                    ),
                    NavigationRailDestination(
                        icon=icons.CHECKLIST_ROUNDED,
                        selected_icon=icons.CHECKLIST_RTL_ROUNDED,
                        label_content=Text("Scan",color=TEXT_COLOUR),
                    ),
                    NavigationRailDestination(
                        icon=icons.SETTINGS_OUTLINED,
                        selected_icon=icons.SETTINGS_ROUNDED,
                        label_content=Text("Settings",color=TEXT_COLOUR),
                    ),
                    NavigationRailDestination(
                        icon=icons.LOGOUT_ROUNDED,
                        selected_icon=icons.LOGOUT_ROUNDED,
                        label_content=Text("Logout",color=TEXT_COLOUR),
                    ),
                    
                ],
                on_change=self.__homepage.destination_change
            ),
            alignment=alignment.top_left,
            height=self.__height,
            padding=4,
            width=87,
        )
        return self.__nav