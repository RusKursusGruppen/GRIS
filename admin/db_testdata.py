# -*- coding: utf-8 -*-

from gris import db
import db_reset
import models

def db_testdata():
    db_reset.db_reset()
    user = models.User(username="rkg", password="123")
    db.session.add(user)
    db.session.commit()

if __name__ == "__main__":
    db_testdata()
