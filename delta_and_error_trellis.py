"""Plot delta between variable pairs with error bars in trellis configuration.

If called as main script:

stdin

    A set of lines where each line has either 1 or 3 fields.  If one field, it
    is the start of a new variable's records.  If it is three fields, it is a
    record of  the form <x, y, error> belonging to the last read variable name.
    Fields are comma separated.

output

    A plot of the data in a trellis configuration.

Example input:

    Var1
    1,0.5,0.02
    2,0.6,0.03
    Var2
    1,0.55,0.03
    2,0.62,0.04

Each variable must have the same number of records at the same x-values.

"""
import sys
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib import rc
from pylab import savefig
import rc_conf
import numpy as np
import argparse

rc_conf.apply_conf(rc)


def trellis_from_data(var_data, var_order, x_title='x title???',
                      y_title='y title???', filename=None, y_abs_limit=None):
    """Plot the trellis from the input data.

    Parameters

        var_data : a dictionary with n keys,  keyed by variable name
        where each value is a list of data items each in the form <x, y,
        error>.

        var_order : a list of n keys which should match those found in
        var_data.  The ordering in this list determines the order in which the
        subplots are generated.

    """
    nrow, ncol = len(var_order), len(var_order)
    fig, axes = plt.subplots(nrow, ncol, sharey=True, sharex=True, figsize=(7,8))
    # make subplots touch
    plt.subplots_adjust(wspace = .00, hspace = .00)

    fig.suptitle(x_title)
    fig.text(0.06, 0.5, y_title, ha='center', va='center', rotation='vertical')
    
    for i in range(nrow):
        for j in range(ncol):
            xs = axes[i,j]
            plt.setp(xs.get_xticklabels(), visible=False)
            plt.setp(xs.get_yticklabels(), visible=False)
            if i == 0:
                xs.set_xlabel(var_order[j])
                xs.xaxis.set_label_position('top')
            if j == 0:
                xs.set_ylabel(var_order[i])
            
            xs.xaxis.set_ticks_position('none')
            xs.yaxis.set_ticks_position('none')
            if i == j:
                xs.set_axis_bgcolor('lightgray')
            
            first_data = var_data[var_order[j]]
            second_data = var_data[var_order[i]]

            xvals = zip(*first_data)[0]
            xvals2 = zip(*second_data)[0]
            assert xvals == xvals2, 'Two datasets with different x values!'

            indep_errs = zip(*first_data)[2]
            dep_errs = zip(*second_data)[2]
            indep_ys = zip(*first_data)[1]
            dep_ys = zip(*second_data)[1]
            deltas = np.subtract(dep_ys, indep_ys)

            xs.fill_between(xvals, indep_errs,
                [-e for e in indep_errs], facecolor='gray', alpha=0.5)
            xs.axhline(y=0.0,color='blue', linestyle=':',linewidth=2.0)
            xs.plot(xvals, deltas,marker=None, color='black')
            xs.fill_between(xvals, deltas+dep_errs, deltas-dep_errs, facecolor='gray',
            alpha=0.5)
            if y_abs_limit is not None:
                xs.set_ylim([-y_abs_limit,y_abs_limit])


    if filename is None:
        plt.show()
    else:
        savefig(filename, bbox_inches='tight', pad_inches=0.0)
    

if __name__ == '__main__':
    # key = variable name, data = list of 3-item iterables of the form <x, y,
    # error> 
    var_data = defaultdict(list)
    var_order = []
    current_var = None
    for line in sys.stdin:
        fields = line.strip().split(',')
        if len(fields) == 1:
            current_var = fields[0]
            var_order.append(current_var)
        else:
            var_data[current_var].append(map(float, fields))

    parser = argparse.ArgumentParser(
        description='Plot delta between variable pairs and error margin.')
    parser.add_argument('--x-title', type=str,
                        help='The main x-title to use for the plot.',
                        default='You need an x title')
    parser.add_argument('--y-title', type=str,
                        help='The main y-title to use for the plot.',
                        default='You need a y title')
    parser.add_argument('-s', '--save-figure',
                        help='A filename for the figure',
                        default = None)
    parser.add_argument('--y-abs-limit', type=float, default=None,
                        help='The absolute limit of the y-axis.  E.g. if ' +\
                        '0.015 is given, then the y-axis will span ' + \
                        '[-0.015, 0.015]')
    args = parser.parse_args()
    trellis_from_data(var_data, var_order, args.x_title, args.y_title,
                      args.save_figure, args.y_abs_limit)
