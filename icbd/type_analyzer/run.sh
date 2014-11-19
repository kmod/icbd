#!/bin/bash

# Helper script for quickly running analyses on different codebases
# Normally dumps to the /tmp directory, but with the '-w' ("web") flag,
# it will put everything into /var/www and alter the generated links
# to be suitable for running in a web server.
#
# To set up a new codebase, just add another 'elif' line with the name of the codebase.
# The source directory is the last argument on the line.
# Add a -I argument for each directory you want to be on the 'python path'
# -c can be used to add custom plugins
# See analyze_all.py for a fuller set of arguments.

cd $(dirname $0)/../..

NAME="$1"
COMMON_OPTS="-I stdlib/python2.5_small"

if [ "$2" = "-w" ]; then
    COMMON_OPTS="$COMMON_OPTS -o /var/www/$NAME -p 2"
fi

if [ -z "$NAME" ]; then
    echo "Usage: $0 NAME [-w]"
elif [ "$NAME" = "demo" ]; then
    python -m icbd.type_analyzer.analyze_all $COMMON_OPTS demos
elif [ "$NAME" = "icbd" ]; then
    python -m icbd.type_analyzer.analyze_all $COMMON_OPTS -I . -E icbd/type_analyzer/tests -E icbd/compiler/benchmarks -E icbd/compiler/tests -I stdlib/type_mocks icbd
elif [ "$NAME" = "bench" ]; then
    python -m icbd.type_analyzer.analyze_all $COMMON_OPTS -I . -E icbd/type_analyzer/tests -E icbd/compiler/benchmarks -E icbd/compiler/tests -I stdlib/type_mocks -n icbd
else
    echo "No project set up with name '$NAME'"
fi
