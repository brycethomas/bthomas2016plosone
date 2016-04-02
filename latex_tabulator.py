"""Make simple LaTeX table out of simple dataset.

If called as main script:

stdin

    A list of comma-separated values, one set per line that should be construed
    as a row of data in the output table.  i.e. n values on each of m lines
    means n columns in the output over n data rows.

stdout

    A LaTeX table that can be inserted into a LaTeX document.

flags

    Call script with -h option for full information.

"""
import sys
import argparse

def build_table(headings, data, caption='',label=''):
    """Build LaTeX table from input data and settings.

    Parameters

        headings : a sequence of table headings.

        data : a sequence of sequences where each element is a row of data to
        output in the table.

        caption : the string to use as the LaTeX table caption.

        label : the string to use as the LaTeX table label.

    Returns

        A LaTeX table that can inserted in a LaTeX document.

    """
    preamble = []
    preamble.append(r'\begin{table}[!t]')
    preamble.append(r'\caption{' + caption + r'}')
    preamble.append(r'\label{' + label + r'}')
    preamble.append(r'\centering')
    preamble.append(r'\begin{tabular}{' + ' '.join('r' *
                    len(headings)) +
                    '}')

    heading = []
    heading.append(r'\hline')
    heading.append(r' & '.join(headings) + r'\\')
    heading.append(r'\hline')

    body = []
    for d in data:
        body.append(r' & '.join(d) + r'\\')

    postamble = []
    postamble.append(r'\hline')
    postamble.append(r'\end{tabular}')
    postamble.append(r'\end{table}')

    table = ''
    table += '\n'.join(preamble) + '\n'
    table += '\n'.join(heading) + '\n'
    table += '\n'.join(body) + '\n'
    table += '\n'.join(postamble)

    return table
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--table-heading', action='append', type=str,
                        help='A heading')
    parser.add_argument('-c', '--caption', type=str, 
                        help='Table caption')
    parser.add_argument('-l', '--label', type=str,
                        help='Table label')

    args = parser.parse_args()
    assert len(args.table_heading) > 0, 'Need at least one heading'
    caption, label = '', ''
    if args.caption:
        caption = args.caption
    if args.label:
        label = args.label

    data = []
    for line in sys.stdin:
        data.append(line.strip().split(','))
    table = build_table(args.table_heading, data, caption, label)
    print table
