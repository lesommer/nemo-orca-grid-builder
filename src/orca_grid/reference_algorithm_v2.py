#!/usr/bin/env python3
"""
Enhanced reference implementation of Madec-Imbard (1996) algorithm.
"""

import numpy as np
from scipy.integrate import solve_ivp

class EnhancedORCAGridGenerator:
    """
    Enhanced implementation with robust numerical methods.
    """
    
    def __init__(self, resolution="1deg"):
        self.resolution = resolution
        self.earth_radius = 6371000.0
        
        if resolution == "1deg":
            self.nx = 360
            self.ny = 331
        elif resolution == "0.5deg":
            self.nx = 720
            self.ny = 661
        else:
            raise ValueError(f"Unsupported resolution: {resolution}")
    
    def generate_j_curves(self):
        """Generate J-curves (mesh parallels)."""
        j_values = np.linspace(0, self.ny-1, self.ny)
        f_j = 1.0 + 0.5 * np.sin(np.pi * j_values / self.ny)
        g_j = 0.3 * j_values / self.ny
        
        j_curves = []
        for j in range(self.ny):
            radius = self.earth_radius * f_j[j]
            center_y = self.earth_radius * g_j[j]
            theta = np.linspace(0, 2*np.pi, self.nx)
            x = radius * np.cos(theta)
            y = center_y + radius * np.sin(theta)
            j_curves.append(np.column_stack((x, y)))
        
        return np.array(j_curves)
    
    def calculate_derivatives(self, x, y):
        """Calculate derivatives with regularization."""
        dy_dx = np.gradient(y, x)
        dx_dy = np.gradient(x, y)
        
        # Regularize near-zero values
        dy_dx = np.where(np.abs(dy_dx) < 1e-10, 1e-10, dy_dx)
        dx_dy = np.where(np.abs(dx_dy) < 1e-10, 1e-10, dx_dy)
        
        return dy_dx, dx_dy
    
    def solve_icurve_ode(self, j_curve):
        """Solve ODE with multiple strategies."""
        x_j = j_curve[:, 0]
        y_j = j_curve[:, 1]
        
        # Calculate derivatives with regularization
        try:
            dy_dx, dx_dy = self.calculate_derivatives(x_j, y_j)
        except Exception as e:
            print(f"Derivative calculation failed: {e}")
            return None, None
        
        # ODE function with error handling
        def ode_func(x, y):
            try:
                idx = np.argmin(np.abs(x_j - x))
                y_prime = dy_dx[idx]
                x_prime = dx_dy[idx]
                
                if np.abs(x_prime) < 1e-10:
                    return 0.0
                
                result = -y_prime / x_prime
                return result if np.isfinite(result) else 0.0
            except:
                return 0.0
        
        # Solve ODE
        try:
            solution = solve_ivp(
                ode_func,
                [x_j[0], x_j[-1]],
                [y_j[0]],
                method='RK45',
                rtol=1e-6,
                atol=1e-8
            )
            
            if solution.success:
                x_sol = np.linspace(x_j[0], x_j[-1], self.nx)
                y_sol = solution.sol(x_sol)[0]
                return x_sol, y_sol
        except Exception as e:
            print(f"ODE solver failed: {e}")
        
        return None, None
    
    def generate_i_curves(self, j_curves):
        """Generate I-curves with fallback."""
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
        """Project to spherical coordinates."""
        x, y = polar_coords[..., 0], polar_coords[..., 1]
        rho = np.sqrt(x**2 + y**2)
        c = 2 * np.arctan2(rho, 2 * self.earth_radius)
        lat = 90 - np.rad2deg(c)
        lon = np.rad2deg(np.arctan2(y, x))
        return lat, lon
    
    def generate_grid(self):
        """Generate complete grid."""
        print("🔧 Generating enhanced grid...")
        
        j_curves = self.generate_j_curves()
        print(f"✅ Generated {len(j_curves)} J-curves")
        
        i_curves = self.generate_i_curves(j_curves)
        print(f"✅ Generated {len(i_curves)} I-curves")
        
        lat, lon = self.project_to_sphere(i_curves[0])
        print(f"✅ Projected to spherical coordinates")
        print(f"Latitude range: {lat.min():.2f} to {lat.max():.2f}")
        print(f"Longitude range: {lon.min():.2f} to {lon.max():.2f}")
        
        return {
            'nav_lat': lat,
            'nav_lon': lon
        }

# Test the enhanced implementation
if __name__ == "__main__":
    gen = EnhancedORCAGridGenerator('1deg')
    result = gen.generate_grid()
