#include "stdio.h"
#include <vector>
using namespace std;
typedef long long LL;
vector<LL>* sort(vector<LL>* v) {
    vector<LL>* rtn = new vector<LL>();
    LL n = v->size();
    for (int i = 0; i < n; i++) {
        rtn->push_back((*v)[i]);
    }
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            if ((*rtn)[i] > (*rtn)[j]) {
                LL t = (*rtn)[i];
                (*rtn)[i] = (*rtn)[j];
                (*rtn)[j] = t;
            }
        }
    }
    return rtn;
}

int main() {
    vector<LL> init;
    init.push_back(1);
    init.push_back(2);
    while (init.size() < 30000) {
        LL next = (init[init.size() - 1] * 127 + init[init.size() - 2]) % 253;
        init.push_back(next);
    }
    vector<LL> *sorted = sort(&init);
    LL sum1 = 0, sum2 = 0;
    for (int i = 0; i < init.size(); i++) {
        sum1 += init[i];
        sum2 += (*sorted)[i];
    }
    printf("%lld %lld\n", sum1, sum2);
    return 0;
}

