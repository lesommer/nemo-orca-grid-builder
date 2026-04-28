#!/usr/bin/env python3
"""
Tests for ORCA Grid Builder.

Validates grid generation using the Madec & Imbard (1996) algorithm.
"""

import numpy as np
import pytest
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
ORCA2_REF = DATA_DIR / "ORCA_R2_zps_domcfg.nc"
ORCA1_REF = DATA_DIR / "domain_cfg.nc"


def _load_ref(path):
    import xarray as xr
    ds = xr.open_dataset(str(path))
    data = {}
    for v in ["glamt", "gphit", "glamu", "gphiu", "glamv", "gphiv",
              "glamf", "gphif", "e1t", "e1u", "e1v", "e1f",
              "e2t", "e2u", "e2v", "e2f", "ff_t", "ff_f"]:
        if v in ds:
            data[v] = ds[v].values.squeeze().astype(np.float64)
    ds.close()
    return data


class TestStereographicProjection:
    """Tests for the stereographic projection round-trip."""

    def test_roundtrip_equator(self):
        from orca_grid.grid_builder import inverse_stereographic, forward_stereographic
        lon, lat = 45.0, 0.0
        x, y = inverse_stereographic(lon, lat)
        assert abs(np.sqrt(x**2 + y**2) - 1.0) < 1e-12
        lon2, lat2 = forward_stereographic(x, y)
        assert abs(lon2 - lon) < 1e-12
        assert abs(lat2 - lat) < 1e-12

    def test_roundtrip_pole(self):
        from orca_grid.grid_builder import inverse_stereographic, forward_stereographic
        lon, lat = 0.0, 90.0
        x, y = inverse_stereographic(lon, lat)
        assert abs(x) < 1e-12 and abs(y) < 1e-12
        lon2, lat2 = forward_stereographic(x, y)
        assert abs(lat2 - 90.0) < 1e-12

    def test_roundtrip_general(self):
        from orca_grid.grid_builder import inverse_stereographic, forward_stereographic
        for lon in [0, 45, 90, 135, 180, -90]:
            for lat in [-60, -30, 0, 30, 60]:
                x, y = inverse_stereographic(float(lon), float(lat))
                lon2, lat2 = forward_stereographic(x, y)
                assert abs(lat2 - lat) < 1e-10, f"lat mismatch at ({lon},{lat})"
                lon_diff = abs((lon2 - lon + 180) % 360 - 180)
                assert lon_diff < 1e-10, f"lon mismatch at ({lon},{lat})"


class TestFGRecovery:
    """Tests for f/g recovery from reference grids."""

    def test_sh_symmetry_orca2(self):
        from orca_grid.grid_builder import inverse_stereographic, recover_fg_from_stereo
        import xarray as xr
        ds = xr.open_dataset(str(ORCA2_REF))
        gphit = ds["gphit"].values.squeeze().astype(np.float64)
        glamt = ds["glamt"].values.squeeze().astype(np.float64)
        ds.close()
        x_s, y_s = inverse_stereographic(glamt, gphit)
        f_arr, g_arr = recover_fg_from_stereo(x_s, y_s)
        eq_j = 73
        sh_err = np.max(np.abs(g_arr[:eq_j] + f_arr[:eq_j]))
        assert sh_err < 1e-10, f"SH symmetry broken: |g+f| = {sh_err}"

    def test_fg_monotonicity_orca2(self):
        from orca_grid.grid_builder import inverse_stereographic, recover_fg_from_stereo
        import xarray as xr
        ds = xr.open_dataset(str(ORCA2_REF))
        gphit = ds["gphit"].values.squeeze().astype(np.float64)
        glamt = ds["glamt"].values.squeeze().astype(np.float64)
        ds.close()
        x_s, y_s = inverse_stereographic(glamt, gphit)
        f_arr, g_arr = recover_fg_from_stereo(x_s, y_s)
        eq_j = 73
        assert np.all(np.diff(f_arr[:eq_j]) < 0), "f should decrease toward equator in SH"
        assert np.all(np.diff(f_arr[eq_j:95]) < 0), "f should decrease in early NH"


