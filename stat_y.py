"""A utility for calculating summary statistics about the y values in an x/y
dataset.  For example, calculating the average y-value at each x or the standard
error of the mean at each x.

If called as main script:

stdin

    A set of lines of the form <x,y> (i.e. two comma-separated numeric values
    per line)

stdout

    A set of lines of the form <x, y-stat1, ..., y-statN>.  i.e. comma-separated
    values on each line, where x always comes first, followed by one of more
    summary statistics depending on the flags passed to the script.

"""
import sys
import numpy as np
import math
from collections import defaultdict
import argparse

def sem(x_ys):
    """Calculate the standard error of the mean.

    Parameters

        x_ys : a dictionary keyed by x-value where each value is a list of
        y-values at the x-value key.

    Returns

        A list where each item is a two-tuple of the form <x-value, standard
        error of mean over all y-values at x>.

    """
    results = []
    for x, ys in x_ys.iteritems():
        results.append([x, np.std(ys)/math.sqrt(float(len(ys)))])
    return results

def avg(x_ys):
    """Calculate the average.

    Parameters

        x_ys : a dictionary keyed by x-value where each value is a list of
        y-values at the x-value key

    Returns

        A list where each item is a two-tuple of the form <x-value, average over
        all y-values at x>.

    """
    results = []
    for x, ys, in x_ys.iteritems():
        results.append([x, sum(ys)/float(len(ys))])
    return results


if __name__ == '__main__':
    xs, ys = [], []
    for line in sys.stdin:
        x, y = map(float, line.strip().split(','))
        xs.append(x), ys.append(y)
    x_ys = defaultdict(list) # key = x, value = y-values at x
    for x, y in zip(xs, ys):
        x_ys[x].append(y)
    if len(set([len(v) for v in x_ys.values()])) > 1:
        print >> sys.stderr, 'WARNING: some x-values have more associated' + \
        'y-values than others'
        
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--stat', action='append', type=str,
                        help='A stat name from the set ("avg", "sem")')
    args = parser.parse_args()
    assert len(args.stat) > 0, 'Need at least one stat'

    # there is one element per selected summary stat in y_summaries.  Each
    # element holds the results for that summary.  After all summary stats are
    # generated, y_summaries are merged on x-values to produce the output lines
    y_summaries = []
    for stat in args.stat:
        if stat == "avg":
            avg_summary = avg(x_ys)
            y_summaries.append(avg_summary)
        elif stat == "sem":
            sem_summary = sem(x_ys)
            y_summaries.append(sem_summary)
        else:
            print >> sys.stderr, 'Unrecognized stat', stat
            sys.exit(1)
    # merge y-summaries on x-values.
    output_summaries = defaultdict(list) # key = x, value = y summaries at x
    for summary in y_summaries:
        for x,y in summary:
            output_summaries[x].append(y)
    # output_summaries now a list
    output_summaries = sorted([(k,v) for k,v in output_summaries.iteritems()])
    for x, ys in output_summaries:
        print ','.join(map(str, [x] + ys))
