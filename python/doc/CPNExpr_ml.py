import os
import sys
import xml.etree.ElementTree as ET
from CPNParser.cpnxml import extract_elements_with_ml, get_ml, set_ml


if __name__ == "__main__":
    in_filename = sys.argv[1]

    xml_tree = ET.parse(in_filename)
    # in_filename = "../tests/cpn_models/cpnabs/cpnabs.cpn"
    # out_filename = "../tests/cpn_models/cpnabs/cpnabs_script_instr.cpn"

    basename = os.path.splitext(in_filename)[0] # "/path/to/some/file.txt"

    print("ML")
    ml_declarations = extract_elements_with_ml(xml_tree)
    for a in ml_declarations:
        expr = get_ml(a)
        print(expr)
