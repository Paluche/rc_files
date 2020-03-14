#!/usr/bin/env python3

import os
import sys
import re
import json
from datetime import datetime
import pygit2
from urllib.parse import urlparse
from argparse import ArgumentParser, RawDescriptionHelpFormatter

__desc__ = '''\
    Compute the git prompt and evaluate
'''

API_URL = {
    'git@gitlab.corp.netatmo.com:1021': 'https://gitlab.corp.netatmo.com',
}

PYGIT_STATUS = {
    "current":          pygit2.GIT_STATUS_CURRENT,
    "index_new":        pygit2.GIT_STATUS_INDEX_NEW,
    "index_modified":   pygit2.GIT_STATUS_INDEX_MODIFIED,
    "index_deleted":    pygit2.GIT_STATUS_INDEX_DELETED,
    "index_renamed":    pygit2.GIT_STATUS_INDEX_RENAMED,
    "index_typechange": pygit2.GIT_STATUS_INDEX_TYPECHANGE,
    "unknown 1":        0b100000,
    "unknown 2":        0b1000000,
    "wt_new":           pygit2.GIT_STATUS_WT_NEW,
    "wt_modified":      pygit2.GIT_STATUS_WT_MODIFIED,
    "wt_deleted":       pygit2.GIT_STATUS_WT_DELETED,
    "wt_typechange":    pygit2.GIT_STATUS_WT_TYPECHANGE,
    "wt_renamed":       pygit2.GIT_STATUS_WT_RENAMED,
    "wt_unreadable":    pygit2.GIT_STATUS_WT_UNREADABLE,
    'unknown 3':        0b10000000000000,
    "ignored":          pygit2.GIT_STATUS_IGNORED,
    "conflicted":       pygit2.GIT_STATUS_CONFLICTED,
}


def __default_status():
    ret = {}

    for key in PYGIT_STATUS.keys():
        ret[key] = False

    return ret


def __parse_file_status(status):
    ret = {}

    for key, value in PYGIT_STATUS.items():
        ret[key] = bool(status & value)

    return ret


def __parse_remote(remote_url):
    SSH_RE = re.compile(
        r'^(?!ssh://)(?P<netloc>(.*)@(.*)):(?P<path>[^(0-9)](.*))$'
    )

    match = SSH_RE.match(remote_url)

    if match:
        url    = match.groupdict()
        path   = url['path']
        netloc = url['netloc']
    else:
        url    = urlparse(remote_url)
        path   = url.path
        netloc = url.netloc

    if path.startswith('/'):
        path = path[len('/'):]

    if path.endswith('.git'):
        path = path[:-len('.git')]

    return path, API_URL.get(netloc)


def main(prog, args):
    ntm_ci_user_token = os.environ.get('NTM_CI_USER_TOKEN')

    parser = ArgumentParser(prog=prog,
                            formatter_class=RawDescriptionHelpFormatter,
                            description=__desc__)

    parser.add_argument('--gitlab-private-token', dest='private_token',
                        required=(not ntm_ci_user_token),
                        default=ntm_ci_user_token,
                        help='Private token to use to access the GitLab API. '
                             'By default we will retrieve the environment '
                             'variable NTM_CI_USER_TOKEN value')

    git_dir = pygit2.discover_repository(os.getcwd())

    if not git_dir:
        return 0

    repository = pygit2.Repository(git_dir)

    ret = {
        # top level
        'top_level': repository.workdir,
        # is submodule
        'is_submodule': os.path.basename(os.path.abspath(repository.path)) != '.git',
        # commit SHA1
        'local_commit': repository.head.target.hex,
        'remote_commit': None,
        # branch name
        'branch_name': repository.head.raw_shorthand.decode('utf-8'),
        # default values:
        'api': None,
        'last_fetch': None,
        'status': {},
        'submodule_status': {},
        'overall_status': __default_status(),
        'overall_submodule_status': __default_status(),
    }

    # name and api URL
    for remote in repository.remotes:
        name, api = __parse_remote(remote.url)

        if 'name' not in ret or remote.name == 'origin':
            ret['name'] = name
            ret['api']  = api

    if 'name' not in ret:
        ret['name'] = os.path.basename(repository.workdir)

    # last fetch
    fetch_head_file = os.path.join(repository.path, 'FETCH_HEAD')

    if os.path.isfile(fetch_head_file):
        ret['last_fetch'] = datetime.fromtimestamp(
            os.lstat(
                fetch_head_file
            ).st_ctime
        ).strftime('%Y %B %d %H:%M')

    # Read the status
    ret['status'] = {}
    ret['submodule_status'] = {}

    submodules = repository.listall_submodules()

    for file_, status in repository.status().items():
        file_status = __parse_file_status(status)

        if file_ in submodules:
            status_key         = 'submodule_status'
            overall_status_key = 'overall_submodule_status'
        else:
            status_key         = 'status'
            overall_status_key = 'overall_status'

        # DBG discard ignored files
        if file_status['ignored']:
            continue

        ret[status_key][file_] = file_status

        for key, value in file_status.items():
            if value:
                ret[overall_status_key][key] = value

    # branch name
    # commit SHA1
    # remote status
    # is dirty
    # has deleted files
    # has modifications added
    # has unmerged files
    # has untracked files

    # submodule deleted
    # submodule added
    # submodule diverged
    # submodule is dirty
    # submodule is unmerged

    # ongoing git operation

    # number of stash pending

    # current tags on reference

    print(json.dumps(ret, indent=4))
    return 0


if __name__ == '__main__':
    main(sys.argv[0], sys.argv[1:])
