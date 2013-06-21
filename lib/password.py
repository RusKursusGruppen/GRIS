# -*- coding: utf-8 -*-

import config
import bcrypt

def encode(raw_password):
    salt = bcrypt.gensalt(config.BCRYPT_LOG_ROUNDS)
    return bcrypt.hashpw(raw_password, salt)

def check(raw_password, enc_password):
    return bcrypt.hashpw(raw_password, enc_password) == enc_password
