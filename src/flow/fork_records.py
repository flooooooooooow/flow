"""Post-parse desugaring of anonymous fork records.

An anonymous fork block

    let s = mic |> { spectrum = fft |> magnitude, loudness = rms }

parses to a `ForkRecord` node. This pass turns each one into a synthesized
struct plus a `StructLiteral` of it, so every later phase (type checker, all
backends, tooling) sees an ordinary named record and needs no special support:

    struct __ForkRecord_0 { spectrum: Spectrum, loudness: f32 }
    let s = __ForkRecord_0 { spectrum: magnitude(fft(mic)), loudness: rms(mic) }

A field's type is the declared return type of the outermost call in its branch
value — pipeline branches bottom out in a function call, so this is exact for
the common case. Branches that don't end in a resolvable call (e.g. a method
call on an inferred receiver) can't be typed structurally here; those must name
the record explicitly (`source |> Name { … }`), and this pass says so.

Records with identical field signatures share one synthesized struct, so
repeated forks don't emit a struct apiece.
"""

import dataclasses
from typing import Dict, List, Optional

from .parser import (
    ForkRecord,
    StructLiteral,
    StructDecl,
    Parameter,
    FunctionCall,
    FunctionDecl,
    Type,
)


class ForkRecordError(Exception):
    """A fork record whose field types cannot be inferred structurally."""


def _return_type_map(declarations: List[object]) -> Dict[str, Type]:
    """Map function name -> declared return type (includes externs)."""
    types: Dict[str, Type] = {}
    for decl in declarations:
        if isinstance(decl, FunctionDecl) and decl.return_type is not None:
            # First declaration wins; overloads share a return type in practice.
            types.setdefault(decl.name, decl.return_type)
    return types


def _infer_field_type(value: object, returns: Dict[str, Type]) -> Optional[Type]:
    """Field type = return type of the outermost call in a branch value."""
    if isinstance(value, FunctionCall):
        return returns.get(value.name)
    return None


class _Desugarer:
    def __init__(self, returns: Dict[str, Type]):
        self._returns = returns
        self._synth: List[StructDecl] = []
        # signature (tuple of (name, type_str)) -> synthesized struct name
        self._by_sig: Dict[tuple, str] = {}

    @property
    def synthesized(self) -> List[StructDecl]:
        return self._synth

    def _struct_for(self, fork: ForkRecord) -> StructLiteral:
        params: List[Parameter] = []
        sig_parts: List[tuple] = []
        for field_name, value in fork.fields:
            field_type = _infer_field_type(value, self._returns)
            if field_type is None:
                raise ForkRecordError(
                    "cannot infer the type of fork field '{}'"
                    " (line {}): an anonymous fork record's fields must end in a"
                    " function whose return type is known. Name the record"
                    " instead: `source |> RecordName {{ ... }}`".format(
                        field_name, fork.line
                    )
                )
            params.append(Parameter(field_name, field_type))
            sig_parts.append((field_name, getattr(field_type, "name", str(field_type))))

        sig = tuple(sig_parts)
        name = self._by_sig.get(sig)
        if name is None:
            name = "__ForkRecord_{}".format(len(self._by_sig))
            self._by_sig[sig] = name
            self._synth.append(StructDecl(name=name, fields=params))
        return StructLiteral(name, list(fork.fields))

    def transform(self, node: object) -> object:
        """Recursively replace ForkRecord nodes, innermost first."""
        if isinstance(node, ForkRecord):
            # Resolve nested forks inside branch values first.
            node.fields = [(fn, self.transform(v)) for fn, v in node.fields]
            return self._struct_for(node)
        if dataclasses.is_dataclass(node) and not isinstance(node, type):
            for f in dataclasses.fields(node):
                setattr(node, f.name, self.transform(getattr(node, f.name)))
            return node
        if isinstance(node, list):
            return [self.transform(x) for x in node]
        if isinstance(node, tuple):
            return tuple(self.transform(x) for x in node)
        return node


def desugar_fork_records(declarations: List[object]) -> List[object]:
    """Rewrite anonymous fork records in-place; append synthesized structs."""
    returns = _return_type_map(declarations)
    desugarer = _Desugarer(returns)
    for decl in declarations:
        desugarer.transform(decl)
    if desugarer.synthesized:
        # Prepend so the struct is declared before any use.
        return list(desugarer.synthesized) + list(declarations)
    return declarations
