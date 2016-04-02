"""Sort a set of .csv records, one record per line. 

stdin:

Example input:

foo,bar,baz
john,kelly,bob

stdout:

Example output corresponding to example input:

bar,baz,foo
bob,john,kelly

"""

import sys
for line in sys.stdin:
    fields = line.strip().split(',')
    print ','.join(sorted(fields))
