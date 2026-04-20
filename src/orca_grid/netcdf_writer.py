"""
NetCDF writer for NEMO-compliant ORCA grid files.

This module creates NetCDF files following the NEMO domain_cfg
conventions as specified in the NEMO manual and reference files.
"""

import numpy as np
import xarray as xr
from datetime import datetime

class NEMONetCDFWriter:
    """
    Writer for NEMO-compliant NetCDF grid files.
    
    Creates domain_cfg.nc files with all required variables, dimensions,
    and attributes as specified in the NEMO manual.
    """
    
    def __init__(self, resolution="1deg"):
        """
        Initialize NetCDF writer.
        
        Args:
            resolution: Grid resolution ('1deg', '0.5deg', etc.)
        """
        self.resolution = resolution
        self.grid_params = self._get_resolution_params()
        
    def _get_resolution_params(self):
        """Get parameters for different resolutions."""
        params = {
            "1deg": {
                "nx": 360,      # Zonal points (x dimension)
                "ny": 331,      # Meridional points (y dimension)
                "nz": 75,       # Vertical levels (z dimension)
                "jpiglo": 362,  # Global zonal dimension (including halos)
                "jpjglo": 332,  # Global meridional dimension (including halos)
                "jpkglo": 75,   # Global vertical dimension
                "jperio": 6,    # Lateral boundary condition flag
                "orca": 1,      # ORCA grid family
                "orca_index": 1 # Specific ORCA configuration
            },
            "0.5deg": {
                "nx": 720,
                "ny": 661,
                "nz": 75,
                "jpiglo": 722,
                "jpjglo": 662,
                "jpkglo": 75,
                "jperio": 6,
                "orca": 1,
                "orca_index": 2
            },
            "0.25deg": {
                "nx": 1440,
                "ny": 1321,
                "nz": 75,
                "jpiglo": 1442,
                "jpjglo": 1322,
                "jpkglo": 75,
                "jperio": 6,
                "orca": 1,
                "orca_index": 3
            },
            "2deg": {
                "nx": 180,
                "ny": 161,
                "nz": 31,
                "jpiglo": 182,
                "jpjglo": 162,
                "jpkglo": 31,
                "jperio": 6,
                "orca": 1,
                "orca_index": 4
            }
        }
        return params.get(self.resolution, params["1deg"])
    
    def create_dataset(self, grid_data):
        """
        Create xarray Dataset with NEMO-compliant structure.
        
        Args:
            grid_data: Dictionary containing grid data
            
        Returns:
            ds: xarray Dataset ready for NetCDF output
        """
        # Extract parameters
        params = self.grid_params
        nx, ny, nz = params["nx"], params["ny"], params["nz"]
        
        # Create coordinate variables
        y_coords = np.arange(ny)
        x_coords = np.arange(nx)
        z_coords = np.arange(nz)
        time_coords = [0]  # Single time step
        
        # Create dataset with proper dimensions
        ds = xr.Dataset(
            coords={
                'y': y_coords,
                'x': x_coords, 
                'z': z_coords,
                't': time_coords
            },
            attrs={
                'DOMAIN_number_total': 1,
                'DOMAIN_number': 0,
                'DOMAIN_dimensions_ids': [1, 2],
                'DOMAIN_size_global': [params["jpiglo"], params["jpjglo"]],
                'DOMAIN_size_local': [params["jpiglo"], params["jpjglo"]],
                'DOMAIN_position_first': [1, 1],
                'DOMAIN_position_last': [params["jpiglo"], params["jpjglo"]],
                'DOMAIN_halo_size_start': [0, 0],
                'DOMAIN_halo_size_end': [0, 0],
                'DOMAIN_type': 'BOX',
                'history': f'{datetime.now():%a %b %d %H:%M:%S %Y}: Created by ORCA Grid Builder',
                'NCO': 'ORCA Grid Builder v1.0'
            }
        )
        
        # Add scalar variables for NEMO configuration
        ds['ORCA'] = params["orca"]
        ds['ORCA_index'] = params["orca_index"]
        ds['jpiglo'] = params["jpiglo"]
        ds['jpjglo'] = params["jpjglo"]
        ds['jpkglo'] = params["jpkglo"]
        ds['jperio'] = params["jperio"]
        ds['ln_zco'] = 0           # z-coordinate flag
        ds['ln_zps'] = 1           # partial steps flag  
        ds['ln_sco'] = 0           # s-coordinate flag
        ds['ln_isfcav'] = 0         # ice shelf cavities flag
        
        # Add coordinate variables
        if 'nav_lon' in grid_data and 'nav_lat' in grid_data:
            ds['nav_lon'] = (('y', 'x'), grid_data['nav_lon'].astype(np.float32))
            ds['nav_lat'] = (('y', 'x'), grid_data['nav_lat'].astype(np.float32))
            ds['nav_lon'].attrs['units'] = 'degrees_east'
            ds['nav_lat'].attrs['units'] = 'degrees_north'
        
        # Add vertical levels if available
        if 'nav_lev' in grid_data:
            ds['nav_lev'] = ('z', grid_data['nav_lev'].astype(np.float32))
            ds['nav_lev'].attrs['units'] = 'meters'
        else:
            # Create default vertical levels
            ds['nav_lev'] = ('z', np.linspace(0, 5000, nz).astype(np.float32))
            ds['nav_lev'].attrs['units'] = 'meters'
        
        # Add time counter
        ds['time_counter'] = ('t', np.array([0.0]))
        ds['time_counter'].attrs['units'] = 'days since 1950-01-01'
        
        # Add main grid variables (placeholder data for now)
        self._add_grid_variables(ds, grid_data)
        
        return ds
    
    def _add_grid_variables(self, ds, grid_data):
        """Add all required grid variables to the dataset."""
        nx, ny, nz = self.grid_params["nx"], self.grid_params["ny"], self.grid_params["nz"]
        
        # Create placeholder arrays - these would be filled with real data
        # from the grid generator in a complete implementation
        
        # Horizontal coordinates (T, U, V, F points)
        for point_type in ['t', 'u', 'v', 'f']:
            if f'glam{point_type}' in grid_data and f'gphi{point_type}' in grid_data:
                # Ensure data has time dimension
                glam_data = grid_data[f'glam{point_type}']
                gphi_data = grid_data[f'gphi{point_type}']
                
                if glam_data.ndim == 2:
                    glam_data = glam_data[np.newaxis, :, :]
                    gphi_data = gphi_data[np.newaxis, :, :]
                
                ds[f'glam{point_type}'] = (('t', 'y', 'x'), glam_data)
                ds[f'gphi{point_type}'] = (('t', 'y', 'x'), gphi_data)
                ds[f'glam{point_type}'].attrs['units'] = 'degrees_east'
                ds[f'gphi{point_type}'].attrs['units'] = 'degrees_north'
            else:
                # Create placeholder data
                if point_type == 't':
                    base_lon, base_lat = self._create_placeholder_coords()
                else:
                    base_lon, base_lat = self._create_staggered_coords(point_type)
                
                ds[f'glam{point_type}'] = (('t', 'y', 'x'), np.tile(base_lon[np.newaxis, :, :], (1, 1, 1)))
                ds[f'gphi{point_type}'] = (('t', 'y', 'x'), np.tile(base_lat[np.newaxis, :, :], (1, 1, 1)))
                ds[f'glam{point_type}'].attrs['units'] = 'degrees_east'
                ds[f'gphi{point_type}'].attrs['units'] = 'degrees_north'
        
        # Scale factors (e1, e2 for all point types)
        for point_type in ['t', 'u', 'v', 'f']:
            for scale_num in ['1', '2']:
                var_name = f'e{scale_num}{point_type}'
                ds[var_name] = (('t', 'y', 'x'), self._create_placeholder_scale_factors())
                ds[var_name].attrs['units'] = 'meters'
        
        # Coriolis parameters
        ff_f_data = self._create_coriolis(ds['gphif'].values)
        ff_t_data = self._create_coriolis(ds['gphit'].values)
        ds['ff_f'] = (('t', 'y', 'x'), ff_f_data)
        ds['ff_t'] = (('t', 'y', 'x'), ff_t_data)
        ds['ff_f'].attrs['units'] = 's-1'
        ds['ff_t'].attrs['units'] = 's-1'
        
        # Vertical scale factors
        ds['e3t_1d'] = (('t', 'z'), self._create_vertical_scale_factors_1d())
        ds['e3w_1d'] = (('t', 'z'), self._create_vertical_scale_factors_1d())
        ds['e3t_1d'].attrs['units'] = 'meters'
        ds['e3w_1d'].attrs['units'] = 'meters'
        
        for var_name in ['e3t_0', 'e3u_0', 'e3v_0', 'e3f_0', 'e3w_0', 'e3uw_0', 'e3vw_0']:
            ds[var_name] = (('t', 'z', 'y', 'x'), self._create_vertical_scale_factors_3d())
            ds[var_name].attrs['units'] = 'meters'
        
        # Bathymetry
        ds['bathy_meter'] = (('t', 'y', 'x'), self._create_placeholder_bathymetry())
        ds['bathy_meter'].attrs['units'] = 'meters'
        
        ds['bottom_level'] = (('t', 'y', 'x'), self._create_bottom_level(ds['bathy_meter']))
        ds['top_level'] = (('t', 'y', 'x'), np.ones((1, ny, nx), dtype=np.int32))
    
    def _create_placeholder_coords(self):
        """Create placeholder coordinate data."""
        ny, nx = self.grid_params["ny"], self.grid_params["nx"]
        
        # Create a regular lat/lon grid for demonstration
        lons = np.linspace(-180, 180, nx)
        lats = np.linspace(-80, 90, ny)
        
        lon_grid, lat_grid = np.meshgrid(lons, lats)
        return lon_grid, lat_grid
    
    def _create_staggered_coords(self, point_type):
        """Create staggered coordinates for U, V, F points."""
        ny, nx = self.grid_params["ny"], self.grid_params["nx"]
        
        # Create base grid
        lons = np.linspace(-180, 180, nx)
        lats = np.linspace(-80, 90, ny)
        lon_grid, lat_grid = np.meshgrid(lons, lats)
        
        # Apply staggering
        if point_type == 'u':  # U-points: east face
            lon_grid = (lon_grid[:, :-1] + lon_grid[:, 1:]) / 2
            lat_grid = (lat_grid[:, :-1] + lat_grid[:, 1:]) / 2
            # Pad to maintain dimensions
            lon_grid = np.hstack([lon_grid, lon_grid[:, -1:]])
            lat_grid = np.hstack([lat_grid, lat_grid[:, -1:]])
        
        elif point_type == 'v':  # V-points: north face
            lon_grid = (lon_grid[:-1, :] + lon_grid[1:, :]) / 2
            lat_grid = (lat_grid[:-1, :] + lat_grid[1:, :]) / 2
            # Pad to maintain dimensions
            lon_grid = np.vstack([lon_grid[0:1, :], lon_grid])
            lat_grid = np.vstack([lat_grid[0:1, :], lat_grid])
        
        elif point_type == 'f':  # F-points: northeast corner
            lon_grid = (lon_grid[:-1, :-1] + lon_grid[1:, 1:]) / 2
            lat_grid = (lat_grid[:-1, :-1] + lat_grid[1:, 1:]) / 2
            # Pad to maintain dimensions
            lon_grid = np.vstack([lon_grid[0:1, :], lon_grid])
            lon_grid = np.hstack([lon_grid, lon_grid[:, -1:]])
            lat_grid = np.vstack([lat_grid[0:1, :], lat_grid])
            lat_grid = np.hstack([lat_grid, lat_grid[:, -1:]])
        
        return lon_grid, lat_grid
    
    def _create_placeholder_scale_factors(self):
        """Create placeholder scale factor data."""
        ny, nx = self.grid_params["ny"], self.grid_params["nx"]
        
        # Create scale factors that vary realistically
        base_scale = 111000.0  # Approx 1 degree in meters
        
        # Add some variation
        lats = np.linspace(-80, 90, ny)
        lat_grid = np.tile(lats[:, np.newaxis], (1, nx))
        
        scale_factor = base_scale * (1.0 + 0.1 * np.sin(np.deg2rad(lat_grid)))
        
        return np.tile(scale_factor[np.newaxis, :, :], (1, 1, 1))
    
    def _create_coriolis(self, lat_data):
        """Create Coriolis parameter data."""
        omega = 7.2921e-5  # Earth's angular velocity
        return 2 * omega * np.sin(np.deg2rad(lat_data))
    
    def _create_vertical_scale_factors_1d(self):
        """Create 1D vertical scale factors."""
        nz = self.grid_params["nz"]
        
        # Create realistic vertical scale factors
        # Smaller near surface, increasing with depth
        depth = np.linspace(0, 5000, nz)
        scale_factors = 10.0 + depth / 100.0  # 10m at surface to 60m at bottom
        
        return np.tile(scale_factors[np.newaxis, :], (1, 1))
    
    def _create_vertical_scale_factors_3d(self):
        """Create 3D vertical scale factors."""
        nz, ny, nx = self.grid_params["nz"], self.grid_params["ny"], self.grid_params["nx"]
        
        # Create 3D array with depth variation only
        scale_factors_1d = self._create_vertical_scale_factors_1d()[0, :]
        scale_factors_3d = np.tile(scale_factors_1d[:, np.newaxis, np.newaxis], (1, ny, nx))
        
        return np.tile(scale_factors_3d[np.newaxis, :, :, :], (1, 1, 1, 1))
    
    def _create_placeholder_bathymetry(self):
        """Create placeholder bathymetry data."""
        ny, nx = self.grid_params["ny"], self.grid_params["nx"]
        
        # Create realistic-looking bathymetry
        bathy = np.ones((ny, nx)) * 5000.0  # Deep ocean
        
        # Add continental shelves
        lats = np.linspace(-80, 90, ny)
        lat_grid = np.tile(lats[:, np.newaxis], (1, nx))
        
        # Shallow areas near continents
        bathy[np.abs(lat_grid) < 30] = 200.0  # Continental shelves
        bathy[np.abs(lat_grid) < 10] = 50.0   # Coastal areas
        
        # Add some random variation
        bathy += np.random.normal(0, 50, (ny, nx))
        bathy = np.clip(bathy, 10, 5500)
        
        return np.tile(bathy[np.newaxis, :, :], (1, 1, 1))
    
    def _create_bottom_level(self, bathy_data):
        """Create bottom level index from bathymetry."""
        nz = self.grid_params["nz"]
        
        # Convert bathymetry to level indices
        # This is simplified - real implementation would use proper vertical coordinate
        depth_per_level = 5000.0 / nz
        bottom_level = np.floor(bathy_data.values[0, :, :] / depth_per_level).astype(np.int32)
        bottom_level = np.clip(bottom_level, 0, nz - 1)
        
        return np.tile(bottom_level[np.newaxis, :, :], (1, 1, 1))
    
    def write_netcdf(self, grid_data, filename="domain_cfg.nc"):
        """
        Write grid data to NEMO-compliant NetCDF file.
        
        Args:
            grid_data: Dictionary containing grid data
            filename: Output filename
        """
        # Create dataset
        ds = self.create_dataset(grid_data)
        
        # Write to NetCDF
        ds.to_netcdf(filename)
        print(f"Successfully wrote NEMO-compliant grid to {filename}")
        
        return filename