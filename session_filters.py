"""Session filtering helpers.

If called as main script:

stdin 

    List of lines, where each line is a 4-tuple of comma-separated values of the
    form <mac, session start, session end, ap>.

stdout

    The input data filtered in a manner which depends on the script flags.

flags

    Call script with -h for available flags.

"""
import sys
import argparse

def filter_by_start(sessions, start):
    """Filter sessions to those after start time.

    Parameters

        sessions : a list of session four-tuples of the form <mac, start,
        end, AP>.

        start : the start time that sessions earlier than this should be
        filtered by.

    """
    res = []
    for s in sessions:
        if s[2] >= start:
            res.append(s)
    # ltrim session starts to begin at earliest when diffusion starts
    for r in res:
        r[1] = max(r[1], start)
    return res


def filter_by_macs(sessions, macs):
    """Filter sessions to those by macs in the macs argument.

    Parameters

        sessions : an iterable of session four-tuples of the form <mac,
        start, end, AP>.

        macs : a set of MACs whose sessions should be retained in the
        output.  MACs must support the Python "in" operator (a regular
        Python set is an easy choice).

    """
    res = []
    for s in sessions:
        if s[0] in macs:
            res.append(s)
    return res


def main(start):
    sessions = []
    for line in sys.stdin.readlines():
        # fields
        f = line.strip().split(',')
        sessions.append([f[0], int(f[1]), int(f[2]), f[3]])
    new_sessions = filter_by_start(sessions, start)
    for s in new_sessions:
        print ','.join(map(str, s))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Filter sessions.')
    parser.add_argument('-s', '--start',
                        help='Filter sessions to those after ' +\
                        'supplied unix start time.  Straddling ' +\
                        'sessions are ltrimed to start at ' +\
                        'the supplied start time.',
                        type=int,
                        required=True)
    args = parser.parse_args()
    main(args.start)
