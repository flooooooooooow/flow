/* Give the host a turn, and tell the program which port to dial.
 *
 * Native: usleep. Under WASM: emscripten_sleep, which needs -sASYNCIFY. That
 * is the whole reason ASYNCIFY is on for this build. Emscripten's socket
 * bridge cannot block, because the WebSocket handshake and every inbound frame
 * arrive on the browser event loop, and a WASM module spinning in a poll loop
 * never lets that loop run. emscripten_sleep unwinds the stack, returns to the
 * event loop, and resumes where it left off.
 *
 * FLOW_DEMO_PORT is baked in at compile time so the same Flow source can dial
 * a plain TCP echo server natively and a WebSocket relay in the browser.
 */
#include <stdint.h>

#ifndef FLOW_DEMO_PORT
#define FLOW_DEMO_PORT 9505
#endif

#ifdef __EMSCRIPTEN__
#include <emscripten.h>
void flow_net_yield(int32_t ms) {
    if (ms > 0) emscripten_sleep((unsigned int)ms);
}
#else
#include <unistd.h>
void flow_net_yield(int32_t ms) {
    if (ms > 0) usleep((useconds_t)ms * 1000);
}
#endif

int32_t flow_demo_port(void) { return FLOW_DEMO_PORT; }
