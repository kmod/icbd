#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
//#include <vector>

#include "alloc.h"

#define ERR *((int*)NULL)
//#define REALMALLOC

LL n_allocs = 0;

void* my_malloc(LL sz, char* t) {
    void* r = malloc(sz);
    assert(r);
#ifndef REALMALLOC
    n_allocs++;
    printf("malloc'd %s %lld bytes at %p; %lld allocs\n", t, sz, r, n_allocs);
#endif
    return r;
}

void* my_realloc(void* ptr, LL size, char* t) {
#ifndef REALMALLOC
    printf("reallocating %s %p to size %lld\n", t, ptr, size);
#endif
    void* rtn = realloc(ptr, size);
    //printf("got %p\n", rtn);
    return rtn;
}

void my_free(void* ptr, char* t) {
#ifndef REALMALLOC
    n_allocs--;
    printf("freeing %s %p; %lld allocs\n", t, ptr, n_allocs);
#endif
    free(ptr);
}

