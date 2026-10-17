#!/bin/sh
set -eu

usage() {
  echo "usage: $0 create|drop <lowercase-slot>" >&2
  exit 64
}

[ "$#" -eq 2 ] || usage
action=$1
slot=$2

case "$slot" in
  ''|*[!a-z0-9_]*)
    echo "slot: expected lowercase letters, digits, and underscores" >&2
    exit 65
    ;;
esac
case "$slot" in
  [a-z0-9]*) ;;
  *)
    echo "slot: must start with a letter or digit" >&2
    exit 65
    ;;
esac

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
slots_dir="$script_dir/.slots"
slot_dir="$slots_dir/$slot"

case "$action" in
  create)
    mkdir -p "$slots_dir"
    mkdir "$slot_dir" 2>/dev/null || {
      echo "slot: already allocated: $slot" >&2
      exit 73
    }
    printf 'FACTORY_TEST_SLOT=%s\n' "$slot"
    ;;
  drop)
    [ -d "$slot_dir" ] || {
      echo "slot: not allocated: $slot" >&2
      exit 74
    }
    rmdir "$slot_dir"
    rmdir "$slots_dir" 2>/dev/null || true
    ;;
  *) usage ;;
esac
