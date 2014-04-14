#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdint.h>
#include <fcntl.h>

#include "alloc.h"
#include "llvm_types.h"

string* bool_repr(i1 b) {
    if (b) {
        string* rtn = (string*)my_malloc(sizeof(string), "bool_repr");
        rtn->nrefs = 1;
        rtn->len = 4;
        rtn->ptr = "True";
        return rtn;
    } else {
        string* rtn = (string*)my_malloc(sizeof(string), "bool_repr");
        rtn->nrefs = 1;
        rtn->len = 5;
        rtn->ptr = "False";
        return rtn;
    }
}
