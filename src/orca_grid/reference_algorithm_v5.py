#!/usr/bin/env python3
"""
Enhanced implementation with modified J-curve generation.
"""

import numpy as np
from scipy.integrate import solve_ivp

class EnhancedORCAGridGenerator:
    """Implementation with modified J-curve generation."""
    
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
        """Generate J-curves with variation."""
        j_values = np.linspace(0, self.ny-1, self.ny)
        
        # Modified functions to introduce variation
        f_j = 1.0 + 0.5 * np.sin(np.pi * j_values / self.ny)
        g_j = 0.3 * j_values / self.ny
        
        # Add small perturbation to break perfect circular symmetry
        perturbation = 0.01 * np.random.randn(len(j_values))
        
        j_curves = []
        for j in range(self.ny):
            radius = self.earth_radius * f_j[j]
            center_y = self.earth_radius * (g_j[j] + 0.01 * perturbation[j])
            
            # Use non-uniform theta spacing
            theta = np.linspace(0, 2*np.pi, self.nx)
            # Add small angular perturbation
            theta = theta + 0.001 * np.sin(3*theta)
            
            x = radius * np.cos(theta)
            y = center_y + radius * np.sin(theta)
            j_curves.append(np.column_stack((x, y)))
        
        return np.array(j_curves)
    
    def calculate_robust_gradient(self, y, x):
        """Calculate gradient with finite differences."""
        if len(x) < 2:
            return np.zeros_like(y), np.zeros_like(x)
        
        dy_dx = np.zeros_like(y)
        dx_dy = np.zeros_like(x)
        
        for i in range(1, len(x)-1):
            dx = x[i+1] - x[i-1]
            if np.abs(dx) > 1e-10:
                dy_dx[i] = (y[i+1] - y[i-1]) / dx
                dx_dy[i] = (x[i+1] - x[i-1]) / dx
            else:
                dy_dx[i] = 0.0
                dx_dy[i] = 0.0
        
        if len(x) > 1:
            dx_forward = x[1] - x[0]
            dx_backward = x[-1] - x[-2]
            
            if np.abs(dx_forward) > 1e-10:
                dy_dx[0] = (y[1] - y[0]) / dx_forward
                dx_dy[0] = (x[1] - x[0]) / dx_forward
            
            if np.abs(dx_backward) > 1e-10:
                dy_dx[-1] = (y[-1] - y[-2]) / dx_backward
                dx_dy[-1] = (x[-1] - x[-2]) / dx_backward
        
        dy_dx = np.nan_to_num(dy_dx, nan=0.0, posinf=1e10, neginf=-1e10)
        dx_dy = np.nan_to_num(dx_dy, nan=0.0, posinf=1e10, neginf=-1e10)
        
        dy_dx = np.where(np.abs(dy_dx) < 1e-10, np.sign(dy_dx) * 1e-10, dy_dx)
        dx_dy = np.where(np.abs(dx_dy) < 1e-10, np.sign(dx_dy) * 1e-10, dx_dy)
        
        return dy_dx, dx_dy
    
    def solve_icurve_ode(self, j_curve):
        """Solve ODE with robust method."""
        x_j = j_curve[:, 0]
        y_j = j_curve[:, 1]
        
        try:
            dy_dx, dx_dy = self.calculate_robust_gradient(y_j, x_j)
        except Exception as e:
            print(f"Robust gradient failed: {e}")
            return None, None
        
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
            
            if solution.success:
                x_sol = np.linspace(x_j[0], x_j[-1], self.nx)
                y_sol = solution.sol(x_sol)[0]
                return x_sol, y_sol
        except Exception as e:
            print(f"ODE solver failed: {e}")
        
        return None, None
    
    def generate_i_curves(self, j_curves):
        """Generate I-curves with modified method."""
        i_curves = []
        success_count = 0
        
        for j_curve in j_curves:
            x_sol, y_sol = self.solve_icurve_ode(j_curve)
            if x_sol is not None:
                i_curves.append(np.column_stack((x_sol, y_sol)))
                success_count += 1
            else:
                theta = np.linspace(0, np.pi, self.ny)
                x = self.earth_radius * np.sin(theta)
                y = self.earth_radius * np.cos(theta)
                i_curves.append(np.column_stack((x, y)))
        
        print(f"ODE solver success rate: {success_count}/{len(j_curves)}")
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
        print("🔧 Generating grid with modified J-curves...")
        
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

# Test the modified implementation
if __name__ == "__main__":
    gen = EnhancedORCAGridGenerator('1deg')
    result = gen.generate_grid()
