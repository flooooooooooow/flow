/* TLS accept-loop for Flow HTTP (OpenSSL when FLOW_HAS_OPENSSL=1). */
#include "flow_tls.h"

#include <arpa/inet.h>
#include <netinet/in.h>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

#ifndef FLOW_HAS_OPENSSL
#define FLOW_HAS_OPENSSL 0
#endif

#if FLOW_HAS_OPENSSL
#include <openssl/err.h>
#include <openssl/evp.h>
#include <openssl/pem.h>
#include <openssl/rsa.h>
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

#else

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

static SSL_CTX *make_server_ctx(void) {
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
    return ctx;
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

typedef struct {
    int lfd;
    SSL_CTX *ctx;
    int n;
} https_pack;

static void https_handle_one(SSL_CTX *ctx, int cfd) {
    SSL *ssl = SSL_new(ctx);
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
    SSL_shutdown(ssl);
    SSL_free(ssl);
    close(cfd);
}

static void *https_accept_thread(void *arg) {
    https_pack *p = (https_pack *)arg;
    for (int i = 0; i < p->n; i++) {
        int cfd = accept(p->lfd, NULL, NULL);
        if (cfd < 0) continue;
        https_handle_one(p->ctx, cfd);
    }
    return NULL;
}

static int https_client_get(int32_t port, const char *path, char *out, int out_cap) {
    tls_init_once();
    int c = socket(AF_INET, SOCK_STREAM, 0);
    if (c < 0) return -1;
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

int32_t flow_rt_https_selftest(int32_t port) {
    SSL_CTX *ctx = make_server_ctx();
    if (!ctx) return 0;
    int lfd = tcp_listen(port);
    if (lfd < 0) {
        SSL_CTX_free(ctx);
        return 0;
    }
    https_pack pack = {.lfd = lfd, .ctx = ctx, .n = 1};
    pthread_t th;
    if (pthread_create(&th, NULL, https_accept_thread, &pack) != 0) {
        close(lfd);
        SSL_CTX_free(ctx);
        return 0;
    }
    usleep(5000);
    char resp[1024];
    int ok = 0;
    for (int attempt = 0; attempt < 50; attempt++) {
        int n = https_client_get(port, "/", resp, (int)sizeof(resp));
        if (n > 0 && strstr(resp, "200") != NULL && strstr(resp, "Hello TLS") != NULL) {
            ok = 1;
            break;
        }
        usleep(2000);
    }
    pthread_join(th, NULL);
    close(lfd);
    SSL_CTX_free(ctx);
    return ok ? 1 : 0;
}

#endif /* FLOW_HAS_OPENSSL */
