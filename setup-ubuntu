#! /bin/bash

## this script should potentially make your pip file appear in the env/bin/ folder.

echo "lets make your pip work"
echo
pyvenv-3.3 env
echo
source env/bin/activate
echo
wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py -O - | python
echo
curl -O https://raw.github.com/pypa/pip/master/contrib/get-pip.py
echo
python get-pip.py
echo
