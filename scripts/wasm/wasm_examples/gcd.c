#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>


int32_t gcd(int32_t a, int32_t b);
int32_t main();

int32_t gcd(int32_t a, int32_t b) {
    while (b != 0) {
        int32_t temp = b;
        b = (a % b);
        a = temp;
    }
    return a;
}

int32_t main() {
    int32_t a = 56;
    int32_t b = 98;
    int32_t result = gcd(a, b);
    return result;
}
