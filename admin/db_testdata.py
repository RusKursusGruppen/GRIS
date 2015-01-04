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

    user = models.User(username="kat", password="123", name="kat")
    user.groups.append(admin)
    db.session.add(user)

    user = models.User(username="fugl", password="123", name="Fugl")
    user.groups.append(admin)
    db.session.add(user)

    user = models.User(username="tiger", password="123", name="TIGER")
    db.session.add(user)

    # k = models.User_creation_key(key="email="me")
    # db.session.add(k)

    db.session
    db.session.commit()


if __name__ == "__main__":
    db_testdata()
