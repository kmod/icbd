#include <assert.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "alloc.h"
#include "llvm_types.h"

i64 int_mod(i64 lhs, i64 rhs) {
    if (lhs < 0 && rhs > 0)
        return ((lhs + 1) % rhs) + (rhs - 1);
    if (lhs > 0 && rhs < 0)
        return ((lhs - 1) % rhs) + (rhs + 1);
    return lhs % rhs;
}

i64 int_div(i64 lhs, i64 rhs) {
    if (lhs < 0 && rhs > 0)
        return (lhs - rhs + 1) / rhs;
    if (lhs > 0 && rhs < 0)
        return (lhs - rhs - 1) / rhs;
    return lhs / rhs;
}

i64 int_pow(i64 lhs, i64 rhs) {
    i64 rtn = 1, curpow = lhs;
    while (rhs) {
        if (rhs & 1)
            rtn *= curpow;
        curpow *= curpow;
        rhs >>= 1;
    }
    return rtn;
}

string* int_repr(i64 x) {
    string* rtn = (string*)my_malloc(sizeof(string) + 40, "int_repr");
    rtn->nrefs = 1;
    rtn->ptr = &(rtn->buf[0]);
    rtn->len = snprintf(rtn->ptr, 40, "%lld", x);
    return rtn;
}

i64 int_(string* s) {
    i64 total = 0;
    i64 n = s->len;
    bool started = false;
    for (int i = 0; i < n; i++) {
        i8 c = s->ptr[i];
        if (!started && (c == ' ' || c == '\t'))
            continue;
        if (c >= '0' && c <= '9') {
            started = true;
            total = 10 * total + (c - '0');
        } else {
            break;
        }
    }
    return total;
}

i64 int_max(i64 a, i64 b) {
    return (a > b) ? a : b;
}

i64 int_min(i64 a, i64 b) {
    return (a < b) ? a : b;
}

double float_min(double a, double b) {
    return a < b ? a : b;
}

double float_max(double a, double b) {
    return a > b ? a : b;
}

string* float_fmt(double x, int precision, char code) {
    string* rtn = (string*)my_malloc(sizeof(string) + 40, "float_fmt");
    rtn->nrefs = 1;
    rtn->ptr = &(rtn->buf[0]);
    i8* buf = rtn->ptr;

    char fmt[5] = "%.*g";
    fmt[3] = code;
    int n = snprintf(buf, 40, fmt, precision, x);
    rtn->len = n;

    int dot = -1;
    int exp = -1;
    int first = -1;
    for (int i = 0; i < n; i++) {
        i8 c = buf[i];
        if (c == '.') {
            dot = i;
        } else if (c == 'e') {
            exp = i;
        } else if (first == -1 && c >= '0' && c <= '9') {
            first = i;
        }
    }

    if (dot == -1 && exp == -1) {
        if (n == precision) {
            memmove(buf + first + 2, buf + first + 1, (n - first - 1));
            buf[first + 1] = '.';
            exp = n + 1;
            int exp_digs = snprintf(buf + n + 1, 5, "e%+.02d", (n-first-1));
            n += exp_digs + 1;
            rtn->len = n;
            dot = 1;
        } else {
            buf[n] = '.';
            buf[n+1] = '0';
            rtn->len += 2;
            return rtn;
        }
    }

    if (exp != -1 && dot == -1) {
        return rtn;
    }

    assert(dot != -1);

    int start, end;
    if (exp) {
        start = exp - 1;
        end = dot;
    } else {
        start = n - 1;
        end = dot + 2;
    }
    for (int i = start; i >= end; i--) {
        if (buf[i] == '0') {
            memmove(buf + i, buf + i + 1, n - i - 1);
            n--;
            rtn->len--;
        } else if (buf[i] == '.') {
            memmove(buf + i, buf + i + 1, n - i - 1);
            n--;
            rtn->len--;
            break;
        } else {
            break;
        }
    }
    return rtn;
}

// This should match cPython's PyOS_double_to_string (though hardcoded for the default values)
string* float_str(double x) {
    return float_fmt(x, 12, 'g');
}

string* float_repr(double x) {
    // TODO I don't think this is exactly the same
    return float_fmt(x, 16, 'g');
}

double float_(i64 n) {
    return (double)n;
}

double float_abs(double x) {
    if (x > 0)
        return x;
    return -x;
}

i64 int_abs(i64 x) {
    if (x > 0)
        return x;
    return -x;
}

tuple2_i64_i64* divmod(i64 x, i64 y) {
    i64 mod = int_mod(x, y);
    i64 div = (x - mod) / y;
    return tuple2_i64_i64_ctor(div, mod);
}
