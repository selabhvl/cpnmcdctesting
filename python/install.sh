#!/usr/bin/env bash
#pip3 uninstall MCDC
pip3 install -r requirements.txt --user
python3 setup.py clean --all
python3 setup.py build
python3 setup.py install --force --user