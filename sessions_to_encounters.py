"""Convert sessions to encounters.

If called as main script:

stdin

    A set of comma-separated value lines describing sessions , each of the form
    <node, start, end, location>.

stdout

    A set of comma-separated value lines describing contact events, each of the
    form <node_1, node_2, start, end, location>.

"""

import sys
from collections import defaultdict

def sessions_to_encounters(sessions, start_time=None):
    """Return a set of encounters from a set of sessions.
    
    Parameters

        sessions : a list of 4-tuples of the form <node, start, end, location>,
        describing the times at which individual nodes were present at individual
        locations.

        start_time : if specified, only returns contacts that have
        occurred after the designated start time.  Contacts which
        straddle the designated start time are ltrimmed to commence at the
        designated start time.
    
    Returns

        A list of 5-tuples of the form <node_1, node_2, start, end, location>,
        describing the intervals during which two connected devices encountered.

    """
    # sort by start_time - prereq for implemented  encounter algorithm.
    sessions.sort(key = lambda x: x[1])
    candidate_encounters = defaultdict(list)
    encounters = []
    for sess in sessions:
        ap = sess[3]
        # only sessions with end time > this sess start time remain
        # candidates
        candidate_encounters[ap] = [x for x in \
        candidate_encounters[ap] if x[2] > sess[1]]
        
        # Sessions with end time < start time already filtered.
        # Any remaining sessions in candidate_encounters[ap]
        # are for the same AP and started prior to or at the
        # same time as this session by virtue of sessions being
        # sorted by start time.  Therefore all remaining sessions
        # in candidate_encounters AP started before this session
        # started and ended after this session started, implying
        # an encounter.
        for enc in candidate_encounters[ap]:
            enc_start = max(sess[1], enc[1])
            enc_end = min(sess[2], enc[2])
            mac_1 = sess[0]
            mac_2 = enc[0]
            #assert mac_1 != mac_2, 'Mac should not encounter itself'
            # have to check this, as with e.g. optimistic session adjustments
            # a MAC's sessions can overlap in time even at the same AP.
            if mac_1 != mac_2:
                encounters.append([mac_1, mac_2, enc_start, enc_end, ap])
        
        candidate_encounters[ap].append(sess) 
    # if no start_time has been designated, return now. otherwise,
    # discard encounters before start time and ltrim those which
    # straddle it.
    if not start_time:   
        return encounters
    else:
        # encounter must end after designated start time
        encounters = [enc for enc in encounters if enc[3] > start_time]
        # ltrim encounters if necessary
        new_encounters = []
        for enc in encounters:
            if enc[2] < start_time:
                new_encounters.append([enc[0],enc[1],start_time,enc[3],enc[4]])
            else:
                new_encounters.append(enc)
        return new_encounters


if __name__ == "__main__":
    sessions = []
    for line in sys.stdin:
        # fields
        f = line.strip().split(',')
        sessions.append([f[0], int(f[1]), int(f[2]), f[3]])
    encounters = sessions_to_encounters(sessions)
    for e in encounters:
        print ','.join(map(str, e))
