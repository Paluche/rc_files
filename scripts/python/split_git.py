#!/usr/bin/env python3

"""
    Script to split a git repository.
"""

import re
import sys
import os
from subprocess import run
from getpass import getpass
from tempfile import TemporaryDirectory
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from pygit2 import clone_repository, init_repository, Keypair, RemoteCallbacks
from pygit2 import Username, Repository
from pygit2.credentials import GIT_CREDENTIAL_USERNAME
from pygit2.credentials import GIT_CREDENTIAL_SSH_KEY
from paluche.logging import print_format, Color

REFS_REMOTE_PREFIX = 'refs/remotes/origin/'
REFS_TAGS_PREFIX   = 'refs/tags/'


class GitRemoteCallbacks(RemoteCallbacks):
    """
    Custom RemoteCallbacks class for handling pygit2 user actions following
    remote actions.
    """

    def __init__(self, username, ssh_priv_key, ssh_pub_key):
        """ Initialize the class.

        :param username:      Username to use for authenticating.
        :param ssh_priv_key:  Path to the SSH private key to use in case we
                              need to authenticate using a SSH key.
        :param ssh_pub_key:   Path to the SSH public key to use.
        """
        self.username = username
        self.ssh_priv_key = ssh_priv_key
        self.ssh_pub_key = ssh_pub_key
        self.keypair = None
        self.first_time = True
        super().__init__()

    def sideband_progress(self, string):
        """
        Progress output callback.  Override this function with your own
        progress reporting function

        Parameters:

        string : str
            Progress output from the remote.
        """
        print('sideband_progress:')
        print(f'    string: {string}')

    def credentials(self, url, username_from_url, allowed_types):
        """
        Credentials callback.  If the remote server requires authentication,
        this function will be called and its return value used for
        authentication. Override it if you want to be able to perform
        authentication.

        Returns: credential

        Parameters:

        url : str
            The url of the remote.

        username_from_url : str or None
            Username extracted from the url, if any.

        allowed_types : int
            Credential types supported by the remote.
        """
        if username_from_url:
            username = username_from_url
        else:
            username = self.username

        if allowed_types & GIT_CREDENTIAL_USERNAME:
            return Username(self.username)

        if allowed_types & GIT_CREDENTIAL_SSH_KEY:
            print('SSH authentication:')
            if self.first_time:
                msg = 'Enter passphrase'
                self.first_time = False
            else:
                msg = 'Bad passphrase, try again'

            passphrase = getpass(f'{msg} for {self.ssh_priv_key}: ')

            self.keypair = Keypair(
                username,
                self.ssh_pub_key,
                self.ssh_priv_key,
                passphrase
            )

            return self.keypair

        print("Unsupported authentication method")
        return None

    def certificate_check(self, certificate, valid, host):
        """
        Certificate callback. Override with your own function to determine
        whether to accept the server's certificate.

        Returns: True to connect, False to abort.

        Parameters:

        certificate : None
            The certificate. It is currently always None while we figure out
            how to represent it cross-platform.

        valid : bool
            Whether the TLS/SSH library thinks the certificate is valid.

        host : str
            The hostname we want to connect to.
        """

        print('certificate_check:')
        print(f'     certificate: {certificate}')
        print(f'     valid: {valid}')
        print(f'     host: {host}')

        return True

    def transfer_progress(self, stats):
        """
        Transfer progress callback. Override with your own function to report
        transfer progress.

        Parameters:

        stats : TransferProgress
            The progress up to now.
        """
        print(
            'Transfer progress: {}/{} {}%'.format(
                stats.indexed_objects,
                stats.total_objects,
                int((stats.indexed_objects * 100) / stats.total_objects)
            ),
            end=('\r'
                 if stats.total_objects != stats.indexed_objects
                 else '\n')
        )


def list_remote_references(repo):
    """list_branches.

    :param repo:  Repository instance from which to retrieve the known remote
                  branches
    :param remote_name: Name of the remote you want the branches from.

    :return: Tuple of 2 sets. The first one being the set of the branches
             name for the specified remote. The second one being the set tags
             in the repository.
    :rtype: (set, set)
    """
    branches = set()
    tags = set()

    for reference in repo.references:
        if reference.startswith(REFS_REMOTE_PREFIX):
            branch_name = reference[len(REFS_REMOTE_PREFIX):]
            if branch_name != 'HEAD':
                branches.add(branch_name)
        elif reference.startswith(REFS_TAGS_PREFIX):
            tags.add(reference[len(REFS_TAGS_PREFIX):])

    return branches, tags


