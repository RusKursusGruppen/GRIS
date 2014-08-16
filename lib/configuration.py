# -*- coding: utf-8 -*-

import os

import config

def create_secret_key():
    length = config.SECRET_KEY_LENGTH
    filename = config.SECRET_KEY_FILE

    key = os.urandom(length)
    with open(filename, "wb") as file:
        file.write(key)
    return key

def load_secret_key():
    if os.path.isfile(config.SECRET_KEY_FILE):
        with open(config.SECRET_KEY_FILE, "rb") as file:
            return file.read()
    else:
        return create_secret_key()
