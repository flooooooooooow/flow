#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>


int32_t sum_range(int32_t start, int32_t end);
int32_t factorial(int32_t n);
int32_t main();

int32_t sum_range(int32_t start, int32_t end) {
    int32_t sum = 0;
    int32_t i = start;
    while (i <= end) {
        sum = (sum + i);
        i = (i + 1);
    }
    return sum;
}

int32_t factorial(int32_t n) {
    int32_t result = 1;
    int32_t i = 2;
    while (i <= n) {
        result = (result * i);
        i = (i + 1);
    }
    return result;
}

int32_t main() {
    int32_t sum_result = sum_range(1, 100);
    int32_t fact_result = factorial(5);
    return (sum_result + fact_result);
}
