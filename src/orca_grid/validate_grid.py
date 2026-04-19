"""
Grid validation module for ORCA grids.
"""
import numpy as np
import xarray as xr

def validate_grid(generated_file, reference_file=None):
    """
    Validate generated grid against reference.
    
    Args:
        generated_file: Path to generated grid NetCDF file
        reference_file: Optional path to reference NetCDF file
        
    Returns:
        dict: Validation report with checks, errors, and warnings
    """
    # Load generated grid
    try:
        generated = xr.open_dataset(generated_file)
    except Exception as e:
        return {
            'validation_passed': False,
            'checks': {},
            'errors': [f'Could not load generated file: {e}'],
            'warnings': []
        }
    
    report = {
        'validation_passed': False,
        'checks': {},
        'errors': [],
        'warnings': []
    }
    
    # Basic validation checks
    required_vars = ['nav_lon', 'nav_lat', 'e1t', 'e2t']
    for var in required_vars:
        if var in generated:
            report['checks'][var] = True
            # Check dimensions
            if hasattr(generated[var], 'shape'):
                report['checks'][f'{var}_shape'] = generated[var].shape
        else:
            report['checks'][var] = False
            report['errors'].append(f'Missing required variable: {var}')
    
    # Check coordinate ranges
    if 'nav_lon' in generated:
        lon_range = (generated['nav_lon'].min().values, generated['nav_lon'].max().values)
        if lon_range[0] < -180 or lon_range[1] > 180:
            report['warnings'].append(f'Longitude range unusual: {lon_range}')
        report['checks']['lon_range'] = lon_range
    
    if 'nav_lat' in generated:
        lat_range = (generated['nav_lat'].min().values, generated['nav_lat'].max().values)
        if lat_range[0] < -90 or lat_range[1] > 90:
            report['warnings'].append(f'Latitude range unusual: {lat_range}')
        report['checks']['lat_range'] = lat_range
    
    # Check scale factors are positive
    if 'e1t' in generated:
        if np.any(generated['e1t'].values <= 0):
            report['errors'].append('e1t contains non-positive values')
        else:
            report['checks']['e1t_positive'] = True
    
    if 'e2t' in generated:
        if np.any(generated['e2t'].values <= 0):
            report['errors'].append('e2t contains non-positive values')
        else:
            report['checks']['e2t_positive'] = True
    
    # If reference provided, compare
    if reference_file:
        try:
            reference = xr.open_dataset(reference_file)
            
            # Compare dimensions
            for var in required_vars:
                if var in reference and var in generated:
                    gen_shape = generated[var].shape
                    ref_shape = reference[var].shape
                    if gen_shape != ref_shape:
                        report['warnings'].append(f'Shape mismatch for {var}: generated {gen_shape} vs reference {ref_shape}')
            
            report['checks']['reference_comparison'] = 'basic comparison completed'
            
        except Exception as e:
            report['errors'].append(f'Could not load reference file: {e}')
    
    # Overall validation result
    report['validation_passed'] = len(report['errors']) == 0
    
    return report
