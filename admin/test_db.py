# -*- coding: utf-8 -*-

from gris import data
from reset_db import rest_db
from server import usermanager

def test_db():
    reset_db()
    usermanager.create_user('rkg','123','RKG', groups=['admin', 'rkg', 'mentor'])
    usermanager.create_user('fugl','123', 'FUGL')
    usermanager.create_user('kat','123', 'KAT')
    usermanager.create_user('tiger','123', 'TIGER')

if __name__ == "__main__":
    test_db()
