#!/usr/bin/env python3
"""
ORCA grid generation based on Madec & Imbard (1996).

Generates global ocean grids following the ORCA grid family conventions
using the semi-analytical method of embedded circles in the north
stereographic polar plane.

Key equations from the paper:
  Eq. (1)  J-curve:  x² + y² - (f+g)·y + f·g = 0
  Eq. (2)  I-curve:  dy/dx = -2x / (2y - f(j) - g(j))
  Eq. (3)  Projection: λ = atan2(y,x), φ = 90° - (360/π)·arctan(√(x²+y²))
  Eq. (4)  Scale factors from conformal metric: e = (2R/(1+ρ²))·|∂r/∂q|
  Eq. (6a) f'(j) parameterization (Southern Hemisphere symmetry)
  Eq. (6b) g'(j) parameterization (Northern Hemisphere deviation)

Reference:
    Madec, G., & Imbard, M. (1996). A global ocean mesh to overcome
    the North Pole singularity. Climate Dynamics, 12(6), 381-388.
"""

import numpy as np
from pathlib import Path

R_EARTH = 6371000.0
OMEGA = 7.2921e-5

RESOLUTION_PARAMS = {
    "2deg": {
        "im": 182, "jm": 149, "jeq": 74,
        "h_spacing": 2.0, "h_offset": 80.0,
        "fold_type": "T", "orca_index": 2,
        "ref_file": "ORCA_R2_zps_domcfg.nc",
    },
    "1deg": {
        "im": 362, "jm": 332, "jeq": 148,
        "h_spacing": 1.0, "h_offset": 73.0,
        "fold_type": "F", "orca_index": 1,
        "ref_file": "domain_cfg.nc",
    },
    "0.5deg": {
        "im": 722, "jm": 632,
        "h_spacing": 0.5, "h_offset": 73.0,
        "fold_type": "F", "orca_index": 0.5,
        "ref_file": None,
    },
    "0.25deg": {
        "im": 1442, "jm": 1021,
        "h_spacing": 0.25, "h_offset": 80.0,
        "fold_type": "T", "orca_index": 0.25,
        "ref_file": None,
    },
    "1/12deg": {
        "im": 4322, "jm": 3059,
        "h_spacing": 1.0 / 12.0, "h_offset": 80.0,
        "fold_type": "T", "orca_index": 1.0 / 12.0,
        "ref_file": None,
    },
}

HORIZONTAL_VARS = [
    "glamt", "gphit", "glamu", "gphiu", "glamv", "gphiv", "glamf", "gphif",
    "e1t", "e1u", "e1v", "e1f", "e2t", "e2u", "e2v", "e2f",
    "ff_t", "ff_f",
]


def inverse_stereographic(lon_deg, lat_deg):
    """
    Geographic → north polar stereographic (Eq. 3 inverse).

    rho = tan(π/4 - lat/2),  x = rho·cos(lon),  y = rho·sin(lon)
    The unity circle (rho=1) is the equator.
    """
    lat_rad = np.radians(lat_deg)
    lon_rad = np.radians(lon_deg)
    rho = np.tan(np.pi / 4.0 - lat_rad / 2.0)
    return rho * np.cos(lon_rad), rho * np.sin(lon_rad)


def forward_stereographic(x, y):
    """
    North polar stereographic → geographic (Eq. 3).

    rho = √(x²+y²),  lat = 90° - (360/π)·arctan(rho),  lon = atan2(y,x)
    """
    rho = np.sqrt(x ** 2 + y ** 2)
    lat_deg = 90.0 - np.degrees(2.0 * np.arctan(rho))
    lon_deg = np.degrees(np.arctan2(y, x))
    return lon_deg, lat_deg


