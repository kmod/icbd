; RUN: opt -load ../../../../Release+Asserts/lib/icbd_passes.so -mallocs_nonnull -o - -S < %s | FileCheck %s

declare i8* @malloc(i64)
declare void @free(i8*)

; CHECK: good_test
define i64 @good_test() {
start:
; CHECK-NOT: br i1 %isnull
; CHECK: br i1 false
    %_m0 = call i8* @malloc(i64 8)
    %isnull = icmp eq i8* %_m0, null
    br i1 %isnull, label %done, label %do_free
do_free:
    call void @free(i8* %_m0)
    br label %done
done:
    ret i64 0
}

; CHECK: good_test
define i64 @good_test_swapped() {
start:
; CHECK-NOT: br i1 %isnull
; CHECK: br i1 false
    %_m1 = call i8* @malloc(i64 8)
    %isnull = icmp eq i8* null, %_m1
    br i1 %isnull, label %done, label %do_free
do_free:
    call void @free(i8* %_m1)
    br label %done
done:
    ret i64 0
}

; CHECK: bad_test
define i64 @bad_test() {
start:
; CHECK-NOT: br i1 false
; CHECK: br i1 %isnull
    %_m2 = call i8* @malloc(i64 8)
    %p = inttoptr i64 123456 to i8*
    %isnull = icmp eq i8* %_m2, %p
    br i1 %isnull, label %done, label %do_free
do_free:
    call void @free(i8* %_m2)
    br label %done
done:
    ret i64 0
}

; CHECK: bitcast_test
define i64 @bitcast_test() {
    %_m3 = call i8* @malloc(i64 8)
    %_m4 = bitcast i8* %_m3 to i64*
    %isnull = icmp eq i64* %_m4, null
; CHECK-NOT: br i1 %isnull
; CHECK: br i1 false
    br i1 %isnull, label %done, label %do_free
do_free:
    call void @free(i8* %_m3)
    br label %done
done:
    ret i64 0
}
