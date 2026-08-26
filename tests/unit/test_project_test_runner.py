from pathlib import Path

from flow.project_test_runner import (
    _discover_files,
    _matches_filter,
    _native_tests,
    _rewrite_native_file,
)


def test_native_test_discovery_and_unique_slugs():
    source = '''
test "delay is exact" {
    expect 1 == 1
}

test "delay is exact" {
    expect 2 == 2
}
'''
    tests = _native_tests(source)
    assert [t.name for t in tests] == ["delay is exact", "delay is exact"]
    assert [t.slug for t in tests] == ["delay_is_exact", "delay_is_exact_2"]


def test_native_test_rewrite_generates_one_main_call():
    source = '''
function helper() -> i32 { return 42 }

test "answer" {
    expect helper() == 42
}

test "other" {
    expect helper() > 0
}
'''
    selected = _native_tests(source)[1]
    rewritten = _rewrite_native_file(source, selected)
    assert 'test "answer"' not in rewritten
    assert 'test "other"' not in rewritten
    assert "function __flow_test_0_answer() -> void" in rewritten
    assert "function __flow_test_1_other() -> void" in rewritten
    assert "__flow_test_1_other()" in rewritten
    assert rewritten.count("function main() -> i32") == 1


def test_discovery_skips_helper_and_wip_files(tmp_path: Path):
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "a.flow").write_text("function main() -> i32 { return 0 }\n")
    (tests / "_helper.flow").write_text("function helper() -> i32 { return 1 }\n")
    wip = tests / "wip"
    wip.mkdir()
    (wip / "later.flow").write_text("function main() -> i32 { return 0 }\n")

    found = _discover_files([tests])
    assert found == [(tests / "a.flow").resolve()]


def test_filter_supports_substring_and_glob():
    case = "tests/delay.flow::integer delay is exact"
    assert _matches_filter(case, "delay")
    assert _matches_filter(case, "tests/delay*")
    assert not _matches_filter(case, "reverb")
