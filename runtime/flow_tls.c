/* TLS kernels for Flow HTTPS (OpenSSL when FLOW_HAS_OPENSSL=1).
 * Ctx/cert machinery, ALPN callbacks, and thin per-call SSL shims live here;
 * the HTTP/1.1 + HTTP/2 protocol logic lives in lib/runtime/tls.flow. */
#include "flow_tls.h"

#include <arpa/inet.h>
#include <errno.h>
#include <netinet/in.h>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <unistd.h>

#ifndef FLOW_HAS_OPENSSL
#define FLOW_HAS_OPENSSL 0
#endif

#if FLOW_HAS_OPENSSL
#include <openssl/err.h>
#include <openssl/evp.h>
#include <openssl/pem.h>
#include <openssl/ssl.h>
#include <openssl/x509.h>
#endif

int32_t flow_rt_tls_available(void) {
#if FLOW_HAS_OPENSSL
    return 1;
#else
    return 0;
#endif
}

#if !FLOW_HAS_OPENSSL

/* No OpenSSL: every shim is a guarded stub (-2 / NULL). */

int32_t flow_rt_tls_tcp_listen(int32_t port) {
    (void)port;
    return -2;
}

int32_t flow_rt_tls_tcp_accept(int32_t lfd) {
    (void)lfd;
    return -2;
}

int32_t flow_rt_tls_tcp_connect(int32_t port) {
    (void)port;
    return -2;
}

void flow_rt_tls_sock_timeouts(int32_t fd, int32_t sec) {
    (void)fd;
    (void)sec;
}

int32_t flow_rt_tls_fd_close(int32_t fd) {
    (void)fd;
    return -2;
}

void *flow_rt_tls_ctx_server_mem(int32_t prefer_h2) {
    (void)prefer_h2;
    return NULL;
}

void *flow_rt_tls_ctx_server_pem(int32_t prefer_h2) {
    (void)prefer_h2;
    return NULL;
}

void *flow_rt_tls_ctx_client(int32_t offer_alpn) {
    (void)offer_alpn;
    return NULL;
}

void flow_rt_tls_ctx_free(void *ctx) {
    (void)ctx;
}

void *flow_rt_ssl_accept_fd(void *ctx, int32_t fd) {
    (void)ctx;
    (void)fd;
    return NULL;
}

void *flow_rt_ssl_connect_fd(void *ctx, int32_t fd) {
    (void)ctx;
    (void)fd;
    return NULL;
}

int32_t flow_rt_ssl_read(void *ssl, void *buf, int32_t len) {
    (void)ssl;
    (void)buf;
    (void)len;
    return -2;
}

int32_t flow_rt_ssl_write(void *ssl, void *buf, int32_t len) {
    (void)ssl;
    (void)buf;
    (void)len;
    return -2;
}

void flow_rt_ssl_shutdown_free(void *ssl) {
    (void)ssl;
}

int32_t flow_rt_ssl_alpn_selected(void *ssl) {
    (void)ssl;
    return 0;
}

int32_t flow_rt_tls_serve_spawn(void *ctx, int32_t lfd) {
    (void)ctx;
    (void)lfd;
    return -2;
}

int32_t flow_rt_tls_serve_join(void) {
    return -2;
}

#else

enum { ALPN_PREF_HTTP11 = 0, ALPN_PREF_H2 = 1 };

static void tls_init_once(void) {
    static int done = 0;
    if (done) return;
#if OPENSSL_VERSION_NUMBER < 0x10100000L
    SSL_library_init();
    SSL_load_error_strings();
    OpenSSL_add_all_algorithms();
#else
    OPENSSL_init_ssl(0, NULL);
#endif
    done = 1;
}

