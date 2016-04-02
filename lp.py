"""Plot multiple sets of x,y points as a rudimentary line plot.

stdin:

Input of the form:

<line_label1>
<x1, y1>
...
<xn, yn>
...
<line_labeln>
<x1, y1>
...
<xn, yn>

Optionally, line labels may be followed by three commas and then
a hex color code if a specific color is desired for a line,
e.g.:

Foo,,,#FFEE00

Output:
A rudimentary line plot of the input data.

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
import os
import time
from datetime import datetime

color_set = ['#e41a1c','#377eb8','#4daf4a',
             '#984ea3','#ff7f00','#FFCC00',
             '#a65628','#f781bf','#999999']
markers = ['v','^','<',
           '>','o','s',
           'p','d','x']
mpl.rcParams['legend.handlelength'] = 0 # just marker, no line in legend

# so time-based plots show up in the local time of the collected trace.
os.environ['TZ'] = 'Australia/Brisbane'
time.tzset()

def main(x_label='', y_label='',
         figname=None, title='', convert_times=False,
         legend_location='lower right', latex=True,
         alpha=1.0, point_size=3,
         min_x=None, max_x=None, min_y=None, max_y=None,
         log_x=None, mark_every=15, steps=False, day_of_week=False,
         no_color=False):
    if latex:
        rc_conf.apply_conf(rc)
    label = None
    label_data = defaultdict(list)
    labels = [] # keep ordered labels so can plot in order later.
    line_colors = []
    line_markers = []
    m_cycler = cycle(markers)
    color_cycler = cycle(color_set)
    
    for line in sys.stdin.readlines():
        fields = line.strip().split(',')
        if len(fields) in set([1,4,5]):
            label = fields[0]
            labels.append(label)
            if len(fields) in set([4,5]):
                color = fields[3]
                line_colors.append(color)
            if len(fields) == 5:
                marker = fields[4]
                line_markers.append(marker)
        else:
            label_data[label].append([float(fields[0]), float(fields[1])])

    for i, label in enumerate(labels):
        data = label_data[label]
        xs, ys = zip(*data)
        if convert_times:
            xs = [float(time)/60.0/60.0/24.0 for time in xs]
        elif day_of_week:
            xs = [datetime.fromtimestamp(a) for a in xs]
            dayNameFmt = mdates.DateFormatter('%a')
            plt.gca().xaxis.set_major_formatter(dayNameFmt)
        
        plot_args = {}
        plot_args['label'] = label
        plot_args['alpha'] = alpha
        plot_args['linewidth'] = 1.25
        plot_args['markersize'] = point_size
        plot_args['markerfacecolor'] = 'none'
        plot_args['markevery'] = mark_every

        if no_color is True:
            plot_args['color'] = 'black'
            plot_args['markeredgecolor'] = 'black'
        elif len(line_colors) > 0:
            plot_args['color'] = line_colors[i]
            plot_args['markeredgecolor'] = line_colors[i]
        else:
            col = next(color_cycler)
            plot_args['color'] = col
            plot_args['markeredgecolor'] = col
            
        if len(line_markers) > 0:
            plot_args['marker'] = line_markers[i]
        else:
            plot_args['marker'] = next(m_cycler)
            
        if steps:
            plot_args['drawstyle'] = 'steps'

        plt.plot(xs, ys, **plot_args)
        if log_x:
            plt.xscale('log')

    if legend_location != 'none':
        plt.legend(loc=legend_location, numpoints=1)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    if min_x is not None:
        plt.xlim(min_x, plt.xlim()[1])
    if max_x is not None:
        plt.xlim(plt.xlim()[0], max_x)
    if min_y is not None:
        plt.ylim(min_y, plt.ylim()[1])
    if max_y is not None:
        plt.ylim(plt.ylim()[0], max_y)
    
    if figname == None:
        plt.show()
    else:
        savefig(figname, bbox_inches='tight', pad_inches=0.0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='A simple x/y line plotter.')
    parser.add_argument('-a', '--alpha', type=float, default=1.0,
                        help='Plot point alpha.  0.0 <= a <= 1.0')
    parser.add_argument('-c', '--convert-timestamps',
                        help='Convert x values from seconds to durations.',
                        action='store_true')
    parser.add_argument('-l', '--legend-location', type=str,
                        default='lower right',
                        help='Standard matplotlib legend location.')
    parser.add_argument('--min-x', type=float, default=None,
                        help='The minimum value of the x-axis.')
    parser.add_argument('--max-x', type=float, default=None,
                        help='The maximum value of the x-axis.')
    parser.add_argument('--min-y', type=float, default=None,
                        help='The minimum value of the y-axis.')
    parser.add_argument('--max-y', type=float, default=None,
                        help='The maximum value of the y-axis.')
    parser.add_argument('-n', '--no-latex', action='store_true',
                        help='Do not use LaTeX text formatting')
    parser.add_argument('--point-size', type=int, default=6,
                        help='The size of individual plot points.')
    parser.add_argument('-s', '--save-figure', type=str, default=None,
                        help='A filename for the figure.')
    parser.add_argument('-t', '--title', type=str, default='',
                        help='A title for the plot.')
    parser.add_argument('-x', '--x-label', type=str, default='',
                        help='Independent variable label.')
    parser.add_argument('-y', '--y-label', type=str, default='',
                        help='Dependent variable label.')
    parser.add_argument('--log-x', action='store_true',
                        help='Make x-axis logarithmic.')
    parser.add_argument('--mark-every', type=int, default=15,
                        help='Place a marker every n points.')
    parser.add_argument('--steps', action='store_true',
                        help='Plot as steps between points.')
    parser.add_argument('--day-of-week', action='store_true',
                        help='Plot x-axis values as day of week names.')
    parser.add_argument('--no-color', action='store_true',
                        help='Do not use color in plot lines.')
    args = parser.parse_args()

    main(args.x_label, args.y_label, args.save_figure, args.title,
         args.convert_timestamps, args.legend_location, not args.no_latex,
         alpha=args.alpha, point_size=args.point_size, min_x=args.min_x,
         max_x=args.max_x, min_y=args.min_y, max_y=args.max_y, log_x=args.log_x,
         mark_every=args.mark_every, steps=args.steps,
         day_of_week=args.day_of_week, no_color=args.no_color)
