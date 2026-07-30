"""Coverage tests for zero-cost effect substitution (flow-test-coverage).

Extends tests/unit/test_zero_cost_effects.py with the multi-effect and
control-flow cases it does not touch: `handle A, B with C` statements,
zipped handler lists, handle blocks inside loops and conditionals, a
capability serving several effects, nested handles of different effects,
and effect calls in deeply nested blocks inside a handle.
"""

from flow.c_generator import flow_to_c
from flow.parser import parse_flow_code


TWO_EFFECTS = """
effect Log {
    info(msg: string) -> void,
}

effect Audit {
    record(msg: string) -> void,
}

capability Console {
    effect Log,
    function info(msg: string) -> void {
        printf("[console] %s\\n", msg)
    },
}

capability Ledger {
    effect Audit,
    function record(msg: string) -> void {
        printf("[ledger] %s\\n", msg)
    },
}

capability Both {
    effect Log, Audit,
    function info(msg: string) -> void {
        printf("[both/i] %s\\n", msg)
    },
    function record(msg: string) -> void {
        printf("[both/r] %s\\n", msg)
    },
}
"""


def gen(main_body: str) -> str:
    code = TWO_EFFECTS + "function main() -> i32 {\n%s\n    return 0\n}\n" % main_body
    return flow_to_c(parse_flow_code(code))


def main_body_of(c_code: str) -> str:
    """Generated C of main() only, so prelude/vtable lines don't match."""
    start = c_code.index("int32_t main(")
    return c_code[start:]


class TestMultiEffectHandle:
    def test_single_capability_serves_both_effects_directly(self):
        body = main_body_of(gen(
            """
    handle Log, Audit with Both {
        Log.info("a")
        Audit.record("b")
    }
"""
        ))
        assert 'Both_info("a")' in body
        assert 'Both_record("b")' in body
        assert 'Log_info("a")' not in body
        assert 'Audit_record("b")' not in body

    def test_zipped_handler_list_pairs_effects_positionally(self):
        body = main_body_of(gen(
            """
    handle Log, Audit with Console, Ledger {
        Log.info("x")
        Audit.record("y")
    }
"""
        ))
        assert 'Console_info("x")' in body
        assert 'Ledger_record("y")' in body

    def test_multi_effect_handle_installs_and_restores_both_vtables(self):
        body = main_body_of(gen(
            """
    handle Log, Audit with Both {
        Log.info("a")
    }
"""
        ))
        assert "_current_Log_handler = &_Both_Log_vtable;" in body
        assert "_current_Audit_handler = &_Both_Audit_vtable;" in body
        assert "_current_Log_handler = _prev_Log_handler;" in body
        assert "_current_Audit_handler = _prev_Audit_handler;" in body

    def test_capability_with_two_effects_handled_for_one_leaves_other_dynamic(self):
        # `handle Log with Both` only binds Log; Audit calls in the block
        # must keep dynamic dispatch even though Both could serve them.
        body = main_body_of(gen(
            """
    handle Log with Both {
        Log.info("a")
        Audit.record("b")
    }
"""
        ))
        assert 'Both_info("a")' in body
        assert 'Audit_record("b")' in body
        assert 'Both_record("b")' not in body


class TestHandleInControlFlow:
    def test_handle_block_inside_for_loop(self):
        body = main_body_of(gen(
            """
    for i in 0 to 3 {
        handle Log with Console {
            Log.info("loop")
        }
    }
"""
        ))
        assert 'Console_info("loop")' in body
        assert 'Log_info("loop")' not in body

    def test_handle_block_inside_conditional(self):
        body = main_body_of(gen(
            """
    if 1 == 1 {
        handle Log with Console {
            Log.info("then")
        }
    } else {
        handle Log with Both {
            Log.info("else")
        }
    }
"""
        ))
        assert 'Console_info("then")' in body
        assert 'Both_info("else")' in body

    def test_call_after_loop_handle_is_dynamic_again(self):
        body = main_body_of(gen(
            """
    for i in 0 to 3 {
        handle Log with Console {
            Log.info("in")
        }
    }
    Log.info("out")
"""
        ))
        assert 'Console_info("in")' in body
        assert 'Log_info("out")' in body
        assert 'Console_info("out")' not in body

    def test_effect_calls_in_deeply_nested_blocks_stay_direct(self):
        body = main_body_of(gen(
            """
    handle Log with Console {
        for i in 0 to 2 {
            if i == 1 {
                while i < 2 {
                    Log.info("deep")
                    break
                }
            }
        }
    }
"""
        ))
        assert 'Console_info("deep")' in body
        assert 'Log_info("deep")' not in body


class TestNestedDifferentEffects:
    def test_inner_handle_of_other_effect_keeps_outer_binding(self):
        body = main_body_of(gen(
            """
    handle Log with Console {
        handle Audit with Ledger {
            Log.info("both bound")
            Audit.record("both bound")
        }
        Log.info("after inner")
        Audit.record("after inner")
    }
"""
        ))
        # Inside the inner block both effects are direct.
        assert 'Console_info("both bound")' in body
        assert 'Ledger_record("both bound")' in body
        # After the inner block Log stays direct, Audit reverts to dynamic.
        assert 'Console_info("after inner")' in body
        assert 'Audit_record("after inner")' in body
        assert 'Ledger_record("after inner")' not in body

    def test_inner_handle_restores_only_its_own_effect(self):
        body = main_body_of(gen(
            """
    handle Log with Console {
        handle Audit with Ledger {
            Audit.record("x")
        }
    }
"""
        ))
        assert "_current_Audit_handler = &_Ledger_Audit_vtable;" in body
        assert "_current_Audit_handler = _prev_Audit_handler;" in body
        # The inner block never touches the Log handler.
        inner = body.split("_current_Audit_handler = &_Ledger_Audit_vtable;", 1)[1]
        inner = inner.split("_current_Audit_handler = _prev_Audit_handler;", 1)[0]
        assert "_current_Log_handler =" not in inner
