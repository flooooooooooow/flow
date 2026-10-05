#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>


int32_t power(int32_t base, int32_t exp);
int32_t main();

int32_t power(int32_t base, int32_t exp) {
    if (exp == 0) {
        return 1;
    }
    if (exp == 1) {
        return base;
    }
    int32_t result = 1;
    int32_t i = 0;
    while (i < exp) {
        result = (result * base);
        i = (i + 1);
    }
    return result;
}

int32_t main() {
    int32_t base = 2;
    int32_t exp = 10;
    int32_t result = power(base, exp);
    return result;
}
