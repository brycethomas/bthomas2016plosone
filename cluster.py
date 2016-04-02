"""Calculate clustering properties from a set of edges.

If called as main script:

stdin

    Set of lines, each with a comma-separated two-tuple of the form
    <u,v> describing an edge in the graph.

stdout

    The selected metric.  By default, the global clustering coefficient.

Call script with -h option to see other calculated properties available.

"""
import sys
import networkx as nx
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    metric_group = parser.add_mutually_exclusive_group()
    metric_group.add_argument('-c', '--average-clustering',
                              action='store_true',
                              help='Average clustering coefficient.')
    metric_group.add_argument('-d', '--density',
                              action='store_true',
                              help='Graph density.')
    metric_group.add_argument('-t', '--triangles',
                              action='store_true',
                              help='Triangle count.')
    metric_group.add_argument('-s', '--average-square-clustering',
                              action='store_true',
                              help='Average square clustering coefficient.')
    parser.add_argument('-z', '--no-zero', action='store_true',
                        help='Exclude nodes with zero clustering.')
    args = parser.parse_args()

    edges = []
    for line in sys.stdin:
        u,v = line.strip().split(',')
        edges.append((u,v))
        
    g = nx.Graph(edges)
    if args.density:
        result = nx.density(g)
    elif args.triangles:
        triangles = nx.triangles(g)
        result = sum([v for _,v in triangles.iteritems()]) / float(len(triangles))
    elif args.average_square_clustering:
        square_clusters = nx.square_clustering(g)
        result = sum([v for _,v in square_clusters.iteritems()]) / \
        float(len(square_clusters))
    else:
        result = nx.average_clustering(g, count_zeros=not args.no_zero)
    print result
