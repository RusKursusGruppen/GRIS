# -*- coding: utf-8 -*-

from lib.configuration import load_secret_key


HOST = "127.0.0.1"
PORT = 5000
URL = "http://localhost:5000"

CSRF_ENABLED = True
DEBUG = True

SECRET_KEY_LENGTH = 24
SECRET_KEY_FILE = "secret_key"
SECRET_KEY = load_secret_key()

BCRYPT_LOG_ROUNDS = 12

USER_CREATION_KEY_MIN_LENGTH = 128
USER_CREATION_KEY_MAX_LENGTH = 256

EMAIL = "mail@example.com"
EMAIL_PASSWORD = ""
EMAIL_HOST = ""
EMAIL_HOST_PORT = 587

LOGFILE = "log.txt"
PRINT_LOG = False

DATABASE_HOST = ""
DATABASE_NAME = ""
DATABASE_USER = ""
DATABASE_PORT = 5432
DATABASE_PASSWORD = ""

MAIL_ADMINS = True
MAIL_ON_EXIT = False
