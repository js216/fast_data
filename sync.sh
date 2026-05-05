#!/bin/sh
# SPDX-License-Identifier: MIT
# sync.sh --- TODO: description
# Copyright (c) 2026 Jakob Kastelic
# Pull latest across parent + submodules.
# Errors abort the script — fix the cause and re-run.
set -eu
cd "$(git rev-parse --show-toplevel)"

git submodule foreach --recursive '
    git fetch origin
    if git show-ref --verify --quiet refs/remotes/origin/main; then
        git checkout main
        git rebase origin/main
    else
        echo "skipping $name: no origin/main branch"
    fi
'

git -c submodule.recurse=false pull --rebase

git submodule foreach --quiet --recursive 'pwd' |
    awk '{ n = gsub("/", "/"); print n " " $0 }' |
    sort -rn |
    sed 's/^[0-9][0-9]* //' |
    while IFS= read -r repo; do
        (
        cd "$repo"
        branch=$(git rev-parse --abbrev-ref HEAD)
        if [ "$branch" = main ]; then
            moved=$(git submodule status 2>/dev/null | awk "/^\\+/{print \$2}")
            if [ -n "$moved" ]; then
                echo "$moved" | xargs git add
                git commit -m "submodules: bump after sync"
            fi
        fi
        )
    done

moved=$(git submodule status | awk '/^\+/{print $2}')
if [ -n "$moved" ]; then
    echo "$moved" | xargs git add
    git commit -m "submodules: bump after sync"
fi
