# -*- coding: utf-8 -*-

import unittest
import datetime
import psycopg2
from psycopg2 import ProgrammingError, InternalError
import werkzeug

import lib.data as lib_data
from lib.data import *

import config

# data = config_db()
from gris import data, app

class DatabaseTestBase(unittest.TestCase):
    start_data = [(x,) for x in ["Default 1", "Default 2", "Default 3"]]

    connection = {"host":config.BUCKET_DATABASE_HOST,
                  "database":config.BUCKET_DATABASE_NAME,
                  "user":config.BUCKET_DATABASE_USER,
                  "port":config.BUCKET_DATABASE_PORT,
                  "password":config.BUCKET_DATABASE_PASSWORD}

    def __init__(self, *args, **kwargs):
        super(DatabaseTestBase, self).__init__(*args, **kwargs)
        sql = """
DROP TABLE IF EXISTS Tests CASCADE;
CREATE TABLE Tests(
    id                  serial PRIMARY KEY,
    value               text,
    type                int DEFAULT 1 CHECK(type > 0)
);"""
        with psycopg2.connect(**self.connection) as con:
            with con.cursor() as cursor:
                cursor.execute(sql)

    def setUp(self):
        self.tearDown()
        sql = "INSERT INTO Tests(value) VALUES(%s)"
        with psycopg2.connect(**self.connection) as con:
            with con.cursor() as cursor:
                cursor.executemany(sql, self.start_data)

    def tearDown(self):
        sql = "DELETE FROM Tests"
        with psycopg2.connect(**self.connection) as con:
            with con.cursor() as cursor:
                cursor.execute(sql)

    def assertDataMatches(self, query):
        with psycopg2.connect(**self.connection) as con:
            with con.cursor() as cursor:
                sql = "SELECT value FROM Tests ORDER BY id"
                cursor.execute(sql)
                result = cursor.fetchall()
                self.assertEqual(len(query), len(result))
                for item, actual in zip(query, result):
                    if not isinstance(item, str):
                        item = item[0]
                    self.assertEqual(item, actual[0])

    def assertDataUnchanged(self):
        self.assertDataMatches(self.start_data)

    def assertValuesInserted(self, *data):
        self.assertDataMatches(self.start_data + list(data))



# TODO: reset database

# class TopLevel(unittest.TestCase):
#     def test_execute(self):
#         lib_data.execute("SELECT * FROM Tours");

#     def test_executemany(self):
#         lib_data.executemany("SELECT * FROM Tours");
#         lib_data.executemany("SELECT * FROM Tours WHERE tour_id = ?", [1, 2, 3]);

#     def test_script(self):
#         lib_data.script("some filename")

