from sortedcontainers import SortedDict, SortedSet
from MCDC._py3k import red


class MCDC_Table:

    def __init__(self, name=""):
        # type: (MCDC_Table) -> None
        # self.table = SortedDict()
        self.table = dict()
        self.name = name
        self.num_truth_values = None

    def __repr__(self):
        # type: (MCDC_Table) -> str
        # l = ['{0}\t{1}\n'.format(bin(i), bin(self.table[i])) for i in self.table.keys()]
        # l = ['{0:0{pad}b}\t{1:0b}\n'.format(i, self.table[i], pad=self.num_truth_values) for i in self.table.keys()]
        l = ['{0}\t{1}\n'.format(self._key_str(i), self._val_str(self.table[i])) for i in sorted(self.table.keys())]
        rows = red(lambda a, b: a + b, l)
        return '{0}\n{1}'.format(self.name, rows.rstrip())

    def __len__(self):
        # type: (MCDC_Table) -> int
        return len(self.table)

    def _key_str(self, key):
        # type: (MCDC_Table) -> str
        return '{0:0{pad}b}'.format(key, pad=self.num_truth_values)

    def _val_str(self, val):
        # type: (MCDC_Table) -> str
        return '{0:0b}'.format(val)

    def num_conditions(self):
        # type: (MCDC_Table) -> int
        return self.num_truth_values

    def update(self, truth_values, result):
        # type: (MCDC_Table, str, str) -> None

        def expand_joker_symbol(truth_values):
            # type: (str) -> list

            result_set = []

            if '?' in truth_values:
                # '?' symbol may happen multiple times in the sequence
                pos = truth_values.find('?')
                seq1 = truth_values[:pos] + '0' + truth_values[pos + 1:]
                seq2 = truth_values[:pos] + '1' + truth_values[pos + 1:]
                result_set.extend(expand_joker_symbol(seq1))
                result_set.extend(expand_joker_symbol(seq2))
            else:
                result_set = [truth_values]

            return result_set

        # Each truth_values[i] represents a bool bit 0/1 (False/True)
        # truth_values = '0110101'
        if self.num_truth_values is None:
            self.num_truth_values = len(truth_values)
        assert self.num_truth_values == len(
            truth_values), 'Incorrect number of truth values for {0}: {1} instead of {2}'.format(self.name,
                                                                                                 len(truth_values),
                                                                                                 self.num_truth_values)
        # Interpret the bool array as an decimal number and use it for indexing the dictionary
        if '?' in truth_values:
            # '?' symbol may happen multiple times in the sequence
            seq_list = expand_joker_symbol(truth_values)
            for seq in seq_list:
                self.update(seq, result)
        else:
            # Convert truth_value "010" into integer(2)
            dec = int(truth_values, 2)
            # Convert result "0"/"1" into bool False/True
            val = bool(int(result))

            # Prevent updating the 'result' value in the MCDC Table
            assert (dec not in self.table.keys()) or (self.table[dec] == val), \
                'Error inserting ({0}, {1}): already in the truth table with value {2}'.format(truth_values, val, not val)

            self.table[dec] = val

    def remove(self, truth_values):
        # type: (MCDC_Table, str) -> None
        dec = int(truth_values, 2)
        del self.table[dec]

    def conditions(self):
        # type: (MCDC_Table) -> list
        # Returns all the entries in the truth table (i.e., only the conditions, not the result expression)
        return list(self._key_str(i) for i in self.table.keys())

    def remaining_conditions(self):
        # type: (MCDC_Table) -> (int, iter)
        # Generates all the combinations that are not included in the truth table
        total_number_conditions = 0
        if self.num_truth_values is not None:
            total_number_conditions = pow(2, self.num_truth_values)
        remaining_keys = (bin(i) for i in range(total_number_conditions) if i not in self.table.keys())
        return total_number_conditions - len(self.table), remaining_keys

    def is_complete(self):
        # type: (MCDC_Table) -> bool
        number, keys = self.remaining_conditions()
        return number == 0

    def partition(self, c):
        # type: (MCDC_Table, int) -> (iter, iter)
        # key_set = set('{0:0{pad}b}'.format(i, pad=self.num_truth_values) for i in self.table.keys())
        key_set = ((key, self._key_str(key)) for key in self.table.keys())
        # ff = SortedSet(key for (key, key_str) in key_set if key_str[c] == '0')
        # tt = SortedSet(self.table.keys()) - ff

        ff = set(key for (key, key_str) in key_set if key_str[c] == '0')
        tt = set(self.table.keys()) - ff

        # return sorted(ff, key=lambda x: int(x,2)), sorted(tt, key=lambda x: int(x,2))
        return sorted(ff), sorted(tt)

    def num_conds_mcdc_covered(self):
        _, conds = self.is_mcdc_covered()
        num_conds_covered = sum(c != [] for c in conds.values())
        return num_conds_covered

    def is_mcdc_covered(self):
        # type: (MCDC_Table) -> (bool, dict)
        def flip(f, c):
            # type: (int, int) -> int
            # flip = key XOR (1<<c)
            mask = 1 << c
            return f ^ mask

        # def flip2(f, c):
        #     # type: (int, int) -> int
        #     key_str = self._key_str(f)
        #     flip_val = (int(key_str[c]) + 1) % 2
        #     key_str = key_str[:c] + str(flip_val) + key_str[c + 1:]
        #     return int(key_str, 2)

        # r = dict.fromkeys(self.table.keys())
        r = {key: [] for key in range(1, self.num_truth_values+1)}
        for cond in range(self.num_truth_values):
            ff_keys, tt_keys = self.partition(cond)
            # print('{0}\t0:{1}\t1:{2}'.format(cond, [self._key_str(f) for f in ff_keys], [self._key_str(t) for t in tt_keys]))
            for f_key in ff_keys:
                # fp_key = flip2(f_key, cond)
                fp_key = flip(f_key, self.num_truth_values - cond - 1)
                if fp_key in tt_keys:
                    if self.table[f_key] != self.table[fp_key]:
                        r[cond+1] += [(self._key_str(f_key), self._key_str(fp_key))]

        return all(len(r[cond]) > 0 for cond in r.keys()), r

    def is_branch_covered(self):
        # type: (MCDC_Table) -> bool
        return (True in self.table.values()) and (False in self.table.values())