def print_list(list_, name, to_keep):
    """print_list. Pretty print of a reference list to be kept during the
    migration or not.

    :param list_:  List of references to be printed.
    :type list_:  list
    :param name:  Name of the type of reference.
    :type name:  str
    :param to_keep:  Boolean to indicate if the printed list is a list of
                     references to be kept or not.
    :type to_keep: bool
    """
    if not list_:
        return

    print(
        '{} which will{} be migrated:'.format(
            name.title(),
            '' if to_keep else ' NOT'
        ),
    )

    for element_name in list_:
        print_format(
            f'    {element_name}',
            fg=(Color.GREEN if to_keep else Color.RED)
        )


def list_references(parsed, repo):
    """list_references.

    :param parsed:  Parsed arguments from the user.
    :type parsed:  argparse.Namespace
    :param repo:  Repository instance from which to retrieve the known remote
                  branches
    :type repo:  pygit2.Repository

    :return: Tuple of 4 lists:
             - The first one being the list of the branches name to keep.
             - The second one being the list tags name to keep.
    :rtype: (list, list, list, list)
    """
    branches, tags = list_remote_references(repo)
    tags_to_keep = set()

    if not parsed.no_tags:
        if parsed.tag_regexps:
            for tag_regexp in parsed.tag_regexps:
                for tag in tags:
                    if tag_regexp.match(tag):
                        tags_to_keep.add(tag)
        else:
            tags_to_keep = tags

    if not parsed.branch_regexps:
        branches_to_keep = branches
    else:
        branches_to_keep = set()
        for branch_regexp in parsed.branch_regexps:
            for branch in branches:
                if branch_regexp.match(branch):
                    branches_to_keep.add(branch)

    tags_to_delete = tags.difference(tags_to_keep)
    branches_to_delete = branches.difference(branches_to_keep)

    print_list(tags_to_delete, 'tags', False)
    print_list(tags_to_keep, 'tags', True)
    print_list(branches_to_delete, 'branches', False)
    print_list(branches_to_keep, 'branches', True)

    return list(branches_to_keep), list(branches_to_delete), \
           list(tags_to_keep), list(tags_to_delete)


def discard_directory(dir_path, paths_to_keep, paths_to_delete):
    """discard_directory. Utils for list_paths() to know if the current
    directory we are can be discarded, as already considered as to be kept or
    deleted.

    :param dir_path:  Path of the directory.
    :type dir_path:  str
    :param paths_to_keep:  List of already identified path as to be kept.
    :type paths_to_keep:  set
    :param paths_to_delete:  List of already identified path as to delete.
    :type paths_to_delete:  set

    :return: True if the directory can be discarded, False otherwise.
    :rtype: bool
    """
    for path_to_delete in paths_to_delete:
        if os.path.commonprefix((path_to_delete, dir_path)) == path_to_delete:
            return True

    for path_to_keep in paths_to_keep:
        if os.path.commonprefix((path_to_keep, dir_path)) == path_to_keep:
            return True

    return False


def delete_path(path, parsed_paths_to_keep):
    """delete_path. Utils for list_paths() to know if the current
    directory we are can be considered as "to delete".

    :param path:  Path of the directory.
    :type path:  str
    :param paths_to_keep:  List of path to keep, as provided by the user.
    :type paths_to_keep:  set

    :return: True if the directory can be deleted, False otherwise.
    :rtype: bool
    """
    if parsed_paths_to_keep:
        for path_to_keep in parsed_paths_to_keep:
            if path_to_keep.startswith(path):
                return False
        return True
    return False


def keep_path(path, parsed_paths_to_keep):
    """keep_path. Utils for list_paths() to know if the current path is one
    of those to be kept.

    :param path:  Path of the directory.
    :type path:  str
    :param paths_to_keep:  List of paths as to keep, as provided by the
                             user.
    :type paths_to_keep:  set

    :return: True if the directory can be deleted, False otherwise.
    :rtype: bool
    """

    if not parsed_paths_to_keep:
        return True

    for path_to_keep in parsed_paths_to_keep:
        if path_to_keep == path:
            return True

    return False


