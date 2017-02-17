
from setuptools import setup


setup(
    name="pyfranca",
    packages=["pyfranca"],
    version="0.2.0",
    description="Python parser and tools for working with the Franca "
                "interface definition language.",
    author="Kaloyan Tenchov",
    author_email="zayfod@gmail.com",
    url="http://github.com/zayfod/pyfranca",
    download_url="https://github.com/zayfod/pyfranca/archive/0.2.0.zip",
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