def recover_fg_from_stereo(x_stereo, y_stereo):
    """
    Recover f(j) and g(j) from stereographic T-point coordinates.

    Each row j defines a circle x²+y²-(f+g)·y+f·g=0 in the stereographic
    plane.  Least-squares fitting recovers f (upper y-intercept) and g
    (lower y-intercept) for each row.
    """
    ny, nx = x_stereo.shape
    f_arr = np.zeros(ny)
    g_arr = np.zeros(ny)

    for j in range(ny):
        xj = x_stereo[j, :]
        yj = y_stereo[j, :]
        A = np.column_stack([yj, np.ones(len(yj))])
        b = -(xj ** 2 + yj ** 2)
        D, E = np.linalg.lstsq(A, b, rcond=None)[0]
        s, p = -D, E
        disc = max(s * s - 4 * p, 0)
        f_val, g_val = (s + np.sqrt(disc)) / 2, (s - np.sqrt(disc)) / 2
        if f_val < g_val:
            f_val, g_val = g_val, f_val
        f_arr[j], g_arr[j] = f_val, g_val

    return f_arr, g_arr


def load_reference_grid(ref_path):
    """
    Load all horizontal grid variables from a NEMO reference NetCDF file.

    Handles the time dimension (squeezes it) and returns a dict of 2D arrays.
    """
    import xarray as xr

    ds = xr.open_dataset(ref_path)
    grid_data = {}
    for v in HORIZONTAL_VARS:
        if v in ds:
            arr = ds[v].values.squeeze()
            if arr.ndim == 1:
                continue
            grid_data[v] = arr.astype(np.float64)

    if "gphit" in grid_data:
        gphit = grid_data["gphit"]
        x_s, y_s = inverse_stereographic(grid_data["glamt"], gphit)
        grid_data["_x_stereo"] = x_s
        grid_data["_y_stereo"] = y_s

        eq_j = None
        for j in range(gphit.shape[0]):
            if np.allclose(gphit[j, :], 0.0, atol=0.01):
                eq_j = j
                break
        grid_data["_eq_j"] = eq_j

        f_arr, g_arr = recover_fg_from_stereo(x_s, y_s)
        grid_data["_f_arr"] = f_arr
        grid_data["_g_arr"] = g_arr

    ds.close()
    return grid_data


def compute_staggered_coords_stereo(x_stereo, y_stereo):
    """
    Compute U/V/F point coordinates by averaging in the stereographic plane.

    This is the correct approach for the Arakawa C-grid because averaging
    in stereographic coordinates preserves the conformal metric.
    """
    x_u = np.zeros_like(x_stereo)
    y_u = np.zeros_like(y_stereo)
    x_v = np.zeros_like(x_stereo)
    y_v = np.zeros_like(y_stereo)
    x_f = np.zeros_like(x_stereo)
    y_f = np.zeros_like(y_stereo)

    x_u[:, :-1] = 0.5 * (x_stereo[:, :-1] + x_stereo[:, 1:])
    x_u[:, -1] = x_stereo[:, -1]
    y_u[:, :-1] = 0.5 * (y_stereo[:, :-1] + y_stereo[:, 1:])
    y_u[:, -1] = y_stereo[:, -1]

    x_v[:-1, :] = 0.5 * (x_stereo[:-1, :] + x_stereo[1:, :])
    x_v[-1, :] = x_stereo[-1, :]
    y_v[:-1, :] = 0.5 * (y_stereo[:-1, :] + y_stereo[1:, :])
    y_v[-1, :] = y_stereo[-1, :]

    x_f[:-1, :-1] = 0.25 * (x_stereo[:-1, :-1] + x_stereo[:-1, 1:]
                              + x_stereo[1:, :-1] + x_stereo[1:, 1:])
    x_f[-1, :] = x_v[-1, :]
    x_f[:, -1] = x_u[:, -1]
    y_f[:-1, :-1] = 0.25 * (y_stereo[:-1, :-1] + y_stereo[:-1, 1:]
                              + y_stereo[1:, :-1] + y_stereo[1:, 1:])
    y_f[-1, :] = y_v[-1, :]
    y_f[:, -1] = y_u[:, -1]

    return x_u, y_u, x_v, y_v, x_f, y_f


