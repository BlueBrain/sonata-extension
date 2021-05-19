#!/usr/bin/env python
"""sonata generator setup"""
from setuptools import setup, find_packages

import importlib.util

spec = importlib.util.spec_from_file_location("sonata_generator.version", "sonata_generator/version.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
VERSION = module.VERSION


setup(
    name="sonata-generator",
    version=VERSION,
    description="generate sample data for SONATA",
    url="https://bbpteam.epfl.ch/documentation/projects/my-project",
    license="BBP-internal-confidential",
    install_requires=[
        "numpy",
        "h5py>=3,<4",
        "morphio>=3,<4",
        "scipy>=1.5.4",
        "click>=7.1.2",
        "pyyaml>=5.4.1",
        "libsonata>=0.1.8"
    ],
    packages=find_packages(),
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            'sonata-generator=sonata_generator.app.__main__:main'
        ]
    }
)
