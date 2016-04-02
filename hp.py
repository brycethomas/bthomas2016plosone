"""Plot multiple sets of points as a sequence of histogram subplots.

If called as main script:

stdin

    Input of the form:

    <histogram_label1>
    val1
    ...
    valn
    <histogram_label2>
    val1
    ...
    valn

    Where values are raw values from which to produce each histogram. 

"""
import sys
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib import rc
import matplotlib.dates as mdates
import rc_conf
from pylab import savefig
import argparse
from itertools import cycle
import matplotlib as mpl

color_set = ['#e41a1c','#377eb8','#4daf4a',
             '#984ea3','#ff7f00','#FFCC00',
             '#a65628','#f781bf','#999999']
markers = ['v','^','<',
           '>','o','s',
           'p','d','x']
mpl.rcParams['legend.handlelength'] = 0 # just marker, no line in legend

def make_histograms(data, ordered_labels, bins=20,
                    x_label='I need an x label', y_label='I need a y label',
                    figname=None):
    """Produce the histograms.

    """
    rc_conf.apply_conf(rc)
    color_cycler = cycle(color_set)

    # maximum range of values for any given histogram
    max_range = max([max(a) - min(a) for a in data.values()])

    nrow = len(data.keys())
    ncol = 1
    fig, axes = plt.subplots(nrow, ncol, sharey=True, sharex=True)

    for i, label in enumerate(ordered_labels):
        xs = axes[i]
        xs.spines['right'].set_linewidth(0.5)
        xs.spines['top'].set_linewidth(0.5)
        xs.spines['left'].set_linewidth(0.5)
        xs.spines['bottom'].set_linewidth(0.5)
        plot_args = {}
        plot_args['color'] = next(color_cycler)
        plot_args['bins'] = bins

        this_min_val = min(data[label]) # minimum value for this histogram
        # force range of each histogram to be the same width, so that for n bins,
        # each histogram has same bin width.  NB. this doesn't mean each
        # histogram's bins start and end at the same absolute values.
        xs.hist(data[label], range=[this_min_val, this_min_val + max_range], edgecolor='none',
                 **plot_args)
        xs.text(x=0.98, y=0.96, s=label, ha='right', va='top', transform=xs.transAxes)

    plt.xlabel(x_label)
    #plt.ylabel(y_label) # Wrong positioning for whatever reason.
    fig.text(0.06, 0.5, y_label, ha='center', rotation='vertical')
    if figname == None:
        plt.show()
    else:
        fig.set_size_inches(8,10)
        fig.savefig(figname, bbox_inches='tight', pad_inches=0.0)

def is_float(value):
    try:
        i = float(value)
        return True
    except ValueError:
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='See module level comments.')
    parser.add_argument('-b', '--bins', type=int, default=20,
                        help='Number of bins.')
    parser.add_argument('-x', '--x-label', type=str, default='Needs an x-label',
                        help='Independent variable label.')
    parser.add_argument('-y', '--y-label', type=str, default='Needs a y-label',
                        help='Dependent variable label.')
    parser.add_argument('-s', '--save-figure', type=str, default=None,
                        help='A filename for the figure.')
    args = parser.parse_args()
    
    data = defaultdict(list) # label --> list of raw values
    ordered_labels = []
    current_label = None
    for line in sys.stdin:
        fields = line.strip().split(',')
        assert len(fields) == 1, 'Expected 1 field, instead got {} ' + \
                             'fields!'.format(len(fields))
        value = fields[0]
        if is_float(value):
            data[current_label].append(float(value))
        else:
            current_label = value
            ordered_labels.append(current_label)
    make_histograms(data, ordered_labels, args.bins, args.x_label,
                    args.y_label, args.save_figure)
