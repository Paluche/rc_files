#! /usr/bin/env python3

import subprocess
import re
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from enum import IntEnum


__desc__ = '''\
    Parse and colorized the output of a `git status` command to the most basic
    information. Mostly including the submodules status.
'''


FG_BLACK          = '\033[30m'
FG_RED            = '\033[31m'
FG_GREEN          = '\033[32m'
FG_YELLOW         = '\033[33m'
FG_BLUE           = '\033[34m'
FG_MAGENTA        = '\033[35m'
FG_CYAN           = '\033[36m'
FG_WHITE          = '\033[37m'
FG_BRIGHT_BLACK   = '\033[90m'
FG_BRIGHT_RED     = '\033[91m'
FG_BRIGHT_GREEN   = '\033[92m'
FG_BRIGHT_YELLOW  = '\033[93m'
FG_BRIGHT_BLUE    = '\033[94m'
FG_BRIGHT_MAGENTA = '\033[95m'
FG_BRIGHT_CYAN    = '\033[96m'
FG_BRIGHT_WHITE   = '\033[97m'
RESET             = '\033[0m'


# Git status porcelain v2 output parsing.
#
# Branch Headers
#
# line                                     Notes
# ------------------------------------------------------------
# # branch.oid <commit> | (initial)        Current commit.
# # branch.head <branch> | (detached)      Current branch.
# # branch.upstream <upstream_branch>      If upstream is set.
# # branch.ab +<ahead> -<behind>           If upstream is set and the commit is
#                                          present.
# ------------------------------------------------------------
BRANCH_OID_RE      = re.compile(r'^# branch.oid (?P<commit>(.*))$')
BRANCH_HEAD_RE     = re.compile(r'^# branch.head (?P<branch>(.*))$')
BRANCH_UPSTREAM_RE = re.compile(r'^# branch.upstream (?P<upstream>(.*))$')
BRANCH_AB_RE       = re.compile(r'^# branch.ab \+(?P<ahead>\d+) -(?P<behind>\d+)$')

# Rendering
BRANCH_FMT = f'{FG_BRIGHT_CYAN}{{commit}} {FG_YELLOW}({{upstream}}) {FG_RED}+{{ahead}} ' \
             f'{FG_GREEN}-{{behind}}{RESET}'

# Changed Tracked Entries
#
# Field       Meaning
# --------------------------------------------------------
# <XY>        A 2 character field containing the staged and
#             unstaged XY values:
#                 . = unmodified
#                 M = modified
#                 A = added
#                 D = deleted
#                 R = renamed
#                 C = copied
#                 U = updated but unmerged
XY_PATTERN = r'(?P<staged>[\.MADRCU])(?P<unstaged>[\.MADRCU])'

# <sub>       A 4 character field describing the submodule state.
#             "N..." when the entry is not a submodule.
#             "S<c><m><u>" when the entry is a submodule.
#             <c> is "C" if the commit changed; otherwise ".".
#             <m> is "M" if it has tracked changes; otherwise ".".
#             <u> is "U" if there are untracked changes; otherwise ".".
SUBMODULE_PATTERN = r'(?P<submodule>[SN])'           \
                    r'(?P<submodule_commit>[\.C])'   \
                    r'(?P<submodule_unstaged>[\.M])' \
                    r'(?P<submodule_untracked>[\.U])'

# <mH>        The octal file mode in HEAD.
# <mI>        The octal file mode in the index.
# <mW>        The octal file mode in the worktree.
# <m1>        The octal file mode in stage 1.
# <m2>        The octal file mode in stage 2.
# <m3>        The octal file mode in stage 3.
HEAD_FILE_MODE_PATTERN     = r'(?P<head_file_mode>[0-7]{6})'
INDEX_FILE_MODE_PATTERN    = r'(?P<index_file_mode>[0-7]{6})'
WORKTREE_FILE_MODE_PATTERN = r'(?P<worktree_file_mode>[0-7]{6})'
STAGE_1_FILE_MODE_PATTERN  = r'(?P<stage_1_file_mode>[0-7]{6})'
STAGE_2_FILE_MODE_PATTERN  = r'(?P<stage_2_file_mode>[0-7]{6})'
STAGE_3_FILE_MODE_PATTERN  = r'(?P<stage_3_file_mode>[0-7]{6})'

