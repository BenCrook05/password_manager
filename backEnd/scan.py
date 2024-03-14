import re
import random
import math
from collections import Counter
from threading import Thread
class PasswordChecker:
    def __init__(self, passwords):
        """
        many of these given as a list:
        passwords contains:
            "password": password
            "username": username 
            "passID": passID
            "url": url
            "title": title
        """
        self.__passwords = passwords
        
    def scan_all_passwords(self):
        #create list of passwords and usernames
        error_dic ={
            "repeated passwords": [],
            "repeated urls": [],
            "password rating": []
        }
        for password_dictionary in self.__passwords:
            password = password_dictionary["password"]
            number_uses = sum(1 for d in self.__passwords if d['password'] == password)
            username = password_dictionary["username"]
            if number_uses > 1:
                password_dictionary["repeated"] = True
            else:
                password_dictionary["repeated"] = False
                
        threads = [Thread(target=self.__create_rating, args=(password_dictionary,)) for password_dictionary in self.__passwords]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
            

        return self.__passwords

    def __create_rating(self, password_dictionary):
        password = password_dictionary["password"]
        username = password_dictionary["username"]
        rating = 0.5
        
        if len(password) > 8 and len(password) < 20:
            rating = rating * (1+len(password)/30)
        elif len(password) >= 20:
            rating = rating * 1.5
        else:
            rating = rating * len(password)/10
        
        has_lowercase = any(char.islower() for char in password)
        has_uppercase = any(char.isupper() for char in password)
        has_digit = any(char.isdigit() for char in password)
        has_special = any(char in r"!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~" for char in password)
        
        if has_lowercase and has_uppercase and has_digit:
            rating = rating * 1.5
        if has_lowercase or has_uppercase or has_digit or has_special:
            rating = rating * 1.1
        
        # check for digit sequences
        if re.search(r"(\d)\1{2,}", password):
            rating = rating * 0.8
        
        # check for username in password
        for i in range(len(username) - 1):
            for j in range(i + 2, len(username) + 1):  
                try:
                    substring = username[i:j]
                    if substring in password:
                        rating = rating * (1-(len(substring)/len(password)))
                except:
                    continue
            
        # check for common passwords
        common_passwords = ['123456', '123456789', '12345', 'qwerty', 'password', 
                            '12345678', '111111', '123123', '1234567890', '1234567', 
                            'qwerty123', '000000', '1q2w3e', 'aa12345678', 'abc123',
                            'password1', '1234', 'qwertyuiop', '123321', 'password123']
        #https://nordpass.com/most-common-passwords-list/
        if password.lower() in common_passwords:
            rating = rating * 0.2
        
        # check for repeated characters
        if re.search(r"(\w)\1{2,}", password.lower()):
            rating = rating * 0.8
            
        # check for entropy (shannon)
        freq = Counter(password.lower())
    
        length = len(password)
        probs = {char: count / length for char, count in freq.items()}
        entropy = -sum(prob * math.log2(prob) for prob in probs.values())
        entropy = entropy / 2   #entropy is usually between 0 and 4, but sometimes -0.0 too, so abs needed
        rating = rating * abs(entropy)
        
        # check for sequences of characters
        characters = 'abcdefghijklmnopqrstuvwxyz' + 'zyxwvutsrqponmlkjihgfedcba' + '0123456789' + '9876543210'
        max_sequence_length = 0
        
        for i in range(len(password) - 1):
            sequence_length = 1
            if password[i:i+2] in characters:
                sequence_length += 1
            else:
                max_sequence_length = max(max_sequence_length, sequence_length)
                sequence_length = 1
        max_sequence_length = max(max_sequence_length, sequence_length)
        relative = 1 - max_sequence_length / len(password)
        rating = rating * relative
        
        
        # set rating between 0 and 1
        rating = max(0.01, min(1, rating))
        
        password_dictionary["rating"] = rating
        
    

class PasswordGenerator:
    @staticmethod
    def create_random_password(length):
        length=length-(length%4)
        lower_letters = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','v','u','w','x','y','z']
        upper_letters = [letter.upper() for letter in lower_letters]
        numbers = ['1','2','3','4','5','6','7','8','9','0']
        symbols = ['!','@','#','$','%','&','*']
        contents = [lower_letters,upper_letters,numbers,symbols]
        length = 16  #must be multiple of 4
        password = []
        for i in range(length):
            password.append(random.choice(random.choice(contents)))
        for i in range (4,len(password)+1,5):
            password.insert(i,'-')
        password = ''.join(str(item) for item in password)
        return password

    