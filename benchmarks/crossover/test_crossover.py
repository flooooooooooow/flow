import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from flow.parser import Parser, Lexer
from flow.cost_model import estimate_backend

def main():
    corpus = list(Path(__file__).parent.glob("*.flow"))
    corpus.sort()
    
    print(f"{'Program':<30} | {'Predicted Backend'}")
    print("-" * 50)
    for f in corpus:
        with open(f) as file:
            lexer = Lexer(file.read())
            ast = Parser(lexer).parse()
        pred = estimate_backend(ast)
        print(f"{f.name:<30} | {pred}")

if __name__ == "__main__":
    main()
