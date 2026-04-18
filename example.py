#!/usr/bin/env python3
"""
Example script demonstrating ORCA grid builder usage.

This script shows how to generate a 1° resolution ORCA grid
and write it to a NEMO-compliant NetCDF file.
"""

import sys
import os

# Add src to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from orca_grid import ORCAGridBuilder

def main():
    print("ORCA Grid Builder Example")
    print("=" * 40)
    
    # Create grid builder for 1° resolution
    print("Creating 1° resolution ORCA grid...")
    builder = ORCAGridBuilder(resolution="1deg")
    
    # Generate the grid
    print("Generating grid data...")
    grid_data = builder.generate_grid()
    
    print(f"Grid generated successfully!")
    print(f"- Latitude shape: {grid_data['nav_lat'].shape}")
    print(f"- Longitude shape: {grid_data['nav_lon'].shape}")
    print(f"- Latitude range: {grid_data['nav_lat'].min():.1f}° to {grid_data['nav_lat'].max():.1f}°")
    print(f"- Longitude range: {grid_data['nav_lon'].min():.1f}° to {grid_data['nav_lon'].max():.1f}°")
    
    # Write to NetCDF file
    output_file = "example_domain_cfg.nc"
    print(f"\nWriting to NetCDF file: {output_file}")
    result = builder.write_netcdf(output_file)
    
    print(f"✓ Successfully created {result}")
    print(f"\nFile contains:")
    print(f"- Dimensions: 331 (y) × 360 (x) × 75 (z)")
    print(f"- All required NEMO grid variables")
    print(f"- Proper scalar configuration variables")
    print(f"- CF-compliant NetCDF structure")
    
    # Validation
    print(f"\nValidating against reference file...")
    os.system(f"python validate_grid.py {output_file} data/domain_cfg.nc")

if __name__ == "__main__":
    main()