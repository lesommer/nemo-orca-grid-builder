# NEMO ORCA Grid Builder - Detailed Technical Specification

## 1. Overview
This document provides the detailed technical specifications for implementing a NEMO ORCA grid builder based on the research from the NEMO manual and Madec & Imbard (1996) paper.

## 2. ORCA Grid Mathematical Foundation

### 2.1 Grid Construction Method (Madec & Imbard, 1996)

The ORCA grid uses a semi-analytical method to create a global orthogonal curvilinear mesh that avoids the North Pole singularity by moving mesh poles to land points.

**Key Mathematical Concepts:**

1. **Stereographic Polar Projection**: The grid is constructed in a north stereographic polar plane, then projected onto the sphere
2. **Embedded Circles**: Mesh parallels (J-curves) are defined as a series of embedded circles
3. **Orthogonal Meridians**: Mesh meridians (I-curves) are computed as curves that intercept each circle at right angles

**Grid Equations:**
- J-curves (parallels): `L(j): x² + (y - P(f(j) + g(j)))² = (f(j) + g(j))²`
- Where f(j) and g(j) are analytical functions controlling resolution and anisotropy

### 2.2 NEMO Grid Point Locations (Table 3.1)

The NEMO model uses an Arakawa C-grid staggering:

- **T-point (tracer)**: Center of grid cell (i, j, k)
- **U-point (zonal velocity)**: East face of grid cell (i+1/2, j, k)  
- **V-point (meridional velocity)**: North face of grid cell (i, j+1/2, k)
- **F-point (vortex)**: Northeast corner of grid cell (i+1/2, j+1/2, k)

## 3. Required NetCDF File Structure

### 3.1 Dimensions
- `y`: 331 (meridional direction)
- `x`: 360 (zonal direction) 
- `z`: 75 (vertical levels)
- `t`: 1 (time dimension, currently unlimited)

### 3.2 Global Attributes
- `ORCA`: 1 (grid family identifier)
- `ORCA_index`: 1 (specific ORCA configuration)
- `jpiglo`: 362 (global zonal dimension including halos)
- `jpjglo`: 332 (global meridional dimension including halos)
- `jpkglo`: 75 (global vertical dimension)
- `jperio`: 6 (lateral boundary condition flag)
- `ln_zco`: 0 (z-coordinate flag)
- `ln_zps`: 1 (partial steps flag)
- `ln_sco`: 0 (s-coordinate flag)
- `ln_isfcav`: 0 (ice shelf cavities flag)

### 3.3 Required Variables

#### Coordinate Variables
- `nav_lon(y, x)`: Longitude at T-points (°E)
- `nav_lat(y, x)`: Latitude at T-points (°N)  
- `nav_lev(z)`: Vertical level depths (m)

#### Horizontal Grid Variables
- `glamt(t, y, x)`: Longitude at T-points (°E)
- `glamu(t, y, x)`: Longitude at U-points (°E)
- `glamv(t, y, x)`: Longitude at V-points (°E)
- `glamf(t, y, x)`: Longitude at F-points (°E)
- `gphit(t, y, x)`: Latitude at T-points (°N)
- `gphiu(t, y, x)`: Latitude at U-points (°N)
- `gphiv(t, y, x)`: Latitude at V-points (°N)
- `gphif(t, y, x)`: Latitude at F-points (°N)

#### Scale Factors
- `e1t(t, y, x)`: Zonal scale factor at T-points (m)
- `e1u(t, y, x)`: Zonal scale factor at U-points (m)
- `e1v(t, y, x)`: Zonal scale factor at V-points (m)
- `e1f(t, y, x)`: Zonal scale factor at F-points (m)
- `e2t(t, y, x)`: Meridional scale factor at T-points (m)
- `e2u(t, y, x)`: Meridional scale factor at U-points (m)
- `e2v(t, y, x)`: Meridional scale factor at V-points (m)
- `e2f(t, y, x)`: Meridional scale factor at F-points (m)

#### Vertical Scale Factors
- `e3t_1d(t, z)`: Vertical scale factor at T-points (1D, m)
- `e3w_1d(t, z)`: Vertical scale factor at W-points (1D, m)
- `e3t_0(t, z, y, x)`: Vertical scale factor at T-points (3D, m)
- `e3u_0(t, z, y, x)`: Vertical scale factor at U-points (3D, m)
- `e3v_0(t, z, y, x)`: Vertical scale factor at V-points (3D, m)
- `e3f_0(t, z, y, x)`: Vertical scale factor at F-points (3D, m)
- `e3w_0(t, z, y, x)`: Vertical scale factor at W-points (3D, m)
- `e3uw_0(t, z, y, x)`: Vertical scale factor at UW-points (3D, m)
- `e3vw_0(t, z, y, x)`: Vertical scale factor at VW-points (3D, m)

#### Coriolis Parameters
- `ff_f(t, y, x)`: Coriolis parameter at F-points (s⁻¹)
- `ff_t(t, y, x)`: Coriolis parameter at T-points (s⁻¹)

#### Bathymetry
- `bathy_meter(t, y, x)`: Bathymetry depth (m)
- `bottom_level(t, y, x)`: Index of bottom level
- `top_level(t, y, x)`: Index of top level