class Transactions(DatabaseTestBase):
    def test_1(self):
        result = None
        with data.transaction() as t:
            result = t.execute("SELECT value FROM Tests")
            self.assertDataUnchanged()
        self.assertDataMatches(result)
        self.assertDataUnchanged()

    def test_2(self):
        with data.transaction() as t:
            t.execute("INSERT INTO Tests(value) VALUES(?)", "a")
            self.assertDataUnchanged()
        self.assertValuesInserted("a")

    def test_3(self):
        with data.transaction() as t:
            t.execute("INSERT INTO Tests(value) VALUES(?)", "a")
            self.assertRaises(ProgrammingError, t.execute, "INSERT INTO Tests(value) VALUES(?, ?)", "b", 0)
            self.assertRaises(InternalError, t.execute, "INSERT INTO Tests(value) VALUES(?)", "c")
        self.assertDataUnchanged()

    def test_4(self):
        with data.transaction() as t:
            t.execute("INSERT INTO Tests(value) VALUES(?)", "a")
            with t:
                t.execute("INSERT INTO Tests(value) VALUES(?)", "b")
                self.assertDataUnchanged()
            self.assertDataUnchanged()
        self.assertValuesInserted("a", "b")

    def test_5(self):
        with data.transaction() as t:
            t.execute("INSERT INTO Tests(value) VALUES(?)", "a")
            with t:
                t.execute("INSERT INTO Tests(value) VALUES(?)", "b")
                self.assertRaises(ProgrammingError, t.execute, "INSERT INTO Tests(value) VALUES(?, ?)", "c", 0)
                self.assertRaises(InternalError, t.execute, "INSERT INTO Tests(value) VALUES(?)", "d")
                self.assertDataUnchanged()
            self.assertDataUnchanged()
        self.assertDataUnchanged()

    def test_6(self):
        with data.transaction() as t:
            t.execute("INSERT INTO Tests(value) VALUES(?)", "a")
            self.assertRaises(ProgrammingError, t.execute, "INSERT INTO Tests(value) VALUES(?, ?)", "b", 0)
            self.assertRaises(InternalError, t.execute, "INSERT INTO Tests(value) VALUES(?)", "c")
            with t:
                self.assertRaises(InternalError, t.execute, "INSERT INTO Tests(value) VALUES(?)", "d")
                self.assertDataUnchanged()
            self.assertDataUnchanged()
        self.assertDataUnchanged()

    def test_7(self):
        with data.transaction() as t:
            t.execute("INSERT INTO Tests(value) VALUES(?)", "a")
            with t:
                t.execute("INSERT INTO Tests(value) VALUES(?)", "b")
                self.assertDataUnchanged()
            t.execute("INSERT INTO Tests(value) VALUES(?)", "c")
            self.assertRaises(ProgrammingError, t.execute, "INSERT INTO Tests(value) VALUES(?, ?)", "d", 0)
            self.assertRaises(InternalError, t.execute, "INSERT INTO Tests(value) VALUES(?)", "e")
            self.assertDataUnchanged()
        self.assertDataUnchanged()

    def test_8(self):
        with data.transaction() as t:
            t.execute("INSERT INTO Tests(value) VALUES(?)", "a")
            with t:
                t.execute("INSERT INTO Tests(value) VALUES(?)", "b")
                self.assertDataUnchanged()
            self.assertDataUnchanged()
        self.assertValuesInserted("a", "b")


    def test_9(self):
        with data.transaction() as t:
            t.execute("INSERT INTO Tests(value) VALUES(?)", "a")
            with data.transaction() as t:
                t.execute("INSERT INTO Tests(value) VALUES(?)", "b")
                self.assertDataUnchanged()
            self.assertDataUnchanged()
        self.assertValuesInserted("a", "b")

    def test_10(self):
        with data.transaction() as t:
            t.execute("INSERT INTO Tests(value) VALUES(?)", "a")
            with data.transaction() as t:
                t.execute("INSERT INTO Tests(value) VALUES(?)", "b")
                self.assertRaises(ProgrammingError, t.execute, "INSERT INTO Tests(value) VALUES(?, ?)", "c", 0)
                self.assertRaises(InternalError, t.execute, "INSERT INTO Tests(value) VALUES(?)", "d")
                self.assertDataUnchanged()
            self.assertDataUnchanged()
        self.assertDataUnchanged()

    def test_11(self):
        with data.transaction() as t:
            t.execute("INSERT INTO Tests(value) VALUES(?)", "a")
            self.assertRaises(ProgrammingError, t.execute, "INSERT INTO Tests(value) VALUES(?, ?)", "b", 0)
            self.assertRaises(InternalError, t.execute, "INSERT INTO Tests(value) VALUES(?)", "c")
            with data.transaction() as t:
                self.assertRaises(InternalError, t.execute, "INSERT INTO Tests(value) VALUES(?)", "d")
                self.assertDataUnchanged()
            self.assertDataUnchanged()
        self.assertDataUnchanged()

    def test_12(self):
        with data.transaction() as t:
            t.execute("INSERT INTO Tests(value) VALUES(?)", "a")
            with data.transaction() as t:
                t.execute("INSERT INTO Tests(value) VALUES(?)", "b")
                self.assertDataUnchanged()
            t.execute("INSERT INTO Tests(value) VALUES(?)", "c")
            self.assertRaises(ProgrammingError, t.execute, "INSERT INTO Tests(value) VALUES(?, ?)", "d", 0)
            self.assertRaises(InternalError, t.execute, "INSERT INTO Tests(value) VALUES(?)", "e")
            self.assertDataUnchanged()
        self.assertDataUnchanged()

    def test_13(self):
        with data.transaction() as t:
            t.execute("INSERT INTO Tests(value) VALUES(?)", "a")
            with data.transaction() as t:
                t.execute("INSERT INTO Tests(value) VALUES(?)", "b")
                self.assertDataUnchanged()
            self.assertDataUnchanged()
        self.assertValuesInserted("a", "b")

    def test_14(self):
        """Same as test_9 but in two different transactions"""
        with data.transaction() as t:
            t.execute("INSERT INTO Tests(value) VALUES(?)", "a")
            with data.new_transaction() as q:
                q.execute("INSERT INTO Tests(value) VALUES(?)", "b")
                self.assertDataUnchanged()
            self.assertValuesInserted("b")
        self.assertValuesInserted("a", "b")
