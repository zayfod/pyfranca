PyFranca
========

[![Build Status](https://travis-ci.org/zayfod/pyfranca.svg?branch=master)](https://travis-ci.org/zayfod/pyfranca)
[![Coverage Status](https://coveralls.io/repos/github/zayfod/pyfranca/badge.svg?branch=master)](https://coveralls.io/github/zayfod/pyfranca?branch=master)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/zayfod/pyfranca/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/zayfod/pyfranca/?branch=master)
[![PyPI Version](http://img.shields.io/pypi/v/pyfranca.svg)](https://pypi.python.org/pypi/pyfranca)


Introduction
------------

`PyFranca` is a Python module and tools for working with
[Franca interface definition language](https://github.com/franca/franca)
(IDL) files (`.fidl`). It is entirely written in Python and intended to be
used as a base for developing code generation and processing tools.

`PyFranca` provides:
 
- abstract syntax tree (AST) representation for a subset of the
    Franca IDL v0.9.2 .
- a lexer and parser for the Franca IDL, based on
    [Python Lex-Yacc](http://www.dabeaz.com/ply/) (PLY).
- a processor for Franca IDL files that handles model imports and
    type references.
- a .fidl file command-line validator

The following extensions are envisioned:

- AST serializer
- diff tool for .fidl files for detecting interface changes   

This project is a tool for exploring the capabilities (and ambiguities) of
Franca. It is unstable and heavily under development.


Library Usage
-------------

Processing Franca IDL:

```python
from pyfranca import Processor

processor = Processor()
processor.import_string("hello.fidl", """
    package Example
    interface Interface {
        method Hello {}
    }
""")
        
assert processor.packages["Example"].interfaces["Interface"].methods["Hello"].name == "Hello"
```

Listing the packages and interfaces, defined in a `.fidl` file:

```python
from pyfranca import Processor, LexerException, ParserException, ProcessorException

processor = Processor()
try:
    processor.import_file("hello.fidl")        
except (LexerException, ParserException, ProcessorException) as e:
    print("ERROR: {}".format(e))

for package in processor.packages.values():
    print(package.name)
    for interface in package.interfaces.values():
        print("\t", interface.name)
```


Tool Usage
----------

Visualizing Franca models:

    fidl_dump.py model.fidl

Validating Franca models:

    fidl_validator.py -I packages model.fidl


Limitations
-----------

The following Franca features are not supported:

- dots in type collection and interface names
- expressions
- unions
- method overloading
- method error extending
- contracts


Requirements
------------

- Python 2.7 or 3.4
- PLY


Installation
------------

Using pip:

    pip install pyfranca

From source:

    git clone http://github.com/zayfod/pyfranca.git
    cd pyfranca
    python setup.py install


Documentation
-------------

API documentation is available on PythonHosted.org:

http://pythonhosted.org/pyfranca/


Bugs
----

Bug reports and patches should be sent via GitHub:

http://github.com/zayfod/pyfranca
