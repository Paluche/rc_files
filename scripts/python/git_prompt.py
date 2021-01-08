#!/usr/bin/env python3

import sys
import re
from urllib.parse import urlparse
from argparse import ArgumentParser, RawDescriptionHelpFormatter

__desc__ = '''\
    Compute the git prompt and evaluate
'''


def main(prog, args):
    parser = ArgumentParser(prog=prog,
                            formatter_class=RawDescriptionHelpFormatter,
                            description=__desc__)

    parser.add_argument(dest='git_url')

    parsed = parser.parse_args(args)

    SSH_RE = re.compile(
        r'^[^ssh://](?P<user>(.*))@(?P<host>(.*)):(?P<path>[^(0-9)](.*))$'
    )

    match = SSH_RE.match(parsed.git_url)

    if match:
        path = match.groupdict()['path']
    else:
        url = urlparse(parsed.git_url)

        path = url.path

    if path.startswith('/'):
        path = path[len('/'):]

    if path.endswith('.git'):
        path = path[:-len('.git')]

    print(path)

    return 0


if __name__ == '__main__':
    main(sys.argv[0], sys.argv[1:])
