# Redundant-Action-Watchdog

A watchdog program for reducing redundant workflow in github actions.
This program watches github workflow in repository as observer process.
If there are running action in same pull request (same head branch), then it cancel ahead one.
So that it can reduce redundant workflow process in github actions.


## Requirements
- Python3.6+

## Getting Started

```
pip install -r requirements.txt

python redundant_action_watchdog.py --repo-owner {repo owner} --repo-name {repo name} --gh-token {personal access token}
```
