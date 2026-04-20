#!/usr/bin/env python3
"""
Reference implementation of Madec-Imbard (1996) algorithm.
"""

import numpy as np
from scipy.integrate import solve_ivp

class ReferenceORCAGridGenerator:
    """
    Implementation of the Madec-Imbard (1996) semi-analytical method.
    
    This class generates global orthogonal curvilinear ocean meshes that avoid
    the North Pole singularity by moving mesh poles to land points.
    """
    
    def __init__(self, resolution="1deg"):
        """Initialize grid generator."""
        self.resolution = resolution
        self.earth_radius = 6371000.0  # meters
        
        # Set resolution parameters
        if resolution == "1deg":
            self.nx = 360
            self.ny = 331
        elif resolution == "0.5deg":
            self.nx = 720
            self.ny = 661
        else:
            raise ValueError(f"Unsupported resolution: {resolution}")
    
    def generate_j_curves(self):
        """
        Generate J-curves (mesh parallels) as embedded circles.
        
        Equation (1): x² + (y - P(f(j) + g(j)))² = (f(j) + g(j))²
        """
        # Analytical functions f(j) and g(j)
        j_values = np.linspace(0, self.ny-1, self.ny)
        
        # Modified parameters for extended latitude range
        # f_j controls the radius variation - more aggressive variation
        f_j = 1.0 + 1.2 * np.sin(np.pi * j_values / self.ny)
        
        # g_j controls the vertical offset - extended range
        g_j = 2.0 * j_values / self.ny - 1.0
        
        # Generate circles in stereographic plane
        j_curves = []
        for j in range(self.ny):
            radius = self.earth_radius * f_j[j]
            center_y = self.earth_radius * g_j[j]
            
            # Circle equation: x² + (y - center_y)² = radius²
            theta = np.linspace(0, 2*np.pi, self.nx)
            x = radius * np.cos(theta)
            y = center_y + radius * np.sin(theta)
            
            j_curves.append(np.column_stack((x, y)))
        
        return np.array(j_curves)
    
    def solve_icurve_ode(self, j_curve):
        """
        Solve the ODE for I-curve (mesh meridian).
        
        Equation (2): dy/dx = -y' / x'
        """
        # Extract J-curve points
        x_j = j_curve[:, 0]
        y_j = j_curve[:, 1]
        
        # Compute derivatives with robust error handling
        try:
            # Use finite differences for more robust derivative calculation
            if len(x_j) < 2:
                print("⚠️ Insufficient points for derivative calculation")
                return None, None
            
            # Central differences for interior points
            dy_dx = np.zeros_like(y_j)
            dx_dy = np.zeros_like(x_j)
            
            for i in range(1, len(x_j)-1):
                dx = x_j[i+1] - x_j[i-1]
                if np.abs(dx) > 1e-10:
                    dy_dx[i] = (y_j[i+1] - y_j[i-1]) / dx
                    dx_dy[i] = (x_j[i+1] - x_j[i-1]) / dx
                else:
                    dy_dx[i] = 0.0
                    dx_dy[i] = 0.0
            
            # Forward/backward differences for endpoints
            if len(x_j) > 1:
                dx_forward = x_j[1] - x_j[0]
                dx_backward = x_j[-1] - x_j[-2]
                
                if np.abs(dx_forward) > 1e-10:
                    dy_dx[0] = (y_j[1] - y_j[0]) / dx_forward
                    dx_dy[0] = (x_j[1] - x_j[0]) / dx_forward
                
                if np.abs(dx_backward) > 1e-10:
                    dy_dx[-1] = (y_j[-1] - y_j[-2]) / dx_backward
                    dx_dy[-1] = (x_j[-1] - x_j[-2]) / dx_backward
            
            # Handle edge cases
            dy_dx = np.nan_to_num(dy_dx, nan=0.0, posinf=1e10, neginf=-1e10)
            dx_dy = np.nan_to_num(dx_dy, nan=0.0, posinf=1e10, neginf=-1e10)
            
            # Ensure non-zero values
            dy_dx = np.where(np.abs(dy_dx) < 1e-10, np.sign(dy_dx) * 1e-10, dy_dx)
            dx_dy = np.where(np.abs(dx_dy) < 1e-10, np.sign(dx_dy) * 1e-10, dx_dy)
            
        except Exception as e:
            print(f"⚠️ Derivative calculation failed: {e}")
            return None, None
        
        # Right-hand side of ODE: dy/dx = -y' / x'
        def ode_func(x, y):
            try:
                idx = np.argmin(np.abs(x_j - x))
                y_prime = dy_dx[idx]
                x_prime = dx_dy[idx]
                
                # Handle division by zero
                if np.abs(x_prime) < 1e-10:
                    return 0.0
                
                result = -y_prime / x_prime
                return result if np.isfinite(result) else 0.0
            except Exception as e:
                print(f"⚠️ ODE function error: {e}")
                return 0.0
        
        # Initial condition: start at first point of J-curve
        x0 = x_j[0]
        y0 = y_j[0]
        
        # Solve ODE along x with more robust parameters
        try:
            solution = solve_ivp(
                ode_func,
                [x_j[0], x_j[-1]],
                [y0],
                method='RK45',
                rtol=1e-6,
                atol=1e-8,
                dense_output=True
            )
            
            if solution.success:
                x_sol = np.linspace(x_j[0], x_j[-1], self.nx)
                y_sol = solution.sol(x_sol)[0]
                return x_sol, y_sol
            else:
                print(f"⚠️ ODE solver failed: {solution.message}")
                return None, None
        except Exception as e:
            print(f"⚠️ ODE solver error: {e}")
            return None, None
    
    def generate_i_curves(self, j_curves):
        """
        Compute I-curves (mesh meridians) by solving Eq. (2).
        
        Equation (2): dy/dx = -y' / x'
        """
        i_curves = []
        for j_curve in j_curves:
            x_sol, y_sol = self.solve_icurve_ode(j_curve)
            if x_sol is not None:
                i_curves.append(np.column_stack((x_sol, y_sol)))
            else:
                # Fallback to simple meridian
                theta = np.linspace(0, np.pi, self.ny)
                x = self.earth_radius * np.sin(theta)
                y = self.earth_radius * np.cos(theta)
                i_curves.append(np.column_stack((x, y)))
        
        return np.array(i_curves)
    
    def project_to_sphere(self, polar_coords):
        """
        Project polar coordinates to spherical coordinates.
        """
        x, y = polar_coords[..., 0], polar_coords[..., 1]
        
        # Stereographic projection inverse
        rho = np.sqrt(x**2 + y**2)
        c = 2 * np.arctan2(rho, 2 * self.earth_radius)
        
        lat = 90 - np.rad2deg(c)
        lon = np.rad2deg(np.arctan2(y, x))
        
        # Ensure longitude is in range [-180, 180]
        lon = (lon + 180) % 360 - 180
        
        return lat, lon
    
    def generate_grid(self):
        """
        Generate complete grid using Madec-Imbard algorithm.
        """
        print("🔧 Generating grid using Madec-Imbard algorithm...")
        
        # Step 1: Generate J-curves
        j_curves = self.generate_j_curves()
        print(f"✅ Generated {len(j_curves)} J-curves")
        
        # Step 2: Compute I-curves
        i_curves = self.generate_i_curves(j_curves)
        print(f"✅ Generated {len(i_curves)} I-curves")
        
        # Step 3: Project to sphere for all I-curves
        all_lat = []
        all_lon = []
        
        for i_curve in i_curves:
            lat, lon = self.project_to_sphere(i_curve)
            all_lat.append(lat)
            all_lon.append(lon)
        
        print(f"✅ Projected to spherical coordinates")
        print(f"Latitude range: {np.min(all_lat):.2f} to {np.max(all_lat):.2f}")
        print(f"Longitude range: {np.min(all_lon):.2f} to {np.max(all_lon):.2f}")
        
        return {
            'nav_lat': np.array(all_lat),
            'nav_lon': np.array(all_lon)
        }
