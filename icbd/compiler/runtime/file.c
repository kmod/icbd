#include <assert.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdint.h>
#include <fcntl.h>

#include "alloc.h"
#include "llvm_types.h"
#include "string.h"
#include "util.h"

file* file_alloc() {
    file* r = (file*) my_malloc(sizeof(file), "file");
    r->nrefs = 1;
    return r;
}

void file_init(file* self, string* path) {
    i8* buf = my_malloc(path->len + 1, "filename");
    memcpy(buf, path->ptr, path->len);
    buf[path->len] = 0;
    i32 fd = open(buf, O_RDONLY, 0644);
    my_free(buf, "filename");

    self->fd = fd;
    self->closed = false;
}

string* file_readline(file* self) {
    int capacity = 80;
    string* rtn = (string*) my_malloc(capacity + sizeof(string), "file_readline");
    rtn->nrefs = 1;

    rtn->ptr = &(rtn->buf[0]);

    i8* ptr = rtn->ptr;
    int total_read = 0;
    while (true) {
        i64 nread = read(self->fd, ptr, 1);
        assert(nread >= 0 && "should throw an exception");
        if (nread == 0) {
            // TODO is this right?
            rtn->len = 0;
            return rtn;
        }

        i8 c = *ptr;
        ptr += 1;
        total_read += 1;
        if (c == '\n')
            break;
        if (total_read == capacity) {
            capacity *= 2;
            rtn = (string*)my_realloc((void*)rtn, capacity + sizeof(string), "file_readline");
            rtn->ptr = &(rtn->buf[0]);
            ptr = rtn->ptr + total_read;
        }
    }
    rtn->len = total_read;
    //printf("%s", rtn->ptr);
    return rtn;
}

string* file_read(file* f, i64 n) {
    string* rtn = (string*)my_malloc(sizeof(string) + n, "file_read");
    rtn->nrefs = 1;
    rtn->ptr = &(rtn->buf[0]);

    i64 nread = read(f->fd, rtn->ptr, n);
    assert(nread >= 0 && "should throw an exception");
    rtn->len = nread;
    return rtn;
}

void file_write(file* f, string* s) {
    i64 written = 0;
    i64 len = s->len;
    while (written < len) {
        i64 new = write(f->fd, s->ptr + written, len - written);
        assert(new >= 0 && "should throw an exception");
        if (new <= 0)
            break;
        written += new;
    }
}

static file* _open(string* path, int flags) {
    i8* buf = my_malloc(path->len + 1, "file_open_fn");
    memcpy(buf, path->ptr, path->len);
    buf[path->len] = 0;
    i32 fd = open(buf, flags, 0644);
    my_free(buf, "file_open");

    file* rtn = (file*)my_malloc(sizeof(file), "file_open");
    rtn->nrefs = 1;
    rtn->closed = 0;
    rtn->fd = fd;

    if (fd == -1) {
        printf("error opening file! %d\n", errno);
        assert(0 && "couldn't open file");
    }
    return rtn;
}

file* file_open(string* path) {
    return _open(path, O_RDONLY);
}

file* file_open2(string* path, string* mode) {
    i32 flags = O_RDONLY;
    for (int i = 0; i < mode->len; i++) {
        i8 c = mode->ptr[i];
        if (c == 'w') {
            flags = O_WRONLY | O_CREAT | O_TRUNC;
            break;
        } else if (c == 'r') {
            flags = O_RDONLY;
            break;
        }
    }

    return _open(path, flags);
}

void file_close(file* f) {
    close(f->fd);
    f->closed = true;
}

void file_incref(file* self) {
    if (self == NULL)
        return;
    self->nrefs++;
}
void file_decref(file* self) {
    if (self == NULL)
        return;
    i64 nrefs = --self->nrefs;
    if (nrefs <= 0) {
        if (nrefs < 0) {
            raise_over_free_error();
        } else {
            if (!self->closed)
                close(self->fd);
            my_free((void*)self, "file");
        }
    }
}

string* file_repr(file* self) {
    return str_from_const("<file>", 6);
}

void file_flush(file* self) {
    // Everything is unbuffered right now
}
