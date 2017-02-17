#!/usr/bin/env python

from pyfranca import Parser, LexerException, ParserException


def main():
    parser = Parser()
    try:
        package = parser.parse("""
            package Example
            interface Interface {
                method Hello {}
            }
        """)        
    except (LexerException, ParserException) as e:
        print("ERROR: {}".format(e))

    assert package.interfaces["Interface"].methods["Hello"].name == "Hello"


if __name__ == "__main__":
    main()
