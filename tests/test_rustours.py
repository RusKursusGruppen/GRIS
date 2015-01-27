# -*- coding: utf-8 -*-

import unittest

from testingutils import ApplicationTestBase
from server import usermanager
from lib.tools import rkgyear

class TestRustours(ApplicationTestBase):
    def test_01_starts_empty(self):
        result = self.get_json("/api/rustours")
        self.assertSuccessful()
        self.assertEqual(result, {"rustours":{}, "total":0, "years":[]})

    def test_02_starts_empty(self):
        result = self.post_json("/api/rustours", data={"year":2014})
        self.assertSuccessful()
        self.assertEqual(result, {"rustours":[], "total":0})

    def test_03_new(self):
        result = self.post_json("/api/rustours/new", data={"year":2014, "type":"m", "tour_name":"DiFaldne", "theme":"Himmel og Helvede", "notes":"Det var fedt"})
        self.assertSuccess()

        result = self.post_json("/api/rustours/new", data={"year":2013, "type":"m", "tour_name":"DiEnd", "theme":"Jordens undergang", "notes":"Lots of zombies!"})
        self.assertSuccess()

        result = self.post_json("/api/rustours/new", data={"year":2011, "type":"p", "tour_name":"DiRudder", "theme":"Ridder"})
        self.assertSuccess()

        result = self.post_json("/api/rustours/new", data={"year":2014, "tour_name":"DiAblo"})
        self.assertSuccess()


    def test_04_added_by_year(self):
        result = self.post_json("/api/rustours", data={"year":2014})
        self.assertSuccessful()

        self.assertEqual(result["total"], 2)
        self.assertEqual(len(result["rustours"]), 2)
        self.assertEqual(result["rustours"][0]["year"], 2014)
        self.assertEqual(result["rustours"][0]["tour_name"], "DiAblo")

        self.assertEqual(result["rustours"][1]["year"], 2014)
        self.assertEqual(result["rustours"][1]["type"], "m")
        self.assertEqual(result["rustours"][1]["tour_name"], "DiFaldne")
        self.assertEqual(result["rustours"][1]["theme"], "Himmel og Helvede")
        self.assertEqual(result["rustours"][1]["notes"], "Det var fedt")

    def test_05_added(self):
        result = self.get_json("/api/rustours")
        self.assertSuccessful()

        self.assertEqual(result["total"], 4)
        self.assertEqual(result["years"], [2014, 2013, 2011])

        self.assertEqual(len(result["rustours"]), 3)
        self.assertEqual(len(result["rustours"]["2014"]), 2)
        self.assertEqual(result["rustours"]["2014"][0]["tour_name"], "DiAblo")
        self.assertEqual(result["rustours"]["2014"][1]["tour_name"], "DiFaldne")

        self.assertEqual(len(result["rustours"]["2013"]), 1)
        self.assertEqual(result["rustours"]["2013"][0]["tour_name"], "DiEnd")

        self.assertEqual(len(result["rustours"]["2011"]), 1)
        self.assertEqual(result["rustours"]["2011"][0]["tour_name"], "DiRudder")

    def test_06_get(self):
        result = self.post_json("api/rustours/tour", data={"tour_id": 1})
        self.assertSuccessful()
        self.assertEqual(result["tour"]["tour_id"], 1)
        self.assertEqual(result["tour"]["tour_name"], "DiFaldne")
        self.assertEqual(len(result["tutors"]), 0)
        self.assertEqual(len(result["russer"]), 0)

    def test_07_update(self):
        result = self.post_json("/api/rustours/update", data={"tour_id":4, "year":2012, "type":"m", "tour_name":"DiRidder", "theme":"Ridder/fantasy"})
        self.assertSuccess()
        result = self.post_json("api/rustours/tour", data={"tour_id": 4})
        self.assertSuccessful()
        self.assertEqual(result["tour"]["tour_id"], 4)
        self.assertEqual(result["tour"]["year"], 2012)
        self.assertEqual(result["tour"]["type"], "m")
        self.assertEqual(result["tour"]["tour_name"], "DiRidder")
        self.assertEqual(result["tour"]["theme"], "Ridder/fantasy")
        self.assertEqual(result["tour"]["notes"], None)


    def test_08_add_tutor(self):
        result = self.post_json("/api/rustours/tutors/add", data={"user_id":2, "tour_id":4})
        self.assertSuccessful()
        result = self.post_json("api/rustours/tour", data={"tour_id": 4})
        print(result)
        self.assertSuccessful()
        self.assertEqual(len(result["tutors"]), 1)
        self.assertTrue(result["tutors"][0]["user_id"], 2)
        self.assertTrue(result["tutors"][0]["username"], "fugl")
