#!/usr/bin/env python3
"""Write commits.json: every commit on the examples branch, plus the tags on it.

The SPARQL editor (wikipathways/Snorql-UI) reads this file from the commit-index
branch to check that a pinned ?example=...&ref=... link points at a published
version, without calling GitHub's API (60 calls an hour per IP without a login).

    python scripts/commit_index.py <branch> <repository> > commits.json

Run it in a full clone with the branch checked out (fetch-depth 0, tags fetched).
"""
import json
import subprocess
import sys


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout.split()


def on_branch(sha, head):
    return subprocess.run(["git", "merge-base", "--is-ancestor", sha, head]).returncode == 0


def main():
    branch, repository = sys.argv[1], sys.argv[2]
    head = git("rev-parse", "HEAD")[0]
    commits = git("rev-list", head)
    tags = {}
    for tag in git("tag", "--list"):
        sha = git("rev-list", "-n", "1", tag)[0]
        if on_branch(sha, head):
            tags[tag] = sha
    json.dump({"repository": repository, "branch": branch, "head": head,
               "commits": commits, "tags": tags}, sys.stdout, indent=1)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
