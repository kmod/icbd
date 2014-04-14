#include <assert.h>
#include <fcntl.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "alloc.h"
#include "llvm_types.h"
#include "slice.h"
#include "util.h"

#define max(a, b) ((a)>(b)?(a):(b))
#define ENSURE(n) if (nwritten > buflen - (n)) {\
    buflen = max(buflen * 2, nwritten + (n)); \
    rtn = (string*)my_realloc((void*)rtn, sizeof(string) + buflen, "str_ensure");\
    out_ptr = &rtn->buf[nwritten]; \
    }

list_string* list_string_ctor();

void str_incref(string* self) {
    if (self == NULL)
        return;
    self->nrefs++;
}
void str_decref(string* self) {
    if (self == NULL)
        return;
    i64 nrefs = --self->nrefs;
    if (nrefs <= 0) {
        if (nrefs < 0)
            raise_over_free_error();
        else
            my_free((void*)self, "str");
    }
}
string* str_from_const(i8* buf, i64 len) {
    string* rtn = (string*)my_malloc(sizeof(string), "str");
    rtn->nrefs = 1;
    rtn->len = len;
    rtn->ptr = buf;
    return rtn;
}

string* str_copy(i8* buf, i64 len) {
    string* rtn = (string*)my_malloc(sizeof(string) + len, "str");
    rtn->nrefs = 1;
    rtn->len = len;
    rtn->ptr = &(rtn->buf[0]);
    memcpy(rtn->buf, buf, len);
    return rtn;
}

string* chr(i64 n) {
    string* rtn = (string*)my_malloc(sizeof(string) + 1, "str");
    rtn->nrefs = 1;
    rtn->len = 1;
    rtn->ptr = &(rtn->buf[0]);
    rtn->buf[0] = n;
    return rtn;
}

i64 ord(string* s) {
    assert(s->len == 1);
    return (i64)s->ptr[0];
}

list_string* str_split_1arg(string* self) {
    list_string* rtn = list_string_ctor();
    i64 n = self->len;
    i8* ptr = self->ptr;
    i8* prev = ptr;
    for (int i = 0; i < n; i++) {
        if (*ptr == ' ' || *ptr == '\t' || *ptr == '\n' || *ptr == '\r') {
            if (prev != ptr) {
                string* s = str_copy(prev, ptr-prev);
                list_string_append(rtn, s);
                str_decref(s);
            }
            prev = ptr+1;
        }
        ptr++;
    }
    if (prev != ptr) {
        string* s = str_copy(prev, ptr-prev);
        list_string_append(rtn, s);
        str_decref(s);
    }
    return rtn;
}

list_string* str_split(string* self, string* sep) {
    if (sep == NULL)
        return str_split_1arg(self);

    list_string* rtn = list_string_ctor();
    i64 n = self->len;
    i64 m = sep->len;
    assert(m > 0 && "empty separator");
    i8* ptr = self->ptr;
    i8* prev = ptr;
    // TODO switch to a linear-time algorithm if the separator is long enough
    for (int i = 0; i <= n - m; ) {
        if (memcmp(ptr, sep->ptr, m) == 0) {
            string* s = str_copy(prev, ptr-prev);
            list_string_append(rtn, s);
            str_decref(s);

            i += m;
            ptr += m;
            prev = ptr;
        } else {
            i++;
            ptr++;
        }
    }

    string* s = str_copy(prev, self->ptr + n - prev);
    list_string_append(rtn, s);
    str_decref(s);

    return rtn;
}

string* str_join(string* joiner, list_string* strings) {
    int sz = strings->size;
    if (sz == 0) {
        return str_from_const("", 0);
    }
    if (sz == 1) {
        strings->ptr[0]->nrefs++;
        return strings->ptr[0];
    }
    i64 len = joiner->len * (sz - 1);
    for (int i = 0; i < sz; i++) {
        len += strings->ptr[i]->len;
    }

    string* rtn = (string*)my_malloc(sizeof(string) + len, "str_join");
    rtn->nrefs = 1;
    rtn->len = len;
    rtn->ptr = &(rtn->buf[0]);
    i8* buf = rtn->ptr;

    for (int i = 0; i < sz; i++) {
        if (i > 0) {
            memcpy(buf, joiner->ptr, joiner->len);
            buf += joiner->len;
        }
        string* s = strings->ptr[i];
        memcpy(buf, s->ptr, s->len);
        buf += s->len;
    }

    assert(buf - rtn->ptr == len);

    return rtn;
}

