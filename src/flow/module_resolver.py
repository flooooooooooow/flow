#!/usr/bin/env python3
"""
FLOW Module Resolver
Handles multi-file resolution and recursive imports.
"""

import os
from pathlib import Path
from typing import List, Dict, Set, Any, Optional
from .parser import Lexer, Parser, ImportDecl, FunctionDecl, StructDecl, EffectDecl, CapabilityDecl

class ModuleResolver:
    """Resolves and merges FLOW modules across multiple files."""
    
    def __init__(self, root_file: str):
        self.root_file = os.path.abspath(root_file)
        self.visited_files: Set[str] = set()
        self.all_declarations: List[Any] = []
        self.symbol_source_files: Dict[str, str] = {} # symbol_name -> file_path
        
    def resolve(self) -> List[Any]:
        """Recursively resolves all imports starting from the root file."""
        self._resolve_recursive(self.root_file, is_root=True)
        return self.all_declarations

    def _resolve_recursive(self, file_path: str, is_root: bool = False):
        if file_path in self.visited_files:
            return
        
        self.visited_files.add(file_path)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Module file not found: {file_path}")

        with open(file_path, 'r') as f:
            code = f.read()

        lexer = Lexer(code)
        parser = Parser(lexer)
        declarations = parser.parse()

        # Split into imports and other declarations
        imports = [d for d in declarations if isinstance(d, ImportDecl)]
        others = [d for d in declarations if not isinstance(d, ImportDecl)]

        # Process imports first (depth-first)
        base_dir = os.path.dirname(file_path)
        # Define stdlib path relative to this file's directory (src/flow/module_resolver.py)
        # Assuming project structure:
        # transpile/
        #   src/flow/module_resolver.py
        #   lib/stdlib/
        stdlib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "lib", "stdlib"))
        packages_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "packages"))

        for imp in imports:
            # Resolve path relative to current file
            imp_path = os.path.join(base_dir, imp.path)
            if not imp_path.endswith('.flow'):
                imp_path += '.flow'
            
            if not os.path.exists(imp_path):
                # Try stdlib
                std_imp_path = os.path.join(stdlib_path, imp.path)
                if not std_imp_path.endswith('.flow'):
                    std_imp_path += '.flow'
                if os.path.exists(std_imp_path):
                    imp_path = std_imp_path
                else:
                    # Try packages
                    pkg_imp_path = os.path.join(packages_path, imp.path)
                    if not pkg_imp_path.endswith('.flow'):
                        pkg_imp_path += '.flow'
                    if os.path.exists(pkg_imp_path):
                        imp_path = pkg_imp_path
            
            imp_path = os.path.abspath(imp_path)
            self._resolve_recursive(imp_path)

        # Merge other declarations
        for decl in others:
            if is_root or getattr(decl, 'is_exported', False):
                # Check for symbol collisions
                name = getattr(decl, 'name', None)
                if name:
                    if name in self.symbol_source_files:
                        original_file = self.symbol_source_files[name]
                        if original_file != file_path:
                            # print(f"Warning: Symbol '{name}' in {file_path} overlaps with {original_file}")
                            pass
                    self.symbol_source_files[name] = file_path
                
                self.all_declarations.append(decl)

def resolve_modules(root_file: str) -> List[Any]:
    resolver = ModuleResolver(root_file)
    return resolver.resolve()
