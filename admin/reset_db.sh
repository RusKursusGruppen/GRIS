#!/bin/bash

dir=$(dirname $(readlink -f $0))
rootdir=$dir/..

cd $rootdir
source env/bin/activate

echo "Clearing everything..."
python -c "from lib import data;data.execute('DROP SCHEMA public CASCADE; CREATE SCHEMA public')"

if [[ $? == 0 ]]
then
echo "Creating databases..."
python -c "from lib import data;result = (data.script('admin/schema.sql'));None if result is None else print(result)"
# python -c "from lib import data;result = (data.script('admin/schema.sql'))"
fi
