#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys
from contextlib import contextmanager
import psycopg2
import psycopg2.extras
import itertools

from lib import log

import config


class BucketCursor(psycopg2.extensions.cursor):
    def __init__(self, *args, **kwargs):
        super(BucketCursor, self).__init__(*args, **kwargs)
        self.row_factory = BucketRow
        self._column_mapping = None

    def column_mapping(self):
        if self._column_mapping is None:
            self._column_mapping = []
            for i in range(len(self.description)):
                self._column_mapping.append(self.description[i][0])
        return self._column_mapping

class Transaction():
    def __init__(self):
        self.connection = psycopg2.connect(host=config.DATABASE_HOST,
                                           database=config.DATABASE_NAME,
                                           user=config.DATABASE_USER,
                                           port=config.DATABASE_PORT,
                                           password=config.DATABASE_PASSWORD,
                                           cursor_factory=BucketRow)

    def _execute(self, query, args, many):
        if query.count("?") != len(args):
            raise Exception("Wrong number of SQL arguments for query "+query)
        query = query.replace("?", "%s")
        try:
            # with self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            with self.connection.cursor() as cursor:
                if many:
                    cursor.executemany(query, args)
                else:
                    cursor.execute(query, args)

                log.data(query, args)
                try:
                    result = QueryList(cursor.fetchall())
                    result.rowcount = cursor.rowcount
                    result.lastrowid = cursor.lastrowid
                    result.statusmessage = cursor.statusmessage
                    return result
                except psycopg2.ProgrammingError as e:
                    if str(e) == "no results to fetch":
                        return None
                    raise
        except:
            log.data(query, args, error=True)
            raise

    def execute(self, query, *args):
        return self._execute(query, args, False)

    def executemany(self, query, argSeq):
        args = []
        query_count = query.count("?")
        for arg in argSeq:
            # if argSeq is like ["a", "b", "c", "d", ...]
            if isinstance(arg, str):
                length = 1
                args.append((arg,))
            else:
                # if argSeq is like [("a", "b"), ("c", "d"), ...]
                try:
                    length = len(arg)
                    args.append(arg)
                # if argSeq is like [1, 2, 3, 4...] where the arguments are not strings
                except:
                    length = 1
                    args.append((arg,))
            if query_count != length:
                raise Exception("Wrong number of SQL arguments for query "+query)

        query = query.replace("?", "%s")
        return self._execute(query, args, True)

    def script(self, filename):
        with open(filename) as f:
            return self._execute(f.read())

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.commit()

class QueryList(list):
    def all(self):
        return self

    def one_or_more(self):
        if len(self) == 1:
            return self[0]
        else:
            return self

    def one(self, code=None, description=None):
        if len(self) != 1:
            if code is None and description is None:
                description = "There are {} rows in the result, but only one was expected!".format(len(self))
            abort(code, description)
        else:
            return self[0]

    def scalar(self, code=None, description=None):
        row = self.one(code, description)
        if len(row) != 1:
            if code is None and description is None:
                description = "There are {} columns in the result, but only one was expected!".format(len(self))
            abort(code, description)
        return row[0]

    def scalars(self, code=None, description=None):
        result = []
        for row in self:
            if len(row) != 1:
                if code is None and description is None:
                    description = "There are {} columns in the result, but only one was expected!".format(len(self))
                abort(code, description)
            result.append(row[0])
        return result


def execute(query, *args):
    with Transaction() as t:
        return t.execute(query, *args)

def executemany(query, argSeq):
    with Transaction() as t:
        return t.executemany(query, *args)

def script(filename):
    with Transaction() as t:
        return t.script(filename)

def store(bucket, sql, *args):
    bucket >> [sql]+list(args)

def bucket_to_dict(bucket):
    """Returns a dict of the validated data from the bucket"""
    d = dict()
    for key in bucket:
        d[key] = bucket[key]
    return d

class Bucket(object):
    def __init__(self, *unsafe,  **kwargs):
        self._lock = False

        self._unsafe = {}
        for d in unsafe:
            # EXPLANATION:
            # You cant use self._unsafe.update(d) here as the request.form
            # for some reason will pack its values in lists
            for k,v in d.items():
                self._unsafe[k] = v

        for k,v in kwargs.items():
            object.__setattr__(self, k, v)

    def __getattribute__(self, item):
        """If there is an attribute 'item' in self, return it.
        If there is a key 'item' in __kv__ return the corresponding value, and insert it into the attributes.
        Else try to look up 'item' in self anyway probably triggering an exception"""

        if item in object.__getattribute__(self, "__dict__"):
            return object.__getattribute__(self, item)

        if not object.__getattribute__(self, "_lock"):
            unsafe = object.__getattribute__(self, "_unsafe")
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

    def __contains__(self, item):
        try:
            self[item]
            return True
        except NameError:
            return False

    def __getitem__(self, item):
        """Returns item in the bucket or if none is found, the item in the unsafe part"""
        prevlock = self._lock
        + self
        try:
            return self.__getattribute__(item)
        except AttributeError:
            return self._unsafe[item]
        finally:
            self._lock = prevlock

    def __setitem__(self, item, value):
        prevlock = self._lock
        + self
        try:
            if hasattr(self, item): #erroneoussssss
                self.__setattr__(item, value)
            else:
                raise AttributeError("To prevent sqlinjections you cant declare new attributes like this")
        finally:
            self._lock = prevlock

    def __pos__(self):
        self._lock = True

    def __neg__(self):
        self._lock = False


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

        return execute(sql, *values)

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

        result = execute(sql, *values)
        return result.one_or_more()

class BucketRow(Bucket):
    def __init__(self, cursor):
        super(BucketRow, self).__init__()
        self._column_mapping = cursor.column_mapping()

    def __getitem__(self, item):
        if isinstance(item, int):
            item = self._column_mapping[item]
        return super(BucketRow, self).__getitem__(item)

    def __setitem__(self, key, value):
        if isinstance(key, int):
            key = self._column_mapping[key]
        return super(BucketRow, self).__setitem__(key, value)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python data.py SCRIPT")
    else:
        print(script(sys.argv[1]))
