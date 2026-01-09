#!/usr/bin/env python3
"""
FLOW REPL - Interactive Mode
Run FLOW expressions and statements interactively.
"""

import sys
import os
import subprocess
import tempfile
import readline  # For history and line editing
from typing import List, Dict, Optional, Any
from pathlib import Path

# Add src to path
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from flow.parser import Lexer, Parser, FunctionDecl, StructDecl, VarDecl, Expression
from flow.c_generator import flow_to_c


class FlowREPL:
    """Interactive FLOW interpreter."""
    
    def __init__(self):
        self.variables: Dict[str, str] = {}  # name -> type
        self.var_values: Dict[str, Any] = {}  # name -> value (for display)
        self.functions: List[str] = []  # Function source code
        self.structs: List[str] = []  # Struct definitions
        self.history: List[str] = []
        self.counter = 0
        self.build_dir = PROJECT_ROOT / "build" / "repl"
        self.build_dir.mkdir(parents=True, exist_ok=True)
        
        # Colors
        self.GREEN = '\033[92m'
        self.BLUE = '\033[94m'
        self.YELLOW = '\033[93m'
        self.RED = '\033[91m'
        self.RESET = '\033[0m'
        self.BOLD = '\033[1m'
        
    def print_banner(self):
        """Print welcome banner."""
        print(f"{self.BOLD}FLOW REPL v0.3.0{self.RESET}")
        print(f"Type expressions, statements, or {self.YELLOW}:help{self.RESET} for commands")
        print(f"Press {self.YELLOW}Ctrl+D{self.RESET} or type {self.YELLOW}:quit{self.RESET} to exit")
        print()
    
    def print_help(self):
        """Print help message."""
        print(f"""
{self.BOLD}REPL Commands:{self.RESET}
  {self.YELLOW}:help{self.RESET}      Show this help
  {self.YELLOW}:quit{self.RESET}      Exit the REPL
  {self.YELLOW}:vars{self.RESET}      Show defined variables
  {self.YELLOW}:funcs{self.RESET}     Show defined functions
  {self.YELLOW}:clear{self.RESET}     Clear all definitions
  {self.YELLOW}:type <expr>{self.RESET}  Show the type of an expression

{self.BOLD}Examples:{self.RESET}
  {self.GREEN}let x = 42{self.RESET}              Define a variable
  {self.GREEN}x * 2{self.RESET}                   Evaluate expression
  {self.GREEN}function add(a: i32, b: i32) -> i32 {{ return a + b }}{self.RESET}
  {self.GREEN}add(1, 2){self.RESET}               Call function
""")
    
    def run(self):
        """Main REPL loop."""
        self.print_banner()
        
        while True:
            try:
                # Read input
                line = input(f"{self.BLUE}flow>{self.RESET} ").strip()
                
                if not line:
                    continue
                
                # Handle commands
                if line.startswith(':'):
                    self.handle_command(line)
                    continue
                
                # Handle multi-line input (functions, structs)
                if line.startswith('function ') or line.startswith('struct '):
                    line = self.read_multiline(line)
                
                # Process the input
                self.process_input(line)
                
            except EOFError:
                print(f"\n{self.YELLOW}Goodbye!{self.RESET}")
                break
            except KeyboardInterrupt:
                print(f"\n{self.YELLOW}Use :quit or Ctrl+D to exit{self.RESET}")
                continue
    
    def read_multiline(self, first_line: str) -> str:
        """Read multi-line input until braces are balanced."""
        lines = [first_line]
        brace_count = first_line.count('{') - first_line.count('}')
        
        while brace_count > 0:
            try:
                continuation = input(f"{self.BLUE}...>{self.RESET} ")
                lines.append(continuation)
                brace_count += continuation.count('{') - continuation.count('}')
            except EOFError:
                break
        
        return '\n'.join(lines)
    
    def handle_command(self, cmd: str):
        """Handle REPL commands."""
        cmd = cmd.lower()
        
        if cmd in [':quit', ':q', ':exit']:
            raise EOFError()
        elif cmd in [':help', ':h', ':?']:
            self.print_help()
        elif cmd == ':vars':
            if self.variables:
                print(f"{self.BOLD}Variables:{self.RESET}")
                for name, typ in self.variables.items():
                    val = self.var_values.get(name, '?')
                    print(f"  {self.GREEN}{name}{self.RESET}: {typ} = {val}")
            else:
                print("No variables defined")
        elif cmd == ':funcs':
            if self.functions:
                print(f"{self.BOLD}Functions:{self.RESET}")
                for func in self.functions:
                    # Extract function signature
                    sig = func.split('{')[0].strip()
                    print(f"  {self.GREEN}{sig}{self.RESET}")
            else:
                print("No functions defined")
        elif cmd == ':clear':
            self.variables.clear()
            self.var_values.clear()
            self.functions.clear()
            self.structs.clear()
            print("Cleared all definitions")
        elif cmd.startswith(':type '):
            expr = cmd[6:].strip()
            self.show_type(expr)
        else:
            print(f"{self.RED}Unknown command: {cmd}{self.RESET}")
    
    def show_type(self, expr: str):
        """Show the type of an expression."""
        # For now, just try to evaluate and infer
        print(f"{self.YELLOW}Type inference not fully implemented yet{self.RESET}")
    
    def process_input(self, line: str) -> None:
        """Process a line of input."""
        self.history.append(line)
        
        # Try to parse
        try:
            lexer = Lexer(line)
            parser = Parser(lexer)
            
            # Check if it's a function definition
            if line.strip().startswith('function '):
                self.add_function(line)
                return
            
            # Check if it's a struct definition
            if line.strip().startswith('struct '):
                self.add_struct(line)
                return
            
            # Check if it's a variable declaration
            if line.strip().startswith('let '):
                self.add_variable(line)
                return
            
            # Otherwise, treat as expression to evaluate
            self.evaluate_expression(line)
            
        except Exception as e:
            print(f"{self.RED}Error: {e}{self.RESET}")
    
    def add_function(self, func_code: str):
        """Add a function definition."""
        self.functions.append(func_code)
        # Extract function name
        try:
            lexer = Lexer(func_code)
            parser = Parser(lexer)
            decls = parser.parse()
            if decls and isinstance(decls[0], FunctionDecl):
                name = decls[0].name
                params = ', '.join([f"{p.name}: {p.type.name}" for p in decls[0].parameters])
                ret = decls[0].return_type.name
                print(f"{self.GREEN}Defined function {name}({params}) -> {ret}{self.RESET}")
        except Exception as e:
            print(f"{self.RED}Error parsing function: {e}{self.RESET}")
            self.functions.pop()
    
    def add_struct(self, struct_code: str):
        """Add a struct definition."""
        self.structs.append(struct_code)
        try:
            lexer = Lexer(struct_code)
            parser = Parser(lexer)
            decls = parser.parse()
            if decls and isinstance(decls[0], StructDecl):
                name = decls[0].name
                fields = ', '.join([f"{f.name}: {f.type.name}" for f in decls[0].fields])
                print(f"{self.GREEN}Defined struct {name} {{ {fields} }}{self.RESET}")
        except Exception as e:
            print(f"{self.RED}Error parsing struct: {e}{self.RESET}")
            self.structs.pop()
    
    def add_variable(self, var_code: str):
        """Add a variable and evaluate its initializer."""
        # Parse the let statement
        # Format: let name: type = value  OR  let name = value
        try:
            # Extract parts
            rest = var_code[4:].strip()  # Remove 'let '
            
            if '=' in rest:
                left, right = rest.split('=', 1)
                left = left.strip()
                right = right.strip()
                
                # Check for type annotation
                if ':' in left:
                    name, type_str = left.split(':', 1)
                    name = name.strip()
                    type_str = type_str.strip()
                else:
                    name = left
                    type_str = 'auto'
                
                # Evaluate the expression
                result = self.compile_and_run_expr(right)
                if result is not None:
                    self.variables[name] = type_str
                    self.var_values[name] = result
                    print(f"{self.GREEN}{name}{self.RESET} = {result}")
            else:
                print(f"{self.RED}Variable declaration needs an initializer{self.RESET}")
                
        except Exception as e:
            print(f"{self.RED}Error: {e}{self.RESET}")
    
    def evaluate_expression(self, expr: str):
        """Evaluate an expression and print the result."""
        result = self.compile_and_run_expr(expr)
        if result is not None:
            print(result)
    
    def compile_and_run_expr(self, expr: str) -> Optional[Any]:
        """Compile and run an expression, returning the result."""
        self.counter += 1
        
        # Build a complete program
        program_lines = []
        
        # Add structs
        for struct in self.structs:
            program_lines.append(struct)
        
        # Add functions
        for func in self.functions:
            program_lines.append(func)
        
        # Add a main function that prints the result
        program_lines.append("function main() -> i32 {")
        
        # Add variable declarations
        for name, typ in self.variables.items():
            val = self.var_values.get(name)
            if val is not None:
                if typ in ['f32', 'f64'] or isinstance(val, float):
                    program_lines.append(f"    let {name}: f64 = {val}")
                else:
                    program_lines.append(f"    let {name}: i32 = {val}")
        
        # Add the expression evaluation
        # Try to determine if it's an integer or float expression
        is_float = any(c in expr for c in ['.', 'sin', 'cos', 'sqrt', 'exp', 'log'])
        
        if is_float:
            program_lines.append(f"    let _result: f64 = {expr}")
            program_lines.append('    printf("%.6f\\n", _result)')
        else:
            program_lines.append(f"    let _result: i32 = {expr}")
            program_lines.append('    printf("%d\\n", _result)')
        
        program_lines.append("    return 0")
        program_lines.append("}")
        
        program = '\n'.join(program_lines)
        
        # Write to temp file
        temp_flow = self.build_dir / f"repl_{self.counter}.flow"
        temp_c = self.build_dir / f"repl_{self.counter}.c"
        temp_exe = self.build_dir / f"repl_{self.counter}"
        
        try:
            temp_flow.write_text(program)
            
            # Compile FLOW to C
            lexer = Lexer(program)
            parser = Parser(lexer)
            decls = parser.parse()
            c_code = flow_to_c(decls)
            temp_c.write_text(c_code)
            
            # Compile C to executable
            result = subprocess.run(
                ['gcc', '-O2', '-lm', str(temp_c), '-o', str(temp_exe)],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"{self.RED}Compilation error:{self.RESET}")
                print(result.stderr)
                return None
            
            # Run and capture output
            result = subprocess.run(
                [str(temp_exe)],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            output = result.stdout.strip()
            
            # Try to parse as number
            try:
                if '.' in output:
                    return float(output)
                else:
                    return int(output)
            except ValueError:
                return output
                
        except subprocess.TimeoutExpired:
            print(f"{self.RED}Execution timed out{self.RESET}")
            return None
        except Exception as e:
            print(f"{self.RED}Error: {e}{self.RESET}")
            return None
        finally:
            # Cleanup
            for f in [temp_flow, temp_c, temp_exe]:
                try:
                    f.unlink()
                except:
                    pass


def main():
    """Entry point for the REPL."""
    repl = FlowREPL()
    repl.run()


if __name__ == '__main__':
    main()
