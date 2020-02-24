import sys

from MCDC.MCDC_Table import MCDC_Table
from MCDC.LogFile import LogFile

if __name__ == "__main__":
    # LogFile generated by CPN Tool
    log = LogFile(filename=sys.argv[1])
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

    for trans in file:
        print(file[trans])
        print(file[trans].remaining_conditions())
        b, r = file[trans].is_mcdc_covered()
        print('MCDC covered? {0}\tR {1}'.format(b, r))
