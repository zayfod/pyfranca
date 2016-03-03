
from setuptools import setup, find_packages


setup(
    name="pyfranca",
    packages=find_packages(),
    version="0.2.0",
    description="Python parser and tools for working with the Franca "
                "interface definition language.",
    author="Kaloyan Tenchov",
    author_email="zayfod@gmail.com",
    url="http://github.com/zayfod/pyfranca",
    license="MIT",
    platforms="Python 2.6 and later.",
    keywords=["franca", "idl", "fidl", "parser"],
    requires=["ply"],
    test_suite="pyfranca.tests",
)
