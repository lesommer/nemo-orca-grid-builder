#!/usr/bin/env python3
"""
Command-line interface for ORCA Grid Builder.

Usage:
    python -m orca_grid [resolution] [output_file]

Examples:
    python -m orca_grid 2deg domain_cfg.nc
    python -m orca_grid 1deg my_grid.nc
"""

import sys
from .grid_builder import ORCAGridBuilder


def main():
    resolution = "2deg"
    output_file = "domain_cfg.nc"

    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg in ["2deg", "1deg", "0.5deg", "0.25deg", "1/12deg"]:
            resolution = arg
        elif arg.endswith(".nc"):
            output_file = arg
        elif i == 0:
            resolution = arg
        elif i == 1:
            output_file = arg

    print(f"Generating ORCA grid at {resolution} resolution...")

    builder = ORCAGridBuilder(resolution=resolution)
    builder.generate_and_write(output_file)

    print(f"Successfully created {output_file}")


if __name__ == "__main__":
    main()
