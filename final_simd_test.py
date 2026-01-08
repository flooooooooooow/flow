#!/usr/bin/env python3
"""Final comprehensive test for SIMD implementation"""

import sys
import os
sys.path.insert(0, 'src')

from flow.parser import Lexer, Parser
from flow.mlir_generator import MLIRGenerator

def test_simd_features():
    """Test all SIMD features comprehensively"""
    
    test_cases = [
        # Basic vector literals
        """
        function test_basic_literals() -> vec4<f32> {
            return <1.0, 2.0, 3.0, 4.0>
        }
        """,
        
        # Integer vectors
        """
        function test_int_vectors() -> vec4<i32> {
            let v: vec4<i32> = <1, 2, 3, 4>
            return v
        }
        """,
        
        # Vector operations
        """
        function test_vector_ops() -> vec4<f32> {
            let a: vec4<f32> = <1.0, 2.0, 3.0, 4.0>
            let b: vec4<f32> = <0.5, 0.5, 0.5, 0.5>
            return a + b * <2.0, 2.0, 2.0, 2.0>
        }
        """,
        
        # Mixed operations
        """
        function test_mixed_ops() -> vec4<f32> {
            let v1: vec4<f32> = <1.0, 2.0, 3.0, 4.0>
            let v2: vec4<f32> = <4.0, 3.0, 2.0, 1.0>
            let result: vec4<f32> = v1 + v2 - <1.0, 1.0, 1.0, 1.0>
            return result
        }
        """,
        
        # Function parameters
        """
        function test_params(v: vec4<f32>) -> vec4<f32> {
            return v * <2.0, 2.0, 2.0, 2.0>
        }
        
        function main() -> i32 {
            let v: vec4<f32> = <1.0, 2.0, 3.0, 4.0>
            let result: vec4<f32> = test_params(v)
            return 0
        }
        """
    ]
    
    print("🧪 Running Comprehensive SIMD Tests...")
    print("=" * 50)
    
    all_passed = True
    
    for i, test_code in enumerate(test_cases, 1):
        try:
            print(f"Test {i}: ", end="")
            
            # Parse
            lexer = Lexer(test_code)
            parser = Parser(lexer)
            declarations = parser.parse()
            
            # Generate MLIR
            generator = MLIRGenerator()
            mlir_code = generator.generate_module(declarations)
            
            # Verify SIMD features in output
            simd_checks = {
                "vector types": "vector<4x" in mlir_code,
                "vector literals": "dense<" in mlir_code,
                "vector operations": any(op in mlir_code for op in ["arith.addf", "arith.mulf", "arith.subf", "arith.addi"]),
            }
            
            if all(simd_checks.values()):
                print("✅ PASS")
            else:
                print("❌ FAIL - Missing SIMD features")
                for check, passed in simd_checks.items():
                    if not passed:
                        print(f"    Missing: {check}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ FAIL - {e}")
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("🎉 All SIMD tests passed! Implementation is working correctly.")
    else:
        print("⚠️  Some SIMD tests failed. Check implementation.")
    
    return all_passed

if __name__ == "__main__":
    test_simd_features()
