# Algorithm Extraction from Madec-Imbard (1996)

## Key Equations

### Equation (1): Mesh Parallels (J-curves)
The mesh parallels are defined as embedded circles in the stereographic polar plane:

L(j): x² + (y - P(f(j) + g(j)))² = (f(j) + g(j))²

Where:
- f(j) controls circle size
- g(j) controls center movement
- P is a projection parameter

### Equation (2): Mesh Meridians (I-curves)
The mesh meridians are solutions to the differential equation:

dy/dx = -y' / x'

Where y' and x' are derivatives of the J-curve equation.

## Algorithm Steps

1. **Define Mesh Parallels (J-curves)**
   - Use analytical functions f(j) and g(j)
   - Create embedded circles in stereographic plane
   - Ensure properties (a)-(e) are satisfied

2. **Compute Mesh Meridians (I-curves)**
   - Solve differential equation numerically
   - Use high-precision numerical methods
   - Find orthogonal trajectories

3. **Project onto Sphere**
   - Use stereographic polar projection
   - Maintain conformal properties
   - Ensure continuity

## Key Parameters

- **Earth Radius**: R = 6371 km (standard)
- **Projection**: Stereographic polar projection
- **Resolution Control**: Functions f(j), g(j)
- **Pole Treatment**: Moved to land points

## Implementation Requirements

1. **Numerical Solution**
   - Solve Eq. (2) for I-curves
   - High-precision required
   - Bisection method for index finding

2. **Grid Generation**
   - Generate J-curves analytically
   - Compute I-curves numerically
   - Project to spherical coordinates

3. **Validation**
   - Check orthogonality
   - Verify continuity
   - Validate scale factors

## Reference Implementation

The algorithm has been implemented in:
- LODYC general circulation ocean model
- Uses semi-analytical approach
- Maintains low anisotropy ratio
- Allows easy resolution control

## Next Steps

1. Implement Eq. (1) for J-curves
2. Solve Eq. (2) numerically for I-curves
3. Add stereographic projection
4. Validate against reference grid

**Status**: Algorithm extracted, ready for implementation 🎯
