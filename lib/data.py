#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys
import sqlite3
import itertools

import config

def connect(dbf=None):
    dbf = dbf if dbf else config.DATABASE
    db = sqlite3.connect(dbf)
    db.row_factory = sqlite3.Row
    return db


def data():
    return connect()


def execute(com, *args):
    with connect() as db:
        db.execute("PRAGMA foreign_keys = ON").fetchone()
        v = db.execute(com, args)
        return v.fetchall()

def script(f):
    with connect() as db:
        with open(f) as f:
            db.cursor().executescript(f.read())

def store(bucket, sql, *args):
    bucket >> [sql]+list(args)

class Bucket(object):
    def __init__(self, *unsafe,  **kwargs):
        self.__lock__ = False

        self.__unsafe__ = {}
        for d in unsafe:
            # EXPLANATION:
            # You cant use self.__unsafe__.update(d) here as the request.form
            # for some reason will pack its values in lists
            for k,v in d.iteritems():
                self.__unsafe__[k] = v

        for k,v in kwargs.iteritems():
            object.__setattr__(self, k, v)

    def __getattribute__(self, item):
        """If there is an attribute 'item' in self, return it.
        If there is a key 'item' in __kv__ return the corresponding value, and insert it into the attributes.
        Else try to look up 'item' in self anyway probably triggering an exception"""

        if item in object.__getattribute__(self, "__dict__"):
            return object.__getattribute__(self, item)

        if not object.__getattribute__(self, "__lock__"):
            unsafe = object.__getattribute__(self, "__unsafe__")
            if item in unsafe:
                value = unsafe[item]
                object.__setattr__(self, item, value)
                return value

        try:
            return object.__getattribute__(self, item)
        except AttributeError as e:
            if config.DEBUG:
                raise e
            else:
                if not item.startswith("_"):
                    print "FAIL: ", item
                return None

    def __getitem__(self, item):
        prevlock = self.__lock__
        + self
        try:
            return self.__getattribute__(item)
        finally:
            self.__lock__ = prevlock

    def __setitem__(self, item, value):
        prevlock = self.__lock__
        + self
        try:
            if hasattr(self, item): #erroneoussssss
                self.__setattr__(item, value)
            else:
                raise AttributeError("To prevent sqlinjections you cant declare new attributes like this")
        finally:
            self.__lock__ = prevlock

    def __pos__(self):
        self.__lock__ = True

    def __neg__(self):
        self.__lock__ = False


    def __iter__(self):
        return (x for x in dir(self) if not x.startswith("_"))

    def __rshift__(self, args):
        """Pour, into database"""
        sql = args[0]
        args = args[1:]

        setstatm = ", ".join(["{0} = ?".format(c) for c in self])
        if sql.lower().find(" set ") == -1:
            sql = sql.replace("$", "SET $")
        sql = sql.replace("$", setstatm)

        values = [self[c] for c in self]
        values.extend(args)

        with connect() as db:
            db.execute(sql, values)

    def __ge__(self, dest):
        """Create entry in database"""
        sql = "INSERT INTO {0}(".format(dest)
        keys = [c for c in self]
        questions = ["?"] * len(keys)
        values = [self[c] for c in self]

        sql += ",".join(keys)
        sql += ") VALUES ("
        sql += ",".join(questions)
        sql += ")"

        with connect() as db:
            db.execute(sql, values)


if __name__ == "__mainn__":
    if len(sys.argv) < 3:
        print ("Usage: python data.py DATABASE SCRIPT")
    else:
        db = sys.argv[1]

        if sys.argv[2] == "tables":
            for a in (execute(db, "SELECT name FROM sqlite_master WHERE type='table'")):
                print (a['name'])
        elif sys.argv[2] == "schema":
            for a in (execute(db, "SELECT * FROM sqlite_master WHERE type='table'")):
                if a['name'] == 'sqlite_sequence':
                    continue
                print (a['name']+":")
                print (a['sql'])
                print ("\n")
        else:
            for item in sys.argv[2:]:
                print("{0} @ {1}".format(item, db))
                script(db, item)
