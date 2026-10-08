/* Native twin of benchmarks/cross_harness/cold/hello (#746). The startup
 * row compares the Flow executable with this one: both are built with the
 * same clang flags and differ only in what the Flow runtime adds. */
#include <stdio.h>

int main(void) {
    fputs("Hello, world!", stdout);
    return 0;
}
