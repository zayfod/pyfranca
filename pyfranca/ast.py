
from abc import ABCMeta


class Package(object):
    """
    AST representation of a Franca package.
    """

    def __init__(self, name=None, interfaces=None):
        """
        Constructs a new Package.
        """
        if interfaces is None:
            interfaces = {}

        self.name = name
        self.interfaces = interfaces

        for interface in self.interfaces.values():
            interface.package = self


class Import(object):

    def __init__(self, file_name, namespace=None):
        self.file = file_name
        self.namespace = namespace


class TypeCollection(object):

    def __init__(self, name, flags=None, version=None, typedefs=None, enumerations=None,
                 structs=None, arrays=None, maps=None):
        self.name = name
        self.flags = flags if flags else []         # Unused
        self.version = version
        self.typedefs = typedefs if typedefs else []
        self.enumerations = enumerations if enumerations else []
        self.structs = structs if structs else []
        self.arrays = arrays if arrays else []
        self.maps = maps if maps else []


class Typedef(object):

    def __init__(self, name, base_type):
        self.name = name
        self.type = base_type


class Type(object):
    __metaclass__ = ABCMeta


class Int8(Type):
    pass


class Int16(Type):
    pass


class Int32(Type):
    pass


class Int64(Type):
    pass


class UInt8(Type):
    pass


class UInt16(Type):
    pass


class UInt32(Type):
    pass


class UInt64(Type):
    pass


class Boolean(Type):
    pass


class Float(Type):
    pass


class Double(Type):
    pass


class String(Type):
    pass


class ByteBuffer(Type):
    pass


class CustomType(Type):

    def __init__(self, name):
        self.name = name


class ComplexType(Type):
    __metaclass__ = ABCMeta


class Enumeration(ComplexType):

    def __init__(self, name, enumerators=None, extends=None, flags=None):
        self.name = name
        self.enumerators = enumerators if enumerators else []
        self.extends = extends
        self.flags = flags if flags else []         # Unused


class Enumerator(object):

    def __init__(self, name, value=None):
        self.name = name
        self.value = value


class Struct(ComplexType):

    def __init__(self, name, fields=None, extends=None, flags=None):
        self.name = name
        self.fields = fields if fields else []
        self.extends = extends
        self.flags = flags if flags else []


class StructField(object):

    def __init__(self, name, field_type):
        self.name = name
        self.type = field_type


class Array(ComplexType):

    def __init__(self, name, element_type):
        self.name = name            # None for implicit arrays.
        self.type = element_type


class Map(ComplexType):
    pass


class Interface(object):

    def __init__(self, name, flags=None, version=None, attributes=None,
                 methods=None, broadcasts=None, extends=None):
        self.package = None
        self.name = name
        self.flags = flags if flags else []         # Unused
        self.version = version
        self.attributes = attributes if attributes else []
        self.methods = methods if methods else []
        self.broadcasts = broadcasts if broadcasts else []
        self.extends = extends

        self.typedefs = []
        self.enumerations = []
        self.structs = []
        self.arrays = []
        self.maps = []


class Version(object):

    def __init__(self, major, minor):
        self.major = major
        self.minor = minor


class Attribute(object):

    def __init__(self, name, attr_type, flags=None):
        self.name = name
        self.type = attr_type
        self.flags = flags if flags else []


class Method(object):

    def __init__(self, name, flags=None,
                 in_args=None, out_args=None, errors=None):
        self.name = name
        self.flags = flags if flags else []
        self.in_args = in_args if in_args else []
        self.out_args = out_args if out_args else []
        self.errors = errors if errors else []


class Broadcast(object):

    def __init__(self, name, flags=None, out_args=None):
        self.name = name
        self.flags = flags if flags else []
        self.out_args = out_args if out_args else []


class Argument(object):

    def __init__(self, name, arg_type):
        self.name = name
        self.type = arg_type
