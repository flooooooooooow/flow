#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

/* ===== Effect Handler Runtime ===== */

/* Effect handler vtable for Log */
typedef struct {
    void (*emit)(char*);
    void (*level)(int32_t);
} Log_Handler;

static Log_Handler* _current_Log_handler = NULL;

void Log_emit(char* message) {
    if (_current_Log_handler && _current_Log_handler->emit) {
        _current_Log_handler->emit(message);
    }
}

void Log_level(int32_t lvl) {
    if (_current_Log_handler && _current_Log_handler->level) {
        _current_Log_handler->level(lvl);
    }
}


void ConsoleLogger_emit(char* message);
void ConsoleLogger_level(int32_t lvl);
void SilentLogger_emit(char* message);
void SilentLogger_level(int32_t lvl);

/* ConsoleLogger handler for Log */
static Log_Handler _ConsoleLogger_Log_vtable = {
    .emit = ConsoleLogger_emit,
    .level = ConsoleLogger_level,
};

/* SilentLogger handler for Log */
static Log_Handler _SilentLogger_Log_vtable = {
    .emit = SilentLogger_emit,
    .level = SilentLogger_level,
};

/* ===== End Effect Handler Runtime ===== */

int32_t do_work(int32_t x);
int32_t process(int32_t n);
int32_t main();

void ConsoleLogger_emit(char* message) {
    printf("%s\n", message);
    return;
}

void ConsoleLogger_level(int32_t lvl) {
    printf("Log level: %d\n", lvl);
    return;
}

void SilentLogger_emit(char* message) {
    return;
}

void SilentLogger_level(int32_t lvl) {
    return;
}

int32_t do_work(int32_t x) {
    Log_emit("Starting work...");
    int32_t result = (x * 2);
    Log_emit("Work complete!");
    return result;
}

int32_t process(int32_t n) {
    Log_level(1);
    int32_t sum = 0;
    int32_t i = 0;
    while (i < n) {
        sum = (sum + i);
        i = (i + 1);
    }
    Log_emit("Processing done");
    return sum;
}

int32_t main() {
    printf("=== Test with ConsoleLogger ===\n");
    /* handle Log with ConsoleLogger */
    {
        Log_Handler* _prev_Log_handler = _current_Log_handler;
        _current_Log_handler = &_ConsoleLogger_Log_vtable;

        int32_t r1 = do_work(21);
        printf("Result: %d\n", r1);

        _current_Log_handler = _prev_Log_handler;
    }
    printf("\n=== Test with SilentLogger ===\n");
    /* handle Log with SilentLogger */
    {
        Log_Handler* _prev_Log_handler = _current_Log_handler;
        _current_Log_handler = &_SilentLogger_Log_vtable;

        int32_t r2 = do_work(10);
        printf("Result: %d\n", r2);

        _current_Log_handler = _prev_Log_handler;
    }
    printf("\n=== Test nested handles ===\n");
    /* handle Log with ConsoleLogger */
    {
        Log_Handler* _prev_Log_handler = _current_Log_handler;
        _current_Log_handler = &_ConsoleLogger_Log_vtable;

        Log_emit("Outer scope");
        /* handle Log with SilentLogger */
        {
            Log_Handler* _prev_Log_handler = _current_Log_handler;
            _current_Log_handler = &_SilentLogger_Log_vtable;

            Log_emit("This should be silent");

            _current_Log_handler = _prev_Log_handler;
        }
        Log_emit("Back to outer scope");

        _current_Log_handler = _prev_Log_handler;
    }
    return 0;
}
