#!/usr/bin/env python3
"""FIR-G: dense-ID structure-of-arrays program graph (Phase 1).

See docs/project/fir-g.md. This is the columnar Program Graph Database —
not a replacement for C/MLIR emitters.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Dict, List, Optional, Tuple


class OpCode(IntEnum):
    NOP = 0
    CONST = 1
    PARAM = 2
    LOAD = 3
    STORE = 4
    BINOP = 5
    UNOP = 6
    CALL = 7
    RET = 8
    BR = 9
    COND_BR = 10
    PHI = 11
    ALLOCA = 12
    GEP = 13
    CAST = 14
    EFFECT = 15
    OTHER = 255


# Effect / purity bitflags on functions (packed for GPU-friendly propagation later).
EFF_NONE = 0
EFF_READS_MEMORY = 1 << 0
EFF_WRITES_MEMORY = 1 << 1
EFF_ALLOCATES = 1 << 2
EFF_IO = 1 << 3          # print / filesystem / network (coarse)
EFF_FFI = 1 << 4
EFF_PANIC = 1 << 5
EFF_ATOMIC = 1 << 6
EFF_THREAD = 1 << 7
EFF_GPU = 1 << 8
EFF_UNKNOWN = 1 << 15


@dataclass
class FirG:
    """Columnar program graph. All identities are dense ints."""

    # --- functions ---
    func_name: List[str] = field(default_factory=list)
    func_first_block: List[int] = field(default_factory=list)
    func_block_count: List[int] = field(default_factory=list)
    func_flags: List[int] = field(default_factory=list)
    func_effect_bits: List[int] = field(default_factory=list)
    func_is_extern: List[bool] = field(default_factory=list)

    # --- blocks ---
    block_function: List[int] = field(default_factory=list)
    block_first_op: List[int] = field(default_factory=list)
    block_op_count: List[int] = field(default_factory=list)

    # --- ops ---
    op_opcode: List[int] = field(default_factory=list)
    op_function: List[int] = field(default_factory=list)
    op_block: List[int] = field(default_factory=list)
    op_flags: List[int] = field(default_factory=list)
    op_operand_begin: List[int] = field(default_factory=list)
    op_operand_count: List[int] = field(default_factory=list)
    op_result_begin: List[int] = field(default_factory=list)
    op_result_count: List[int] = field(default_factory=list)
    # CALL extras: callee function id (-1 if unknown / indirect)
    op_callee: List[int] = field(default_factory=list)

    # --- operands (edges into values) ---
    operand_value: List[int] = field(default_factory=list)
    operand_owner: List[int] = field(default_factory=list)
    operand_index: List[int] = field(default_factory=list)

    # --- values ---
    value_producer: List[int] = field(default_factory=list)  # op id or -1
    value_type_id: List[int] = field(default_factory=list)
    value_flags: List[int] = field(default_factory=list)
    value_use_begin: List[int] = field(default_factory=list)
    value_use_count: List[int] = field(default_factory=list)

    # --- type table ---
    type_name: List[str] = field(default_factory=list)

    # --- symbol maps (build helpers; not GPU columns) ---
    _func_by_name: Dict[str, int] = field(default_factory=dict, repr=False)
    _type_by_name: Dict[str, int] = field(default_factory=dict, repr=False)

    # --- CSR call graph (filled by analyses or finalize) ---
    call_row_offsets: List[int] = field(default_factory=list)
    call_columns: List[int] = field(default_factory=list)  # callee func ids
    call_edge_sites: List[int] = field(default_factory=list)  # op ids

    def num_funcs(self) -> int:
        return len(self.func_name)

    def num_blocks(self) -> int:
        return len(self.block_function)

    def num_ops(self) -> int:
        return len(self.op_opcode)

    def num_values(self) -> int:
        return len(self.value_producer)

    def num_operands(self) -> int:
        return len(self.operand_value)

    def intern_type(self, name: str) -> int:
        tid = self._type_by_name.get(name)
        if tid is not None:
            return tid
        tid = len(self.type_name)
        self.type_name.append(name)
        self._type_by_name[name] = tid
        return tid

    def add_function(
        self,
        name: str,
        *,
        is_extern: bool = False,
        effect_bits: int = EFF_NONE,
        flags: int = 0,
    ) -> int:
        fid = len(self.func_name)
        self.func_name.append(name)
        self.func_first_block.append(0)
        self.func_block_count.append(0)
        self.func_flags.append(flags)
        self.func_effect_bits.append(effect_bits)
        self.func_is_extern.append(is_extern)
        self._func_by_name[name] = fid
        return fid

    def add_block(self, function_id: int) -> int:
        bid = len(self.block_function)
        self.block_function.append(function_id)
        self.block_first_op.append(self.num_ops())
        self.block_op_count.append(0)
        if self.func_block_count[function_id] == 0:
            self.func_first_block[function_id] = bid
        self.func_block_count[function_id] += 1
        return bid

    def add_value(self, producer_op: int, type_id: int, flags: int = 0) -> int:
        vid = len(self.value_producer)
        self.value_producer.append(producer_op)
        self.value_type_id.append(type_id)
        self.value_flags.append(flags)
        self.value_use_begin.append(0)
        self.value_use_count.append(0)
        return vid

    def add_op(
        self,
        opcode: OpCode,
        function_id: int,
        block_id: int,
        *,
        operand_values: Optional[List[int]] = None,
        result_type_ids: Optional[List[int]] = None,
        callee: int = -1,
        flags: int = 0,
    ) -> Tuple[int, List[int]]:
        """Append an op; returns (op_id, result_value_ids)."""
        op_id = self.num_ops()
        operand_values = operand_values or []
        result_type_ids = result_type_ids or []

        op_operand_begin = self.num_operands()
        for i, vid in enumerate(operand_values):
            self.operand_value.append(vid)
            self.operand_owner.append(op_id)
            self.operand_index.append(i)

        result_ids: List[int] = []
        result_begin = self.num_values()
        for tid in result_type_ids:
            result_ids.append(self.add_value(op_id, tid))

        self.op_opcode.append(int(opcode))
        self.op_function.append(function_id)
        self.op_block.append(block_id)
        self.op_flags.append(flags)
        self.op_operand_begin.append(op_operand_begin)
        self.op_operand_count.append(len(operand_values))
        self.op_result_begin.append(result_begin)
        self.op_result_count.append(len(result_ids))
        self.op_callee.append(callee)

        if self.block_op_count[block_id] == 0:
            self.block_first_op[block_id] = op_id
        self.block_op_count[block_id] += 1
        return op_id, result_ids

    def finalize_uses(self) -> None:
        """Build per-value use lists from operand edges (CSR-style counts)."""
        n = self.num_values()
        uses: List[List[int]] = [[] for _ in range(n)]
        for ei, vid in enumerate(self.operand_value):
            if 0 <= vid < n:
                uses[vid].append(self.operand_owner[ei])
        # Flatten into value_use_* — store use op ids in a side list for Phase 1
        # by encoding begin/count over a packed use_ops array.
        self._use_ops: List[int] = []
        for vid in range(n):
            self.value_use_begin[vid] = len(self._use_ops)
            self.value_use_count[vid] = len(uses[vid])
            self._use_ops.extend(uses[vid])

    def build_call_graph_csr(self) -> None:
        """CSR: for each function, list of callee function ids (with call sites)."""
        F = self.num_funcs()
        edges: List[List[Tuple[int, int]]] = [[] for _ in range(F)]
        for op in range(self.num_ops()):
            if self.op_opcode[op] != OpCode.CALL:
                continue
            callee = self.op_callee[op]
            if callee < 0:
                continue
            caller = self.op_function[op]
            edges[caller].append((callee, op))
        self.call_row_offsets = [0]
        self.call_columns = []
        self.call_edge_sites = []
        for f in range(F):
            for callee, site in edges[f]:
                self.call_columns.append(callee)
                self.call_edge_sites.append(site)
            self.call_row_offsets.append(len(self.call_columns))

    def summary(self) -> str:
        return (
            f"FIR-G: funcs={self.num_funcs()} blocks={self.num_blocks()} "
            f"ops={self.num_ops()} values={self.num_values()} "
            f"operands={self.num_operands()} types={len(self.type_name)}"
        )
