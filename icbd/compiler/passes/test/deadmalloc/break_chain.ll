; RUN: opt -load ../../../../Release+Asserts/lib/icbd_passes.so -deadmalloc -o - -S < %s | FileCheck %s

declare i8* @malloc(i64)
declare void @free(i8*)

%T = type {i64}
define i64 @main() {
start:
; CHECK: call i8* @malloc
; CHECK: call i8* @malloc
; CHECK: call void @free
    %_m = call i8* @malloc(i64 8)
    br i1 1, label %int, label %loop

int:
    %_m2 = call i8* @malloc(i64 16)
    br label %loop

loop:
    %m = phi i8* [%_m, %start], [%_m2, %int]
    call void @free(i8* %m)
    ret i64 0
}

