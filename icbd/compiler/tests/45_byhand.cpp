#include <cstdio>

typedef long long LL;

int main() {
    LL a = 1;
    LL b = 2;

    for (LL i = 0; i < 123456789; i++) {
        LL t = a;
        a = b;
        b = t;
    }
    printf("%lld %lld\n", a, b);
    return 0;
}
