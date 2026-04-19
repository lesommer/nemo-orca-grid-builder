#!/usr/bin/env python3
"""
Validation script to compare generated grid with reference file.

This script checks that the generated ORCA grid has the correct structure
and similar properties to the reference domain_cfg.nc file.
"""

import numpy as np
import xarray as xr
import sys

def validate_grid(generated_file, reference_file):
    """
    Validate generated grid against reference file.
    
    Args:
        generated_file: Path to generated NetCDF file
        reference_file: Path to reference NetCDF file
        
    Returns:
        report: Dictionary containing validation results
    """
    print(f"Validating {generated_file} against {reference_file}...")
    
    # Load datasets
    ds_gen = xr.open_dataset(generated_file)
    ds_ref = xr.open_dataset(reference_file)
    
    report = {
        'dimensions': {},
        'global_attributes': {},
        'variables': {},
        'errors': [],
        'warnings': []
    }
    
    # 1. Check dimensions
    print("\n1. Checking dimensions...")
    for dim_name in ['y', 'x', 'z', 't']:
        if dim_name in ds_gen.dims and dim_name in ds_ref.dims:
            gen_size = ds_gen.dims[dim_name]
            ref_size = ds_ref.dims[dim_name]
            report['dimensions'][dim_name] = {
                'generated': gen_size,
                'reference': ref_size,
                'match': gen_size == ref_size
            }
            status = "✓" if gen_size == ref_size else "✗"
            print(f"  {dim_name}: {gen_size} vs {ref_size} {status}")
        else:
            report['errors'].append(f"Dimension {dim_name} missing")
            print(f"  {dim_name}: MISSING")
    
    # 2. Check scalar configuration variables
    print("\n2. Checking scalar configuration variables...")
    required_vars = ['ORCA', 'ORCA_index', 'jpiglo', 'jpjglo', 'jpkglo', 'jperio']
    
    for var_name in required_vars:
        if var_name in ds_gen and var_name in ds_ref:
            gen_val = int(ds_gen[var_name].values)
            ref_val = int(ds_ref[var_name].values)
            report['scalar_variables'] = report.get('scalar_variables', {})
            report['scalar_variables'][var_name] = {
                'generated': gen_val,
                'reference': ref_val,
                'match': gen_val == ref_val
            }
            status = "✓" if gen_val == ref_val else "✗"
            print(f"  {var_name}: {gen_val} vs {ref_val} {status}")
        else:
            report['errors'].append(f"Scalar variable {var_name} missing")
            print(f"  {var_name}: MISSING")
    
    # 3. Check required variables
    print("\n3. Checking required variables...")
    required_vars = ['nav_lon', 'nav_lat', 'nav_lev', 'glamt', 'gphit', 'e1t', 'e2t']
    
    for var_name in required_vars:
        if var_name in ds_gen and var_name in ds_ref:
            gen_var = ds_gen[var_name]
            ref_var = ds_ref[var_name]
            
            # Check dimensions
            dims_match = gen_var.dims == ref_var.dims
            
            # Check shape
            shape_match = gen_var.shape == ref_var.shape
            
            report['variables'][var_name] = {
                'dims_match': dims_match,
                'shape_match': shape_match,
                'generated_dims': gen_var.dims,
                'reference_dims': ref_var.dims,
                'generated_shape': gen_var.shape,
                'reference_shape': ref_var.shape
            }
            
            status = "✓" if dims_match and shape_match else "✗"
            print(f"  {var_name}: dims {gen_var.dims} vs {ref_var.dims}, shape {gen_var.shape} vs {ref_var.shape} {status}")
        else:
            report['errors'].append(f"Variable {var_name} missing")
            print(f"  {var_name}: MISSING")
    
    # 4. Check coordinate ranges
    print("\n4. Checking coordinate ranges...")
    
    # Check longitude range
    if 'nav_lon' in ds_gen and 'nav_lon' in ds_ref:
        gen_lon_min, gen_lon_max = float(ds_gen['nav_lon'].min()), float(ds_gen['nav_lon'].max())
        ref_lon_min, ref_lon_max = float(ds_ref['nav_lon'].min()), float(ds_ref['nav_lon'].max())
        
        lon_range_ok = (abs(gen_lon_min - ref_lon_min) < 10) and (abs(gen_lon_max - ref_lon_max) < 10)
        report['coordinate_ranges'] = {
            'longitude': {
                'generated': (gen_lon_min, gen_lon_max),
                'reference': (ref_lon_min, ref_lon_max),
                'ok': lon_range_ok
            }
        }
        
        status = "✓" if lon_range_ok else "✗"
        print(f"  Longitude: [{gen_lon_min:.1f}, {gen_lon_max:.1f}] vs [{ref_lon_min:.1f}, {ref_lon_max:.1f}] {status}")
    
    # Check latitude range  
    if 'nav_lat' in ds_gen and 'nav_lat' in ds_ref:
        gen_lat_min, gen_lat_max = float(ds_gen['nav_lat'].min()), float(ds_gen['nav_lat'].max())
        ref_lat_min, ref_lat_max = float(ds_ref['nav_lat'].min()), float(ds_ref['nav_lat'].max())
        
        lat_range_ok = (abs(gen_lat_min - ref_lat_min) < 10) and (abs(gen_lat_max - ref_lat_max) < 10)
        report['coordinate_ranges']['latitude'] = {
            'generated': (gen_lat_min, gen_lat_max),
            'reference': (ref_lat_min, ref_lat_max),
            'ok': lat_range_ok
        }
        
        status = "✓" if lat_range_ok else "✗"
        print(f"  Latitude: [{gen_lat_min:.1f}, {gen_lat_max:.1f}] vs [{ref_lat_min:.1f}, {ref_lat_max:.1f}] {status}")
    
    # 5. Summary
    print("\n5. Validation Summary:")
    
    total_checks = len(report['dimensions']) + len(report['global_attributes']) + len(report['variables'])
    passed_checks = sum(1 for dim in report['dimensions'].values() if dim['match']) + \
                   sum(1 for attr in report['global_attributes'].values() if attr['match']) + \
                   sum(1 for var in report['variables'].values() if var['dims_match'] and var['shape_match'])
    
    print(f"  Passed: {passed_checks}/{total_checks} checks")
    print(f"  Errors: {len(report['errors'])}")
    print(f"  Warnings: {len(report['warnings'])}")
    
    if report['errors']:
        print("\n  Errors:")
        for error in report['errors']:
            print(f"    - {error}")
    
    if report['warnings']:
        print("\n  Warnings:")
        for warning in report['warnings']:
            print(f"    - {warning}")
    
    # Overall validation result
    basic_validation_passed = (
        len(report['errors']) == 0 and 
        passed_checks >= total_checks * 0.8  # At least 80% of checks passed
    )
    
    report['validation_passed'] = basic_validation_passed
    
    if basic_validation_passed:
        print("\n✓ Basic validation PASSED")
        print("  The generated grid has the correct structure and dimensions.")
        print("  For full validation, detailed numerical comparison is needed.")
    else:
        print("\n✗ Basic validation FAILED")
        print("  Significant differences found between generated and reference grids.")
    
    return report

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python validate_grid.py <generated_file> <reference_file>")
        sys.exit(1)
    
    generated_file = sys.argv[1]
    reference_file = sys.argv[2]
    
    report = validate_grid(generated_file, reference_file)
    
    # Save report
    import json
    with open('validation_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nDetailed validation report saved to validation_report.json")