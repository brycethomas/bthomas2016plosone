"""Calculate average of an iterable of numbers.

If called as main script:

stdin

    One numeric value per line.

stdout

    The average of the input values.

"""
import sys

def avg(numbers):
    """Calculate average of an iterable of numbers.

    Parameters

        numbers : iterable of numeric values.

    Returns

        The average of ``numbers``.

    """
    return float(sum(numbers))/len(numbers)

if __name__ == "__main__":
    numbers = []
    for line in sys.stdin:
        numbers.append(float(line.strip()))
    print avg(numbers)
