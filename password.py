import os
import hashlib
import config

def generate_salt():
    return os.urandom(config.SALT_LENGTH).encode('hex')

def set(raw_password):
    algo = config.HASH_ALGORITHM
    salt = generate_salt()
    hsh = encrypt(algo, salt, raw_password)
    return "{0}${1}${2}".format(algo, salt, hsh)

def check(raw_password, enc_password):
    """
    Returns a boolean of whether the raw_password was correct.
    Handles encryption formats behind the scenes.
    """
    algo, salt, hsh = enc_password.split('$')
    return hsh == encrypt(algo, salt, raw_password)

def encrypt(algo, salt, raw_password):
    crypter = hashlib.new(algo)
    crypter.update(raw_password)
    crypter.update(salt)
    return crypter.hexdigest()
