"""Calculate how many sessions are active at each timestep.

If called as main script:

stdin

    Set of '\n'-separated lines, where each line is in format <session_start,
    session_end>, i.e. a comma-separated pair of unix timestamp integers.

stdout

    Set of '\n'-separated lines, where each line is in the format <timestamp,
    num_active_sessions>.

"""
import sys
from collections import defaultdict

def sessions_to_active_sessions(sessions):
    """Calculate active sessions at each timestamp.

    Parameters

        sessions: iterable of [start, end] integer pairs.
    
    Returns

        iterable of [time, num_active] integer pairs.

    """
    events = []
    # timestamp -> 'S' or 'E' -> count of event type.
    time_event_type_count = defaultdict(lambda: defaultdict(int))
    timestamps = set()
    for s in sessions:
        timestamps.add(s[0])
        timestamps.add(s[1])
        time_event_type_count[s[0]]['S'] += 1
        time_event_type_count[s[1]]['E'] += 1
    timestamps = sorted(timestamps)
    min_time = timestamps[0]
    time_active_sessions = []
    active_session_count = 0
    for t in timestamps:
        active_session_count += time_event_type_count[t]['S']
        active_session_count -= time_event_type_count[t]['E']
        time_active_sessions.append([t, active_session_count])
    return time_active_sessions

if __name__ == '__main__':
    sessions = []
    for line in sys.stdin:
        sessions.append(map(int, line.strip().split(',')))
    results = sessions_to_active_sessions(sessions)
    print '\n'.join([','.join(map(str, r)) for r in results])
