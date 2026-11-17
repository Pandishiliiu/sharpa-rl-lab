#!/usr/bin/env bash
set -uo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

tests=(
  "test_tactile_mock.py"
  "test_control_mock.py"
  "test_reset_mock.py"
  "test_cleanup_mock.py"
  "test_week2_contracts.py"
)

failed=0
echo "Week 2 offline regression"
echo "Repository: $REPO_ROOT"
echo "Python: $($PYTHON_BIN --version 2>&1)"

for test_file in "${tests[@]}"; do
  echo
  echo "RUN: $PYTHON_BIN $SCRIPT_DIR/$test_file"
  if "$PYTHON_BIN" "$SCRIPT_DIR/$test_file"; then
    echo "RESULT: PASS ($test_file)"
  else
    status=$?
    echo "RESULT: FAIL ($test_file, exit=$status)"
    failed=1
  fi
done

echo
if [[ "$failed" -eq 0 ]]; then
  echo "WEEK2_RESULT: PASS"
  exit 0
fi

echo "WEEK2_RESULT: FAIL"
exit 1
