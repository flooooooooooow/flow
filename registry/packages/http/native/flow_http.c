#include "flow_http.h"

#include <curl/curl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define FLOW_HTTP_DEFAULT_TIMEOUT_SECS 30

struct flow_http_buf {
    char *data;
    size_t len;
    size_t cap;
};

static size_t flow_http_write_cb(char *ptr, size_t size, size_t nmemb, void *userdata) {
    size_t total = size * nmemb;
    struct flow_http_buf *b = (struct flow_http_buf *)userdata;
    if (b->len + total + 1 > b->cap) {
        size_t remain = (b->cap > b->len + 1) ? (b->cap - b->len - 1) : 0;
        if (remain == 0) {
            return total; /* drop overflow but report success to curl */
        }
        if (total > remain) {
            total = remain;
        }
    }
    memcpy(b->data + b->len, ptr, total);
    b->len += total;
    b->data[b->len] = '\0';
    return size * nmemb;
}

static int flow_http_nonempty(const char *s) {
    return s != NULL && s[0] != '\0';
}

/* Append '\n'-separated "Name: value" lines to a curl_slist. */
static struct curl_slist *flow_http_append_headers(struct curl_slist *headers,
                                                   const char *headers_nl) {
    if (!flow_http_nonempty(headers_nl)) {
        return headers;
    }

    const char *p = headers_nl;
    while (*p) {
        while (*p == '\n' || *p == '\r') {
            p++;
        }
        if (!*p) {
            break;
        }
        const char *start = p;
        while (*p && *p != '\n' && *p != '\r') {
            p++;
        }
        size_t n = (size_t)(p - start);
        if (n == 0) {
            continue;
        }
        char *line = (char *)malloc(n + 1);
        if (!line) {
            return headers;
        }
        memcpy(line, start, n);
        line[n] = '\0';
        /* trim trailing spaces */
        while (n > 0 && (line[n - 1] == ' ' || line[n - 1] == '\t')) {
            line[--n] = '\0';
        }
        if (n > 0) {
            headers = curl_slist_append(headers, line);
        }
        free(line);
    }
    return headers;
}

int64_t flow_http_request(const char *method, const char *url, const char *headers_nl,
                          const char *body, const char *content_type, int64_t timeout_secs,
                          char *buf, int64_t buflen, int64_t *status_out,
                          int64_t *curl_err_out) {
    if (status_out) {
        *status_out = 0;
    }
    if (curl_err_out) {
        *curl_err_out = -1; /* invalid-args sentinel until perform */
    }
    if (!method || !url || !buf || buflen <= 0) {
        return -1;
    }
    buf[0] = '\0';

    CURL *curl = curl_easy_init();
    if (!curl) {
        if (curl_err_out) {
            *curl_err_out = (int64_t)CURLE_FAILED_INIT;
        }
        return -1;
    }

    long timeout = (timeout_secs > 0) ? (long)timeout_secs : (long)FLOW_HTTP_DEFAULT_TIMEOUT_SECS;
    struct flow_http_buf out = {.data = buf, .len = 0, .cap = (size_t)buflen};

    curl_easy_setopt(curl, CURLOPT_URL, url);
    curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, flow_http_write_cb);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &out);
    curl_easy_setopt(curl, CURLOPT_USERAGENT, "flow-http/0.1");
    curl_easy_setopt(curl, CURLOPT_TIMEOUT, timeout);
    curl_easy_setopt(curl, CURLOPT_CUSTOMREQUEST, method);

    int is_post = (strcmp(method, "POST") == 0);
    if (is_post) {
        curl_easy_setopt(curl, CURLOPT_POST, 1L);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, body ? body : "");
    }

    struct curl_slist *headers = NULL;
    headers = flow_http_append_headers(headers, headers_nl);
    if (flow_http_nonempty(content_type)) {
        char hdr[256];
        snprintf(hdr, sizeof(hdr), "Content-Type: %s", content_type);
        headers = curl_slist_append(headers, hdr);
    }
    if (headers) {
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    }

    CURLcode rc = curl_easy_perform(curl);
    long status = 0;
    curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &status);
    if (status_out) {
        *status_out = (int64_t)status;
    }
    if (curl_err_out) {
        *curl_err_out = (rc == CURLE_OK) ? 0 : (int64_t)rc;
    }

    if (headers) {
        curl_slist_free_all(headers);
    }
    curl_easy_cleanup(curl);

    if (rc != CURLE_OK) {
        return -1;
    }
    return (int64_t)out.len;
}

int64_t flow_http_get(const char *url, char *buf, int64_t buflen, int64_t *status_out) {
    int64_t curl_err = 0;
    return flow_http_request("GET", url, NULL, NULL, NULL, FLOW_HTTP_DEFAULT_TIMEOUT_SECS, buf,
                             buflen, status_out, &curl_err);
}

int64_t flow_http_post(const char *url, const char *content_type, const char *body,
                       char *buf, int64_t buflen, int64_t *status_out) {
    int64_t curl_err = 0;
    return flow_http_request("POST", url, NULL, body ? body : "", content_type,
                             FLOW_HTTP_DEFAULT_TIMEOUT_SECS, buf, buflen, status_out, &curl_err);
}
