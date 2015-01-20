# -*- coding: utf-8 -*-

from gris import app, data
from admin.reset_db import reset_db
from server import usermanager

def test_db():
    reset_db()
    usermanager.create_user('rkg','123','RKG', groups=['admin', 'rkg', 'mentor'])
    usermanager.create_user('fugl','123', 'FUGL')
    usermanager.create_user('kat','123', 'KAT')
    usermanager.create_user('tiger','123', 'TIGER')

if __name__ == "__main__":
    with app.app_context():
        test_db()
