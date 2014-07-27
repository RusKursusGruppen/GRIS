#!/bin/bash

dir=$(dirname $(readlink -f $0))
rootdir=$dir/..

cd $rootdir
source env/bin/activate

# Clear everything:
python -c "from lib import data;data.execute('DROP SCHEMA public CASCADE; CREATE SCHEMA public')"
# Create databases:
python -c "from lib import data;result = (data.script('admin/schema.sql'));print('No errors.' if result is None else result)"
