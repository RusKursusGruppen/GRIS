# -*- coding: utf-8 -*-

import unittest

from admin.test_db import test_db
from gris import app
import config

from test_tools import *
from test_data import *
from test_usermanager import *
from test_news import *

# REMEMBER TEST METHODS ARE RUN IN ALPHABETICAL ORDER
# BY THEIR METHOD NAMES

if __name__ == "__main__":
    if not app.config["DEBUG"] and not app.config["TESTING"]:
        raise Exception("You should never run unittests on production servers. Data WILL be modified!")

    with app.test_request_context():
        test_db()
    app.config["SLEEP_ATTEMPT"] = 0
    app.config["SLEEP_FAIL"] = 0
    config.SLEEP_ATTEMPT = 0
    config.SLEEP_FAIL = 0

    app.config["MAIL_ADMINS"] = False
    config.MAIL_ADMINS = False

    with app.test_request_context():
        unittest.main(failfast=True)
