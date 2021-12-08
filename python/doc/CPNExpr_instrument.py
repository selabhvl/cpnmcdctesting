import sys
import csv
import xml.etree.ElementTree as ET
from CPNParser.cpnxml import extract_elements_with_conditions, extract_elements_with_annotations, find_element_by_expr_name, get_cond, set_cond, get_annot, set_annot
from CPNParser.cpnexprparse import parse, parse_guard

if __name__ == "__main__":
    in_filename = sys.argv[1]
    out_filename = sys.argv[2]

    xml_tree = ET.parse(in_filename)
    # in_filename = "../tests/cpn_models/cpnabs/cpnabs.cpn"
    # out_filename = "../tests/cpn_models/cpnabs/cpnabs_script_instr.cpn"

    csvfile = open('./temp_trans.csv', 'w', newline='')
    trace = csv.writer(csvfile, delimiter='|', quoting=csv.QUOTE_MINIMAL)

    print("Transitions")
    transitions = extract_elements_with_conditions(xml_tree)
    for t in transitions:
        expr = get_cond(t)
        if expr is not None:
            inst_expr = parse_guard(expr)
            set_cond(t, inst_expr)
            trace.writerow([expr, inst_expr])
            print("{0} | {1}".format(expr, inst_expr))

    csvfile.close()
    csvfile = open('./temp_arcs.csv', 'w', newline='')
    trace = csv.writer(csvfile, delimiter='|', quoting=csv.QUOTE_MINIMAL)

    print("Arcs")
    arcs = extract_elements_with_annotations(xml_tree)
    for a in arcs:
        expr = get_annot(a)
        if expr is not None:
            inst_expr = parse(expr)
            set_annot(a, inst_expr)
            trace.writerow([expr, inst_expr])
            print("{0} | {1}".format(expr, inst_expr))

    xml_tree.write(out_filename, xml_declaration=True)
    csvfile.close()