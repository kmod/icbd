#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdint.h>
#include <fcntl.h>

#include "alloc.h"
#include "llvm_types.h"
#include "string.h"

double float_pow(double base, double exp) {
    return pow(base, exp);
}
