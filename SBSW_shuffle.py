"""DCWB, DCB, DCW, D contact shuffling.

Each contact shuffling algorithm is implemented as a function with the same
signature.  That is, each algorithm takes as input a set of contact records
which is an iterable where each element is a 3-element iterable of the form
<node_1, node_2, start> describing a contact.

Each contact shuffling algorithm also returns the same type of data structure.
That data structure takes exactly the same form as the input data -- an iterable
where each element is a 3-element iterable of the form <node_1, node_2, start>
that is the product of performing the relevant shuffling algorithm over the
input data.


If called as main script:

stdin

    Comma-separated 3-tuples, one tuple per line, of the form <node_1, node_2,
    start> describing a contact event.

stdout

    Comma-separated 3-tuples, one tuple per line, of the input data after
    performing the selected shuffling algorithm (specified via positional
    parameter)

positional parameters

    A shuffling algorithm acronym from the set ["Original", "DCWB", "DCB",
    "DCW", "D"].

DCWB, DCB, DCW and D shuffling of encounters as described in "Slow But Small
World: How Network Topology and Burstiness Slow Down
Spreading". http://www.barabasilab.com/pubs/CCNR-ALB_Publications/201102-18_PhysRevE-Smallbut/201102-18_PhysRevE-Smallbut.pdf

"""
import sys
from collections import defaultdict
import random
random.seed(1000)
import argparse


def dcwb(encounters):
    """ DCWB shuffle of encounters.

    """
    # two item mac set -> list of encounter start times
    macpair_start = defaultdict(list)
    for enc in encounters:
        mac_1, mac_2, start = enc
        if mac_1 > mac_2:
            key = ','.join([mac_1,mac_2])
        else:
            key = ','.join([mac_2,mac_1])
        macpair_start[key].append(start)

    # num repeats -> mac pair -> encounter start times
    rms = defaultdict(dict)
    for macpair, starts in macpair_start.iteritems():
        rms[len(starts)][macpair] = starts

    results = []
    for repeats, macpair_starts in rms.iteritems():
        keys = macpair_starts.keys()
        random.shuffle(keys)
        for (k,v) in zip(keys, macpair_starts.values()):
            mac1, mac2 = k.split(',')
            for start in v:
                results.append([mac1, mac2, start])

    return results


def dcb(encounters):
    """ DCB shuffle of encounters.

    """
    # two item mac set -> list of encounter start times
    macpair_start = defaultdict(list)
    for enc in encounters:
        mac_1, mac_2, start = enc
        macpair_start[frozenset([mac_1, mac_2])].append(start)
    # shuffle dict's key/values
    keys = macpair_start.keys()
    random.shuffle(keys)
    shuf = dict(zip(keys, macpair_start.values()))

    results = []
    for macpair, starts in shuf.iteritems():
        for start in starts:
            mac1, mac2 = list(macpair)
            results.append([mac1, mac2, start])
    return results


def dcw(encounters):
    """ DCW shuffle of encounters.

    """
    # a two item mac set -> list of encounter start times
    macpair_start = defaultdict(list)
    # a list of all start times
    all_starts = []
    for enc in encounters:
        mac_1, mac_2, start = enc
        macpair_start[frozenset([mac_1, mac_2])].append(start)
        all_starts.append(start)
    random.shuffle(all_starts)
    # apply shuffled start times
    sms = defaultdict(list)
    for macpair, starts in macpair_start.iteritems():
        for i in range(len(starts)):
            rand_start = all_starts.pop()
            sms[macpair].append(rand_start)

    results = []
    for macpair, starts in sms.iteritems():
        for start in starts:
            mac1, mac2 = list(macpair)
            results.append([mac1, mac2, start])
    return results


def d(encounters):
    """ D shuffle of encounters.

    Notes:

    See
    http://tuvalu.santafe.edu/~aaronc/courses/5352/fall2013/csci5352_2013_L11.pdf
    for a good description of the configuration model (D) shuffling
    algorithm.

    """
    # a two item mac set -> list of encounter start times
    macpair_start = defaultdict(list)
    # a list of all start times
    all_starts = []
    # mac -> set of encountered macs
    mac_encounters = defaultdict(set)
    for enc in encounters:
        mac1, mac2, start = enc
        macpair_start[frozenset([mac1, mac2])].append(start)
        all_starts.append(start)
        mac_encounters[mac1].add(mac2)
        mac_encounters[mac2].add(mac1)

    pairing_list = []
    # add each mac k times to pairing_list, where k is the mac's degree
    for mac, other_macs in mac_encounters.iteritems():
        pairing_list.extend([mac for k in range(len(other_macs))])
    # each item is the number of repeat encounters between one pair of macs
    repeat_counts = []
    for macpair, starts in macpair_start.iteritems():
        repeat_counts.append(len(starts))
        
    random.shuffle(pairing_list)
    random.shuffle(all_starts)
    random.shuffle(repeat_counts)

    shuffled = []
    for repeats in repeat_counts:
        mac1, mac2 = pairing_list.pop(), pairing_list.pop()
        starts = []
        for i in range(repeats):
            shuffled.append([mac1, mac2, all_starts.pop()])

    # should have popped all records by now
    assert(len(pairing_list) == 0)
    assert(len(all_starts) == 0)

    return shuffled


def main(method):
    # read in original encounters
    original_encounters = []
    for line in sys.stdin.readlines():
        mac1, mac2, start = line.strip().split(',')
        start = int(start)
        original_encounters.append([mac1, mac2, start])

    # If "Original", don't actually shuffle at all - return the
    # original input.
    if method.lower() == 'original':
        for enc in original_encounters:
            print ','.join(map(str, enc))
        return
    
    # translate string method to function to call
    thismodule = sys.modules[__name__]
    shuf_func = getattr(thismodule, method.lower())

    # shuffle and emit
    shuffled_encounters = shuf_func(original_encounters)
    for enc in shuffled_encounters:
        print ','.join(map(str, enc))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Perform A shuffling from Small But Slow Worlds.')
    parser.add_argument('method',
                        type=str,
                        help='The shuffling acronym to perform.')
    args = parser.parse_args()
    main(args.method)
