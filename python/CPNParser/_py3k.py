import sys
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