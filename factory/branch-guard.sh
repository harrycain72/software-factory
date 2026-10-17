#!/bin/sh
set -eu

usage() {
  echo "usage: $0 <worktree> <expected-branch>" >&2
  exit 64
}

[ "$#" -eq 2 ] || usage
worktree=$1
expected=$2

[ -n "$worktree" ] && [ -d "$worktree" ] || {
  echo "branch guard: worktree does not exist: $worktree" >&2
  exit 65
}
[ -n "$expected" ] && [ "$expected" != "main" ] || {
  echo "branch guard: expected branch must be non-main" >&2
  exit 66
}

current=$(git -C "$worktree" symbolic-ref --quiet --short HEAD) || {
  echo "branch guard: detached HEAD or unreadable branch in $worktree" >&2
  exit 67
}

[ "$current" != "main" ] || {
  echo "branch guard: local main is forbidden" >&2
  exit 68
}
[ "$current" = "$expected" ] || {
  echo "branch guard: expected $expected, found $current" >&2
  exit 69
}
