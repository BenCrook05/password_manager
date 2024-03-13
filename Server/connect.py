from dotenv import load_dotenv
import os
load_dotenv('/home/BenCrook/mysite/.env')
import MySQLdb
import traceback
from datetime import datetime


def connect_to_db():
    try:
        db_password = os.getenv('DB_KEY')
        db = MySQLdb.connect('BenCrook.mysql.eu.pythonanywhere-services.com',
                              'BenCrook', db_password, 'BenCrook$PI_manager')
        return db
    except Exception as e:
        write_errors(traceback.format_exc(),"Connecting")
        return "FAILED TO CONNECT"

def write_errors(error_code="None",function_name="None"):
    existing_content = ""
    with open("/home/BenCrook/mysite/error.txt", "r") as file:
        existing_content = file.read()
    with open("/home/BenCrook/mysite/error.txt", "w") as file:
        file.write(f"\n\nFunction attempt: {function_name}\nError code: {str(error_code)}\nTime: {datetime.now().replace(second=0, microsecond=0)}")
        file.write(existing_content)