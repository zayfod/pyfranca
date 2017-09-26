#!/usr/bin/env python

import argparse
from pyfranca import Processor, LexerException, ParserException, \
    ProcessorException


def dump_namespace(namespace):
    if namespace.typedefs:
        print("\t\tTypedefs:")
        for item in namespace.typedefs.values():
            dump_comments(item.comments, "\t\t- ")
            print("\t\t- {} is {}".format(item.name, item.type.name))
    if namespace.enumerations:
        print("\t\tEnumerations:")
        for item in namespace.enumerations.values():
            dump_comments(item.comments, "\t\t- ")
            print("\t\t- {}".format(item.name))
    if namespace.structs:
        print("\t\tStructs:")
        for item in namespace.structs.values():
            dump_comments(item.comments, "\t\t- ")
            print("\t\t- {}".format(item.name))
    if namespace.arrays:
        print("\t\tArrays:")
        for item in namespace.arrays.values():
            dump_comments(item.comments, "\t\t- ")
            print("\t\t- {}".format(item.name))
    if namespace.maps:
        print("\t\tMaps:")
        for item in namespace.maps.values():
            dump_comments(item.comments, "\t\t- ")
            print("\t\t- {}".format(item.name))


def dump_interface(interface):
    if interface.attributes:
        print("\t\tAttributes:")
        for item in interface.attributes.values():
            dump_comments(item.comments, "\t\t- ")
            print("\t\t- {}".format(item.name))
    if interface.methods:
        print("\t\tMethods:")
        for item in interface.methods.values():
            dump_comments(item.comments, "\t\t- ")
            print("\t\t- {}()".format(item.name))
    if interface.broadcasts:
        print("\t\tBroadcasts:")
        for item in interface.broadcasts.values():
            dump_comments(item.comments, "\t\t- ")
            print("\t\t- {}".format(item.name))
    dump_namespace(interface)


def dump_package(package):
    dump_comments(package.comments, "")
    print("- {} ({})".format(package.name, str.join(", ", package.files)))
    if package.imports:
        print("\tImports:")
        for imp in package.imports:
            print("\t- {} from {}".format(imp.namespace, imp.file))
    if package.interfaces:
        print("\tInterfaces:")
        for interface in package.interfaces.values():
            if interface.version:
                version_str = " (v{})".format(interface.version)
            else:
                version_str = ""
            dump_comments(interface.comments, "\t- ")
            print("\t- {}{}".format(interface.name, version_str))
            dump_interface(interface)
    if package.typecollections:
        print("\tType collections:")
        for typecollection in package.typecollections.values():
            if typecollection.version:
                version_str = " (v{})".format(typecollection.version)
            else:
                version_str = ""
            dump_comments(typecollection.comments, "\t- ")
            print("\t- {}{}".format(typecollection.name, version_str))
            dump_namespace(typecollection)


def dump_packages(packages):
    print("Packages:")
    for package in packages.values():
        dump_package(package)


def dump_comments(comments, präfix):
    for key, value in comments.items():
        print (präfix + key + " : " + value)


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

    dump_packages(processor.packages)


if __name__ == "__main__":
    main()
