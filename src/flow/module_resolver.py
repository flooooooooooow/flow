#!/usr/bin/env python3
"""
FLOW Module Resolver
Handles multi-file resolution and recursive imports with proper import/export system.
"""

import os
from pathlib import Path
from typing import List, Dict, Set, Any, Optional, Tuple
from .parser import Lexer, Parser, ImportDecl, FunctionDecl, StructDecl, EffectDecl, CapabilityDecl, ConstDecl

class ModuleSymbol:
    """Represents a symbol exported from a module."""
    
    def __init__(self, name: str, declaration: Any, source_file: str, is_exported: bool = False):
        self.name = name
        self.declaration = declaration
        self.source_file = source_file
        self.is_exported = is_exported
        self.imported_as: Optional[str] = None  # For aliasing imports

class ModuleInfo:
    """Information about a loaded module."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.symbols: Dict[str, ModuleSymbol] = {}
        self.dependencies: Set[str] = set()
        self.is_loaded = False

class ModuleResolver:
    """Resolves and merges FLOW modules across multiple files with proper import/export."""
    
    def __init__(self, root_file: str):
        self.root_file = os.path.abspath(root_file)
        self.modules: Dict[str, ModuleInfo] = {}
        self.all_declarations: List[Any] = []
        self.symbol_table: Dict[str, ModuleSymbol] = {}
        self.import_stack: List[str] = []
        self.circular_imports: Set[Tuple[str, str]] = set()
        
    def resolve(self) -> List[Any]:
        """Recursively resolves all imports starting from the root file."""
        self._resolve_recursive(self.root_file, is_root=True)
        self._resolve_symbols()
        return self.all_declarations

    def _resolve_recursive(self, file_path: str, is_root: bool = False):
        """Recursively resolve imports from a file."""
        if file_path in self.import_stack:
            # Detect circular import
            cycle = tuple(self.import_stack[self.import_stack.index(file_path):] + [file_path])
            self.circular_imports.add(cycle)
            return
        
        if file_path in self.modules and self.modules[file_path].is_loaded:
            return
        
        self.import_stack.append(file_path)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Module file not found: {file_path}")

        # Create module info
        module_info = ModuleInfo(file_path)
        self.modules[file_path] = module_info

        # Parse the file
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
        stdlib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "lib", "stdlib"))
        packages_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "packages"))

        for imp in imports:
            resolved_path = self._resolve_import_path(imp.path, base_dir, stdlib_path, packages_path)
            if resolved_path:
                module_info.dependencies.add(resolved_path)
                self._resolve_recursive(resolved_path)

        # Process symbols in this module
        for decl in others:
            name = getattr(decl, 'name', None)
            if name:
                is_exported = getattr(decl, 'is_exported', False)
                symbol = ModuleSymbol(name, decl, file_path, is_exported)
                module_info.symbols[name] = symbol
                
                # Add to global symbol table if exported or root module
                if is_root or is_exported:
                    if name in self.symbol_table:
                        existing = self.symbol_table[name]
                        if existing.source_file != file_path:
                            # Symbol collision - prefer exported symbols
                            if is_exported and not existing.is_exported:
                                self.symbol_table[name] = symbol
                            elif existing.is_exported and not is_exported:
                                pass  # Keep existing exported symbol
                            elif is_exported == existing.is_exported:
                                print(f"Warning: Symbol '{name}' collision between {file_path} and {existing.source_file}")
                    else:
                        self.symbol_table[name] = symbol
                
                # Add to declarations list
                self.all_declarations.append(decl)

        module_info.is_loaded = True
        self.import_stack.pop()

    def _resolve_import_path(self, import_path: str, base_dir: str, stdlib_path: str, packages_path: str) -> Optional[str]:
        """Resolve import path to actual file path."""
        # Try relative to current file
        imp_path = os.path.join(base_dir, import_path)
        if not imp_path.endswith('.flow'):
            imp_path += '.flow'
        
        if os.path.exists(imp_path):
            return os.path.abspath(imp_path)
        
        # Try stdlib
        std_imp_path = os.path.join(stdlib_path, import_path)
        if not std_imp_path.endswith('.flow'):
            std_imp_path += '.flow'
        if os.path.exists(std_imp_path):
            return os.path.abspath(std_imp_path)
        
        # Try packages
        pkg_imp_path = os.path.join(packages_path, import_path)
        if not pkg_imp_path.endswith('.flow'):
            pkg_imp_path += '.flow'
        if os.path.exists(pkg_imp_path):
            return os.path.abspath(pkg_imp_path)
        
        return None

    def _resolve_symbols(self):
        """Resolve all symbol references and check for missing symbols."""
        # This would be used to resolve symbol references in expressions
        # For now, we just check for circular imports
        if self.circular_imports:
            print("Warning: Circular imports detected:")
            for cycle in self.circular_imports:
                print("  -> ".join(cycle))

    def get_module_info(self, file_path: str) -> Optional[ModuleInfo]:
        """Get information about a specific module."""
        return self.modules.get(os.path.abspath(file_path))

    def get_symbol(self, name: str) -> Optional[ModuleSymbol]:
        """Get a symbol by name."""
        return self.symbol_table.get(name)

    def list_exported_symbols(self, module_path: str) -> List[str]:
        """List all exported symbols from a module."""
        module_info = self.get_module_info(module_path)
        if not module_info:
            return []
        
        return [name for name, symbol in module_info.symbols.items() if symbol.is_exported]

    def get_module_dependencies(self, module_path: str) -> List[str]:
        """Get all dependencies of a module."""
        module_info = self.get_module_info(module_path)
        if not module_info:
            return []
        
        return list(module_info.dependencies)

    def validate_imports(self) -> List[str]:
        """Validate all imports and return list of errors."""
        errors = []
        
        # Check for circular imports
        for cycle in self.circular_imports:
            errors.append(f"Circular import detected: {' -> '.join(cycle)}")
        
        # Check for missing symbols (this would require expression analysis)
        # For now, just check that all imported files exist
        
        return errors

def resolve_modules(root_file: str) -> List[Any]:
    """Resolve modules starting from root file."""
    resolver = ModuleResolver(root_file)
    return resolver.resolve()

def get_module_resolver(root_file: str) -> ModuleResolver:
    """Get a module resolver instance for analysis."""
    resolver = ModuleResolver(root_file)
    resolver.resolve()
    return resolver
