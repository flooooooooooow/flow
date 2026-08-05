#!/usr/bin/env python3
"""N-Body Benchmark - Tests floating-point and struct performance"""
import time
import math

PI = 3.141592653589793
SOLAR_MASS = 4 * PI * PI
DAYS_PER_YEAR = 365.24

class Body:
    __slots__ = ['x', 'y', 'z', 'vx', 'vy', 'vz', 'mass']
    
    def __init__(self, x, y, z, vx, vy, vz, mass):
        self.x = x
        self.y = y
        self.z = z
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.mass = mass

def advance(bodies, dt):
    n = len(bodies)
    for i in range(n):
        bi = bodies[i]
        for j in range(i + 1, n):
            bj = bodies[j]
            dx = bi.x - bj.x
            dy = bi.y - bj.y
            dz = bi.z - bj.z
            
            d2 = dx * dx + dy * dy + dz * dz
            mag = dt / (d2 * math.sqrt(d2))
            
            mm_i = bi.mass * mag
            mm_j = bj.mass * mag
            
            bi.vx -= dx * mm_j
            bi.vy -= dy * mm_j
            bi.vz -= dz * mm_j
            
            bj.vx += dx * mm_i
            bj.vy += dy * mm_i
            bj.vz += dz * mm_i
    
    for b in bodies:
        b.x += dt * b.vx
        b.y += dt * b.vy
        b.z += dt * b.vz

def energy(bodies):
    e = 0.0
    n = len(bodies)
    
    for i in range(n):
        bi = bodies[i]
        v2 = bi.vx**2 + bi.vy**2 + bi.vz**2
        e += 0.5 * bi.mass * v2
        
        for j in range(i + 1, n):
            bj = bodies[j]
            dx = bi.x - bj.x
            dy = bi.y - bj.y
            dz = bi.z - bj.z
            d = math.sqrt(dx**2 + dy**2 + dz**2)
            e -= bi.mass * bj.mass / d
    
    return e

def offset_momentum(bodies):
    px = py = pz = 0.0
    for b in bodies:
        px += b.vx * b.mass
        py += b.vy * b.mass
        pz += b.vz * b.mass
    
    bodies[0].vx = -px / SOLAR_MASS
    bodies[0].vy = -py / SOLAR_MASS
    bodies[0].vz = -pz / SOLAR_MASS

def init_solar_system():
    return [
        Body(0, 0, 0, 0, 0, 0, SOLAR_MASS),  # Sun
        Body(4.84143144246472090, -1.16032004402742839, -0.103622044471123109,
             0.00166007664274403694 * DAYS_PER_YEAR,
             0.00769901118419740425 * DAYS_PER_YEAR,
             -0.0000690460016972063023 * DAYS_PER_YEAR,
             0.000954791938424326609 * SOLAR_MASS),  # Jupiter
        Body(8.34336671824457987, 4.12479856412430479, -0.403523417114321381,
             -0.00276742510726862411 * DAYS_PER_YEAR,
             0.00499852801234917238 * DAYS_PER_YEAR,
             0.0000230417297573763929 * DAYS_PER_YEAR,
             0.000285885980666130812 * SOLAR_MASS),  # Saturn
        Body(12.8943695621391310, -15.1111514016986312, -0.223307578892655734,
             0.00296460137564761618 * DAYS_PER_YEAR,
             0.00237847173959480950 * DAYS_PER_YEAR,
             -0.0000296589568540237556 * DAYS_PER_YEAR,
             0.0000436624404335156298 * SOLAR_MASS),  # Uranus
        Body(15.3796971148509165, -25.9193146099879641, 0.179258772950371181,
             0.00268067772490389322 * DAYS_PER_YEAR,
             0.00162824170038242295 * DAYS_PER_YEAR,
             -0.0000951592254519715870 * DAYS_PER_YEAR,
             0.0000515138902046611451 * SOLAR_MASS),  # Neptune
    ]

def main():
    print("==============================================")
    print("  N-BODY BENCHMARK (Solar System) - Python")
    print("==============================================")
    print()
    
    bodies = init_solar_system()
    offset_momentum(bodies)
    
    e0 = energy(bodies)
    print(f"Initial energy: {e0:.9f}")
    print()
    
    # Use smaller iterations for Python
    iterations = [100000, 500000, 1000000]
    
    for n in iterations:
        bodies = init_solar_system()
        offset_momentum(bodies)
        
        print(f"Running {n} iterations...")
        
        start = time.perf_counter()
        for _ in range(n):
            advance(bodies, 0.01)
        elapsed = time.perf_counter() - start
        
        e1 = energy(bodies)
        print(f"  Time: {elapsed:.3f} sec | Energy: {e1:.9f} | {n / elapsed / 1000000:.2f} M steps/sec")
    
    print()
    print("Benchmark complete.")

if __name__ == "__main__":
    main()
