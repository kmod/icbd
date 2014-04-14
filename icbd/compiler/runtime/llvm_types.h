#ifndef ICBD_LLVM_TYPES
#define ICBD_LLVM_TYPES

#include "stdbool.h"

typedef bool i1;
typedef int i32;
typedef long long i64;
typedef char i8;

typedef struct {
    i64 nrefs;
    bool closed;
    i64 fd;
} file;

typedef struct{
    i64 nrefs;
    i64 len;
    i8* ptr;
    i8 buf[0];
} string ;

typedef struct {
    i64 nrefs;
    string* str;
    i64 pos;
} striterator;

typedef struct{
    i64 nrefs;
    i64 capacity;
    i64 size;
    string** ptr;
} list_string ;

typedef struct{
    i64 nrefs;
    i64 capacity;
    i64 size;
    i64* ptr;
} list_i64;

typedef struct {
    i64 nrefs;
    i64 flags;
    i64 start;
    i64 end;
    i64 step;
} slice;

typedef struct {
    i64 nrefs;
    i64 elt0, elt1;
} tuple2_i64_i64;

extern list_string sys_argv;
extern string str_newline;
extern string str_space;
extern file sys_stdin;
extern file sys_stdout;
extern file sys_stderr;

void list_string_append(list_string*, string*);
void list_i64_append(list_i64*, i64);

tuple2_i64_i64* tuple2_i64_i64_ctor(i64, i64);

typedef struct type {
    i64 nrefs;
    string* name;
    struct type* parent;
} type;

#endif
