#!/bin/bash
FILES="examples/basics/bigint_smoke.flow
examples/basics/bubble_sort.flow
examples/basics/factorial.flow
examples/basics/fibonacci.flow
examples/basics/gcd.flow
examples/basics/hashmap_i64_smoke.flow
examples/basics/loops.flow
examples/basics/palindrome.flow
examples/basics/prime_numbers.flow
examples/basics/simple_search.flow
examples/crypto/sha256.flow
examples/demos/ui_layout_flow/src/main.flow
examples/evolution/robot_connect.flow
examples/generics_traits/composition_car_engine.flow
examples/generics_traits/composition_team_employee.flow
examples/generics_traits/oop_counter.flow
examples/generics_traits/oop_person.flow
examples/wasm/fs_counter.flow
examples/wasm/fs_preload.flow
examples/wasm/python_embed.flow
examples/wasm/tcp_echo.flow"

for f in $FILES; do
    echo "Recording $f"
    # To fix the regex match, we replace / with \/
    pattern=$(echo "$f" | sed 's/\//\\\//g')
    ./flow tool compiler/scripts/parity_mlir.flow --record --only "^$pattern\$"
done
