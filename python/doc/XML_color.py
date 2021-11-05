import sys
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
import re
from CPNParser.cpnxml import extract_elements_with_conditions, find_element_by_expr_name, set_color

if __name__ == "__main__":
    log_filename = sys.argv[1]
    in_filename = sys.argv[2]
    out_filename = sys.argv[3]

    # LogFile generated by CPN Tool
    log = LogFile(filename=log_filename)
    # The LogFile contains several transition names (i.e., truth tables)
    # Each transition of the PN generates an MCDC_Table
    # All the transitions of the PN are stored in a dictionary of MCDC_Tables
    file = dict()
    for row in log.read_line():
        filtered_row = log.filter_line(row)
        if filtered_row is not None:
            # print(filtered_row)
            id_name, truth_values, result = filtered_row
            if id_name not in file.keys():
                file[id_name] = MCDC_Table(id_name)

            file[id_name].update(truth_values, result)

    xml_tree = ET.parse(in_filename)
    elements = extract_elements_with_conditions(xml_tree)
    for expr_name in file:
        e = find_element_by_expr_name(elements, expr_name)
        if e is not None:
            b, r = file[expr_name].is_mcdc_covered()
            color = 'Green' if b else 'Red'
            set_color(e, color)

    xml_tree.write(out_filename, xml_declaration=True)