import hashlib
from wachtwoord.pbkdf2 import Engine

def make_hash(password, pbkdf2=True):
    if pbkdf2:
        return Engine().hash(password)
    return hashlib.sha256(f'ent{password}ropy'.encode()).hexdigest()

def check_hash(password, hash, pbkdf2=True):
    if pbkdf2:
        return Engine().verify(password, hash)
    return hashlib.sha256(f'ent{password}ropy'.encode()).hexdigest() == hash