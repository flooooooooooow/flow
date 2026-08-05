#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>


int32_t get_array_value(int32_t pos);
int32_t linear_search(int32_t item);
int32_t main();

int32_t get_array_value(int32_t pos) {
    if (pos == 0) {
        return 2;
    }
    if (pos == 1) {
        return 5;
    }
    if (pos == 2) {
        return 8;
    }
    if (pos == 3) {
        return 12;
    }
    if (pos == 4) {
        return 16;
    }
    if (pos == 5) {
        return 23;
    }
    if (pos == 6) {
        return 38;
    }
    if (pos == 7) {
        return 56;
    }
    if (pos == 8) {
        return 72;
    }
    if (pos == 9) {
        return 91;
    }
    return (-1);
}

int32_t linear_search(int32_t item) {
    int32_t index = 0;
    while (index < 10) {
        int32_t current = get_array_value(index);
        if (current == item) {
            return index;
        }
        index = (index + 1);
    }
    return (-1);
}

int32_t main() {
    int32_t number = 23;
    int32_t location = linear_search(number);
    return location;
}
