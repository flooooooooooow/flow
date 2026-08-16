/* Browser CSPRNG for Flow's crypto runtime on wasm.
 *
 * Natively, lib/runtime/crypto.flow's flow_random_bytes delegates to
 * flow_rt_random_bytes in runtime/flow_rt_crypto.c (arc4random/CCRandom on
 * Darwin, getrandom on Linux). Those kernels do not exist in a browser; this
 * file provides the wasm backend: WebCrypto's synchronous CSPRNG
 * (crypto.getRandomValues), which is a genuine cryptographic RNG — the same
 * family as crypto.subtle, just the non-async half of the API.
 *
 * Everything else in lib/runtime/crypto.flow — SHA-256 included — is pure
 * Flow with no externs, so linking that module as a library TU runs Flow's
 * own implementation unchanged in the browser.
 */
#include <emscripten/emscripten.h>
#include <stdint.h>

int32_t flow_rt_random_bytes(void *buf, int64_t len) {
    if (!buf || len <= 0) {
        return 0;
    }
    EM_ASM({
        crypto.getRandomValues(new Uint8Array(HEAPU8.buffer, $0, $1));
    }, buf, (int32_t)len);
    return 0;
}
