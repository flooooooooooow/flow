/* Host for `./flow shader` — single or gallery mode. */
#include "shader_view_metal.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr,
            "Usage:\n"
            "  %s <file.metal> [entry] [width] [height] [max_frames]\n"
            "  %s --gallery <file.metal> <file.entries> [width] [height] [max_frames]\n",
            argv[0], argv[0]);
        return 1;
    }

    int argi = 1;
    int gallery = 0;
    if (strcmp(argv[argi], "--gallery") == 0) {
        gallery = 1;
        argi++;
    }
    if (argi >= argc) {
        fprintf(stderr, "missing metal path\n");
        return 1;
    }
    const char *metal = argv[argi++];

    if (gallery) {
        if (argi >= argc) {
            fprintf(stderr, "missing entries path\n");
            return 1;
        }
        const char *entries = argv[argi++];
        int width = argi < argc ? atoi(argv[argi++]) : 960;
        int height = argi < argc ? atoi(argv[argi++]) : 540;
        int max_frames = argi < argc ? atoi(argv[argi++]) : 0;
        return flow_shader_show_gallery_file(metal, entries, width, height, max_frames);
    }

    /* Auto-gallery: sibling *_gallery.entries or stem.entries */
    char entries_guess[1024];
    snprintf(entries_guess, sizeof(entries_guess), "%s", metal);
    size_t len = strlen(entries_guess);
    if (len > 6 && strcmp(entries_guess + len - 6, ".metal") == 0) {
        /* foo_gallery.metal -> foo_gallery.entries */
        strcpy(entries_guess + len - 6, ".entries");
        FILE *ef = fopen(entries_guess, "r");
        if (ef) {
            fclose(ef);
            const char *entry_arg = argi < argc ? argv[argi++] : NULL;
            (void)entry_arg;
            int width = 960;
            int height = 540;
            int max_frames = 0;
            /* Remaining args: [entry] [w] [h] [frames] — if first looks numeric, it's width */
            if (argi < argc && argv[argi][0] >= '0' && argv[argi][0] <= '9') {
                width = atoi(argv[argi++]);
                if (argi < argc) height = atoi(argv[argi++]);
                if (argi < argc) max_frames = atoi(argv[argi++]);
            } else {
                if (argi < argc) argi++; /* skip explicit entry; gallery uses all */
                if (argi < argc) width = atoi(argv[argi++]);
                if (argi < argc) height = atoi(argv[argi++]);
                if (argi < argc) max_frames = atoi(argv[argi++]);
            }
            return flow_shader_show_gallery_file(metal, entries_guess, width, height, max_frames);
        }
        /* single: foo_fill.metal + foo_fill.entry */
        char entry_path[1024];
        snprintf(entry_path, sizeof(entry_path), "%s", metal);
        size_t elen = strlen(entry_path);
        strcpy(entry_path + elen - 6, ".entry");
        const char *entry = argi < argc ? argv[argi++] : "shader_frag";
        FILE *f = fopen(entry_path, "r");
        if (f) {
            static char buf[256];
            if (fgets(buf, sizeof(buf), f)) {
                size_t n = strlen(buf);
                while (n > 0 && (buf[n - 1] == '\n' || buf[n - 1] == '\r')) buf[--n] = '\0';
                if (n > 0) entry = buf;
            }
            fclose(f);
        }
        int width = argi < argc ? atoi(argv[argi++]) : 800;
        int height = argi < argc ? atoi(argv[argi++]) : 600;
        int max_frames = argi < argc ? atoi(argv[argi++]) : 0;
        return flow_shader_show_file(metal, entry, width, height, max_frames);
    }

    fprintf(stderr, "expected a .metal path\n");
    return 1;
}
