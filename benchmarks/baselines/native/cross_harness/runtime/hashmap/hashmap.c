#include <stdint.h>
#include <stdlib.h>

static int32_t hash_i64(int64_t k) {
    uint32_t h = (uint32_t)(int32_t)(k ^ (k >> 32));
    h ^= h >> 16;
    h *= 0x7feb352du;
    h ^= h >> 15;
    h *= 0x846ca68bu;
    h ^= h >> 16;
    return (int32_t)(h & 0x7FFFFFFFu);
}

int main(void) {
    const int32_t n = 4096;
    const int32_t cap = 8192;
    int64_t *keys = (int64_t *)calloc((size_t)cap, sizeof(int64_t));
    int64_t *values = (int64_t *)calloc((size_t)cap, sizeof(int64_t));
    int32_t *occupied = (int32_t *)calloc((size_t)cap, sizeof(int32_t));
    if (keys == NULL || values == NULL || occupied == NULL) {
        return 1;
    }

    for (int32_t i = 0; i < n; i += 1) {
        int64_t key = (int64_t)i;
        int64_t value = (int64_t)i * 3;
        int32_t slot = hash_i64(key) % cap;
        int32_t probes = 0;
        while (probes < cap) {
            if (occupied[slot] == 0) {
                keys[slot] = key;
                values[slot] = value;
                occupied[slot] = 1;
                break;
            }
            if (occupied[slot] == 1 && keys[slot] == key) {
                values[slot] = value;
                break;
            }
            slot += 1;
            if (slot >= cap) {
                slot = 0;
            }
            probes += 1;
        }
        if (probes >= cap) {
            return 2;
        }
    }

    int64_t checksum = 0;
    for (int32_t i = 0; i < n; i += 1) {
        int64_t key = (int64_t)i;
        int32_t slot = hash_i64(key) % cap;
        int64_t found = -1;
        int32_t probes = 0;
        while (probes < cap) {
            if (occupied[slot] == 0) {
                break;
            }
            if (occupied[slot] == 1 && keys[slot] == key) {
                found = values[slot];
                break;
            }
            slot += 1;
            if (slot >= cap) {
                slot = 0;
            }
            probes += 1;
        }
        if (found < 0) {
            return 3;
        }
        checksum += found;
    }

    free(keys);
    free(values);
    free(occupied);
    if (checksum != 25159680LL) {
        return 4;
    }
    return 0;
}
