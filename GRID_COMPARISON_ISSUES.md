# Grid Comparison Issues Analysis and Resolution Plan

## Current Situation

The comparison between generated grids and reference grids shows significant differences:

### Key Issues Identified:

1. **Coordinate Range Mismatch**
   - Generated: Limited latitude range (20.27° to 55.30°)
   - Reference: Full global range (-85.79° to 89.74°)
   - Issue: Generated grid covers only a subset of the globe

2. **Scale Factor Differences**
   - Generated: e1t/e2t range 100,068 - 122,100
   - Reference: e1t/e2t range 2.20 - 111,198
   - Issue: Scale factors differ by orders of magnitude

3. **Mean Value Differences**
   - Large differences in mean values across all variables
   - Issue: Fundamental discrepancy in grid generation

## Root Cause Analysis

### Likely Causes:

1. **Different Grid Generation Algorithms**
   - Current implementation may not follow Madec & Imbard (1996) exactly
   - Reference grid uses different parameters or method

2. **Resolution Mismatch**
   - Generated grid may have different resolution than reference
   - Grid parameters (nx, ny) may differ

3. **Coordinate System Differences**
   - Different projection or reference frame
   - Different pole treatment

4. **Implementation Issues**
   - Potential bugs in grid generation code
   - Incorrect scale factor calculations

## Resolution Plan

### Phase 1: Research and Documentation

1. **Obtain Madec & Imbard (1996) Paper**
   - [ ] Get PDF of original paper
   - [ ] Study algorithm details
   - [ ] Document key equations and parameters

2. **Analyze Reference Grid**
   - [ ] Examine data/domain_cfg.nc metadata
   - [ ] Document reference grid parameters
   - [ ] Understand reference grid generation method

3. **Document Current Implementation**
   - [ ] Review src/orca_grid/grid_generator.py
   - [ ] Document current algorithm
   - [ ] Identify deviations from reference

### Phase 2: Diagnostic Tests

1. **Create Minimal Test Cases**
   - [ ] Generate simple test grids
   - [ ] Compare with known good outputs
   - [ ] Isolate specific issues

2. **Add Detailed Logging**
   - [ ] Instrument grid generation code
   - [ ] Log key intermediate values
   - [ ] Identify where divergence occurs

3. **Visual Inspection**
   - [ ] Plot generated vs reference grids
   - [ ] Visualize differences
   - [ ] Identify patterns in discrepancies

### Phase 3: Algorithm Verification

1. **Implement Reference Algorithm**
   - [ ] Create separate reference implementation
   - [ ] Follow Madec & Imbard (1996) exactly
   - [ ] Compare with current implementation

2. **Parameter Sensitivity Analysis**
   - [ ] Test different resolution parameters
   - [ ] Vary grid generation parameters
   - [ ] Identify optimal settings

3. **Scale Factor Verification**
   - [ ] Verify scale factor calculations
   - [ ] Check units and magnitudes
   - [ ] Validate against analytical solutions

### Phase 4: Code Modifications

1. **Fix Coordinate Generation**
   - [ ] Ensure full global coverage
   - [ ] Correct latitude/longitude ranges
   - [ ] Validate pole treatment

2. **Correct Scale Factors**
   - [ ] Review scale factor calculations
   - [ ] Ensure proper units (meters)
   - [ ] Validate against reference values

3. **Match Reference Parameters**
   - [ ] Align resolution settings
   - [ ] Use identical grid parameters
   - [ ] Ensure consistent projections

### Phase 5: Validation and Testing

1. **Create Comprehensive Test Suite**
   - [ ] Unit tests for individual components
   - [ ] Integration tests for full pipeline
   - [ ] Regression tests against reference

2. **Automated Validation**
   - [ ] Statistical comparison metrics
   - [ ] Visual difference maps
   - [ ] Quantitative error measures

3. **Performance Benchmarking**
   - [ ] Measure generation speed
   - [ ] Compare with reference implementation
   - [ ] Optimize if needed

## Expected Outcomes

### Success Criteria:

1. **Coordinate Match**
   - Generated grid covers same global extent as reference
   - Latitude/longitude ranges match
   - Pole treatment is consistent

2. **Scale Factor Consistency**
   - Magnitudes match reference values
   - Units are correct (meters)
   - Spatial patterns are similar

3. **Statistical Agreement**
   - Mean differences < 1%
   - Max differences < 5%
   - Spatial correlation > 0.99

## Implementation Strategy

### Recommended Approach:

1. **Incremental Fixes**
   - Address one issue at a time
   - Test after each change
   - Document progress

2. **Reference Implementation**
   - Create parallel implementation
   - Compare step-by-step
   - Identify exact divergence points

3. **Comprehensive Testing**
   - Test at multiple resolutions
   - Validate against multiple references
   - Ensure robustness

## Resources Needed

### Documentation:
- Madec & Imbard (1996) paper
- NEMO documentation
- ORCA grid specifications

### Tools:
- Python testing frameworks
- Visualization tools
- Statistical analysis libraries

### Time Estimate:
- Research: 2-4 hours
- Diagnosis: 4-8 hours
- Implementation: 8-16 hours
- Testing: 4-8 hours

## Next Steps

1. **Gather Documentation**
   - Obtain Madec & Imbard (1996) paper
   - Review NEMO ORCA specifications

2. **Create Diagnostic Tests**
   - Isolate specific issues
   - Develop minimal test cases

3. **Implement Fixes**
   - Address coordinate generation first
   - Then fix scale factors
   - Finally match all parameters

## Notes

- Current implementation generates valid grids
- Differences are quantitative, not qualitative
- Reference grid may use different parameters
- Step-by-step approach recommended
