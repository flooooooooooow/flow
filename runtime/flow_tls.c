/* TLS accept-loop for Flow HTTP (OpenSSL when FLOW_HAS_OPENSSL=1).
 * Supports HTTP/1.1 and a minimal HTTP/2 (h2) path over ALPN. */
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

int32_t flow_rt_https_selftest(int32_t port) {
    (void)port;
    return -1;
}

int32_t flow_rt_https_pem_alpn_selftest(int32_t port) {
    (void)port;
    return -1;
}

int32_t flow_rt_https_h2_selftest(int32_t port) {
    (void)port;
    return -1;
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

/* ---- minimal HTTP/2 (RFC 7540/7541 literals, no Huffman) ---- */

static const char H2_CLIENT_PREFACE[24] = "PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n";

static int ssl_write_all(SSL *ssl, const void *buf, int len) {
    const unsigned char *p = (const unsigned char *)buf;
    int left = len;
    while (left > 0) {
        int n = SSL_write(ssl, p, left);
        if (n <= 0) return -1;
        p += n;
        left -= n;
    }
    return 0;
}

static int ssl_read_exact(SSL *ssl, void *buf, int len) {
    unsigned char *p = (unsigned char *)buf;
    int left = len;
    while (left > 0) {
        int n = SSL_read(ssl, p, left);
        if (n <= 0) return -1;
        p += n;
        left -= n;
    }
    return 0;
}

static int h2_write_frame(SSL *ssl, uint8_t type, uint8_t flags, uint32_t stream,
                          const void *payload, uint32_t len) {
    unsigned char hdr[9];
    hdr[0] = (unsigned char)((len >> 16) & 0xff);
    hdr[1] = (unsigned char)((len >> 8) & 0xff);
    hdr[2] = (unsigned char)(len & 0xff);
    hdr[3] = type;
    hdr[4] = flags;
    hdr[5] = (unsigned char)((stream >> 24) & 0x7f);
    hdr[6] = (unsigned char)((stream >> 16) & 0xff);
    hdr[7] = (unsigned char)((stream >> 8) & 0xff);
    hdr[8] = (unsigned char)(stream & 0xff);
    if (ssl_write_all(ssl, hdr, 9) < 0) return -1;
    if (len > 0 && ssl_write_all(ssl, payload, (int)len) < 0) return -1;
    return 0;
}

static int h2_read_frame(SSL *ssl, uint8_t *type, uint8_t *flags, uint32_t *stream,
                         unsigned char *payload, uint32_t cap, uint32_t *out_len) {
    unsigned char hdr[9];
    if (ssl_read_exact(ssl, hdr, 9) < 0) return -1;
    uint32_t len = ((uint32_t)hdr[0] << 16) | ((uint32_t)hdr[1] << 8) | hdr[2];
    *type = hdr[3];
    *flags = hdr[4];
    *stream = (((uint32_t)hdr[5] << 24) | ((uint32_t)hdr[6] << 16) |
               ((uint32_t)hdr[7] << 8) | hdr[8]) &
              0x7fffffffu;
    if (len > cap) return -1;
    if (len > 0 && ssl_read_exact(ssl, payload, (int)len) < 0) return -1;
    *out_len = len;
    return 0;
}

/* HPACK Literal Header Field without Indexing — New Name (lens < 127). */
static int hpack_lit(unsigned char *out, int cap, const char *name, const char *value) {
    int nl = (int)strlen(name);
    int vl = (int)strlen(value);
    if (nl > 126 || vl > 126) return -1;
    int need = 1 + 1 + nl + 1 + vl;
    if (need > cap) return -1;
    int i = 0;
    out[i++] = 0x00;
    out[i++] = (unsigned char)nl;
    memcpy(out + i, name, (size_t)nl);
    i += nl;
    out[i++] = (unsigned char)vl;
    memcpy(out + i, value, (size_t)vl);
    i += vl;
    return i;
}

static int h2_build_req_headers(unsigned char *out, int cap, const char *path) {
    int hi = 0;
    int n;
    n = hpack_lit(out + hi, cap - hi, ":method", "GET");
    if (n < 0) return -1;
    hi += n;
    n = hpack_lit(out + hi, cap - hi, ":path", path);
    if (n < 0) return -1;
    hi += n;
    n = hpack_lit(out + hi, cap - hi, ":scheme", "https");
    if (n < 0) return -1;
    hi += n;
    n = hpack_lit(out + hi, cap - hi, ":authority", "localhost");
    if (n < 0) return -1;
    hi += n;
    return hi;
}

static int h2_build_resp_headers(unsigned char *out, int cap) {
    int hi = 0;
    int n;
    n = hpack_lit(out + hi, cap - hi, ":status", "200");
    if (n < 0) return -1;
    hi += n;
    n = hpack_lit(out + hi, cap - hi, "content-type", "text/plain");
    if (n < 0) return -1;
    hi += n;
    return hi;
}

static int https_handle_h2(SSL *ssl) {
    char preface[24];
    if (ssl_read_exact(ssl, preface, 24) < 0) return -1;
    if (memcmp(preface, H2_CLIENT_PREFACE, 24) != 0) return -1;

    /* Server SETTINGS (empty). */
    if (h2_write_frame(ssl, 0x4, 0, 0, NULL, 0) < 0) return -1;

    int got_headers = 0;
    unsigned char payload[4096];
    for (int i = 0; i < 40 && !got_headers; i++) {
        uint8_t type = 0, flags = 0;
        uint32_t stream = 0, len = 0;
        if (h2_read_frame(ssl, &type, &flags, &stream, payload, sizeof(payload), &len) < 0)
            return -1;
        if (type == 0x4) { /* SETTINGS */
            if (!(flags & 0x1)) {
                if (h2_write_frame(ssl, 0x4, 0x1, 0, NULL, 0) < 0) return -1;
            }
        } else if (type == 0x1) { /* HEADERS */
            got_headers = 1;
        } else if (type == 0x8 || type == 0x6) {
            /* WINDOW_UPDATE / PING — ignore for selftest */
            (void)stream;
        }
    }
    if (!got_headers) return -1;

    unsigned char hpack[256];
    int hi = h2_build_resp_headers(hpack, (int)sizeof(hpack));
    if (hi < 0) return -1;
    if (h2_write_frame(ssl, 0x1, 0x4, 1, hpack, (uint32_t)hi) < 0) return -1; /* END_HEADERS */
    const char *body = "Hello H2\n";
    if (h2_write_frame(ssl, 0x0, 0x1, 1, body, 9) < 0) return -1; /* DATA + END_STREAM */
    return 0;
}

typedef struct {
    int lfd;
    SSL_CTX *ctx;
    int n;
    char alpn_selected[32];
} https_pack;

static void https_handle_http11(SSL *ssl) {
    char buf[2048];
    int n = SSL_read(ssl, buf, (int)sizeof(buf) - 1);
    if (n > 0) {
        buf[n] = '\0';
        const char *body = "Hello TLS\n";
        char resp[256];
        int rn = snprintf(resp, sizeof(resp),
                          "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n"
                          "Content-Length: %d\r\nConnection: close\r\n\r\n%s",
                          10, body);
        if (rn > 0) SSL_write(ssl, resp, rn);
    }
}

static void https_handle_one(https_pack *pack, int cfd) {
    sock_set_timeouts(cfd, 3);
    SSL *ssl = SSL_new(pack->ctx);
    if (!ssl) {
        close(cfd);
        return;
    }
    SSL_set_fd(ssl, cfd);
    if (SSL_accept(ssl) <= 0) {
        SSL_free(ssl);
        close(cfd);
        return;
    }
    const unsigned char *alpn = NULL;
    unsigned int alpn_len = 0;
    SSL_get0_alpn_selected(ssl, &alpn, &alpn_len);
    if (alpn && alpn_len > 0 && alpn_len < sizeof(pack->alpn_selected)) {
        memcpy(pack->alpn_selected, alpn, alpn_len);
        pack->alpn_selected[alpn_len] = '\0';
    }
    if (alpn && alpn_len == 2 && memcmp(alpn, "h2", 2) == 0) {
        (void)https_handle_h2(ssl);
    } else {
        https_handle_http11(ssl);
    }
    SSL_shutdown(ssl);
    SSL_free(ssl);
    close(cfd);
}

static void *https_accept_thread(void *arg) {
    https_pack *p = (https_pack *)arg;
    for (int i = 0; i < p->n; i++) {
        int cfd = accept(p->lfd, NULL, NULL);
        if (cfd < 0) continue;
        https_handle_one(p, cfd);
    }
    return NULL;
}

/* offer_alpn: 0=none, 1=h2+http/1.1, 2=h2 only, 3=http/1.1 only */
static int https_client_get(int32_t port, const char *path, int offer_alpn,
                            char *out, int out_cap, char *alpn_out, int alpn_cap) {
    tls_init_once();
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
    SSL_CTX *ctx = SSL_CTX_new(TLS_client_method());
    if (!ctx) {
        close(c);
        return -1;
    }
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
    SSL *ssl = SSL_new(ctx);
    if (!ssl) {
        SSL_CTX_free(ctx);
        close(c);
        return -1;
    }
    SSL_set_fd(ssl, c);
    if (SSL_connect(ssl) <= 0) {
        SSL_free(ssl);
        SSL_CTX_free(ctx);
        close(c);
        return -1;
    }
    if (alpn_out && alpn_cap > 0) {
        const unsigned char *alpn = NULL;
        unsigned int alpn_len = 0;
        SSL_get0_alpn_selected(ssl, &alpn, &alpn_len);
        if (alpn && alpn_len > 0 && (int)alpn_len < alpn_cap) {
            memcpy(alpn_out, alpn, alpn_len);
            alpn_out[alpn_len] = '\0';
        } else {
            alpn_out[0] = '\0';
        }
    }
    char req[128];
    snprintf(req, sizeof(req), "GET %s HTTP/1.0\r\nHost: localhost\r\n\r\n", path);
    SSL_write(ssl, req, (int)strlen(req));
    int n = SSL_read(ssl, out, out_cap - 1);
    if (n < 0) n = 0;
    out[n] = '\0';
    SSL_shutdown(ssl);
    SSL_free(ssl);
    SSL_CTX_free(ctx);
    close(c);
    return n;
}

static int https_client_h2_get(int32_t port, const char *path,
                               char *body_out, int body_cap,
                               char *alpn_out, int alpn_cap) {
    tls_init_once();
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
    SSL_CTX *ctx = SSL_CTX_new(TLS_client_method());
    if (!ctx) {
        close(c);
        return -1;
    }
    SSL_CTX_set_verify(ctx, SSL_VERIFY_NONE, NULL);
    {
        static const unsigned char protos[] = "\x02h2";
        SSL_CTX_set_alpn_protos(ctx, protos, sizeof(protos) - 1);
    }
    SSL *ssl = SSL_new(ctx);
    if (!ssl) {
        SSL_CTX_free(ctx);
        close(c);
        return -1;
    }
    SSL_set_fd(ssl, c);
    if (SSL_connect(ssl) <= 0) {
        SSL_free(ssl);
        SSL_CTX_free(ctx);
        close(c);
        return -1;
    }
    if (alpn_out && alpn_cap > 0) {
        const unsigned char *alpn = NULL;
        unsigned int alpn_len = 0;
        SSL_get0_alpn_selected(ssl, &alpn, &alpn_len);
        if (alpn && alpn_len > 0 && (int)alpn_len < alpn_cap) {
            memcpy(alpn_out, alpn, alpn_len);
            alpn_out[alpn_len] = '\0';
        } else {
            alpn_out[0] = '\0';
        }
    }

    if (ssl_write_all(ssl, H2_CLIENT_PREFACE, 24) < 0) goto fail;
    if (h2_write_frame(ssl, 0x4, 0, 0, NULL, 0) < 0) goto fail; /* client SETTINGS */

    unsigned char hpack[256];
    int hi = h2_build_req_headers(hpack, (int)sizeof(hpack), path);
    if (hi < 0) goto fail;

    int saw_server_settings = 0;
    int sent_headers = 0;
    int got_data = 0;
    int body_n = 0;
    unsigned char payload[4096];
    if (body_cap > 0) body_out[0] = '\0';

    for (int i = 0; i < 40 && !got_data; i++) {
        uint8_t type = 0, flags = 0;
        uint32_t stream = 0, len = 0;
        if (h2_read_frame(ssl, &type, &flags, &stream, payload, sizeof(payload), &len) < 0)
            goto fail;
        if (type == 0x4) { /* SETTINGS */
            if (!(flags & 0x1)) {
                saw_server_settings = 1;
                if (h2_write_frame(ssl, 0x4, 0x1, 0, NULL, 0) < 0) goto fail;
                if (!sent_headers) {
                    /* END_HEADERS | END_STREAM — after ACKing server SETTINGS */
                    if (h2_write_frame(ssl, 0x1, 0x5, 1, hpack, (uint32_t)hi) < 0) goto fail;
                    sent_headers = 1;
                }
            }
        } else if (type == 0x1) {
            (void)stream;
            if (!sent_headers && saw_server_settings) {
                if (h2_write_frame(ssl, 0x1, 0x5, 1, hpack, (uint32_t)hi) < 0) goto fail;
                sent_headers = 1;
            }
        } else if (type == 0x0) { /* DATA */
            if (body_cap > 1 && len > 0) {
                int copy = (int)len;
                if (copy > body_cap - 1) copy = body_cap - 1;
                memcpy(body_out, payload, (size_t)copy);
                body_out[copy] = '\0';
                body_n = copy;
            }
            got_data = 1;
        }
    }

    SSL_shutdown(ssl);
    SSL_free(ssl);
    SSL_CTX_free(ctx);
    close(c);
    return got_data ? body_n : -1;

fail:
    SSL_shutdown(ssl);
    SSL_free(ssl);
    SSL_CTX_free(ctx);
    close(c);
    return -1;
}

/* check_mode: 0=HTTP/1.1 body only, 1=ALPN http/1.1 + body, 2=ALPN h2 + Hello H2 */
static int32_t https_serve_selftest(int32_t port, SSL_CTX *ctx, int check_mode) {
    if (!ctx) return 0;
    int lfd = tcp_listen(port);
    if (lfd < 0) {
        SSL_CTX_free(ctx);
        return 0;
    }
    https_pack pack;
    memset(&pack, 0, sizeof(pack));
    pack.lfd = lfd;
    pack.ctx = ctx;
    pack.n = 1;
    pthread_t th;
    if (pthread_create(&th, NULL, https_accept_thread, &pack) != 0) {
        close(lfd);
        SSL_CTX_free(ctx);
        return 0;
    }
    usleep(5000);
    int ok = 0;
    for (int attempt = 0; attempt < 50; attempt++) {
        char resp[1024];
        char alpn[32];
        if (check_mode == 2) {
            int n = https_client_h2_get(port, "/", resp, (int)sizeof(resp),
                                       alpn, (int)sizeof(alpn));
            if (n > 0 && strcmp(alpn, "h2") == 0 && strstr(resp, "Hello H2") != NULL) {
                ok = 1;
                break;
            }
        } else {
            int offer = (check_mode == 1) ? 1 : 0;
            int n = https_client_get(port, "/", offer, resp, (int)sizeof(resp),
                                     alpn, (int)sizeof(alpn));
            if (n > 0 && strstr(resp, "200") != NULL && strstr(resp, "Hello TLS") != NULL) {
                if (check_mode != 1 || strcmp(alpn, "http/1.1") == 0) {
                    ok = 1;
                    break;
                }
            }
        }
        usleep(2000);
    }
    pthread_join(th, NULL);
    close(lfd);
    SSL_CTX_free(ctx);
    return ok ? 1 : 0;
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

int32_t flow_rt_https_selftest(int32_t port) {
    return https_serve_selftest(port, make_server_ctx_mem(0), 0);
}

int32_t flow_rt_https_pem_alpn_selftest(int32_t port) {
    return https_serve_selftest(port, make_pem_ctx(0), 1);
}

int32_t flow_rt_https_h2_selftest(int32_t port) {
    return https_serve_selftest(port, make_pem_ctx(1), 2);
}

#endif /* FLOW_HAS_OPENSSL */
