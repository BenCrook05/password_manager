from flet import *
from views import views_handler
from assets.colours import Colours
from extensionAPI import localserver as ls
from datetime import datetime
from threading import Thread
class Data(dict):
    def __init__(self):
        super().__init__()
        self._datadic={}
    def add_data(self, label, info):
        self._datadic[label] = info
    def get_data(self, label):
        return self._datadic[label]
    def empty(self):
        self._datadic = {}
        
        
def run_flask_server():
    ls.app.run(host='127.0.0.1', port=5000)


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
    data = Data()


    def on_window_event(e):
        if e == "close":
            page.window_visible = False
    
    page.on_window_event = on_window_event

    def route_change(route): 
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
            page.views[-1].controls[1].run_background_tasks()


    page.on_route_change = route_change
    page.go('/') 

    

    
if __name__ == '__main__':
    flask_thread = Thread(target=run_flask_server)
    flask_thread.start()
    app(port=8550, target=main)
    
    
    
    
