#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>


int32_t factorial(int32_t n);
int32_t main();

int32_t factorial(int32_t n) {
    if (n <= 1) {
        return 1;
    } else {
        return (n * factorial((n - 1)));
    }
}

int32_t main() {
    int32_t n = 5;
    int32_t result = factorial(n);
    return result;
}
