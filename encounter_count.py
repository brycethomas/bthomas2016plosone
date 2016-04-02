"""Tally number of encounters.

If called as main script:

stdin

    List of comma-separated triplets (one per line) of the form <mac1, mac2,
    encounter_start>.

stdout

    List of comma-separated pairs (one per line) of the form <time, # encounters
    so far>.

Notes

    The default tally option is non-unique i.e. total encounters.  Call this
    script with the -h flag to see the options available.

"""
import sys
import argparse
from operator import itemgetter

def tally(encounters,start=None):
    """Simple count of encounters vs. elapsed time.

    Parameters

        encounters : an iterable of encounter three-tuples of the form <mac1,
        mac2, encounter_start>.

        start : if not None, the time to consider as t = 0.

    Returns

        An iterable of two-tuples where each two-tuple is of the form
        <time_elapsed, encounter_total_so_far>.

    """
    # indices
    MAC1, MAC2, START = range(3)
    
    # sort by start time
    encounters = sorted(encounters, key=itemgetter(START))
    if start == None:
        start = encounters[0][START]
    current_time = None
    count = 0
    time_tallys = [] # 2-tuples of <time, tally>
    for e in encounters:
        if current_time == None:
            current_time = e[START]
        if current_time != e[START]:
            time_tallys.append([current_time - start, count])
        count += 1
        current_time = e[START]
    # append last record
    time_tallys.append([current_time - start, count])
    return time_tallys

def unique_tally(encounters, start=None):
    """Count of unique encounter pairs vs. elapsed time.

    Parameters

        encounters : an iterable of encounter three-tuples of the form
        <mac1, mac2, encounter_start>.

        start : if not None, the time to consider as t = 0.

    Returns

        An iterable of two-tuples where each two-tuple is of the form
        <time_elapsed, encounter_total_so_far>.

    """
    # indices
    MAC1, MAC2, START = range(3)
    
    # sort by start time
    encounters = sorted(encounters, key=itemgetter(START))
    if start == None:
        start = encounters[0][START]
    current_time = None
    count = 0
    time_tallys = [] # 2-tuples of <time, tally>
    seen_pairs = set() # each item is a frozenset of encountering mac pairs
    for e in encounters:
        if current_time == None:
            current_time = e[START]
        if current_time != e[START]:
            time_tallys.append([current_time - start, count])
        encounter_pair = frozenset([e[MAC1], e[MAC2]])
        if encounter_pair not in seen_pairs:
            count += 1
            seen_pairs.add(encounter_pair)
        current_time = e[START]
    # append last record
    time_tallys.append([current_time - start, count])
    return time_tallys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Tally number of encounters.')
    parser.add_argument('-s', '--start',
                        help='A unix start time that should be ' +\
                        'treated as time 0.  Default is the ' +\
                        'first encounter start time.', type=int,
                        default=None)
    parser.add_argument('-u', '--unique',
                        help='Count unique encounter pairs only',
                        action='store_true')
    args = parser.parse_args()

    encounters = []
    for line in sys.stdin:
        f = line.strip().split(',')
        encounters.append([f[0], f[1], int(f[2])])
    if args.unique:
        res = unique_tally(encounters, args.start)
    else:
        res = tally(encounters, args.start)
    for r in res:
        print ','.join(map(str, r))