static EVP_PKEY *make_key(void) {
    EVP_PKEY *pkey = NULL;
    EVP_PKEY_CTX *ctx = EVP_PKEY_CTX_new_id(EVP_PKEY_RSA, NULL);
    if (!ctx) return NULL;
    if (EVP_PKEY_keygen_init(ctx) <= 0) {
        EVP_PKEY_CTX_free(ctx);
        return NULL;
    }
    if (EVP_PKEY_CTX_set_rsa_keygen_bits(ctx, 2048) <= 0) {
        EVP_PKEY_CTX_free(ctx);
        return NULL;
    }
    if (EVP_PKEY_keygen(ctx, &pkey) <= 0) {
        EVP_PKEY_CTX_free(ctx);
        return NULL;
    }
    EVP_PKEY_CTX_free(ctx);
    return pkey;
}

static X509 *make_cert(EVP_PKEY *pkey) {
    X509 *x = X509_new();
    if (!x) return NULL;
    ASN1_INTEGER_set(X509_get_serialNumber(x), 1);
    X509_gmtime_adj(X509_get_notBefore(x), 0);
    X509_gmtime_adj(X509_get_notAfter(x), 60 * 60 * 24);
    X509_set_pubkey(x, pkey);
    X509_NAME *name = X509_get_subject_name(x);
    X509_NAME_add_entry_by_txt(name, "CN", MBSTRING_ASC,
                               (const unsigned char *)"localhost", -1, -1, 0);
    X509_set_issuer_name(x, name);
    if (!X509_sign(x, pkey, EVP_sha256())) {
        X509_free(x);
        return NULL;
    }
    return x;
}

static int write_pem_pair(const char *cert_path, const char *key_path,
                          X509 *cert, EVP_PKEY *pkey) {
    FILE *fc = fopen(cert_path, "w");
    FILE *fk = fopen(key_path, "w");
    if (!fc || !fk) {
        if (fc) fclose(fc);
        if (fk) fclose(fk);
        return 0;
    }
    int ok = PEM_write_X509(fc, cert) == 1 &&
             PEM_write_PrivateKey(fk, pkey, NULL, NULL, 0, NULL, NULL) == 1;
    fclose(fc);
    fclose(fk);
    return ok;
}

static int alpn_match(const unsigned char *in, unsigned int inlen,
                      const char *want, unsigned int want_len,
                      const unsigned char **out, unsigned char *outlen) {
    const unsigned char *p = in;
    const unsigned char *end = in + inlen;
    while (p < end) {
        unsigned int len = *p++;
        if (p + len > end) break;
        if (len == want_len && memcmp(p, want, want_len) == 0) {
            *out = p;
            *outlen = (unsigned char)want_len;
            return 1;
        }
        p += len;
    }
    return 0;
}

static int alpn_select_cb(SSL *ssl, const unsigned char **out, unsigned char *outlen,
                          const unsigned char *in, unsigned int inlen, void *arg) {
    (void)ssl;
    int pref = arg ? *(int *)arg : ALPN_PREF_HTTP11;
    if (pref == ALPN_PREF_H2) {
        if (alpn_match(in, inlen, "h2", 2, out, outlen)) return SSL_TLSEXT_ERR_OK;
        if (alpn_match(in, inlen, "http/1.1", 8, out, outlen)) return SSL_TLSEXT_ERR_OK;
    } else {
        if (alpn_match(in, inlen, "http/1.1", 8, out, outlen)) return SSL_TLSEXT_ERR_OK;
        if (alpn_match(in, inlen, "h2", 2, out, outlen)) return SSL_TLSEXT_ERR_OK;
    }
    return SSL_TLSEXT_ERR_NOACK;
}

static int g_alpn_pref_http11 = ALPN_PREF_HTTP11;
static int g_alpn_pref_h2 = ALPN_PREF_H2;

static void ctx_enable_alpn(SSL_CTX *ctx, int prefer_h2) {
    SSL_CTX_set_alpn_select_cb(ctx, alpn_select_cb,
                               prefer_h2 ? &g_alpn_pref_h2 : &g_alpn_pref_http11);
}

