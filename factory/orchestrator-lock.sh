#!/bin/sh
set -eu

usage() {
  echo "usage: $0 acquire|release <owner-token>" >&2
  exit 64
}

[ "$#" -eq 2 ] || usage
action=$1
owner=$2

case "$owner" in
  ''|*[!A-Za-z0-9._:@-]*)
    echo "orchestrator lock: invalid owner token" >&2
    exit 65
    ;;
esac

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
lock_dir="$script_dir/.orchestrator-lock"
owner_file="$lock_dir/owner"

case "$action" in
  acquire)
    if mkdir "$lock_dir" 2>/dev/null; then
      umask 077
      printf '%s\n' "$owner" > "$owner_file"
      exit 0
    fi
    if [ -f "$owner_file" ]; then
      held_by=$(sed -n '1p' "$owner_file")
    else
      held_by='<unknown: incomplete acquisition>'
    fi
    echo "orchestrator lock: occupied by $held_by" >&2
    exit 73
    ;;
  release)
    [ -d "$lock_dir" ] || {
      echo "orchestrator lock: no lock is held" >&2
      exit 74
    }
    [ -f "$owner_file" ] || {
      echo "orchestrator lock: owner is unreadable; human inspection required" >&2
      exit 75
    }
    held_by=$(sed -n '1p' "$owner_file")
    [ "$held_by" = "$owner" ] || {
      echo "orchestrator lock: held by $held_by, not $owner" >&2
      exit 76
    }
    rm "$owner_file"
    rmdir "$lock_dir"
    ;;
  *) usage ;;
esac