i64 str_len(string* self) {
    return self->len;
}
i1 str_nonzero(string* self) {
    return self->len != 0;
}
i8* str_buf(string* self) {
    return self->ptr;
}
string* str_str(string* self) {
    if (self == NULL)
        return str_from_const("None", 4);

    str_incref(self);
    return self;
}
static bool _needs_escaping[256] = {
    true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, false, false, false, false, false, false, false, true, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, true, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true
};
static i8 hex[16] = "0123456789abcdef";
string* str_repr(string* self) {
    if (self == NULL)
        return str_from_const("None", 4);

    i64 buflen = self->len + 2;
    string* rtn = my_malloc(sizeof(string) + buflen, "str_repr");

    rtn->nrefs = 1;
    rtn->ptr = &(rtn->buf[0]);
    rtn->ptr[0] = '\'';
    i8* out_ptr = &rtn->buf[1];
    i64 nwritten = 1;

    for (int i = 0; i < self->len; i++) {
        i8 c = self->ptr[i];
        if (!_needs_escaping[c & 0xff]) {
            ENSURE(1);
            *out_ptr = c;
            out_ptr++;
            nwritten++;
        } else {
            i8 special = 0;
            switch (c) {
                case '\t':
                    special = 't';
                    break;
                case '\n':
                    special = 'n';
                    break;
                case '\r':
                    special = 'r';
                    break;
                case '\'':
                    special = '\'';
                    break;
                case '\"':
                    special = '\"';
                    break;
                case '\\':
                    special = '\\';
                    break;
            }
            if (special) {
                ENSURE(2);
                *(out_ptr++) = '\\';
                *(out_ptr++) = special;
                nwritten += 2;
            } else {
                ENSURE(4);
                *(out_ptr++) = '\\';
                *(out_ptr++) = 'x';
                *(out_ptr++) = hex[(c & 0xff) / 16];
                *(out_ptr++) = hex[(c & 0xff) % 16];
                nwritten += 4;
            }
        }
    }
    ENSURE(1);
    *out_ptr = '\'';
    nwritten++;
    rtn->len = nwritten;;
    rtn->ptr = &(rtn->buf[0]);
    return rtn;
}

string* str_add(string* lhs, string* rhs) {
    i64 newlen = lhs->len + rhs->len;
    string* rtn = (string*)my_malloc(sizeof(string) + newlen, "str_add");
    rtn->nrefs = 1;
    rtn->len = newlen;
    rtn->ptr = &(rtn->buf[0]);

    memcpy(rtn->ptr, lhs->ptr, lhs->len);
    memcpy(rtn->ptr + lhs->len, rhs->ptr, rhs->len);
    return rtn;
}

string* str_mul(string* lhs, i64 rhs) {
    if (rhs < 0)
        rhs = 0;

    i64 newlen = lhs->len * rhs;
    string* rtn = (string*)my_malloc(sizeof(string) + newlen, "str_mul");
    rtn->nrefs = 1;
    rtn->len = newlen;
    rtn->ptr = &(rtn->buf[0]);

    for (i64 i = 0; i < rhs; i++) {
        memcpy(rtn->ptr + i * lhs->len, lhs->ptr, lhs->len);
    }
    return rtn;
}

bool str_eq(string* lhs, string* rhs) {
    if (lhs->len != rhs->len)
        return 0;
    return !memcmp(lhs->ptr, rhs->ptr, lhs->len);
}
bool str_ne(string* lhs, string* rhs) {
    return !str_eq(lhs, rhs);
}

i64 min(i64 a, i64 b) {
    return (a<b) ? a : b;
}
static bool str_lc(string* lhs, string* rhs, bool eq) {
    i64 min_len = min(lhs->len, rhs->len);
    int r = memcmp(lhs->ptr, rhs->ptr, min_len);
    if (r < 0)
        return 1;
    else if (r > 0)
        return 0;
    else
        return lhs->len < rhs->len || (eq && (lhs->len == rhs->len));
}
bool str_lt(string* lhs, string* rhs) {
    return str_lc(lhs, rhs, false);
}
bool str_le(string* lhs, string* rhs) {
    return str_lc(lhs, rhs, true);
}

string* func_repr() {
    i8* buf = "<callable>";
    return str_from_const(buf, strlen(buf));
}

string* instance_repr(type* t) {
    i64 buflen = 20 + t->name->len;
    char* buf = my_malloc(buflen, "instance_repr");
    i64 len = snprintf(buf, buflen, "<%s object>", t->name->ptr);
    string* rtn = str_copy(buf, len);
    my_free(buf, "instance_repr");
    return rtn;
}

