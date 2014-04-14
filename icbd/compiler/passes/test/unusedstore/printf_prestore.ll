; RUN: opt -load ../../../../Release+Asserts/lib/icbd_passes.so -basicaa -myaa -unusedstore -o - -S < %s | FileCheck %s

target datalayout = "e-p:64:64:64-i1:8:8-i8:8:8-i16:16:16-i32:32:32-i64:64:64-f32:32:32-f64:64:64-v64:64:64-v128:128:128-a0:0:64-s0:64:64-f80:128:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

@str_2 = internal constant [6 x i8] c"%.*s\0A\00"

declare i32 @printf(i8* noalias nocapture, ...) nounwind

declare noalias i8* @my_malloc(i64) nounwind

declare void @my_free(i8* nocapture) nounwind

define i64 @main() nounwind {
str_decref.exit34:
  %call.i6 = tail call i8* @my_malloc(i64 25) nounwind

; CHECK-NOT: store i64 1234
  ; this is unnecessary:
  %nrefs.i7 = bitcast i8* %call.i6 to i64*
  store i64 1234, i64* %nrefs.i7, align 8

  %buf.i = getelementptr inbounds i8* %call.i6, i64 24
  store i8 97, i8* %buf.i, align 1

  %0 = tail call i32 (i8*, ...)* @printf(i8* noalias nocapture getelementptr inbounds ([6 x i8]* @str_2, i64 0, i64 0), i64 1, i8* %buf.i)
  tail call void @my_free(i8* %call.i6) nounwind

  ret i64 0
}

