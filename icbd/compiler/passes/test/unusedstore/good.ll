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
    %m = call i8* @my_malloc(i64 64)
    store i8 1, i8* %m
    ret void
}

; CHECK: freed
; CHECK-NOT: store
define void @freed() {
    %m = call i8* @my_malloc(i64 64)
    store i8 1, i8* %m
    call void @my_free(i8* %m)
    ret void
}

; CHECK: overwrites
; CHECK-NOT: store i8
; CHECK: store i64
; CHECK-NOT: store i8
define i32 @overwrites() {
    %m = call i8* @my_malloc(i64 64)
    %p1 = getelementptr inbounds i8* %m, i64 6
    %p2 = bitcast i8* %m to i64*
    store i8 1, i8* %p1
    store i64 -1, i64* %p2
    %p = bitcast i8* %m to i32*
    %r = load i32* %p
    ret i32 %r
}

; CHECK: gep_test
; CHECK-NOT: store
define i8* @gep_test(i64* %p) {
    %m = call i8* @my_malloc(i64 64)
    store i8 1, i8* %m
    %r = getelementptr i8* %m, i64 24
    ret i8* %r
}

; CHECK: preload_test
; CHECK-NOT: store
define i8 @preload_test() {
    %m = call i8* @my_malloc(i64 64)
    %r = load i8* %m
    store i8 1, i8* %m
    ret i8 %r
}

; CHECK: cfg_test
; CHECK-NOT: store
define i8* @cfg_test(i1 %b) {
    %m = call i8* @my_malloc(i64 64)
    br i1 %b, label %yes, label %no

yes:
    %r = load i8* %m
    call void @external(i8* %m)
    ret i8* %m

no:
    store i8 5, i8* %m
    ret i8* null
}

; test loads and phis
