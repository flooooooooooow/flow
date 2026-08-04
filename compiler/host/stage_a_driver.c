/* Tiny C host for Stage-A-emitted flowc frontend.
 *
 * Usage: stage_a_driver <in.flow> <out.c>
 *
 * Reads source with libc, calls flowc_parse_program + flowc_cgen_emit from
 * compiler/build/flowc_frontend.o, writes emitted C.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "flowc_frontend.h"

enum {
    FLOWC_SRC_CAP = 65536,
    FLOWC_OUT_CAP = 262144,
    FLOWC_AST_CAP = 8192
};

static int read_file(const char *path, uint8_t *buf, int32_t cap, int32_t *out_n) {
    FILE *fp = fopen(path, "rb");
    if (fp == NULL) {
        return -1;
    }
    size_t n = fread(buf, 1, (size_t)(cap - 1), fp);
    if (ferror(fp)) {
        fclose(fp);
        return -1;
    }
    fclose(fp);
    buf[n] = 0;
    *out_n = (int32_t)n;
    return 0;
}

static int write_file(const char *path, const uint8_t *buf, int32_t n) {
    FILE *fp = fopen(path, "wb");
    if (fp == NULL) {
        return -1;
    }
    size_t w = fwrite(buf, 1, (size_t)n, fp);
    if (fclose(fp) != 0 || (int32_t)w != n) {
        return -1;
    }
    return 0;
}

int main(int argc, char **argv) {
    if (argc != 3) {
        fprintf(stderr, "usage: %s <in.flow> <out.c>\n", argv[0]);
        return 2;
    }

    uint8_t *src = (uint8_t *)malloc(FLOWC_SRC_CAP);
    if (src == NULL) {
        fprintf(stderr, "stage_a_driver: malloc src failed\n");
        return 1;
    }
    memset(src, 0, FLOWC_SRC_CAP);

    int32_t nsrc = 0;
    if (read_file(argv[1], src, FLOWC_SRC_CAP, &nsrc) != 0 || nsrc <= 0) {
        fprintf(stderr, "stage_a_driver: read '%s' failed\n", argv[1]);
        free(src);
        return 1;
    }

    /* Parser / AstArena layouts must match Stage-A emit (see flowc_frontend.h). */
    Parser p = flowc_parser_new(src, nsrc, FLOWC_AST_CAP);
    int32_t root = flowc_parse_program(&p);
    if (root < 0 || p.err != 0) {
        fprintf(stderr, "stage_a_driver: parse failed (err=%d cur.start=%d arena_len=%d)\n",
                p.err, p.cur.start, p.arena.len);
        flowc_parser_free(p);
        free(src);
        return 1;
    }

    uint8_t *out = (uint8_t *)malloc(FLOWC_OUT_CAP);
    if (out == NULL) {
        fprintf(stderr, "stage_a_driver: malloc out failed\n");
        flowc_parser_free(p);
        free(src);
        return 1;
    }
    memset(out, 0, FLOWC_OUT_CAP);

    /* AstArena is passed by value (pointer + len/cap); matches flowc_cgen_emit. */
    int32_t nout = flowc_cgen_emit(p.arena, root, src, out, FLOWC_OUT_CAP);
    if (nout <= 0) {
        fprintf(stderr, "stage_a_driver: cgen failed\n");
        free(out);
        flowc_parser_free(p);
        free(src);
        return 1;
    }

    if (write_file(argv[2], out, nout) != 0) {
        fprintf(stderr, "stage_a_driver: write '%s' failed\n", argv[2]);
        free(out);
        flowc_parser_free(p);
        free(src);
        return 1;
    }

    free(out);
    flowc_parser_free(p);
    free(src);
    return 0;
}
