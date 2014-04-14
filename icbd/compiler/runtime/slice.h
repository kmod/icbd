#ifndef ICBD_SLICE
#define ICBD_SLICE

#include "llvm_types.h"

typedef struct {
    i64 cur, end, step;
} slice_iterator;

void parse_slice(slice* s, i64 sz, slice_iterator* it);
i64 sliceit_num_left(slice_iterator* it);
i64 sliceit_get_next(slice_iterator* it);

#endif
