# -*- coding: utf-8 -*-

import unittest

from gris import app

from test_tools import *
from test_data import *

if __name__ == "__main__":
    with app.app_context():
        unittest.main(failfast=True)
