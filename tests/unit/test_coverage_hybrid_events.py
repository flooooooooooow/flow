"""Coverage tests for hybrid events (flow-test-coverage).

Extends tests/unit/test_hybrid_events.py with cases it does not touch:
several when-blocks firing in declaration order within one step and an
event whose reset targets a different state than the guard. The
compile-and-run half of this file now lives in
tests/lang/test_hybrid_events.flow.
"""

from flow.c_generator import flow_to_c
from flow.parser import Lexer, Parser


def parse_lowered(code: str):
    return Parser(Lexer(code), source=code).parse()


TWO_WHENS = """
flow F {
    state t : f64 = 0.0
    state a : f64 = 1.0
    state b : f64 = 0.0
    t evolves as 1.0
    when t reaches 1.0 {
        a becomes a * 2.0
    }
    when t reaches 1.0 {
        b becomes a
    }
}
"""


class TestMultipleWhenBlockOrdering:
    def test_each_when_gets_its_own_guard_memory(self):
        c = flow_to_c(parse_lowered(TWO_WHENS + "function main() -> i32 { return 0 }"))
        struct_body = c.split("struct F {", 1)[1].split("};", 1)[0]
        assert "double __guard_0_prev;" in struct_body
        assert "double __guard_1_prev;" in struct_body

    def test_guards_are_checked_in_declaration_order(self):
        c = flow_to_c(parse_lowered(TWO_WHENS + "function main() -> i32 { return 0 }"))
        step = c.split("void F_step(F* self, double dt) {", 1)[1].split("\n}", 1)[0]
        first = step.index("double __g_0 =")
        second = step.index("double __g_1 =")
        assert first < second
        # The first event's reset is fully applied before the second
        # event's reset is staged, so event 1 observes event 0's writes.
        write_a = step.index("self->a = __reset_0_a;")
        stage_b = step.index("double __reset_1_b = self->a;")
        assert write_a < stage_b

    # test_second_event_observes_first_events_reset ran the two-when program
    # and read a and b off stdout. It is now the TwoWhens section of
    # tests/lang/test_hybrid_events.flow.


class TestCrossStateReset:
    COUNTER = """
flow Counter {
    state t : f64 = 0.0
    state hits : f64 = 0.0
    t evolves as 1.0
    when t reaches 1.0 {
        hits becomes hits + 1.0
    }
}
"""

    def test_guard_state_differs_from_reset_target(self):
        c = flow_to_c(parse_lowered(self.COUNTER + "function main() -> i32 { return 0 }"))
        step = c.split("void Counter_step(Counter* self, double dt) {", 1)[1]
        step = step.split("\n}", 1)[0]
        # Guard watches t; the reset writes hits and never writes t.
        assert "double __g_0 = (self->t - 1.0);" in step
        assert "self->hits = __reset_0_hits;" in step
        reset_block = step.split("if ((__g_0", 1)[1].split("}", 1)[0]
        assert "self->t =" not in reset_block

    # test_event_fires_once_when_guard_state_keeps_growing is now the Counter
    # section of tests/lang/test_hybrid_events.flow.

# TestGuardNearThresholdTinyDt held three compile-and-run cases: an exact hit
# at dt = 2^-10, a crossing between steps at an unrepresentable threshold,
# and an asymptotic approach that must never fire. All three are now the
# Tiny / Cross / Approach sections of tests/lang/test_hybrid_events.flow.


