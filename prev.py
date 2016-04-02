"""Calculate prevalence as a function of time under ideal diffusion.

If called as main script:

stdin

    Contact records, one per line of the form
    <node1, node2, contact time> where the 3 values are comma-separated.

stdout

    Prevalence records, one per line of the form <time, prevalence>, again
    comma-separated.

flags

    source : the source node name from which spreading should start.

    start : a timestamp to consider as time "0" i.e. this value will be
    sutracted from all prevalence times.

"""
import sys
import argparse
from operator import itemgetter
from collections import deque

def contacts_to_prevalence_events(contacts, source):
    """Calculate prevalence events from contacts.

    Parameters

        contacts : an iterable where each item is a three-tuple of the
        form <node1, node2, time>.

        source : the name of the source node.

    Returns

        An iterable of two-tuples of the form <timestamp, prevalence>,
        where prevalence is the percentage of all nodes in input
        contacts that are infected (based on ideal diffusion) at the
        given timestamp.
    
    """
    all_nodes = set() # all nodes in the input contacts.
    infected = set()
    infected.add(source)
    contacts = sorted(contacts, key=itemgetter(2)) # sort by start time.
    current_time = None
    contact_pairs_at_current_time = []
    # each item is two-tuple of form [num infections, timestamp].
    infection_count_time = []
    for c in contacts:
        node1, node2, time = c
        if current_time == None:
            current_time = time
        if time != current_time:
            # Calculate whose now infected based on all contacts
            # occurring at the past timestamp.
            infected = now_infected(contact_pairs_at_current_time,
                                    infected)
            infection_count_time.append([current_time, len(infected)])
            contact_pairs_at_current_time = []
            current_time = time
        contact_pairs_at_current_time.append([node1, node2])
        all_nodes.add(node1)
        all_nodes.add(node2)
        
    # do this one last time for the final timestamp.
    infected = now_infected(contact_pairs_at_current_time,
                             infected)
    infection_count_time.append([current_time, len(infected)])

    num_total_nodes = len(all_nodes)
    
    # convert absolute infections to relative to node set size.
    prevs = map(lambda x: [x[0], float(x[1]) / num_total_nodes],
                    infection_count_time)
    return prevs


def now_infected(contact_nodes, currently_infected):
    """Calculate nodes now infected after set of concurrent contacts.

    Parameters

        contact_nodes : iterable of two-tuples of the form <node1,
        node2> describing pairs of encountering nodes.

        currently_infected : set of nodes already infected prior to
        contact_nodes.

    Returns

        Set of all infected nodes after simulating all contacts, assuming
        all contacts occur at the same time.

    """
    # Construct min heap with infected items prioritized so that comparing
    # consecutive elements at single timestamp properly honors transitive
    # infections.
    prioritized_contact_nodes = deque()
    for c in contact_nodes:
        if c[0] in currently_infected or c[1] in currently_infected:
            prioritized_contact_nodes.appendleft(c) # append front of queue.
        else:
            prioritized_contact_nodes.append(c) # append back of queue.

    for c in prioritized_contact_nodes:
        node1, node2 = c
        # xor
        if bool(node1 in currently_infected) != bool(node2 in currently_infected):
            currently_infected.add(node1)
            currently_infected.add(node2)
    return currently_infected


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('start', type=int, help='A unix integer that should ' +\
                        'be considered as time offset 0.')
    parser.add_argument('source', type=str, help='The source node name')
    args = parser.parse_args()
    
    contacts = []
    for line in sys.stdin:
        node1, node2, time = line.strip().split(',')
        time = int(time)
        contacts.append([node1, node2, time])
    res = contacts_to_prevalence_events(contacts, args.source)
    for r in res:
        print ','.join(map(str, [r[0] - args.start, r[1]]))
