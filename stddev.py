"""Calculate standard deviation of floats read from stdin

If called as main script:

stdin

    A list of numbers, one per line.

stdout

    The standard deviation of the input numbers.

"""
import sys
import numpy as np

def stddev(numbers):
    """Calculate standard deviation of some numbers.

    Parameters

        numbers: an interable of numeric values.

    Returns

        The standard deviation of ``numbers``.

    """
    return np.std(numbers)


if __name__ == '__main__':
    numbers = []
    for line in sys.stdin:
        numbers.append(float(line.strip()))
    print stddev(numbers)
