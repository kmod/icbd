#include "stdio.h"
typedef long long LL;
int main() {
    LL total = 0;
    for (LL i = 2; i < 1000000; i++) {
        LL j = 2;
        bool prime = true;
        while (j * j <= i) {
            if (i % j == 0) {
                prime = false;
                break;
            }
            j++;
        }
        if (prime)
            total += i;
    }
    printf("%lld\n", total);
    return 0;
}
