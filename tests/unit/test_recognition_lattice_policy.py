from flow.optimization_policy import CallablePolicy, CostPolicy, LoweringCandidate, choose_candidate, evaluate_candidates
from flow.parser import FlowDecl, Lexer, Parser
from flow.recognition_lattice import recognition_residual, refines_on_corpus

BASE = """
flow Controller {
    state x : f64 = 0.0
    input u : f64
    output y : f64 = x
    param k : f64 = 2.0
    solver { dt 1 ms method euler }
    x evolves as k * u
    recognize { numerical memory }
}
"""

def flow_of(code: str) -> FlowDecl:
    declarations = Parser(Lexer(code), source=code).parse(expand_flows=False)
    return next(item for item in declarations if isinstance(item, FlowDecl))

def test_memory_can_erase_a_distinction_numerical_retains():
    before = flow_of(BASE)
    after = flow_of(BASE.replace("x evolves as k * u", "x evolves as k * u + 1.0"))
    residual = recognition_residual(before, after, "memory", "numerical")
    assert residual is not None

def test_numerical_refines_memory_on_simple_dynamics_corpus():
    corpus = (flow_of(BASE), flow_of(BASE.replace("k * u", "k * u + 1.0")), flow_of(BASE.replace("k * u", "-k * u")))
    assert refines_on_corpus(corpus, "numerical", "memory")

def test_policy_cannot_select_semantically_illegal_candidate():
    source = flow_of(BASE)
    legal = flow_of(BASE.replace("k * u", "k * u + 1.0"))
    illegal = flow_of(BASE.replace("state x : f64", "state x : i32"))
    candidates = (
        LoweringCandidate("gpu-fast", "mlir-gpu", legal, 1.0),
        LoweringCandidate("neural-favourite", "neural", illegal, 0.01),
    )
    policy = CallablePolicy(lambda candidate: 1000.0 if candidate.name == "neural-favourite" else 1.0)
    chosen = choose_candidate(source, candidates, ("memory",), policy)
    assert chosen is not None
    assert chosen.candidate.name == "gpu-fast"

def test_cost_policy_ranks_legal_parallel_lowerings():
    source = flow_of(BASE)
    same = flow_of(BASE)
    candidates = (
        LoweringCandidate("c", "c", same, 4.0),
        LoweringCandidate("mlir", "mlir-cpu", same, 2.0),
        LoweringCandidate("gpu", "mlir-gpu", same, 1.0),
    )
    evaluations = evaluate_candidates(source, candidates, ("numerical",), CostPolicy())
    assert all(item.admissible for item in evaluations)
    chosen = choose_candidate(source, candidates, ("numerical",), CostPolicy())
    assert chosen is not None
    assert chosen.candidate.backend == "mlir-gpu"
