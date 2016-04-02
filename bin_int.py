"""Bin a set of integers at the specified boundaries.

If called as main script:

stdin

    A list of integers, one per line.

stdout

    A count of each bin

flags

    Call bin_int.py -h for further details.  Essentially, a minimum of one
    integer must be supplied with either the '-e' or '-g' flag.

    -e 3 -- count number of integers that are exactly 3.

    -e 3 -e 5 -- count number of integers that are exactly 3 and number of
     integers that are exactly 5.

    -e 3 -g 5 -- count number of integers that are exactly 3 and number of
     integers that are greater than 5.


Example input/output when called with "-e 3 -g 5"

    in:

    3
    2
    1
    5
    5
    4
    6
    7

    out:

    3, 1
    5, 2

"""
import sys
import argparse
from collections import defaultdict

def do_counts(values, exacts=None, greaters=None):
    """ Calculate counts.

    Parameters

        values : an iterable of the input data values.

        exacts : the exact integer values to look for.

        greaters : count values exceeding each of these.

    """
    exact_count, greater_count = defaultdict(int), defaultdict(int)
    for v in values:
        if exacts!= None:
            for e in exacts:
                if v == e:
                    exact_count[e] += 1
        if greaters != None:
            for g in greaters:
                if v > g:
                    greater_count[g] += 1
    return exact_count, greater_count


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--exact', action='append', type=int,
                        help='Specific exact integer to look for in the input')
    parser.add_argument('-g', '--greater-than', action='append',
                        type=int, 
                        help='All integers greater than this value')
    parser.add_argument('-l', '--latex', action='store_true',
                        help='Use LaTeX string formatting on output',
                        default=False)
    args = parser.parse_args()
    
    values = []
    for line in sys.stdin:
        value = int(line)
        values.append(value)
        
    exact_count, greater_count = do_counts(values, args.exact, args.greater_than)
    for e, count in exact_count.iteritems():
        print ','.join([str(e), '{:,}'.format(count).replace(',', ' ')])
    for g, count in greater_count.iteritems():
        if not args.latex:
            print ','.join(['> ' + str(g),
                            '{:,}'.format(count).replace(',', ' ')])
        else:
            print ','.join(['$>$ ' + str(g),
                            '{:,}'.format(count).replace(',', ' ')])
