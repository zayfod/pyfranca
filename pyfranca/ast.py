
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

    def __init__(self, file, namespace=None):
        self.file = file
        self.namespace = namespace


class TypeCollection(object):

    def __init__(self, name, ver=None, members=None):
        self.name = name
        self.ver = ver
        self.members = members if members else []


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

    def __init__(self, name, enumerators=None, extends=None):
        self.name = name
        self.enumerators = enumerators if enumerators else []
        self.extends = extends


class Enumerator(object):

    def __init__(self, name, value=None):
        self.name = name
        self.value = value


class Struct(ComplexType):

    def __init__(self, name, fields=None, extends=None):
        self.name = name
        self.fields = fields if fields else []
        self.extends = extends


class StructField(object):

    def __init__(self, name, field_type):
        self.name = name
        self.type = field_type


class Array(ComplexType):
    pass


class Map(ComplexType):
    pass


class Interface(object):

    def __init__(self, name, ver=None, attributes=None,
                 methods=None, broadcasts=None, extends=None):
        self.package = None
        self.name = name
        self.version = ver
        self.attributes = attributes if attributes else []
        self.methods = methods if methods else []
        self.broadcasts = broadcasts if broadcasts else []
        self.extends = extends


class Version(object):

    def __init__(self, major, minor):
        self.major = major
        self.minor = minor


class Attribute(object):

    def __init__(self, name, attr_type):
        self.name = name
        self.type = attr_type


class Method(object):

    def __init__(self, name, in_args=None, out_args=None):
        self.name = name
        self.in_args = in_args if in_args else []
        self.out_args = out_args if out_args else []


class Broadcast(object):

    def __init__(self, name, out_args=None):
        self.name = name
        self.out_args = out_args if out_args else []


class Argument(object):

    def __init__(self, name, arg_type):
        self.name = name
        self.type = arg_type
