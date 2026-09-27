import pytest
import os
import glob
import shutil
from src.flow.module_resolver import resolve_modules, ast_to_dict, dict_to_ast
from src.flow.parser import Lexer, Parser, SourceLocation


def test_ast_json_serialization_roundtrip():
    code = """
    enum Color { Red, Green, Blue }
    function add(a: i32, b: i32) -> i32 {
        if a > 0 {
            return a + b;
        }
        return b;
    }
    """
    lexer = Lexer(code)
    parser = Parser(lexer)
    original_decls = parser.parse()

    serialized = ast_to_dict(original_decls)
    restored_decls = dict_to_ast(serialized)

    assert original_decls == restored_decls


def test_dict_to_ast_rejects_unauthorized_classes():
    # Attempting to deserialize non-allowlisted classes or modules must raise ValueError
    malicious_payload = {
        "__class__": "os.system",
        "command": "echo vulnerable"
    }
    with pytest.raises(ValueError, match="Unauthorized class type in cache"):
        dict_to_ast(malicious_payload)

    malicious_enum = {
        "__enum__": "subprocess.Popen",
        "value": "ls"
    }
    with pytest.raises(ValueError, match="Unauthorized enum type in cache"):
        dict_to_ast(malicious_enum)


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

        # Verify cache file created is .json, not .pkl
        json_caches = glob.glob(os.path.join(cache_dir, "*.json"))
        pkl_caches = glob.glob(os.path.join(cache_dir, "*.pkl"))
        assert len(json_caches) > 0
        assert len(pkl_caches) == 0

        # Test corrupt cache file gracefully falls back to reparse
        for jc in json_caches:
            with open(jc, "w") as f:
                f.write("{ invalid json content ...")

        declarations_4 = resolve_modules(test_file)
        assert len(declarations_4) > 0
        assert declarations_4[0].name == "main"
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
        
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