# <hH>        The object name in HEAD.
# <hI>        The object name in the index.
# <h1>        The object name in stage 1.
# <h2>        The object name in stage 2.
# <h3>        The object name in stage 3.
HEAD_OBJECT_NAME_PATTERN    = r'(?P<head_object_name>[0-9a-f]{40})'
INDEX_OBJECT_NAME_PATTERN   = r'(?P<index_object_name>[0-9a-f]{40})'
STAGE_1_OBJECT_NAME_PATTERN = r'(?P<stage_1_object_name>[0-9a-f]{40})'
STAGE_2_OBJECT_NAME_PATTERN = r'(?P<stage_2_object_name>[0-9a-f]{40})'
STAGE_3_OBJECT_NAME_PATTERN = r'(?P<stage_3_object_name>[0-9a-f]{40})'

# <X><score>  The rename or copy score (denoting the percentage
#             of similarity between the source and target of the
#             move or copy). For example "R100" or "C75".
RENAME_COPY_SCORE_PATTERN = r'(?P<rename_copy_score>[RC](\d+))'

# <path>      The pathname.  In a renamed/copied entry, this
#             is the target path.
PATH_PATTERN = r'(?P<path_name>(.+))'

# <sep>       When the `-z` option is used, the 2 pathnames are separated
#             with a NUL (ASCII 0x00) byte; otherwise, a tab (ASCII 0x09)
#             byte separates them.
SEP_PATTERN = r'[\t\0]'

# <origPath>  The pathname in the commit at HEAD or in the index.
#             This is only present in a renamed/copied entry, and
#             tells where the renamed/copied contents came from.
ORIGIN_PATH_PATTERN = r'(?P<origin_path_name>(.+))'

# Following the headers, a series of lines are printed for tracked entries.
# One of three different line formats may be used to describe an entry
# depending on the type of change. Tracked entries are printed in an undefined
# order; parsers should allow for a mixture of the 3 line types in any order.
#
# Ordinary changed entries have the following format:
#
#     1 <XY> <sub> <mH> <mI> <mW> <hH> <hI> <path>
CHANGED_ENTRY_PATTERN = r'^' + r' '.join(
                            [
                                r'1',
                                XY_PATTERN,
                                SUBMODULE_PATTERN,
                                HEAD_FILE_MODE_PATTERN,
                                INDEX_FILE_MODE_PATTERN,
                                WORKTREE_FILE_MODE_PATTERN,
                                HEAD_OBJECT_NAME_PATTERN,
                                INDEX_OBJECT_NAME_PATTERN,
                                PATH_PATTERN
                            ]
                        ) + r'$'
CHANGED_ENTRY_RE = re.compile(CHANGED_ENTRY_PATTERN)

CHANGED_ENTRY_FMT = f'{FG_GREEN}{{staged}}{FG_RED}{{unstaged}} '      \
                    f'{FG_BLUE}{{submodule}}{{submodule_commit}}'     \
                    f'{{submodule_unstaged}}{{submodule_untracked}} ' \
                    f'{FG_WHITE}{{path_name}}{RESET}'

# Renamed or copied entries have the following format:
#
#     2 <XY> <sub> <mH> <mI> <mW> <hH> <hI> <X><score> <path><sep><origPath>
RENAMED_COPY_ENTRY_PATTERN = r'^' + ' '.join(
                                 [
                                     r'2',
                                     XY_PATTERN,
                                     SUBMODULE_PATTERN,
                                     HEAD_FILE_MODE_PATTERN,
                                     INDEX_FILE_MODE_PATTERN,
                                     WORKTREE_FILE_MODE_PATTERN,
                                     HEAD_OBJECT_NAME_PATTERN,
                                     INDEX_OBJECT_NAME_PATTERN,
                                     RENAME_COPY_SCORE_PATTERN,
                                     PATH_PATTERN + SEP_PATTERN +
                                     ORIGIN_PATH_PATTERN
                                 ]
                             ) + r'$'
RENAMED_COPY_ENTRY_RE = re.compile(RENAMED_COPY_ENTRY_PATTERN)

RENAMED_COPY_ENTRY_FMT = f'{FG_GREEN}{{staged}}{FG_RED}{{unstaged}} '      \
                         f'{FG_BLUE}{{submodule}}{{submodule_commit}}'     \
                         f'{{submodule_unstaged}}{{submodule_untracked}} ' \
                         f'{FG_WHITE}{{origin_path_name}} '                \
                         f'{FG_BRIGHT_MAGENTA}->{FG_WHITE} {{path_name}}{RESET}'


