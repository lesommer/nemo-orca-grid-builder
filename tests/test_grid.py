#!/usr/bin/env python3
"""
Tests for ORCA Grid Builder.

Validates grid generation against reference NEMO domain_cfg files.
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


class TestORCA2:
    """Tests for ORCA2 (2°, T-pivot) grid generation."""

    @pytest.fixture(scope="class")
    def grid(self):
        from orca_grid import ORCAGridBuilder
        builder = ORCAGridBuilder("2deg")
        return builder.generate_grid()

    @pytest.fixture(scope="class")
    def ref(self):
        return _load_ref(ORCA2_REF)

    def test_shape(self, grid):
        assert grid["glamt"].shape == (148, 180)
        assert grid["gphit"].shape == (148, 180)

    @pytest.mark.parametrize("var", [
        "glamt", "gphit", "glamu", "gphiu", "glamv", "gphiv",
        "glamf", "gphif", "e1t", "e1u", "e1v", "e1f",
        "e2t", "e2u", "e2v", "e2f", "ff_t", "ff_f",
    ])
    def test_variable_match(self, grid, ref, var):
        assert var in grid, f"Missing variable: {var}"
        assert var in ref, f"Missing reference variable: {var}"
        assert grid[var].shape == ref[var].shape, f"Shape mismatch for {var}"
        err = np.max(np.abs(grid[var] - ref[var]))
        assert err < 1e-6, f"{var}: max_abs_error={err:.2e}"

    def test_equator(self, grid):
        gphit = grid["gphit"]
        eq_j = None
        for j in range(gphit.shape[0]):
            if np.allclose(gphit[j, :], 0.0, atol=0.01):
                eq_j = j
                break
        assert eq_j is not None, "No equator row found"
        assert eq_j == 73

    def test_north_fold_t_pivot(self, grid):
        glamt = grid["glamt"]
        last_row_lons = np.unique(np.round(glamt[-1, :], 1))
        assert len(last_row_lons) <= 3, "T-pivot: last T-row should have ≤3 unique lons"

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


class TestORCA1:
    """Tests for ORCA1 (1°, F-pivot) grid generation."""

    @pytest.fixture(scope="class")
    def grid(self):
        from orca_grid import ORCAGridBuilder
        builder = ORCAGridBuilder("1deg")
        return builder.generate_grid()

    @pytest.fixture(scope="class")
    def ref(self):
        return _load_ref(ORCA1_REF)

    def test_shape(self, grid):
        assert grid["glamt"].shape == (331, 360)

    @pytest.mark.parametrize("var", [
        "glamt", "gphit", "glamu", "gphiu", "glamv", "gphiv",
        "glamf", "gphif", "e1t", "e1u", "e1v", "e1f",
        "e2t", "e2u", "e2v", "e2f", "ff_t", "ff_f",
    ])
    def test_variable_match(self, grid, ref, var):
        assert var in grid, f"Missing variable: {var}"
        assert var in ref, f"Missing reference variable: {var}"
        assert grid[var].shape == ref[var].shape, f"Shape mismatch for {var}"
        err = np.max(np.abs(grid[var] - ref[var]))
        assert err < 1e-3, f"{var}: max_abs_error={err:.2e}"

    def test_north_fold_f_pivot(self, grid):
        glamf = grid["glamf"]
        last_f_lons = np.unique(np.round(glamf[-1, :], 0))
        assert len(last_f_lons) <= 2, "F-pivot: last F-row should have ≤2 unique lons"


class TestStereographicProjection:
    """Tests for the stereographic projection round-trip."""

    def test_roundtrip_equator(self):
        from orca_grid.grid_builder import inverse_stereographic, forward_stereographic
        lon, lat = 45.0, 0.0
        x, y = inverse_stereographic(lon, lat)
        assert abs(np.sqrt(x**2 + y**2) - 1.0) < 1e-12, "Equator should map to rho=1"
        lon2, lat2 = forward_stereographic(x, y)
        assert abs(lon2 - lon) < 1e-12
        assert abs(lat2 - lat) < 1e-12

    def test_roundtrip_pole(self):
        from orca_grid.grid_builder import inverse_stereographic, forward_stereographic
        lon, lat = 0.0, 90.0
        x, y = inverse_stereographic(lon, lat)
        assert abs(x) < 1e-12 and abs(y) < 1e-12, "Pole should map to origin"
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


class TestAnalyticalMode:
    """Tests for analytical grid generation mode."""

    @pytest.fixture(scope="class")
    def grid(self):
        from orca_grid import ORCAGridBuilder
        builder = ORCAGridBuilder("2deg")
        return builder.generate_grid(mode="analytical")

    @pytest.fixture(scope="class")
    def ref(self):
        return _load_ref(ORCA2_REF)

    def test_coordinates_match(self, grid, ref):
        for v in ["glamt", "gphit"]:
            err = np.max(np.abs(grid[v] - ref[v]))
            assert err < 1e-6, f"{v}: max_abs_error={err:.2e}"
        for v in ["glamu", "gphiu", "glamv", "gphiv", "glamf", "gphif"]:
            a, b = grid[v], ref[v]
            if "glam" in v:
                diff = np.abs((a - b + 180) % 360 - 180)
            else:
                diff = np.abs(a - b)
            median_err = np.median(diff)
            assert median_err < 0.01, f"{v}: median_abs_error={median_err:.2e}"

    def test_coriolis_match(self, grid, ref):
        for v in ["ff_t"]:
            err = np.max(np.abs(grid[v] - ref[v]))
            assert err < 1e-6, f"{v}: max_abs_error={err:.2e}"
        for v in ["ff_f"]:
            err = np.max(np.abs(grid[v] - ref[v]))
            assert err < 1e-4, f"{v}: max_abs_error={err:.2e}"

    def test_scale_factors_reasonable(self, grid, ref):
        for v in ["e1t", "e2t", "e1u", "e2u", "e1v", "e2v", "e1f", "e2f"]:
            mask = ref[v] > 100
            if mask.sum() > 0:
                rel_err = np.median(np.abs((grid[v][mask] - ref[v][mask]) / ref[v][mask])) * 100
                assert rel_err < 1.0, f"{v}: median rel error={rel_err:.2f}%"

    def test_sh_half_rays(self, grid):
        gphit = grid["gphit"]
        for j in range(73):
            lats = gphit[j, :]
            assert np.allclose(lats, lats[0], atol=0.01), f"SH row {j} not constant lat"


class TestNetCDFOutput:
    """Tests for NetCDF output compliance."""

    def test_output_has_required_vars(self, tmp_path):
        from orca_grid import ORCAGridBuilder
        import xarray as xr

        builder = ORCAGridBuilder("2deg")
        out_path = str(tmp_path / "test_grid.nc")
        builder.generate_and_write(out_path)

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
        builder.generate_and_write(out_path)

        ds = xr.open_dataset(out_path)
        assert ds.attrs["CfgName"] == "ORCA"
        assert ds.attrs["NFtype"] == "T"
        assert ds.attrs["Iperio"] == 1
        ds.close()

    def test_output_compressed(self, tmp_path):
        from orca_grid import ORCAGridBuilder

        builder = ORCAGridBuilder("2deg")
        out_path = str(tmp_path / "test_grid.nc")
        builder.generate_and_write(out_path)

        import os
        size = os.path.getsize(out_path)
        # Compressed file should be < 5 MB for a 148x180 grid
        assert size < 5 * 1024 * 1024, f"File too large: {size / 1024:.0f} KB"
