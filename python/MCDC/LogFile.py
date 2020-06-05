import csv
import re


class LogFile:
    def __init__(self, filename=''):
        # type: (LogFile, str) -> None
        self.filename = filename
        self.re_pattern = self._reg_exp()

    @staticmethod
    def _reg_exp():
        # id_name = r'(?P<id_name>[^:]*)'
        # truth_values = r'(?P<truth_values>[^:]*)'
        # result = r'(?P<result>[^:]*)'
        # bool_expr = r'(\b{0}\:\b({1}\:\b{2}\b)*)'.format(id_name, truth_values, result)
        id_name = r'(?P<id_name>[\w]+)'
        truth_values = r'(?P<truth_values>[0|1]+)'
        result = r'(?P<result>[0|1])'
        bool_expr = r'(\b{0}\:\b{1}\:\b{2}\b)'.format(id_name, truth_values, result)
        return re.compile(bool_expr)

    def read_line(self):
        # type: (LogFile) -> list
        csvfile = open(self.filename, 'r')
        reader = csv.reader(csvfile, delimiter=' ', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            yield row
        csvfile.close()

    def filter_line(self, row):
        # type: (str) -> list
        assert row != ""
        # Input: 'PQo:01011:0'
        # Output: ['PQo','01011','0']
        # [id_name, truth_values, result]

        val_formula = self.re_pattern.match(row[len(row) - 1])
        if val_formula is not None:
            return [val_formula.group('id_name'), val_formula.group('truth_values'), val_formula.group('result')]
