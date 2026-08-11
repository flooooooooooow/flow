#!/usr/bin/env python3
"""
FLOW Package Manager
Manages FLOW projects and dependencies.
"""

import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
import subprocess
import signal

# For Python < 3.11, fall back
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # pip install tomli
    except ImportError:
        # Simple TOML parser fallback
        class tomllib:
            @staticmethod
            def loads(s):
                """Very basic TOML parser for our limited use case."""
                result = {"package": {}, "dependencies": {}, "dev-dependencies": {}, "native": {}}
                current_section = None
                for line in s.strip().split("\n"):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("["):
                        section = line[1:-1].strip()
                        if section == "package":
                            current_section = "package"
                        elif section == "dependencies":
                            current_section = "dependencies"
                        elif section == "dev-dependencies":
                            current_section = "dev-dependencies"
                        elif section == "native":
                            current_section = "native"
                    elif "=" in line and current_section:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()
                        # Handle array values [...]
                        if value.startswith("[") and value.endswith("]"):
                            # Parse simple array
                            array_str = value[1:-1]
                            items = []
                            for item in array_str.split(","):
                                item = item.strip().strip('"').strip("'")
                                if item:
                                    items.append(item)
                            result[current_section][key] = items
                        else:
                            value = value.strip('"').strip("'")
                            result[current_section][key] = value
                return result


@dataclass
class FlowPackage:
    """Represents a FLOW package configuration."""
    name: str
    version: str = "0.1.0"
    description: str = ""
    author: str = ""
    license: str = "MIT"
    entry: str = "src/main.flow"
    dependencies: Dict[str, Any] = None
    dev_dependencies: Dict[str, Any] = None
    # Native linking support
    native_sources: List[str] = None  # e.g., ["runtime/gfx_macos.m"]
    frameworks: List[str] = None  # macOS frameworks, e.g., ["Cocoa", "CoreGraphics"]
    libs: List[str] = None  # libraries to link, e.g., ["SDL2"]
    cflags: List[str] = None  # extra compile flags
    ldflags: List[str] = None  # extra link flags
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = {}
        if self.dev_dependencies is None:
            self.dev_dependencies = {}
        if self.native_sources is None:
            self.native_sources = []
        if self.frameworks is None:
            self.frameworks = []
        if self.libs is None:
            self.libs = []
        if self.cflags is None:
            self.cflags = []
        if self.ldflags is None:
            self.ldflags = []
    
    def to_toml(self) -> str:
        """Convert to TOML format."""
        lines = [
            "[package]",
            f'name = "{self.name}"',
            f'version = "{self.version}"',
            f'description = "{self.description}"',
            f'author = "{self.author}"',
            f'license = "{self.license}"',
            f'entry = "{self.entry}"',
            "",
            "[dependencies]",
        ]
        
        for name, spec in self.dependencies.items():
            lines.append(f"{name} = {self._toml_value(spec)}")
        
        lines.append("")
        lines.append("[dev-dependencies]")
        
        for name, spec in self.dev_dependencies.items():
            lines.append(f"{name} = {self._toml_value(spec)}")
        
        # Native linking section
        if self.native_sources or self.frameworks or self.libs:
            lines.append("")
            lines.append("[native]")
            if self.native_sources:
                sources_str = ', '.join(f'"{s}"' for s in self.native_sources)
                lines.append(f'sources = [{sources_str}]')
            if self.frameworks:
                frameworks_str = ', '.join(f'"{f}"' for f in self.frameworks)
                lines.append(f'frameworks = [{frameworks_str}]')
            if self.libs:
                libs_str = ', '.join(f'"{lib}"' for lib in self.libs)
                lines.append(f'libs = [{libs_str}]')
            if self.cflags:
                cflags_str = ', '.join(f'"{f}"' for f in self.cflags)
                lines.append(f'cflags = [{cflags_str}]')
            if self.ldflags:
                ldflags_str = ', '.join(f'"{f}"' for f in self.ldflags)
                lines.append(f'ldflags = [{ldflags_str}]')

        lines.append("")
        lines.append("[build]")
        lines.append('host = "python"')
        lines.append('# test_command = "FLOW_HOST=python flow run tests/test_main.flow"')
        lines.append("")
        lines.append("[conventions]")
        lines.append("# avoid = [")
        lines.append('#   { pattern = "reverse for loop", reason = "generates incorrect step direction (#410)", workaround = "use while with explicit decrement" },')
        lines.append('# ]')
        lines.append("")
        lines.append("[patterns]")
        lines.append('# math = "use fabs((x) as f64) as f32 for single-precision abs"')

        return "\n".join(lines) + "\n"

    @staticmethod
    def _toml_value(value: Any) -> str:
        """Render the small TOML subset used by flow.toml package specs."""
        if isinstance(value, dict):
            parts = []
            for key, item in value.items():
                parts.append(f"{key} = {FlowPackage._toml_value(item)}")
            return "{ " + ", ".join(parts) + " }"
        if isinstance(value, list):
            return "[" + ", ".join(FlowPackage._toml_value(item) for item in value) + "]"
        if isinstance(value, bool):
            return "true" if value else "false"
        return f'"{str(value)}"'
    
    @classmethod
    def from_toml(cls, toml_str: str) -> 'FlowPackage':
        """Parse from TOML string."""
        data = tomllib.loads(toml_str)
        pkg = data.get("package", {})
        native = data.get("native", {})
        return cls(
            name=pkg.get("name", "unnamed"),
            version=pkg.get("version", "0.1.0"),
            description=pkg.get("description", ""),
            author=pkg.get("author", ""),
            license=pkg.get("license", "MIT"),
            entry=pkg.get("entry", "src/main.flow"),
            dependencies=data.get("dependencies", {}),
            dev_dependencies=data.get("dev-dependencies", {}),
            native_sources=native.get("sources", []),
            frameworks=native.get("frameworks", []),
            libs=native.get("libs", []),
            cflags=native.get("cflags", []),
            ldflags=native.get("ldflags", []),
        )


