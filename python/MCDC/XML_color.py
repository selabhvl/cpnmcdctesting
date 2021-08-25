import sys
import xml.etree.ElementTree as ET
import re

pattern = r"\W*EXPR\W*(?P<cond_name>\w+)\b"
cond_regex = re.compile(pattern)
# example = '[EXPR("sS", AND(AND(AND(AND(AND( AND(AP("1",(checkClientCON(cs))), AP("2",(nLR msgs))), AP("3",(c = #1 cs))),  AP("4",(listpids = []))),  AP("5",(notSubscribed(t,cs)))),  AP("6",(subLR (#pid (#2 cs))))), AP("7",(isSubscriber(cs)))))]'

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

def color(element):
    # <fillattr colour="White"
                  # pattern=""
                  # filled="false"/>
        # <lineattr colour="Black"
                  # thick="1"
                  # type="solid"/>
    return


def extract_elements_with_conditions(file_name):
    tree = ET.parse(file_name)
    root = tree.getroot()
    parent = {p for p in tree.findall('.//cond/..')}
    # for p in parent:
        # print(p.get('id'))
    return parent

def find_element(elements_with_conditions, name):
    sname = name.strip()
    for element in elements_with_conditions:
        cond = element.find('cond')
        text = cond.find('text').text
        if text is not None:
            res = cond_regex.match(text)
            cond_name = res.group(1)
            if cond_name == sname:
                print(cond_name, cond.attrib, element.attrib)
                return element


 
def find_element_f(file_name, name):
    tree = ET.parse(file_name)
    root = tree.getroot()
    sname = name.strip()
    for cond in root.iter('cond'):
        id = cond.get('id')
        text = cond.find('text').text
        if text is not None:
            res = cond_regex.match(text)
            cond_name = res.group(1)
            if cond_name == sname:
                return cond
            # print(id, cond_name)

if __name__ == "__main__":
    file_name = sys.argv[1]
    # main(file_name)
    # find_element(file_name, file_name)
    parent = extract_elements_with_conditions(file_name)
    find_element(parent, 'rQR0')

