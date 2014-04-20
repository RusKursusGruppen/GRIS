#!/bin/bash

dir=$(dirname $(readlink -f $0))
rootdir=$dir/..

rm -f $rootdir/data.db

sqlite3 $rootdir/data.db < $dir/schema.sql
