import os
import re
import unittest

from MCDC.LogFile import LogFile

############
# LogFile #
############

class LogFileTestCase(unittest.TestCase):

    def setUp(self):
        self.logfiles = 'logfiles'
        # Number of examples that will execute
        self.numfiles_test = 100

    def read_logfiles(self, list_files):
        # type: (LogFileTestCase, list) -> None
        for filename in list_files:
            self.assertTrue(os.path.isfile(filename), filename)
            # Log file generated by CPN Tool
            log = LogFile(filename=filename)
            for row in log.read_line():
                filtered_row = log.filter_line(row)
                if filtered_row is not None:
                    id_name, truth_values, result = filtered_row
                    self.assertTrue(re.match(r'(\b\w+\b)', id_name))
                    self.assertTrue(re.match(r'(\b[0-1\?]+\b)', truth_values))
                    self.assertTrue(re.match(r'(\b[0-1]\b)', result))

    def test_read_logfiles(self):
        # type: (LogFileTestCase) -> None

        test_dir = self.logfiles
        files_path = os.listdir(test_dir)
        list_test_files = [os.path.join(test_dir, x) for x in files_path if x.endswith('.log') or x.endswith('.txt')]
        num_files_test = min(self.numfiles_test, len(list_test_files))
        list_test_files = sorted(list_test_files)[:num_files_test]
        self.read_logfiles(list_files=list_test_files)


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)
