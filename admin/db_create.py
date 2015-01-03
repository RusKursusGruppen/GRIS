# -*- coding: utf-8 -*-

from gris import db
from models import Group

def db_create():
    print("Creating database")
    db.create_all()

    db.session.add_all([
        Group("admin"),
        Group("admin_mail_log"),
        Group("rkg"),
        Group("mentor")])

    db.session.commit()

if __name__ == "__main__":
    db_create()