## 4. ORCA Grid Characteristics (1° Resolution)

### 4.1 Horizontal Grid
- **Resolution**: 1° × 1° nominal resolution
- **Grid Type**: Tripolar orthogonal curvilinear
- **North Pole Treatment**: Two mesh poles placed on land (Canada and Russia)
- **Equator Handling**: Equator is a mesh line for better equatorial dynamics
- **Domain Size**: 362 × 332 global grid points (including halos)
- **Active Domain**: 360 × 331 points (excluding halos)

### 4.2 Vertical Grid
- **Levels**: 75 vertical levels
- **Coordinate System**: z-coordinate with partial steps (ln_zps=1)
- **Surface Resolution**: High resolution in upper ocean (10m near surface)
- **Bottom Topography**: Based on Smith & Sandwell (1997) atlas

### 4.3 Special Features
- **North Fold Boundary**: Special treatment for tripolar grid north fold
- **Bering Strait**: Open without special treatment due to grid continuity
- **Partial Cells**: Partial bottom cells for better bathymetry representation
- **Anisotropy Control**: Maintains low ratio of anisotropy (e1/e2 ≈ 1)

## 5. Implementation Requirements

### 5.1 Core Algorithms
1. **Stereographic Projection**: Implement forward and inverse transformations
2. **Embedded Circle Generation**: Create series of circles for J-curves
3. **Orthogonal Meridian Calculation**: Numerical solution for I-curves
4. **Sphere Projection**: Convert polar plane coordinates to spherical coordinates
5. **Scale Factor Computation**: Calculate e1, e2, e3 scale factors
6. **Staggered Grid Generation**: Create T, U, V, F point locations
7. **Coriolis Parameter**: Compute f-plane or beta-plane approximation

### 5.2 Numerical Methods
1. **Grid Generation**: Use numerical ODE solver for meridian curves
2. **Interpolation**: High-order interpolation for staggered points
3. **Bathymetry Processing**: Partial cell calculations
4. **Vertical Coordinate**: Z-coordinate with partial steps implementation

### 5.3 Software Architecture
1. **Modular Design**: Separate grid generation from file I/O
2. **JAX Integration**: Use JAX for numerical computations (GPU/CPU)
3. **NetCDF Interface**: Use netCDF4 or xarray for file operations
4. **Validation Module**: Compare with reference domain_cfg.nc
5. **Resolution Control**: Parameterized resolution selection

## 6. Validation Criteria

### 6.1 Numerical Accuracy
- Coordinate values should match reference file within 1e-6 tolerance
- Scale factors should match within 1e-4 relative error
- Grid orthogonality should be maintained (dot product of tangents < 1e-8)

### 6.2 Physical Consistency
- Scale factors must be positive everywhere
- Grid should cover global ocean without gaps
- North fold should be continuous and differentiable
- Bathymetry should be physically reasonable

### 6.3 File Compliance
- NetCDF file must be CF-compliant
- All required variables and attributes must be present
- Variable dimensions must match NEMO expectations
- Data types must match reference file

## 7. Implementation Roadmap

### Phase 1: Core Grid Generation
1. Implement stereographic projection functions
2. Create embedded circle generator for J-curves
3. Implement numerical ODE solver for I-curves
4. Add sphere projection and coordinate conversion
5. Generate base 1° resolution grid

### Phase 2: Scale Factors and Metrics
1. Implement scale factor calculations (e1, e2, e3)
2. Add Coriolis parameter computation
3. Implement bathymetry processing
4. Add vertical coordinate system

### Phase 3: NetCDF Output
1. Create NetCDF writer module
2. Implement NEMO-compliant file structure
3. Add all required variables and attributes
4. Implement proper dimension handling

### Phase 4: Validation
1. Create comparison tool against reference file
2. Implement numerical validation tests
3. Add grid quality metrics
4. Test orthogonality and continuity

### Phase 5: Optimization
1. Add JAX acceleration for key computations
2. Implement GPU/CPU detection
3. Optimize memory usage
4. Add resolution parameterization

## 8. References

### Key Equations from Madec & Imbard (1996)

**J-curve equation (embedded circles):**
```
L(j): x² + (y - P(f(j) + g(j)))² = (f(j) + g(j))²
```

**I-curve differential equation:**
```
dx/ds = -y' / x', dy/ds = x' / y'
```

Where (x', y') are derivatives of the J-curve equation.

### NEMO Manual References
- Section 3.1.3: Grid point location table
- Section 17.4: ORCA family configurations  
- Appendix F: DOMAINcfg tool specifications
- Table 17.1: Domain sizes for ORCA configurations

## 9. Implementation Notes

1. **Precision**: Use double precision (float64) for all calculations
2. **Numerical Stability**: Handle polar regions carefully to avoid singularities
3. **Performance**: Vectorize operations where possible
4. **Modularity**: Design for easy extension to other resolutions
5. **Documentation**: Include mathematical derivations in code comments

This specification provides the complete technical foundation for implementing the NEMO ORCA grid builder as outlined in the development plan.