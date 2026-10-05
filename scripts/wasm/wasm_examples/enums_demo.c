#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>


typedef enum {
    Color_Red,
    Color_Green,
    Color_Blue
} Color_Tag;

typedef struct {
    Color_Tag tag;
} Color;

typedef enum {
    Option_i32_Some,
    Option_i32_None
} Option_i32_Tag;

typedef struct {
    Option_i32_Tag tag;
    union {
        int32_t Some_value;
    } data;
} Option_i32;

Color make_red();
Color make_green();
Option_i32 some_i32(int32_t value);
Option_i32 none_i32();
int32_t is_some(Option_i32 opt);
int32_t is_none(Option_i32 opt);
int32_t main();

Color make_red() {
    Color c = (Color){ .tag = Color_Red };
    return c;
}

Color make_green() {
    Color c = (Color){ .tag = Color_Green };
    return c;
}

Option_i32 some_i32(int32_t value) {
    Option_i32 opt = (Option_i32){ .tag = Option_i32_Some };
    return opt;
}

Option_i32 none_i32() {
    Option_i32 opt = (Option_i32){ .tag = Option_i32_None };
    return opt;
}

int32_t is_some(Option_i32 opt) {
    return opt.tag == Option_i32_Some;
}

int32_t is_none(Option_i32 opt) {
    return opt.tag == Option_i32_None;
}

int32_t main() {
    printf("=== Enums Demo ===\n\n");
    Color red = make_red();
    Color green = make_green();
    printf("red.tag = %d\n", red.tag);
    printf("green.tag = %d\n", green.tag);
    Option_i32 some_val = some_i32(42);
    Option_i32 none_val = none_i32();
    printf("some_val is_some: %d\n", is_some(some_val));
    printf("none_val is_none: %d\n", is_none(none_val));
    printf("\n=== End Demo ===\n");
    return 0;
}
