#!/bin/bash

rm -f data.db

sqlite3 data.db < admin/schema.sql
