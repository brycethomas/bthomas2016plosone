"""Select a random encounter event.

If called as main script:

stdin

    A set of comma-separated three tuples of the form <mac1, mac2,
    encounter_start>.

stdout

    A randomly chosen encounter event.

"""
import sys
import argparse
from random import choice
import random

def rand_encounter(encounters):
    """Choose random encounter event.

    Parameters

        encounters : a sequence of three-tuples of the form <mac1, mac2, 
        encounter_start>

    Returns

        A random three-tuple from the input.

    """
    return choice(encounters)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='See module description.')
    parser.add_argument('-s', '--seed', help='A random seed integer', type=int)
    args = parser.parse_args()
    if not args.seed:
        print >> sys.stderr, 'WARNING: selecting random encounter without ' + \
                             'setting seed.'
    else:
        random.seed(args.seed)
    encounters = []
    for line in sys.stdin:
        mac1, mac2, enc_start = line.strip().split(',')
        enc_start = int(enc_start)
        encounters.append([mac1, mac2, enc_start])
    enc = rand_encounter(encounters)
    print ','.join(map(str, enc))
