"""Tabulate repeat encounters between MAC pairs.

Can either be used as main script or as a module import.  

If called as main script:

stdin

    A set of lines separated by '\n's, where each line has two MACs
    separated by a comma.

stdout

    A set of lines separated by '\n's, where each line is in the form
    <mac1, mac2, repeat encounters>.

Exampline stdin:

AAA,BBB
BBB,AAA
CCC,EEE
FFF,CCC

Example stdout:

AAA,BBB,2
CCC,EEE,1
FFF,CCC,1

"""
from collections import defaultdict
import sys

def repeat_encounter_count(encounters):
    """
    Arguments:

    encounters : encounter iterable where each element is a 2-tuple
    of the form <MAC_1, MAC_2>.

    Returns:

    A list of 3-tuples of the form <MAC_1, MAC_2, repeat encounters>.
    Note that the order of MACs is unimportant and so there should never
    be two returned values in the list where the second is simply the
    transposition of MAC_1 and MAC_2.

    """
    # two item mac set -> number of times encountered
    macpair_encounters = defaultdict(int)
    for (mac1, mac2) in encounters:
        macpair_encounters[frozenset([mac1, mac2])] += 1
    return macpair_encounters


def main():
    encounters = []
    for line in sys.stdin:
        mac1, mac2 = line.strip().split(',')
        encounters.append([mac1, mac2])
    repeats = repeat_encounter_count(encounters)
    for macpair, repeats in repeats.iteritems():
        mac1, mac2 = list(macpair)
        print ','.join(map(str, (mac1, mac2, repeats)))
        

if __name__ == "__main__":
    main()
