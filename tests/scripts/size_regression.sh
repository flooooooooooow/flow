#!/usr/bin/env bash
# The stripped hello_world binary stays small. It is around 80 KB; the limit
# is a generous 200 KB, loose enough to avoid flaky failures and tight enough
# to catch a large regression.
source "$(dirname "$0")/lib.sh"

MAX_SIZE=$((200 * 1024))

check_hello_world_size_regression() {
    t_need strip size
    ./flow compile examples/basics/hello_world.flow
    strip build/hello_world
    local bytes
    bytes="$(($(wc -c < build/hello_world)))"
    a_true "hello_world stripped binary size $bytes is under the $MAX_SIZE byte limit" \
        test "$bytes" -lt "$MAX_SIZE"
}

t_check hello_world_size_regression check_hello_world_size_regression
t_done
