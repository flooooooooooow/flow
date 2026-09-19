#!/usr/bin/env python3
"""
FLOW Module Resolver
Resolves dot-path imports (verify.nat) and legacy string imports.
"""

from __future__ import annotations

import os
import json
import hashlib
import pickle
import functools
import warnings
from itertools import product
from pathlib import Path
from typing import List, Dict, Set, Any, Optional, Tuple, Iterator

from .dynamics_dsl import expand_dynamics_dsl, has_dynamics_dsl
from .parser import (
    Lexer,
    Parser,
    ImportDecl,
    ImplDecl,
    ExportDecl,
    ModuleDecl,
    FunctionDecl,
    Type,
    Block,
    ReturnStatement,
    Literal,
)
from .project_config import load_project_config
from .shader_dsl import extract_shader_module, has_fill_shader_dsl


# Bump when the on-disk cache entry format changes, or when a frontend change
# that the source fingerprint below cannot see would alter a parse. Any bump
# changes every cache key, so entries written by an older schema become
# unreachable and can never be served as stale.
CACHE_SCHEMA_VERSION = "2"

# Frontend source files whose behaviour determines the parsed declaration
# graph. Their contents are folded into the cache key, so changing the lexer,
# parser, resolver or any DSL expander invalidates every cached parse even when
# the .flow source text is byte-for-byte identical. Without this, an upgraded
# compiler silently reuses declarations produced by the old frontend.
_FRONTEND_SOURCE_FILES = (
    "lexer.py",
    "parser.py",
    "module_resolver.py",
    "dynamics_dsl.py",
    "field_dsl.py",
    "field_dsl_core.py",
    "shader_dsl.py",
)


@functools.lru_cache(maxsize=1)
def _frontend_code_fingerprint() -> str:
    """SHA-256 over the frontend source files that shape a parse."""
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    digest = hashlib.sha256()
    for name in _FRONTEND_SOURCE_FILES:
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        try:
            with open(os.path.join(pkg_dir, name), "rb") as handle:
                digest.update(handle.read())
        except OSError:
            # A frontend module we cannot read is treated as changed, so a
            # parse from an unknown implementation is never reused.
            digest.update(b"<unreadable>")
        digest.update(b"\0")
    return digest.hexdigest()


def _compiler_cache_salt() -> str:
    """Everything about the compiler that can change a parse of fixed source."""
    from .version import __version__

    salt = f"{CACHE_SCHEMA_VERSION}:{__version__}:{_frontend_code_fingerprint()}"
    # An explicit override lets a caller (or a test) perturb the key without
    # editing source. It augments the real salt, so genuine protection stays.
    override = os.environ.get("FLOW_CACHE_SALT")
    if override:
        salt = f"{salt}:{override}"
    return salt


def _config_cache_salt(project: Any) -> str:
    """Resolution config that can change which file an import resolves to."""
    try:
        relevant = {
            "stdlib_root": project.stdlib_root,
            "project_root": project.project_root,
            "paths": project.paths,
            "dependencies": sorted(project.dependencies),
        }
        blob = json.dumps(relevant, sort_keys=True, default=str)
    except Exception:
        blob = repr(project)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _file_content_hash(path: str) -> Optional[str]:
    """SHA-256 of a file's current bytes, or None if it cannot be read."""
    try:
        with open(path, "rb") as handle:
            return hashlib.sha256(handle.read()).hexdigest()
    except OSError:
        return None


def _fill_shader_host_stub() -> List[Any]:
    """Host-Flow stub so fill-shader modules can pass the C transpile corpus.

    Fill shaders are compiled by `./flow shader` / `shader_codegen`, not the
    host C backend. Tier-2 still runs every tracked `examples/**/*.flow` through
    `flow.transpiler --c`, so FSL modules need a harmless host entry point.
    """
    return [
        FunctionDecl(
            name="main",
            parameters=[],
            return_type=Type(name="i32"),
            body=Block(
                statements=[
                    ReturnStatement(value=Literal(value="0", type=Type(name="i32")))
                ]
            ),
            attributes=[],
        )
    ]


class SymbolCollisionError(ValueError):
    """Two different declarations claim the same exported name.

    A `ValueError` subclass so existing callers that catch `ValueError`
    keep working; the distinct type lets the re-export path add context
    about which forwarding import brought the second declaration in.
    """


