#!/usr/bin/env python3
"""
Setup script for ORCA Grid Builder package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="orca-grid-builder",
    version="1.0.0",
    author="ORCA Grid Builder Team",
    author_email="",
    description="A modular Python library for generating global ocean grids following the ORCA grid family conventions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lesommer/nemo-orca-grid-builder",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
        "numpy>=1.19.0",
        "jax>=0.2.10",
        "jaxlib>=0.1.69",
        "xarray>=0.16.0",
        "matplotlib>=3.3.0",
    ],
    entry_points={
        "console_scripts": [
            "orca-grid=orca_grid.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Hydrology",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)