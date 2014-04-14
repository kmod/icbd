#!/bin/bash

set -eu

cd $(dirname $0)

PYTHONPATH=. icbd/compiler/closure_analyzer_unittests.py

# make -C icbd/compiler all23 -k -j4 OPTLEVEL= >/dev/null 2>&1 || true
icbd/compiler/tester.py

icbd/type_analyzer/test_all.sh
echo "(38 expected)"
