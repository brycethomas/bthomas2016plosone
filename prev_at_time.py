"""Calculate the prevalence at a supplied time and the standard error.

If called as main script:

stdin

    A list of lines, each of the form <time, prevalence, error> (comma-separated
    three-tuple) or <time, prevalence> (comma-separated two-tuple).  Times
    should be monotonically increasing and prevalence should be monotonically
    non-decreasing.  Error, though technically acceptable as any floating point
    value, should typically represent the standard error of the mean of each
    input measurement.

stdout

    A single line of the form <prevalence, error> (comma-separated two-tuple) or
    <prevalence> (one-tuple).  The returned values are based on linearly
    interpolating between the nearest two points, so e.g. if the prevalence at 1
    day is requested but measurements are only available at 0.9 and 1.1 days,
    then both the returned prevalence and error will be based on linearly
    interpolating between the prevalence and error at 0.9 and 1.1 days.

positional parameters

    time : the time the client would like to know the prevalence at, in seconds.

flags

    --single-sample : should be set if the input data is only two-tuples from a
      single simulation run, where the caller simply wants to know the
      prevalence at a given time.  i.e. the input data is not some pre-averaged
      set of data from multiple simulation trials.

"""
import sys
import argparse
from scipy import interpolate

def prev_at_time(records, time, single_sample=False):
    """Calculate prevalence at supplied time and standard error.

    Parameters

        records : An iterable where each item is itself an iterable of three
        items of the form <time, prevalence, error>.  Times should be
        monotonically increasing and prevalence should be monotonically
        non-decreasing.  Error, though technically acceptable as any floating
        point value, should typically represent the standard error of the mean
        of each input measurement.

        time : An integer time.

    Returns

        An iterable of the form <prevalence, error> that is the prevalence and
        error at the supplied time after linearly interpolating between the
        nearest two points.   That is, both the prevalence and error are
        interpolated based on the prevalence and error of the closest two
        points, one to the left of the specified time and one to the right
        (unless of course the exact supplied time's prevalence is available, in
        which case the exact values can be returned).

    """
    if single_sample is False:
        times, prevs, errors = zip(*records)
    else:
        times, prevs = zip(*records)
    # prev interpolator
    p_t = interpolate.interp1d(times, prevs)
    if single_sample is False:
        # error interpolator
        e_t = interpolate.interp1d(times, errors)
        return [float(p_t(time)), float(e_t(time))]
    else:
        return float(p_t(time))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('time', type=int)
    parser.add_argument('--single-sample', action='store_true')
    args = parser.parse_args()
    records = []
    for line in sys.stdin:
        fields = map(float, line.strip().split(','))
        records.append(fields)
    if args.single_sample is False:
        prev, error = prev_at_time(records, args.time, False)
        print ','.join(map(str, [prev, error]))
    else:
        prev = prev_at_time(records, args.time, True)
        print prev

