; RUN: opt -load ../../../../Release+Asserts/lib/icbd_passes.so -deadmalloc -o - -S < %s | FileCheck %s

declare i8* @malloc(i64)
declare void @free(i8*)

%T = type {i64}
define i64 @main() {
start:
; CHECK-NOT: call i8* @malloc
; CHECK-NOT: call void @free
    %_m = call i8* @malloc(i64 8)
    %t = bitcast i8* %_m to %T*
    %ref_ptr = getelementptr %T* %t, i64 0, i32 0
    %x = add i64 0, 1
    store i64 %x, i64* %ref_ptr
    br label %loop

loop:
    %n = phi i64 [1000, %start], [%nn, %loop]
    %r = phi i64 [%x, %start], [%nr, %loop]
    %nn = sub i64 %n, 1
    %mul = mul i64 %r, %n
    %nr = add i64 %mul, %n
    %done = icmp eq i64 %n, 1
    br i1 %done, label %return, label %loop

return:
    call void @free(i8* %_m)
    ret i64 %nr
}

