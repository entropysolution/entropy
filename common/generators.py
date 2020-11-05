from random import choice
from os import urandom
from hashlib import sha256
from base64 import b64encode, b64decode
from pbkdf2 import crypt


def generate_alphanum(length):
	str = []
	chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
	for k in range(0, length):
		str.append(choice(chars))
	return ''.join(str)


def generate_hash(input_string, pbkdf2=True, salt_length=24, cost_factor=12000):
	if pbkdf2:
		if isinstance(input_string, str):
			input_string = input_string.encode('utf-8')
		while True:
			try:
				salt = generate_alphanum(salt_length)
				_hash = crypt(input_string, salt, cost_factor)
				break
			except:
				pass
		return 'PBKDF2$%s$%s$%s' % (salt, cost_factor, _hash)
	else:
		return sha256('ent%sropy' % (input_string)).hexdigest()


def check_hash(test_string, input_string, pbkdf2=True):
	if pbkdf2:
		if isinstance(input_string, str):
			input_string = input_string.encode('utf-8')
		try:
			algo, salt, cost_factor, _hash = test_string.split('$', 3)
		except:
			return False
		if _hash == crypt(input_string, _hash):
			return True
		return False
	else:
		return sha256('ent%sropy' % (input_string).hexdigest()) == test_string


def generate_random_password():
	 str = []
	 chars = 'abcdefghijklmnopqrstuvwxyz1234567890'
	 for k in range(0, 8):
		  str.append(choice(chars))
	 return ''.join(str)