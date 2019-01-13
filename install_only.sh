#!/usr/bin/env bash

CFLAGS=$(python3-config --cflags)
LDFLAGS=$(python3-config --ldflags)

python setup.py build_ext
python setup.py bdist
python setup.py install