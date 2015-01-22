# -*- coding: utf-8 -*-

import unittest

from flask import session

from testingutils import ApplicationTestBase
from server import usermanager

from gris import app

class TestAuthentication(ApplicationTestBase):
    def test_01_authenticate_1(self):
        result = self.post("/api/usermanager/authenticate", data={"username":"rkg", "raw_password":"123"})
        self.assertSuccess()

    def test_02_authenticate_2(self):
        with self.app:
            result = self.post("/api/usermanager/authenticate", data={"username":"rkg", "raw_password":"123"})
            self.assertSuccess()
            self.assertEqual(session["logged_in"], True)
            self.assertEqual(session["user_id"], 1)
            self.assertEqual(session["username"], "rkg")

    def test_03_unauthenticate_1(self):
        with self.app:
            result = self.post("/api/usermanager/unauthenticate")
            self.assertSuccess()
            self.assertFalse(hasattr(session, "logged_in"))
            self.assertFalse(hasattr(session, "user_id"))
            self.assertFalse(hasattr(session, "username"))

    def test_04_unauthenticate_2(self):
        "unauthenticate while not authenticated"
        with self.app:
            result = self.post("/api/usermanager/unauthenticate")
            self.assertSuccess()
            self.assertFalse(hasattr(session, "logged_in"))
            self.assertFalse(hasattr(session, "user_id"))
            self.assertFalse(hasattr(session, "username"))

    def test_05_is_not_authenticated(self):
        result = self.post_json("/api/usermanager/authenticated")
        self.assertSuccessful()
        self.assertEqual(result["authenticated"], False)

    def test_06_is_authenticated(self):
        self.post("/api/usermanager/authenticate", data={"username":"rkg", "raw_password":"123"})
        self.assertSuccess()
        result = self.post_json("/api/usermanager/authenticated")
        self.assertSuccessful()
        self.assertEqual(result["authenticated"], True)

    def test_07_is_authenticated_session(self):
        with self.app:
            self.post("/api/usermanager/authenticate", data={"username":"rkg", "raw_password":"123"})
            result = self.post_json("/api/usermanager/authenticated")
            self.assertSuccessful()
            self.assertEqual(result["authenticated"], True)
            self.assertEqual(session["logged_in"], True)
            self.assertEqual(session["user_id"], 1)
            self.assertEqual(session["username"], "rkg")

    def test_08_each_case_will_start_unauthenticate(self):
        with self.app:
            result = self.post_json("/api/usermanager/authenticated")
            self.assertSuccessful()
            self.assertEqual(result["authenticated"], False)
            self.assertFalse(hasattr(session, "logged_in"))
            self.assertFalse(hasattr(session, "user_id"))
            self.assertFalse(hasattr(session, "username"))
