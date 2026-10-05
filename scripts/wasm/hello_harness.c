/* Minimal C harness for Flow → C → WASM smoke tests.
 * Mirrors a tiny Flow `main() -> i32` (see examples/basics/hello_world.flow).
 * No Emscripten-specific headers — plain ISO C so `emcc` and host clang both work.
 */
#include <stdint.h>
#include <stdio.h>

int32_t main(void) {
    printf("Hello from Flow C → WASM\n");
    return 0;
}
