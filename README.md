GRIS
====

Generelt Rus Informations System

# Conventions  
Always write in English.  
"Rus", "russer" and "rkg" are excepted from this  

Translations  
<Danish> = <English>  
rus      = rus  
russer   = russer  
rkg      = rkg  
vejleder = tutor  
mentor   = mentor  
rustur   = tour  
hytte    = hut  


# How to install:
install python3 through your package manager  
install sqlite3 through your package manager  
install pip (python-pip or python3-pip) through your package manager  
sudo pip install virtualenv (might be necessary)  

Get the GRIS repo:
```
git clone git@github.com:RusKursusGruppen/GRIS.git
```

Run the setup script (Ubuntu users should use ./setup-ubuntu)
```
./setup
```

Create a config file
```
cp config-example.py config.py
```

create a database, while standing in the GRIS dir:
```
./admin/test_db.sh
```

Start the build in webserver:
```
./gris
```

Visit the page in your browser at
```
localhost:5000
```

## Ubuntu:
Beaware that python defaults to python2 in ubuntu!

on ubuntu you might also have to install:  
python3.3-dev  
libffi-dev  
libevent-dev  
libmemcached-dev  
and use ./setup-ubuntu instead  

## Bcrypt
if bcrypt is not working on arch linux you might try the following:  
sudo cp /usr/lib/ffi.h /usr/local/include  
sudo cp /usr/lib/libffi.so /usr/local/lib  
sudo cp /usr/lib/libffi-3.0.13/include/ffitarget.h /usr/local/include  
sudo cp /usr/lib/libffi-3.0.13/include/ffi.h /usr/local/include  

# Working on GRIS
The webserver will automatically detect changes in files, there is no need to restart it manually all the time.

See how-to-work-on-gris.md in the docs folder for the preferred workflow.  

# Application structure
Folder                      Description  
applications/               sub-application files for each module  
templates/<application>     sub-application templates for each module  


# import convention:
```
import generic python modules

from flask import ...

from lib import ...
from lib.tools import ...

import config

from application. ... import ...
```


#Deployment:
in /usr/lib/python3.3/pkgutil.py  
in find_loader on line 501 and 502  
