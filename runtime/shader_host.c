/* Thin argv shim for ./flow shader — orchestration in lib/runtime/shader_host.flow */
#include "shader_view_metal.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Flow-exported */
int32_t flow_shader_host_run(
    int32_t gallery,
    int32_t layout,
    const char *metal,
    const char *entries,
    int32_t width,
    int32_t height,
    int32_t max_frames
);

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr,
            "Usage:\n"
            "  %s [--grid|--cycle] <file.metal> [width] [height] [max_frames]\n"
            "  %s --gallery [--grid|--cycle] <file.metal> <file.entries> [w] [h] [frames]\n",
            argv[0], argv[0]);
        return 1;
    }

    int argi = 1;
    int gallery = 0;
    int layout = FLOW_SHADER_LAYOUT_GRID;

    while (argi < argc && argv[argi][0] == '-') {
        if (strcmp(argv[argi], "--gallery") == 0) {
            gallery = 1;
            argi++;
        } else if (strcmp(argv[argi], "--grid") == 0) {
            layout = FLOW_SHADER_LAYOUT_GRID;
            argi++;
        } else if (strcmp(argv[argi], "--cycle") == 0) {
            layout = FLOW_SHADER_LAYOUT_CYCLE;
            argi++;
        } else {
            break;
        }
    }

    if (argi >= argc) {
        fprintf(stderr, "missing metal path\n");
        return 1;
    }
    const char *metal = argv[argi++];
    const char *entries = "";
    int width = gallery ? 1280 : 800;
    int height = gallery ? 720 : 600;
    int max_frames = 0;

    if (gallery) {
        if (argi >= argc) {
            fprintf(stderr, "missing entries path\n");
            return 1;
        }
        entries = argv[argi++];
        if (argi < argc) width = atoi(argv[argi++]);
        if (argi < argc) height = atoi(argv[argi++]);
        if (argi < argc) max_frames = atoi(argv[argi++]);
    } else {
        /* Guess sibling .entries */
        static char entries_guess[1024];
        snprintf(entries_guess, sizeof(entries_guess), "%s", metal);
        size_t len = strlen(entries_guess);
        if (len > 6 && strcmp(entries_guess + len - 6, ".metal") == 0) {
            strcpy(entries_guess + len - 6, ".entries");
            FILE *ef = fopen(entries_guess, "r");
            if (ef) {
                fclose(ef);
                entries = entries_guess;
                gallery = 1;
                width = 1280;
                height = 720;
            }
        }
        if (argi < argc && argv[argi][0] >= '0' && argv[argi][0] <= '9') {
            width = atoi(argv[argi++]);
            if (argi < argc) height = atoi(argv[argi++]);
            if (argi < argc) max_frames = atoi(argv[argi++]);
        } else {
            if (argi < argc && argv[argi][0] != '-' &&
                !(argv[argi][0] >= '0' && argv[argi][0] <= '9')) {
                argi++; /* skip entry name; Flow uses shader_frag default */
            }
            if (argi < argc) width = atoi(argv[argi++]);
            if (argi < argc) height = atoi(argv[argi++]);
            if (argi < argc) max_frames = atoi(argv[argi++]);
        }
    }

    return (int)flow_shader_host_run(
        gallery, layout, metal, entries, width, height, max_frames
    );
}
