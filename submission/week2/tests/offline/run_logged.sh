#!/usr/bin/env bash
set -uo pipefail

if [[ "$#" -lt 2 ]]; then
  echo "usage: $0 LOG_FILE COMMAND [ARG ...]" >&2
  exit 2
fi

log_file="$1"
shift
mkdir -p -- "$(dirname -- "$log_file")"

{
  echo "DATE: $(date --iso-8601=seconds)"
  printf "COMMAND:"
  printf " %q" "$@"
  echo
  echo
  "$@"
  command_status=$?
  echo
  echo "EXIT_STATUS: $command_status"
  if [[ "$command_status" -eq 0 ]]; then
    echo "RESULT: PASS"
  else
    echo "RESULT: FAIL"
  fi
  exit "$command_status"
} 2>&1 | tee "$log_file"

exit "${PIPESTATUS[0]}"
