// To make it not complain about nanosleep:
#define _POSIX_C_SOURCE 199309L

#include <assert.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <time.h>
#include <unistd.h>

#include "alloc.h"
#include "llvm_types.h"
#include "string.h"
#include "util.h"

list_i64* list_i64_ctor();
void list_i64_append(list_i64*, i64);

void str_incref(string*);
void str_decref(string*);
string* str_copy(char*, i64);
i64 list_string_len(list_string*);

list_i64* range(i64 end) {
    list_i64* rtn = list_i64_ctor();
    for (i64 i = 0; i < end; i++) {
        list_i64_append(rtn, i);
    }
    return rtn;
}

double time_time() {
    struct timeval now;
    gettimeofday(&now, NULL);
    return now.tv_sec + .000001 * now.tv_usec;
}

double time_clock() {
    return 1.0 * clock() / CLOCKS_PER_SEC;
}

void time_sleep(double d) {
    // TODO: err if d<0 or > max uint32

    struct timespec s;
    s.tv_sec = (unsigned int)d;
    s.tv_nsec = 1000000000 * (d - s.tv_sec);
    nanosleep(&s, NULL);
}

// Runtime hooks
void init_runtime(i64 argc, i8** argv) {
    //printf("Runtime initialized\n");
    sys_argv.nrefs = 1;
    sys_argv.capacity = 10;
    sys_argv.size = 0;
    sys_argv.ptr = (string**)my_malloc(10 * sizeof(string*), "sys.argv");

    for (int i = 0; i < argc; i++) {
        string* s = str_from_const(argv[i], strlen(argv[i]));
        list_string_append(&sys_argv, s);
        str_decref(s);
    }

    sys_stdin.nrefs = 1;
    sys_stdin.closed = 0;
    sys_stdin.fd = STDIN_FILENO;
    sys_stdout.nrefs = 1;
    sys_stdout.closed = 0;
    sys_stdout.fd = STDOUT_FILENO;
    sys_stderr.nrefs = 1;
    sys_stderr.closed = 0;
    sys_stderr.fd = STDERR_FILENO;

    str_newline.nrefs = 1;
    str_newline.len = 1;
    str_newline.ptr = "\n";
    str_space.nrefs = 1;
    str_space.len = 1;
    str_space.ptr = " ";
}

void print_space_if_necessary(string* last) {
    if (last->len == 0 || last->ptr[last->len - 1] != '\n') {
        write(STDOUT_FILENO, " ", 1);
    }
}

void teardown_runtime() {
    int n = list_string_len(&sys_argv);
    for (int i = 0; i < n; i++) {
        str_decref(sys_argv.ptr[i]);
    }
    my_free(sys_argv.ptr, "sys.argv");
    //printf("Runtime cleaned up\n");

    if (n_allocs != 0) {
        printf("Warning: %lld allocs did not get freed\n", n_allocs);
    }
}

void raise_index_error(i64 idx) {
    printf("IndexError: %lld\n", idx);
    exit(-1);
}

void raise_over_free_error() {
    printf("Internal error: decremented a refcount to below 0!\n");
    exit(-2);
}

void raise_called_none_error() {
    printf("Error: called None!\n");
    exit(-6);
}

void check_unpacking_length(i64 expected, i64 gotten) {
    if (gotten > expected) {
        printf("Too many values to unpack: expected %lld but got %lld\n", expected, gotten);
        exit(-3);
    } else if (gotten < expected) {
        printf("Not enough values to unpack: expected %lld but got %lld\n", expected, gotten);
        exit(-3);
    }
}

void assert_(i1 condition) {
    if (!condition) {
        printf("AssertionError!\n");
        exit(-4);
    }
}

string* none_repr(void* n) {
    assert(n == NULL);
    return str_from_const("None", 4);
}

i1 none_eq(void* lhs, void* rhs) {
    assert(lhs == NULL);
    assert(rhs == NULL);
    return 1;
}

// These methods all have an underscore at the end of their name since it's too much work
// to prevent the compiler from emitting the normal versions of these methods,
// but we still want to override them.

string* type_repr_(type* c) {
    i64 buflen = 20 + c->name->len;
    char* buf = my_malloc(buflen, "classname");
    i64 len = snprintf(buf, buflen, "<class '%s'>", c->name->ptr);
    string* rtn = str_copy(buf, len);
    my_free(buf, "classname");
    return rtn;
}

// All typeobjects are currently global+static, so they don't need refcounting
void type_incref_(type* c) {}
void type_decref_(type* c) {}
