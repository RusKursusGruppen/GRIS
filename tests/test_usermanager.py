# -*- coding: utf-8 -*-

import unittest

from flask import session

from testingutils import ApplicationTestBase
from server import usermanager

from gris import app

class TestAuthentication(ApplicationTestBase):
    def test_01_login_1(self):
        result = self.post("/api/usermanager/login", data={"username":"rkg", "raw_password":"123"})
        self.assertSuccess()

    def test_02_login_2(self):
        with self.app:
            result = self.post("/api/usermanager/login", data={"username":"rkg", "raw_password":"123"})
            self.assertSuccess()
            self.assertEqual(session["logged_in"], True)
            self.assertEqual(session["user_id"], 1)
            self.assertEqual(session["username"], "rkg")

    def test_03_logout_1(self):
        with self.app:
            result = self.post("/api/usermanager/logout")
            self.assertSuccess()
            self.assertFalse(hasattr(session, "logged_in"))
            self.assertFalse(hasattr(session, "user_id"))
            self.assertFalse(hasattr(session, "username"))

    def test_04_logout_2(self):
        "logout while not logged_in"
        with self.app:
            result = self.post("/api/usermanager/logout")
            self.assertSuccess()
            self.assertFalse(hasattr(session, "logged_in"))
            self.assertFalse(hasattr(session, "user_id"))
            self.assertFalse(hasattr(session, "username"))

    def test_05_is_not_logged_in(self):
        result = self.post_json("/api/usermanager/logged_in")
        self.assertSuccessful()
        self.assertEqual(result["logged_in"], False)

    def test_06_is_logged_in(self):
        self.post("/api/usermanager/login", data={"username":"rkg", "raw_password":"123"})
        self.assertSuccess()
        result = self.post_json("/api/usermanager/logged_in")
        self.assertSuccessful()
        self.assertEqual(result["logged_in"], True)

    def test_07_is_logged_in_session(self):
        with self.app:
            self.post("/api/usermanager/login", data={"username":"rkg", "raw_password":"123"})
            result = self.post_json("/api/usermanager/logged_in")
            self.assertSuccessful()
            self.assertEqual(result["logged_in"], True)
            self.assertEqual(session["logged_in"], True)
            self.assertEqual(session["user_id"], 1)
            self.assertEqual(session["username"], "rkg")

    def test_08_each_case_will_start_logout(self):
        with self.app:
            result = self.post_json("/api/usermanager/logged_in")
            self.assertSuccessful()
            self.assertEqual(result["logged_in"], False)
            self.assertFalse(hasattr(session, "logged_in"))
            self.assertFalse(hasattr(session, "user_id"))
            self.assertFalse(hasattr(session, "username"))
