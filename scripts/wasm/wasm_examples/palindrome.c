#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>


int32_t is_palindrome_number(int32_t n);
int32_t main();

int32_t is_palindrome_number(int32_t n) {
    int32_t original = n;
    int32_t reversed = 0;
    while (n > 0) {
        int32_t digit = (n % 10);
        reversed = ((reversed * 10) + digit);
        n = (n / 10);
    }
    if (original == reversed) {
        return 1;
    } else {
        return 0;
    }
}

int32_t main() {
    int32_t number = 121;
    int32_t result = is_palindrome_number(number);
    return result;
}
