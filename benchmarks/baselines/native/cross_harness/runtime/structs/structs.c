#include <stdint.h>

typedef struct {
    int32_t x;
    int32_t y;
} Point;

int main(void) {
    const Point p = {.x = 1, .y = 2};
    return p.x == 1 && p.y == 2 ? 0 : 1;
}