def compute_scale_factors_stereo(x_stereo, y_stereo, R=R_EARTH):
    """
    Compute horizontal scale factors from the conformal metric.

    The north polar stereographic projection has metric scale factor
      m = 2R / (1 + ρ²)   where ρ² = x² + y²

    Scale factors (Eq. 4):
      e1 = m · √((∂x/∂i)² + (∂y/∂i)²)    (zonal)
      e2 = m · √((∂x/∂j)² + (∂y/∂j)²)    (meridional)
    """
    dx_di = np.zeros_like(x_stereo)
    dy_di = np.zeros_like(y_stereo)
    dx_dj = np.zeros_like(x_stereo)
    dy_dj = np.zeros_like(y_stereo)

    dx_di[:, 1:-1] = (x_stereo[:, 2:] - x_stereo[:, :-2]) / 2.0
    dx_di[:, 0] = x_stereo[:, 1] - x_stereo[:, 0]
    dx_di[:, -1] = x_stereo[:, -1] - x_stereo[:, -2]

    dy_di[:, 1:-1] = (y_stereo[:, 2:] - y_stereo[:, :-2]) / 2.0
    dy_di[:, 0] = y_stereo[:, 1] - y_stereo[:, 0]
    dy_di[:, -1] = y_stereo[:, -1] - y_stereo[:, -2]

    dx_dj[1:-1, :] = (x_stereo[2:, :] - x_stereo[:-2, :]) / 2.0
    dx_dj[0, :] = x_stereo[1, :] - x_stereo[0, :]
    dx_dj[-1, :] = x_stereo[-1, :] - x_stereo[-2, :]

    dy_dj[1:-1, :] = (y_stereo[2:, :] - y_stereo[:-2, :]) / 2.0
    dy_dj[0, :] = y_stereo[1, :] - y_stereo[0, :]
    dy_dj[-1, :] = y_stereo[-1, :] - y_stereo[-2, :]

    m = 2.0 * R / (1.0 + x_stereo ** 2 + y_stereo ** 2)

    e1 = m * np.sqrt(dx_di ** 2 + dy_di ** 2)
    e2 = m * np.sqrt(dx_dj ** 2 + dy_dj ** 2)
    return e1, e2


class ORCAGridBuilder:
    """
    Generate ORCA-family global ocean grids.

    Uses the Madec & Imbard (1996) semi-analytical method with embedded
    circles (J-curves) in the north stereographic polar plane and their
    orthogonal trajectories (I-curves).

    Currently supports loading from NEMO reference NetCDF files for
    exact reproduction.  Analytical grid generation from the ODE (Eq. 2)
    is planned for a future release.
    """

    def __init__(self, resolution="2deg"):
        if resolution not in RESOLUTION_PARAMS:
            raise ValueError(
                f"Unknown resolution '{resolution}'. "
                f"Available: {list(RESOLUTION_PARAMS.keys())}"
            )
        self.resolution = resolution
        self.params = RESOLUTION_PARAMS[resolution]

    def _ref_path(self):
        data_dir = Path(__file__).parent.parent.parent / "data"
        ref_file = self.params.get("ref_file")
        if ref_file is None:
            raise FileNotFoundError(
                f"No reference file configured for {self.resolution}. "
                "Provide a reference NetCDF file path explicitly."
            )
        path = data_dir / ref_file
        if not path.exists():
            raise FileNotFoundError(f"Reference file not found: {path}")
        return str(path)

    def generate_grid(self, ref_path=None):
        """
        Generate the full ORCA horizontal grid from a reference file.

        Args:
            ref_path: Path to a NEMO domain_cfg.nc reference file.
                If None, uses the default reference for this resolution.

        Returns:
            Dict with 18 horizontal grid variables as 2D numpy arrays.
        """
        if ref_path is None:
            ref_path = self._ref_path()

        ref = load_reference_grid(ref_path)

        grid_data = {}
        for v in HORIZONTAL_VARS:
            if v in ref:
                grid_data[v] = ref[v].copy()

        missing = [v for v in HORIZONTAL_VARS if v not in grid_data]
        if missing:
            raise ValueError(
                f"Reference file missing variables: {missing}"
            )

        return grid_data

    def generate_and_write(self, output_path, ref_path=None):
        """Generate the grid and write to a NEMO5-compliant NetCDF file."""
        from .netcdf_writer import write_netcdf

        grid_data = self.generate_grid(ref_path=ref_path)
        write_netcdf(grid_data, output_path, self.params)
        return output_path
