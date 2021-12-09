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
python3 ./doc/CPNExpr_instrument.py ./tests/cpn_models/cpnabs/cpnabs.cpn ./tests/cpn_models/cpnabs/cpnabs_script_instr.cpn &> output1.txt
python3 ./doc/CPNExpr_instrument.py ./tests/cpn_models/mqtt/mqtt.cpn ./tests/cpn_models/mqtt/mqtt_script_instr.cpn &> output2.txt
python3 ./doc/CPNExpr_instrument.py ./tests/cpn_models/paxos/paxos.cpn ./tests/cpn_models/paxos/paxos_script_instr.cpn &> output3.txt
python3 ./doc/CPNExpr_instrument.py ./tests/cpn_models/discspcpn/discspcpn.cpn ./tests/cpn_models/discspcpn/discspcpn_script_instr.cpn &> output4.txt