class FlowPackageManager:
    """FLOW package manager."""
    
    # Colors
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir).absolute()
        self.config_file = self.project_dir / "flow.toml"
        self.packages_dir = self.project_dir / "flow_packages"
        self.lock_file = self.project_dir / "flow.lock"
        self._registry = None
        self._last_install_git_sha: Optional[str] = None

    def registry(self):
        """Lazy-load the Flow package registry index."""
        if self._registry is None:
            from .registry import FlowRegistry
            self._registry = FlowRegistry()
        return self._registry
    
    def init(self, name: Optional[str] = None) -> bool:
        """Initialize a new FLOW project."""
        if self.config_file.exists():
            print(f"{self.YELLOW}Project already initialized (flow.toml exists){self.RESET}")
            return False
        
        # Determine project name
        if not name:
            name = self.project_dir.name
        
        # Create package config
        package = FlowPackage(
            name=name,
            description="A FLOW project",
        )
        
        # Write flow.toml
        self.config_file.write_text(package.to_toml())
        print(f"{self.GREEN}✓ Created flow.toml{self.RESET}")
        
        # Create src directory
        src_dir = self.project_dir / "src"
        src_dir.mkdir(exist_ok=True)
        
        # Create main.flow
        main_file = src_dir / "main.flow"
        if not main_file.exists():
            main_file.write_text('''# {name} - A FLOW project

function main() -> i32 {{
    printf("Hello from {name}!\\n")
    return 0
}}
'''.format(name=name))
            print(f"{self.GREEN}✓ Created src/main.flow{self.RESET}")
        
        # Create .gitignore
        gitignore = self.project_dir / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text("""# FLOW build artifacts
build/
flow_packages/
*.o
*.so
*.dylib

# Editor files
.vscode/
.idea/
*.swp
*~
""")
            print(f"{self.GREEN}✓ Created .gitignore{self.RESET}")
        
        print(f"\n{self.BOLD}Project '{name}' initialized!{self.RESET}")
        print("\nNext steps:")
        print(f"  {self.BLUE}cd {name}{self.RESET}")
        print(f"  {self.BLUE}flow run src/main.flow{self.RESET}")
        
        return True
    
    def load_config(self) -> Optional[FlowPackage]:
        """Load project configuration."""
        if not self.config_file.exists():
            print(f"{self.RED}No flow.toml found. Run 'flow init' first.{self.RESET}")
            return None
        
        try:
            return FlowPackage.from_toml(self.config_file.read_text())
        except Exception as e:
            print(f"{self.RED}Error parsing flow.toml: {e}{self.RESET}")
            return None
    
    def save_config(self, package: FlowPackage):
        """Save project configuration."""
        self.config_file.write_text(package.to_toml())
    
    def _read_lock(self) -> dict:
        """Load flow.lock or return empty dict."""
        if not self.lock_file.exists():
            return {"version": 1, "packages": {}}
        try:
            import json
            return json.loads(self.lock_file.read_text())
        except Exception:
            return {"version": 1, "packages": {}}

    def _write_lock(self, lock_data: dict) -> None:
        """Persist flow.lock with pinned dependency versions."""
        import json
        self.lock_file.write_text(json.dumps(lock_data, indent=2) + "\n")

    def _update_lock_entry(
        self,
        package_name: str,
        version: Any,
        source: str,
        resolved: Optional[Dict[str, Any]] = None,
    ) -> None:
        lock = self._read_lock()
        entry: Dict[str, Any] = {
            "version": version if not isinstance(version, dict) else version,
            "source": source,
        }
        if resolved is not None:
            entry["resolved"] = resolved
        lock.setdefault("packages", {})[package_name] = entry
        self._write_lock(lock)

    @staticmethod
    def _looks_like_git_url(value: str) -> bool:
        """True for https/git SSH/file URLs commonly used as git remotes."""
        v = value.strip()
        if v.startswith("git+"):
            return True
        if v.startswith("git@"):
            return True
        if v.startswith("ssh://git@"):
            return True
        if v.startswith("file://"):
            return True
        if v.startswith("http://") or v.startswith("https://"):
            # Prefer explicit .git, but also accept github/gitlab-style paths
            lower = v.lower()
            if lower.endswith(".git") or ".git#" in lower:
                return True
            for host in ("github.com/", "gitlab.com/", "bitbucket.org/", "codeberg.org/"):
                if host in lower:
                    return True
        return False

    @staticmethod
    def _normalize_git_url(url: str) -> str:
        """Strip git+ prefix and fragment (Cargo-style git+https://…#rev)."""
        u = url.strip()
        if u.startswith("git+"):
            u = u[4:]
        if "#" in u and not u.startswith("file://"):
            # Keep file:// paths intact; for http(s) fragment may be a rev hint
            # handled separately — drop fragment from the clone URL.
            base, _frag = u.split("#", 1)
            u = base
        return u.rstrip("/")

    @staticmethod
    def _infer_git_name(url: str) -> str:
        """Infer package name from a git URL basename (strip .git)."""
        u = FlowPackageManager._normalize_git_url(url)
        if u.startswith("git@") and ":" in u:
            # git@host:org/repo.git
            path = u.split(":", 1)[1]
        else:
            path = u
        name = Path(path).name
        if name.endswith(".git"):
            name = name[: -len(".git")]
        return name or "unnamed"

    @staticmethod
    def _git_head_sha(repo: Path) -> Optional[str]:
        try:
            out = subprocess.run(
                ["git", "-C", str(repo), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            )
            sha = out.stdout.strip()
            return sha or None
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    @staticmethod
    def _parse_add_spec(package_spec: str) -> tuple:
        """Parse `name`, `name@version`, or `name@^1.2`."""
        if "@" in package_spec and not package_spec.startswith("@"):
            # Avoid treating git@host:… as name@version
            if package_spec.startswith("git@"):
                return package_spec.strip(), "*"
            name, ver = package_spec.split("@", 1)
            return name.strip(), ver.strip() or "*"
        return package_spec.strip(), "*"

    def add(
        self,
        package_name: str,
        version: str = "*",
        *,
        git: Optional[str] = None,
        path: Optional[str] = None,
        tag: Optional[str] = None,
        rev: Optional[str] = None,
        branch: Optional[str] = None,
        subdir: Optional[str] = None,
    ) -> bool:
        """Add a dependency (registry name, path, or git) — package registry style."""
        config = self.load_config()
        if not config:
            return False

        # URL shorthand: `flow add https://github.com/org/repo.git [--tag …]`
        if not git and not path and self._looks_like_git_url(package_name):
            git = package_name
            package_name = self._infer_git_name(git)

        name, ver_from_at = self._parse_add_spec(package_name)
        if version == "*" and ver_from_at != "*":
            version = ver_from_at

        if git:
            git = self._normalize_git_url(git)
            if name in ("unnamed", "") or self._looks_like_git_url(name):
                name = self._infer_git_name(git)

        if name in config.dependencies:
            print(f"{self.YELLOW}{name} already in dependencies{self.RESET}")
            return False

        # Build dependency spec for flow.toml
        if path:
            spec: Any = {"path": path}
            source = "path"
        elif git:
            spec = {"git": git}
            if tag:
                spec["tag"] = tag
            elif rev:
                spec["rev"] = rev
            elif branch:
                spec["branch"] = branch
            if subdir:
                spec["subdir"] = subdir
            source = "git"
        else:
            # Registry resolution
            pkg_ver = self.registry().resolve(name, version)
            if pkg_ver is None:
                # Fall back: stdlib single-file module
                stdlib_path = (
                    Path(__file__).parent.parent.parent
                    / "lib"
                    / "stdlib"
                    / f"{name}.flow"
                )
                if stdlib_path.exists():
                    spec = version if version != "*" else "0.0.0"
                    source = "stdlib"
                else:
                    print(
                        f"{self.RED}Package '{name}' not found in registry "
                        f"({self.registry().name}).{self.RESET}"
                    )
                    print(
                        f"  Try: {self.BLUE}flow search {name}{self.RESET}  "
                        f"or  {self.BLUE}flow add --git <url> --name {name}{self.RESET}"
                    )
                    return False
            else:
                # Store a version requirement string in flow.toml;
                # install resolves via registry each time (lock pins the pick).
                spec = pkg_ver.version if version in ("*", "latest") else version
                if version.startswith("^") or version.startswith(">="):
                    spec = version
                source = "registry"
                print(
                    f"{self.BLUE}Resolved {name}@{pkg_ver.version} "
                    f"from {self.registry().name}{self.RESET}"
                )

        config.dependencies[name] = spec
        self.save_config(config)
        print(f"{self.GREEN}✓ Added {name} = {FlowPackage._toml_value(spec)}{self.RESET}")

        ok = self.install_package(name, config.dependencies[name])
        if ok:
            locked_ver = spec
            resolved = None
            if source == "registry":
                pkg_ver = self.registry().resolve(
                    name, spec if isinstance(spec, str) else "*"
                )
                if pkg_ver:
                    locked_ver = pkg_ver.version
                    resolved = pkg_ver.to_dep_spec()
            elif source == "git":
                resolved = dict(spec)
                sha = self._last_install_git_sha
                if sha:
                    resolved["rev"] = sha
                    print(f"{self.BLUE}  pinned rev {sha[:12]}{self.RESET}")
            self._update_lock_entry(name, locked_ver, source, resolved=resolved)
        return ok

    def search(self, query: str = "") -> bool:
        """Search the package registry."""
        from .registry import resolve_version

        results = self.registry().search(query)
        if not results:
            print(f"{self.YELLOW}No packages matched {query!r}{self.RESET}")
            return False
        print(f"{self.BOLD}{self.registry().name}{self.RESET} — {len(results)} package(s)\n")
        for pkg in results:
            latest = resolve_version(pkg, "*")
            ver = latest.version if latest else "?"
            print(f"  {self.GREEN}{pkg.name}{self.RESET}  {ver}")
            if pkg.description:
                print(f"    {pkg.description}")
        return True

    def info(self, package_name: str) -> bool:
        """Show package metadata."""
        from .registry import resolve_version

        pkg = self.registry().get(package_name)
        if not pkg:
            print(f"{self.RED}Unknown package: {package_name}{self.RESET}")
            return False
        latest = resolve_version(pkg, "*")
        print(f"{self.BOLD}{pkg.name}{self.RESET}")
        print(f"  description: {pkg.description}")
        print(f"  license:     {pkg.license}")
        if pkg.homepage:
            print(f"  homepage:    {pkg.homepage}")
        print("  versions:")
        for v in pkg.versions:
            mark = " (yanked)" if v.yanked else ""
            src = v.path or v.git or "?"
            print(f"    {v.version}{mark}  →  {src}")
        if latest:
            print(f"  latest:      {latest.version}")
        return True

    def publish(
        self,
        *,
        git: Optional[str] = None,
        tag: Optional[str] = None,
        path: Optional[str] = None,
        dry_run: bool = False,
    ) -> bool:
        """
        Publish the current package to the local package index.

        Writes/updates registry/index.json. For the official index, open a PR
        with that change. Remote hosted publish API is not required yet.
        """
        config = self.load_config()
        if not config:
            return False

        # Prefer explicit sources; else path relative to repo root if inside repo
        repo_root = Path(__file__).resolve().parent.parent.parent
        pub_path = path
        pub_git = git
        pub_tag = tag
        if not pub_path and not pub_git:
            try:
                rel = self.project_dir.resolve().relative_to(repo_root.resolve())
                pub_path = str(rel).replace("\\", "/")
            except ValueError:
                print(
                    f"{self.RED}Package is outside the Flow repo. "
                    f"Pass --git <url> [--tag vX.Y.Z] to publish.{self.RESET}"
                )
                return False

        print(f"{self.BLUE}Publishing {config.name}@{config.version}…{self.RESET}")
        print(f"  source: {pub_path or pub_git}")
        if dry_run:
            print(f"{self.YELLOW}dry-run — index not written{self.RESET}")
            return True

        index_path = self.registry().publish_local(
            name=config.name,
            version=config.version,
            description=config.description,
            license=config.license,
            path=pub_path,
            git=pub_git,
            tag=pub_tag,
        )
        print(f"{self.GREEN}✓ Registered in {index_path}{self.RESET}")
        print(
            f"\nNext: commit the index change (or open a PR) so others can "
            f"{self.BLUE}flow add {config.name}{self.RESET}"
        )
        return True
    
    def _copy_package_dir(self, source: Path, dest: Path) -> None:
        """Copy a package directory without carrying build artifacts."""
        ignore = shutil.ignore_patterns(
            ".git", "build", "flow_packages", "__pycache__", "*.pyc"
        )
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(source, dest, ignore=ignore)

    def install_package(self, package_name: str, spec: Any = "*") -> bool:
        """Install a package from stdlib, a local path, or a git URL."""
        self.packages_dir.mkdir(exist_ok=True)
        
        # Check if it's a stdlib package
        stdlib_path = Path(__file__).parent.parent.parent / "lib" / "stdlib" / f"{package_name}.flow"
        if stdlib_path.exists():
            # Copy from stdlib
            dest = self.packages_dir / f"{package_name}.flow"
            shutil.copy(stdlib_path, dest)
            print(f"{self.GREEN}✓ Installed {package_name} from stdlib{self.RESET}")
            return True

        if isinstance(spec, dict):
            if "path" in spec:
                raw_path = Path(str(spec["path"])).expanduser()
                source = (
                    raw_path.resolve()
                    if raw_path.is_absolute()
                    else (self.project_dir / raw_path).resolve()
                )
                if not source.exists():
                    print(f"{self.RED}Path dependency not found: {source}{self.RESET}")
                    return False
                dest = self.packages_dir / package_name
                if source.is_dir():
                    self._copy_package_dir(source, dest)
                else:
                    dest.parent.mkdir(exist_ok=True)
                    shutil.copy(source, dest.with_suffix(".flow"))
                print(f"{self.GREEN}✓ Installed {package_name} from {source}{self.RESET}")
                return True

            if "git" in spec:
                return self._install_git_dependency(package_name, spec)

            print(f"{self.RED}Unsupported dependency spec for {package_name}: {spec}{self.RESET}")
            return False
        
        # Check if it's a local file
        local_path = self.project_dir / f"{package_name}.flow"
        if local_path.exists():
            print(f"{self.YELLOW}{package_name} is a local file{self.RESET}")
            return True

        # Package registry: bare name / version requirement string
        if isinstance(spec, str) or spec is None:
            req = spec if isinstance(spec, str) else "*"
            pkg_ver = self.registry().resolve(package_name, req)
            if pkg_ver is not None:
                resolved = pkg_ver.to_dep_spec()
                print(
                    f"{self.BLUE}↓ {package_name}@{pkg_ver.version} "
                    f"from registry{self.RESET}"
                )
                return self.install_package(package_name, resolved)

        print(
            f"{self.RED}Unknown dependency '{package_name}'. "
            f"Not in registry, path, git, or stdlib. "
            f"Try: flow search {package_name}{self.RESET}"
        )
        return False

    def _install_git_dependency(self, package_name: str, spec: Dict[str, Any]) -> bool:
        """Clone a git dep into flow_packages/, optionally extracting `subdir`."""
        self._last_install_git_sha = None
        git_url = self._normalize_git_url(str(spec["git"]))
        dest = self.packages_dir / package_name
        ref = spec.get("tag") or spec.get("rev") or spec.get("branch")
        subdir = spec.get("subdir")
        # Clone into a staging dir when we need a subdirectory extract
        clone_dest = dest
        staging: Optional[Path] = None
        if subdir:
            staging = self.packages_dir / f".git-staging-{package_name}"
            if staging.exists():
                shutil.rmtree(staging)
            clone_dest = staging

        try:
            if clone_dest.exists() and (clone_dest / ".git").exists():
                subprocess.run(
                    ["git", "-C", str(clone_dest), "fetch", "--tags", "--prune"],
                    check=True,
                    capture_output=True,
                )
            else:
                if clone_dest.exists():
                    shutil.rmtree(clone_dest)
                clone_cmd = ["git", "clone"]
                # Shallow clone when pinning a branch/tag (not a full SHA)
                is_sha = (
                    isinstance(ref, str)
                    and len(ref) >= 7
                    and all(c in "0123456789abcdef" for c in ref.lower())
                )
                if ref and not is_sha:
                    clone_cmd.extend(["--depth", "1", "--branch", str(ref)])
                    ref = None  # already on the right branch/tag
                clone_cmd.extend([git_url, str(clone_dest)])
                subprocess.run(clone_cmd, check=True, capture_output=True)
            if ref:
                subprocess.run(
                    ["git", "-C", str(clone_dest), "fetch", "--tags", "--prune"],
                    check=False,
                    capture_output=True,
                )
                subprocess.run(
                    ["git", "-C", str(clone_dest), "checkout", str(ref)],
                    check=True,
                    capture_output=True,
                )

            sha = self._git_head_sha(clone_dest)
            self._last_install_git_sha = sha

            if subdir:
                src = clone_dest / str(subdir)
                if not src.exists():
                    print(
                        f"{self.RED}Git dependency {package_name}: "
                        f"subdir '{subdir}' not found in repo{self.RESET}"
                    )
                    return False
                if dest.exists():
                    shutil.rmtree(dest)
                self._copy_package_dir(src, dest)
                if staging and staging.exists():
                    shutil.rmtree(staging)
            # else: dest is the clone itself

            label = f"{git_url}" + (f"/{subdir}" if subdir else "")
            print(f"{self.GREEN}✓ Installed {package_name} from git ({label}){self.RESET}")
            return True
        except subprocess.CalledProcessError as e:
            err = e.stderr or ""
            if isinstance(err, bytes):
                err = err.decode("utf-8", errors="replace")
            print(
                f"{self.RED}Git dependency install failed for {package_name}: {e}"
                f"{(' — ' + err.strip()) if err else ''}{self.RESET}"
            )
            if staging and staging.exists():
                shutil.rmtree(staging)
            return False
        except FileNotFoundError:
            print(f"{self.RED}git not found on PATH{self.RESET}")
            return False
    
    def install(self) -> bool:
        """Install all dependencies and refresh flow.lock."""
        config = self.load_config()
        if not config:
            return False
        
        print(f"{self.BLUE}Installing dependencies...{self.RESET}")
        
        success = True
        lock = self._read_lock()
        lock.setdefault("packages", {})
        for name, spec in config.dependencies.items():
            locked_entry = lock.get("packages", {}).get(name, {})
            # Prefer locked resolved source when present
            install_spec = locked_entry.get("resolved") or locked_entry.get("version") or spec
            # If flow.toml has a richer dict (path/git), prefer that over a stale string lock
            if isinstance(spec, dict):
                install_spec = spec
            if not self.install_package(name, install_spec):
                success = False
                continue

            stdlib_path = (
                Path(__file__).parent.parent.parent / "lib" / "stdlib" / f"{name}.flow"
            )
            resolved = None
            locked_ver: Any = spec
            if stdlib_path.exists() and not isinstance(spec, dict):
                source = "stdlib"
            elif isinstance(spec, dict) and "path" in spec:
                source = "path"
            elif isinstance(spec, dict) and "git" in spec:
                source = "git"
                if self._last_install_git_sha:
                    resolved = dict(spec)
                    resolved["rev"] = self._last_install_git_sha
            else:
                source = "registry"
                pkg_ver = self.registry().resolve(
                    name, spec if isinstance(spec, str) else "*"
                )
                if pkg_ver:
                    locked_ver = pkg_ver.version
                    resolved = pkg_ver.to_dep_spec()
            entry: Dict[str, Any] = {"version": locked_ver, "source": source}
            if resolved:
                entry["resolved"] = resolved
            lock["packages"][name] = entry
        
        if success:
            self._write_lock(lock)
            print(f"\n{self.GREEN}✓ All dependencies installed (flow.lock updated){self.RESET}")
        
        return success
    
    def build(self, release: bool = False) -> bool:
        """Build the project."""
        config = self.load_config()
        if not config:
            return False
        
        entry_file = self.project_dir / config.entry
        if not entry_file.exists():
            print(f"{self.RED}Entry file not found: {config.entry}{self.RESET}")
            return False
        
        build_dir = self.project_dir / "build"
        build_dir.mkdir(exist_ok=True)
        
        output_name = config.name
        build_dir / output_name
        
        print(f"{self.BLUE}Building {config.name}...{self.RESET}")
        
        # Use the flow compiler
        flow_bin = Path(__file__).parent.parent.parent / "flow"
        
        cmd = [str(flow_bin), "compile", str(entry_file)]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"{self.RED}Build failed:{self.RESET}")
                print(result.stderr)
                return False
            
            print(f"{self.GREEN}✓ Built {output_name}{self.RESET}")
            return True
            
        except Exception as e:
            print(f"{self.RED}Build error: {e}{self.RESET}")
            return False
    
    def run(self) -> bool:
        """Build and run the project."""
        config = self.load_config()
        if not config:
            return False
        
        entry_file = self.project_dir / config.entry
        if not entry_file.exists():
            print(f"{self.RED}Entry file not found: {config.entry}{self.RESET}")
            return False
        
        # Use the flow compiler to run
        flow_bin = Path(__file__).parent.parent.parent / "flow"
        
        cmd = [str(flow_bin), "run", str(entry_file)]
        
        try:
            result = subprocess.run(cmd)
            return result.returncode == 0
        except Exception as e:
            print(f"{self.RED}Run error: {e}{self.RESET}")
            return False
    
    def clean(self) -> bool:
        """Clean build artifacts."""
        build_dir = self.project_dir / "build"
        if build_dir.exists():
            shutil.rmtree(build_dir)
            print(f"{self.GREEN}✓ Cleaned build/{self.RESET}")
        
        return True
    
    def _collect_dependency_native(self, config: "FlowPackage") -> Tuple[List[str], List[str], List[str], List[str], List[str]]:
        """Gather native sources/flags from installed dependency packages.

        Returns (sources, frameworks, libs, cflags, ldflags). Sources are absolute paths.
        Project-local native settings are applied by the caller and take precedence for
        ordering (deps first, then project).
        """
        sources: List[str] = []
        frameworks: List[str] = []
        libs: List[str] = []
        cflags: List[str] = []
        ldflags: List[str] = []
        seen_src: set = set()
        seen_fw: set = set()
        seen_lib: set = set()

        if not self.packages_dir.exists():
            return sources, frameworks, libs, cflags, ldflags

        for dep_name in config.dependencies.keys():
            dep_dir = self.packages_dir / dep_name
            dep_toml = dep_dir / "flow.toml"
            if not dep_toml.exists():
                continue
            try:
                dep_pkg = FlowPackage.from_toml(dep_toml.read_text(encoding="utf-8"))
            except Exception as e:
                print(f"{self.YELLOW}Warning: could not read {dep_toml}: {e}{self.RESET}")
                continue
            for native_src in dep_pkg.native_sources:
                native_path = (dep_dir / native_src).resolve()
                key = str(native_path)
                if key in seen_src:
                    continue
                if native_path.exists():
                    sources.append(key)
                    seen_src.add(key)
                else:
                    print(f"{self.YELLOW}Warning: dep native source not found: {native_path}{self.RESET}")
            for fw in dep_pkg.frameworks:
                if fw not in seen_fw:
                    frameworks.append(fw)
                    seen_fw.add(fw)
            for lib in dep_pkg.libs:
                if lib not in seen_lib:
                    libs.append(lib)
                    seen_lib.add(lib)
            cflags.extend(dep_pkg.cflags)
            ldflags.extend(dep_pkg.ldflags)

        return sources, frameworks, libs, cflags, ldflags

    def build_native(self, entry_file: Optional[str] = None, release: bool = False) -> bool:
        """Build the project with native source support."""
        config = self.load_config()
        if not config:
            return False
        
        # Determine entry file
        if entry_file:
            src_file = Path(entry_file)
        else:
            src_file = self.project_dir / config.entry
        
        if not src_file.exists():
            print(f"{self.RED}Entry file not found: {src_file}{self.RESET}")
            return False
        
        build_dir = self.project_dir / "build"
        build_dir.mkdir(exist_ok=True)
        
        output_name = config.name
        output_file = build_dir / output_name
        c_file = build_dir / f"{output_name}.c"
        
        print(f"{self.BLUE}Building {config.name} with native support...{self.RESET}")
        
        # Step 1: Transpile Flow to C (without compiling C)
        repo_root = Path(__file__).parent.parent.parent
        cmd = [
            "python3",
            "-m",
            "flow.transpiler",
            str(src_file),
            "--c",
            "--lenient",
            "-o",
            str(c_file),
        ]
        
        try:
            env = os.environ.copy()
            env["PYTHONPATH"] = f"{repo_root / 'src'}{os.pathsep}{env.get('PYTHONPATH', '')}".rstrip(os.pathsep)
            result = subprocess.run(cmd, capture_output=True, text=True, env=env)
            if result.returncode != 0:
                print(f"{self.RED}Flow compilation failed:{self.RESET}")
                print(result.stderr)
                return False
        except Exception as e:
            print(f"{self.RED}Flow compilation error: {e}{self.RESET}")
            return False
        
        # Step 2: Compile native sources and Flow C output together
        dep_sources, dep_frameworks, dep_libs, dep_cflags, dep_ldflags = self._collect_dependency_native(config)

        c_flags = ["-g", "-O0"] if not release else ["-O2"]
        c_flags += dep_cflags
        c_flags += config.cflags

        sources = [str(c_file)]
        sources.extend(dep_sources)

        # Add project-local native sources
        for native_src in config.native_sources:
            native_path = self.project_dir / native_src
            if native_path.exists():
                sources.append(str(native_path.resolve()))
            else:
                print(f"{self.YELLOW}Warning: native source not found: {native_src}{self.RESET}")

        # Use C++ compiler if any C++ sources are present
        uses_cxx = any(str(src).endswith((".cpp", ".cc", ".cxx", ".mm")) for src in sources)
        cc = "clang++" if uses_cxx else "clang"
        
        # Build framework flags (deps first, then project)
        framework_flags = []
        seen_fw: set = set()
        for framework in list(dep_frameworks) + list(config.frameworks):
            if framework in seen_fw:
                continue
            seen_fw.add(framework)
            framework_flags.extend(["-framework", framework])
        
        # Build library flags
        lib_flags = []
        seen_lib: set = set()
        for lib in list(dep_libs) + list(config.libs):
            if lib in seen_lib:
                continue
            seen_lib.add(lib)
            lib_flags.extend(["-l", lib])

        # Dependency ldflags before project ldflags
        all_ldflags = list(dep_ldflags) + list(config.ldflags)
        
        try:
            if uses_cxx:
                # Compile Flow-generated C with C compiler
                c_obj = build_dir / f"{output_name}.o"
                c_flags_c = [f for f in c_flags if not f.startswith("-std=c++")]
                c_compile = ["clang"] + c_flags_c + ["-c", str(c_file), "-o", str(c_obj)]
                print(f"{self.BLUE}Running: {' '.join(c_compile)}{self.RESET}")
                result = subprocess.run(c_compile, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"{self.RED}Native compilation failed:{self.RESET}")
                    print(result.stderr)
                    return False

                # Compile native sources with C++ compiler
                native_objs = []
                for idx, src in enumerate(sources[1:]):
                    src_path = Path(src)
                    obj_path = build_dir / f"{src_path.stem}_{idx}.o"
                    native_compile = ["clang++"] + c_flags + ["-c", str(src_path), "-o", str(obj_path)]
                    print(f"{self.BLUE}Running: {' '.join(native_compile)}{self.RESET}")
                    result = subprocess.run(native_compile, capture_output=True, text=True)
                    if result.returncode != 0:
                        print(f"{self.RED}Native compilation failed:{self.RESET}")
                        print(result.stderr)
                        return False
                    native_objs.append(str(obj_path))

                # Link all objects
                link_cmd = ["clang++", str(c_obj)] + native_objs + framework_flags + lib_flags + all_ldflags + ["-o", str(output_file)]
                print(f"{self.BLUE}Running: {' '.join(link_cmd)}{self.RESET}")
                result = subprocess.run(link_cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"{self.RED}Native compilation failed:{self.RESET}")
                    print(result.stderr)
                    return False
            else:
                # Compile command (all-C)
                compile_cmd = [cc] + c_flags + sources + framework_flags + lib_flags + all_ldflags + ["-o", str(output_file)]
                print(f"{self.BLUE}Running: {' '.join(compile_cmd)}{self.RESET}")
                result = subprocess.run(compile_cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"{self.RED}Native compilation failed:{self.RESET}")
                    print(result.stderr)
                    return False
            
            print(f"{self.GREEN}✓ Built {output_name}{self.RESET}")
            return True
            
        except Exception as e:
            print(f"{self.RED}Native compilation error: {e}{self.RESET}")
            return False
    
    def run_native(self, entry_file: Optional[str] = None) -> bool:
        """Build and run with native support."""
        if not self.build_native(entry_file):
            return False
        
        config = self.load_config()
        if not config:
            return False
        
        output_file = self.project_dir / "build" / config.name
        
        print(f"{self.BLUE}Running {config.name}...{self.RESET}")
        
        try:
            process = subprocess.Popen([str(output_file)])
            return process.wait() == 0
        except KeyboardInterrupt:
            try:
                print(f"{self.YELLOW}Shutdown requested (SIGINT). Waiting for app to exit...{self.RESET}")
                process.send_signal(signal.SIGINT)
                try:
                    return process.wait(timeout=5) == 0
                except subprocess.TimeoutExpired:
                    process.terminate()
                    try:
                        return process.wait(timeout=2) == 0
                    except subprocess.TimeoutExpired:
                        process.kill()
                        return False
            except Exception as e:
                print(f"{self.RED}Run error during shutdown: {e}{self.RESET}")
                return False
        except Exception as e:
            print(f"{self.RED}Run error: {e}{self.RESET}")
            return False


