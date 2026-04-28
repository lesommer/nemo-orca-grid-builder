#!/usr/bin/env python3
"""
NetCDF writer for NEMO5-compliant ORCA horizontal grid files.

Outputs the 18 horizontal grid variables:
  glamt, gphit, glamu, gphiu, glamv, gphiv, glamf, gphif,
  e1t, e1u, e1v, e1f, e2t, e2u, e2v, e2f, ff_t, ff_f

Global attributes follow NEMO5 domain_cfg conventions:
  CfgName, CfgIndex, Iperio, Jperio, NFold, NFtype, VertCoord, IsfCav
"""

import numpy as np
import xarray as xr


VAR_UNITS = {
    "glam": "degrees_east",
    "gphi": "degrees_north",
    "e1": "metres",
    "e2": "metres",
    "ff": "s-1",
}

VAR_LONG_NAMES = {
    "glamt": "T-point longitude",
    "gphit": "T-point latitude",
    "glamu": "U-point longitude",
    "gphiu": "U-point latitude",
    "glamv": "V-point longitude",
    "gphiv": "V-point latitude",
    "glamf": "F-point longitude",
    "gphif": "F-point latitude",
    "e1t": "T-point zonal scale factor",
    "e1u": "U-point zonal scale factor",
    "e1v": "V-point zonal scale factor",
    "e1f": "F-point zonal scale factor",
    "e2t": "T-point meridional scale factor",
    "e2u": "U-point meridional scale factor",
    "e2v": "V-point meridional scale factor",
    "e2f": "F-point meridional scale factor",
    "ff_t": "Coriolis parameter at T-points",
    "ff_f": "Coriolis parameter at F-points",
}


def _get_units(name):
    for prefix, unit in VAR_UNITS.items():
        if name.startswith(prefix):
            return unit
    return ""


def write_netcdf(grid_data, output_path, params):
    """
    Write the horizontal grid data to a NEMO5-compliant NetCDF file.

    Args:
        grid_data: Dict with 18 horizontal grid variables as 2D arrays.
        output_path: Path to the output NetCDF file.
        params: Resolution parameters dictionary.
    """
    ny, nx = grid_data["glamt"].shape

    ds = xr.Dataset()
    ds.coords["y"] = np.arange(ny)
    ds.coords["x"] = np.arange(nx)

    var_names = [
        "glamt", "gphit", "glamu", "gphiu",
        "glamv", "gphiv", "glamf", "gphif",
        "e1t", "e1u", "e1v", "e1f",
        "e2t", "e2u", "e2v", "e2f",
        "ff_t", "ff_f",
    ]

    for name in var_names:
        if name in grid_data:
            da = xr.DataArray(
                grid_data[name].astype(np.float64),
                dims=["y", "x"],
                name=name,
            )
            da.attrs["units"] = _get_units(name)
            if name in VAR_LONG_NAMES:
                da.attrs["long_name"] = VAR_LONG_NAMES[name]
            ds[name] = da

    fold_type = params.get("fold_type", "F")

    ds.attrs["CfgName"] = "ORCA"
    ds.attrs["CfgIndex"] = float(params.get("orca_index", 2))
    ds.attrs["Iperio"] = 1
    ds.attrs["Jperio"] = 0
    ds.attrs["NFold"] = 1
    ds.attrs["NFtype"] = fold_type
    ds.attrs["VertCoord"] = "zps"
    ds.attrs["IsfCav"] = 0

    encoding = {name: {"zlib": True, "complevel": 4} for name in var_names if name in ds}
    ds.to_netcdf(output_path, encoding=encoding)
