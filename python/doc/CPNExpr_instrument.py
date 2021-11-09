import sys
import xml.etree.ElementTree as ET
from CPNParser.cpnxml import extract_elements_with_conditions, find_element_by_expr_name, get_cond, set_cond
from CPNParser.cpnexprparse import parse

if __name__ == "__main__":
    log_filename = sys.argv[1]
    in_filename = sys.argv[2]
    out_filename = sys.argv[3]

    xml_tree = ET.parse(in_filename)
    elements = extract_elements_with_conditions(xml_tree)
    for e in elements:
        expr = get_cond(e)
        inst_expr = parse(expr)
        set_cond(e, inst_expr)
        print(inst_expr)

    xml_tree.write(out_filename, xml_declaration=True)
