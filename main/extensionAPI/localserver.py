from flask import Flask, request, jsonify
app = Flask(__name__)
import sqlite3
import base64
import socket
import traceback
from backEnd.encryption import Encrypt, Decrypt, Generate
from backEnd.dbrequests import PyAnyWhereRequests as pr

def fix_padding(encoded_data):
    missing_padding = len(encoded_data) % 4
    if missing_padding != 0:
        encoded_data += '=' * (4 - missing_padding)
    return encoded_data


def get_private_data(content):
    # url = content["url"]
    code = content["extensioncode"]
    db = sqlite3.connect(rf"extensionAPI\infoapi.db")
    curs = db.cursor()
    curs.execute("SELECT SessionKey, ClientPermanentKey, ClientEmail FROM Keys")
    data = curs.fetchone()
    
    encrypted_session_key = data[0]
    encrypted_permanent_key = data[1]
    encrypted_client_email = data[2]
    
    fernet_key = Generate().generate_fernet(extra=code)
    
    session_key = fernet_key.decrypt(encrypted_session_key).decode("utf-8")
    client_permanent_key = fernet_key.decrypt(encrypted_permanent_key)
    client_email = fernet_key.decrypt(encrypted_client_email).decode("utf-8")
    curs.close()
    db.close()
    
    return session_key, client_permanent_key, client_email

   
def get_password(content):
    try:
        session_key, client_permanent_key, client_email = get_private_data(content)
        db = sqlite3.connect(rf"extensionAPI\infoapi.db")
        curs = db.cursor()
        curs.execute(f"SELECT PassID, URL, Username FROM UrlPassID")
        data = curs.fetchall()
        curs.close()
        db.commit()
        db.close()
        for element in data:
            if content['url'] in element[1]:
                url = element[1]
                pass_id = element[0]
                username = element[2]
                break
            else:
                raise Exception("No password found for this url")
            
        server_public_key = pr.get_server_key()
        data = pr.get_password(server_public_key, session_key, client_email, pass_id)
        
        if data == "UNAUTHENTICATED":
            raise Exception("Unauthenticated: App refresh required")
        
        encrypted_password = data[0]
        additional_info = data[1]
        encrypted_password_key = data[2]
        manager = data[3]
        print(f"encrypted_password_key: {encrypted_password_key}")
        print(f"encrypted_password: {encrypted_password}")
        print(f"client_permanent_key: {client_permanent_key}")
        password_key = Decrypt.decrypt_password_key(encrypted_password_key, client_permanent_key)
        password = Decrypt.decrypt_password(encrypted_password, password_key)
        
        return {
            "password": password,
            "additional_info": additional_info,
            "username": username,
            "url": url,
            "manager": manager,
            "flag": "success"
        }
        
    except Exception as e:
        print(traceback.format_exc())
        return {
            "flag": "error",
            # "error": str(e)
        }


def verify_code(content):
    try:
        session_key, client_permanent_key, client_email = get_private_data(content)
        return {"flag": "success", "code_validity": "valid"}
    except Exception as e:
        print(traceback.format_exc())
        return {
            "flag": "error", 
            "code_validity": "invalid",
            # "error_message": str(e)
        }



@app.route('/endpoint', methods=['POST'])
def endpoint():
    data = request.get_json()
    try:
        header = data["header"]
        content = data["content"]
        print(f"Request received: {header}\ncontent:{content}")
        if header == "get_password":
            data_to_return = get_password(content)
        elif header == "verify_code":
            data_to_return = verify_code(content)



        print(data_to_return)
    except Exception as e:
        print(traceback.format_exc())
        data_to_return = {
            "flag": "error",
            # "error": str(e)
        }
    return jsonify(data_to_return)  

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc', debug=True)