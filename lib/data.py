#!/usr/bin/python2
import sys
import sqlite3
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
        v = db.execute(com, args)
        return v.fetchall()

def script(f):
    with connect() as db:
        with open(f) as f:
            db.cursor().executescript(f.read())


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