def walk_head(repo):
    """walk_head. Generator that will allow you to walk through the tracked
    files at the head of the repository.

    :param repo: Repository to walk into.
    :type repo: pygit2.Repository
    """
    trees = [('', repo.head.peel().tree)]

    for dir_path, objects in trees:
        file_names = []
        for object_ in objects:
            if object_.type_str == 'tree':
                tree_dir_path = os.path.join(dir_path, object_.name)
                trees.append((f'{tree_dir_path}/', object_))
            file_names.append(object_.name)

        yield dir_path, file_names


def list_paths(repo, parsed_paths_to_keep):
    """list_paths.  List the path of tracked files / folders

    :param repo:
    :param parsed_paths_to_keep:
    """
    if parsed_paths_to_keep:
        parsed_paths_to_keep = set(parsed_paths_to_keep)
    paths_to_delete = set()
    paths_to_keep = set()

    for dir_path, file_names in walk_head(repo):
        if discard_directory(dir_path, paths_to_keep, paths_to_delete):
            continue

        for file_name in file_names:
            path = os.path.join(dir_path, file_name)
            if delete_path(path, parsed_paths_to_keep):
                paths_to_delete.add(path)

            if keep_path(path, parsed_paths_to_keep):
                paths_to_keep.add(path)

    if parsed_paths_to_keep:
        parsed_paths_to_keep = parsed_paths_to_keep.difference(paths_to_keep)

    if parsed_paths_to_keep:
        print('WARNING: Unmatched path to be kept:')
        for path in parsed_paths_to_keep:
            print_format(f'    {path}', fg=Color.YELLOW)
    print_list(paths_to_delete, 'paths', False)
    if paths_to_keep:
        print_list(paths_to_keep, 'paths', True)

    return list(paths_to_keep), list(paths_to_delete)


def parse_args(prog, args):
    """parse_args. Parse the arguments provided by the script.

    :param prog:  Name of the script file.
    :type prog: str
    :param args:  List of argument provided to the script.
    :type prog: list
    """
    parser = ArgumentParser(prog=prog,
                            formatter_class=RawDescriptionHelpFormatter,
                            description=__doc__)

    home = os.environ.get('HOME')
    if home:
        ssh_dir = os.path.join(home, '.ssh')
        default_id_rsa_pub = os.path.join(ssh_dir, 'id_rsa.pub')
        default_id_rsa = os.path.join(ssh_dir, 'id_rsa')
    else:
        default_id_rsa_pub = None
        default_id_rsa = None

    parser.add_argument(
        dest='source',
        help='Path/URL to the source repository which we will split'
    )

    parser.add_argument(
        dest='destination',
        help='Path/URL to the destination repository where to push the '
             'splited result.'
    )

    parser.add_argument(
        '-b',
        '--branch-regex',
        action='append',
        metavar='REGEXP',
        type=re.compile,
        dest='branch_regexps',
        help='Specify the regular expression the branches to keep from the '
             'source repository must match. You can specify several ones by '
             'repeatedly using this option. By default all the branches will '
             'be kept.'
    )

    parser.add_argument(
        '-t',
        '--tag-regexp',
        action='append',
        metavar='REGEXP',
        type=re.compile,
        dest='tag_regexps',
        help='Specify a regular expression the tags to keep from the source '
             'repository must match. You can specify several ones by '
             'repeatedly using this option. By default all the tags will be '
             'kept.'
    )

    parser.add_argument(
        '--no-tags',
        action='store_true',
        dest='no_tags',
        help='Specify this option if you want to have none of the tags from '
             'the source repository being kept in the split one.'
    )

    parser.add_argument(
        '-p',
        '--paths',
        action='append',
        metavar='path',
        dest='paths',
        help='Specify a paths (path from the git root of a path to keep. '
             'You can specify several ones by repeatedly using this option. '
             'If you specify only one, then the split repository will have '
             'its root being the specified path.'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        dest='dry_run',
        help='Have the script run without the splitting operations performed. '
             'Use this option to check what branches / tags / files the '
             'script will keep based on the options you provided. In order to '
             'do so the script will still clone the source repository.'
    )

    parser.add_argument(
        '--username',
        default='git',
        dest='username',
        help='User to use to authenticate to clone the source repository and '
             'push the split one. Defaults to "git".'
    )

    parser.add_argument(
        '--public-key',
        default=default_id_rsa_pub,
        dest='public_key',
        help='Path to the public key to use to authenticate to clone the '
             'source repository and push the destination one. Defaults to '
             f'"{default_id_rsa_pub}".'
    )

    parser.add_argument(
        '--private-key',
        default=default_id_rsa,
        dest='private_key',
        help='Path to the private key to use to authenticate to clone the '
             'source repository and push the destination one. Defaults to '
             f'{default_id_rsa_pub}.'
    )

    parsed = parser.parse_args(args)

    if not any((parsed.branch_regexps,
                parsed.tag_regexps,
                parsed.no_tags,
                parsed.paths)):
        parser.error('Nothing to be changed to the source repository.')

    if os.path.exists(os.path.dirname(parsed.destination)):
        if os.path.exists(parsed.destination):
            parser.error('Destination path already exists')

    return parsed


