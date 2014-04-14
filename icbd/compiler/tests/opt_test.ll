; OPT=/home/kmod/icbd_deps/llvm-3.1.src/Release+Asserts/bin/opt LOAD=/home/kmod/icbd_deps/llvm-3.1.src/Release+Asserts/lib/icbd_passes.so OPTLEVEL="-inline-threshold=255 -basicaa -myaa -O3 -deadmalloc -unusedstore -mallocs_nonnull" python compiler/superopt.py kmod/opt_test.ll
target datalayout = "e-p:64:64:64-i1:8:8-i8:8:8-i16:16:16-i32:32:32-i64:64:64-f32:32:32-f64:64:64-v64:64:64-v128:128:128-a0:0:64-s0:64:64-f80:128:128-n8:16:32:64-S128"

declare i8* @malloc()

define i32 @neg(i32 %x) {
    %r = sub i32 0, %x
    ret i32 %r
}

define i64 @main(i32 %argc, i8** %argv) {
    %p = call i8* @malloc()
    %p1 = bitcast i8* %p to i32 (i32)**
    store i32 (i32)* @neg, i32 (i32)** %p1
    %p2 = bitcast i8* %p to i64 (i64)**
    ; %f = load i64 (i64)** %p2
    %f = bitcast i32 (i32)* @neg to i64 (i64)*
    %r = call i64 %f(i64 -10)
    ret i64 %r
}

define i8 @foo(i1 %br) {
    %p = call i8* @malloc()
    br i1 %br, label %l1, label %l2

l1:
    store i8 5, i8* %p
    br label %done

l2:
    store i8 7, i8* %p
    br label %done

done:
    %r = load i8* %p
    ret i8 %r
}

define i8 @foo2(i1 %br) {
    %p1 = call noalias i8* @malloc()
    %p2 = getelementptr i8* %p1, i32 1
    %p = select i1 %br, i8* %p1, i8* %p2
    store i8 5, i8* %p1
    store i8 7, i8* %p2
    %r = load i8* %p
    ret i8 %r
}
