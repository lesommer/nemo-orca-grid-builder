"""
ORCA Grid Builder

This module implements the ORCA grid generation algorithm based on Madec & Imbard (1996).

Core Components:
- grid_generator.py: Main grid generation algorithms
- stereographic.py: Stereographic projection utilities
- coordinates.py: Coordinate system transformations  
- scale_factors.py: Scale factor calculations
- netcdf_writer.py: NetCDF file output

Mathematical Foundation:
The ORCA grid uses a semi-analytical method:
1. Define mesh parallels as embedded circles in stereographic polar plane
2. Compute orthogonal mesh meridians numerically
3. Project onto sphere
4. Calculate scale factors and metrics

Usage:
    from orca_grid import ORCAGridBuilder
    builder = ORCAGridBuilder(resolution="1deg")
    builder.write_netcdf("domain_cfg.nc")
"""

from .__main__ import ORCAGridBuilder

__all__ = ['ORCAGridBuilder']