# -*- coding: utf-8 -*-

from gris import db

def db_create():
    print("Creating database")
    db.create_all()

if __name__ == "__main__":
    db_create()
