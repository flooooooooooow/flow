#!/usr/bin/env python3
"""
FLOW Function Overload Resolution

Enables multiple functions with the same name but different parameter types.
Uses name mangling to generate unique C function names.
"""

from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from .parser import FunctionDecl, Type, Parameter, Expression, Variable, Literal, FunctionCall, StructLiteral, FieldAccess, BinaryOperation


@dataclass
class OverloadEntry:
    """A single overload of a function."""
    function: FunctionDecl
    param_types: List[str]  # Normalized type names
    mangled_name: str


class OverloadResolver:
    """Resolves function overloads based on argument types."""
    
    def __init__(self):
        # function_name -> list of overloads
        self._overloads: Dict[str, List[OverloadEntry]] = {}
        # Maps original (name, param_types) -> mangled_name
        self._mangled_names: Dict[Tuple[str, Tuple[str, ...]], str] = {}
        # Known variable types for resolving expressions
        self._var_types: Dict[str, str] = {}
        # Known struct definitions
        self._structs: Dict[str, Dict[str, str]] = {}  # struct_name -> {field: type}
        # Known function return types
        self._func_return_types: Dict[str, str] = {}
    
    def _normalize_type(self, t: Union[Type, str, None]) -> str:
        """Convert a Type to a normalized string for comparison."""
        if t is None:
            return "void"
        if isinstance(t, str):
            return t
        if isinstance(t, Type):
            return t.name
        return str(t)
    
    def _mangle_name(self, name: str, param_types: List[str]) -> str:
        """Generate a mangled C name for an overload."""
        if not param_types:
            return name
        suffix = "_".join(param_types)
        return f"{name}_{suffix}"
    
    def register_struct(self, name: str, fields: Dict[str, str]):
        """Register a struct definition."""
        self._structs[name] = fields
    
    def register_function(self, func: FunctionDecl):
        """Register a function, creating an overload entry."""
        name = func.name
        param_types = [self._normalize_type(p.type) for p in func.parameters]
        
        # Check if this exact overload already exists
        key = (name, tuple(param_types))
        if key in self._mangled_names:
            return  # Already registered
        
        # Create mangled name
        mangled = self._mangle_name(name, param_types)
        
        # Store overload
        if name not in self._overloads:
            self._overloads[name] = []
        
        entry = OverloadEntry(
            function=func,
            param_types=param_types,
            mangled_name=mangled
        )
        self._overloads[name].append(entry)
        self._mangled_names[key] = mangled
        
        # Track return type
        ret_type = self._normalize_type(func.return_type)
        self._func_return_types[mangled] = ret_type
        # Also store by original name for non-overloaded lookup
        if name not in self._func_return_types:
            self._func_return_types[name] = ret_type
    
    def get_overloads(self, name: str) -> List[OverloadEntry]:
        """Get all overloads for a function name."""
        return self._overloads.get(name, [])
    
    def has_overloads(self, name: str) -> bool:
        """Check if a function has multiple overloads."""
        return len(self._overloads.get(name, [])) > 1
    
    def set_var_type(self, name: str, typ: str):
        """Set the type of a variable (for expression type inference)."""
        self._var_types[name] = typ
    
    def get_expr_type(self, expr: Expression) -> Optional[str]:
        """Infer the type of an expression."""
        if isinstance(expr, Literal):
            # First check if the literal has an explicit type
            if hasattr(expr, 'type') and expr.type is not None:
                return self._normalize_type(expr.type)
            # Fall back to Python type inference
            val = expr.value
            if isinstance(val, bool):
                return "bool"
            elif isinstance(val, int):
                return "i32"
            elif isinstance(val, float):
                return "f32"
            elif isinstance(val, str):
                # Could be a string literal or a numeric literal stored as string
                if val.replace('.', '').replace('-', '').replace('e', '').replace('E', '').isdigit():
                    return "f32" if '.' in val else "i32"
                return "string"
            return None
        
        elif isinstance(expr, Variable):
            return self._var_types.get(expr.name)
        
        elif isinstance(expr, FieldAccess):
            # Get type of object, then look up field type
            obj_type = self.get_expr_type(expr.object)
            if obj_type and obj_type in self._structs:
                return self._structs[obj_type].get(expr.field)
            return None
        
        elif isinstance(expr, FunctionCall):
            # Try to find return type
            # First check if we can resolve overload
            resolved = self.resolve_call(expr)
            if resolved:
                return self._func_return_types.get(resolved)
            return self._func_return_types.get(expr.name)
        
        elif isinstance(expr, StructLiteral):
            return expr.name
        
        elif isinstance(expr, BinaryOperation):
            # Binary ops usually preserve type of operands
            left_type = self.get_expr_type(expr.left)
            right_type = self.get_expr_type(expr.right)
            # Comparison ops return bool
            if expr.operator in ('==', '!=', '<', '<=', '>', '>=', '&&', '||'):
                return "bool"
            # Arithmetic with float promotes to float
            if left_type == "f32" or right_type == "f32":
                return "f32"
            if left_type == "f64" or right_type == "f64":
                return "f64"
            return left_type or right_type
        
        return None
    
    # Math functions that should use C stdlib names (not mangled)
    C_MATH_FUNCTIONS = {'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'atan2',
                        'sinh', 'cosh', 'tanh', 'asinh', 'acosh', 'atanh',
                        'sqrt', 'cbrt', 'pow', 'exp', 'exp2', 'log', 'log2', 'log10',
                        'fabs', 'abs', 'floor', 'ceil', 'round', 'fmod',
                        'fmin', 'fmax', 'hypot'}
    PRIMITIVES = {'f32', 'f64', 'i32', 'i64', 'float', 'double', 'int', 'bool'}
    
    def resolve_call(self, call: FunctionCall) -> Optional[str]:
        """
        Resolve a function call to its mangled name.
        Returns None if no matching overload found.
        """
        name = call.name
        overloads = self._overloads.get(name, [])
        
        # If calling a C math function with primitive args, don't mangle
        if name in self.C_MATH_FUNCTIONS:
            arg_types = [self.get_expr_type(arg) for arg in call.arguments]
            all_primitive = all(
                at is None or at in self.PRIMITIVES 
                for at in arg_types
            )
            if all_primitive:
                return name  # Use C stdlib name
        
        if not overloads:
            return None  # Not a registered function - use original name

        # Extern functions must not be mangled (C ABI)
        if any(getattr(entry.function, "is_extern", False) for entry in overloads):
            return name
        
        # Get argument types
        arg_types = [self.get_expr_type(arg) for arg in call.arguments]
        
        # Find exact match first
        for entry in overloads:
            if len(entry.param_types) != len(arg_types):
                continue
            
            exact_match = True
            for param_type, arg_type in zip(entry.param_types, arg_types):
                if arg_type is None:
                    # Unknown type - not an exact match
                    exact_match = False
                    break
                if param_type != arg_type:
                    exact_match = False
                    break
            
            if exact_match:
                return entry.mangled_name
        
        # If only one overload and no exact match found, check if it's compatible
        if len(overloads) == 1:
            entry = overloads[0]
            if len(entry.param_types) == len(arg_types):
                all_compatible = True
                for param_type, arg_type in zip(entry.param_types, arg_types):
                    if arg_type is None:
                        continue  # Unknown type, might be compatible
                    if param_type != arg_type and not self._types_compatible(param_type, arg_type):
                        all_compatible = False
                        break
                if all_compatible:
                    return entry.mangled_name
                # Fallback: if there's only one overload and arity matches,
                # prefer the mangled name to avoid unresolved calls.
                return entry.mangled_name
        
        # No match found - return original name (might be C stdlib function)
        return name
    
    def _types_compatible(self, expected: str, actual: str) -> bool:
        """Check if actual type is compatible with expected type."""
        if expected == actual:
            return True
        # Allow f32/f64 interchangeability for now
        if expected in ('f32', 'f64') and actual in ('f32', 'f64'):
            return True
        # Allow i32/i64 interchangeability
        if expected in ('i32', 'i64') and actual in ('i32', 'i64'):
            return True
        return False
    
    def get_all_functions_with_mangled_names(self) -> List[Tuple[FunctionDecl, str]]:
        """Get all registered functions with their mangled names."""
        result = []
        for overloads in self._overloads.values():
            for entry in overloads:
                result.append((entry.function, entry.mangled_name))
        return result
