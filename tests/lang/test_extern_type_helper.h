// test_extern_type_helper.h
// Helper header for test_extern_type.flow
#pragma once
#include <stdint.h>

typedef struct TestOpaque TestOpaque;

static inline TestOpaque* test_opaque_create(int32_t value) {
    TestOpaque* p = (TestOpaque*)0;
    (void)value;
    return p;
}

static inline int32_t test_opaque_value(TestOpaque* p) {
    (void)p;
    return 42;
}
