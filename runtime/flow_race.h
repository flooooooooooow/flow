/* Lightweight race / lock-order detector hooks (opt-in via FLOW_RACE=1). */
#ifndef FLOW_RACE_H
#define FLOW_RACE_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

void flow_race_init(void);      /* → lib/runtime/race.flow */
int flow_race_enabled(void);    /* → lib/runtime/race.flow */

/* Mutex / lock-order tracking */
void flow_race_mutex_lock(void *mu);
void flow_race_mutex_unlock(void *mu);

/* Channel / shared-object touch (addr = buffer or channel ptr) */
void flow_race_read(void *addr, int32_t size);
void flow_race_write(void *addr, int32_t size);

#ifdef __cplusplus
}
#endif

#endif /* FLOW_RACE_H */
