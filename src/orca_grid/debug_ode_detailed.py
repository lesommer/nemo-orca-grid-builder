#!/usr/bin/env python3
"""
Detailed ODE debugging to understand constant solutions.
"""

import numpy as np
from scipy.integrate import solve_ivp

# Create simple test case
x = np.linspace(0, 10, 100)
y = x**2  # Simple quadratic function

print(f"Test function: y = x^2")
print(f"x: {x[0]:.2f} to {x[-1]:.2f}")
print(f"y: {y[0]:.2f} to {y[-1]:.2f}")

# Calculate derivatives
dy_dx = np.gradient(y, x)
dx_dy = np.gradient(x, y)

print(f"\nDerivatives:")
print(f"dy_dx: {dy_dx[0]:.2f} to {dy_dx[-1]:.2f}")
print(f"dx_dy: {dx_dy[0]:.2f} to {dx_dy[-1]:.2f}")

# ODE function: dy/dx = -y'/x'
def ode_func(x_val, y_val):
    idx = np.argmin(np.abs(x - x_val))
    y_prime = dy_dx[idx]
    x_prime = dx_dy[idx]
    
    print(f"At x={x_val:.2f}, idx={idx}, y_prime={y_prime:.2f}, x_prime={x_prime:.2f}")
    
    if np.abs(x_prime) < 1e-10:
        result = 0.0
        print(f"Division by zero avoided, returning 0")
    else:
        result = -y_prime / x_prime
        print(f"Result: {result:.2f}")
    
    return result

# Solve ODE
print(f"\nSolving ODE:")
solution = solve_ivp(
    ode_func,
    [x[0], x[-1]],
    [y[0]],
    method='RK45',
    rtol=1e-6,
    atol=1e-8,
    dense_output=True
)

print(f"\nSolution:")
print(f"Success: {solution.success}")
print(f"Message: {solution.message}")

if solution.success:
    x_sol = np.linspace(x[0], x[-1], 5)
    y_sol = solution.sol(x_sol)[0]
    print(f"y({x_sol[0]:.2f}) = {y_sol[0]:.2f}")
    print(f"y({x_sol[-1]:.2f}) = {y_sol[-1]:.2f}")
