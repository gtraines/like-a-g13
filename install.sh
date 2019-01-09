#!/usr/bin/env bash

sudo apt-get update
sudo apt-get install -y rustc cargo

pip install -r requirements.txt
python setup.py install
