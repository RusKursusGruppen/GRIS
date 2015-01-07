# -*- coding: utf-8 -*-

import unittest
import datetime
import werkzeug

from lib.tools import *

class Now(unittest.TestCase):
    def test_1(self):
        n = now().replace(tzinfo=None)
        utc = datetime.datetime.utcnow()
        delta = utc - n

        self.assertLess(delta.total_seconds(), 10)


class Abort(unittest.TestCase):
    def test_1(self):
        exception = werkzeug.exceptions.InternalServerError
        self.assertRaises(exception, abort)
        self.assertRaises(exception, abort, 500)
        self.assertRaises(exception, abort, 500, "hello")
        self.assertRaises(exception, abort, 500, ["hello", "bye"])
        self.assertRaises(exception, abort, "hello")
        self.assertRaises(exception, abort, ["hello", "bye"])
        self.assertRaises(exception, abort, description="hello")
        self.assertRaises(exception, abort, description=["hello", "bye"])
    def test_2(self):
        exception = werkzeug.exceptions.NotFound
        self.assertRaises(exception, abort, 404)
        self.assertRaises(exception, abort, 404, "hello")
        self.assertRaises(exception, abort, 404, ["hello", "bye"])

    def getException(self, exception, function, *args, **kwargs):
        try:
            function(*args, **kwargs)
        except exception as e:
            return e

    def test_3(self):
        exception = werkzeug.exceptions.InternalServerError

        raised = self.getException(exception, abort)
        self.assertIsInstance(raised, exception)

        raised = self.getException(exception, abort, 500, "hello")
        self.assertIsInstance(raised, exception)
        self.assertEqual(raised.description, "hello")

        raised = self.getException(exception, abort, 500, ["hello", "bye"])
        self.assertIsInstance(raised, exception)
        self.assertEqual(raised.description, ["hello", "bye"])

        raised = self.getException(exception, abort, "hello")
        self.assertIsInstance(raised, exception)
        self.assertEqual(raised.description, "hello")

        raised = self.getException(exception, abort, ["hello", "bye"])
        self.assertIsInstance(raised, exception)
        self.assertEqual(raised.description, ["hello", "bye"])

        raised = self.getException(exception, abort, description="hello")
        self.assertIsInstance(raised, exception)
        self.assertEqual(raised.description, "hello")

        raised = self.getException(exception, abort, description=["hello", "bye"])
        self.assertIsInstance(raised, exception)
        self.assertEqual(raised.description, ["hello", "bye"])

    def test_3(self):
        exception = werkzeug.exceptions.NotFound

        raised = self.getException(exception, abort, 404, "hello")
        self.assertIsInstance(raised, exception)
        self.assertEqual(raised.description, "hello")

        raised = self.getException(exception, abort, 404, ["hello", "bye"])
        self.assertIsInstance(raised, exception)
        self.assertEqual(raised.description, ["hello", "bye"])
