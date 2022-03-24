import os
import sys
import csv
import xml.etree.ElementTree as ET
from CPNParser.cpnxml import extract_elements_with_conditions, extract_elements_with_annotations, extract_elements_with_ml, find_element_by_expr_name, get_cond, set_cond, get_annot, set_annot, get_ml, set_ml
from CPNParser.cpnexprparse import parse_cond, parse_annot, parse_fdecls
from CPNParser.cpnexprtransf import traverse, traverse_cond, traverse_annot, traverse_decl

if __name__ == "__main__":
    in_filename = sys.argv[1]
    if len(sys.argv) == 3:
        out_filename = sys.argv[2]
    else:
        # TODO: error output should go to stderr.
        out_filename = "/dev/stdout"

    xml_tree = ET.parse(in_filename)
    # in_filename = "../tests/cpn_models/cpnabs/cpnabs.cpn"
    # out_filename = "../tests/cpn_models/cpnabs/cpnabs_script_instr.cpn"

    basename = os.path.splitext(in_filename)[0] # "/path/to/some/file.txt"

    csvfile = open(basename + '_arcs.csv', 'w', newline='')
    trace = csv.writer(csvfile, delimiter='|', quoting=csv.QUOTE_MINIMAL)

    print("Arcs", file=sys.stderr)
    arcs = extract_elements_with_conditions(xml_tree)
    for t in arcs:
        expr = get_cond(t)
        if expr is not None:
            try:
                ast = parse_cond(expr.replace("\n", " "))
                inst_expr = traverse_cond(ast)
                set_cond(t, inst_expr)
                trace.writerow([expr, inst_expr])
                # print("{0} | {1}".format(expr, inst_expr))
            except:
                # Keep the original SML code if error while instrumenting
                set_cond(t, expr)
                continue
    csvfile.close()

    csvfile = open(basename + '_trans.csv', 'w', newline='')
    trace = csv.writer(csvfile, delimiter='|', quoting=csv.QUOTE_MINIMAL)

    print("Transitions")
    transitions = extract_elements_with_annotations(xml_tree)
    for a in transitions:
        expr = get_annot(a)
        if expr is not None:
            try:
                ast = parse_annot(expr.replace("\n", " "))
                inst_expr = traverse_annot(ast)
                set_annot(a, inst_expr)
                trace.writerow([expr, inst_expr])
                # print("{0} | {1}".format(expr, inst_expr))
            except:
                # Keep the original SML code if error while instrumenting
                set_annot(a, expr)
                continue

    xml_tree.write(out_filename, xml_declaration=True)
    csvfile.close()

    csvfile = open(basename + '_ml.csv', 'w', newline='')
    trace = csv.writer(csvfile, delimiter='|', quoting=csv.QUOTE_MINIMAL)

    print("ML", file=sys.stderr)
    ml_declarations = extract_elements_with_ml(xml_tree)
    for a in ml_declarations:
        expr = get_ml(a)
        if expr is not None:
            try:
                ast = parse_fdecls(expr.replace("\n", " "))
                inst_expr = traverse_decl(ast)
                set_ml(a, inst_expr)
                trace.writerow([expr, inst_expr])
                # print("{0} | {1}".format(expr, inst_expr))
            except:
                # Keep the original SML code if error while instrumenting
                set_ml(a, expr)
                continue

    xml_tree.write(out_filename, xml_declaration=True)
    csvfile.close()