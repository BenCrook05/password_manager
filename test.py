except:
    Application.delete_saved_login_data()
    page.go('/')