class ModuleSymbol:
    """Represents a symbol exported from a module."""

    def __init__(
        self,
        name: str,
        declaration: Any,
        source_file: str,
        is_exported: bool = False,
    ):
        self.name = name
        self.declaration = declaration
        self.source_file = source_file
        self.is_exported = is_exported
        self.imported_as: Optional[str] = None


class ModuleInfo:
    """Information about a loaded module."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.symbols: Dict[str, ModuleSymbol] = {}
        self.dependencies: Set[str] = set()
        self.is_loaded = False
        # name -> file that this module re-exported the symbol from
        # (`export import`). Populated before local declarations are bound,
        # so a local declaration shadowing a re-export is caught as a clash.
        self.reexports: Dict[str, str] = {}


class ModuleResolver:
    """Resolves and merges FLOW modules across multiple files."""

    def __init__(self, root_file: str):
        self.root_file = os.path.abspath(root_file)
        self.project = load_project_config(self.root_file)
        self.modules: Dict[str, ModuleInfo] = {}
        self.all_declarations: List[Any] = []
        self.symbol_table: Dict[str, ModuleSymbol] = {}
        self.import_stack: List[str] = []
        self.circular_imports: Set[Tuple[str, ...]] = set()
        self._legacy_import_warnings: Set[str] = set()

        # Salt for every cache key produced by this resolver. It captures the
        # compiler/schema version, the frontend source fingerprint and the
        # resolution config, so a cached parse is reused only under an identical
        # frontend and configuration. Recomputing it per resolver keeps it in
        # step with the project config loaded above.
        self._cache_salt = (
            _compiler_cache_salt() + ":" + _config_cache_salt(self.project)
        )

        # Legacy search paths (string imports)
        compiler_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )
        self._stdlib_path = self.project.stdlib_root
        self._packages_path = os.path.join(compiler_root, "packages")

    def resolve(self) -> List[Any]:
        """Recursively resolves all imports starting from the root file."""
        self._resolve_recursive(self.root_file, is_root=True)
        self._resolve_symbols()
        return self.all_declarations

    def _resolve_recursive(self, file_path: str, is_root: bool = False):
        if file_path in self.import_stack:
            idx = self.import_stack.index(file_path)
            cycle = tuple(self.import_stack[idx:] + [file_path])
            self.circular_imports.add(cycle)
            return

        if file_path in self.modules and self.modules[file_path].is_loaded:
            return

        self.import_stack.append(file_path)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Module file not found: {file_path}")

        module_info = ModuleInfo(file_path)
        self.modules[file_path] = module_info

        cache_dir = os.path.join(os.path.dirname(self.root_file), ".flow_cache")
        os.makedirs(cache_dir, exist_ok=True)

        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()

        # Content-addressed key over the salt (compiler/schema version, frontend
        # fingerprint, resolution config) and the source text. Identical source
        # can no longer reuse declarations produced by a different frontend or
        # under a different configuration.
        cache_key = hashlib.sha256(
            f"{self._cache_salt}\0{code}".encode("utf-8")
        ).hexdigest()
        cache_path = os.path.join(cache_dir, f"{cache_key}.pkl")

        declarations = self._load_cache_entry(cache_path)
        cache_hit = declarations is not None

        if declarations is None:
            # Fill-shader dialect (`shader fill` / FSL `fn`) is not host Flow.
            # Validate the FSL module, then provide a stub main for C transpile.
            if has_fill_shader_dsl(code):
                mod = extract_shader_module(code)
                if not mod.fills:
                    raise SyntaxError(
                        f"Fill-shader module has no `shader fill` blocks: {file_path}"
                    )
                declarations = _fill_shader_host_stub()
            else:
                from .field_dsl import expand_field_dsl, has_field_dsl

                if has_field_dsl(code):
                    code = expand_field_dsl(code)
                if has_dynamics_dsl(code):
                    code = expand_dynamics_dsl(code)

                lexer = Lexer(code)
                parser = Parser(lexer)
                declarations = parser.parse()

        imports = [d for d in declarations if isinstance(d, ImportDecl)]
        others = [
            d
            for d in declarations
            if not isinstance(d, ImportDecl) and not isinstance(d, ExportDecl)
        ]
        export_lists = [d for d in declarations if isinstance(d, ExportDecl)]
        export_names: Set[str] = set()
        for export_decl in export_lists:
            export_names.update(export_decl.symbols)

        base_dir = os.path.dirname(file_path)

        # Content hashes of the direct imports this module resolves to. Recorded
        # in the cache entry so a later run misses when any imported module
        # changed on disk. A change to this file's own text is already covered
        # by the content-addressed key above.
        dep_hashes: Dict[str, Optional[str]] = {}

        for imp in imports:
            resolved_path, import_symbols = self._resolve_import(imp, base_dir)
            if resolved_path:
                module_info.dependencies.add(resolved_path)
                dep_hashes[resolved_path] = _file_content_hash(resolved_path)
                is_reexport = getattr(imp, "is_reexport", False)
                try:
                    self._resolve_recursive(resolved_path)
                except SymbolCollisionError as exc:
                    if not is_reexport:
                        raise
                    raise SymbolCollisionError(
                        f"Re-export collision in {file_path}: forwarding "
                        f"'{imp.path}' brings in a name that is already "
                        f"exported elsewhere — {exc}"
                    ) from exc
                self._validate_import_symbols(
                    imp, resolved_path, import_symbols, file_path
                )
                if is_reexport:
                    self._apply_reexport(
                        imp, resolved_path, import_symbols, module_info
                    )

        # Persist only on a miss; a hit already validated its dependencies.
        # Writing after the imports loop lets the entry carry the dependency
        # hashes needed for import-aware invalidation.
        if not cache_hit:
            self._store_cache_entry(cache_path, declarations, dep_hashes)

        for decl in others:
            if isinstance(decl, ImplDecl):
                name = f"{decl.for_type.name}_{decl.trait_name}_impl"
            else:
                name = getattr(decl, "name", None)

            # Declarations without a name (e.g. CIncludeDecl) are passed
            # through directly without symbol table registration.
            if name is None:
                self.all_declarations.append(decl)
                continue

            if name:
                imported_entry_point = name == "main" and not is_root
                is_exported = (
                    getattr(decl, "is_exported", False) or name in export_names
                ) and not imported_entry_point
                if name in module_info.reexports:
                    raise SymbolCollisionError(
                        f"Re-export collision on symbol '{name}' in {file_path}: "
                        f"re-exported from {module_info.reexports[name]} and also "
                        f"declared locally in {file_path}"
                    )
                symbol = ModuleSymbol(name, decl, file_path, is_exported)
                module_info.symbols[name] = symbol

                # `main` belongs to the root compilation unit. An imported
                # module may still define one so it can run on its own, but
                # surfacing that entry point would make it precede the root
                # `main` in emitted declarations and silently win C dedup.
                # Keep it in its module for introspection, but never import,
                # re-export, or emit it (#621).
                if imported_entry_point:
                    continue

                if is_root or is_exported:
                    if name in self.symbol_table:
                        existing = self.symbol_table[name]
                        if existing.source_file != file_path:
                            if is_exported and not existing.is_exported:
                                self.symbol_table[name] = symbol
                            elif existing.is_exported and not is_exported:
                                pass
                            elif is_exported == existing.is_exported:
                                raise SymbolCollisionError(
                                    f"Symbol '{name}' collision between "
                                    f"{file_path} and {existing.source_file}"
                                )
                    else:
                        self.symbol_table[name] = symbol

                self.all_declarations.append(decl)

        module_info.is_loaded = True
        self.import_stack.pop()

    def _load_cache_entry(self, cache_path: str) -> Optional[List[Any]]:
        """Return cached declarations for `cache_path`, or None to recompile.

        Any doubt yields None so the caller reparses. The entry is trusted only
        when its schema and salt match this resolver and every recorded
        dependency still hashes to the same content on disk.
        """
        if not os.path.exists(cache_path):
            return None
        try:
            with open(cache_path, "rb") as handle:
                # The compiler is the only writer of this file, and the entry is
                # rejected below unless its schema and salt match. A corrupt or
                # foreign file raises here and falls through to a reparse.
                entry = pickle.load(handle)  # nosec B301
        except Exception:
            return None

        if not isinstance(entry, dict):
            return None
        if entry.get("schema") != CACHE_SCHEMA_VERSION:
            return None
        if entry.get("salt") != self._cache_salt:
            # The filename already encodes the salt; this rejects a hash
            # collision or a hand-placed file that lands on the same name.
            return None

        deps = entry.get("deps")
        declarations = entry.get("declarations")
        if not isinstance(deps, dict) or declarations is None:
            return None

        # Dependency-aware invalidation: if any imported module's current
        # content differs from what this entry was built against, miss.
        for dep_path, recorded_hash in deps.items():
            if _file_content_hash(dep_path) != recorded_hash:
                return None

        return declarations

    def _store_cache_entry(
        self,
        cache_path: str,
        declarations: List[Any],
        dep_hashes: Dict[str, Optional[str]],
    ) -> None:
        """Write a cache entry atomically. Failure is silent and safe."""
        entry = {
            "schema": CACHE_SCHEMA_VERSION,
            "salt": self._cache_salt,
            "deps": dep_hashes,
            "declarations": declarations,
        }
        tmp_path = f"{cache_path}.{os.getpid()}.tmp"
        try:
            with open(tmp_path, "wb") as handle:
                pickle.dump(entry, handle)
            # Atomic rename so a crashed writer never leaves a half-written
            # entry that a later run could load and misread as valid.
            os.replace(tmp_path, cache_path)
        except Exception:
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except OSError:
                pass

    def _apply_reexport(
        self,
        imp: ImportDecl,
        resolved_path: str,
        import_symbols: Optional[List[str]],
        module_info: ModuleInfo,
    ):
        """Forward another module's exports as exports of this one.

        `export import .model` re-exports everything `.model` exports;
        `export import .model { a, b }` re-exports just `a` and `b`.

        Re-export binds the *same* `ModuleSymbol` object, so the declaration
        is never copied into `all_declarations` a second time and the emitted
        C contains exactly one definition. Re-exports chain: a symbol that
        arrived in the source module by re-export is itself re-exportable.
        """
        source = self.modules.get(resolved_path)
        if source is None or not source.is_loaded:
            raise ValueError(
                f"Cannot re-export from '{imp.path}' ({resolved_path}): the "
                f"module is not fully loaded (circular import?)"
            )

        available = {
            name: sym for name, sym in source.symbols.items() if sym.is_exported
        }

        if import_symbols:
            wanted = []
            for sym in import_symbols:
                if sym not in available:
                    # _validate_import_symbols already rejected genuinely
                    # missing / unexported names; anything left here is a
                    # citation-style brace entry with nothing to forward.
                    continue
                wanted.append(sym)
            selected = {name: available[name] for name in wanted}
        else:
            selected = available

        for name, symbol in selected.items():
            existing = module_info.symbols.get(name)
            if existing is not None and existing.source_file != symbol.source_file:
                first = module_info.reexports.get(name, existing.source_file)
                raise SymbolCollisionError(
                    f"Re-export collision on symbol '{name}' in "
                    f"{module_info.file_path}: re-exported from {first} and "
                    f"from {symbol.source_file}"
                )
            module_info.symbols[name] = symbol
            module_info.reexports.setdefault(name, symbol.source_file)

    def _resolve_import(
        self, imp: ImportDecl, base_dir: str
    ) -> Tuple[Optional[str], Optional[List[str]]]:
        if imp.is_legacy_string:
            self._warn_legacy_import(imp.path)
            path = self._resolve_legacy_import_path(imp.path, base_dir)
            symbols = imp.symbols
            return path, symbols

        path, extra_symbols = self._resolve_dot_import_path(imp.path, base_dir)
        symbols = list(imp.symbols) if imp.symbols else None
        if extra_symbols:
            symbols = (symbols or []) + extra_symbols
        return path, symbols

    def _resolve_dot_import_path(
        self, module_path: str, base_dir: str
    ) -> Tuple[str, Optional[List[str]]]:
        """Resolve verify.nat, std.audio.filters, .sibling_mod"""
        if ".." in module_path.split("."):
            raise FileNotFoundError(
                f"Parent-relative imports (..) are not allowed: {module_path}"
            )

        if module_path.startswith("."):
            return self._resolve_relative_dot_path(module_path, base_dir)

        return self._resolve_absolute_dot_path(module_path)

    @staticmethod
    def _filesystem_stems(part: str) -> List[str]:
        """Map a logical module-path segment to filesystem stem candidates.

        Claim-path morphisms (`Nat/+`, `Bool/||`) are logical addresses;
        on disk they usually live as the domain file (`Nat.flow`). Prefer
        the literal stem first (`Nat/+.flow`) then the domain-only fallback.
        """
        stems = [part]
        if "/" in part:
            domain = part.split("/", 1)[0]
            if domain and domain not in stems:
                stems.append(domain)
        return stems

    def _iter_flow_candidates(
        self, root: str, file_parts: List[str]
    ) -> Iterator[str]:
        """Yield absolute .flow candidate paths for a module-path prefix."""
        options = [self._filesystem_stems(p) for p in file_parts]
        seen: Set[str] = set()
        for combo in product(*options):
            candidate = os.path.join(root, *combo)
            if not candidate.endswith(".flow"):
                candidate += ".flow"
            if candidate in seen:
                continue
            seen.add(candidate)
            yield candidate

    def _resolve_relative_dot_path(
        self, module_path: str, base_dir: str
    ) -> Tuple[str, Optional[List[str]]]:
        rel = module_path[1:]
        parts = rel.split(".") if rel else []
        if not parts:
            raise FileNotFoundError(f"Invalid relative import: {module_path}")

        for i in range(len(parts), 0, -1):
            file_parts = parts[:i]
            sym_parts = parts[i:]
            for candidate in self._iter_flow_candidates(base_dir, file_parts):
                if os.path.exists(candidate):
                    return os.path.abspath(candidate), sym_parts or None

        raise FileNotFoundError(
            f"Could not resolve relative import '{module_path}' from {base_dir}"
        )

    def _resolve_absolute_dot_path(
        self, module_path: str
    ) -> Tuple[str, Optional[List[str]]]:
        parts = module_path.split(".")
        if not parts:
            raise FileNotFoundError(f"Invalid module path: {module_path}")

        roots: List[Tuple[str, List[str]]] = []

        if parts[0] == "std":
            roots.append((self._stdlib_path, parts[1:]))
        elif parts[0] in self.project.paths:
            root = os.path.join(self.project.project_root, self.project.paths[parts[0]])
            roots.append((root, parts[1:]))
        elif parts[0] in self.project.dependencies:
            package_root = os.path.join(
                self.project.project_root, "flow_packages", parts[0]
            )
            roots.append((os.path.join(package_root, "src"), parts[1:]))
            roots.append((package_root, parts[1:]))
        else:
            # stdlib/ prefix compatibility: stdlib.math -> lib/stdlib/math.flow
            if parts[0] == "stdlib":
                roots.append((self._stdlib_path, parts[1:]))
            roots.append((self._stdlib_path, parts))
            roots.append((self.project.project_root, parts))

        seen: Set[str] = set()
        for root, rest in roots:
            if not rest:
                continue
            for i in range(len(rest), 0, -1):
                file_parts = rest[:i]
                sym_parts = rest[i:]
                for candidate in self._iter_flow_candidates(root, file_parts):
                    if candidate in seen:
                        continue
                    seen.add(candidate)
                    if os.path.exists(candidate):
                        return os.path.abspath(candidate), sym_parts or None

        raise FileNotFoundError(f"Could not resolve import '{module_path}'")

    def _resolve_legacy_import_path(
        self, import_path: str, base_dir: str
    ) -> Optional[str]:
        if os.path.isabs(import_path) or import_path.startswith("~"):
            raise FileNotFoundError(f"Unsafe import path: {import_path}")
        if ".." in Path(import_path).parts:
            raise FileNotFoundError(f"Unsafe import path: {import_path}")

        import_file = (
            import_path if import_path.endswith(".flow") else import_path + ".flow"
        )

        candidates = [
            os.path.join(base_dir, import_file),
        ]

        if import_path.startswith("stdlib/"):
            stripped = import_path[7:]
            stripped_file = stripped if stripped.endswith(".flow") else stripped + ".flow"
            candidates.append(os.path.join(self._stdlib_path, stripped_file))

        candidates.append(os.path.join(self._stdlib_path, import_file))
        candidates.append(os.path.join(self._packages_path, import_file))
        candidates.append(os.path.join(self.project.project_root, import_file))

        for imp_path in candidates:
            if os.path.exists(imp_path):
                return os.path.abspath(imp_path)

        raise FileNotFoundError(f"Could not resolve import '{import_path}'")

    @staticmethod
    def _is_verify_citation_module(resolved_path: str) -> bool:
        """True for flow-verify proof modules (lib/verify, examples/verify).

        Their `import … { facet }` brace lists are dependency citations
        (claim facets / kebab names), not bindings into `module_info.symbols`
        — declarations are claim-path / guillemet-named and are pulled in
        transitively via the resolved file regardless of the brace list.
        """
        norm = resolved_path.replace("\\", "/")
        return "/lib/verify/" in norm or norm.endswith("/lib/verify") \
            or "/examples/verify/" in norm

    def _validate_import_symbols(
        self,
        imp: ImportDecl,
        resolved_path: str,
        import_symbols: Optional[List[str]],
        importing_file: str,
    ):
        if not import_symbols:
            return
        module_info = self.modules.get(resolved_path)
        if not module_info:
            return
        # Morphism imports (`verify.Nat/+ { zero-left }`) and verify-corpus
        # sibling citations (`import .Nat-plus-commutes { commutes }`) use
        # the brace list as documentation only — never as a real binding.
        citation_module = (
            self._is_verify_citation_module(resolved_path)
            or ("/" in (imp.path or ""))
        )
        for sym in import_symbols:
            if "-" in sym or citation_module:
                # Hyphenated names can never match a Flow declaration;
                # verify/morphism brace lists are citation-only (see above).
                continue
            if sym not in module_info.symbols:
                raise ValueError(
                    f"Module {imp.path} ({resolved_path}) has no symbol '{sym}' "
                    f"(imported from {importing_file})"
                )
            if not module_info.symbols[sym].is_exported:
                raise ValueError(
                    f"Symbol '{sym}' in {resolved_path} is not exported "
                    f"(imported from {importing_file})"
                )

    def _warn_legacy_import(self, path: str):
        if path in self._legacy_import_warnings:
            return
        self._legacy_import_warnings.add(path)
        warnings.warn(
            f'String import "{path}" is deprecated. '
            f"Use dot-path imports (e.g. std.math or verify.nat).",
            DeprecationWarning,
            stacklevel=3,
        )

    def _resolve_symbols(self):
        if self.circular_imports:
            cycles = [" -> ".join(cycle) for cycle in self.circular_imports]
            raise ValueError("Circular imports detected:\n  " + "\n  ".join(cycles))

    def get_module_info(self, file_path: str) -> Optional[ModuleInfo]:
        return self.modules.get(os.path.abspath(file_path))

    def get_symbol(self, name: str) -> Optional[ModuleSymbol]:
        return self.symbol_table.get(name)

    def list_exported_symbols(self, module_path: str) -> List[str]:
        module_info = self.get_module_info(module_path)
        if not module_info:
            return []
        return [name for name, sym in module_info.symbols.items() if sym.is_exported]

    def get_module_dependencies(self, module_path: str) -> List[str]:
        module_info = self.get_module_info(module_path)
        if not module_info:
            return []
        return list(module_info.dependencies)

    def validate_imports(self) -> List[str]:
        errors = []
        for cycle in self.circular_imports:
            errors.append(f"Circular import detected: {' -> '.join(cycle)}")
        return errors


def flatten_module_declarations(declarations: List[Any]) -> List[Any]:
    """Expand module { ... } blocks into top-level declarations."""
    flat: List[Any] = []
    for decl in declarations:
        if isinstance(decl, ModuleDecl):
            flat.extend(flatten_module_declarations(decl.declarations))
        else:
            flat.append(decl)
    return flat


def resolve_modules(root_file: str) -> List[Any]:
    resolver = ModuleResolver(root_file)
    return flatten_module_declarations(resolver.resolve())


def get_module_resolver(root_file: str) -> ModuleResolver:
    resolver = ModuleResolver(root_file)
    resolver.resolve()
    return resolver
