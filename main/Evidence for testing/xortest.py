# import backEnd.SymmetricEncryption.XorEncryption as xor
import XorEncryption as xor

encryptor = xor.XorEncryption()
data = {
    "password": "password",
    "username": "username",
    "url": "url",
    "list_of_tags": ["tag1", "tag2"],
    "notes": "notes",
    "true": True,
    "data": 34,
    "temp_dic": {
        "temp": "temp",
        "temp2": "temp2"
    },
}

key = encryptor.generate_key(24)
print(f"key: {key}")
def encryptdecrypt_directory(data, key):
    if isinstance(data, dict):
        for key, value in data.items():
            data[key] = encryptdecrypt_directory(value, key) #has to treat dic differently as can't iterate through
        return data
    
    elif isinstance(data, (list, tuple, set)):
        encrypted_data = [encryptdecrypt_directory(element, key) for element in data] #iterates through list and executes encryptdecrpt_directory on each element
        return type(data)(encrypted_data)
    
    elif isinstance(data, str):
        return encryptor.encryptdecrypt(data, key)
    else:
        return data #doesn't encrypt if not a string (as can't encrypt int and boolean function etc)
    
    
encrypted_data = encryptdecrypt_directory(data, key)
print(encrypted_data)
print(encryptdecrypt_directory(encrypted_data, key))
            
            
