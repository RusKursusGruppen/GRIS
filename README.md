GRIS
====

Generelt Rus Informations System

Note
Dette er ikke den nyeste version, den blev nakket da Søren var en spasser der ikke comittede.
Så nu skal GRIS genskabbes ud fra dette.


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

Dependencies:
Python2
python-flask 9.2
python-bcrypt
sqlite3
python2-itsdangerous (a dependency of flask that might not be satisfied automaticly)
python2-markdown


# Application structure
Folder                      Description
applications/               sub-application files for each module
templates/<application>     sub-application templates for each module


# import convention:
import generic python modules

from flask import ...

from lib import ...
from lib.tools import ...

import config

from application. ... import ...
