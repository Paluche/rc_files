#!/usr/bin/env python3

"""
Script to ptin
"""

import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from fontTools.ttLib import TTFont
from fontTools.unicode import Unicode


def main(prog, args):
    """main.

    :param prog:  Name of the program.
    :param args:  Arguments provided by the user.
    """
    parser = ArgumentParser(prog=prog,
                            formatter_class=RawDescriptionHelpFormatter,
                            description=__doc__)

    parser.add_argument(
        dest='font_file',
        help='Path the font you want to print the characters it contains'
    )

    parser.add_argument(
        '-o',
        '--output',
        dest='output',
        help='Where to write the font characters. By default it will be '
             'simply printed out.'
    )

    # Parse the arguments.
    parsed = parser.parse_args(args)

    ttf = TTFont(file=parsed.font_file,
                 res_name_or_index=0,
                 allowVID=0,
                 ignoreDecompileErrors=True,
                 fontNumber=-1)

    chars = {}

    for table in ttf["cmap"].tables:
        for item in table.cmap.items():
            chars[Unicode[item[0]]] = chr(item[0])

    i = 0

    if parsed.output is None:
        for value in chars.values():
            print(f'{value} ', end=('\n' if i and not i % 40 else ''))
            i += 1
    else:
        with open(parsed.output, 'w') as output_file:
            for value in chars.values():
                output_file.write(value)
                if not i or i % 40:
                    output_file.write(' ')
                else:
                    output_file.write('\n')
                i += 1
    ttf.close()


# Main entry point.
if __name__ == "__main__":
    sys.exit(main(sys.argv[0], sys.argv[1:]))
