#!/usr/bin/env python3
"""
FLOW Package Manager
Manages FLOW projects and dependencies.
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import subprocess

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
                result = {"package": {}, "dependencies": {}, "dev-dependencies": {}}
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
                    elif "=" in line and current_section:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
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
    dependencies: Dict[str, str] = None
    dev_dependencies: Dict[str, str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = {}
        if self.dev_dependencies is None:
            self.dev_dependencies = {}
    
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
        
        for name, version in self.dependencies.items():
            lines.append(f'{name} = "{version}"')
        
        lines.append("")
        lines.append("[dev-dependencies]")
        
        for name, version in self.dev_dependencies.items():
            lines.append(f'{name} = "{version}"')
        
        return "\n".join(lines) + "\n"
    
    @classmethod
    def from_toml(cls, toml_str: str) -> 'FlowPackage':
        """Parse from TOML string."""
        data = tomllib.loads(toml_str)
        pkg = data.get("package", {})
        return cls(
            name=pkg.get("name", "unnamed"),
            version=pkg.get("version", "0.1.0"),
            description=pkg.get("description", ""),
            author=pkg.get("author", ""),
            license=pkg.get("license", "MIT"),
            entry=pkg.get("entry", "src/main.flow"),
            dependencies=data.get("dependencies", {}),
            dev_dependencies=data.get("dev-dependencies", {}),
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
    
    # Registry (simple local/github-based for now)
    REGISTRY_URL = "https://raw.githubusercontent.com/flow-lang/packages/main"
    
    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir).absolute()
        self.config_file = self.project_dir / "flow.toml"
        self.packages_dir = self.project_dir / "flow_packages"
        self.lock_file = self.project_dir / "flow.lock"
    
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
            description=f"A FLOW project",
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
        print(f"\nNext steps:")
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
    
    def add(self, package_name: str, version: str = "*") -> bool:
        """Add a dependency to the project."""
        config = self.load_config()
        if not config:
            return False
        
        # Check if already added
        if package_name in config.dependencies:
            print(f"{self.YELLOW}{package_name} already in dependencies{self.RESET}")
            return False
        
        # Add to dependencies
        config.dependencies[package_name] = version
        self.save_config(config)
        
        print(f"{self.GREEN}✓ Added {package_name} to dependencies{self.RESET}")
        
        # Try to install
        return self.install_package(package_name, version)
    
    def install_package(self, package_name: str, version: str = "*") -> bool:
        """Install a package from the stdlib or registry."""
        self.packages_dir.mkdir(exist_ok=True)
        
        # Check if it's a stdlib package
        stdlib_path = Path(__file__).parent.parent.parent / "lib" / "stdlib" / f"{package_name}.flow"
        if stdlib_path.exists():
            # Copy from stdlib
            dest = self.packages_dir / f"{package_name}.flow"
            shutil.copy(stdlib_path, dest)
            print(f"{self.GREEN}✓ Installed {package_name} from stdlib{self.RESET}")
            return True
        
        # Check if it's a local file
        local_path = self.project_dir / f"{package_name}.flow"
        if local_path.exists():
            print(f"{self.YELLOW}{package_name} is a local file{self.RESET}")
            return True
        
        # For now, just mark as "available via import"
        print(f"{self.YELLOW}Package {package_name} will be resolved at compile time{self.RESET}")
        return True
    
    def install(self) -> bool:
        """Install all dependencies."""
        config = self.load_config()
        if not config:
            return False
        
        print(f"{self.BLUE}Installing dependencies...{self.RESET}")
        
        success = True
        for name, version in config.dependencies.items():
            if not self.install_package(name, version):
                success = False
        
        if success:
            print(f"\n{self.GREEN}✓ All dependencies installed{self.RESET}")
        
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
        output_file = build_dir / output_name
        
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


def main():
    """CLI entry point for package manager."""
    import argparse
    
    parser = argparse.ArgumentParser(description="FLOW Package Manager")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # init
    init_parser = subparsers.add_parser("init", help="Initialize a new project")
    init_parser.add_argument("name", nargs="?", help="Project name")
    
    # add
    add_parser = subparsers.add_parser("add", help="Add a dependency")
    add_parser.add_argument("package", help="Package name")
    add_parser.add_argument("--version", "-v", default="*", help="Version")
    
    # install
    subparsers.add_parser("install", help="Install all dependencies")
    
    # build
    build_parser = subparsers.add_parser("build", help="Build the project")
    build_parser.add_argument("--release", "-r", action="store_true", help="Release build")
    
    # run
    subparsers.add_parser("run", help="Build and run the project")
    
    # clean
    subparsers.add_parser("clean", help="Clean build artifacts")
    
    args = parser.parse_args()
    
    pm = FlowPackageManager()
    
    if args.command == "init":
        pm.init(args.name)
    elif args.command == "add":
        pm.add(args.package, args.version)
    elif args.command == "install":
        pm.install()
    elif args.command == "build":
        pm.build(args.release)
    elif args.command == "run":
        pm.run()
    elif args.command == "clean":
        pm.clean()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
