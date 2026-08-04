"""Known bugs found while expanding coverage (flow-test-coverage).

Each test asserts the CORRECT behavior and is marked strict xfail, so it
starts failing loudly the moment the bug is fixed and the mark should be
removed.
"""

from flow.parser import parse_flow_code
from flow.c_generator import flow_to_c
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


def test_concrete_trait_impl_method_call_lowers_to_impl_function():
    c = flow_to_c(
        parse_flow_code(
            TRAIT_METHOD_PRELUDE
            + """
            function main() -> i32 {
                let stats: RunningStats = RunningStats { sum: 9.0, count: 3 }
                let avg: f32 = stats.average()
                return 0
            }
            """
        )
    )
    assert "RunningStats_Averager_average" in c
    assert "average(stats)" not in c


def test_capability_parameter_call_lowers_to_mangled_overload():
    c = flow_to_c(
        parse_flow_code(
            """
            effect Database {
                function query(sql: string) -> string
            }

            struct MockDB {}

            impl Database for MockDB {
                function query(self, sql: string) -> string {
                    return "ok"
                }
            }

            function read_name(db: capability Database) -> string {
                return db.query("select")
            }

            function main() -> i32 {
                let db: MockDB = MockDB {}
                let name: string = read_name(db)
                return 0
            }
            """
        )
    )
    assert "read_name_capability_Database(&db)" in c
    assert "read_name(db)" not in c


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

    c = flow_to_c(parse_flow_code(source))
    assert "get_count_ptr_Reader(" in c
    assert "&(reader)" in c
    assert "get_count(reader)" not in c


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


def test_c_backend_appends_handle_bound_effect_parameters_to_helper_calls():
    c = flow_to_c(
        parse_flow_code(
            """
            extern {
                function array_f32(size: i32) -> ptr<f32>
            }

            effect GPU {
                function allocate(size: i32) -> i32
            }

            capability CUDAGPU {
                effect GPU,
                function allocate(size: i32) -> i32 {
                    return size
                },
            }

            function helper(xs: array_f32, gpu: GPU) -> array_f32 {
                let size: i32 = gpu.allocate(4)
                return xs
            }

            function main() -> i32 {
                let xs: array_f32 = array_f32(4)
                handle GPU with CUDAGPU {
                    let ys: array_f32 = helper(xs)
                }
                return 0
            }
            """
        )
    )
    assert "helper_array_f32_GPU(xs, (GPU){  })" in c
    assert "helper(xs)" not in c


def test_c_backend_keeps_extern_calls_unmangled():
    c = flow_to_c(
        parse_flow_code(
            """
            extern {
                function cuda_malloc(size: i32) -> i64
            }

            function main() -> i32 {
                let ptr: i64 = cuda_malloc(16)
                return 0
            }
            """
        )
    )
    assert "int64_t cuda_malloc(int32_t size);" in c
    assert "cuda_malloc(16)" in c
    assert "cuda_malloc_i32" not in c
