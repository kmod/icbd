; RUN: opt -load ../../../../Release+Asserts/lib/icbd_passes.so -basicaa -myaa -gvn -o - -S < %s | FileCheck %s
; XFAIL:
target datalayout = "e-p:64:64:64-i1:8:8-i8:8:8-i16:16:16-i32:32:32-i64:64:64-f32:32:32-f64:64:64-v64:64:64-v128:128:128-a0:0:64-s0:64:64-f80:128:128-n8:16:32:64-S128"

%list_i64 = type { i64, i64, i64, i64* }
%f_0 = type { i64, void (%f_0*, i64)*, void (%f_0*)* }

declare noalias i8* @my_malloc(i64) nounwind

declare void @init_runtime()

declare i64 @int_mod(i64, i64)

define i64 @main() {
func_start:
  tail call void @init_runtime()
  %list_alloc.i = tail call noalias i8* @my_malloc(i64 32) nounwind
  %ref_ptr.i2 = bitcast i8* %list_alloc.i to i64*
  store i64 1, i64* %ref_ptr.i2, align 8
  %list_alloc.i3 = tail call noalias i8* @my_malloc(i64 32) nounwind
  %ref_ptr.i7 = bitcast i8* %list_alloc.i3 to i64*
  store i64 1, i64* %ref_ptr.i7, align 8
  %_tmp_3 = tail call i64 @int_mod(i64 5, i64 2)
  %r.i = icmp eq i64 %_tmp_3, 0
  br i1 %r.i, label %block5, label %block4

block4:                                           ; preds = %func_start
  store i64 2, i64* %ref_ptr.i2, align 8
  %alloc.i11 = tail call noalias i8* @my_malloc(i64 40) nounwind
  %func_ptr.i = getelementptr i8* %alloc.i11, i64 32
  %0 = bitcast i8* %func_ptr.i to void (%list_i64*, i64)**
  store void (%list_i64*, i64)* @list_i64_append, void (%list_i64*, i64)** %0, align 8
  br label %block6

block5:                                           ; preds = %func_start
  store i64 2, i64* %ref_ptr.i7, align 8
  %alloc.i22 = tail call noalias i8* @my_malloc(i64 40) nounwind
  %func_ptr.i28 = getelementptr i8* %alloc.i22, i64 32
  %1 = bitcast i8* %func_ptr.i28 to void (%list_i64*, i64)**
  store void (%list_i64*, i64)* @list_i64_append, void (%list_i64*, i64)** %1, align 8
  br label %block6

block6:                                           ; preds = %block5, %block4
  %_a_6_0.in = phi i8* [ %alloc.i11, %block4 ], [ %alloc.i22, %block5 ]
  %f_p.i = getelementptr inbounds i8* %_a_6_0.in, i64 32
  %2 = bitcast i8* %f_p.i to void (%f_0*, i64)**
  %3 = load void (%f_0*, i64)** %2, align 8
  %f.i = bitcast void (%f_0*, i64)* %3 to void (%list_i64*, i64)*
  tail call void %f.i(%list_i64* null, i64 1)
  ret i64 0
}

define internal void @list_i64_append(%list_i64* nocapture %self, i64 %elt) nounwind readnone {
  ret void
}
