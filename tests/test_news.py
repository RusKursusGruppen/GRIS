# -*- coding: utf-8 -*-

import unittest

from testingutils import ApplicationTestBase
from server import usermanager

class TestNews(ApplicationTestBase):
    def test_1_starts_empty(self):
        result = self.get_json("/api/news")
        self.assertSuccessful()
        self.assertEqual(result, {"values":[], "length":0})

    def test_2_new_missing_title(self):
        self.post("/api/usermanager/authenticate", data={"username":"rkg", "raw_password":"123"})
        result = self.post("/api/news/new", data={"title":"", "body":"Hello"})
        self.assertAborted(400, "illegal title")

    def test_3_new(self):
        self.post("/api/usermanager/authenticate", data={"username":"rkg", "raw_password":"123"})
        result = self.post("/api/news/new", data={"title":"Hello, World!", "body":"Welcome to GRIS!"})
        self.assertSuccess()

    def test_4_new(self):
        self.post("/api/usermanager/authenticate", data={"username":"rkg", "raw_password":"123"})
        result = self.post("/api/news/new", data={"title":"Second message", "body":"With a body"})
        self.assertSuccess()

    def test_5_contains_news(self):
        result = self.get_json("/api/news")
        self.assertSuccessful()
        self.assertEqual(result["length"], 2)

        self.assertEqual(result["values"][0]["news_id"], 1)
        self.assertEqual(result["values"][0]["title"], "Hello, World!")
        self.assertEqual(result["values"][0]["body"], "Welcome to GRIS!")
        self.assertEqual(result["values"][0]["creator"], 1)

        self.assertEqual(result["values"][1]["news_id"], 2)
        self.assertEqual(result["values"][1]["title"], "Second message")
        self.assertEqual(result["values"][1]["body"], "With a body")
        self.assertEqual(result["values"][1]["creator"], 1)

    def test_6_update(self):
        self.post("/api/usermanager/authenticate", data={"username":"rkg", "raw_password":"123"})
        result = self.post("/api/news/update", data={"news_id":2, "title":"Second message!", "body":"With a body!"})
        self.assertSuccess()

        result = self.get_json("/api/news")
        self.assertSuccessful()
        self.assertEqual(result["length"], 2)
        self.assertEqual(result["values"][1]["news_id"], 2)
        self.assertEqual(result["values"][1]["title"], "Second message!")
        self.assertEqual(result["values"][1]["body"], "With a body!")
        self.assertEqual(result["values"][1]["creator"], 1)

    def test_7_update(self):
        self.post("/api/usermanager/authenticate", data={"username":"rkg", "raw_password":"123"})
        result = self.post("/api/news/update", data={"news_id":2, "body":"With a body"})
        self.assertSuccess()

        result = self.get_json("/api/news")
        self.assertSuccessful()
        self.assertEqual(result["length"], 2)
        self.assertEqual(result["values"][1]["news_id"], 2)
        self.assertEqual(result["values"][1]["title"], "Second message!")
        self.assertEqual(result["values"][1]["body"], "With a body")
        self.assertEqual(result["values"][1]["creator"], 1)

    #TODO: test update and delete as wrong user

    def test_8_delete(self):
        self.post("/api/usermanager/authenticate", data={"username":"rkg", "raw_password":"123"})
        result = self.post("/api/news/new", data={"title":"third", "body":"content"})
        self.assertSuccess()

        result = self.get_json("/api/news")
        self.assertSuccessful()
        self.assertEqual(result["length"], 3)
        self.assertEqual(result["values"][2]["news_id"], 3)
        self.assertEqual(result["values"][2]["title"], "third")
        self.assertEqual(result["values"][2]["body"], "content")
        self.assertEqual(result["values"][2]["creator"], 1)

        result = self.post("/api/news/delete", data={"news_id":3})
        self.assertSuccess()

        result = self.get_json("/api/news")
        self.assertSuccessful()
        self.assertEqual(result["length"], 2)
        self.assertEqual(result["values"][0]["news_id"], 1)
        self.assertEqual(result["values"][1]["news_id"], 2)
