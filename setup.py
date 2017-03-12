#!/usr/bin/env python
"""
Pyfranca setup script.
"""

import os
import re
from setuptools import setup, find_packages


def read_package_variable(key):
    fspec = os.path.join("pyfranca", "__init__.py")
    with open(fspec) as f:
        for line in f:
            m = re.match(r"(\S+)\s*=\s*[\"']?(.+?)[\"']?\s*$", line)
            if m and key == m.group(1):
                return m.group(2)
    return None


version = read_package_variable("__version__")

setup(
    name="pyfranca",
    packages=find_packages(),
    version=version,
    description="Python parser and tools for working with the Franca "
                "interface definition language.",
    author="Kaloyan Tenchov",
    author_email="zayfod@gmail.com",
    url="http://github.com/zayfod/pyfranca",
    download_url="https://github.com/zayfod/pyfranca/archive/{}.zip".format(
        version),
    license="MIT",
    platforms="Python 2.7 and later.",
    keywords=["franca", "franca-idl", "idl", "fidl", "parsing"],
    install_requires=["ply"],
    test_suite="pyfranca.tests.get_suite",
    scripts=[
        "tools/fidl_dump.py",
        "tools/fidl_validator.py",
    ],
)
