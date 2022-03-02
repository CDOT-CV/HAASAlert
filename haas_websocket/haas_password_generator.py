import string
import random



alphabets = list(string.ascii_letters)
digits = list(string.digits)
special_characters = list("!@#$%^&*()")
characters = list(string.ascii_letters + string.digits + "!@#$%^&*()")


def gen_password(length):
    # extra_char_count = length - (lc_count + uc_count + sc_count + digit_count)
    password = []

    i=0
    while i < 1:
        password.append(random.choice(alphabets).lower())
        i += 1
    
    i=0
    while i < 1:
        password.append(random.choice(alphabets).upper())
        i += 1

    i=0
    while i < 1:
        password.append(random.choice(digits))
        i += 1

    i=0
    while i < 1:
        password.append(random.choice(special_characters))
        i += 1
    
    while len(password) < length:
        password.append(random.choice(characters))

    random.shuffle(password)
    return "".join(password)