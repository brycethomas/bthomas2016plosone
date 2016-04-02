""" Session shuffling algorithms.

Each session shuffling algorithm is implemented as a function with the same
signature.  That is, each algorithm takes as input a set of session records
which is an iterable where each element is a 4-element iterable of the form
<node, start, end, location> describing a session.

Each session shuffling algorithm also returns the same type of data
structure.  That data structure takes exactly the same form as the input
data -- an iterable where each element is a 4-element iterable of the
form <node, start, end, location> that is the product of performing the
relevant shuffling algorithm over the input data.


If called as main script:

stdin

    Comma-separated four-tuples, one tuple per line, of the form <node,
    start, end, location> describing a session.

stdout

    Comma-separated four-tuples, one tuple per line, of the input data
    after performing the selected shuffling algorithm (specified via
    positional parameter)

positional parameters

    A shuffling algorithm acronym.  Call script with -h for available options.

"""

import sys
import random
import argparse
from collections import defaultdict

def tn(sessions):
    """ Shuffle location.

    Correlations retained:

        * Time and Node (TN)

    Correlations destroyed:

        * Time and Location (TL)
        * Location and Node (LN)
    """
    aps = []
    AP_IDX = 3
    for s in sessions:
        aps.append(s[AP_IDX])
    random.shuffle(aps)
    out = []
    for s in sessions:
        out.append([s[0], s[1], s[2], aps.pop()])
    return out


def ln(sessions):
    """ Shuffle times.

    Correlations retained:

        * Location and Node (LN)

    Correlations destroyed:

        * Time and Location (TL)
        * Time and Node (TN)
    """
    time_pairs = []
    START_IDX, END_IDX = 1, 2
    for s in sessions:
        time_pairs.append([s[START_IDX], s[END_IDX]])
    random.shuffle(time_pairs)
    out = []
    for s in sessions:
        new_start, new_end = time_pairs.pop()
        out.append([s[0], new_start, new_end, s[3]])
    return out


def tl(sessions):
    """ Shuffle nodes.

    Correlations retained:

        * Time and Location (TL)

    Correlations destroyed:

        * Location and Node (LN)
        * Time and Node (TN)

    """
    macs = []
    MAC_IDX = 0
    for s in sessions:
        macs.append(s[MAC_IDX])
    random.shuffle(macs)
    out = []
    for s in sessions:
        mac = macs.pop()
        out.append([mac, s[1], s[2], s[3]])
    return out


def tlln(sessions):
    """ Group by location, shuffle time.

    Correlations retained:

        * Time and Location (TL)
        * Location and Node (LN)

    Correlations destroyed:

        * Time and Node (TN)

    """
    # key = ap, value = list of [start, end] two-pairs
    ap_times = defaultdict(list)
    AP_IDX, START_IDX, END_IDX = 3, 1, 2
    for s in sessions:
        ap, start, end = s[AP_IDX], s[START_IDX], s[END_IDX]
        ap_times[ap].append([start, end])
    for k in ap_times.keys():
        times = ap_times[k]
        random.shuffle(times)
        ap_times[k] = times
    out = []
    for s in sessions:
        ap = s[AP_IDX]
        new_start, new_end = ap_times[ap].pop()
        out.append([s[0], new_start, new_end, s[3]])
    return out


def lntn(sessions):
    """ Group by node, shuffle location.

    Correlations retained:

        * Location and Node (LN)
        * Time and Node (TN)

    Correlations destroyed:

        * Time and Location (TL)
    
    """
    mac_aps = defaultdict(list)
    MAC_IDX, AP_IDX = 0,3
    for s in sessions:
        mac, ap = s[MAC_IDX], s[AP_IDX]
        mac_aps[mac].append(ap)
    for k in mac_aps.keys():
        aps = mac_aps[k]
        random.shuffle(aps)
        mac_aps[k] = aps
    out = []
    for s in sessions:
        mac = s[MAC_IDX]
        out.append([s[0], s[1], s[2], mac_aps[mac].pop()])
    return out


def tltn(sessions):
    """ Group by time, shuffle node.

    Correlations retained:

        * Time and Location (TL)
        * Time and Node (TN)

    Correlations destroyed:

        * Location and Node (LN)

    """
    # this will need some figuring out because time will need to be "bucketed"
    # somehow
    raise NotImplementedError('TLTD not implemented yet!')

def destroy_all(sessions):
    """Shuffle by node, shuffle by location.

    Correlations retained:

        * None

    Correlations destroyed:

        * Time and Location (TL)
        * Time and Node (TN)
        * Location and Node (LN)

    """
    nodes, locations = [], []
    NODE_IDX, LOC_IDX = 0, 3
    for s in sessions:
        nodes.append(s[NODE_IDX])
        locations.append(s[LOC_IDX])
    random.shuffle(nodes)
    random.shuffle(locations)
    out = []
    for s in sessions:
        node = nodes.pop()
        location = locations.pop()
        out.append([node, s[1], s[2], location])
    return out


if __name__ == "__main__":
    # configure arguments
    parser = argparse.ArgumentParser(
        description='Also see module-level documentation.')
    parser.add_argument('algorithm', type=str,
                        help="One of the null model abbreviations.")
    parser.add_argument('-s', '--random-seed', type=int, default=1000,
                        help='A random seed for shuffling')
    args = parser.parse_args()
    random.seed(args.random_seed)

    # read sessions from stdin
    sessions = []
    for line in sys.stdin:
        f = line.strip().split(',')
        sessions.append([f[0], int(f[1]), int(f[2]), f[3]])

    # shuffle (or don't if original)
    algorithm = args.algorithm.lower()
    if algorithm == 'original':
        for s in sessions:
            print ','.join(map(str, s))
    else:
        if algorithm == '_':
            algorithm = 'destroy_all'
        thismodule = sys.modules[__name__]
        alg_func = getattr(thismodule, algorithm)
        shuffled = alg_func(sessions)
        for s in shuffled:
            print ','.join(map(str, s))
