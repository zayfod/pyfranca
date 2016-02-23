#!/usr/bin/env python

from pyfranca import franca_lexer
from pyfranca import franca_parser


def main():
    fname = "examples/Calculator.fidl"
    with open(fname, "r") as f:
        s = f.read()

    # lexer = franca_lexer.Lexer()
    # lexer.tokenize(s)

    # parser = franca_parser.Parser()
    parser = franca_parser.Parser(write_tables=1, debug=True)
    res = parser.parse(s)
    print(res)


if __name__ == "__main__":
    main()
