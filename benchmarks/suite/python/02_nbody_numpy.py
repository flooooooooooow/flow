#!/usr/bin/env python3
"""N-Body simulation using NumPy - vectorized operations.
This is how you'd actually write numerical Python.
"""
import numpy as np
import time

# Solar system constants
PI = 3.141592653589793
SOLAR_MASS = 4 * PI * PI
DAYS_PER_YEAR = 365.24

def create_bodies():
    """Create initial state as NumPy arrays."""
    # [sun, jupiter, saturn, uranus, neptune]
    # Each body: [x, y, z, vx, vy, vz, mass]
    
    bodies = np.array([
        # Sun
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, SOLAR_MASS],
        # Jupiter
        [4.84143144246472090e+00, -1.16032004402742839e+00, -1.03622044471123109e-01,
         1.66007664274403694e-03 * DAYS_PER_YEAR, 7.69901118419740425e-03 * DAYS_PER_YEAR, 
         -6.90460016972063023e-05 * DAYS_PER_YEAR, 9.54791938424326609e-04 * SOLAR_MASS],
        # Saturn  
        [8.34336671824457987e+00, 4.12479856412430479e+00, -4.03523417114321381e-01,
         -2.76742510726862411e-03 * DAYS_PER_YEAR, 4.99852801234917238e-03 * DAYS_PER_YEAR,
         2.30417297573763929e-05 * DAYS_PER_YEAR, 2.85885980666130812e-04 * SOLAR_MASS],
        # Uranus
        [1.28943695621391310e+01, -1.51111514016986312e+01, -2.23307578892655734e-01,
         2.96460137564761618e-03 * DAYS_PER_YEAR, 2.37847173959480950e-03 * DAYS_PER_YEAR,
         -2.96589568540237556e-05 * DAYS_PER_YEAR, 4.36624404335156298e-05 * SOLAR_MASS],
        # Neptune
        [1.53796971148509165e+01, -2.59193146099879641e+01, 1.79258772950371181e-01,
         2.68067772490389322e-03 * DAYS_PER_YEAR, 1.62824170038242295e-03 * DAYS_PER_YEAR,
         -9.51592254519715870e-05 * DAYS_PER_YEAR, 5.15138902046611451e-05 * SOLAR_MASS],
    ], dtype=np.float64)
    
    return bodies

def offset_momentum(bodies):
    """Offset sun's momentum to make total momentum zero."""
    px = np.sum(bodies[1:, 3] * bodies[1:, 6])
    py = np.sum(bodies[1:, 4] * bodies[1:, 6])
    pz = np.sum(bodies[1:, 5] * bodies[1:, 6])
    bodies[0, 3] = -px / SOLAR_MASS
    bodies[0, 4] = -py / SOLAR_MASS
    bodies[0, 5] = -pz / SOLAR_MASS

def energy(bodies):
    """Calculate total system energy."""
    n = len(bodies)
    # Kinetic energy
    v_sq = bodies[:, 3]**2 + bodies[:, 4]**2 + bodies[:, 5]**2
    ke = 0.5 * np.sum(bodies[:, 6] * v_sq)
    
    # Potential energy
    pe = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            dx = bodies[i, 0] - bodies[j, 0]
            dy = bodies[i, 1] - bodies[j, 1]
            dz = bodies[i, 2] - bodies[j, 2]
            dist = np.sqrt(dx*dx + dy*dy + dz*dz)
            pe -= bodies[i, 6] * bodies[j, 6] / dist
    
    return ke + pe

def advance(bodies, dt, steps):
    """Advance simulation by steps timesteps."""
    n = len(bodies)
    
    for _ in range(steps):
        # Update velocities (all pairs)
        for i in range(n):
            for j in range(i + 1, n):
                dx = bodies[i, 0] - bodies[j, 0]
                dy = bodies[i, 1] - bodies[j, 1]
                dz = bodies[i, 2] - bodies[j, 2]
                
                dist_sq = dx*dx + dy*dy + dz*dz
                dist = np.sqrt(dist_sq)
                mag = dt / (dist_sq * dist)
                
                bodies[i, 3] -= dx * bodies[j, 6] * mag
                bodies[i, 4] -= dy * bodies[j, 6] * mag
                bodies[i, 5] -= dz * bodies[j, 6] * mag
                
                bodies[j, 3] += dx * bodies[i, 6] * mag
                bodies[j, 4] += dy * bodies[i, 6] * mag
                bodies[j, 5] += dz * bodies[i, 6] * mag
        
        # Update positions
        bodies[:, 0] += dt * bodies[:, 3]
        bodies[:, 1] += dt * bodies[:, 4]
        bodies[:, 2] += dt * bodies[:, 5]

def main():
    print("=" * 50)
    print("  N-BODY BENCHMARK - Python (NumPy)")
    print("=" * 50)
    print()
    
    for n_steps in [1000, 10000, 50000]:
        bodies = create_bodies()
        offset_momentum(bodies)
        
        e_before = energy(bodies)
        
        start = time.perf_counter()
        advance(bodies, 0.01, n_steps)
        end = time.perf_counter()
        
        e_after = energy(bodies)
        elapsed_ms = (end - start) * 1000
        
        # Calculate interactions per second
        n_bodies = 5
        interactions = n_steps * n_bodies * (n_bodies - 1) // 2
        rate = interactions / (end - start) / 1e6
        
        print(f"Steps: {n_steps}")
        print(f"  Energy before: {e_before:.9f}")
        print(f"  Energy after:  {e_after:.9f}")
        print(f"  Time: {elapsed_ms:.1f} ms")
        print(f"  Rate: {rate:.2f} M interactions/sec")
        print()

if __name__ == "__main__":
    main()
