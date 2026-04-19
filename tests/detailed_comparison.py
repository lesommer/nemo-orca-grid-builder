#!/usr/bin/env python3
"""
Detailed comparison of generated vs reference grids.
"""

import xarray as xr
import numpy as np

def detailed_comparison():
    """Perform detailed comparison between generated and reference grids."""
    
    print("🔬 Detailed Grid Comparison")
    print("="*60)
    
    try:
        # Load both grids
        print("Loading grids...")
        generated = xr.open_dataset('diagnostic_test.nc')
        reference = xr.open_dataset('data/domain_cfg.nc')
        
        # Key variables to compare
        key_vars = ['nav_lon', 'nav_lat', 'glamt', 'gphit', 'e1t', 'e2t']
        
        print("\nComparison Results:")
        print("-"*60)
        
        for var in key_vars:
            if var in generated and var in reference:
                gen_data = generated[var].values
                ref_data = reference[var].values
                
                # Handle different shapes
                if gen_data.shape != ref_data.shape:
                    print(f"{var}: SHAPE MISMATCH")
                    print(f"  Generated: {gen_data.shape}")
                    print(f"  Reference: {ref_data.shape}")
                    continue
                
                # Calculate differences
                diff = np.abs(gen_data - ref_data)
                rel_diff = 100 * diff / (np.abs(ref_data) + 1e-10)  # Avoid division by zero
                
                print(f"\n{var}:")
                print(f"  Generated: min={gen_data.min():.2f}, max={gen_data.max():.2f}, mean={gen_data.mean():.2f}")
                print(f"  Reference: min={ref_data.min():.2f}, max={ref_data.max():.2f}, mean={ref_data.mean():.2f}")
                print(f"  Abs Diff:   min={diff.min():.2f}, max={diff.max():.2f}, mean={diff.mean():.2f}")
                print(f"  Rel Diff:   min={rel_diff.min():.2f}%, max={rel_diff.max():.2f}%, mean={rel_diff.mean():.2f}%")
                
                # Check if differences are significant
                if diff.max() > 1e-6:
                    print(f"  ⚠️  SIGNIFICANT DIFFERENCES")
                else:
                    print(f"  ✅ Minor differences")
            else:
                print(f"{var}: Missing in one of the grids")
        
        print("\n" + "="*60)
        print("Analysis complete!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    detailed_comparison()
