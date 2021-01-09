#!/usr/bin/env python3

"""
Script to ptin
"""

import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter


def print_no_end(*args):
    """print_no_end.

    :param args:
    """
    print(*args, end='')


def generate_chars(parsed, print_function):
    """generate_chars.

    :param parsed:
    :param print_function:
    """
    i = 0
    for j in range(parsed.from_, parsed.to + 1):
        if not i or i % parsed.width:
            print_function(' ')
        else:
            print_function(f'\n{i}..{i + parsed.width} ')

        try:
            print_function(chr(j))
        except UnicodeError:
            continue

        i += 1


def main(prog, args):
    """main.

    :param prog:  Name of the program.
    :param args:  Arguments provided by the user.
    """
    parser = ArgumentParser(prog=prog,
                            formatter_class=RawDescriptionHelpFormatter,
                            description=__doc__)

    parser.add_argument(
        '-o',
        '--output',
        dest='output',
        help='Where to write the font characters. By default it will be '
             'simply printed out.'
    )

    parser.add_argument(
        '--width',
        dest='width',
        default=30,
        help='Number of characters per line'
    )

    parser.add_argument(
        '-f',
        '--from',
        dest='from_',
        type=int,
        default=0,
        help='From which unicode number to start the list. Default is 0'
    )

    parser.add_argument(
        '-t',
        '--to',
        dest='to',
        type=int,
        default=0x10fff,
        help='To which unicode number to start the list. Default is 0x10ffff.'
    )

    # Parse the arguments.
    parsed = parser.parse_args(args)

    if parsed.output is None:
        generate_chars(parsed, print_no_end)
    else:
        with open(parsed.output, 'w') as output_file:
            generate_chars(parsed, output_file.write)


# Main entry point.
if __name__ == "__main__":
    sys.exit(main(sys.argv[0], sys.argv[1:]))
