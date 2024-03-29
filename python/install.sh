#!/usr/bin/env bash
pip3 install -r requirements.txt
#pip3 uninstall MCDC
python3 setup_mcdc.py clean --all
python3 setup_mcdc.py build
python3 setup_mcdc.py install --force --user
#pip3 uninstall CPNParser
python3 setup_cpnparser.py clean --all
python3 setup_cpnparser.py build
python3 setup_cpnparser.py install --force --user
#run tests
cd tests
./instrument.sh