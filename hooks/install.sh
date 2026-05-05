#!/bin/sh
# SPDX-License-Identifier: MIT
# install.sh --- symlink each repo's hook entries to fast_data/hooks/
# Copyright (c) 2026 Jakob Kastelic
#
# Run from anywhere inside the superproject. Idempotent.

set -eu

ROOT=$(git rev-parse --show-toplevel)
SRC="$ROOT/hooks"

# List of hooks to install (file names in $SRC, excluding install.sh and README*).
HOOKS="commit-msg pre-commit"

link_one() {
  hooks_dir=$1
  mkdir -p "$hooks_dir"
  for h in $HOOKS; do
    ln -sfn "$SRC/$h" "$hooks_dir/$h"
  done
}

# Superproject
link_one "$(git -C "$ROOT" rev-parse --git-path hooks)"
echo "installed: $ROOT"

# Submodules (recursive)
git -C "$ROOT" submodule foreach --recursive --quiet '
  hooks_dir=$(git rev-parse --git-path hooks)
  mkdir -p "$hooks_dir"
  for h in '"$HOOKS"'; do
    ln -sfn "'"$SRC"'/$h" "$hooks_dir/$h"
  done
  echo "installed: $displaypath"
'
