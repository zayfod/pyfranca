
import os
from collections import OrderedDict
from pyfranca import franca_parser, ast


class ProcessorException(Exception):

    def __init__(self, message):
        super(ProcessorException, self).__init__()
        self.message = message

    def __str__(self):
        return self.message


class Processor:
    """
    Franca IDL processor.
    """

    def __init__(self):
        """
        Constructor.
        """
        # Default package paths.
        self.package_paths = []
        self.files = {}
        self.packages = {}

    @staticmethod
    def basename(namespace):
        """
        Extract the type or namespace name from a Franca FQN.
        """
        dot = namespace.rfind(".")
        if dot == -1:
            return namespace
        else:
            return namespace[dot + 1:]

    @staticmethod
    def packagename(namespace):
        """
        Extract the package name from a Franca FQN.
        """
        dot = namespace.rfind(".")
        if dot == -1:
            return None
        else:
            return namespace[0:dot]

    @staticmethod
    def is_fqn(string):
        """
        Defines whether a Franca name is an ID or an FQN.
        """
        return string.count(".") >= 2

    @staticmethod
    def split_fqn(fqn):
        """
        Split a Franca FQN into a tuple - package, namespace, and name.
        """
        parts = fqn.rsplit(".", 2)
        while len(parts) < 3:
            parts.insert(0, None)
        return tuple(parts)

    @staticmethod
    def resolve(namespace, fqn):
        """
        Resolve type references.

        :param namespace: context ast.Namespace object.
        :param fqn: FQN or ID string.
        :return: Dereferenced ast.Type object.
        """
        if not isinstance(namespace, ast.Namespace) or \
                not isinstance(fqn, str):
            raise ValueError("Unexpected input.")
        pkg, ns, name = Processor.split_fqn(fqn)
        if pkg is None:
            # This is an ID
            # Look in the type's namespace
            if name in namespace:
                return namespace[name]
            # Look in other type collections in the type's package
            for typecollection in namespace.package.typecollections.values():
                if name in typecollection:
                    return typecollection[name]
            # Look in imports
            for package_import in namespace.package.imports:
                if package_import.namespace_reference:
                    # Look in namespaces imported in the type's package
                    if name in package_import.namespace_reference:
                        return package_import.namespace_reference[name]
        else:
            # This is an FQN
            if pkg == namespace.package.name:
                # Check in the current package
                if ns in namespace.package.typecollections:
                    if name in namespace.package.typecollections[ns]:
                        return namespace.package.typecollections[ns][name]
            else:
                # Look in typecollections of packages imported in the
                #   type's package using FQNs.
                for package_import in namespace.package.imports:
                    if package_import.namespace == "{}.{}.*".format(pkg, ns):
                        for typecollection in package_import.\
                                package_reference.typecollections.values():
                            if typecollection.name == ns and \
                                    name in typecollection:
                                return typecollection[name]
                        for interface in package_import. \
                                package_reference.interfaces.values():
                            if name in interface:
                                return interface[name]
        # Give up
        raise ProcessorException(
            "Unresolved reference '{}'.".format(fqn))

    @staticmethod
    def resolve_namespace(package, fqn):
        """
        Resolve namespace references.

        :param package: context ast.Package object.
        :param fqn: FQN or ID string.
        :return: Dereferenced ast.Namespace object.
        """
        if not isinstance(package, ast.Package) or not isinstance(fqn, str):
            raise ValueError("Unexpected input.")
        if fqn.count(".") > 0:
            pkg, name = fqn.rsplit(".", 2)
        else:
            pkg, name = (None, fqn)
        if pkg is None:
            # This is an ID
            # Look for other namespaces in the package
            if name in package:
                return package[name]
            # Look in model imports
            for package_import in package.imports:
                if not package_import.namespace:
                    if name in package_import.package_reference:
                        return package_import.package_reference[name]
        else:
            # This is an FQN
            if pkg == package.name:
                # Check in the current package
                if name in package:
                    return package[name]
            else:
                # Look in model imports
                for package_import in package.imports:
                    if not package_import.namespace:
                        if name in package_import.package_reference:
                            return package_import.package_reference[name]
        # Give up
        raise ProcessorException(
            "Unresolved namespace reference '{}'.".format(fqn))

    def _update_complextype_references(self, name):
        """
        Update type references in a complex type.

        :param name: ast.ComplexType object.
        """
        if isinstance(name, ast.Enumeration):
            if name.extends:
                name.reference = self.resolve(name.namespace, name.extends)
                if not isinstance(name.reference, ast.Enumeration):
                    raise ProcessorException(
                        "Invalid enumeration reference '{}'.".format(
                            name.extends))
        elif isinstance(name, ast.Struct):
            for field in name.fields.values():
                self._update_type_references(name.namespace, field.type)
            if name.extends:
                name.reference = self.resolve(name.namespace, name.extends)
                if not isinstance(name.reference, ast.Struct):
                    raise ProcessorException(
                        "Invalid struct reference '{}'.".format(
                            name.extends))
        elif isinstance(name, ast.Union):
            for field in name.fields.values():
                self._update_type_references(name.namespace, field.type)
            if name.extends:
                name.reference = self.resolve(name.namespace, name.extends)
                if not isinstance(name.reference, ast.Union):
                    raise ProcessorException(
                        "Invalid union reference '{}'.".format(
                            name.extends))
        elif isinstance(name, ast.Array):
            self._update_type_references(name.namespace, name.type)
        elif isinstance(name, ast.Map):
            self._update_type_references(name.namespace, name.key_type)
            self._update_type_references(name.namespace, name.value_type)
        else:
            assert False

    def _update_type_references(self, namespace, name):
        """
        Update type references in a type.

        :param namespace: ast.Namespace context.
        :param name: ast.Type object.
        """
        if isinstance(name, ast.Typedef):
            self._update_type_references(name.namespace, name.type)
        elif isinstance(name, ast.PrimitiveType):
            pass
        elif isinstance(name, ast.ComplexType):
            self._update_complextype_references(name)
        elif isinstance(name, ast.Reference):
            if not name.namespace:
                name.namespace = namespace
            if not name.reference:
                resolved_name = self.resolve(namespace, name.name)
                name.reference = resolved_name
        elif isinstance(name, ast.Attribute):
            self._update_type_references(name.namespace, name.type)
        elif isinstance(name, ast.Method):
            for arg in name.in_args.values():
                self._update_type_references(name.namespace, arg.type)
            for arg in name.out_args.values():
                self._update_type_references(name.namespace, arg.type)
            if isinstance(name.errors, OrderedDict):
                for arg in name.errors.values():
                    # I end up here also when it's an Enumeration so it
                    # fails on arg.type.  Why?  Trying to workaround
                    try:
                        self._update_type_references(name.namespace, arg.type)
                    except:
                        pass
            elif isinstance(name.errors, ast.Reference):
                # Errors can be a reference to an enumeration
                self._update_type_references(name.namespace, name.errors)
                if not isinstance(name.errors.reference, ast.Enumeration):
                    raise ProcessorException(
                        "Invalid error reference '{}'.".format(
                            name.errors.name))
            else:
                assert False
        elif isinstance(name, ast.Broadcast):
            for arg in name.out_args.values():
                self._update_type_references(name.namespace, arg.type)
        else:
            assert False

    def _update_namespace_references(self, namespace):
        """
        Update type references in a namespace.

        :param namespace: ast.Namespace object.
        """
        for name in namespace.typedefs.values():
            self._update_type_references(namespace, name)
        for name in namespace.enumerations.values():
            self._update_type_references(namespace, name)
        for name in namespace.structs.values():
            self._update_type_references(namespace, name)
        for name in namespace.unions.values():
            self._update_type_references(namespace, name)
        for name in namespace.arrays.values():
            self._update_type_references(namespace, name)
        for name in namespace.maps.values():
            self._update_type_references(namespace, name)

    def _update_interface_references(self, namespace):
        """
        Update type references in an interface.

        :param namespace: ast.Interface object.
        """
        self._update_namespace_references(namespace)
        for name in namespace.attributes.values():
            self._update_type_references(namespace, name)
        for name in namespace.methods.values():
            self._update_type_references(namespace, name)
        for name in namespace.broadcasts.values():
            self._update_type_references(namespace, name)
        if namespace.extends:
            namespace.reference = self.resolve_namespace(
                namespace.package, namespace.extends)
            if not isinstance(namespace.reference, ast.Interface):
                raise ProcessorException(
                    "Invalid interface reference '{}'.".format(
                        namespace.extends))

    def _update_package_references(self, package):
        """
        Update type references in a package.

        :param package: ast.Package object.
        """
        for package_import in package.imports:
            assert package_import.package_reference is not None
            if package_import.namespace:
                # Namespace import
                package_reference = package_import.package_reference
                if not package_import.namespace.endswith(".*"):
                    raise ProcessorException(
                        "Invalid namespace import {}.".format(
                            package_import.namespace))
                namespace_name = \
                    package_import.namespace[len(package_reference.name)+1:-2]
                # Update namespace reference
                if namespace_name in package_reference:
                    namespace = package_reference[namespace_name]
                    package_import.namespace_reference = namespace
                else:
                    raise ProcessorException(
                        "Namespace '{}' not found.".format(
                            package_import.namespace))
            else:
                # Model import
                assert package_import.namespace_reference is None
        for namespace in package.typecollections:
            self._update_namespace_references(
                package.typecollections[namespace])
        for namespace in package.interfaces:
            self._update_interface_references(
                package.interfaces[namespace])

    def import_package(self, fspec, package, references=None):
        """
        Import an ast.Package into the processor.

        :param fspec: File specification of the package.
        :param package: ast.Package object.
        :param references: A list of package references.
        """
        if not isinstance(package, ast.Package):
            ValueError("Expected ast.Package as input.")
        if not references:
            references = []
        # Check whether package is already imported
        if package.name in self.packages:
            if fspec not in self.packages[package.name].files:
                # Merge the new package into the already existing one.
                self.packages[package.name] += package
                # Register the package file in the processor.
                self.files[fspec] = self.packages[package.name]
                package = self.packages[package.name]
            else:
                return
        else:
            # Register the package in the processor.
            self.packages[package.name] = package
            # Register the package file in the processor.
            self.files[fspec] = package
        # Process package imports
        fspec_path = os.path.abspath(fspec)
        fspec_dir = os.path.dirname(fspec_path)
        for package_import in package.imports:
            imported_package = self.import_file(
                package_import.file, references + [package.name], fspec_dir)
            # Update import reference
            package_import.package_reference = imported_package
        # Update type references
        self._update_package_references(package)

    def import_string(self, fspec, fidl, references=None):
        """
        Parse an FIDL string and import it into the processor as package.

        :param fspec: File specification of the package.
        :param fidl: FIDL string.
        :param references: A list of package references.
        :return: The parsed ast.Package.
        """
        # Parse the string.
        parser = franca_parser.Parser()
        package = parser.parse(fidl)
        package.files = [fspec]
        # Import the package in the processor.
        self.import_package(fspec, package, references)
        return package

    def import_file(self, fspec, references=None, package_path=None):
        """
        Parse an FIDL file and import it into the processor as package.

        :param fspec: File specification.
        :param references: A list of package references.
        :param package_paths: Additional model path to search for imports.
        :return: The parsed ast.Package.
        """
        if fspec in self.files:
            # File already loaded.
            return self.files[fspec]
        if not os.path.exists(fspec):
            if os.path.isabs(fspec):
                # Absolute specification
                raise ProcessorException(
                    "Model '{}' not found.".format(fspec))
            else:
                # Relative specification.
                package_paths = self.package_paths[:]
                if package_path:
                    package_paths.insert(0, package_path)
                # Check in the package path list.
                for path in package_paths:
                    temp_fspec = os.path.join(path, fspec)
                    if os.path.exists(temp_fspec):
                        fspec = temp_fspec
                        break
                else:
                    raise ProcessorException(
                        "Model '{}' not found.".format(fspec))
        # Parse the file.
        parser = franca_parser.Parser()
        package = parser.parse_file(fspec)
        # Import the package in the processor.
        self.import_package(fspec, package, references)
        return package
