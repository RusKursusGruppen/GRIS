#!/bin/bash
# -*- coding: utf-8 -*-

dir=$(dirname $(readlink -f $0))
rootdir=$dir/..

cd $rootdir
source ./env/bin/activate

python << EOF
from lib.configuration import create_secret_key
create_secret_key()
EOF

if [[ $? == 0 ]]
then
    echo "Generated new secret_key"
fi
