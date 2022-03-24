python3 ../doc/CPNExpr_instrument.py ./cpn_models/paxos/paxos.cpn ./cpn_models/paxos/paxos_instr_2.cpn &> output1.txt
python3 ../doc/CPNExpr_instrument.py ./cpn_models/cpnabs/cpnabs.cpn ./cpn_models/cpnabs/cpnabs_instr_2.cpn &> output2.txt
python3 ../doc/CPNExpr_instrument.py ./cpn_models/mqtt/mqtt.cpn ./cpn_models/mqtt/mqtt_instr_2.cpn &> output3.txt
python3 ../doc/CPNExpr_instrument.py ./cpn_models/discspcpn/discspcpn.cpn ./cpn_models/discspcpn/discspcpn_instr_2.cpn &> output4.txt

python3 ../doc/CPNExpr_instrument.py ./cpn_models/paxos/paxos_instr_2.cpn /dev/null &>> output1.txt
python3 ../doc/CPNExpr_instrument.py ./cpn_models/cpnabs/cpnabs_instr_2.cpn /dev/null  &>> output2.txt
python3 ../doc/CPNExpr_instrument.py ./cpn_models/mqtt/mqtt_instr_2.cpn /dev/null  &>> output3.txt
python3 ../doc/CPNExpr_instrument.py ./cpn_models/discspcpn/discspcpn_instr_2.cpn /dev/null  &>> output4.txt

#python3 ../doc/CPNExpr_ml.py ./cpn_models/cpnabs/cpnabs.cpn &> ml_output1.txt
#python3 ../doc/CPNExpr_ml.py ./cpn_models/mqtt/mqtt.cpn &> ml_output2.txt
#python3 ../doc/CPNExpr_ml.py ./cpn_models/paxos/paxos.cpn &> ml_output3.txt
#python3 ../doc/CPNExpr_ml.py ./cpn_models/discspcpn/discspcpn.cpn  &> ml_output4.txt