# FlowDB - In-Memory Database Demo

A comprehensive demonstration of the FLOW programming language, implementing
a fully-functional in-memory database system.

## Quick Start

```bash
# Run the working demo
./flow run examples/flowdb/demo.flow
```

## Overview

FlowDB is a teaching project that showcases all major FLOW language features
through a practical, real-world application: a simplified database engine.

## Project Structure

```
flowdb/
├── demo.flow      # ✅ WORKING - Complete demo of all features
├── main.flow      # Full multi-module version (WIP)
├── types.flow     # Core data types (Value, Row, Schema, etc.)
├── traits.flow    # Trait definitions (Display, Comparable, Hashable)
├── engine.flow    # Database engine with effects
├── query.flow     # Query system with pattern matching
├── index.flow     # Hash index and algorithms
└── README.md      # This file
```

## Features Demonstrated

### 1. Core Language Features

- **Structs**: `Row`, `Value`, `TableSchema`, `ColumnDef`, etc.
- **Functions**: With typed parameters and return types
- **Control Flow**: `if/elif/else`, `while`, `for`, `match`
- **Arrays**: Fixed-size arrays with compile-time bounds
- **Constants**: `const MAX_ROWS: i32 = 1000`

### 2. Type System

- **Primitives**: `i32`, `i64`, `f32`, `f64`, `bool`, `string`
- **Generics**: `Box<T>`, `Pair<K, V>` with monomorphization
- **Option Types**: `Option_i32`, `Option_f64` for nullable values
- **Result Types**: `Result_f64_string` for error handling

### 3. Effect System

Effects make side-effects explicit and controllable:

```flow
effect Logger {
    log_info(message: string) -> void,
    log_error(message: string) -> void,
}

capability ConsoleLogger {
    effect Logger,
    function log_info(message: string) -> void {
        printf("[INFO] %s\n", message)
    }
}

# Usage: Effects are scoped by handlers
handle Logger with ConsoleLogger {
    Logger.log_info("This is logged!")
}
```

### 4. Traits

Traits enable ad-hoc polymorphism:

```flow
trait Display {
    function show(self) -> void
}

impl Display for Value {
    function show(self) -> void {
        # Pretty print the value
    }
}

# Call trait method
Value_Display_show(some_value)
```

### 5. Pattern Matching

```flow
match query_type {
    0 => printf("SELECT\n")
    1 => printf("INSERT\n")
    2 => printf("UPDATE\n")
    _ => printf("UNKNOWN\n")
}
```

### 6. Module System

```flow
import "types.flow"
import "stdlib/option.flow"

export function public_api() -> void { ... }
function private_helper() -> void { ... }
```

## Database Features

### Schema Definition
- Column definitions with types
- Primary key support
- Nullable/Non-null constraints
- Index markers

### Data Operations
- INSERT with auto-incrementing IDs
- SELECT with WHERE clauses
- DELETE (soft delete)
- UPDATE support

### Query Engine
- Full table scans
- Condition-based filtering
- Aggregate functions: COUNT, SUM, AVG, MIN, MAX
- Comparison operators: =, !=, <, <=, >, >=

### Indexing
- Hash-based index structure
- Fast equality lookups
- Bucket-based collision handling

### Transactions
- BEGIN/COMMIT/ROLLBACK
- Snapshot isolation (simplified)

## Running the Demo

```bash
# From the transpile directory - run the complete working demo
./flow run examples/flowdb/demo.flow

# The demo showcases:
# - Structs and user-defined types
# - Generics (Box<T>, Pair<K,V>)
# - Pattern matching
# - Effects and capabilities
# - Traits and implementations  
# - Option and Result types
# - Algorithms (prime checking, fibonacci)
```

## Sample Output

```
╔══════════════════════════════════════════════════════════════════╗
║     ███████╗██╗      ██████╗ ██╗    ██╗██████╗ ██████╗           ║
║     ██╔════╝██║     ██╔═══██╗██║    ██║██╔══██╗██╔══██╗          ║
║     █████╗  ██║     ██║   ██║██║ █╗ ██║██║  ██║██████╔╝          ║
║     ██╔══╝  ██║     ██║   ██║██║███╗██║██║  ██║██╔══██╗          ║
║     ██║     ███████╗╚██████╔╝╚███╔███╔╝██████╔╝██████╔╝          ║
║     ╚═╝     ╚══════╝ ╚═════╝  ╚══╝╚══╝ ╚═════╝ ╚═════╝           ║
║           In-Memory Database Demo - FLOW Language                ║
╚══════════════════════════════════════════════════════════════════╝

[INFO] Inserting new row
[QUERY] INSERT - 1 rows affected
...

+----------+----------+----------+----------+----------+
| id       | name     | age      | salary   | active   |
+----------+----------+----------+----------+----------+
| 1        | 'Alice'  | 30       | 75000.0  | TRUE     |
| 2        | 'Bob'    | 25       | 55000.0  | TRUE     |
| 3        | 'Carol'  | 35       | 85000.0  | TRUE     |
...
```

## Educational Value

This project demonstrates how to:

1. **Design type-safe data structures** using FLOW's struct system
2. **Manage side effects** explicitly with the effect system
3. **Implement polymorphism** via traits
4. **Handle errors safely** with Option and Result types
5. **Organize code** into modules
6. **Use pattern matching** for control flow
7. **Build generic containers** with type parameters

## Limitations

This is a teaching project with intentional simplifications:

- Fixed maximum table size (16 rows) due to no heap allocation
- No actual file I/O (in-memory only)
- Simplified transaction model
- String comparison not fully implemented
- No JOIN operations

## License

Part of the FLOW Programming Language project.
MIT License.
