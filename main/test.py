
import math
from collections import Counter

while  True:
    password = input("Enter a password: ")
    freq = Counter(password)
    length = len(password)
    probs = {char: count / length for char, count in freq.items()}
    entropy = -sum(prob * math.log2(prob) for prob in probs.values())
    print(entropy)