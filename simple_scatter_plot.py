"""Plot multiple sets of x,y points as a rudimentary scatter plot.

stdin:

Input of the form:

<line_label1>
<x1,y1>
...
<xn,yn>
...
<line_labeln>
<x1,y1>
...
<xn,yn>

Output:

A rudimentary scatter plot of the input data.

"""
import sys
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib import rc
import rc_conf
from pylab import savefig
import argparse
from itertools import cycle
import matplotlib.lines as matplotlib_lines
import matplotlib as mpl

color_set = ['#e41a1c','#377eb8','#4daf4a',
             '#984ea3','#ff7f00','#FFCC00',
             '#a65628','#f781bf','#999999']
color_set = map(lambda x: mpl.colors.ColorConverter().to_rgba(x, alpha=0.1),
    color_set)
marker_set = ['v','^','<',
              '>','o','s',
              'p','d','x']
mpl.rcParams['axes.color_cycle'] = color_set


def scatter(data, labels):
    c_cyc = cycle(color_set)
    m_cyc = cycle(marker_set)
    for lab in labels:
        d = data[lab]
        xs, ys = zip(*d)
        plt_args = {}
        plt_args['markerfacecolor'] = 'none'
        plt_args['alpha'] = 0.1
        plt_args['markeredgecolor'] = next(c_cyc)
        plt_args['marker'] = next(m_cyc)
        plt.plot(xs, ys,label=lab,linestyle='none',**plt_args)
    plt.legend(loc='upper right')
    plt.show()

if __name__ == '__main__':
    labels = []
    label_data = defaultdict(list)
    curr_label = None
    for line in sys.stdin:
        fields = line.strip().split(',')
        if len(fields) == 1:
            curr_label = fields[0]
            labels.append(curr_label)
        else:
            label_data[curr_label].append(map(float, [fields[0], fields[1]]))
    scatter(label_data, labels)
