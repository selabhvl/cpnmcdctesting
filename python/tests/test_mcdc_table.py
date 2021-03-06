import os
import sys
import unittest

from MCDC.MCDC_Table import MCDC_Table
from MCDC.LogFile import LogFile


##############
# MCDC_Table #
##############

class MCDCTableTestCase(unittest.TestCase):

    def setUp(self):
        self.logfiles = 'examples'
        # Number of examples that will execute
        self.numfiles_test = 100

    def read_logfiles(self, list_filenames):
        # type: (MCDCTableTestCase, list) -> iter
        list_dict = []
        for filename in list_filenames:
            self.assertTrue(os.path.isfile(filename), filename)
            # Log file generated by CPN Tool
            log = LogFile(filename=filename)
            # Dictionary of MCDC_Table
            file = dict()
            for row in log.read_line():
                filtered_row = log.filter_line(row)
                if filtered_row is not None:
                    id_name, truth_values, result = filtered_row
                    if id_name not in file.keys():
                        file[id_name] = MCDC_Table(id_name)
                    else:
                        # self.assertEqual(len(truth_values), len(d[id_name]))
                        self.assertEqual(len(truth_values), file[id_name].num_conditions())

                    file[id_name].update(truth_values, result)
            list_dict.append(file)
        return list_dict

    def is_mcdc_covered(self, list_dict):
        # type: (MCDCTableTestCase, list) -> iter
        # Each input file generates a dict
        for file in list_dict:
            # Each file contains several transition names (i.e., truth tables)
            for trans in file:
                b, r = file[trans].is_mcdc_covered()
                print(file[trans])
                print(file[trans].remaining_conditions())
                print('MCDC covered? {0}\tR {1}'.format(b, r))
                self.assertTrue(b, msg='Failed {0}'.format(file[trans]))
                print('\n')

    def is_not_mcdc_covered(self, list_dict):
        # type: (MCDCTableTestCase, list) -> iter
        # Each input file generates a dict
        for file in list_dict:
            # Each file contains several transition names (i.e., truth tables)
            for trans in file:
                b, r = file[trans].is_mcdc_covered()
                print(file[trans])
                print(file[trans].remaining_conditions())
                print('MCDC covered? {0}\tR {1}'.format(b, r))
                self.assertFalse(b, msg='Failed {0}'.format(file[trans]))
                print('\n')

    def falsify(self, list_dict):
        # type: (MCDCTableTestCase, list) -> iter
        # Remove a row of the truth table so that MCDC is not covered (supposing that initially it is)
        # Each input file generates a dict
        for file in list_dict:
            # Each file contains several transition names (i.e., truth tables)
            for trans in file:
                lconds = file[trans].conditions()
                file[trans].remove(lconds[0])

        return list_dict

    def test_mcdc(self):
        # type: (MCDCTableTestCase) -> None
        test_dir = self.logfiles
        files_path = os.listdir(test_dir)
        list_test_files = [os.path.join(test_dir, x) for x in files_path if x.endswith('.log') or x.endswith('.txt')]
        num_files_test = min(self.numfiles_test, len(list_test_files))
        list_test_files = sorted(list_test_files)[:num_files_test]
        list_dict = self.read_logfiles(list_filenames=list_test_files)
        self.is_mcdc_covered(list_dict)
        list_dict_falsified = self.falsify(list_dict)
        self.is_not_mcdc_covered(list_dict_falsified)


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)