string* float_fmt(double, int, char);
string* str_format(string* fmt, ...) {
    va_list args;
    va_start(args, fmt);

    i8* fmt_ptr = fmt->ptr;
    i8* fmt_end_ptr = fmt_ptr + fmt->len;

    int buflen = 40;
    int nwritten = 0;
    string* rtn = (string*)my_malloc(sizeof(string) + buflen, "str_format");
    i8* out_ptr = &rtn->buf[0];

    while (fmt_ptr < fmt_end_ptr) {
        if (*fmt_ptr != '%') {
            ENSURE(1);
            *(out_ptr++) = *(fmt_ptr++);
            nwritten++;
        } else {
            fmt_ptr++;

            int nspace = 0;
            int ndot = 0;
            int mode = 0;
            while (true) {
                i8 c = *fmt_ptr;
                fmt_ptr++;

                if (c == ' ') {
                    mode = 1;
                } else if (c == '.') {
                    mode = 2;
                } else if ('0' <= c && c <= '9') {
                    assert(mode == 1 || mode == 2);
                    if (mode == 1) {
                        nspace = nspace * 10 + c - '0';
                    } else if (mode == 2) {
                        ndot = ndot * 10 + c - '0';
                    } else {
                        assert(0);
                    }
                } else if (c == '%') {
                    ENSURE(1 + nspace);
                    for (int i = 1; i < nspace; i++) {
                        *(out_ptr++) = ' ';
                        nwritten++;
                    }
                    *(out_ptr++) = '%';
                    nwritten++;
                    break;
                } else if (c == 's') {
                    string* s = va_arg(args, string*);
                    ENSURE(max(s->len, nspace));
                    for (int i = s->len; i < nspace; i++) {
                        *(out_ptr++) = ' ';
                        nwritten++;
                    }
                    memcpy(out_ptr, s->ptr, s->len);
                    out_ptr += s->len;
                    nwritten += s->len;
                    break;
                } else if (c == 'd') {
                    i64 n = va_arg(args, i64);
                    ENSURE(20);
                    int x = snprintf(out_ptr, 20, "%lld", n);
                    out_ptr += x;
                    nwritten += x;
                    break;
                } else if (c == 'f') {
                    double f = va_arg(args, double);
                    if (ndot == 0) ndot = 6;
                    string* s = float_fmt(f, ndot, 'f');
                    ENSURE(max(s->len, nspace));
                    for (int i = s->len; i < nspace; i++) {
                        *(out_ptr++) = ' ';
                        nwritten++;
                    }
                    memcpy(out_ptr, s->ptr, s->len);
                    out_ptr += s->len;
                    nwritten += s->len;
                    str_decref(s);
                    break;
                } else {
                    assert(false && "unsupported character");
                }
            }
        }
    }
    assert(fmt_ptr == fmt_end_ptr && "incomplete format");

    // string* foo = va_arg(args, string*);
    // foo->nrefs += 1;
    rtn->nrefs = 1;
    rtn->len = nwritten;
    rtn->ptr = &rtn->buf[0];
    return rtn;
}

string* str_getitem(string* s, i64 n) {
    assert(n >= 0);
    assert(n < s->len);
    return str_from_const(s->ptr + n, 1);
}

string* str_getitem_slice(string* self, slice* s) {
    i64 sz = self->len;

    slice_iterator it;
    parse_slice(s, sz, &it);
    i64 nelements = sliceit_num_left(&it);

    string* rtn = (string*) my_malloc(sizeof(string) + nelements, "str_getitem_slice");
    rtn->nrefs = 1;
    rtn->len = nelements;
    rtn->ptr = rtn->buf;

    int idx = 0;
    while (true) {
        i64 cur = sliceit_get_next(&it);
        if (cur == -1)
            break;

        assert(0 <= cur);
        assert(cur < sz);

        rtn->ptr[idx] = self->ptr[cur];
        idx++;
    }
    assert(idx == nelements);
    return rtn;
}

string* str_strip(string* self) {
    int start = 0;
    for (; start < self->len; start++) {
        char c = self->ptr[start];
        if (c != ' ' && c != '\t' && c != '\n' && c != '\r' && c != '\v')
            break;
    }
    if (start == self->len)
        return str_from_const(NULL, 0);

    int end = self->len - 1;
    for (; end >= 0; end--) {
        char c = self->ptr[end];
        if (c != ' ' && c != '\t' && c != '\n' && c != '\r' && c != '\v')
            break;
    }

    return str_copy(self->ptr + start, end - start + 1);
}

striterator* str_iter(string* self) {
    assert(self != NULL);
    striterator* rtn = (striterator*)my_malloc(sizeof(striterator), "striterator");
    rtn->nrefs = 1;
    rtn->str = self;
    rtn->pos = 0;
    self->nrefs++;
    return rtn;
}

i1 striterator_hasnext(striterator* self) {
    return self->pos < self->str->len;
}

string* striterator_next(striterator* self) {
    string* rtn = str_copy(self->str->ptr + self->pos, 1);
    self->pos++;
    return rtn;
}
