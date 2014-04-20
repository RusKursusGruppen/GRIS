#!/bin/bash
# -*- coding: utf-8 -*-

dir=$(dirname $(readlink -f $0))
rootdir=$dir/..

cd $rootdir

admin/reset_db.sh

source /env/bin/activate

python -c "from applications import usermanager;
usermanager.create_user('rkg','abe','RKG',['admin', 'rkg', 'tutor', 'mentor'])
usermanager.create_user('fugl','123', 'FUGL');
usermanager.create_user('kat','123', 'KAT');
usermanager.create_user('tiger','123', 'TIGER');
"

deactivate
cd -
