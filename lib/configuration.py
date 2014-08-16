# -*- coding: utf-8 -*-

import os

import config

def create_secret_key():
    length = config.SECRET_KEY_LENGTH
    filename = config.SECRET_KEY_FILE

    key = os.urandom(length)
    with open(filename, "wb") as file:
        file.write(key)
