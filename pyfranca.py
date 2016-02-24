#!/usr/bin/env python

from pyfranca import franca_lexer
from pyfranca import franca_parser


def main():
    # fname = "examples/AppOnOff.fidl"
    # fname = "examples/BasicTypes.fidl"
    # fname = "examples/Calculator.fidl"
    # fname = "examples/CommonTypes.fidl"
    # fname = "examples/ComponentTrigger.fidl"
    # fname = "examples/CompOnOff.fidl"
    # fname = "examples/InternalClientConnect.fidl"
    # fname = "examples/InternalConnect.fidl"
    # fname = "examples/InternalGateway.fidl"
    # fname = "examples/InternalServerConnect.fidl"
    # fname = "examples/NodeBroker.fidl"
    # fname = "examples/NodeOnOff.fidl"
    # fname = "examples/Persistence.fidl"
    # fname = "examples/RemoteControlGateway.fidl"
    # fname = "examples/WatchdogMaster.fidl"
    # fname = "examples/WatchdogVIPAdmin.fidl"
    fname = "examples/Test.fidl"

    # lexer = franca_lexer.Lexer()
    # lexer.tokenize_file(fname)

    # parser = franca_parser.Parser()
    parser = franca_parser.Parser(write_tables=1, debug=True)
    try:
        res = parser.parse_file(fname)
        print(res)
    except (franca_lexer.LexerException, franca_parser.ParserException) as e:
        print("ERROR: {}".format(e))


if __name__ == "__main__":
    main()
