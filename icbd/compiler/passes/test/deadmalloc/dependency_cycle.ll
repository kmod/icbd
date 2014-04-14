; RUN: opt -load ../../../../Release+Asserts/lib/icbd_passes.so -deadmalloc -o - -S < %s | FileCheck %s

declare i8* @malloc(i64)
declare void @free(i8*)

%T = type {i64}
; CHECK: define i64 @main() {
define i64 @main() {
start:
    %_m = call i8* @malloc(i64 8)
    br label %loop

loop:
    %m = phi i8* [%_m, %start], [%m, %loop]
    br i1 1, label %return, label %loop

return:
    call void @free(i8* %m)
    ret i64 0
}


