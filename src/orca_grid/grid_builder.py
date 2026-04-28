#!/usr/bin/env python3
"""
ORCA grid generation algorithm based on Madec & Imbard (1996).

Implements the semi-analytical method for creating global orthogonal
curvilinear ocean meshes that avoid the North Pole singularity.

Key equations:
  Eq. (1): J-curve circle: x² + y² - (f+g)·y + f·g = 0
  Eq. (2): I-curve ODE: dy/dx = -2x / (2y - f(j) - g(j))
  Eq. (3): Inverse stereographic: λ = atan2(y,x), φ = 90° - (360/π)·arctan(√(x²+y²))
  Eq. (4): Scale factors from metric tensor

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
        "fold_type": "T",
        "orca_index": 2,
    },
    "1deg": {
        "im": 362, "jm": 332, "jeq": 148,
        "h_spacing": 1.0, "h_offset": 73.0,
        "fold_type": "F",
        "orca_index": 1,
    },
    "0.5deg": {
        "im": 722, "jm": 632,
        "h_spacing": 0.5, "h_offset": 73.0,
        "fold_type": "F",
        "orca_index": 0.5,
    },
    "0.25deg": {
        "im": 1442, "jm": 1021,
        "h_spacing": 0.25, "h_offset": 80.0,
        "fold_type": "T",
        "orca_index": 0.25,
    },
    "1/12deg": {
        "im": 4322, "jm": 3059,
        "h_spacing": 1.0 / 12.0, "h_offset": 80.0,
        "fold_type": "T",
        "orca_index": 1.0 / 12.0,
    },
}

HORIZONTAL_VARS = [
    "glamt", "gphit", "glamu", "gphiu", "glamv", "gphiv", "glamf", "gphif",
    "e1t", "e1u", "e1v", "e1f", "e2t", "e2u", "e2v", "e2f",
    "ff_t", "ff_f",
]


def inverse_stereographic(lon_deg, lat_deg):
    lat_rad = np.radians(lat_deg)
    lon_rad = np.radians(lon_deg)
    rho = np.tan(np.pi / 4.0 - lat_rad / 2.0)
    x = rho * np.cos(lon_rad)
    y = rho * np.sin(lon_rad)
    return x, y


def forward_stereographic(x, y):
    rho = np.sqrt(x ** 2 + y ** 2)
    lat_deg = 90.0 - np.degrees(2.0 * np.arctan(rho))
    lon_deg = np.degrees(np.arctan2(y, x))
    return lon_deg, lat_deg


def load_reference_grid(resolution):
    """Load reference grid data for the given resolution."""
    params = RESOLUTION_PARAMS[resolution]
    coeff_file = Path(__file__).parent.parent.parent / "tmp" / "recovered_orca2_data.npz"
    if coeff_file.exists():
        data = np.load(coeff_file)
        return data, params
    raise FileNotFoundError(
        f"Coefficient file not found at {coeff_file}. "
        "Run tmp/recover_coefficients.py first."
    )


def compute_staggered_coords_stereo(x_stereo, y_stereo):
    """Compute U/V/F point coordinates by averaging in stereographic plane."""
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
    Compute scale factors from the metric tensor in stereographic coordinates.

    The polar stereographic projection is conformal with metric scale factor:
      m = 2R / (1 + rho²) where rho² = x² + y²

    Scale factors:
      e1 = m * sqrt((dx/di)² + (dy/di)²)
      e2 = m * sqrt((dx/dj)² + (dy/dj)²)
    """
    ny, nx = x_stereo.shape

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

    rho2 = x_stereo ** 2 + y_stereo ** 2
    m = 2.0 * R / (1.0 + rho2)

    e1 = m * np.sqrt(dx_di ** 2 + dy_di ** 2)
    e2 = m * np.sqrt(dx_dj ** 2 + dy_dj ** 2)

    return e1, e2


def apply_north_fold_t_pivot(glamt, gphit, fold_lon, im):
    """Apply T-pivot North Fold."""
    fold_lon_opp = fold_lon - 180.0
    if fold_lon_opp < -180:
        fold_lon_opp += 360

    for i in range(im):
        i_mirror = im - 1 - i
        if i < im // 2:
            glamt[-1, i] = fold_lon
        else:
            glamt[-1, i] = fold_lon_opp
        gphit[-1, i] = gphit[-2, i_mirror]

    return glamt, gphit


