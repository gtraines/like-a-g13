#!/usr/bin/env bash

sudo apt-get update
sudo apt-get install -y rustc cargo

chmod +x utils/set_perms.sh
sudo bash utils/set_perms.sh

pip install -r requirements.txt

CFLAGS=$(python-config --cflags)
LDFLAGS=$(python-config --ldflags)

python setup.py build_ext
python setup.py bdist
python setup.py install
