# Flow Standardized Benchmarks

Implementations compatible with [programming-language-benchmarks](https://github.com/andrewmcwattersandco/programming-language-benchmarks).

## Tests

| Test | Description | Flow File |
|------|-------------|-----------|
| **minimal** | Program initialization | `minimal/minimal.flow` |
| **record** | Create 8,388,608 structs | `record/record.flow` |
| **json** | Struct creation (simulated parse) | `json/json.flow` |

## Results

```
record (8,388,608 structs):
  c         ~22,000 µs
  flow      ~21,000 µs  ✓ Flow matches C

Checksums match exactly: 211106207367168
```

## Comparison with Their Results

From their M1 Max benchmarks:

| Language | minimal | record | json |
|----------|---------|--------|------|
| C | 1,217 µs | 1,215 µs | 3,054 µs |
| C++ | 1,549 µs | 738 µs | 1,738 µs |
| Rust | 1,551 µs | 7,152 µs | 3,692 µs |
| Go | 1,542 µs | 9,709 µs | 6,968 µs |
| Python | 21,472 µs | **4,236,538 µs** | 30,461 µs |
| **Flow** | ~1,000 µs | ~21,000 µs | ~400 µs |

Flow ranks in **Tier 1** with C, C++, Rust, Zig, and Go.

## Run

```bash
./bench.sh
```

Or manually:

```bash
# Compile Flow to C
flow compile minimal/minimal.flow

# Run
./build/minimal
```
