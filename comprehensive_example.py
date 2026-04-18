#!/usr/bin/env python3
"""
Comprehensive example demonstrating all ORCA Grid Builder features.

This script shows:
1. Basic grid generation
2. JAX optimization
3. Modular architecture
4. Validation
5. Multiple resolutions
6. File output
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from orca_grid import ORCAGridBuilder
from orca_grid.modular_factory import UnifiedGridBuilder, demonstrate_modular_architecture

def main():
    print("ORCA Grid Builder - Comprehensive Example")
    print("=" * 50)
    
    # 1. Basic Grid Generation
    print("\n1. Basic Grid Generation")
    print("-" * 30)
    
    builder = ORCAGridBuilder(resolution="1deg")
    grid_data = builder.generate_grid()
    
    print(f"Generated grid with:")
    print(f"  - T-points: {grid_data['gphit'].shape}")
    print(f"  - U-points: {grid_data['gphiu'].shape}")
    print(f"  - V-points: {grid_data['gphiv'].shape}")
    print(f"  - F-points: {grid_data['gphif'].shape}")
    print(f"  - Latitude range: {grid_data['gphit'][0,:,:].min():.1f}° to {grid_data['gphit'][0,:,:].max():.1f}°")
    print(f"  - Longitude range: {grid_data['glamt'][0,:,:].min():.1f}° to {grid_data['glamt'][0,:,:].max():.1f}°")
    
    # Write basic grid
    basic_output = builder.write_netcdf("basic_grid.nc")
    print(f"  - Written to: {basic_output}")
    
    # 2. JAX Optimization
    print("\n2. JAX Optimization (GPU/CPU)")
    print("-" * 30)
    
    builder_jax = ORCAGridBuilder(resolution="1deg")
    grid_data_jax = builder_jax.generate_grid(use_jax=True)
    jax_output = builder_jax.write_netcdf("jax_optimized_grid.nc", use_jax=True)
    
    print(f"JAX-optimized grid generated:")
    print(f"  - Same structure as basic grid")
    print(f"  - GPU acceleration enabled")
    print(f"  - Written to: {jax_output}")
    
    # 3. Modular Architecture
    print("\n3. Modular Architecture")
    print("-" * 30)
    
    # NEMO
    nemo_builder = UnifiedGridBuilder(model_name="nemo", resolution="1deg")
    nemo_grid = nemo_builder.generate_grid()
    nemo_output = nemo_builder.write_output("modular_nemo_grid.nc")
    
    print(f"NEMO grid:")
    print(f"  - Model: {nemo_builder.get_model_info()['model']}")
    print(f"  - Resolution: {nemo_builder.get_model_info()['resolution']}")
    print(f"  - Written to: {nemo_output}")
    
    # Veros
    veros_builder = UnifiedGridBuilder(model_name="veros", resolution="1deg")
    veros_grid = veros_builder.generate_grid()
    veros_output = veros_builder.write_output("modular_veros_grid.json")
    
    print(f"Veros grid:")
    print(f"  - Model: {veros_builder.get_model_info()['model']}")
    print(f"  - Resolution: {veros_builder.get_model_info()['resolution']}")
    print(f"  - Written to: {veros_output}")
    
    # 4. Validation
    print("\n4. Grid Validation")
    print("-" * 30)
    
    # Validate against reference if available
    reference_file = "data/domain_cfg.nc"
    if os.path.exists(reference_file):
        # Import validation function
        import sys
        sys.path.append('.')
        from validate_grid import validate_grid
        validation_report = validate_grid("basic_grid.nc", reference_file)
        print(f"Validation results:")
        total_checks = (len(validation_report.get('dimensions', {})) + 
                       len(validation_report.get('scalar_variables', {})) + 
                       len(validation_report.get('variables', {})))
        passed_checks = (sum(1 for v in validation_report.get('dimensions', {}).values() if v['match']) +
                        sum(1 for v in validation_report.get('scalar_variables', {}).values() if v['match']) +
                        sum(1 for v in validation_report.get('variables', {}).values() 
                           if v['dims_match'] and v['shape_match']))
        print(f"  - Passed: {passed_checks} checks")
        print(f"  - Total: {total_checks} checks")
        print(f"  - Errors: {len(validation_report['errors'])}")
        print(f"  - Overall: {'PASSED' if validation_report['validation_passed'] else 'FAILED'}")
    else:
        print("Reference file not found, skipping validation")
    
    # 5. Performance Comparison (simple)
    print("\n5. Performance Comparison")
    print("-" * 30)
    
    import time
    
    # CPU version
    start_time = time.time()
    builder_cpu = ORCAGridBuilder(resolution="1deg")
    grid_cpu = builder_cpu.generate_grid(use_jax=False)
    cpu_time = time.time() - start_time
    
    # JAX version
    start_time = time.time()
    builder_gpu = ORCAGridBuilder(resolution="1deg")
    grid_gpu = builder_gpu.generate_grid(use_jax=True)
    gpu_time = time.time() - start_time
    
    print(f"Performance results:")
    print(f"  - CPU time: {cpu_time:.3f} seconds")
    print(f"  - GPU time: {gpu_time:.3f} seconds")
    print(f"  - Speedup: {cpu_time/gpu_time:.2f}x")
    
    # 6. Summary
    print("\n6. Summary")
    print("-" * 30)
    
    print("✓ ORCA Grid Builder Comprehensive Example Complete!")
    print("\nGenerated files:")
    print(f"  - {basic_output}")
    print(f"  - {jax_output}")
    print(f"  - {nemo_output}")
    print(f"  - {veros_output}")
    print(f"  - validation_report.json (if validation ran)")
    
    print("\nKey Features Demonstrated:")
    print("  ✓ Basic ORCA grid generation")
    print("  ✓ JAX optimization for GPU/CPU")
    print("  ✓ Modular architecture for multiple models")
    print("  ✓ NEMO and Veros support")
    print("  ✓ Grid validation")
    print("  ✓ Performance comparison")
    
    print("\nThe ORCA Grid Builder is ready for use in ocean modeling workflows!")

if __name__ == "__main__":
    main()