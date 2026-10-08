/* Native twin of benchmarks/cross_harness/cold/file_transform (#746): write
 * 200 lines, read them back, uppercase, write, remove both files. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

static int write_all(const char *path, const char *buf, size_t n) {
    FILE *f = fopen(path, "wb");
    if (f == NULL) {
        return 0;
    }
    size_t w = fwrite(buf, 1, n, f);
    fclose(f);
    return w == n;
}

int main(void) {
    const char *in_path = "/tmp/flow_file_transform_in.txt";
    const char *out_path = "/tmp/flow_file_transform_out.txt";

    char *text = (char *)malloc(8192);
    if (text == NULL) {
        return 1;
    }
    int32_t written = 0;
    for (int32_t line = 0; line < 200; line += 1) {
        int n = snprintf(text + written, (size_t)(8192 - written),
                         "key_%d%d%d=value_data_payload_string_line_\n",
                         (line / 100) % 10, (line / 10) % 10, line % 10);
        if (n < 0) {
            free(text);
            return 1;
        }
        written += n;
    }
    if (!write_all(in_path, text, (size_t)written)) {
        free(text);
        return 1;
    }
    free(text);

    FILE *f = fopen(in_path, "rb");
    if (f == NULL) {
        return 2;
    }
    char *data = (char *)malloc((size_t)written + 1);
    if (data == NULL) {
        fclose(f);
        return 2;
    }
    size_t len = fread(data, 1, (size_t)written + 1, f);
    fclose(f);
    if ((int32_t)len != written) {
        free(data);
        return 2;
    }

    int32_t total_bytes = 0;
    for (size_t i = 0; i < len; i += 1) {
        if (data[i] >= 'a' && data[i] <= 'z') {
            data[i] = (char)(data[i] - 32);
        }
        total_bytes += 1;
    }
    if (!write_all(out_path, data, len)) {
        free(data);
        return 3;
    }
    free(data);

    remove(in_path);
    remove(out_path);
    if (total_bytes <= 0) {
        return 4;
    }
    return 0;
}
