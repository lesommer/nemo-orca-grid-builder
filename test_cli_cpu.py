#!/usr/bin/env python3
"""
CPU-only CLI test to avoid JAX issues.
"""

import sys
import os

# Add src to path
sys.path.insert(0, 'src')

def main():
    # Parse command line arguments
    args = sys.argv[1:]
    
    if len(args) < 2:
        print("Usage: python test_cli_cpu.py [resolution] [output_file]")
        print("Example: python test_cli_cpu.py 1deg my_grid.nc")
        return
    
    resolution = args[0] if args[0] in ['1deg', '0.5deg', '0.25deg'] else "1deg"
    output_file = args[1] if args[1].endswith('.nc') else "domain_cfg.nc"
    
    print(f"Generating ORCA grid at {resolution} resolution using CPU...")
    
    try:
        # Import and use CPU-only functionality
        from orca_grid.grid_generator import ORCAGridGenerator
        from orca_grid.netcdf_writer import NEMONetCDFWriter
        
        # Generate grid without JAX
        generator = ORCAGridGenerator(resolution)
        spherical_grid = generator.generate_spherical_grid()
        
        # Calculate scale factors
        e1t, e2t = generator.calculate_scale_factors(
            spherical_grid['lat_t'], spherical_grid['lon_t']
        )
        
        # Create grid data
        grid_data = {
            'nav_lon': spherical_grid['lon_t'],
            'nav_lat': spherical_grid['lat_t'],
            'glamt': spherical_grid['lon_t'],
            'gphit': spherical_grid['lat_t'],
            'e1t': e1t,
            'e2t': e2t
        }
        
        # Write to NetCDF
        writer = NEMONetCDFWriter(resolution)
        result = writer.write_netcdf(grid_data, output_file)
        
        print(f"Successfully created {result}")
        print("Grid generation complete using CPU!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()