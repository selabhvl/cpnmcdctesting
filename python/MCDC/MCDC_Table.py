from sortedcontainers import SortedDict
from MCDC._py3k import red


class MCDC_Table:

    def __init__(self, name=""):
        # type: (MCDC_Table) -> None
        self.table = SortedDict()
        self.name = name
        self.num_truth_values = None

    def __repr__(self):
        # type: (MCDC_Table) -> str
        l = ['{0}\t{1}\n'.format(bin(i), bin(self.table[i])) for i in self.table.keys()]
        return '{0}\n{1}'.format(self.name, red(lambda a, b: a + b, l))

    def update(self, truth_values, result):
        # type: (MCDC_Table, str, str) -> None
        # Each truth_values[i] represents a bool bit 0/1 (False/True)
        # truth_values = '0110101'
        if self.num_truth_values is None:
            self.num_truth_values = len(truth_values)
        assert self.num_truth_values == len(truth_values), 'Incorrect number of truth values for {0}'.format(self.name)
        # Interpret the bool array as an decimal number and use it for indexing the dictionary
        if '?' in truth_values:
            pos = truth_values.find('?')
            self.update(truth_values[:pos] + '0' + truth_values[pos + 1:], result)
            self.update(truth_values[:pos] + '1' + truth_values[pos + 1:], result)
        else:
            dec = int(truth_values, 2)
            # Convert result "0"/"1" into bool False/True
            val = bool(int(result))

            # Prevent updating the 'result' value in the MCDC Table
            assert (dec not in self.table.keys()) or (self.table[dec] == val)

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

    def is_mcdc_covered(self):
        return False
