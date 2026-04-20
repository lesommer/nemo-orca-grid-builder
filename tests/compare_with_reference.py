#!/usr/bin/env python3
"""
Compare generated ORCA grid with reference grid.
"""

import os
import xarray as xr
import numpy as np

def compare_grids(generated_file='domain_cfg.nc', reference_file='data/domain_cfg.nc'):
    """
    Compare generated grid with reference grid.
    
    Args:
        generated_file: Path to generated grid file
        reference_file: Path to reference grid file
        
    Returns:
        dict: Comparison report with statistics and differences
    """
    
    print("🔍 Comparing generated grid with reference...")
    
    try:
        # Load both datasets
        print(f"Loading {generated_file}...")
        generated = xr.open_dataset(generated_file)
        
        print(f"Loading {reference_file}...")
        reference = xr.open_dataset(reference_file)
        
        # Initialize comparison report
        report = {
            'status': 'success',
            'variables_compared': [],
            'statistics': {},
            'differences': {},
            'warnings': [],
            'errors': []
        }
        
        # List of variables to compare
        key_vars = ['nav_lon', 'nav_lat', 'glamt', 'gphit', 'e1t', 'e2t']
        
        for var in key_vars:
            if var in generated and var in reference:
                report['variables_compared'].append(var)
                
                # Get data arrays
                gen_data = generated[var].values
                ref_data = reference[var].values
                
                # Calculate statistics
                diff = np.abs(gen_data - ref_data)
                
                report['statistics'][var] = {
                    'generated_min': float(gen_data.min()),
                    'generated_max': float(gen_data.max()),
                    'generated_mean': float(gen_data.mean()),
                    'reference_min': float(ref_data.min()),
                    'reference_max': float(ref_data.max()),
                    'reference_mean': float(ref_data.mean()),
                    'max_difference': float(diff.max()),
                    'mean_difference': float(diff.mean()),
                    'std_difference': float(diff.std())
                }
                
                # Check if differences are significant
                if diff.max() > 1e-6:  # More than 1e-6 difference
                    report['warnings'].append(f"{var}: max difference {diff.max():.6f}")
                
            else:
                missing = []
                if var not in generated:
                    missing.append(f"generated:{var}")
                if var not in reference:
                    missing.append(f"reference:{var}")
                report['errors'].append(f"Variable {var} missing in: {', '.join(missing)}")
        
        # Overall assessment
        if not report['errors'] and not report['warnings']:
            report['status'] = 'perfect_match'
        elif not report['errors'] and report['warnings']:
            report['status'] = 'minor_differences'
        else:
            report['status'] = 'has_errors'
        
        return report
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'variables_compared': [],
            'statistics': {},
            'differences': {},
            'warnings': [],
            'errors': [str(e)]
        }

def print_comparison_report(report):
    """Print comparison report in readable format."""
    
    print("\n" + "="*60)
    print("GRID COMPARISON REPORT")
    print("="*60)
    
    print(f"Status: {report['status'].upper()}")
    
    if report['variables_compared']:
        print(f"\nVariables compared: {len(report['variables_compared'])}")
        for var in report['variables_compared']:
            stats = report['statistics'][var]
            print(f"\n{var}:")
            print(f"  Generated: min={stats['generated_min']:.2f}, max={stats['generated_max']:.2f}, mean={stats['generated_mean']:.2f}")
            print(f"  Reference: min={stats['reference_min']:.2f}, max={stats['reference_max']:.2f}, mean={stats['reference_mean']:.2f}")
            print(f"  Differences: max={stats['max_difference']:.6f}, mean={stats['mean_difference']:.6f}")
    
    if report['warnings']:
        print(f"\n⚠️  Warnings ({len(report['warnings'])}):")
        for warning in report['warnings']:
            print(f"  - {warning}")
    
    if report['errors']:
        print(f"\n❌ Errors ({len(report['errors'])}):")
        for error in report['errors']:
            print(f"  - {error}")
    
    print("\n" + "="*60)
    
    if report['status'] == 'perfect_match':
        print("🎉 PERFECT MATCH: Generated grid matches reference exactly!")
    elif report['status'] == 'minor_differences':
        print("✅ GOOD MATCH: Minor differences within acceptable tolerance")
    elif report['status'] == 'has_errors':
        print("⚠️  ISSUES FOUND: Check warnings and errors above")
    else:
        print("❌ ERROR: Could not complete comparison")

def main():
    """Run grid comparison."""
    
    # Generate a test grid first
    print("🔧 Generating test grid...")
    try:
        from orca_grid.grid_generator import ORCAGridGenerator
        from orca_grid.netcdf_writer import NEMONetCDFWriter
        
        # Generate grid
        gen = ORCAGridGenerator('1deg')
        result = gen.generate_spherical_grid()
        
        # Write to NetCDF
        writer = NEMONetCDFWriter('1deg')
        writer.write_netcdf(result, "test_grid.nc")
        print("✅ Test grid generated: test_grid.nc")
    except Exception as e:
        print(f"❌ Could not generate test grid: {e}")
        return
    
    # Compare with reference
    report = compare_grids('test_grid.nc', 'data/domain_cfg.nc')
    print_comparison_report(report)
    
    # Clean up
    import os
    if os.path.exists('test_grid.nc'):
        os.remove('test_grid.nc')
        print("\n✅ Temporary test file cleaned up")

if __name__ == "__main__":
    main()
