"""Average the set of y-values after grouping by x-value.

If called as main script:

stdin

    Comma-separated pairs, one per line of <x,y> values.

stdout

    Comma-separated triplets, one perline of <x,y,count> values.  y is the
    average y-value over all input records with an x-value of x.  count is the
    number of y-value observations from which the average was derived.

Notes

    By default, the script considers it to be an error for there to be more of
    one x-value than another x-value.  i.e. unless the counts are the same for
    all rows in the stdout, the script fails.

"""
import sys
from collections import defaultdict
from operator import itemgetter

def avg_y(xs, ys):
    """Average y-values for each x-value.

    Parameters

        xs : n-length iterable of numeric x-values.

        ys : n-length iterable of numeric y-values matched with the x-values.

    Returns

        The average y-value for each unique x-value.

    """
    x_ys = defaultdict(list)
    for x,y in zip(xs, ys):
        x_ys[x].append(y)
    x_ys_list = sorted([(k,v) for k,v in x_ys.iteritems()],
                   key=itemgetter(0))
    results = []
    old_count = len(x_ys_list[0][1]) if len(x_ys_list) > 0 else None
    for x, ys in x_ys_list:
        if len(ys) != old_count:
            print >> sys.stderr, 'different x-vals with different y-counts!', \
            'x: ', x, 'ys: ', ys, 'old count:', old_count, 'new count:', len(ys)
            sys.exit(1)
        results.append([str(x), str(float(sum(ys))/len(ys)), str(len(ys))])
    return results

    
if __name__ == "__main__":
    xs, ys = [], []
    for line in sys.stdin:
        try:
            x,y = map(float, line.strip().split(','))
        except:
            print >> sys.stderr, line.strip(), 'is not all numeric'
            raise
        xs.append(x)
        ys.append(y)
    results = avg_y(xs, ys)
    for r in results:
        print ','.join(map(str,r))
        
