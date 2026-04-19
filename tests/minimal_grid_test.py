#!/usr/bin/env python3
"""
Minimal grid generation test for diagnostic purposes.
"""

import numpy as np
import xarray as xr

def create_minimal_grid():
    """Create a minimal test grid for comparison."""
    
    print("🧪 Creating minimal test grid...")
    
    # Create minimal coordinates
    y = np.linspace(20, 55, 10)  # Limited range for testing
    x = np.linspace(-180, 180, 10)
    
    # Create minimal grid data
    nav_lon, nav_lat = np.meshgrid(x, y)
    
    # Create xarray dataset
    ds = xr.Dataset({
        'nav_lon': (['y', 'x'], nav_lon),
        'nav_lat': (['y', 'x'], nav_lat),
        'glamt': (['y', 'x'], nav_lon),
        'gphit': (['y', 'x'], nav_lat),
        'e1t': (['y', 'x'], np.ones_like(nav_lon) * 100000),
        'e2t': (['y', 'x'], np.ones_like(nav_lat) * 100000)
    }, coords={
        'y': y,
        'x': x
    })
    
    # Add minimal attributes
    ds.attrs['title'] = 'Minimal Test Grid'
    ds.attrs['resolution'] = 'test'
    
    print(f"✅ Minimal grid created: {ds.dims}")
    return ds

def save_minimal_grid(ds, filename='minimal_test.nc'):
    """Save minimal grid to NetCDF file."""
    ds.to_netcdf(filename)
    print(f"✅ Saved to {filename}")
    return filename

def main():
    """Run minimal grid test."""
    
    # Create and save minimal grid
    ds = create_minimal_grid()
    save_minimal_grid(ds)
    
    print("\n📊 Minimal grid statistics:")
    for var in ds.data_vars:
        print(f"{var}: min={float(ds[var].min()):.2f}, max={float(ds[var].max()):.2f}")

if __name__ == "__main__":
    main()
