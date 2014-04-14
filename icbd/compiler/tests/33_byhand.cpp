#include <cstdio>

typedef long long LL;

LL fib(int n) {
    if (n <= 1)
        return n;
    return fib(n-1) + fib(n-2);
}

int main() {
    LL r = fib(38);
    printf("%lld\n", r);
}
