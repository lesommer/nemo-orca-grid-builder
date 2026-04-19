"""
ORCA Grid Builder

This module implements the ORCA grid generation algorithm based on Madec & Imbard (1996).

Core Components:
- grid_builder.py: Main grid generation algorithms
- reference_algorithm.py: Reference algorithm implementation
- stereographic.py: Stereographic projection utilities
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

from .grid_builder import ORCAGridGenerator as ORCAGridBuilder
from .plotting import plot_grid_structure, plot_scale_factors, plot_staggered_points
from .validate_grid import validate_grid

__all__ = ['ORCAGridBuilder', 'validate_grid', 'plot_grid_structure', 'plot_scale_factors', 'plot_staggered_points']