def main():
    """CLI entry point for package manager."""
    import argparse
    
    parser = argparse.ArgumentParser(description="FLOW Package Manager")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # init
    init_parser = subparsers.add_parser("init", help="Initialize a new project")
    init_parser.add_argument("name", nargs="?", help="Project name")
    
    # add
    add_parser = subparsers.add_parser("add", help="Add a dependency (name, name@version, --git, --path)")
    add_parser.add_argument("package", nargs="?", help="Package name or name@version")
    add_parser.add_argument("--version", "-v", default="*", help="Version req (*, ^1.0, exact)")
    add_parser.add_argument("--git", help="Git repository URL")
    add_parser.add_argument("--path", help="Local path to package")
    add_parser.add_argument("--tag", help="Git tag")
    add_parser.add_argument("--rev", help="Git commit SHA")
    add_parser.add_argument("--branch", help="Git branch")
    add_parser.add_argument(
        "--subdir",
        help="Subdirectory inside a git repo (monorepo packages)",
    )
    add_parser.add_argument(
        "--name",
        dest="dep_name",
        help="Dependency name (with --git/--path; inferred from URL if omitted)",
    )
    
    # install
    subparsers.add_parser("install", help="Install all dependencies from flow.toml")

    # search / info / publish
    search_parser = subparsers.add_parser("search", help="Search the package registry")
    search_parser.add_argument("query", nargs="?", default="", help="Search query")

    info_parser = subparsers.add_parser("info", help="Show package info")
    info_parser.add_argument("package", help="Package name")

    publish_parser = subparsers.add_parser(
        "publish", help="Register this package in the local package index"
    )
    publish_parser.add_argument("--git", help="Publish as git dependency")
    publish_parser.add_argument("--tag", help="Git tag")
    publish_parser.add_argument("--path", help="Repo-relative path override")
    publish_parser.add_argument("--dry-run", action="store_true", help="Validate only")
    
    # build
    build_parser = subparsers.add_parser("build", help="Build the project")
    build_parser.add_argument("--release", "-r", action="store_true", help="Release build")
    
    # build-native
    build_native_parser = subparsers.add_parser("build-native", help="Build with native source support")
    build_native_parser.add_argument("file", nargs="?", help="Entry file (optional)")
    build_native_parser.add_argument("--release", "-r", action="store_true", help="Release build")
    
    # run
    subparsers.add_parser("run", help="Build and run the project")
    
    # run-native
    run_native_parser = subparsers.add_parser("run-native", help="Build and run with native support")
    run_native_parser.add_argument("file", nargs="?", help="Entry file (optional)")
    
    # clean
    subparsers.add_parser("clean", help="Clean build artifacts")
    
    args = parser.parse_args()
    
    pm = FlowPackageManager()
    
    if args.command == "init":
        pm.init(args.name)
    elif args.command == "add":
        pkg = args.package or args.dep_name
        git_url = args.git
        # Positional URL shorthand: `flow add https://…/repo.git`
        if (
            pkg
            and not git_url
            and not args.path
            and FlowPackageManager._looks_like_git_url(pkg)
        ):
            git_url = pkg
            pkg = args.dep_name or FlowPackageManager._infer_git_name(git_url)
        if not pkg and not git_url and not args.path:
            add_parser.error(
                "package name or git URL required "
                "(or --git/--path; --name optional for git URLs)"
            )
        if git_url and not pkg and not args.dep_name:
            pkg = FlowPackageManager._infer_git_name(git_url)
        name = args.dep_name or pkg or "unnamed"
        if args.path and not args.dep_name and not args.package:
            add_parser.error("--name required with --path")
        pm.add(
            name,
            args.version,
            git=git_url,
            path=args.path,
            tag=args.tag,
            rev=args.rev,
            branch=args.branch,
            subdir=args.subdir,
        )
    elif args.command == "install":
        pm.install()
    elif args.command == "search":
        pm.search(args.query)
    elif args.command == "info":
        pm.info(args.package)
    elif args.command == "publish":
        pm.publish(git=args.git, tag=args.tag, path=args.path, dry_run=args.dry_run)
    elif args.command == "build":
        pm.build(args.release)
    elif args.command == "build-native":
        pm.build_native(args.file, args.release)
    elif args.command == "run":
        pm.run()
    elif args.command == "run-native":
        pm.run_native(args.file)
    elif args.command == "clean":
        pm.clean()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
