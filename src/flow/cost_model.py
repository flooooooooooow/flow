from typing import List, Any
from .parser import FunctionDecl, ForStatement, BinaryOperation, MatchStatement, Literal

def estimate_backend(ast: List[Any]) -> str:
    """
    Cost model to predict whether C or MLIR is the best backend for the program.
    Returns "c" or "mlir".
    """
    
    total_loop_iters = 0
    max_loop_depth = 0
    elementwise_ops = 0
    has_unsupported = False
    
    class Visitor:
        def __init__(self):
            self.depth = 0
        
        def visit(self, node):
            nonlocal total_loop_iters, max_loop_depth, elementwise_ops, has_unsupported
            
            # Fallback for MLIR unsupported constructs
            if isinstance(node, MatchStatement):
                # MLIR match statement support is limited, play it safe
                has_unsupported = True
                
            if isinstance(node, ForStatement):
                self.depth += 1
                nonlocal max_loop_depth
                max_loop_depth = max(max_loop_depth, self.depth)
                
                bound = 100
                if hasattr(node, 'range_end') and isinstance(node.range_end, Literal):
                    try:
                        end_val = int(node.range_end.value)
                        start_val = 0
                        if hasattr(node, 'range_start') and isinstance(node.range_start, Literal):
                            start_val = int(node.range_start.value)
                        bound = end_val - start_val
                    except (ValueError, AttributeError, TypeError):
                        pass
                
                total_loop_iters += (bound ** self.depth)
                
                if hasattr(node, "body") and getattr(node, "body"):
                    for stmt in getattr(node.body, "statements", []):
                        self.visit(stmt)
                
                self.depth -= 1
                
            elif isinstance(node, BinaryOperation):
                elementwise_ops += 1
                self.visit(node.left)
                self.visit(node.right)
            elif hasattr(node, '__dict__'):
                for v in vars(node).values():
                    if isinstance(v, list):
                        for item in v:
                            if hasattr(item, '__dict__'):
                                self.visit(item)
                    elif hasattr(v, '__dict__'):
                        self.visit(v)

    visitor = Visitor()
    for decl in ast:
        if isinstance(decl, FunctionDecl):
            if decl.body:
                for stmt in decl.body.statements:
                    visitor.visit(stmt)

    if has_unsupported:
        return "c"
        
    # Heuristics for C vs MLIR crossover
    if total_loop_iters > 50000 or (max_loop_depth > 1 and total_loop_iters > 5000) or elementwise_ops > 100:
        return "mlir"
        
    return "c"
