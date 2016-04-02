"""Calculate median of some numbers.

If called as main script:

stdin

    A list one numbers, one per line.

stdout

    The median of the input numbers.

"""
import sys

def median(numbers):
    """Calculate median of some numbers.

    Parameters

        numbers : an iterable of numeric values.

    Returns

        The median of ``numbers``.

    """
    numbers = sorted(numbers)
    if len(numbers) % 2 != 0:
        # odd
        print numbers[len(numbers)/2]
    else:
        print (numbers[len(numbers)/2] + numbers[len(numbers)/2 - 1]) / 2.0
        #[0][1][2][3][4][5]
    

if __name__ == '__main__':
    numbers = []
    for line in sys.stdin:
        numbers.append(float(line.strip()))
    med = median(numbers)
    print med
