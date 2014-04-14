; RUN: opt -load ../../../../Release+Asserts/lib/icbd_passes.so -basicaa -unusedstore -o - -S < %s | FileCheck %s

target datalayout = "e-p:64:64:64-i1:8:8-i8:8:8-i16:16:16-i32:32:32-i64:64:64-f32:32:32-f64:64:64-v64:64:64-v128:128:128-a0:0:64-s0:64:64-f80:128:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

@str_2 = internal constant [6 x i8] c"%.*s\0A\00"

declare noalias i8* @my_malloc(i64) nounwind

declare void @my_free(i8* nocapture) nounwind

declare void @external(i8*)

; CHECK: trivial
; CHECK-NOT: store
define void @trivial() {
    ; Include this as a sanity test to make sure it's turned on
    %m = call i8* @my_malloc(i64 64)
    store i8 1, i8* %m
    ret void
}


; CHECK: arg_test
; CHECK: store
define void @arg_test(i64* %p) {
    store i64 0, i64* %p
    ret void
}

; CHECK: ret_test
; CHECK: store
define i8* @ret_test(i64* %p) {
    %m = call i8* @my_malloc(i64 64)
    store i8 1, i8* %m
    ret i8* %m
}

; CHECK: global_test
; CHECK: store
@global_int = global i64 5
define void @global_test() {
    store i64 6, i64* @global_int
    ret void
}

; CHECK: call_test
; CHECK: store
define void @call_test() {
    %m = call i8* @my_malloc(i64 64)
    call void @external(i8* %m)
    store i8 1, i8* %m
    ret void
}

; CHECK: load_test
; CHECK: store
define i8 @load_test() {
    %m = call i8* @my_malloc(i64 64)
    store i8 1, i8* %m
    %r = load i8* %m
    ret i8 %r
}

; CHECK: stored_test
; CHECK: store i8 1
define void @stored_test(i8** %p) {
    %m = call i8* @my_malloc(i64 64)
    store i8 1, i8* %m
    store i8* %m, i8** %p
    ret void
}

; test loads and phis
