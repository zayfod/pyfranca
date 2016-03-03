
from distutils.core import setup

setup(
    name = "pyfranca",
    packages = ["pyfranca"],
    version = "0.1.0",
    description = "Python parser and tools for working with the Franca "
                  "interface definition language.",
    author = "Kaloyan Tenchov",
    author_email = "zayfod@gmail.com",
    url = "http://github.com/zayfod/pyfranca",
    download_url = "http://github.com/zayfod/pyfranca/tarball/0.1.0",
    keywords = ["franca", "idl", "fidl", "parser"],
    requires = ["ply"]
)
