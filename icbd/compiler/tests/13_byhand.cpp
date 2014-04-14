#include "stdio.h"
#include <vector>
using namespace std;
typedef long long LL;

LL f_even(LL x) {
    return x;
}

LL f_odd(LL x) {
    return 0;
}

int main() {
    LL t = 0;
    for (LL i = 0; i < 200000000; i++) {
        LL (*x)(LL);
        if (i % 2 == 0) {
            x = &f_even;
        } else {
            x = &f_odd;
        }
        t += x(i);
    }
    printf("%lld\n", t);
    return 0;
}


