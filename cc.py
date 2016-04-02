"""Utils for finding contact network components.


If called as main script:

stdin

    A set of lines where each line is at minimum a two-tuple of the form
    <mac_1, mac_2>, i.e. a pair of macs representing a contact.  Lines may
    contain other auxillary information such as the contact start time as the
    3rd through nth comma separated field.  For calculating the LCC these fields
    will be ignored but will be included in the output results making it easy
    for the caller to filter more complete contact records.

stdout

    Same as the input dataset, but only including contacts that are in the
    largest connected component.  i.e. contacts not in the greatest connected
    component are dropped from the input.

"""
import sys
from collections import defaultdict

def lcc(contacts):
    """Calculate largest connection component (LCC).

    Parameters

        contacts -- an iterable where each item is a two-tuple of the
        form <mac1, mac2>.

    Returns

        A set of macs that are part of the LCC.

    """
    def dfs(graph, start):
        visited, stack = set(), [start]
        while stack:
            vertex = stack.pop()
            if vertex not in visited:
                visited.add(vertex)
                stack.extend(graph[vertex] - visited)
        return visited
    
    all_nodes = set()
    adj = defaultdict(set)
    for node1, node2 in contacts:
        adj[node1].add(node2)
        adj[node2].add(node1)
        all_nodes.add(node1)
        all_nodes.add(node2)
    num_nodes = len(all_nodes)
    comps = []
    while len(adj.keys()) > 0:
        # any start will do
        start = next(iter(adj[adj.keys()[0]]))
        comp = dfs(adj, start)
        if len(comp)/float(num_nodes) > 0.5:
            # shortcut if component is larger than half network size
            return comp
        else:
            for n in comp:
                # adjacency list nodes for all vertices in comp cannot be in
                # any other component.
                del adj[n]
            comps.append(comp)
    # component with most nodes
    return sorted(comps, key=lambda x: len(x), reverse=True)[0]
        
    

if __name__ == '__main__':
    encounters = []
    for line in sys.stdin:
        fields = line.strip().split(',')
        mac1, mac2, rest = fields[0], fields[1], fields[2:]
        record = [mac1, mac2] + rest
        encounters.append(record)
    in_lcc = lcc([[r[0],r[1]] for r in encounters])
    # filter contact events to only those in LCC.
    encounters = filter(lambda x: x[0] in in_lcc, encounters)
    for record in encounters:
        print ','.join(record)
