/* OpenSSL TLS kernels for Flow HTTPS (protocol logic in lib/runtime/tls.flow).
 * Without OpenSSL, ptr shims return NULL and i32 shims return -2. */
#ifndef FLOW_TLS_H
#define FLOW_TLS_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* 1 if built with OpenSSL, else 0. */
int32_t flow_rt_tls_available(void);

/* TCP kernels (loopback client connect uses 3s socket timeouts). */
int32_t flow_rt_tls_tcp_listen(int32_t port);
int32_t flow_rt_tls_tcp_accept(int32_t lfd);
int32_t flow_rt_tls_tcp_connect(int32_t port);
void flow_rt_tls_sock_timeouts(int32_t fd, int32_t sec);
int32_t flow_rt_tls_fd_close(int32_t fd);

/* SSL_CTX factories. Server "mem": ephemeral self-signed cert in memory.
 * Server "pem": writes an ephemeral PEM pair under build/ and loads it.
 * Client offer_alpn: 0=none, 1=h2+http/1.1, 2=h2 only, 3=http/1.1 only. */
void *flow_rt_tls_ctx_server_mem(int32_t prefer_h2);
void *flow_rt_tls_ctx_server_pem(int32_t prefer_h2);
void *flow_rt_tls_ctx_client(int32_t offer_alpn);
void flow_rt_tls_ctx_free(void *ctx);

/* Per-connection SSL shims (SSL* / SSL_CTX* pass as void*). */
void *flow_rt_ssl_accept_fd(void *ctx, int32_t fd);
void *flow_rt_ssl_connect_fd(void *ctx, int32_t fd);
int32_t flow_rt_ssl_read(void *ssl, void *buf, int32_t len);
int32_t flow_rt_ssl_write(void *ssl, void *buf, int32_t len);
void flow_rt_ssl_shutdown_free(void *ssl);

/* Negotiated ALPN protocol: 0=none, 1=http/1.1, 2=h2. */
int32_t flow_rt_ssl_alpn_selected(void *ssl);

/* Selftest accept thread: runs flow_tls_serve_one_conn (lib/runtime/tls.flow)
 * on a pthread. One thread at a time; join before respawning. */
int32_t flow_rt_tls_serve_spawn(void *ctx, int32_t lfd);
int32_t flow_rt_tls_serve_join(void);

#ifdef __cplusplus
}
#endif

#endif /* FLOW_TLS_H */
