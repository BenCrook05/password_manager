import XorEncryption as xor

key = "1234531215"
encryptor = xor.XorEncryption()
data = "crookbenj@gmail.com"
encrypted_data = encryptor.encryptdecrypt(data, key)
print(encrypted_data)
decrypted_data = encryptor.encryptdecrypt(encrypted_data, key)
print(decrypted_data)