class TestORCA2Fitted:
    """Tests for ORCA2 grid generation with fitted f/g coefficients."""

    @pytest.fixture(scope="class")
    def grid(self):
        from orca_grid import ORCAGridBuilder
        builder = ORCAGridBuilder("2deg")
        return builder.generate_grid(fg_source="fitted")

    @pytest.fixture(scope="class")
    def ref(self):
        return _load_ref(ORCA2_REF)

    def test_shape(self, grid):
        assert grid["glamt"].shape == (148, 182)

    def test_equator(self, grid):
        gphit = grid["gphit"]
        eq_j = None
        for j in range(gphit.shape[0]):
            if np.allclose(gphit[j, :], 0.0, atol=0.01):
                eq_j = j
                break
        assert eq_j is not None, "No equator row found"
        assert eq_j == 73

    def test_latitude_range(self, grid):
        gphit = grid["gphit"]
        assert gphit.min() >= -91
        assert gphit.max() <= 91

    def test_scale_factors_positive(self, grid):
        for v in ["e1t", "e2t", "e1u", "e2u", "e1v", "e2v", "e1f", "e2f"]:
            assert grid[v].min() >= 0, f"{v} has negative values"

    def test_coriolis_range(self, grid):
        assert grid["ff_t"].min() >= -2 * 7.2921e-5
        assert grid["ff_t"].max() <= 2 * 7.2921e-5

    def test_sh_coordinates(self, grid, ref):
        gphit = grid["gphit"][:, :180]
        ref_gphit = ref["gphit"]
        eq_j = 73
        sh_err = np.max(np.abs(gphit[:eq_j, :] - ref_gphit[:eq_j, :]))
        assert sh_err < 1e-4, f"SH latitude error too large: {sh_err}"

    def test_dipolar_nh_coordinates(self, grid, ref):
        gphit = grid["gphit"][:, :180]
        ref_gphit = ref["gphit"]
        eq_j = 73
        dipolar_err = np.max(np.abs(gphit[eq_j:eq_j+20, :] - ref_gphit[eq_j:eq_j+20, :]))
        assert dipolar_err < 0.05, f"Dipolar NH error too large: {dipolar_err}"

    def test_sh_constant_latitude(self, grid):
        gphit = grid["gphit"]
        eq_j = 73
        for j in range(eq_j):
            lats = gphit[j, :]
            assert np.allclose(lats, lats[0], atol=0.01), f"SH row {j} not constant lat"


class TestORCA2Paper:
    """Tests for ORCA2 grid generation with paper f/g coefficients."""

    @pytest.fixture(scope="class")
    def grid(self):
        from orca_grid import ORCAGridBuilder
        builder = ORCAGridBuilder("2deg")
        return builder.generate_grid(fg_source="paper")

    def test_shape(self, grid):
        ny, nx = grid["glamt"].shape
        assert nx == 182
        assert ny >= 148

    def test_equator(self, grid):
        gphit = grid["gphit"]
        eq_j = None
        for j in range(gphit.shape[0]):
            if np.allclose(gphit[j, :], 0.0, atol=0.5):
                eq_j = j
                break
        assert eq_j is not None, "No equator row found"

    def test_latitude_range(self, grid):
        gphit = grid["gphit"]
        assert gphit.min() >= -91
        assert gphit.max() <= 91

    def test_scale_factors_positive(self, grid):
        for v in ["e1t", "e2t"]:
            assert grid[v].min() >= 0, f"{v} has negative values"


class TestORCA1Fitted:
    """Tests for ORCA1 grid generation with fitted f/g coefficients."""

    @pytest.fixture(scope="class")
    def grid(self):
        from orca_grid import ORCAGridBuilder
        builder = ORCAGridBuilder("1deg")
        return builder.generate_grid(fg_source="fitted")

    def test_shape(self, grid):
        assert grid["glamt"].shape == (331, 362)

    def test_latitude_range(self, grid):
        gphit = grid["gphit"]
        assert gphit.min() >= -91
        assert gphit.max() <= 91


