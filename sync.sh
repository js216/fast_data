#!/bin/sh
# SPDX-License-Identifier: MIT
# sync.sh --- TODO: description
# Copyright (c) 2026 Jakob Kastelic
# Pull latest, push local work, across parent + submodules.
# Errors abort the script — fix the cause and re-run.
set -eu
cd "$(git rev-parse --show-toplevel)"

git submodule foreach '
    git fetch origin
    git checkout main
    git rebase origin/main
    if git rev-list @{u}..HEAD | grep -q .; then
        git push origin main
    fi
'

git -c submodule.recurse=false pull --rebase
moved=$(git submodule status | awk '/^\+/{print $2}')
if [ -n "$moved" ]; then
    echo "$moved" | xargs git add
    git commit -m "submodules: bump after sync"
fi
if git rev-list '@{u}..HEAD' | grep -q .; then
    git push
fi
