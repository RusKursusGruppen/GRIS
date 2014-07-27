#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys
import psycopg2
import itertools

from lib import log

import config

def execute(com, *args):
    try:
        with psycopg2.connect(host=config.DATABASE_HOST,
                              database=config.DATABASE_NAME,
                              user=config.DATABASE_USER,
                              port=config.DATABASE_PORT,
                              password=config.DATABASE_PASSWORD) as connection:
            with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(com, args)
                log.data(com, args)
                return v.fetchall()
    except:
        log.data(com, args, error=True)
        raise

def executemany(com, argSeq):
    try:
        with psycopg2.connect(host=config.DATABASE_HOST,
                              database=config.DATABASE_NAME,
                              user=config.DATABASE_USER,
                              port=config.DATABASE_PORT,
                              password=config.DATABASE_PASSWORD) as connection:
            with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.executemany(com, argSeq)
                log.data(com, argSeq)
                return v.fetchall()
    except:
        log.data(com, argSeq, error=True)
        raise

def script(filename):
    with open(filename) as f:
        execute(f.read())

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
            for k,v in d.items():
                self.__unsafe__[k] = v

        for k,v in kwargs.items():
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
                print("bucket not filled")
                raise e
            else:
                if not item.startswith("_"):
                    print("FAIL: ", item)
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

        return execute(sql, values)

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
        sql += " returning *"

        return execute(sql, values)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python data.py SCRIPT")
    else:
        print(script(sys.argv[1]))
