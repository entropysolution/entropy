import random
import string
from os import urandom
from random import choice

def generate_alphanum(length):
	str = []
	chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
	for k in range(0, length):
		str.append(choice(chars))
	return ''.join(str)

def generate_random_password(length=8):
	 str = []
	 chars = 'abcdefghijklmnopqrstuvwxyz1234567890'
	 for k in range(0, length):
		  str.append(choice(chars))
	 return ''.join(str)

def genid():
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(9))
