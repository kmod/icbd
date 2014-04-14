; RUN: opt -load ../../../../Release+Asserts/lib/icbd_passes.so -deadmalloc -o - -S < %s | FileCheck %s

declare i8* @malloc(i64)
declare void @free(i8*)

%T = type {i64}
define i64 @main() {
start:
; CHECK-NOT: call i8* @malloc
; CHECK-NOT: call void @free
    %_m = call i8* @malloc(i64 8)

    br i1 1, label %yes, label %no

yes:
    call void @free(i8* %_m)
    br label %no

no:
    ret i64 0
}



