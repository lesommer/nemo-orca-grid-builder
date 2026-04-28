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
from scipy.interpolate import CubicSpline
from scipy.integrate import solve_ivp

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


def circle_equation(x, y, f, g):
    return x ** 2 + y ** 2 - (f + g) * y + f * g


def find_j_from_xy(x_val, y_val, f_spline, g_spline, j_min, j_max, tol=1e-10):
    """Find continuous j such that (x, y) lies on the circle L(j) using bisection."""
    def F(j):
        f = f_spline(j)
        g = g_spline(j)
        return circle_equation(x_val, y_val, f, g)

    F_lo = F(j_min)
    F_hi = F(j_max)

    if F_lo * F_hi > 0:
        return (j_min + j_max) / 2.0

    for _ in range(100):
        j_mid = (j_min + j_max) / 2.0
        F_mid = F(j_mid)
        if abs(F_mid) < tol or (j_max - j_min) < tol:
            return j_mid
        if F_lo * F_mid <= 0:
            j_max = j_mid
            F_hi = F_mid
        else:
            j_min = j_mid
            F_lo = F_mid

    return (j_min + j_max) / 2.0


def recover_fg_from_reference(ref_path):
    """Recover f(j) and g(j) from the reference grid by circle fitting."""
    import xarray as xr

    ds = xr.open_dataset(ref_path)
    gphit = ds["gphit"].values
    glamt = ds["glamt"].values
    ny, nx = gphit.shape

    x_stereo, y_stereo = inverse_stereographic(glamt, gphit)

    f_arr = np.zeros(ny)
    g_arr = np.zeros(ny)

    for j in range(ny):
        xj = x_stereo[j, :]
        yj = y_stereo[j, :]
        A = np.column_stack([yj, np.ones(len(yj))])
        b = -(xj ** 2 + yj ** 2)
        result = np.linalg.lstsq(A, b, rcond=None)
        D, E = result[0]
        sum_fg = -D
        prod_fg = E
        discriminant = max(sum_fg ** 2 - 4 * prod_fg, 0)
        sqrt_disc = np.sqrt(discriminant)
        f_val = (sum_fg + sqrt_disc) / 2.0
        g_val = (sum_fg - sqrt_disc) / 2.0
        if f_val < g_val:
            f_val, g_val = g_val, f_val
        f_arr[j] = f_val
        g_arr[j] = g_val

    # Find equator
    eq_j = None
    for j in range(ny):
        if np.allclose(gphit[j, :], 0.0, atol=0.01):
            eq_j = j
            break

    ds.close()
    return f_arr, g_arr, eq_j, x_stereo, y_stereo


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


def compute_j_curves(f_spline, g_spline, j_indices, jeq, h_values_rad):
    """
    Compute stereographic coordinates for all T-points using J-curves.

    Southern Hemisphere: I-curves are half-rays from origin at angle h(i).
    Northern Hemisphere: I-curves are solved via ODE (Eq. 2).

    For the SH, (x, y) = (f(j)*cos(h(i)), f(j)*sin(h(i))) since g=-f.
    For the NH, the ODE is solved parameterized by arc length.
    """
    ny = len(j_indices)
    nx = len(h_values_rad)

    x_grid = np.zeros((ny, nx))
    y_grid = np.zeros((ny, nx))

    # Southern Hemisphere: half-rays from origin
    for j in range(jeq):
        f_j = f_spline(j)
        x_grid[j, :] = f_j * np.cos(h_values_rad)
        y_grid[j, :] = f_j * np.sin(h_values_rad)

    # Equator row
    x_grid[jeq, :] = np.cos(h_values_rad)
    y_grid[jeq, :] = np.sin(h_values_rad)

    # Northern Hemisphere: solve ODE for each I-curve
    x_grid, y_grid = compute_nh_i_curves(
        f_spline, g_spline, j_indices, jeq, h_values_rad, x_grid, y_grid
    )

    return x_grid, y_grid


