#!/bin/bash
# -*- coding: utf-8 -*-

source env/bin/activate

sqlite3 data.db < admin/schema.sql
python -c "from applications import usermanager;
usermanager.create_user('rkg','abe','RKG',['admin', 'rkg', 'tutor', 'mentor'])
usermanager.create_user('fugl','123', 'FUGL');
usermanager.create_user('kat','123', 'KAT');
usermanager.create_user('tiger','123', 'TIGER');
"
