import pytest

import re
import sys
import xml.etree.ElementTree as ET
from CPNParser.cpnxml import extract_elements_with_conditions, extract_elements_with_annotations, find_element_by_expr_name, get_cond, set_cond, get_annot, set_annot
from CPNParser.cpnexprparse import parse, parse_guard, condparser

cpn_files = ["cpn_models/cpnabs/cpnabs.cpn", "cpn_models/discspcpn/discspcpn.cpn", "cpn_models/mqtt/mqtt.cpn", "cpn_models/paxos/paxos.cpn"]
csv_cond_files = ["cpn_models/cpnabs/cpnabs_trans.csv", "cpn_models/discspcpn/discspcpn_trans.cpn", "cpn_models/mqtt/mqtt_trans.cpn", "cpn_models/paxos/paxos_trans.cpn"]
csv_annot_files = ["cpn_models/cpnabs/cpnabs_arcs.csv", "cpn_models/discspcpn/discspcpn_arcs.cpn", "cpn_models/mqtt/mqtt_arcs.cpn", "cpn_models/paxos/paxos_arcs.cpn"]

error_cpnabs = ["p9=hd pl9 andalso (if (mem pl27 p9) then p24=p9 else not (p24=p9))"]
error_mqtt = ['1`(id,tag)++1`(id,cval)']
error_paxos = ["if (not b) andalso PrepareQFCond(cid,crnd',preparereplies') then 1`PrepareQFProm(cid,crnd',preparereplies') else empty"]
error_discspcpn = ['1`(id,tag)++1`(id,cval)']

# def add_file_to_load():
#     # type: () -> list
#     # local_dirs = [x[0] for x in os.walk('Oracle/OracleSTL')]
#     local_dirs = [x[0] for x in os.walk(self.this_dir)]
#     oraclestl_filenames = []
#     for local_dir in local_dirs:
#         oraclestl_filenames += self.add_file_to_load_from_folder(local_dir)
#     return oraclestl_filenames
#
#
# def add_file_to_load_from_folder( folder):
#     # type: (str) -> list
#     # test_dir = self.this_dir + folder
#     test_dir = folder
#     files_path = os.listdir(test_dir)
#     test_txt = [os.path.join(test_dir, x) for x in files_path if x.endswith('.txt')]
#
#     assert all(os.path.isfile(test) for test in test_txt)
#
#     return test_txt
#
# @pytest.mark.parametrize("original_expected_annot", zip(cpn_files, csv_annot_files))
# def test_arc_transformation(original_expected_annot):
#     original, expected = original_expected_annot
#
#     transformation = [parse(t) for t in original]
#     for i, trans in enumerate(transformation):
#         if trans not in expected:
#             pytest.xfail('{} > {}'.format(original[i], trans))
#
# @pytest.mark.parametrize("original_expected_guard_cond", zip(cpn_files, csv_cond_files))
# def test_transition_transformation(original_expected_guard_cond):
#     original, expected = original_expected_guard_cond
#
#     transformation = [parse_guard(t) for t in original]
#     for i, trans in enumerate(transformation):
#         if trans not in expected:
#             pytest.xfail('{} > {}'.format(original[i], trans))

def test_cond1():
    e = condparser.parse("hd foo = bar")
    print(e)
    assert re.match("^AP.*",e) is not None


def test_cond2():
    e = condparser.parse("if hd foo = bar the true else false")
    print(e)
    assert re.match("^AP.*",e) is not None


def test_exp1():
    e = parse("hd foo = bar")
    print(e)
    assert re.match("EXPR.*",e) is not None

@pytest.mark.parametrize("error_cpnabs", error_cpnabs)
def test_cpnabs(error_cpnabs):
    for expr in error_cpnabs:
        e = parse(expr)
        print(e)
        assert re.match("EXPR.*",e) is not None

def test_mqtt(error_mqtt):
    for expr in error_mqtt:
        e = parse(expr)
        print(e)
        assert re.match("EXPR.*",e) is not None

def test_paxos(error_paxos):
    for expr in error_paxos:
        e = parse(expr)
        print(e)
        assert re.match("EXPR.*",e) is not None

def test_discspcpn(error_discspcpn):
    for expr in error_discspcpn:
        e = parse(expr)
        print(e)
        assert re.match("EXPR.*",e) is not None
