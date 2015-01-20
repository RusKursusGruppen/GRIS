# -*- coding: utf-8 -*-

import config
import bcrypt

def encode(raw_password):
    salt = bcrypt.gensalt(config.BCRYPT_LOG_ROUNDS)
    return bcrypt.hashpw(raw_password.encode('utf-8'), salt).decode('utf-8')

def check(raw_password, enc_password):
    return bcrypt.hashpw(raw_password.encode('utf-8'), enc_password.encode('utf-8')) == enc_password.encode('utf-8')
