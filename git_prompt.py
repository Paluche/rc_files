#!/usr/bin/env python3

import os
import sys
import re
from pygit2 import Repository, discover_repository
from urllib.parse import urlparse
from argparse import ArgumentParser, RawDescriptionHelpFormatter

__desc__ = '''\
    Compute the git prompt and evaluate
'''


def main(prog, args):
    ci_api_v4_url     = os.environ.get('CI_API_V4_URL')
    ntm_ci_user_token = os.environ.get('NTM_CI_USER_TOKEN')

    parser = ArgumentParser(prog=prog,
                            formatter_class=RawDescriptionHelpFormatter,
                            description=__desc__)

    parser.add_argument('--private-token', dest='private_token',
                        required=(not ntm_ci_user_token),
                        default=ntm_ci_user_token,
                        help='Private token to use to access the GitLab API. '
                             'By default we will retrieve the environment '
                             'variable NTM_CI_USER_TOKEN value')

    parser.add_argument('--gitlab-url', dest='gitlab_url',
                        required=(not ci_api_v4_url),
                        default=ci_api_v4_url[:-len('/api/v4')]
                            if ci_api_v4_url else None,
                        help='URL to the GitLab API. By default we will '
                             'retrieve the environment variable CI_API_V4_URL '
                             'value to which we will remove the "api/v4" at '
                             'the end of it.')

    git_dir = discover_repository(os.getcwd())

    if not git_dir:
        return 0

    repository = Repository(git_dir)




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
