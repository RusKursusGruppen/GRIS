
sqlite3 data.db < admin/schema.sql
python2 -c "from applications import usermanager; usermanager.create_user('rkg','abe','RKG',1)"
