import sys
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
import re

# pattern = r"\W*EXPR\W*(?P<cond_name>\w+)\b"
pattern = r"[.\s]*(?<=EXPR)\W*(?P<cond_name>\w+)[.\s]*"
cond_regex = re.compile(pattern)
# example = '(* REQx  *)\n' \
#           '    EXPR("RQ4T1", AND(AND(AND(\n' \
#           '    AP("1", the_system_mode = preparing_weak_coffee),\n' \
#           '    AP("2",(time() - the_request_timer)  <= 30)),\n' \
#           '    AP("3", (time() - the_request_timer)  >= 10)),\n' \
#           '    NOT(AP("4",(String.isSuffix "REQ004" trace)))))\n'
# res = cond_regex.match(example)
# res.group('cond_name')


def get_arcs(xml_tree):
    root = xml_tree.getroot()
    for arc in root.iter('arc'):
        id = arc.get('id')
        name = arc.find('text').text
        print(id, name)


def get_trans(xml_tree):
    root = xml_tree.getroot()
    for arc in root.iter('trans'):
        id = arc.get('id')
        name = arc.find('text').text
        print(id, name)


def main(file_name):
    tree = ET.parse(file_name)
    get_arcs(tree)


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

# <cond id="ID1421718565">
#   <posattr x="1402.000000"
# 		   y="-193.000000"/>
#   <fillattr colour="White"
# 			pattern="Solid"
# 			filled="false"/>
#   <lineattr colour="Black"
# 			thick="0"
# 			type="Solid"/>
#   <textattr colour="Black"
# 			bold="false"/>
#   <text tool="CPN Tools"
# 		version="4.0.1">EXPR("Cidle",ITE(AP("1", b2=true),AP("2", ob14 =ob25),AP("3", ob14<>ob25)))</text>
# </cond>


def get_cond(element):
    # type: (Element) -> str
    cond = element.find('cond')
    text = cond.find('text')
    if text.text is not None:
        return text.text

def set_cond(element, c):
    # type: (Element, str) -> None
    cond = element.find('cond')
    text = cond.find('text')
    text.text = c


def extract_elements_with_conditions(xml_tree):
    # type: (ET) -> set
    # Transitions have conditions
    parent = [p for p in xml_tree.findall('.//cond/..')]
    return parent


def get_annot(element):
    # type: (Element) -> str
    cond = element.find('annot')
    text = cond.find('text')
    if text.text is not None:
        return text.text

def set_annot(element, c):
    # type: (Element, str) -> None
    cond = element.find('annot')
    text = cond.find('text')
    text.text = c

def extract_elements_with_annotations(xml_tree):
    # type: (ET) -> set
    # Arcs have annotations
    parent = [p for p in xml_tree.findall('.//annot/..')]
    return parent


#TODO: Do we also process the "conditions" in the arcs? Right now, we only color transitions.
def find_element_by_expr_name(elements_with_conditions, elements_with_annotations, expr_name):
    # type: (set, set, str) -> Element
    sname = expr_name.strip()
    for element in elements_with_conditions:
        cond = element.find('cond')
        text = cond.find('text').text
        if text is not None:
            # res = cond_regex.match(text)
            res = cond_regex.search(text)
            # print(text)
            # print(res)
            if res is not None:
                cond_name = res.group(1)
                if cond_name == sname:
                    print(cond_name, cond.attrib, element.attrib)
                    return element

    for element in elements_with_annotations:
        cond = element.find('annot')
        text = cond.find('text').text
        if text is not None:
            # res = cond_regex.match(text)
            res = cond_regex.search(text)
            # print(text)
            # print(res)
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
