#!/bin/bash

set -eu
shopt -s nullglob

cd $(dirname $0)

PASSED=0
TOTAL=0
for i in *tests.py; do
    TOTAL=$((TOTAL + 1))
    if python $i >/dev/null 2>&1; then
        PASSED=$((PASSED + 1))
        echo -en '\033[32m';
    else
        echo -en '\033[31m';
    fi
    echo $i;
    echo -en '\033[0m'
done

for i in tests/*.py; do
    TOTAL=$((TOTAL + 1))
    if PYTHONPATH=../.. python test.py $i --nooutput >/dev/null 2>&1; then
        PASSED=$((PASSED + 1))
        echo -en '\033[32m';
    else
        echo -en '\033[31m';
    fi
    echo $i;
    echo -en '\033[0m'
done

echo "$PASSED/$TOTAL passed"
