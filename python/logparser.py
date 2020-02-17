# import re
# number = '([+-]?(\d+(\.\d*)?)|(\.\d+))([eE][-+]?\d+)?'
# op = '(\*|\/|\+|\-)+'
# math_regex = r'(\b{0}\b({1}\b{2}\b)*)'.format(number, op, number)
# re.compile(math_regex)
#
# hour = r'(\d{2}:\d{2}:\d{2})'
# day_text = r'(\w{3})'
# day_num = r'(\d{3})'
# month
# year = r'(\d{4})'
# date_matcher = r'(\b{0}\b({1}\b{2}\b)*)'.format(day_text, month, day_num, hour, year)

import sys
import csv
import re
from sortedcontainers import SortedDict

#############################################################################################
if sys.version_info[0] >= 3:
    # Code for Python 3
    from functools import reduce

    def red(function, sequence):
        """Call 'reduce', which applies 'function' over all the elements of the sequence"""
        return reduce(function, sequence)
else:  # sys.version_info[0] < 3
    # Code for Python 2

    def red(function, sequence):
        """Call 'reduce', which applies 'function' over all the elements of the sequence"""
        return reduce(function, sequence)
#############################################################################################


def read_logfile(filename):
    # type: (str) -> list
    csvfile = open(filename, 'r')
    reader = csv.reader(csvfile, delimiter=' ', quoting=csv.QUOTE_MINIMAL)
    for row in reader:
        yield row


def reg_exp():
    id_name = r'(?P<id_name>[^:]*)'
    truth_values = r'(?P<truth_values>[^:]*)'
    result = r'(?P<result>[^:]*)'
    bool_expr = r'(\b{0}\:\b({1}\:\b{2}\b)*)'.format(id_name, truth_values, result)
    return re.compile(bool_expr)


def filter_log_row(row, re_pattern):
    # type: (str) -> list
    assert row != ""
    # Input: 'PQo:01011:0'
    val_formula = re_pattern.match(row[len(row) - 1])
    if val_formula is not None:
        # [id_name, truth_values, result]
        # Output: ['PQo','01011','0']
        return [val_formula.group('id_name'), val_formula.group('truth_values'), val_formula.group('result')]


def filter_log_row2(row):
    # type: (str) -> list
    # id_name = r'(?P<id_name>\w+)'
    # truth_values = r'(?P<truth_values>\d+)'
    # result = r'(?P<result>\d)'
    id_name = r'(?P<id_name>[^:]*)'
    truth_values = r'(?P<truth_values>[^:]*)'
    result = r'(?P<result>[^:]*)'
    bool_expr = r'(\b{0}\:\b({1}\:\b{2}\b)*)'.format(id_name, truth_values, result)
    re_pattern = re.compile(bool_expr)

    print(row[len(row) - 1])
    val_formula = re_pattern.match(row[len(row) - 1])
    if val_formula is not None:
        # print(r'({0} {1} {2})'.format(val_formula.group(0), val_formula.group(1), val_formula.group(2)))
        print(r'({0} {1} {2})'.format(val_formula.group('id_name'), val_formula.group('truth_values'), val_formula.group('result')))
    return val_formula


class MCDC_Table:

    def __init__(self, name=""):
        # type: (MCDC_Table) -> None
        self.table = SortedDict()
        self.name = name
        self.num_truth_values = None

    def __repr__(self):
        # type: (MCDC_Table) -> str
        l = ['{0}\t{1}\n'.format(bin(i), bin(self.table[i])) for i in self.table.keys()]
        return '{0}\n{1}'.format(self.name, red(lambda a, b: a+b, l))

    def update(self, truth_values, result):
        # type: (MCDC_Table, str, str) -> None
        # Each truth_values[i] represents a bool bit 0/1 (False/True)
        # truth_values = '0110101'
        if self.num_truth_values is None:
            self.num_truth_values = len(truth_values)
        assert self.num_truth_values == len(truth_values), 'Incorrect number of truth values for {0}'.format(self.name)
        # Interpret the bool array as an decimal number and use it for indexing the dictionary
        dec = int(truth_values, 2)
        # Convert result "0"/"1" into bool False/True
        val = bool(int(result))
        self.table[dec] = val

    def remaining_conditions(self):
        # type: (MCDC_Table) -> (int, iter)
        total_number_conditions = 0
        if self.num_truth_values is not None:
            total_number_conditions = pow(2, self.num_truth_values)
        remaining_keys = (bin(i) for i in range(total_number_conditions) if i not in self.table.keys())
        return total_number_conditions - len(self.table), remaining_keys

    def is_complete(self):
        number, keys = self.remaining_conditions()
        return number == 0


if __name__ == "__main__":
    filename = sys.argv[1]
    # Dictionary of MCDC_Table
    d = dict()
    re_pattern = reg_exp()
    for row in read_logfile(filename):
        filtered_row = filter_log_row(row, re_pattern)
        if filtered_row is not None:
            print(filter_log_row(row, re_pattern))
            id_name, truth_values, result = filtered_row
            if id_name not in d.keys():
                d[id_name] = MCDC_Table(id_name)

            d[id_name].update(truth_values, result)

    for key in d:
        print(d[key])
        print(d[key].remaining_conditions())
