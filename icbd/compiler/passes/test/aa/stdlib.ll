; RUN: opt -load ../../../../Release+Asserts/lib/icbd_passes.so -basicaa -myaa -gvn -o - -S < %s | FileCheck %s

target datalayout = "e-p:64:64:64-i1:8:8-i8:8:8-i16:16:16-i32:32:32-i64:64:64-f32:32:32-f64:64:64-v64:64:64-v128:128:128-a0:0:64-s0:64:64-f80:128:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

%string = type opaque
%file = type opaque
declare noalias i8* @get_ptr()
declare noalias %string* @mk_string()
declare noalias %file* @get_file()
declare void @file_write(%file* noalias nocapture, %string* noalias nocapture)

; CHECK: test_file_write
define i8 @test_file_write() nounwind {
    %p = call i8* @get_ptr()
    %s = call %string* @mk_string()
    %f = call %file* @get_file()
    store i8 5, i8* %p
    call void @file_write(%file* %f, %string* %s)
    %r = load i8* %p
; CHECK: ret i8 5
    ret i8 %r
}


