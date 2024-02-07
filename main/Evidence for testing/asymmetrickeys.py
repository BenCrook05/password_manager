from subprocess import Popen, PIPE
import os
import base64

def encrypt(data_to_encrypt,e,n):
    file_path = os.path.dirname(os.path.realpath("asyncencrypt.dll"))
    file_path = os.path.join(file_path, "asyncencrypt.dll")


    p = Popen([file_path], stdout=PIPE, stdin=PIPE)

    p.stdin.write(b"1\n")
    p.stdin.write(data_to_encrypt.encode('utf-8'))
    p.std.write(e.encode('utf-8'))
    p.std.write(n.encode('utf-8'))
    p.stdin.flush()

    result = p.stdout.readline().strip()
    return result

def decrypt(data_to_decrypt, d, n):
    file_path = os.path.dirname(os.path.realpath("asyncdecrypt.dll"))
    file_path = os.path.join(file_path, "asyncdecrypt.dll")

    p = Popen([file_path], stdout=PIPE, stdin=PIPE)

    p.stdin.write(b"2\n")
    p.stdin.write(data_to_decrypt.encode('utf-8'))
    p.stdin.write(d.encode('utf-8'))
    p.stdin.write(n.encode('utf-8'))
    p.stdin.flush()

    result = p.stdout.readline().strip()
    return result

def get_keys():
    file_path = os.path.dirname(os.path.realpath("keygenerator.dll"))
    file_path = os.path.join(file_path, "keygenerator.dll")

    p = Popen([file_path], stdout=PIPE, stdin=PIPE)

    result = p.stdout.readline().strip()
    return result