static SSL_CTX *make_server_ctx_mem(int prefer_h2) {
    tls_init_once();
    SSL_CTX *ctx = SSL_CTX_new(TLS_server_method());
    if (!ctx) return NULL;
    EVP_PKEY *pkey = make_key();
    X509 *cert = pkey ? make_cert(pkey) : NULL;
    if (!pkey || !cert ||
        SSL_CTX_use_certificate(ctx, cert) != 1 ||
        SSL_CTX_use_PrivateKey(ctx, pkey) != 1) {
        if (cert) X509_free(cert);
        if (pkey) EVP_PKEY_free(pkey);
        SSL_CTX_free(ctx);
        return NULL;
    }
    X509_free(cert);
    EVP_PKEY_free(pkey);
    ctx_enable_alpn(ctx, prefer_h2);
    return ctx;
}

static SSL_CTX *make_server_ctx_pem(const char *cert_path, const char *key_path,
                                   int prefer_h2) {
    tls_init_once();
    SSL_CTX *ctx = SSL_CTX_new(TLS_server_method());
    if (!ctx) return NULL;
    if (SSL_CTX_use_certificate_file(ctx, cert_path, SSL_FILETYPE_PEM) != 1 ||
        SSL_CTX_use_PrivateKey_file(ctx, key_path, SSL_FILETYPE_PEM) != 1 ||
        SSL_CTX_check_private_key(ctx) != 1) {
        SSL_CTX_free(ctx);
        return NULL;
    }
    ctx_enable_alpn(ctx, prefer_h2);
    return ctx;
}

static SSL_CTX *make_pem_ctx(int prefer_h2) {
    tls_init_once();
    EVP_PKEY *pkey = make_key();
    X509 *cert = pkey ? make_cert(pkey) : NULL;
    if (!pkey || !cert) {
        if (cert) X509_free(cert);
        if (pkey) EVP_PKEY_free(pkey);
        return NULL;
    }
    const char *cert_path = "build/flow_tls_test.crt.pem";
    const char *key_path = "build/flow_tls_test.key.pem";
    if (mkdir("build", 0755) != 0 && errno != EEXIST) {
        X509_free(cert);
        EVP_PKEY_free(pkey);
        return NULL;
    }
    if (!write_pem_pair(cert_path, key_path, cert, pkey)) {
        X509_free(cert);
        EVP_PKEY_free(pkey);
        return NULL;
    }
    X509_free(cert);
    EVP_PKEY_free(pkey);
    return make_server_ctx_pem(cert_path, key_path, prefer_h2);
}

static void sock_set_timeouts(int fd, int sec) {
    struct timeval tv;
    tv.tv_sec = sec;
    tv.tv_usec = 0;
    setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
    setsockopt(fd, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv));
}

static int tcp_listen(int32_t port) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) return -1;
    int yes = 1;
    setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(yes));
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons((uint16_t)port);
    if (bind(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0 || listen(fd, 16) < 0) {
        close(fd);
        return -1;
    }
    return fd;
}

/* ---- shims for lib/runtime/tls.flow ---- */

int32_t flow_rt_tls_tcp_listen(int32_t port) {
    return tcp_listen(port);
}

int32_t flow_rt_tls_tcp_accept(int32_t lfd) {
    return accept(lfd, NULL, NULL);
}

int32_t flow_rt_tls_tcp_connect(int32_t port) {
    int c = socket(AF_INET, SOCK_STREAM, 0);
    if (c < 0) return -1;
    sock_set_timeouts(c, 3);
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = htons((uint16_t)port);
    if (connect(c, (struct sockaddr *)&addr, sizeof(addr)) != 0) {
        close(c);
        return -1;
    }
    return c;
}

void flow_rt_tls_sock_timeouts(int32_t fd, int32_t sec) {
    sock_set_timeouts(fd, sec);
}

int32_t flow_rt_tls_fd_close(int32_t fd) {
    return close(fd);
}

void *flow_rt_tls_ctx_server_mem(int32_t prefer_h2) {
    return make_server_ctx_mem(prefer_h2);
}

void *flow_rt_tls_ctx_server_pem(int32_t prefer_h2) {
    return make_pem_ctx(prefer_h2);
}

