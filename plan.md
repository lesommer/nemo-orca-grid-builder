# Development Plan for NEMO ORCA Grid Builder

## Overview
Create a Python module that generates global discretization grids for ocean models following the ORCA grid family conventions, specifically compatible with the NEMO ocean model. The module should be modular, support multiple resolutions (starting with 1°), and leverage JAX for GPU/CPU compatibility.

## Key Requirements
1. **Output Format**: Generate NetCDF files following NEMO conventions
2. **Grid Family**: ORCA grid family as described in Madec & Imbard (1996)
3. **Reference Implementation**: Match the structure of `data/domain_cfg.nc` for 1° resolution
4. **Modularity**: Design for reuse with other ocean models (e.g., Veros)
5. **Performance**: Use JAX for GPU/CPU compatibility

## Implementation Phases

### Phase 1: Research and Specification (Current Phase)
- [x] Review NEMO manual section 3 for naming conventions
- [x] Examine Madec-Imbard-1996.pdf for ORCA grid specifications
- [x] Analyze reference file `data/domain_cfg.nc` structure
- [x] Document all required NetCDF variables and attributes
- [ ] Create detailed specification document

### Phase 2: Core Grid Generation
- [ ] Implement ORCA grid coordinate system
- [ ] Create 1° resolution grid generator
- [ ] Implement coordinate transformations (glamt, gphit, etc.)
- [ ] Add scale factors (e1t, e2t, etc.) calculations
- [ ] Implement Coriolis parameter (ff_t, ff_f) calculations
- [ ] Add vertical coordinate system (nav_lev, e3* fields)

### Phase 3: NetCDF Output
- [ ] Create NetCDF writer module
- [ ] Implement NEMO-compliant file structure
- [ ] Add all required global attributes
- [ ] Add dimension variables (nav_lon, nav_lat, nav_lev)
- [ ] Add all grid variables with proper dimensions
- [ ] Implement time dimension handling

### Phase 4: Validation and Testing
- [ ] Create test suite comparing output to `data/domain_cfg.nc`
- [ ] Implement numerical validation for grid properties
- [ ] Add unit tests for individual components
- [ ] Create integration test for full grid generation

### Phase 5: Modularization and Extensibility
- [ ] Design abstract base classes for grid generation
- [ ] Create NEMO-specific implementation
- [ ] Design adapter pattern for other ocean models
- [ ] Add Veros compatibility layer
- [ ] Document extension points for new models

### Phase 6: Performance Optimization
- [ ] Implement JAX-based computations
- [ ] Add GPU/CPU detection and optimization
- [ ] Optimize memory usage for large grids
- [ ] Add batching support for high-resolution grids

### Phase 7: Documentation and Examples
- [ ] Write comprehensive API documentation
- [ ] Create usage examples for different resolutions
- [ ] Add Jupyter notebook tutorials
- [ ] Document extension for new ocean models

## Technical Specifications

### Required NetCDF Variables (from domain_cfg.nc)
- **Dimensions**: y=331, x=360, z=75, t=1
- **Coordinate variables**: nav_lon, nav_lat, nav_lev
- **Grid variables**: glamt, glamu, glamv, glamf, gphit, gphiu, gphiv, gphif
- **Scale factors**: e1t, e1u, e1v, e1f, e2t, e2u, e2v, e2f
- **Vertical scale factors**: e3t_1d, e3w_1d, e3t_0, e3u_0, e3v_0, e3f_0, e3w_0, e3uw_0, e3vw_0
- **Coriolis parameters**: ff_f, ff_t
- **Bathymetry**: bathy_meter, bottom_level, top_level
- **Global attributes**: ORCA, ORCA_index, jpiglo, jpjglo, jpkglo, jperio, ln_zco, ln_zps, ln_sco, ln_isfcav

### ORCA Grid Characteristics (1° resolution)
- Horizontal resolution: 1° × 1°
- Grid type: Tripolar ORCA grid
- North pole treatment: Displaced to avoid singularity
- Vertical levels: 75 standard levels
- Domain: Global ocean with partial cells

## Implementation Approach

1. **Modular Design**: Separate coordinate generation, NetCDF writing, and model-specific adaptations
2. **JAX Integration**: Use JAX for numerical computations to enable GPU acceleration
3. **Validation Framework**: Compare generated grids with reference file using numerical metrics
4. **Extensible Architecture**: Abstract interfaces for supporting multiple ocean models

## Deliverables
1. Python module with core grid generation functionality
2. NetCDF writer compliant with NEMO conventions
3. Validation suite comparing against reference data
4. Documentation for usage and extension
5. Example scripts for generating different resolutions

## Timeline Estimate
- Phase 1 (Research): 1-2 days
- Phase 2 (Core Generation): 3-5 days
- Phase 3 (NetCDF Output): 2-3 days  
- Phase 4 (Validation): 2 days
- Phase 5 (Modularization): 2-3 days
- Phase 6 (Optimization): 1-2 days
- Phase 7 (Documentation): 1-2 days

Total: ~2-3 weeks for full implementation

## Next Steps
1. Finalize detailed specifications from NEMO manual and Madec-Imbard paper
2. Create mathematical formulation for ORCA grid generation
3. Begin implementation with 1° resolution prototype
4. Implement validation against reference NetCDF file