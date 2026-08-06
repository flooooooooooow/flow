/* Lightweight race / lock-order detector hooks (opt-in via FLOW_RACE=1). */
#ifndef FLOW_RACE_H
#define FLOW_RACE_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Hooks called by lib/stdlib/concurrent.flow — defined in flow_race.c. */
void flow_race_mutex_lock(void *mu);
void flow_race_mutex_unlock(void *mu);
void flow_race_read(void *addr, int32_t size);
void flow_race_write(void *addr, int32_t size);

/* Detector state and logic — defined in lib/runtime/race.flow. */
void flow_race_init(void);
int32_t flow_race_enabled(void);
void flow_race_note_edge(void *before, void *after);
void flow_race_shadow_touch(void *addr, int32_t size, int32_t is_write,
                            int64_t tid, int32_t locked);

#ifdef __cplusplus
}
#endif

#endif /* FLOW_RACE_H */
