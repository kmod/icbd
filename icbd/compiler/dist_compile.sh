#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 FN ARGS"
    exit 3
fi

FN=$(readlink -f "$1")
shift
ARGS=$@
OUT_FN="${FN}icbd"
DEP_FN="${FN}d"

GCC=gcc

compile() {
    _compile() {
        PYTHONPATH=icbd.egg python -m icbd.compiler.compile -p stdlib/compiler -t stdlib/type_mocks "$FN" $TEMPDIR/gen.ll $TEMPDIR/cgen.c $TEMPDIR/gen.d || return 1
        /home/kmod/icbd_deps/llvm-3.1.src/Release+Asserts/bin/clang -Wall -emit-llvm -Werror -iquote runtime_includes $TEMPDIR/cgen.c -o $TEMPDIR/cgen.bc -c || return 1
        ./llvm-link $TEMPDIR/gen.ll $TEMPDIR/cgen.bc runtime_nodebug.bc -o $TEMPDIR/linked.bc || return 1
        ./llc $TEMPDIR/linked.bc -o $TEMPDIR/linked.s || return 1
        $GCC -lm $TEMPDIR/linked.s -o $TEMPDIR/out || return 1
        cp $TEMPDIR/out "$OUT_FN" || return 1
        cp $TEMPDIR/gen.d "$DEP_FN" || return 1
    }

    _compile
    EXIT=$?
    rm -rf $TEMPDIR
    return $EXIT
}

TEMPDIR=$(mktemp -d)

OUT_OF_DATE=

escape() {
    sed 's/\\ /!Q#/g'
}
unescape() {
    sed 's/!Q#/ /g'
}

if [[ ! -e "$DEP_FN" || ! -e "$OUT_FN" ]]; then
    OUT_OF_DATE=1
else
    (head -n1 "$DEP_FN" | grep -q "!Q#" && echo "uh oh") && exit 1
    DEPS=$(head -n1 "$DEP_FN" | escape | cut -f2- -d ' ')
    for d in $DEPS; do
        d=$(echo $d | unescape)
        if [ ! -e "$d" ]; then
            echo "error: $d does not exist"
            exit 2
        fi
        if [[ "$d" -nt "$OUT_FN" ]]; then
            OUT_OF_DATE=1
            break
        fi
    done
fi

if [[ -n "$OUT_OF_DATE" ]]; then
    pushd $(dirname $0) >/dev/null
    compile || exit $?
    popd >/dev/null
fi
"$OUT_FN" $ARGS
