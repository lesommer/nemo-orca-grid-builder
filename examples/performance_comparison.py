"""
Performance comparison example.

NOTE: This example demonstrates performance testing but may require
additional setup or dependencies to run successfully.
"""
import time
from orca_grid import ORCAGridBuilder

def performance_comparison():
    builder = ORCAGridBuilder(resolution="1deg")
    
    # CPU version
    start = time.time()
    grid_cpu = builder.generate_grid()
    cpu_time = time.time() - start
    
    print(f"CPU: {cpu_time:.3f}s")
    print("Optimized NumPy implementation completed successfully")

if __name__ == "__main__":
    performance_comparison()
