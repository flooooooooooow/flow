#!/usr/bin/env python3
"""
Test Metal GPU integration
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from flow.metal_runtime import get_metal_runtime, metal_is_available
    print("✓ Metal runtime imported successfully")
    
    runtime = get_metal_runtime()
    print("✓ Metal runtime created")
    
    if runtime.initialize():
        print("✓ Metal initialized successfully")
        print("Metal available:", metal_is_available())
    else:
        print("✗ Metal initialization failed")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
