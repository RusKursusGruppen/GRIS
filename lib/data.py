#!/usr/bin/python2
import sys
import sqlite3
import config
import itertools

def connect(dbf=None):
    dbf = dbf if dbf else config.DATABASE
    db = sqlite3.connect(dbf)
    db.row_factory = sqlite3.Row
    return db


def data():
    return connect()


def execute(com, *args):
    with connect() as db:
        v = db.execute(com, args)
        return v.fetchall()

def script(f):
    with connect() as db:
        with open(f) as f:
            db.cursor().executescript(f.read())

def store(bucket, sql, *args):
    columns = [c for c in bucket]
    setstatm = ", ".join(["{0} = ?".format(c) for c in columns])
    if sql.lower().find(" set ") == -1:
        sql = sql.replace("$", "SET $")
    sql = sql.replace("$", setstatm)

    values = [bucket[c] for c in columns]
    values.extend(args)

    with connect() as db:
        db.execute(sql, values)

class Bucket(object):
    def __init__(self, **kwargs):
        for k,v in kwargs:
            self.k = v
    def __getitem__(self, item):
        return self.__getattribute__(item)
    def __setitem__(self, item, value):
        self.__setattr__(item, value)
    def __iter__(self):
        return itertools.ifilter(lambda x: not x.startswith("_"), dir(self))

if __name__ == "__main__":
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
