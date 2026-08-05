"""Post-parse desugaring of fork blocks (`source |> [Record] { a = f, ... }`).

Both the named and anonymous forms parse to a `ForkBlock` whose branches are
pipelines over a `ForkSource` placeholder. This pass:

  1. Binds `source` to a temp `let` when it is non-trivial (a call, not a
     variable/field), so the piped value is evaluated **once** even though it
     feeds every branch — hoisting the binding just above the statement the fork
     appears in.
  2. Substitutes that binding (or the trivial source directly) for `ForkSource`.
  3. For the anonymous form, infers each field's type from the outermost call's
     return type and synthesizes a struct; identical field signatures share one.
  4. Rewrites the `ForkBlock` into a `StructLiteral`.

Everything downstream — type checker, all backends, tooling — then sees an
ordinary named record and needs no fork-specific support.
"""

import dataclasses
from typing import Dict, List, Optional

from .parser import (
    ForkBlock,
    ForkSource,
    FlowStage,
    FlowSyntaxError,
    StructLiteral,
    StructDecl,
    Parameter,
    VarDecl,
    Variable,
    FieldAccess,
    Literal,
    FunctionCall,
    FunctionDecl,
    Block,
    Type,
)


class ForkRecordError(FlowSyntaxError):
    """A fork block that can't be lowered (uninferrable record, or a flow-stage
    param block used outside a flow output).

    Subclasses FlowSyntaxError so it is a clean rejection of invalid source —
    not an internal crash — for callers (and the fuzzer) that distinguish the
    two by `SyntaxError`.
    """


def _return_type_map(declarations: List[object]) -> Dict[str, Type]:
    types: Dict[str, Type] = {}
    for decl in declarations:
        if isinstance(decl, FunctionDecl) and decl.return_type is not None:
            types.setdefault(decl.name, decl.return_type)
    return types


def _is_trivial(expr: object) -> bool:
    """A source cheap and side-effect-free to repeat across branches."""
    if isinstance(expr, (Variable, Literal, ForkSource)):
        return True
    if isinstance(expr, FieldAccess):
        return _is_trivial(expr.object)
    return False


def _subst_source(node: object, replacement: object) -> object:
    """Replace every ForkSource in a branch template with `replacement`."""
    if isinstance(node, ForkSource):
        return replacement
    if dataclasses.is_dataclass(node) and not isinstance(node, type):
        for f in dataclasses.fields(node):
            setattr(node, f.name, _subst_source(getattr(node, f.name), replacement))
        return node
    if isinstance(node, list):
        return [_subst_source(x, replacement) for x in node]
    if isinstance(node, tuple):
        return tuple(_subst_source(x, replacement) for x in node)
    return node


class _Desugarer:
    def __init__(self, returns: Dict[str, Type]):
        self._returns = returns
        self._synth: List[StructDecl] = []
        self._by_sig: Dict[tuple, str] = {}
        self._tmp = 0

    @property
    def synthesized(self) -> List[StructDecl]:
        return self._synth

    # --- record synthesis / lowering -------------------------------------

    def _infer_field_type(self, value: object) -> Optional[Type]:
        if isinstance(value, FunctionCall):
            return self._returns.get(value.name)
        return None

    def _lower(self, fork: ForkBlock, source: object) -> StructLiteral:
        """Turn a fork into a struct literal, substituting `source` for holes."""
        fields = [(name, _subst_source(tmpl, source)) for name, tmpl in fork.branches]
        if fork.record_name is not None:
            return StructLiteral(fork.record_name, fields)

        params: List[Parameter] = []
        sig: List[tuple] = []
        for field_name, value in fields:
            ftype = self._infer_field_type(value)
            if ftype is None:
                raise ForkRecordError(
                    "cannot infer the type of fork field '{}' (line {}): an"
                    " anonymous fork record's fields must end in a function whose"
                    " return type is known. Name the record instead:"
                    " `source |> RecordName {{ ... }}`".format(field_name, fork.line)
                )
            params.append(Parameter(field_name, ftype))
            sig.append((field_name, getattr(ftype, "name", str(ftype))))

        key = tuple(sig)
        name = self._by_sig.get(key)
        if name is None:
            name = "__ForkRecord_{}".format(len(self._by_sig))
            self._by_sig[key] = name
            self._synth.append(StructDecl(name=name, fields=params))
        return StructLiteral(name, fields)

    # --- traversal with statement-level hoisting -------------------------

    def _resolve(self, node: object, hoisted: List[object]) -> object:
        """Resolve forks in an expression, appending temp `let`s to `hoisted`.

        Nested `Block`s are handled by `_process_block` so their forks hoist
        into *their* statement list, not an outer one.
        """
        if isinstance(node, Block):
            self._process_block(node)
            return node
        if isinstance(node, FlowStage):
            # Flow-stage param blocks are resolved only inside a flow output
            # pipeline (by _expand_flow_pipelines). One reaching here was used
            # somewhere that has no flow-stage meaning.
            raise ForkRecordError(
                "flow stage params `{} {{ ... }}` (line {}) are only valid for a"
                " flow used as a pipeline stage inside a flow `output`".format(
                    node.name, node.line
                )
            )
        if isinstance(node, ForkBlock):
            # Resolve nested forks in the source and branch templates first.
            source = self._resolve(node.source, hoisted)
            node.branches = [
                (name, self._resolve(tmpl, hoisted)) for name, tmpl in node.branches
            ]
            # Hoist a non-trivial source to a temp so it is evaluated once. This
            # needs a surrounding statement list; without one (`hoisted is None`)
            # we fall back to inlining the source into each branch.
            if hoisted is not None and not _is_trivial(source):
                tmp_name = "__fork_src_{}".format(self._tmp)
                self._tmp += 1
                hoisted.append(
                    VarDecl(name=tmp_name, type=Type(name="auto"),
                            initializer=source, is_mutable=False)
                )
                source = Variable(tmp_name)
            return self._lower(node, source)
        if dataclasses.is_dataclass(node) and not isinstance(node, type):
            for f in dataclasses.fields(node):
                setattr(node, f.name, self._resolve(getattr(node, f.name), hoisted))
            return node
        if isinstance(node, list):
            return [self._resolve(x, hoisted) for x in node]
        if isinstance(node, tuple):
            return tuple(self._resolve(x, hoisted) for x in node)
        return node

    def _process_block(self, block: Block) -> None:
        new_statements: List[object] = []
        for stmt in block.statements:
            hoisted: List[object] = []
            stmt = self._resolve(stmt, hoisted)
            new_statements.extend(hoisted)
            new_statements.append(stmt)
        block.statements = new_statements

    def transform_decl(self, decl: object) -> None:
        # Pass None (no enclosing statement list): forks reachable through a
        # Block hoist into it; any outside one inline their source instead.
        self._resolve(decl, None)


def desugar_forks(declarations: List[object]) -> List[object]:
    """Rewrite fork blocks in-place; prepend any synthesized record structs."""
    desugarer = _Desugarer(_return_type_map(declarations))
    for decl in declarations:
        desugarer.transform_decl(decl)
    if desugarer.synthesized:
        return list(desugarer.synthesized) + list(declarations)
    return declarations
