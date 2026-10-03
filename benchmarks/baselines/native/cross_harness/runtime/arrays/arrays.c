#include <stdint.h>

int main(void) {
    int32_t arr[1000] = {0};
    for (int32_t i = 0; i < 1000; i += 1) {
        arr[i] = i;
    }
    return 0;
}