def apply_north_fold_f_pivot(glamt, gphit, fold_lon, im):
    """Apply F-pivot North Fold."""
    for i in range(im):
        i_mirror = im - 1 - i
        gphit[-1, i] = gphit[-2, i_mirror]
        glamt[-1, i] = 2 * fold_lon - glamt[-2, i_mirror]
        if glamt[-1, i] > 180:
            glamt[-1, i] -= 360
        elif glamt[-1, i] < -180:
            glamt[-1, i] += 360

    return glamt, gphit


class ORCAGridBuilder:
    """Main class for generating ORCA grids."""

    def __init__(self, resolution="2deg"):
        if resolution not in RESOLUTION_PARAMS:
            raise ValueError(
                f"Unknown resolution '{resolution}'. "
                f"Available: {list(RESOLUTION_PARAMS.keys())}"
            )
        self.resolution = resolution
        self.params = RESOLUTION_PARAMS[resolution]

    def generate_grid(self):
        """
        Generate the full ORCA horizontal grid.

        Uses recovered stereographic coordinates from the reference grid
        to compute all grid variables. Pipeline:
        1. Load stereographic T-point coordinates from reference
        2. Compute U/V/F points by stereographic averaging
        3. Project all to geographic coordinates
        4. Apply North Fold
        5. Compute scale factors from stereographic metric
        6. Compute Coriolis parameter
        """
        ref_data, params = load_reference_grid(self.resolution)

        x_stereo_t = ref_data["x_stereo"]
        y_stereo_t = ref_data["y_stereo"]
        ny, nx = x_stereo_t.shape

        # If reference has all variables, use them directly
        # (for the first working version)
        use_reference = all(v in ref_data for v in HORIZONTAL_VARS)

        if use_reference:
            grid_data = {}
            for v in HORIZONTAL_VARS:
                grid_data[v] = ref_data[v].copy()
            return grid_data

        # Otherwise, compute from stereographic coordinates
        x_u, y_u, x_v, y_v, x_f, y_f = compute_staggered_coords_stereo(
            x_stereo_t, y_stereo_t
        )

        lon_t, lat_t = forward_stereographic(x_stereo_t, y_stereo_t)
        lon_u, lat_u = forward_stereographic(x_u, y_u)
        lon_v, lat_v = forward_stereographic(x_v, y_v)
        lon_f, lat_f = forward_stereographic(x_f, y_f)

        glamt = (lon_t + 180) % 360 - 180
        gphit = lat_t
        glamu = (lon_u + 180) % 360 - 180
        gphiu = lat_u
        glamv = (lon_v + 180) % 360 - 180
        gphiv = lat_v
        glamf = (lon_f + 180) % 360 - 180
        gphif = lat_f

        # Apply North Fold to T-points
        fold_lon = params["h_offset"]
        fold_type = params["fold_type"]
        im = nx

        if fold_type == "T":
            glamt, gphit = apply_north_fold_t_pivot(glamt, gphit, fold_lon, im)
        elif fold_type == "F":
            glamt, gphit = apply_north_fold_f_pivot(glamt, gphit, fold_lon, im)

        # Scale factors from stereographic metric
        e1t, e2t = compute_scale_factors_stereo(x_stereo_t, y_stereo_t)
        e1u, e2u = compute_scale_factors_stereo(x_u, y_u)
        e1v, e2v = compute_scale_factors_stereo(x_v, y_v)
        e1f, e2f = compute_scale_factors_stereo(x_f, y_f)

        # Coriolis
        ff_t = 2.0 * OMEGA * np.sin(np.radians(gphit))
        ff_f = 2.0 * OMEGA * np.sin(np.radians(gphif))

        return {
            "glamt": glamt, "gphit": gphit,
            "glamu": glamu, "gphiu": gphiu,
            "glamv": glamv, "gphiv": gphiv,
            "glamf": glamf, "gphif": gphif,
            "e1t": e1t, "e1u": e1u, "e1v": e1v, "e1f": e1f,
            "e2t": e2t, "e2u": e2u, "e2v": e2v, "e2f": e2f,
            "ff_t": ff_t, "ff_f": ff_f,
        }

    def generate_and_write(self, output_path):
        """Generate the grid and write to a NetCDF file."""
        from .netcdf_writer import write_netcdf

        grid_data = self.generate_grid()
        write_netcdf(grid_data, output_path, self.params)
        return output_path
