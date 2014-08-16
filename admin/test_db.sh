#!/bin/bash
# -*- coding: utf-8 -*-

dir=$(dirname $(readlink -f $0))
rootdir=$dir/..

cd $rootdir
source ./env/bin/activate

admin/reset_db.sh

if [[ $? == 0 ]]
then
echo "Inserting entries..."
python << EOF
# Insert python code for testdata here:
from lib import data
from applications import usermanager

# Create users:
usermanager.create_user('rkg','abe','RKG', groups=['admin', 'rkg', 'mentor'])
usermanager.create_user('fugl','123', 'FUGL')
usermanager.create_user('kat','123', 'KAT')
usermanager.create_user('tiger','123', 'TIGER')



# End of python
EOF
fi
