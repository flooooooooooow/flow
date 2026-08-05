#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>


int32_t fibonacci_i32(int32_t n);
int32_t main(void);

int32_t fibonacci_i32(int32_t n) {
    if (n <= 1) {
        return n;
    } else {
        return (fibonacci_i32((n - 1)) + fibonacci_i32((n - 2)));
    }
}

int32_t main(void) {
    int32_t result = fibonacci_i32(10);
    return result;
}
