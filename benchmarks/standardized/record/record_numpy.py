#!/usr/bin/env python3
"""Record creation benchmark using NumPy structured arrays.
Creates 8,388,608 records - the idiomatic NumPy way.
"""
import numpy as np
import time

NUM_RECORDS = 8_388_608

def main():
    start = time.perf_counter()
    
    # NumPy structured array - this is how you'd actually do it
    dtype = np.dtype([('x', np.float64), ('y', np.float64), ('z', np.float64)])
    records = np.zeros(NUM_RECORDS, dtype=dtype)
    
    # Vectorized initialization
    indices = np.arange(NUM_RECORDS, dtype=np.float64)
    records['x'] = indices * 1.0
    records['y'] = indices * 2.0
    records['z'] = indices * 3.0
    
    # Verify (prevent optimization)
    checksum = records['x'].sum() + records['y'].sum() + records['z'].sum()
    
    end = time.perf_counter()
    elapsed_us = (end - start) * 1_000_000
    
    print(f"{elapsed_us:.1f} µs (checksum: {checksum:.0f})")

if __name__ == "__main__":
    main()
