# RFC: Algebraic Effects Continuation Limitation

## Status
Accepted (Documentation Only)

## Context
Flow supports a capability-based algebraic effect system, where `effect` defines operations and `capability` implements handlers. The handlers are installed via `handle ... with ...` for a dynamic scope.

However, as noted in `docs/effects-showcase.md` and `#564`, handlers in Flow are exclusively **tail-resumptive**. 

When a handler operation is invoked, it behaves like a standard function call: the operation executes and returns directly to the original call site. The handler cannot capture, manipulate, or invoke the remainder of the computation (the continuation) as a first-class value.

## Limitations

Because continuations are not exposed as first-class objects, the following patterns are not expressible:

1. **Abort**: A handler cannot decline to resume. It must return to the call site. It cannot cancel or short-circuit the execution of the block enclosed by the `handle` statement. This means exceptions cannot be encoded via effects.
2. **Retry**: A handler cannot run the continuation again with different state or inputs. To model a retry, the caller itself must explicitly loop. 
3. **Multi-shot**: A handler cannot invoke the continuation multiple times. This means generators (yielding multiple values), backtracking search, or scheduler encodings are not possible. 

## Architectural Justification
Flow intentionally maps effect dispatch directly to `_Thread_local` pointer lookups and standard C ABI function calls (via vtables). 

To support abort, retry, or multi-shot continuations, the compiler would need to perform Continuation-Passing Style (CPS) transformation, use heap-allocated stacks, or generate complex state machines. This conflicts with Flow's emphasis on zero-overhead predictability, integration with the C ABI, and deterministic memory usage.

This limitation is a structural design choice, optimizing for the 80% of effect use cases (dependency injection, logging, configuration, metrics) that only require tail resumption.

## Conclusion
The current implementation of algebraic effects as tail-resumptive handlers is the intended design. There are no plans to add general, resumable, or multi-shot continuations to the language. Users requiring complex control flow must implement it explicitly using loops, standard returns, or dedicated constructs rather than effect handlers.
