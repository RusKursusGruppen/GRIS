# -*- coding: utf-8 -*-

from gris import db
import db_reset
import models

def db_testdata():
    db_reset.db_reset()
    admin = models.Group.query.filter_by(groupname="admin").one()

    # user = models.User("rkg", "123", "RKG", "rkg@rkg.rkg", ["admin"])
    user = models.User(username="rkg", password="123", name="RKG")
    user.groups.append(admin)
    db.session.add(user)
    db.session.commit()

if __name__ == "__main__":
    db_testdata()
