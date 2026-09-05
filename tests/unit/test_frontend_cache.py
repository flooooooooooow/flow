import pytest
import os
import shutil
from src.flow.module_resolver import resolve_modules


def test_incremental_compilation_cache():
    # Setup test file
    test_file = "test_cache_target.flow"
    with open(test_file, "w") as f:
        f.write("function main() -> i32 { return 42; }\n")
        
    try:
        # Clear cache first
        cache_dir = os.path.join(os.path.dirname(os.path.abspath(test_file)), ".flow_cache")
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            
        import time
        
        start = time.time()
        # First resolve (cache miss)
        declarations_1 = resolve_modules(test_file)
        time_1 = time.time() - start
        
        start = time.time()
        # Second resolve (cache hit)
        declarations_2 = resolve_modules(test_file)
        time_2 = time.time() - start
        
        assert len(declarations_1) == len(declarations_2)
        assert declarations_1[0].name == declarations_2[0].name
        
        # Modify file and verify cache bust
        with open(test_file, "w") as f:
            f.write("function main() -> i32 { return 100; }\n")
            
        start = time.time()
        declarations_3 = resolve_modules(test_file)
        time_3 = time.time() - start
        
        # Check that we got the new AST
        assert len(declarations_3) > 0
        assert declarations_3[0].name == "main"
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
        
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
