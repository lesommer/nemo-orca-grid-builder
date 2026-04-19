"""Performance comparison example."""
import time
from orca_grid import ORCAGridBuilder

def performance_comparison():
    builder = ORCAGridBuilder(resolution="1deg")
    
    # CPU version
    start = time.time()
    grid_cpu = builder.generate_grid(use_jax=False)
    cpu_time = time.time() - start
    
    # GPU version (if available)
    try:
        start = time.time()
        grid_gpu = builder.generate_grid(use_jax=True)
        gpu_time = time.time() - start
        print(f"CPU: {cpu_time:.3f}s, GPU: {gpu_time:.3f}s")
        print(f"GPU speedup: {cpu_time/gpu_time:.2f}x")
    except Exception as e:
        print(f"CPU: {cpu_time:.3f}s, GPU: Not available ({e})")

if __name__ == "__main__":
    performance_comparison()
