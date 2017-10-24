#!/usr/bin/env python

import argparse
from pyfranca import Processor, LexerException, ParserException, \
    ProcessorException


def dump_comments(item, prefix):
    for key, value in item.comments.items():
        print (prefix + key + ": " + value)


def dump_namespace(namespace):
    if namespace.typedefs:
        print("\t\tTypedefs:")
        for item in namespace.typedefs.values():
            print("\t\t- {} is {}".format(item.name, item.type.name))
            dump_comments(item, "\t\t\t")
    if namespace.enumerations:
        print("\t\tEnumerations:")
        for item in namespace.enumerations.values():
            print("\t\t- {}".format(item.name))
            dump_comments(item, "\t\t\t")
    if namespace.structs:
        print("\t\tStructs:")
        for item in namespace.structs.values():
            print("\t\t- {}".format(item.name))
            dump_comments(item, "\t\t\t")
    if namespace.unions:
        print("\t\tUnions:")
        for item in namespace.unions.values():
            print("\t\t- {}".format(item.name))
            dump_comments(item, "\t\t\t")
    if namespace.arrays:
        print("\t\tArrays:")
        for item in namespace.arrays.values():
            print("\t\t- {}".format(item.name))
            dump_comments(item, "\t\t\t")
    if namespace.maps:
        print("\t\tMaps:")
        for item in namespace.maps.values():
            print("\t\t- {}".format(item.name))
            dump_comments(item, "\t\t\t")


def dump_interface(interface):
    if interface.attributes:
        print("\t\tAttributes:")
        for item in interface.attributes.values():
            print("\t\t- {}".format(item.name))
            dump_comments(item, "\t\t\t")
    if interface.methods:
        print("\t\tMethods:")
        for item in interface.methods.values():
            print("\t\t- {}()".format(item.name))
            dump_comments(item, "\t\t\t")
    if interface.broadcasts:
        print("\t\tBroadcasts:")
        for item in interface.broadcasts.values():
            print("\t\t- {}".format(item.name))
            dump_comments(item, "\t\t\t")
    dump_namespace(interface)


def dump_package(package):
    print("- {} ({})".format(package.name, str.join(", ", package.files)))
    dump_comments(package, "\t")
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
            print("\t- {}{}".format(interface.name, version_str))
            dump_comments(interface, "\t\t")
            dump_interface(interface)
    if package.typecollections:
        print("\tType collections:")
        for typecollection in package.typecollections.values():
            if typecollection.version:
                version_str = " (v{})".format(typecollection.version)
            else:
                version_str = ""
            print("\t- {}{}".format(typecollection.name, version_str))
            dump_comments(typecollection, "\t\t")
            dump_namespace(typecollection)


def dump_packages(packages):
    print("Packages:")
    for package in packages.values():
        dump_package(package)


def plot_namepsace_dependencie(namespace, output):
    ns_fqn = "{}.{}".format(namespace.package.name,namespace.name)

    ns_fqn_line = "\n\t\"" + ns_fqn + "\"\n"
    if ns_fqn_line not in output:
         output += ns_fqn_line
    for import_ns in namespace.namespace_references:
        import_ns_fqn = "{}.{}".format(import_ns.package.name, import_ns.name)
        tmp_output = "\t\"" + ns_fqn + "\" -> \"" + import_ns_fqn + "\";\n"
        if tmp_output not in output:
            output += tmp_output
        output = plot_namepsace_dependencie(import_ns, output)
    return output


def plot_namespace_dependencies(namespace, type_str):
    output = "\n\n"
    output += "digraph \" {} {}.{} \" \n".format(type_str, namespace.package.name, namespace.name) + "{\n"
    output = plot_namepsace_dependencie(namespace, output)
    output += "}"
    print(output)


def plot_namespaces_dependencies(packages):
    for package in packages.values():
        for ns in package.typecollections.values():
            plot_namespace_dependencies(ns, "typecollection")
        for ns in package.interfaces.values():
            plot_namespace_dependencies(ns, "interface")


def plot_package_dependencie(package, output):
    pkg_fqn_line = "\t\"" + package.name + "\"\n"

    if pkg_fqn_line not in output:
        output += pkg_fqn_line

    for package_import in package.imports:
        if package.name != package_import.package_reference.name:
            tmp_output = "\t\"" + package.name + "\" -> \"" + package_import.package_reference.name + "\";\n"

            if tmp_output not in output:
                output += tmp_output
            output = plot_package_dependencie(package_import.package_reference, output)
    return output


def plot_package_dependencies(package):
    output = "\n\n"

    output += "digraph \" {} \"\n".format(package.name) + "{\n"
    output = plot_package_dependencie(package, output)
    output += "}"

    print(output)


def plot_packages_dependencies(packages):
    for package in packages.values():
        plot_package_dependencies(package)


def parse_command_line():
    parser = argparse.ArgumentParser(
        description="Dumps the contents of a Franca IDL model.")
    parser.add_argument(
        "fidl", nargs="+",
        help="Input FIDL file.")
    parser.add_argument(
        "-I", "--import", dest="import_dirs", metavar="import_dir",
        action="append", help="Model import directories.")
    parser.add_argument("-pl", "--plot", choices=['p', 'n', 'f', 'c'],
                        help='''\plot FIDL dependecies as a dot image:
                                p    plot package dependencies
                                n    plot namespace dependencies
                                f    plot file dependencies
                                c    plot type collaboration diagram
                         ''')
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

    if args.plot is None:
        dump_packages(processor.packages)
    elif args.plot == "p":
        plot_packages_dependencies(processor.packages)
    elif args.plot == "n":
        plot_namespaces_dependencies(processor.packages)

if __name__ == "__main__":
    main()