class TestNetCDFOutput:
    """Tests for NetCDF output compliance."""

    def test_output_has_required_vars(self, tmp_path):
        from orca_grid import ORCAGridBuilder
        import xarray as xr

        builder = ORCAGridBuilder("2deg")
        out_path = str(tmp_path / "test_grid.nc")
        builder.generate_and_write(out_path, fg_source="paper")

        ds = xr.open_dataset(out_path)
        required = ["glamt", "gphit", "glamu", "gphiu", "glamv", "gphiv",
                     "glamf", "gphif", "e1t", "e1u", "e1v", "e1f",
                     "e2t", "e2u", "e2v", "e2f", "ff_t", "ff_f"]
        for v in required:
            assert v in ds, f"Missing variable in output: {v}"
        ds.close()

    def test_output_attributes(self, tmp_path):
        from orca_grid import ORCAGridBuilder
        import xarray as xr

        builder = ORCAGridBuilder("2deg")
        out_path = str(tmp_path / "test_grid.nc")
        builder.generate_and_write(out_path, fg_source="paper")

        ds = xr.open_dataset(out_path)
        assert ds.attrs["CfgName"] == "ORCA"
        assert ds.attrs["NFtype"] == "T"
        assert ds.attrs["Iperio"] == 1
        ds.close()

    def test_output_compressed(self, tmp_path):
        from orca_grid import ORCAGridBuilder

        builder = ORCAGridBuilder("2deg")
        out_path = str(tmp_path / "test_grid.nc")
        builder.generate_and_write(out_path, fg_source="paper")

        import os
        size = os.path.getsize(out_path)
        assert size < 5 * 1024 * 1024, f"File too large: {size / 1024:.0f} KB"


class TestODEIntegration:
    """Tests for the I-curve ODE integration."""

    def test_ode_preserves_circle_membership(self):
        from orca_grid.grid_builder import inverse_stereographic, recover_fg_from_stereo, compute_icurves_ode
        import xarray as xr
        ds = xr.open_dataset(str(ORCA2_REF))
        gphit = ds["gphit"].values.squeeze().astype(np.float64)
        glamt = ds["glamt"].values.squeeze().astype(np.float64)
        ds.close()
        x_s, y_s = inverse_stereographic(glamt, gphit)
        f_arr, g_arr = recover_fg_from_stereo(x_s, y_s)
        C_arr = f_arr + g_arr
        P_arr = f_arr * g_arr
        eq_j = 73
        h_rad = np.radians(glamt[eq_j, :])

        x_grid, y_grid = compute_icurves_ode(f_arr, g_arr, h_rad, eq_j)

        for j in [75, 80, 85, 90]:
            phi = x_grid[j, :]**2 + y_grid[j, :]**2 - C_arr[j]*y_grid[j, :] + P_arr[j]
            assert np.max(np.abs(phi)) < 1e-6, f"Row {j} not on circle: max|phi|={np.max(np.abs(phi))}"

    def test_ode_sh_matches_halfray(self):
        from orca_grid.grid_builder import inverse_stereographic, recover_fg_from_stereo, compute_icurves_ode
        import xarray as xr
        ds = xr.open_dataset(str(ORCA2_REF))
        gphit = ds["gphit"].values.squeeze().astype(np.float64)
        glamt = ds["glamt"].values.squeeze().astype(np.float64)
        ds.close()
        x_s, y_s = inverse_stereographic(glamt, gphit)
        f_arr, g_arr = recover_fg_from_stereo(x_s, y_s)
        eq_j = 73
        h_rad = np.radians(glamt[eq_j, :])

        x_grid, y_grid = compute_icurves_ode(f_arr, g_arr, h_rad, eq_j)

        for j in range(0, eq_j, 10):
            x_expected = f_arr[j] * np.cos(h_rad)
            y_expected = f_arr[j] * np.sin(h_rad)
            assert np.allclose(x_grid[j, :], x_expected, atol=1e-10)
            assert np.allclose(y_grid[j, :], y_expected, atol=1e-10)
