#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>


int32_t bubble_sort_demo();
int32_t main();

int32_t bubble_sort_demo() {
    int32_t a1 = 64;
    int32_t a2 = 34;
    int32_t a3 = 25;
    int32_t a4 = 12;
    int32_t a5 = 22;
    int32_t a6 = 11;
    int32_t a7 = 90;
    int32_t n = 7;
    int32_t i = 0;
    int32_t j = 0;
    while (i < (n - 1)) {
        j = 0;
        while (j < ((n - i) - 1)) {
            if (a1 > a2) {
                int32_t temp = a1;
                a1 = a2;
                a2 = temp;
            }
            j = (j + 1);
        }
        i = (i + 1);
    }
    return ((((((a1 + a2) + a3) + a4) + a5) + a6) + a7);
}

int32_t main() {
    int32_t result = bubble_sort_demo();
    return result;
}
