#!/usr/bin/env python3
"""
NetCDF writer for NEMO-compliant ORCA horizontal grid files.

Outputs only the horizontal grid variables:
  glamt, gphit, glamu, gphiu, glamv, gphiv, glamf, gphif,
  e1t, e1u, e1v, e1f, e2t, e2u, e2v, e2f, ff_t, ff_f

Follows NEMO5 domain_cfg conventions:
  - Dimensions: x, y (no time dimension on 2D variables)
  - Global attributes: CfgName, CfgIndex, Iperio, Jperio, NFold, NFtype, VertCoord, IsfCav
"""

import numpy as np
import xarray as xr


def write_netcdf(grid_data, output_path, params):
    """
    Write the horizontal grid data to a NEMO5-compliant NetCDF file.

    Args:
        grid_data: Dictionary with keys glamt, gphit, glamu, gphiu, etc.
        output_path: Path to the output NetCDF file.
        params: Resolution parameters dictionary.
    """
    ny, nx = grid_data["glamt"].shape

    ds = xr.Dataset()

    dim_y = np.arange(ny)
    dim_x = np.arange(nx)
    ds.coords["y"] = dim_y
    ds.coords["x"] = dim_x

    var_names = [
        "glamt", "gphit", "glamu", "gphiu",
        "glamv", "gphiv", "glamf", "gphif",
        "e1t", "e1u", "e1v", "e1f",
        "e2t", "e2u", "e2v", "e2f",
        "ff_t", "ff_f",
    ]

    for name in var_names:
        if name in grid_data:
            ds[name] = (["y", "x"], grid_data[name].astype(np.float64))

    fold_type = params.get("fold_type", "F")

    ds.attrs["CfgName"] = "ORCA"
    ds.attrs["CfgIndex"] = float(params.get("orca_index", 2))
    ds.attrs["Iperio"] = 1
    ds.attrs["Jperio"] = 0
    ds.attrs["NFold"] = 1
    ds.attrs["NFtype"] = fold_type
    ds.attrs["VertCoord"] = "zps"
    ds.attrs["IsfCav"] = 0

    ds.to_netcdf(output_path)
