"""Known bugs found while expanding coverage (flow-test-coverage).

Each test asserts the CORRECT behavior and is marked strict xfail, so it
starts failing loudly the moment the bug is fixed and the mark should be
removed.
"""

from flow.parser import parse_flow_code
from flow.type_checker import TypeChecker


def check(source: str):
    return TypeChecker().check(parse_flow_code(source))


EFFECT_PRELUDE = """
effect Scale {
    apply(x: i32) -> i32,
}

capability Doubler {
    effect Scale,
    function apply(x: i32) -> i32 {
        return x * 2
    },
}
"""


def test_guarded_bool_arm_should_not_count_as_coverage():
    result = check(
        """
        function f(b: bool) -> i32 {
            match b {
                true if 1 == 2 => { return 1 }
                false => { return 0 }
            }
            return -1
        }
        """
    )
    assert result.errors == []
    # Correct behavior: the guarded `true` arm does not guarantee
    # coverage, so this match is non-exhaustive and must warn.
    assert any("do not cover both" in w for w in result.warnings)


def test_effect_call_outside_handle_block_should_type_check():
    result = check(
        EFFECT_PRELUDE
        + """
        function main() -> i32 {
            let a: i32 = Scale.apply(1)
            return 0
        }
        """
    )
    assert result.errors == []


def test_effect_call_inside_unrelated_handle_type_checks_by_signature():
    result = check(
        EFFECT_PRELUDE
        + """
        effect Offset {
            shift(x: i32) -> i32,
        }

        function main() -> i32 {
            handle Scale with Doubler {
                let b: i32 = Offset.shift(1)
            }
            return 0
        }
        """
    )
    assert result.errors == []


def test_capability_parameter_method_call_type_checks_by_effect_signature():
    result = check(
        EFFECT_PRELUDE
        + """
        function use_scale(scale: capability Scale) -> i32 {
            return scale.apply(2)
        }
        """
    )
    assert result.errors == []


def test_capability_parameter_method_call_wrong_type_is_rejected():
    result = check(
        EFFECT_PRELUDE
        + """
        function use_scale(scale: capability Scale) -> i32 {
            return scale.apply("bad")
        }
        """
    )
    assert any("Scale.apply' argument 1 expects i32, got string" in e for e in result.errors)


def test_effect_call_wrong_argument_type_is_rejected():
    result = check(
        EFFECT_PRELUDE
        + """
        function main() -> i32 {
            let a: i32 = Scale.apply("bad")
            return a
        }
        """
    )
    assert any("Scale.apply' argument 1 expects i32, got string" in e for e in result.errors)


def test_effect_call_wrong_arity_is_rejected():
    result = check(
        EFFECT_PRELUDE
        + """
        function main() -> i32 {
            let a: i32 = Scale.apply()
            return a
        }
        """
    )
    assert any("Scale.apply' expects 1 argument(s), got 0" in e for e in result.errors)


def test_unknown_effect_operation_is_rejected():
    result = check(
        EFFECT_PRELUDE
        + """
        function main() -> i32 {
            let a: i32 = Scale.missing(1)
            return a
        }
        """
    )
    assert "Effect 'Scale' has no operation 'missing'" in result.errors


TRAIT_METHOD_PRELUDE = """
trait Averager {
    function average(self) -> f32
}

struct RunningStats {
    sum: f32,
    count: i32
}

impl Averager for RunningStats {
    function average(self) -> f32 {
        return self.sum / self.count
    }
}
"""


def test_concrete_trait_impl_method_call_type_checks():
    result = check(
        TRAIT_METHOD_PRELUDE
        + """
        function main() -> f32 {
            let stats: RunningStats = RunningStats { sum: 9.0, count: 3 }
            return stats.average()
        }
        """
    )
    assert result.errors == []


def test_empty_array_literal_can_initialize_typed_struct_array():
    result = check(
        """
        struct MusicNote {
            midi: i32,
            duration: i32
        }

        function main() -> i32 {
            let notes: array<MusicNote, 128> = []
            return 0
        }
        """
    )
    assert result.errors == []


def test_method_sugar_resolves_pointer_receiver_function():
    source = """
    struct Reader {
        count: i32
    }

    function get_count(reader: ptr<Reader>) -> i32 {
        return reader.count
    }

    function main() -> i32 {
        let reader: Reader = Reader { count: 3 }
        return reader.get_count()
    }
    """
    result = check(source)
    assert result.errors == []


def test_array_scalar_alias_is_compatible_with_generic_array():
    result = check(
        """
        extern {
            function array_f32(size: i32) -> ptr<f32>
        }

        function takes_array(xs: array_f32) -> i32 {
            return 0
        }

        function main() -> i32 {
            let xs: array_f32 = array_f32(4)
            let ys: array<f32> = array_f32(4)
            return takes_array(ys)
        }
        """
    )
    assert result.errors == []


def test_concrete_generic_struct_fields_type_check_before_monomorphization():
    result = check(
        """
        struct Box<T> {
            value: T,
            has_value: bool
        }

        struct Pair<A, B> {
            first: A,
            second: B
        }

        function main() -> i32 {
            let box: Box<i32> = Box<i32> { value: 42, has_value: true }
            let pair: Pair<i32, f32> = Pair<i32, f32> { first: box.value, second: 2.5 }
            return pair.first
        }
        """
    )
    assert result.errors == []


# The C lowering checks that lived here (extern names, bare null, pointer
# receiver method sugar, handle-bound effect parameters) are the golden
# tests/cgen/cov_known_bugs_calls.
