#!/usr/bin/env python3
"""
Command-line interface for ORCA Grid Builder.

Usage:
    python -m orca_grid [resolution] [output_file] [--fg-source SOURCE] [--ref PATH]

Examples:
    python -m orca_grid 2deg domain_cfg.nc
    python -m orca_grid 2deg domain_cfg.nc --fg-source fitted --ref data/ORCA_R2_zps_domcfg.nc
"""

import argparse
import sys

from .grid_builder import RESOLUTION_PARAMS


def main():
    parser = argparse.ArgumentParser(
        description="Generate NEMO-compliant ORCA horizontal grid files "
                    "using the Madec & Imbard (1996) algorithm",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            f"Available resolutions: {', '.join(RESOLUTION_PARAMS.keys())}\n\n"
            "fg-source modes:\n"
            "  paper   - Use log-cosh parameterization from the paper (default)\n"
            "  fitted  - Recover f/g from a reference NEMO domain_cfg file"
        ),
    )
    parser.add_argument(
        "resolution",
        nargs="?",
        default="2deg",
        choices=list(RESOLUTION_PARAMS.keys()),
        help="Grid resolution (default: 2deg)",
    )
    parser.add_argument(
        "output",
        nargs="?",
        default="domain_cfg.nc",
        help="Output NetCDF file path (default: domain_cfg.nc)",
    )
    parser.add_argument(
        "--fg-source",
        default="paper",
        choices=["paper", "fitted"],
        help="Method for obtaining f/g coefficients (default: paper)",
    )
    parser.add_argument(
        "--ref",
        default=None,
        help="Path to reference NEMO domain_cfg.nc file (required for --fg-source fitted)",
    )

    args = parser.parse_args()

    from .grid_builder import ORCAGridBuilder

    print(f"Generating ORCA grid at {args.resolution} resolution "
          f"(fg-source: {args.fg_source})...")

    builder = ORCAGridBuilder(resolution=args.resolution)

    try:
        builder.generate_and_write(
            args.output, ref_path=args.ref, fg_source=args.fg_source
        )
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Successfully created {args.output}")


if __name__ == "__main__":
    main()
