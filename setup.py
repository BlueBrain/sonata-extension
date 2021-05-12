#!/usr/bin/env python

import imp

from setuptools import setup, find_packages

setup(
    name="sonata-generator",
    version="0.0.1",
    description="generate sample data for SONATA",
    url="https://bbpteam.epfl.ch/documentation/projects/my-project",
    license="BBP-internal-confidential",
    install_requires=[
        "numpy",
        "loguru",
        "h5py",
        "morphio",
        "scipy",
        "click",
        "pyyaml",
        "libsonata"
    ],
    packages=find_packages(),
    python_requires=">=3.6",
)
