#!/usr/bin/env python3

import sys
import os
from gitlab import Gitlab
from gitlab.exceptions import GitlabGetError
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from netatmo.logging import Color, format_string

__desc__ = '''\
    Script which will use the GitLab API to retrieve the link to a merge
    request associated with a branch name.
'''


def __prompt_output(parsed, commit, merge_request, approvals):
    PIPELINE_STATUS = {
        'created':  format_string('', fg=Color.YELLOW),
        'pending':  format_string('', fg=Color.YELLOW),
        'running':  format_string('', fg=Color.YELLOW),
        'manual':   format_string('', fg=Color.YELLOW),
        'success':  format_string('', fg=Color.GREEN),
        'failed':   format_string('', fg=Color.RED),
        'canceled': format_string('', fg=Color.YELLOW, fg_bright=True),
        'skipped':  format_string('', fg=Color.YELLOW, fg_bright=True),
    }

    MR_STATE = {
        'opened':  format_string('', fg=Color.GREEN),
        'wip':     format_string('', fg=Color.YELLOW),
        'closed':  format_string('', fg=Color.RED),
        'locked':  format_string('', fg=Color.RED),
        'merged':  format_string('', fg=Color.YELLOW),
        'unknown': format_string('?', fg=Color.YELLOW),
    }

    msg = []

    if commit:
        if parsed.remote_commit is None or commit.id != parsed.remote_commit:
            msg.append(format_string('', fg=Color.RED))

        if commit.last_pipeline:
            msg.append(PIPELINE_STATUS[commit.last_pipeline['status']])

    elif parsed.remote_commit is not None:
        msg.append(format_string('', fg=Color.RED))

    if merge_request:
        if merge_request.work_in_progress and merge_request.state == 'opened':
            mr_state = 'wip'
        else:
            mr_state = merge_request.state

        msg.append(f'{MR_STATE[mr_state]}{merge_request.reference}')
        nb_approvals = len(approvals.approved_by)

        if nb_approvals:
            msg.append(format_string(f'{nb_approvals}', fg=Color.GREEN))

        if merge_request.upvotes:
            msg.append(format_string(f'{merge_request.upvotes}',
                                     fg=Color.YELLOW))

        if merge_request.downvotes:
            msg.append(format_string(f'{merge_request.downvotes}',
                                     fg=Color.YELLOW))
    print(format_string('-', fg=Color.CYAN).join(msg))


def __full_output(parsed, commit, merge_request, approvals):
    PIPELINE_STATUS = {
        'created':  {'fg': Color.YELLOW},
        'pending':  {'fg': Color.YELLOW},
        'running':  {'fg': Color.YELLOW},
        'manual':   {'fg': Color.YELLOW},
        'success':  {'fg': Color.GREEN},
        'failed':   {'fg': Color.RED},
        'canceled': {'fg': Color.YELLOW, 'fg_bright': True},
        'skipped':  {'fg': Color.YELLOW, 'fg_bright': True},
    }

    MR_STATE = {
        'opened': {'fg': Color.GREEN},
        'closed': {'fg': Color.RED},
        'locked': {'fg': Color.RED},
        'merged': {'fg': Color.YELLOW},
    }

    msg = []

    if commit:
        if parsed.remote_commit is None or commit.id != parsed.remote_commit:
            msg.append(format_string('LOCAL DIVERGED', fg=Color.RED))

        if commit.last_pipeline:
            msg.append('Pipeline {}:'.format(commit.last_pipeline['id']))
            msg.append(
                '    {}'.format(
                    format_string(
                        commit.last_pipeline['status'],
                        **PIPELINE_STATUS[commit.last_pipeline['status']]
                    )
                )
            )
            msg.append('    {}'.format(commit.last_pipeline['web_url']))
        else:
            msg.append('Pipeline unknown')

    elif parsed.remote_commit is not None:
        msg.append(format_string('No remote', fg=Color.RED))

    if merge_request:
        msg.append(f'Merge request {merge_request.reference}:')
        msg.append(
            '    State     {}'.format(
                format_string(
                    merge_request.state,
                    **MR_STATE[merge_request.state]
                )
            )
        )

        msg.append(f'    WIP       {merge_request.work_in_progress}')

        msg.append(
            '    {}         {}'.format(
                format_string('', fg=Color.GREEN),
                '0' if not approvals.approved_by
                else ', '.join(x['user']['name'] for x in approvals.approved_by)
            )
        )

        msg.append(
            '    {}         {}'.format(
                format_string('', fg=Color.YELLOW),
                merge_request.upvotes
            )
        )

        msg.append(
            '    {}         {}'.format(
                format_string('', fg=Color.YELLOW),
                merge_request.downvotes
            )
        )

        msg.append(
            '    Labels    {}'.format(
                ', '.join(merge_request.labels)
            )
        )

        notes_count = 0
        notes_resolved = 0

        for note in merge_request.notes.list(all=True):
            if note.type is None:
                continue

            if not hasattr(note, 'resolved'):
                continue

            notes_count += 1
            if note.resolved:
                notes_resolved += 1

        msg.append(f'    Comments  {notes_resolved}/{notes_count}')
        msg.append(f'    URL       {merge_request.web_url}')
    else:
        # Print link to create a merge request:
        msg.append('No merge request, to create one:')
        msg.append(
            '    {}/{}/merge_requests/new?merge_request%5Bsource_branch%5D={}'
            .format(
                parsed.gitlab_url,
                parsed.project_path,
                parsed.branch.replace('/', '%2F'),
            )
        )

    print('\n'.join(msg))


def main(prog, args):
    ci_api_v4_url           = os.environ.get('CI_API_V4_URL')
    ntm_ci_user_token       = os.environ.get('NTM_CI_USER_TOKEN')
    git_name                = os.environ.get('__GIT_NAME')
    git_branch_name         = os.environ.get('__GIT_BRANCH_NAME')
    git_remote_commit_sha1  = os.environ.get('__GIT_REMOTE_COMMIT_SHA1')

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

    parser.add_argument('--project-path', dest='project_path',
                        required=(not git_name),
                        default=git_name,
                        help='GitLab path with namespace of the project where '
                        'to look for the branch.')

    parser.add_argument('--branch', dest='branch',
                        required=(not git_branch_name),
                        default=git_branch_name,
                        help='Git branch name you want the information about.')

    parser.add_argument('--remote-commit', dest='remote_commit',
                        default=git_remote_commit_sha1,
                        help='SHA of the commit the remote of the current '
                             'branch is at.')

    parser.add_argument('--prompt', dest='prompt', action='store_true',
                        help='Prompt output')

    parsed = parser.parse_args(args)

    try:
        gitlab = Gitlab(parsed.gitlab_url, private_token=parsed.private_token)
        project = gitlab.projects.get(parsed.project_path)
    except Exception:
        return 1

    try:
        commit = project.commits.get(parsed.branch)
    except GitlabGetError:
        commit = None

    merge_request = project.mergerequests.list(source_branch=parsed.branch)

    if merge_request:
        if len(merge_request) > 1:
            print(f'Several merge requests found for branch {parsed.branch} in '
                  f'project {parsed.project_path}.', file=sys.stderr)

        merge_request = merge_request.pop()
        approvals = merge_request.approvals.get()
    else:
        approvals = None

    if parsed.prompt:
        __prompt_output(parsed, commit, merge_request, approvals)
    else:
        __full_output(parsed, commit, merge_request, approvals)

    return 0


if __name__ == '__main__':
    main(sys.argv[0], sys.argv[1:])
