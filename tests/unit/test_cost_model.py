import pytest
from flow.parser import Parser, Lexer
from flow.cost_model import estimate_backend

def parse(code: str):
    return Parser(Lexer(code)).parse()

def test_cost_model_trivial():
    ast = parse("""
function main() -> i32 {
    let mut x: i32 = 0
    return x
}
""")
    assert estimate_backend(ast) == "c"

def test_cost_model_small_loop():
    ast = parse("""
function main() -> i32 {
    let mut sum: i32 = 0
    for i in 0..10 step 1 {
        sum = sum + i
    }
    return sum
}
""")
    assert estimate_backend(ast) == "c"

def test_cost_model_heavy_numeric():
    ast = parse("""
function main() -> i32 {
    let mut sum: f32 = 0.0
    for i in 0..10000000 step 1 {
        sum = sum + (i as f32) * 1.5
    }
    return 0
}
""")
    assert estimate_backend(ast) == "mlir"

def test_cost_model_unsupported():
    ast = parse("""
function main() -> i32 {
    match 1 {
        1 => { return 1 }
        _ => { return 0 }
    }
}
""")
    assert estimate_backend(ast) == "c"
