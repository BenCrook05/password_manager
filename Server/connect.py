from dotenv import load_dotenv
import os
load_dotenv('/home/BenCrook/mysite/.env')
import MySQLdb
import traceback
from datetime import datetime

import ssl
from email.message import EmailMessage
import smtplib

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
        file.write(f"\n\nFunction attempt: {function_name}\nError code: 
                   {str(error_code)}\nTime: {datetime.now().replace(second=0, microsecond=0)}")
        file.write(existing_content)

def send_email(subject, content, recipient_address):
    try:
        email_sender = "securenetNEA@gmail.com"
        email_password = os.getenv('EMAILPASSWORD')
        if not email_password:
            raise ValueError("No email password")
        email_receiver = recipient_address
        subject = subject
        #created in my strypo email editor
        email_template = f"""
        <html>
            <head>
                <style>
                    body {{
                        font-family: 'Arial', sans-serif;
                        background-color: #f4f4f4;
                        padding: 20px;
                        text-align: center;
                    }}
                    h2 {{
                        font-size: 20px;
                        color: #3498db;
                    }}
                    p {{
                        font-size: 15px;
                        color: #555;
                    }}
                </style>
            </head>
            <body>
                <h2>{subject}</h2>
                <p>{content}</p>
            </body>
        </html>
        """
        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['Subject'] = subject
        em.add_alternative(email_template, subtype='html')

        # to improve security using ssl
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
            smtp.login(email_sender, email_password)
            return smtp.sendmail(email_sender, email_receiver, em.as_string())
    except Exception as e:
        write_errors(traceback.format_exc(),"Sending email")
        return ["FAILED",traceback.format_exc()]
