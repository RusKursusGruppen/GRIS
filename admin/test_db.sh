
sqlite3 data.db < admin/schema.sql
python2 -c "from applications import usermanager;
usermanager.create_user('rkg','abe','RKG',1)
usermanager.create_user('fugl','123');
usermanager.create_user('kat','123');
usermanager.create_user('tiger','123');
"
