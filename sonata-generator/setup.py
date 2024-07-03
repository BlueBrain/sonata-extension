#!/usr/bin/env python
# SPDX-License-Identifier: Apache-2.0
"""sonata generator setup"""
from setuptools import setup, find_packages

import importlib.util

spec = importlib.util.spec_from_file_location("sonata_generator.version",
                                              "sonata_generator/version.py")
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
        "numpy<2",
        "h5py>=3,<4",
        "morphio>=3,<4",
        "click>=7.1.2",
        "pyyaml>=5.4.1",
        "libsonata>=0.1.8",
        "morph_tool>=2.4.3,<3.0.0",
        "cached-property>=1.5.2",
        "astrovascpy>=0.1.4"
    ],
    packages=find_packages(),
    python_requires=">=3.10",
    entry_points={
        'console_scripts': [
            'sonata-generator=sonata_generator.app.__main__:main'
        ]
    }
)
