import time
import subprocess
import os

def run():
    print("Testing AoS (original)...")
    os.environ['FLOW_NO_AOSOA'] = '1'
    os.system("FLOW_HOST=python ./flow compile benchmarks/aosoa.flow --backend=c > /dev/null 2>&1")
    t1 = time.time()
    os.system("/app/build/aosoa")
    t2 = time.time()
    aos_time = t2 - t1
    print(f"AoS time: {aos_time:.4f}s")
    
    print("Testing SoA (transformed)...")
    del os.environ['FLOW_NO_AOSOA']
    os.system("FLOW_HOST=python ./flow compile benchmarks/aosoa.flow --backend=c > /dev/null 2>&1")
    t1 = time.time()
    os.system("/app/build/aosoa")
    t2 = time.time()
    soa_time = t2 - t1
    print(f"SoA time: {soa_time:.4f}s")
    print(f"Benefit: {aos_time / soa_time:.2f}x speedup")

if __name__ == '__main__':
    run()
