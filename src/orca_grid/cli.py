#!/usr/bin/env python3
"""
Command-line interface for ORCA grid builder.

Usage:
    python -m orca_grid [resolution] [output_file]
    
Examples:
    python -m orca_grid 1deg domain_cfg.nc
    python -m orca_grid 0.5deg my_grid.nc
"""

import sys
from . import ORCAGridBuilder

def main():
    # Parse command line arguments
    resolution = "1deg"  # Default resolution
    output_file = "domain_cfg.nc"  # Default output
    
    if len(sys.argv) > 1:
        resolution = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    print(f"Generating ORCA grid at {resolution} resolution...")
    
    # Create and run grid builder
    builder = ORCAGridBuilder(resolution=resolution)
    result = builder.write_netcdf(output_file)
    
    print(f"Successfully created {result}")
    print("Grid generation complete!")

if __name__ == "__main__":
    main()