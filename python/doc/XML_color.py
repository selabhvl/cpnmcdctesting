import sys
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
import re

from MCDC.LogFile import LogFile
from MCDC.MCDC_Table import MCDC_Table

pattern = r"\W*EXPR\W*(?P<cond_name>\w+)\b"
cond_regex = re.compile(pattern)
# example = '[EXPR("sS", AND(AND(AND(AND(AND( AND(AP("1",(checkClientCON(cs))), AP("2",(nLR msgs))), AP("3",(c = #1 cs))), AP("4",(listpids = []))), AP("5",(notSubscribed(t,cs)))), AP("6",(subLR (#pid (#2 cs))))), AP("7",(isSubscriber(cs)))))]'
# res = cond_regex.match(example)
# res.group(1)
# res.group('cond_name')

def main(file_name):
    tree = ET.parse(file_name)
    root = tree.getroot()
    for arc in root.iter('arc'):
        id = arc.get('id')
        name = arc.find('text').text
        print(id, name)

    for trans in root.iter('trans'):
        id = trans.get('id')
        name = trans.find('text').text
        print(id, name)


def set_color(element, color):
    # type: (Element, str) -> Element
    # <fillattr colour="White"
                  # pattern=""
                  # filled="false"/>
    # <lineattr colour="Black"
                  # thick="1"
                  # type="solid"/>
    fa = element.find('fillattr')
    fa.attrib['colour'] = color
    fa.attrib['filled'] = 'true'

    la = element.find('fillattr')
    la.attrib['colour'] = color

    return element


def extract_elements_with_conditions(xml_tree):
    # type: (ET) -> set
    parent = {p for p in xml_tree.findall('.//cond/..')}
    return parent


def find_element_with_expr(elements_with_conditions, name):
    # type: (set, str) -> Element
    sname = name.strip()
    for element in elements_with_conditions:
        cond = element.find('cond')
        text = cond.find('text').text
        if text is not None:
            res = cond_regex.match(text)
            if res is not None:
                cond_name = res.group(1)
                if cond_name == sname:
                    print(cond_name, cond.attrib, element.attrib)
                    return element


def find_element_f(xml_tree, name):
    # type: (ET, str) -> Element
    root = xml_tree.getroot()
    sname = name.strip()
    for cond in root.iter('cond'):
        id = cond.get('id')
        text = cond.find('text').text
        if text is not None:
            res = cond_regex.match(text)
            if res is not None:
                cond_name = res.group(1)
                if cond_name == sname:
                    return cond
                # print(id, cond_name)


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
    for cond in file:
        e = find_element_with_expr(elements, cond)
        if e is not None:
            b, r = file[cond].is_mcdc_covered()
            color = 'Green' if b else 'Red'
            set_color(e, color)

    xml_tree.write(out_filename)
