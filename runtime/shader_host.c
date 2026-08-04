/* Tiny host for `./flow shader` demos. */
#include "shader_view_metal.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static char *read_entry(const char *path) {
    FILE *f = fopen(path, "r");
    if (!f) {
        return NULL;
    }
    char buf[256];
    if (!fgets(buf, sizeof(buf), f)) {
        fclose(f);
        return NULL;
    }
    fclose(f);
    size_t n = strlen(buf);
    while (n > 0 && (buf[n - 1] == '\n' || buf[n - 1] == '\r' || buf[n - 1] == ' ')) {
        buf[--n] = '\0';
    }
    return strdup(buf);
}

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "Usage: %s <file.metal> <entry_fn> [width] [height] [max_frames]\n", argv[0]);
        return 1;
    }
    const char *metal = argv[1];
    const char *entry = argv[2];
    int width = argc > 3 ? atoi(argv[3]) : 800;
    int height = argc > 4 ? atoi(argv[4]) : 600;
    int max_frames = argc > 5 ? atoi(argv[5]) : 0;

    /* Optional: sibling .entry file overrides argv entry */
    char entry_path[1024];
    snprintf(entry_path, sizeof(entry_path), "%s", metal);
    size_t len = strlen(entry_path);
    if (len > 6 && strcmp(entry_path + len - 6, ".metal") == 0) {
        strcpy(entry_path + len - 6, ".entry");
        char *from_file = read_entry(entry_path);
        if (from_file && from_file[0]) {
            entry = from_file;
            int rc = flow_shader_show_file(metal, entry, width, height, max_frames);
            free(from_file);
            return rc;
        }
        free(from_file);
    }

    return flow_shader_show_file(metal, entry, width, height, max_frames);
}
