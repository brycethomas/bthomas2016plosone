"""Calculate ECDF from set of data points.

If called as main script:

stdin

    List of floating point numbers, one per line.

stdout

    List of <x,y> pairs representing the ECDF of the input data, one per line.
    x and y are comma-separated.

"""
import sys
import numpy as np
import argparse

def ecdf(values):
    sorted_float_values = sorted(map(float, sorted(values)))
    num_values = len(sorted_float_values)
    return [[x, float(i)/num_values] for i, x in enumerate(sorted_float_values)]

if __name__ == '__main__':
    vals = []
    for line in sys.stdin:
        vals.append(float(line))

    x_y_pairs = ecdf(vals)
    print '\n'.join([','.join(map(str,p)) for p in x_y_pairs])
