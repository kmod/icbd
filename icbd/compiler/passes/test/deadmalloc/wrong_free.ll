; RUN: opt -load ../../../../Release+Asserts/lib/icbd_passes.so -deadmalloc -o - -S < %s | FileCheck %s

declare i8* @malloc(i64)
declare void @free(i8*)

%T = type {i64}
define i64 @main() {
start:
; CHECK: call i8* @malloc
; CHECK: call void @free
    %_m = call i8* @malloc(i64 8)
    %g = getelementptr i8* %_m, i64 1
    call void @free(i8* %g)
    ret i64 0
}



