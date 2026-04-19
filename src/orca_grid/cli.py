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
    
    # Simple argument parsing
    args = sys.argv[1:]
    
    for i, arg in enumerate(args):
        if arg in ['1deg', '0.5deg', '0.25deg']:
            resolution = arg
        elif arg.endswith('.nc'):
            output_file = arg
        elif i == 0:
            resolution = arg
        elif i == 1:
            output_file = arg
    
    print(f"Generating ORCA grid at {resolution} resolution using CPU...")
    
    # Create and run grid builder
    builder = ORCAGridBuilder(resolution=resolution)
    result = builder.write_netcdf(output_file)
    
    print(f"Successfully created {result}")
    print("Grid generation complete using CPU!")

if __name__ == "__main__":
    main()