def main(prog, args):
    """main.

    :param prog:  Name of the script file.
    :type prog: str
    :param args:  List of argument provided to the script.
    :type prog: list
    """
    parsed = parse_args(prog, args)

    with TemporaryDirectory() as tmp_src_dir:
        print(f'Cloning source repository in {tmp_src_dir}')
        callbacks = GitRemoteCallbacks(parsed.username,
                                       parsed.private_key,
                                       parsed.public_key)

        clone_repository(parsed.source, tmp_src_dir, callbacks=callbacks)

        repo = Repository(tmp_src_dir)
        branches_to_keep, _, tags_to_keep, tags_to_delete = \
             list_references(parsed, repo)
        paths_to_keep, paths_to_delete = list_paths(repo, parsed.paths)

        if len(paths_to_keep) == 1:
            print('Single path split')
        elif paths_to_keep and paths_to_delete:
            print('Several paths split')
        else:
            print('Keeping all paths')

        if parsed.dry_run:
            return 0

        # Track all the branch we want to migrate locally.
        for branch in branches_to_keep:
            repo.create_branch(
                branch,
                repo.references.get(f'{REFS_REMOTE_PREFIX}/{branch}').peel()
            )

        # Remove old origin
        repo.remotes.delete('origin')

        for tag in tags_to_delete:
            repo.references.delete(f'{REFS_TAGS_PREFIX}/{tag}')

        print(repo.listall_references())

        if len(paths_to_keep) == 1:
            run(['git',
                 '-C', tmp_src_dir,
                 'filter-branch',
                 '--tag-name-filter',
                 'cat',
                 '--prune-empty',
                 '--subdirectory-filter', paths_to_keep[0],
                 '--all'],
                 check=True)
            run(['git', '-C', tmp_src_dir, 'reset', '--hard'], check=True)

        if len(paths_to_keep) > 1 and len(paths_to_delete) > 1:
            # Filter tags using inverted regex
            run(['git',
                 '-C', tmp_src_dir,
                 'filter-branch',
                 '--force',
                 '--index-filter',
                 '"git rm -r --cached --ignore-unmatch {}"'.format(
                     ' '.join(paths_to_delete)
                 ),
                 '--prune-empty',
                 '--tag-name-filter',
                 'cat',
                 '--',
                 '--all'],
                 check=True)
            run(['git', '-C', tmp_src_dir, 'reset', '--hard'], check=True)

        # Clean up the mess
        run(['git',
             '-C', tmp_src_dir,
             'reflog,',
             'expire,',
             '--expire=now,',
             '--all'],
             check=True)

        run(['git', '-C', tmp_src_dir, 'gc', '--aggressive,', '--prune=now'],
            check=True)

        # Create destination repository
        if os.path.exists(os.path.dirname(parsed.destination)):
            init_repository(parsed.destination, True)

        # Add new origin and push master
        remote = repo.remotes.add('origin', parsed.destination).push()

        # push all branches and tags to be kept.
        remote.push(branches_to_keep + tags_to_keep)

    return 0


# Main entry point.
if __name__ == "__main__":
    sys.exit(main(sys.argv[0], sys.argv[1:]))
