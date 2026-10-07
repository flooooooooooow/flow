#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
    const char *in_path = "/tmp/flow_buffered_io_in.txt";
    const char *out_path = "/tmp/flow_buffered_io_out.txt";

    char *text = (char *)malloc(65536);
    if (text == NULL) {
        return 1;
    }
    int32_t written = 0;
    for (int32_t line = 0; line < 2000; line += 1) {
        int n = snprintf(
            text + written,
            (size_t)(65536 - written),
            "key_%d%d%d%d=value_data_payload_string_line_\n",
            (line / 1000) % 10,
            (line / 100) % 10,
            (line / 10) % 10,
            line % 10
        );
        if (n < 0) {
            free(text);
            return 1;
        }
        written += n;
    }

    FILE *in = fopen(in_path, "wb");
    if (in == NULL) {
        free(text);
        return 1;
    }
    if (fwrite(text, 1, (size_t)written, in) != (size_t)written) {
        fclose(in);
        free(text);
        return 1;
    }
    fclose(in);
    free(text);

    FILE *rd = fopen(in_path, "rb");
    if (rd == NULL) {
        return 2;
    }
    if (fseek(rd, 0, SEEK_END) != 0) {
        fclose(rd);
        return 2;
    }
    long len = ftell(rd);
    if (len != (long)written) {
        fclose(rd);
        return 2;
    }
    if (fseek(rd, 0, SEEK_SET) != 0) {
        fclose(rd);
        return 2;
    }
    uint8_t *p = (uint8_t *)malloc((size_t)len);
    if (p == NULL) {
        fclose(rd);
        return 2;
    }
    if (fread(p, 1, (size_t)len, rd) != (size_t)len) {
        fclose(rd);
        free(p);
        return 2;
    }
    fclose(rd);

    int32_t checksum = 0;
    for (long i = 0; i < len; i += 1) {
        int32_t c = (int32_t)p[i];
        if (c >= 97 && c <= 122) {
            c = c - 32;
            p[i] = (uint8_t)c;
        }
        checksum += c;
    }

    FILE *out = fopen(out_path, "wb");
    if (out == NULL) {
        free(p);
        return 3;
    }
    if (fwrite(p, 1, (size_t)len, out) != (size_t)len) {
        fclose(out);
        free(p);
        return 3;
    }
    fclose(out);
    free(p);

    remove(in_path);
    remove(out_path);
    if (checksum <= 0) {
        return 4;
    }
    return 0;
}
