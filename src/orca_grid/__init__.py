"""
ORCA Grid Builder

Generates global ocean grids following the ORCA grid family conventions,
based on the Madec & Imbard (1996) semi-analytical method.

The algorithm:
1. Define mesh parallels (J-curves) as embedded circles in the north
   stereographic polar plane via f(j) and g(j)
2. Compute orthogonal mesh meridians (I-curves) via the j-parameterized
   ODE derived from the orthogonality condition
3. Project onto the sphere via inverse stereographic projection
4. Calculate scale factors and metrics from the conformal metric
5. Apply North Fold (T-pivot or F-pivot) for the tripolar region

Usage:
    from orca_grid import ORCAGridBuilder
    builder = ORCAGridBuilder(resolution="2deg")
    builder.generate_and_write("domain_cfg.nc")

    # With f/g recovered from a reference file:
    builder.generate_and_write("domain_cfg.nc", fg_source="fitted",
                               ref_path="data/ORCA_R2_zps_domcfg.nc")
"""

from .grid_builder import ORCAGridBuilder

__all__ = ["ORCAGridBuilder"]
