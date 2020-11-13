from github import Github
from github.Repository import Repository
from github.WorkflowRun import WorkflowRun
from argparse import ArgumentParser
from time import sleep
from typing import Dict
import re
import logging
import os

#
# A watchdog program for reducing redundant workflow in github actions
#   this program watches github workflow in repository as observer process
#   if there are running action in same pull request, then it cancel ahead one
#   so that it can reduce redundant workflow process in github actions
#
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(os.path.basename(__file__))


def main(args):
    gh_api_url = args.gh_api_url
    gh_token = args.gh_token
    repo_owner = args.repo_owner
    repo_name = args.repo_name
    filter = args.filter
    interval = args.interval
    g = Github(base_url=gh_api_url, login_or_token=gh_token)
    repo_key = f'{repo_owner}/{repo_name}'
    r: Repository = g.get_repo(repo_key)
    logger.info(f'''

configure
  repo: {repo_owner}/{repo_name}
  filter: {filter}
  interval: {interval}

''')
    logger.info(f'start github action watchdog...')
    # watch loop
    while True:
        in_progress_wfs_by_head: Dict[str, WorkflowRun] = {}
        # get all workflow available on repository
        # and check that it has same head branch
        # if it has same head branch, then cancel ahead one
        for wfr in r.get_workflow_runs():
            if wfr.status == 'queued':
                wf = r.get_workflow(str(wfr.raw_data['workflow_id']))
                key = (wf.id, wfr.head_branch)
                in_progress_wfs_by_head[key] = wfr
            elif wfr.status == 'in_progress':
                wf = r.get_workflow(str(wfr.raw_data['workflow_id']))
                # decision rule of same workflow
                #   combination of both workflow id and head branch
                key = (wf.id, wfr.head_branch)
                if key in in_progress_wfs_by_head:
                    m = re.match(filter, wf.name)
                    if m:
                        wfr.cancel()
                        subsequent = in_progress_wfs_by_head[key]
                        logger.info(f'cancel workflow id: {wf.id}, run id: {wfr.id}, subsequent: {subsequent.id}, branch: {wfr.head_branch}')

        sleep(interval)


if __name__ == '__main__':
    parser = ArgumentParser('A watchdog program for reducing redundant workflow in github actions')
    parser.add_argument('--repo-owner', type=str, required=True, help='repository owner')
    parser.add_argument('--repo-name', type=str, required=True, help='repository name')
    parser.add_argument('--gh-api-url', type=str, default='https://github.com/api/v3', help='github api url')
    parser.add_argument('--gh-token', type=str, required=True, help='github personal access token')
    parser.add_argument('--interval', type=int, default=2, help='sleep seconds until next check')
    parser.add_argument('--filter', type=str, default='.*', help='filter workflow name with regex')
    args = parser.parse_args()
    main(args)
