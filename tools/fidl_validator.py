#!/usr/bin/env python

import argparse
from pyfranca import Processor, LexerException, ParserException, \
    ProcessorException


def parse_command_line():
    parser = argparse.ArgumentParser(
        description="Behavioral cloning model trainer.")
    parser.add_argument(
        "fidl", nargs="+",
        help="Input FIDL file.")
    parser.add_argument(
        "-I", "--import", dest="import_dirs", metavar="import_dir",
        action="append", help="Model import directories.")
    args = parser.parse_args()
    return args


def main():
    args = parse_command_line()

    processor = Processor()
    if args.import_dirs:
        processor.package_paths.extend(args.import_dirs)

    try:
        for fidl in args.fidl:
            processor.import_file(fidl)
    except (LexerException, ParserException, ProcessorException) as e:
        print("ERROR: {}".format(e))
        exit(1)

    print("Valid Franca model.")


if __name__ == "__main__":
    main()
