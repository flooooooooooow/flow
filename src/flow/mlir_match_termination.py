"""MLIR exhaustive-control-flow termination parity.

The legacy control-flow lowering materializes synthetic join blocks for matches.
When every arm of an exhaustive match returns, that join is unreachable but
still needs a terminator.  Two extra details matter for valid nested control
flow:

* ``llvm.unreachable`` is itself a terminator and enclosing lowering must not
  append a branch after it.
* once a statement is known to return on every path, later statements in the
  same source block are unreachable and must not be emitted into the dead join.

Keep those rules here while the parity layer remains separate from the legacy
MLIR generator.
"""

from __future__ import annotations

import copy

from .parser import Block, IfStatement, MatchStatement, ReturnStatement, Variable


def _is_unconditional_catch_all(generator, case) -> bool:
    if case.guard is not None or not isinstance(case.pattern, Variable):
        return False

    name = case.pattern.name
    if name == "_":
        return True

    # Enum variants are constants, not binding patterns. Every other bare
    # identifier follows Flow's binding-pattern semantics.
    return getattr(generator, "_enum_variant_owner", {}).get(name) is None


def _block_always_returns(generator, block: Block) -> bool:
    """Whether execution of ``block`` is guaranteed to return.

    This is deliberately stricter than the generator's historical
    ``_block_has_return`` helper, which answers whether *any* nested path has a
    return.  Terminator placement needs an all-paths predicate.
    """

    for stmt in block.statements:
        if _statement_always_returns(generator, stmt):
            return True
    return False


def _match_exhaustively_returns(generator, match_stmt: MatchStatement) -> bool:
    cases = list(match_stmt.cases)
    if not cases or not all(_block_always_returns(generator, case.body) for case in cases):
        return False

    if match_stmt.default_case is not None:
        return _block_always_returns(generator, match_stmt.default_case)

    return _is_unconditional_catch_all(generator, cases[-1])


def _if_always_returns(generator, if_stmt: IfStatement) -> bool:
    if if_stmt.else_block is None:
        return False
    if not _block_always_returns(generator, if_stmt.then_block):
        return False
    if any(not _block_always_returns(generator, block) for _, block in if_stmt.elif_blocks):
        return False
    return _block_always_returns(generator, if_stmt.else_block)


def _statement_always_returns(generator, stmt) -> bool:
    if isinstance(stmt, ReturnStatement):
        return True
    if isinstance(stmt, MatchStatement):
        return _match_exhaustively_returns(generator, stmt)
    if isinstance(stmt, IfStatement):
        return _if_always_returns(generator, stmt)
    if isinstance(stmt, Block):
        return _block_always_returns(generator, stmt)
    return False


def install() -> None:
    from .mlir_generator import MLIRGenerator

    previous_generate_match = MLIRGenerator.generate_match
    previous_generate_block = MLIRGenerator.generate_block
    previous_block_has_terminator = MLIRGenerator._block_has_terminator

    def block_has_terminator(self, block_code: str) -> bool:
        if previous_block_has_terminator(self, block_code):
            return True
        lines = [line.strip() for line in block_code.splitlines() if line.strip()]
        return bool(lines) and lines[-1].startswith("llvm.unreachable")

    def generate_match(self, match_stmt) -> str:
        code = previous_generate_match(self, match_stmt)
        stripped = code.rstrip()
        if _match_exhaustively_returns(self, match_stmt) and stripped.endswith(":"):
            return stripped + f"\n{self.indent()}llvm.unreachable"
        return code

    def generate_block(self, block: Block) -> str:
        # The legacy block walker only stops after a syntactic return/break/
        # continue.  An exhaustive match (or if/else) whose branches all return
        # is just as terminal.  Truncate the copied block so no dead operation
        # can be emitted after its terminator, while leaving the original AST
        # untouched for other backends/passes.
        statements = list(block.statements)
        cutoff = None
        for index, stmt in enumerate(statements):
            if _statement_always_returns(self, stmt):
                cutoff = index + 1
                break

        if cutoff is None or cutoff == len(statements):
            return previous_generate_block(self, block)

        reachable = copy.copy(block)
        reachable.statements = statements[:cutoff]
        return previous_generate_block(self, reachable)

    MLIRGenerator._block_has_terminator = block_has_terminator
    MLIRGenerator.generate_match = generate_match
    MLIRGenerator.generate_block = generate_block
