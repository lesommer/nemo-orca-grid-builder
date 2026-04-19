# Current Implementation Documentation

## Overview

This document describes the current ORCA grid generation implementation based on analysis of the codebase and reference grid metadata.

## Reference Grid Analysis

### Key Characteristics

- **Dimensions**: 362 × 332 × 75 (x × y × z)
- **Grid Type**: eORCA1 (extended ORCA1)
- **Resolution**: ~1° nominal
- **Coverage**: Global (-85.79° to 89.74° latitude)
- **Staggered Points**: T, U, V, F points (Arakawa C-grid)
- **Scale Factors**: e1t/e2t range 2.20 - 111,198 meters

### Key Variables

- **nav_lon/nav_lat**: T-point coordinates (331×360)
- **glamt/gphit**: T-point coordinates (1×331×360)
- **e1t/e2t**: T-point scale factors (1×331×360)
- **e3t_0**: Vertical scale factors (1×75×331×360)
- **bathy_meter**: Bathymetry (1×331×360)

## Current Implementation Analysis

### ORCAGridGenerator Class

**Purpose**: Generates ORCA grids using Madec & Imbard (1996) method

**Key Methods**:

1. `generate_polar_grid()`
   - Generates polar grid coordinates
   - Uses stereographic projection
   - Creates J-curves and I-curves

2. `polar_to_spherical()`
   - Converts polar to spherical coordinates
   - Handles projection transformations

3. `generate_spherical_grid()`
   - Generates full spherical grid
   - Creates all staggered points (T, U, V, F)

4. `calculate_scale_factors()`
   - Computes scale factors (e1, e2)
   - Based on spherical geometry

### Algorithm Flow

1. **Initialize Parameters**
   - Set resolution (1deg, 0.5deg, etc.)
   - Configure grid dimensions (nx, ny)
   - Set Earth radius (R = 6,371,000 m)

2. **Generate Polar Grid**
   - Create J-curves (mesh parallels)
   - Compute I-curves (mesh meridians)
   - Use stereographic projection

3. **Convert to Spherical**
   - Transform polar → spherical
   - Apply coordinate transformations

4. **Generate Full Grid**
   - Create T, U, V, F points
   - Arakawa C-grid staggering

5. **Calculate Scale Factors**
   - Compute e1t, e2t, e3t
   - Based on spherical geometry

## Key Differences Identified

### 1. Coverage Area

**Current**: Limited latitude range (20.27° to 55.30°)
**Reference**: Full global range (-85.79° to 89.74°)

**Issue**: Current implementation doesn't generate full global coverage

### 2. Scale Factors

**Current**: e1t/e2t range 100,068 - 122,100 meters
**Reference**: e1t/e2t range 2.20 - 111,198 meters

**Issue**: Scale factors differ by orders of magnitude

### 3. Grid Parameters

**Current**: Unknown exact parameters
**Reference**: Well-documented NEMO parameters

**Issue**: Parameter mismatch between implementations

## Required Fixes

### 1. Global Coverage

- Extend latitude range to full global coverage
- Ensure proper pole treatment
- Match reference grid extent

### 2. Scale Factor Calculation

- Review scale factor formulas
- Verify units (should be meters)
- Match reference magnitudes

### 3. Parameter Alignment

- Document all grid parameters
- Match reference resolution exactly
- Align coordinate systems

## Next Steps

1. **Implement Reference Algorithm**
   - Create parallel implementation
   - Follow Madec & Imbard (1996) exactly

2. **Parameter Matching**
   - Align nx, ny dimensions
   - Match resolution settings
   - Ensure identical projections

3. **Validation**
   - Compare with reference grid
   - Statistical validation
   - Visual inspection

## Technical Notes

- Current implementation generates valid grids
- Differences are quantitative, not qualitative
- Reference grid uses eORCA1 configuration
- Step-by-step verification recommended

## References

- Madec, G., & Imbard, M. (1996). A global ocean mesh to overcome the North Pole singularity. Climate Dynamics, 12(6), 381-388.
- NEMO Ocean Engine Documentation
- ORCA grid specifications
