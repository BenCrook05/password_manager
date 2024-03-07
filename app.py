from flet import *
from pages.views import views_handler
from assets.colours import Colours
from datetime import datetime
import traceback
import sqlite3
from backEnd.loginlogic import Application

def main(page: Page):
    page.window_title_bar_hidden = True
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.window_width = 1065
    page.window_height = 900
    page.resizable = False
    page.theme_mode = Colours().get_theme()
    page.scroll = ScrollMode.AUTO
    page.window_frameless = False
    page.window_min_width = 468
    page.window_min_height = 500
    page.window_opacity = 0.99
    page.padding = 0
    page.window_visible = True
    page.window_prevent_close = True
    page.window_resizable = False
    data = {}


    def on_window_event(e):
        if e == "close":
            page.window_visible = False
    
    page.on_window_event = on_window_event

    def route_change(route): 
        try:
            print(page.route)
            page.views.clear()
            page.views.append(
                views_handler(page, data)[page.route]
            )
            page.update()
            if page.route == "/":
                starttime = datetime.now()
                page.views[-1].controls[1].attempt_auto_login()
                print(f"Time to load: {datetime.now() - starttime}")
                
            elif page.route == "/Home":
                page.views[-1].controls[1].initialise()
                page.views[-1].controls[1].run_background_tasks()
        except:
            print(traceback.format_exc())
            Application.delete_saved_login_data()
            page.go('/')


    page.on_route_change = route_change
    page.go('/') 

    

    
if __name__ == '__main__':
    app(port=8550, target=main)
    
    
    
    
