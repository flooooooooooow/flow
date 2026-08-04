#ifndef FLOW_HTTP_H
#define FLOW_HTTP_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Perform an HTTP request.
 *
 * method:        "GET" or "POST" (case-sensitive)
 * headers_nl:    optional, NUL-terminated lines of "Name: value" separated by '\n'
 * body:          optional request body (POST); ignored for GET when NULL/empty
 * content_type:  optional; appended as Content-Type if non-empty
 * timeout_secs:  overall transfer timeout; <=0 uses default 30s
 *
 * Writes response body into buf (NUL-terminated if space).
 * On success returns body length (excluding NUL), *status_out = HTTP status,
 * and *curl_err_out = 0. HTTP 4xx/5xx still counts as curl success (len >= 0,
 * curl_err 0) so callers can distinguish transport failure from HTTP errors.
 * On curl failure returns -1 and *curl_err_out = CURLcode (>0).
 * On invalid args returns -1 and *curl_err_out = -1 (sentinel). */
int64_t flow_http_request(const char *method, const char *url, const char *headers_nl,
                          const char *body, const char *content_type, int64_t timeout_secs,
                          char *buf, int64_t buflen, int64_t *status_out,
                          int64_t *curl_err_out);

/* Perform HTTP GET (default 30s timeout, no custom headers).
 * On success returns body length and writes HTTP status to *status_out.
 * On failure returns -1. */
int64_t flow_http_get(const char *url, char *buf, int64_t buflen, int64_t *status_out);

/* Perform HTTP POST with raw body and content-type header (default 30s). */
int64_t flow_http_post(const char *url, const char *content_type, const char *body,
                       char *buf, int64_t buflen, int64_t *status_out);

#ifdef __cplusplus
}
#endif

#endif /* FLOW_HTTP_H */
