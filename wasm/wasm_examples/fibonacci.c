#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>


int32_t fibonacci(int32_t n);
int32_t main();

int32_t fibonacci(int32_t n) {
    if (n <= 1) {
        return n;
    } else {
        return (fibonacci((n - 1)) + fibonacci((n - 2)));
    }
}

int32_t main() {
    int32_t result = fibonacci(10);
    return result;
}
