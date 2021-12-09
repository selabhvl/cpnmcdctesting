import pytest

import re
import sys
import xml.etree.ElementTree as ET
from CPNParser.cpnxml import extract_elements_with_conditions, extract_elements_with_annotations, find_element_by_expr_name, get_cond, set_cond, get_annot, set_annot
from CPNParser.cpnexprparse import parse, parse_guard

cpn_files = ["cpn_models/cpnabs/cpnabs.cpn", "cpn_models/discspcpn/discspcpn.cpn", "cpn_models/mqtt/mqtt.cpn", "cpn_models/paxos/paxos.cpn"]

def add_file_to_load():
    # type: () -> list
    # local_dirs = [x[0] for x in os.walk('Oracle/OracleSTL')]
    local_dirs = [x[0] for x in os.walk(self.this_dir)]
    oraclestl_filenames = []
    for local_dir in local_dirs:
        oraclestl_filenames += self.add_file_to_load_from_folder(local_dir)
    return oraclestl_filenames


def add_file_to_load_from_folder( folder):
    # type: (str) -> list
    # test_dir = self.this_dir + folder
    test_dir = folder
    files_path = os.listdir(test_dir)
    test_txt = [os.path.join(test_dir, x) for x in files_path if x.endswith('.txt')]

    assert all(os.path.isfile(test) for test in test_txt)

    return test_txt

def test_exp1():
    e = parse("hd foo = bar")
    print(e)
    assert re.match("EXPR.*",e) is not None
