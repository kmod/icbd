#include <assert.h>

#include "alloc.h"
#include "util.h"
#include "slice.h"

slice* slice_alloc(i64 flags, i64 start, i64 end, i64 step) {
    slice* rtn = (slice*) my_malloc(sizeof(slice), "slice");
    rtn->nrefs = 1;
    rtn->flags = flags;
    rtn->start = start;
    rtn->end = end;
    rtn->step = step;
    return rtn;
}

void slice_decref(slice* self) {
    i64 nrefs = --self->nrefs;
    if (nrefs <= 0) {
        if (nrefs < 0) {
            raise_over_free_error();
        } else {
            my_free((void*)self, "slice");
        }
    }
}

void slice_incref(slice* self) {
    self->nrefs++;
}

void parse_slice(slice* s, i64 sz, slice_iterator* it) {
    i64 step = s->step;
    assert(step != 0);
    bool neg = (step < 0);

    i64 cur = s->start;
    if (!(s->flags & 1)) {
        cur = neg ? sz - 1 : 0;
    }
    if (cur < 0)
        cur = sz + cur;

    if (cur >= sz) {
        if (neg)
            cur = sz - 1;
        else
            cur = sz;
    }

    i64 end = s->end;
    if (end < 0)
        end = sz + end;
    if (!(s->flags & 2)) {
        end = neg ? -1 : sz;
    }
    if (end > sz)
        end = sz;

    it->cur = cur;
    it->end = end;
    it->step = step;
}

i64 sliceit_num_left(slice_iterator* it) {
    if (it->step < 0)
        return (it->cur - it->end - (it->step + 1)) / (-it->step);
    else
        return (it->end - it->cur + it->step - 1) / it->step;
}

i64 sliceit_get_next(slice_iterator* it) {
    if (it->step < 0) {
        if (it->cur <= it->end)
            return -1;
    } else {
        if (it->cur >= it->end)
            return -1;
    }
    assert(0 <= it->cur);

    i64 rtn = it->cur;
    it->cur += it->step;
    return rtn;
}
