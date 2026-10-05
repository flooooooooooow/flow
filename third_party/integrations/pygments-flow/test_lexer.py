import sys
from pathlib import Path

from pygments import lex
from pygments.token import Error, Keyword, Name

from flow_pygments import FlowLexer


SOURCE = """function main() -> i32 {
    let mut counter: i32 = 0
    # comment
    if counter == 0 {
        println("Flow")
    }
    return 0
}
"""

REPO_ROOT = Path(__file__).resolve().parents[3]
REAL_SOURCES = (
    REPO_ROOT / "examples/basics/hello_world.flow",
    REPO_ROOT / "examples/basics/gcd.flow",
    REPO_ROOT / "examples/evolution/pendulum.flow",
)


def assert_no_error_tokens(source: str, name: str) -> None:
    errors = [(token, value) for token, value in lex(source, FlowLexer()) if token is Error]
    assert not errors, f"{name}: Pygments emitted Error tokens: {errors[:10]}"


def main() -> None:
    tokens = list(lex(SOURCE, FlowLexer()))
    assert any(token is Name.Function and value == "main" for token, value in tokens)
    assert any(token in Keyword and value == "if" for token, value in tokens)
    assert any(value == "# comment" for _, value in tokens)
    assert_no_error_tokens(SOURCE, "synthetic smoke test")

    for path in REAL_SOURCES:
        assert path.is_file(), f"missing representative Flow source: {path}"
        assert_no_error_tokens(path.read_text(), str(path.relative_to(REPO_ROOT)))

    print("Testing entire corpus for regression check...")
    files = list(REPO_ROOT.glob('**/*.flow'))
    files = [f for f in files if "third_party" not in str(f) and ".venv" not in str(f)]
    failed = 0
    for path in files:
        try:
            source = path.read_text()
            errors = [(token, value) for token, value in lex(source, FlowLexer()) if token is Error]
            if errors:
                print(f"FAIL: {path.relative_to(REPO_ROOT)}")
                print(f"  Errors: {errors[:5]}")
                failed += 1
        except Exception as e:
            print(f"ERROR reading/lexing {path.relative_to(REPO_ROOT)}: {e}")
            failed += 1

    if failed:
        print(f"\n{failed} files failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