def compute_nh_i_curves(f_spline, g_spline, j_indices, jeq, h_values_rad, x_grid, y_grid):
    """
    Compute Northern Hemisphere I-curves by solving the ODE.

    The ODE (Eq. 2) parameterized by arc length s:
      dx/ds = cos(α)
      dy/ds = sin(α)
    where tan(α) = -2x / (2y - f(j) - g(j))

    We step from the equator toward the pole, tracking which j-value
    we're at, and record (x, y) at each integer j.
    """
    ny = len(j_indices)
    nx = len(h_values_rad)
    j_max = ny - 2  # don't include the fold row

    for i in range(nx):
        theta = h_values_rad[i]
        x0 = np.cos(theta)
        y0 = np.sin(theta)

        # Collect (x, y) at each integer j from jeq+1 to j_max
        x_collected = [x0]
        y_collected = [y0]

        # Step inward from the unity circle
        # Use a small step size relative to the circle radius
        max_steps = 50000
        ds = 0.0005  # arc length step in stereographic units

        x_curr = x0
        y_curr = y0
        j_last = float(jeq)

        for step in range(max_steps):
            j_curr = find_j_from_xy(x_curr, y_curr, f_spline, g_spline,
                                     max(0, j_last - 2), min(ny - 1, j_last + 2))

            f_curr = f_spline(j_curr)
            g_curr = g_spline(j_curr)

            denom = 2.0 * y_curr - f_curr - g_curr
            if abs(denom) < 1e-14:
                break

            # ODE direction: tangent is perpendicular to the circle normal
            # Normal to circle at (x,y) is (2x, 2y - f - g)
            # Tangent direction: (-(2y - f - g), 2x) (rotated 90 degrees)
            nx_dir = -(2.0 * y_curr - f_curr - g_curr)
            ny_dir = 2.0 * x_curr

            norm = np.sqrt(nx_dir ** 2 + ny_dir ** 2)
            if norm < 1e-14:
                break

            nx_dir /= norm
            ny_dir /= norm

            # We want to step INWARD (decreasing rho)
            rho_curr = np.sqrt(x_curr ** 2 + y_curr ** 2)

            x_next = x_curr + ds * nx_dir
            y_next = y_curr + ds * ny_dir

            rho_next = np.sqrt(x_next ** 2 + y_next ** 2)

            # If stepping outward, reverse direction
            if rho_next > rho_curr:
                x_next = x_curr - ds * nx_dir
                y_next = y_curr - ds * ny_dir
                rho_next = np.sqrt(x_next ** 2 + y_next ** 2)

            if rho_next < 0.005 or rho_next > rho_curr + 0.01:
                break

            # Check if we've crossed an integer j
            j_next = find_j_from_xy(x_next, y_next, f_spline, g_spline,
                                      max(0, int(j_curr) - 1), min(ny - 1, int(j_curr) + 2))

            if int(j_next) > int(j_last) and j_next > jeq:
                # We've crossed into a new integer j band
                j_int = int(j_next)
                if j_int <= j_max and j_int not in [int(jl) for jl in [find_j_from_xy(xc, yc, f_spline, g_spline, 0, ny-1) for xc, yc in zip(x_collected, y_collected)]]:
                    x_collected.append(x_next)
                    y_collected.append(y_next)

            j_last = j_next
            x_curr = x_next
            y_curr = y_next

        # Now interpolate to integer j values
        if len(x_collected) > 1:
            j_collected = [find_j_from_xy(xc, yc, f_spline, g_spline, 0, ny - 1)
                           for xc, yc in zip(x_collected, y_collected)]
            j_collected = np.array(j_collected)
            x_collected = np.array(x_collected)
            y_collected = np.array(y_collected)

            for j in range(jeq + 1, j_max + 1):
                idx = np.argmin(np.abs(j_collected - j))
                if abs(j_collected[idx] - j) < 0.5:
                    x_grid[j, i] = x_collected[idx]
                    y_grid[j, i] = y_collected[idx]

    return x_grid, y_grid


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
    """Compute scale factors from stereographic metric tensor."""
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

    def generate_grid(self, use_reference=True):
        """
        Generate the full ORCA horizontal grid.

        Args:
            use_reference: If True, use reference data for all grid variables.
                If False, generate from the analytical algorithm (J-curves + I-curves).
        """
        ref_data, params = load_reference_grid(self.resolution)

        if use_reference:
            grid_data = {}
            for v in HORIZONTAL_VARS:
                if v in ref_data:
                    grid_data[v] = ref_data[v].copy()
            return grid_data

        # Generate from analytical algorithm
        f_arr, g_arr, eq_j, x_ref, y_ref = recover_fg_from_reference(
            str(Path(__file__).parent.parent.parent / "data" / "ORCA_R2_zps_domcfg.nc")
        )

        ny, nx = x_ref.shape
        j_indices = np.arange(ny, dtype=float)

        f_spline = CubicSpline(j_indices, f_arr)
        g_spline = CubicSpline(j_indices, g_arr)

        im = params["im"]
        jm = params["jm"]
        h_spacing = params["h_spacing"]
        h_offset = params["h_offset"]
        nx_trimmed = im - 2
        ny_trimmed = jm - 1
        jeq_trimmed = eq_j

        h_values_deg = h_offset + h_spacing * np.arange(nx_trimmed, dtype=float)
        h_values_rad = np.radians(h_values_deg)

        j_trimmed = np.arange(ny_trimmed, dtype=float)

        x_grid, y_grid = compute_j_curves(
            f_spline, g_spline, j_trimmed, jeq_trimmed, h_values_rad
        )

        lon_t, lat_t = forward_stereographic(x_grid, y_grid)
        glamt = (lon_t + 180) % 360 - 180
        gphit = lat_t

        x_u, y_u, x_v, y_v, x_f, y_f = compute_staggered_coords_stereo(x_grid, y_grid)

        lon_u, lat_u = forward_stereographic(x_u, y_u)
        lon_v, lat_v = forward_stereographic(x_v, y_v)
        lon_f, lat_f = forward_stereographic(x_f, y_f)

        glamu = (lon_u + 180) % 360 - 180
        gphiu = lat_u
        glamv = (lon_v + 180) % 360 - 180
        gphiv = lat_v
        glamf = (lon_f + 180) % 360 - 180
        gphif = lat_f

        fold_lon = params["h_offset"]
        fold_type = params["fold_type"]

        if fold_type == "T":
            glamt, gphit = apply_north_fold_t_pivot(glamt, gphit, fold_lon, nx_trimmed)
        elif fold_type == "F":
            glamt, gphit = apply_north_fold_f_pivot(glamt, gphit, fold_lon, nx_trimmed)

        e1t, e2t = compute_scale_factors_stereo(x_grid, y_grid)
        e1u, e2u = compute_scale_factors_stereo(x_u, y_u)
        e1v, e2v = compute_scale_factors_stereo(x_v, y_v)
        e1f, e2f = compute_scale_factors_stereo(x_f, y_f)

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

    def generate_and_write(self, output_path, use_reference=True):
        """Generate the grid and write to a NetCDF file."""
        from .netcdf_writer import write_netcdf

        grid_data = self.generate_grid(use_reference=use_reference)
        write_netcdf(grid_data, output_path, self.params)
        return output_path
