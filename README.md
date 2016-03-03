PyFranca
========

[![Build Status](https://travis-ci.org/zayfod/pyfranca.svg?branch=master)](https://travis-ci.org/zayfod/pyfranca)
[![Coverage Status](https://coveralls.io/repos/github/zayfod/pyfranca/badge.svg?branch=master)](https://coveralls.io/github/zayfod/pyfranca?branch=master)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/zayfod/pyfranca/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/zayfod/pyfranca/?branch=master)
[![PyPI Version](http://img.shields.io/pypi/v/pyfranca.svg)](https://pypi.python.org/pypi/pyfranca)


Introduction
------------

`PyFranca` is a Python module and tools for working with [Franca interface definition language](https://github.com/franca/franca) (IDL) files (`.fidl`). It is entirely written in Python and intended to be used as a base for developing code generation and processing tools.

`PyFranca` provides:
 
- abstract syntax tree (AST) representation for a subset of the Franca IDL v0.9.2 .
- a lexer and parser for the Franca IDL, based on [Python Lex-Yacc](http://www.dabeaz.com/ply/) (PLY)

The following extensions are envisioned:

- a base processor for Franca IDL files
- .fidl validator
- diff tool for .fidl files for detecting interface changes   

This project is a tool for exploring the capabilities of Franca. It is unstable and heavily under development.


Usage
-----

Parsing Franca IDL:

    from pyfranca.franca_parser import Parser

    parser = Parser()
    package = parser.parse("""
        package Example
        interface Interface {
            method Hello {}
        }
    """)

    assert package.interfaces["Interface"].methods["Hello"].name == "Hello"

Parsing a `.fidl` file:

    from pyfranca.franca_lexer import LexerException
    from pyfranca.franca_parser import Parser, ParserException

    parser = Parser()
    try:
        package = parser.parse_file("examples/Calculator.fidl")
        print(package.name)
        for interface in package.interfaces.values():
            print(interface.name)
    except (LexerException, ParserException) as e:
        print("ERROR: {}".format(e))
    	

Limitations
-----------

The following Franca features are not supported:

- structured comments are currently ignored
- constants
- expressions
- unions
- contracts


Requirements
------------

- Python 2.7 or 3
- PLY


Installation
------------

Using pip:

	pip install pyfranca

From source:

	git clone http://github.com/zayfod/pyfranca.git
	cd pyfranca
	python setup.py install


Bugs
----

Bug reports and patches should be sent via GitHub:

http://github.com/zayfod/pyfranca
