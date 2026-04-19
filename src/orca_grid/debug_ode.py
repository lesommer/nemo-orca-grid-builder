#!/usr/bin/env python3
"""
Debug ODE solver to understand constant solutions.
"""

import numpy as np
from scipy.integrate import solve_ivp

# Test with simple J-curve
j_curve = np.array([
    [6371000.0, 0.0],
    [6370000.0, 1000.0],
    [6369000.0, 2000.0],
    [6368000.0, 3000.0],
    [6367000.0, 4000.0]
])

x_j = j_curve[:, 0]
y_j = j_curve[:, 1]

print(f"Test J-curve:")
print(f"x: {x_j}")
print(f"y: {y_j}")

# Calculate derivatives
dy_dx = np.gradient(y_j, x_j)
dx_dy = np.gradient(x_j, y_j)

print(f"\nDerivatives:")
print(f"dy_dx: {dy_dx}")
print(f"dx_dy: {dx_dy}")

# ODE function
def ode_func(x, y):
    idx = np.argmin(np.abs(x_j - x))
    y_prime = dy_dx[idx]
    x_prime = dx_dy[idx]
    
    print(f"At x={x:.2f}, idx={idx}, y_prime={y_prime:.2e}, x_prime={x_prime:.2e}")
    
    if np.abs(x_prime) < 1e-10:
        result = 0.0
        print(f"Division by zero avoided, returning 0")
    else:
        result = -y_prime / x_prime
        print(f"Result: {result:.2e}")
    
    return result

# Test ODE function at different points
test_points = [x_j[0], x_j[2], x_j[-1]]
print(f"\nTesting ODE function:")
for x in test_points:
    result = ode_func(x, y_j[0])
    print(f"x={x:.2f} -> {result:.2e}")

# Try solving ODE
print(f"\nSolving ODE:")
try:
    solution = solve_ivp(
        ode_func,
        [x_j[0], x_j[-1]],
        [y_j[0]],
        method='RK45',
        rtol=1e-6,
        atol=1e-8,
        dense_output=True
    )
    
    print(f"Success: {solution.success}")
    print(f"Message: {solution.message}")
    
    if solution.success:
        x_sol = np.linspace(x_j[0], x_j[-1], 10)
        y_sol = solution.sol(x_sol)[0]
        print(f"Solution: y({x_sol[0]:.2f}) = {y_sol[0]:.2f}")
        print(f"         y({x_sol[-1]:.2f}) = {y_sol[-1]:.2f}")
except Exception as e:
    print(f"Error: {e}")
