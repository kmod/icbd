; RUN: opt -load ../../../../Release+Asserts/lib/icbd_passes.so -basicaa -myaa -gvn -o - -S < %s | FileCheck %s

target datalayout = "e-p:64:64:64-i1:8:8-i8:8:8-i16:16:16-i32:32:32-i64:64:64-f32:32:32-f64:64:64-v64:64:64-v128:128:128-a0:0:64-s0:64:64-f80:128:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

@str_0 = internal constant [6 x i8] c"%.*s\0A\00"

declare i32 @printf(i8* noalias nocapture, ...) nounwind

declare noalias i8* @my_malloc(i64) nounwind

declare void @my_free(i8* nocapture) nounwind

define i64 @main() nounwind {
closure0_decref.exit:
  %call.i = tail call noalias i8* @my_malloc(i64 64) nounwind
  %nrefs.i = bitcast i8* %call.i to i64*
  %buf.i = getelementptr inbounds i8* %call.i, i64 24
  %ptr.i = getelementptr inbounds i8* %call.i, i64 16
  %0 = bitcast i8* %ptr.i to i8**
  store i8* %buf.i, i8** %0, align 8
  store i64 1, i64* %nrefs.i, align 8
  %1 = tail call i32 (i8*, ...)* @printf(i8* noalias nocapture getelementptr inbounds ([6 x i8]* @str_0, i64 0, i64 0)), !nowrite !{i64 0}
; CHECK-NOT: load
  %2 = load i64* %nrefs.i, align 8
  tail call void @my_free(i8* %call.i) nounwind
  ret i64 %2
}

