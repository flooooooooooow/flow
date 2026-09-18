from pygments import lex
from pygments.token import Keyword, Name

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


def main() -> None:
    tokens = list(lex(SOURCE, FlowLexer()))
    assert any(token is Name.Function and value == "main" for token, value in tokens)
    assert any(token in Keyword and value == "if" for token, value in tokens)
    assert any(value == "# comment" for _, value in tokens)


if __name__ == "__main__":
    main()