/* offer_alpn: 0=none, 1=h2+http/1.1, 2=h2 only, 3=http/1.1 only */
void *flow_rt_tls_ctx_client(int32_t offer_alpn) {
    tls_init_once();
    SSL_CTX *ctx = SSL_CTX_new(TLS_client_method());
    if (!ctx) return NULL;
    SSL_CTX_set_verify(ctx, SSL_VERIFY_NONE, NULL);
    if (offer_alpn == 1) {
        static const unsigned char protos[] = "\x02h2\x08http/1.1";
        SSL_CTX_set_alpn_protos(ctx, protos, sizeof(protos) - 1);
    } else if (offer_alpn == 2) {
        static const unsigned char protos[] = "\x02h2";
        SSL_CTX_set_alpn_protos(ctx, protos, sizeof(protos) - 1);
    } else if (offer_alpn == 3) {
        static const unsigned char protos[] = "\x08http/1.1";
        SSL_CTX_set_alpn_protos(ctx, protos, sizeof(protos) - 1);
    }
    return ctx;
}

void flow_rt_tls_ctx_free(void *ctx) {
    if (ctx) SSL_CTX_free((SSL_CTX *)ctx);
}

void *flow_rt_ssl_accept_fd(void *ctx, int32_t fd) {
    SSL *ssl = SSL_new((SSL_CTX *)ctx);
    if (!ssl) return NULL;
    SSL_set_fd(ssl, fd);
    if (SSL_accept(ssl) <= 0) {
        SSL_free(ssl);
        return NULL;
    }
    return ssl;
}

void *flow_rt_ssl_connect_fd(void *ctx, int32_t fd) {
    SSL *ssl = SSL_new((SSL_CTX *)ctx);
    if (!ssl) return NULL;
    SSL_set_fd(ssl, fd);
    if (SSL_connect(ssl) <= 0) {
        SSL_free(ssl);
        return NULL;
    }
    return ssl;
}

int32_t flow_rt_ssl_read(void *ssl, void *buf, int32_t len) {
    return SSL_read((SSL *)ssl, buf, len);
}

int32_t flow_rt_ssl_write(void *ssl, void *buf, int32_t len) {
    return SSL_write((SSL *)ssl, buf, len);
}

void flow_rt_ssl_shutdown_free(void *ssl) {
    if (!ssl) return;
    SSL_shutdown((SSL *)ssl);
    SSL_free((SSL *)ssl);
}

/* Negotiated ALPN protocol: 0=none, 1=http/1.1, 2=h2. */
int32_t flow_rt_ssl_alpn_selected(void *ssl) {
    const unsigned char *alpn = NULL;
    unsigned int alpn_len = 0;
    SSL_get0_alpn_selected((SSL *)ssl, &alpn, &alpn_len);
    if (!alpn || alpn_len == 0) return 0;
    if (alpn_len == 2 && memcmp(alpn, "h2", 2) == 0) return 2;
    if (alpn_len == 8 && memcmp(alpn, "http/1.1", 8) == 0) return 1;
    return 0;
}

/* ---- selftest accept thread (spawn kernel; handler is Flow) ---- */

/* Implemented in lib/runtime/tls.flow (always linked with this file). */
int32_t flow_tls_serve_one_conn(void *ctx, int32_t lfd);

typedef struct {
    void *ctx;
    int32_t lfd;
} tls_serve_args;

static tls_serve_args g_serve_args;
static pthread_t g_serve_thread;
static int g_serve_active = 0;

static void *tls_serve_trampoline(void *arg) {
    tls_serve_args *a = (tls_serve_args *)arg;
    (void)flow_tls_serve_one_conn(a->ctx, a->lfd);
    return NULL;
}

/* One serve thread at a time (selftests run sequentially). */
int32_t flow_rt_tls_serve_spawn(void *ctx, int32_t lfd) {
    if (g_serve_active) return -1;
    g_serve_args.ctx = ctx;
    g_serve_args.lfd = lfd;
    if (pthread_create(&g_serve_thread, NULL, tls_serve_trampoline, &g_serve_args) != 0)
        return -1;
    g_serve_active = 1;
    return 0;
}

int32_t flow_rt_tls_serve_join(void) {
    if (!g_serve_active) return -1;
    pthread_join(g_serve_thread, NULL);
    g_serve_active = 0;
    return 0;
}

#endif /* FLOW_HAS_OPENSSL */
