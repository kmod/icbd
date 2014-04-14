#include "llvm_types.h"

string* str_from_const(i8*, i64);
i1 striterator_hasnext(striterator* self);
string* striterator_next(striterator* self);
void striterator_decref(striterator*);