# Unmerged entries have the following format; the first character is a "u" to
# distinguish from ordinary changed entries.
#
#     u <xy> <sub> <m1> <m2> <m3> <mW> <h1> <h2> <h3> <path>
UNMERGED_ENTRY_RE = re.compile(
                       r'^' + r' '.join(
                           [
                               r'u',
                               XY_PATTERN,
                               SUBMODULE_PATTERN,
                               STAGE_1_FILE_MODE_PATTERN,
                               STAGE_2_FILE_MODE_PATTERN,
                               STAGE_3_FILE_MODE_PATTERN,
                               WORKTREE_FILE_MODE_PATTERN,
                               STAGE_1_OBJECT_NAME_PATTERN,
                               STAGE_2_OBJECT_NAME_PATTERN,
                               STAGE_3_OBJECT_NAME_PATTERN,
                               PATH_PATTERN
                           ]
                       ) + r'$'
                    )

UNMERGED_ENTRY_FMT = f'{FG_GREEN}{{staged}}{FG_RED}{{unstaged}} '      \
                     f'{FG_BLUE}{{submodule}}{{submodule_commit}}'     \
                     f'{{submodule_unstaged}}{{submodule_untracked}} ' \
                     f'{FG_WHITE}{{path_name}}{RESET}'

# Untracked items have the following format:
#
# ? <path>
UNTRACKED_ENTRY_RE  = re.compile(
                          r'^' + r' '.join([r'\?', PATH_PATTERN]) + r'$'
                      )
UNTRACKED_ENTRY_FMT = f'{FG_CYAN}?? ???? {FG_WHITE}{{path_name}}{RESET}'

# Ignored items have the following format:
#
# ! <path>
IGNORED_ENTRY_RE  = re.compile(r'^' + r' '.join([r'!', PATH_PATTERN]) + r'$')
IGNORED_ENTRY_FMT = f'{FG_CYAN}!! !!!! {FG_BLUE}{{path_name}}{RESET}'


def main(prog, args):
    parser = ArgumentParser(prog=prog,
                            formatter_class=RawDescriptionHelpFormatter,
                            description=__desc__)

    parser.add_argument('--ignored', dest='show_ignored', action='store_true',
                        help='Show ignored files as well.')

    parsed = parser.parse_args(args)

    git_status_args = ['git', 'status', '--porcelain=v2', '--branch']

    if parsed.show_ignored:
        git_status_args.append('--ignored=traditional')

    proc = subprocess.Popen(git_status_args,
                            shell=False,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL)

    msg = []
    branch_results = {}
    branch_matchers = [
        BRANCH_AB_RE,
        BRANCH_OID_RE,
        BRANCH_HEAD_RE,
        BRANCH_UPSTREAM_RE,
    ]

    matchers = {
        'changed_entry     ': (CHANGED_ENTRY_RE,      CHANGED_ENTRY_FMT),
        'renamed_copy_entry': (RENAMED_COPY_ENTRY_RE, RENAMED_COPY_ENTRY_FMT),
        'unmerged_entry    ': (UNMERGED_ENTRY_RE,     UNMERGED_ENTRY_FMT),
        'untracked_entry   ': (UNTRACKED_ENTRY_RE,    UNTRACKED_ENTRY_FMT),
        'ignored_entry     ': (IGNORED_ENTRY_RE,      IGNORED_ENTRY_FMT),
        'NO MATCH          ': (re.compile(r'^(?P<line>.*)$'), '{line}'),
    }

    while True:
        line = proc.stdout.readline().decode('utf-8').rstrip()

        if line == '':
            break

        if line[0] == '#':
            for matcher in branch_matchers:
                match = matcher.match(line)

                if not match:
                    continue

                branch_results.update(match.groupdict())

            continue

        for name, (matcher, format_) in matchers.items():
            match = matcher.match(line)

            if not match:
                continue

            msg.append(format_.format(**match.groupdict()))
            break

    if branch_results:
        print(BRANCH_FMT.format(**branch_results))

    print('\n'.join(msg))


if __name__ == '__main__':
    main(sys.argv[0], sys.argv[1:])
