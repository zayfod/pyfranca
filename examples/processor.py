#!/usr/bin/env python
"""
Pyfranca processor example.
"""

from pyfranca import Processor, LexerException, ParserException, \
    ProcessorException


def main():
    processor = Processor()
    try:
        processor.import_string("hello.fidl", """
            package Example
            interface Interface {
                method Hello {}
            }
        """)
        assert processor.packages["Example"].interfaces["Interface"].\
            methods["Hello"].name == "Hello"
    except (LexerException, ParserException, ProcessorException) as e:
        print("ERROR: {}".format(e))


if __name__ == "__main__":
    main()
