# -*- coding: utf-8 -*-

import unittest

from testingutils import ApplicationTestBase
from server import usermanager

class TestNews(ApplicationTestBase):
    def test_01_starts_empty(self):
        result = self.get_json("/api/news")
        self.assertSuccessful()
        self.assertEqual(result, {"values":[], "length":0})

    def test_02_new_missing_title(self):
        self.post("/api/usermanager/login", data={"username":"rkg", "raw_password":"123"})
        result = self.post("/api/news/new", data={"title":"", "body":"Hello"})
        self.assertAborted(400, "illegal title")

    def test_03_new_missing_body(self):
        self.post("/api/usermanager/login", data={"username":"rkg", "raw_password":"123"})
        result = self.post("/api/news/new", data={"title":"Hello", "body":""})
        self.assertAborted(400, "illegal body")

    def test_04_new(self):
        self.post("/api/usermanager/login", data={"username":"rkg", "raw_password":"123"})
        result = self.post("/api/news/new", data={"title":"Hello, World!", "body":"Welcome to GRIS!"})
        self.assertSuccess()

    def test_05_new(self):
        self.post("/api/usermanager/login", data={"username":"rkg", "raw_password":"123"})
        result = self.post("/api/news/new", data={"title":"Second message", "body":"With a body"})
        self.assertSuccess()

    def test_06_contains_news(self):
        result = self.get_json("/api/news")
        self.assertSuccessful()
        self.assertEqual(result["length"], 2)

        self.assertEqual(result["values"][0]["news_id"], 2)
        self.assertEqual(result["values"][0]["title"], "Second message")
        self.assertEqual(result["values"][0]["body"], "With a body")
        self.assertEqual(result["values"][0]["creator"]["user_id"], 1)

        self.assertEqual(result["values"][1]["news_id"], 1)
        self.assertEqual(result["values"][1]["title"], "Hello, World!")
        self.assertEqual(result["values"][1]["body"], "Welcome to GRIS!")
        self.assertEqual(result["values"][1]["creator"]["user_id"], 1)

    def test_07_update(self):
        self.post("/api/usermanager/login", data={"username":"rkg", "raw_password":"123"})
        result = self.post("/api/news/update", data={"news_id":2, "title":"Second message!", "body":"With a body!"})
        self.assertSuccess()

        result = self.get_json("/api/news")
        self.assertSuccessful()
        self.assertEqual(result["length"], 2)
        self.assertEqual(result["values"][0]["news_id"], 2)
        self.assertEqual(result["values"][0]["title"], "Second message!")
        self.assertEqual(result["values"][0]["body"], "With a body!")
        self.assertEqual(result["values"][0]["creator"]["user_id"], 1)

    def test_08_update(self):
        self.post("/api/usermanager/login", data={"username":"rkg", "raw_password":"123"})
        result = self.post("/api/news/update", data={"news_id":2, "body":"With a body"})
        self.assertSuccess()

        result = self.get_json("/api/news")
        self.assertSuccessful()
        self.assertEqual(result["length"], 2)
        self.assertEqual(result["values"][0]["news_id"], 2)
        self.assertEqual(result["values"][0]["title"], "Second message!")
        self.assertEqual(result["values"][0]["body"], "With a body")
        self.assertEqual(result["values"][0]["creator"]["user_id"], 1)

    def test_09_delete(self):
        self.post("/api/usermanager/login", data={"username":"rkg", "raw_password":"123"})
        result = self.post("/api/news/new", data={"title":"third", "body":"content"})
        self.assertSuccess()

        result = self.get_json("/api/news")
        self.assertSuccessful()
        self.assertEqual(result["length"], 3)
        self.assertEqual(result["values"][0]["news_id"], 3)
        self.assertEqual(result["values"][0]["title"], "third")
        self.assertEqual(result["values"][0]["body"], "content")
        self.assertEqual(result["values"][0]["creator"]["user_id"], 1)

        result = self.post("/api/news/delete", data={"news_id":3})
        self.assertSuccess()

        result = self.get_json("/api/news")
        self.assertSuccessful()
        self.assertEqual(result["length"], 2)
        self.assertEqual(result["values"][1]["news_id"], 1)
        self.assertEqual(result["values"][0]["news_id"], 2)

    #TODO: test update and delete as wrong user
    def test_10_update_as_wrong_user(self):
        self.post("/api/usermanager/login", data={"username":"fugl", "raw_password":"123"})
        result = self.post("/api/news/update", data={"news_id":2, "title":"Second message!", "body":"With a body!"})
        self.assertAborted(403, "You are not the creator")

    def test_11_delete_as_wrong_user(self):
        self.post("/api/usermanager/login", data={"username":"fugl", "raw_password":"123"})
        result = self.post("/api/news/delete", data={"news_id":2})
        self.assertAborted(403, "You are not the creator")

    def test_12_update_missing_title(self):
        self.post("/api/usermanager/login", data={"username":"rkg", "raw_password":"123"})
        result = self.post("/api/news/update", data={"news_id":2, "title":"", "body":"Hello"})
        self.assertAborted(400, "illegal title")

    def test_13_update_missing_body(self):
        self.post("/api/usermanager/login", data={"username":"rkg", "raw_password":"123"})
        result = self.post("/api/news/update", data={"news_id":2, "title":"Hello", "body":""})
        self.assertAborted(400, "illegal body")
