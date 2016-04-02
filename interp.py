"""Interpolate between a set of x,y points.

If called as main script:

stdin

    A set of comma-separated x,y pairs, one per line.

stdout

    A set of comma-separated x,y pairs, one per line, that result from
    interpolating between the input points at a linear interval.

flags

    Call the script with -h for more information.

"""
import sys
from scipy import interpolate
import argparse
import numpy as np


def interp(xs, ys, samples=35, kind='linear', domain=None,
           flat_extrapolate=False):
    """Interpolate between a point sequence.

    Parameters

        xs : an n-length sequence of x-values.

        ys : an n-length sequence of y-values matched to xs.

    Returns

        A ``samples``-length set of points interpolated between the min and max
        of the input xs at uniform points.

    """
    x_ys = zip(xs, ys)
    x_ys.sort()
    xs, ys = zip(*x_ys)

    f = interpolate.interp1d(xs, ys, kind=kind)
    min_x, max_x = min(xs), max(xs)
    if domain is None:
        sample_times = np.linspace(min_x, max_x, samples)
    else:
        sample_times = np.linspace(domain/samples * 0.5,
                                   domain - (domain/samples * 0.5),
                                   samples)
    if not flat_extrapolate:
        out_points = [[i, f(i)] for i in sample_times]
    else:
        # y value at earliest and latest x value
        min_x_y = x_ys[0][1]
        max_x_y = x_ys[-1][1]
        out_points = []
        for s in sample_times:
            if s < min_x:
                out_points.append([s, min_x_y])
            elif s > max_x:
                out_points.append([s, max_x_y])
            else:
                out_points.append([s, f(s)])
    return out_points

            
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Interpolate points.')
    parser.add_argument('-k', '--kind',
                        help='Kind of interpolation to use.  Should be a ' + \
                        'string that interpolate.interp1d accepts as the ' + \
                        'kind argument', type=str)
    parser.add_argument('-s', '--samples',
                        help='Number of output samples', type=int)
    # e.g. if -s is 10 and -m is 20, interpolate at
    # x = [  1.,   3.,   5.,   7.,   9.,  11.,  13.,  15.,  17.,  19.]
    parser.add_argument('-d', '--domain', type=float,
                        help='Sample from the domain 0 -- <this value> in ' + \
                        'bucket middles.')
    parser.add_argument('-f', '--flat-extrapolate', action='store_true',
                        help='For points either side of the interpolation ' + \
                        'range just use the closest interpolable value.')
    args = parser.parse_args()
    samples = 35
    kind = 'linear'
    domain = None
    if args.samples:
        samples = args.samples
    if args.kind:
        kind = args.kind
    if args.domain:
        domain = args.domain

    xs, ys = [], []
    for line in sys.stdin:
        x, y = map(float, line.strip().split(','))
        xs.append(x)
        ys.append(y)

    results = interp(xs, ys, samples, kind, domain, args.flat_extrapolate)
    for r in results:
        print ','.join(map(str, r))
