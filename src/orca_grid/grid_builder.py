#!/usr/bin/env/python3
"""
ORCA grid generation based on Madec & Imbard (1996).

Generates global ocean grids following the ORCA grid family conventions
using the semi-analytical method of embedded circles in the north
stereographic polar plane.

Algorithm overview:
  1. Define J-curves (mesh parallels) as circles in the north polar
     stereographic plane via f(j) and g(j) (Eq. 1)
  2. Compute I-curves (mesh meridians) as orthogonal trajectories
     of the J-curve family (Eq. 2), integrated via the j-parameterized
     ODE derived from the orthogonality condition
  3. Project stereographic coordinates to geographic (Eq. 3)
  4. Compute scale factors from the conformal metric (Eq. 4)
  5. Apply North Fold (T-pivot or F-pivot) for the tripolar region
  6. Compute Coriolis parameter

Key equations:
  Eq. (1)  J-curve:  x² + y² - (f+g)·y + f·g = 0
  Eq. (2)  I-curve ODE (j-parameterized):
           dx/dj = 2x·(C'·y - P') / (4x² + (2y-C)²)
           dy/dj = (2y-C)·(C'·y - P') / (4x² + (2y-C)²)
           where C = f+g, P = f·g
  Eq. (3)  Projection: λ = atan2(y,x), φ = 90° - (360/π)·arctan(√(x²+y²))
  Eq. (4)  Scale factors: e = m·|∂r/∂q|, m = 2R/(1+ρ²)
  Eq. (6a) f'(j) = A₀ + A₁·j - B₀·lc_B(j) - C₀·lc_C(j)
  Eq. (6b) g'(j) = D₀ + D₁·j - E₀·lc_E(j)   [NH only]

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
    lat_rad = np.radians(lat_deg)
    lon_rad = np.radians(lon_deg)
    rho = np.tan(np.pi / 4.0 - lat_rad / 2.0)
    return rho * np.cos(lon_rad), rho * np.sin(lon_rad)


def forward_stereographic(x, y):
    rho = np.sqrt(x ** 2 + y ** 2)
    lat_deg = 90.0 - np.degrees(2.0 * np.arctan(rho))
    lon_deg = np.degrees(np.arctan2(y, x))
    return lon_deg, lat_deg


def recover_fg_from_stereo(x_stereo, y_stereo):
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


def compute_fg_paper(jeql_idx, jm, params):
    jeq = params["jeq"]
    h_spacing = params["h_spacing"]

    A0 = 0.1592509277
    A1 = -0.0030337314
    B0 = -1.9999740553
    B1 = 28.493972
    JB = 47.913129
    C0c = 0.2153139938
    C1 = 7.181609
    JC = 100.0

    D0 = 0.0356621295
    D1 = -0.0004014324
    E0 = 0.0031798337
    E1c = 2.000000
    JE = 14.679962

    j_1based = np.arange(1, jm + 1, dtype=float)

    def logcosh(j, joff, w):
        a = (j - jeq - joff) / w
        b = (j - jeq + joff) / w
        return np.log(np.cosh(a) / np.cosh(b)) / w

    f_prime = (A0 + A1 * j_1based
               - B0 * logcosh(j_1based, JB, B1)
               - C0c * logcosh(j_1based, JC, C1))

    g_prime = np.zeros_like(j_1based)
    nh_mask = j_1based >= jeq
    g_prime[nh_mask] = (D0 + D1 * j_1based[nh_mask]
                        - E0 * logcosh(j_1based[nh_mask], JE, E1c))
    sh_mask = ~nh_mask
    g_prime[sh_mask] = -f_prime[sh_mask]

    f_arr = np.zeros(jm)
    g_arr = np.zeros(jm)
    f_arr[0] = np.tan(np.pi / 4.0 - np.radians(-90.0 + h_spacing / 2.0) / 2.0)
    g_arr[0] = -f_arr[0]

    for j in range(1, jm):
        f_arr[j] = f_arr[j - 1] + 0.5 * (f_prime[j - 1] + f_prime[j])
        g_arr[j] = g_arr[j - 1] + 0.5 * (g_prime[j - 1] + g_prime[j])
        if g_arr[j] > f_arr[j]:
            g_arr[j] = f_arr[j]

    eq_j_0based = jeq - 1
    f_eq_target = 1.0
    f_arr = f_arr * (f_eq_target / f_arr[eq_j_0based]) if abs(f_arr[eq_j_0based]) > 1e-10 else f_arr
    g_arr[:eq_j_0based + 1] = -f_arr[:eq_j_0based + 1]

    return f_arr, g_arr


def compute_fg_fitted(ref_path):
    import xarray as xr

    ds = xr.open_dataset(ref_path)
    gphit = ds["gphit"].values.squeeze().astype(np.float64)
    glamt = ds["glamt"].values.squeeze().astype(np.float64)

    x_s, y_s = inverse_stereographic(glamt, gphit)
    f_arr, g_arr = recover_fg_from_stereo(x_s, y_s)

    ds.close()
    return f_arr, g_arr


def compute_icurves_ode(f_arr, g_arr, h_rad, eq_j):
    ny = len(f_arr)
    nx = len(h_rad)

    C_arr = f_arr + g_arr
    P_arr = f_arr * g_arr

    j_idx = np.arange(ny, dtype=float)
    C_spl = CubicSpline(j_idx, C_arr)
    P_spl = CubicSpline(j_idx, P_arr)

    x_grid = np.zeros((ny, nx))
    y_grid = np.zeros((ny, nx))

    f_sh = f_arr[:eq_j]
    x_grid[:eq_j, :] = np.outer(f_sh, np.cos(h_rad))
    y_grid[:eq_j, :] = np.outer(f_sh, np.sin(h_rad))

    x_grid[eq_j, :] = np.cos(h_rad)
    y_grid[eq_j, :] = np.sin(h_rad)

    if ny <= eq_j + 1:
        return x_grid, y_grid

    def ode_rhs(j, state):
        x = state[:nx]
        y = state[nx:]
        C = float(C_spl(j))
        Cp = float(C_spl(j, 1))
        Pp = float(P_spl(j, 1))

        Q = 4.0 * x ** 2 + (2.0 * y - C) ** 2
        Q = np.maximum(Q, 1e-30)

        factor = (Cp * y - Pp) / Q

        dx_dj = 2.0 * x * factor
        dy_dj = (2.0 * y - C) * factor

        return np.concatenate([dx_dj, dy_dj])

    state0 = np.concatenate([x_grid[eq_j, :], y_grid[eq_j, :]])
    j_span = (float(eq_j), float(ny - 1))
    j_eval = np.arange(eq_j, ny, dtype=float)

    sol = solve_ivp(
        ode_rhs, j_span, state0,
        t_eval=j_eval,
        method="RK45",
        rtol=1e-10,
        atol=1e-12,
        max_step=0.5,
    )

    if sol.success:
        for k, j_val in enumerate(sol.t):
            j_int = int(round(j_val))
            if 0 <= j_int < ny:
                x_grid[j_int, :] = sol.y[:nx, k]
                y_grid[j_int, :] = sol.y[nx:, k]
    else:
        x_grid[eq_j + 1:, :] = 0.0
        y_grid[eq_j + 1:, :] = 0.0

    for j in range(eq_j + 1, ny):
        C_j = C_arr[j]
        P_j = P_arr[j]
        x_j = x_grid[j, :]
        y_j = y_grid[j, :]
        phi = x_j ** 2 + y_j ** 2 - C_j * y_j + P_j
        rho_j = np.sqrt(x_j ** 2 + y_j ** 2)
        if np.max(np.abs(phi)) > 1e-6 and np.max(rho_j) > 1e-10:
            disc = C_j ** 2 - 4.0 * P_j
            disc = np.maximum(disc, 0)
            rho_from_f = (C_j + np.sqrt(disc)) / 2.0
            rho_from_g = (C_j - np.sqrt(disc)) / 2.0
            rho_target = np.where(
                np.abs(rho_from_f - rho_j) < np.abs(rho_from_g - rho_j),
                rho_from_f, rho_from_g
            )
            scale = np.where(rho_j > 1e-10, rho_target / rho_j, 1.0)
            x_grid[j, :] = x_j * scale
            y_grid[j, :] = y_j * scale

    return x_grid, y_grid


def apply_north_fold_t_pivot(x_grid, y_grid, eq_j, h_rad, fold_lon_deg):
    ny, nx = x_grid.shape
    jm = ny - 1
    im = nx

    fold_lon_rad = np.radians(fold_lon_deg)
    i_fold = None
    for i in range(nx):
        if abs((np.degrees(h_rad[i]) - fold_lon_deg + 180) % 360 - 180) < 0.1:
            i_fold = i
            break

    if i_fold is None:
        i_fold = nx // 2

    x_fold = x_grid.copy()
    y_fold = y_grid.copy()

    x_fold[-1, :i_fold] = x_grid[-1, im - 1 - np.arange(i_fold)]
    y_fold[-1, :i_fold] = y_grid[-1, im - 1 - np.arange(i_fold)]

    return x_fold, y_fold


def apply_north_fold_f_pivot(x_grid, y_grid, eq_j, h_rad, fold_lon_deg):
    ny, nx = x_grid.shape

    x_fold = x_grid.copy()
    y_fold = y_grid.copy()

    im = nx
    for i in range(nx):
        i_mirror = im - 1 - i
        if i_mirror <= i:
            break
        x_fold[-1, i] = x_grid[-1, i_mirror]
        y_fold[-1, i] = y_grid[-1, i_mirror]

    return x_fold, y_fold


def compute_staggered_coords_stereo(x_stereo, y_stereo):
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


def generate_grid(f_arr, g_arr, params):
    jm = len(f_arr)
    im = params["im"]
    jeq = params["jeq"]
    h_spacing = params["h_spacing"]
    h_offset = params["h_offset"]
    fold_type = params["fold_type"]

    h_values_deg = h_offset + h_spacing * np.arange(im, dtype=float)
    h_rad = np.radians(h_values_deg)

    eq_j = jeq - 1

    x_grid, y_grid = compute_icurves_ode(f_arr, g_arr, h_rad, eq_j)

    if fold_type == "T":
        x_grid, y_grid = apply_north_fold_t_pivot(
            x_grid, y_grid, eq_j, h_rad, h_offset
        )
    elif fold_type == "F":
        x_grid, y_grid = apply_north_fold_f_pivot(
            x_grid, y_grid, eq_j, h_rad, h_offset
        )

    x_u, y_u, x_v, y_v, x_f, y_f = compute_staggered_coords_stereo(
        x_grid, y_grid
    )

    lon_t, lat_t = forward_stereographic(x_grid, y_grid)
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


class ORCAGridBuilder:
    """
    Generate ORCA-family global ocean grids.

    Uses the Madec & Imbard (1996) semi-analytical method with embedded
    circles (J-curves) in the north stereographic polar plane and their
    orthogonal trajectories (I-curves).

    Two modes for obtaining f(j)/g(j) coefficients:
      - "paper" (default): use log-cosh parameterization from the paper
      - "fitted": recover f/g from a reference NEMO domain_cfg file
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

    def generate_grid(self, ref_path=None, fg_source="paper"):
        """
        Generate the full ORCA horizontal grid.

        Args:
            ref_path: Path to a NEMO domain_cfg.nc reference file.
                Required when fg_source="fitted". If None and
                fg_source="fitted", uses the default reference.
            fg_source: "paper" to use the log-cosh parameterization
                from the paper, "fitted" to recover f/g from a
                reference file.

        Returns:
            Dict with 18 horizontal grid variables as 2D numpy arrays.
        """
        jm = self.params["jm"]
        jeq = self.params["jeq"]

        if fg_source == "fitted":
            if ref_path is None:
                ref_path = self._ref_path()
            f_arr, g_arr = compute_fg_fitted(ref_path)
            if len(f_arr) != jm:
                f_arr = f_arr[:jm]
                g_arr = g_arr[:jm]
        elif fg_source == "paper":
            f_arr, g_arr = compute_fg_paper(jeq, jm, self.params)
        else:
            raise ValueError(
                f"Unknown fg_source: {fg_source}. Use 'paper' or 'fitted'."
            )

        return generate_grid(f_arr, g_arr, self.params)

    def generate_and_write(self, output_path, ref_path=None, fg_source="paper"):
        from .netcdf_writer import write_netcdf

        grid_data = self.generate_grid(ref_path=ref_path, fg_source=fg_source)
        write_netcdf(grid_data, output_path, self.params)
        return output_path
