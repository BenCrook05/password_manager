from argon2 import PasswordHasher
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class Hash:
    @staticmethod
    def create_hash(data, salt_type="random"): #data passed in bytes, salt is "random" or "default"
        ph = PasswordHasher(time_cost=2, memory_cost=65536, parallelism=4)
        if salt_type == "random":
            hash = ph.hash(data)
            return str(hash)
        elif salt_type == "default":
            salt=b"passwordmanagerrandomsalt" #only use salt for mac address hash
            hash = ph.hash(data,salt=salt)
            return str(hash)
        else:
            salt = salt_type.encode('utf-8')
            hash = ph.hash(data,salt=salt)
            #format hash
            hash = hash[30:]
            return str(hash)

    def verify_hash(hash, data):
        ph = PasswordHasher()
        try:
            ph.verify(hash, data)
            return True
        except:
            return False
        
    @staticmethod
    def create_client_permanent_key(client_raw_password, client_email):
        password = client_raw_password+(client_email[0:5])
        password = password.encode('utf-8')
        salt = client_email[5:].encode('utf-8')
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    