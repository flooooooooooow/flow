"""MLIR match exhaustiveness termination parity.

The legacy control-flow match lowering always materializes a join block.  When
an unguarded catch-all arm makes a match exhaustive and every arm returns, that
join is unreachable but still needs an MLIR terminator for verifier validity.
"""

from __future__ import annotations

from .parser import Variable


def _is_unconditional_catch_all(generator, case) -> bool:
    if case.guard is not None or not isinstance(case.pattern, Variable):
        return False

    name = case.pattern.name
    if name == "_":
        return True

    # Enum variants are constants, not binding patterns. Every other bare
    # identifier follows Flow's binding-pattern semantics.
    return getattr(generator, "_enum_variant_owner", {}).get(name) is None


def install() -> None:
    from .mlir_generator import MLIRGenerator

    previous_generate_match = MLIRGenerator.generate_match

    def generate_match(self, match_stmt) -> str:
        code = previous_generate_match(self, match_stmt)

        cases = list(match_stmt.cases)
        all_cases_return = bool(cases) and all(
            self._block_has_return(case.body) for case in cases
        )

        if match_stmt.default_case is not None:
            exhaustive_returns = all_cases_return and self._block_has_return(
                match_stmt.default_case
            )
        else:
            exhaustive_returns = (
                all_cases_return
                and bool(cases)
                and _is_unconditional_catch_all(self, cases[-1])
            )

        stripped = code.rstrip()
        if (
            exhaustive_returns
            and stripped.endswith(":")
            and not stripped.endswith("llvm.unreachable")
        ):
            return stripped + f"\n{self.indent()}llvm.unreachable"

        return code

    MLIRGenerator.generate_match = generate_match
