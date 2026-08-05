/* OpenSSL TLS for Flow HTTP accept-loop (server + test client). */
#ifndef FLOW_TLS_H
#define FLOW_TLS_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* 1 if built with OpenSSL, else 0. */
int32_t flow_rt_tls_available(void);

/* HTTPS selftest: ephemeral self-signed cert, GET / → 200 over TLS.
 * Returns 1 on success, 0 on fail, -1 if TLS unavailable. */
int32_t flow_rt_https_selftest(int32_t port);

/* PEM cert/key + ALPN http/1.1 selftest.
 * Writes ephemeral PEM under build/, loads via SSL_CTX_use_*_file,
 * negotiates ALPN http/1.1 (client offers h2+http/1.1; server prefers 1.1).
 * Returns 1 on success, 0 on fail, -1 if TLS unavailable. */
int32_t flow_rt_https_pem_alpn_selftest(int32_t port);

/* HTTPS HTTP/2 selftest: PEM + ALPN h2, minimal preface/SETTINGS/HEADERS/DATA.
 * Server prefers h2; client offers only h2; GET / → "Hello H2".
 * Returns 1 on success, 0 on fail, -1 if TLS unavailable. */
int32_t flow_rt_https_h2_selftest(int32_t port);

#ifdef __cplusplus
}
#endif

#endif /* FLOW_TLS_H */
