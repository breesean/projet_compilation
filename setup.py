#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from glob import glob
from os.path import basename
from os.path import splitext

from setuptools import find_packages
from setuptools import setup

setup(
    name="compiler",
    version="0.0.0",
    license="BSD-2-Clause",
    py_modules=[splitext(basename(path))[0] for path in glob("compiler/*.py")],
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.9",
    install_requires=["pytest"],
)
