
from abc import ABCMeta
from collections import OrderedDict


class Package(object):
    """
    AST representation of a Franca package.
    """

    def __init__(self, name, file_name=None, imports=None,
                 interfaces=None, typecollections=None):
        """
        Constructs a new Package.
        """
        self.name = name
        self.file = file_name
        self.imports = imports if imports else []
        self.interfaces = interfaces if interfaces else OrderedDict()
        self.typecollections = typecollections if typecollections else \
            OrderedDict()

        for item in self.interfaces.values():
            item.package = self
        for item in self.typecollections.values():
            item.package = self


class Import(object):

    def __init__(self, file_name, namespace=None):
        self.file = file_name
        self.namespace = namespace          # None for "import model"


class Namespace(object):

    __metaclass__ = ABCMeta

    def __init__(self, name, flags=None, version=None, typedefs=None,
                 enumerations=None, structs=None, arrays=None, maps=None):
        self.package = None
        self.name = name
        self.flags = flags if flags else []         # Unused
        self.version = version
        self.typedefs = typedefs if typedefs else OrderedDict()
        self.enumerations = enumerations if enumerations else OrderedDict()
        self.structs = structs if structs else OrderedDict()
        self.arrays = arrays if arrays else OrderedDict()
        self.maps = maps if maps else OrderedDict()

        for item in self.typedefs.values():
            item.namespace = self
        for item in self.enumerations.values():
            item.namespace = self
        for item in self.structs.values():
            item.namespace = self
        for item in self.arrays.values():
            item.namespace = self
        for item in self.maps.values():
            item.namespace = self


class TypeCollection(Namespace):

    def __init__(self, name, flags=None, version=None, typedefs=None,
                 enumerations=None, structs=None, arrays=None, maps=None):
        super(TypeCollection, self).__init__(name, flags=flags, version=version,
                                             typedefs=typedefs,
                                             enumerations=enumerations,
                                             structs=structs, arrays=arrays,
                                             maps=maps)


class Typedef(object):

    def __init__(self, name, base_type):
        self.namespace = None
        self.name = name
        self.type = base_type


class Type(object):

    __metaclass__ = ABCMeta

    def __init__(self):
        self.name = self.__class__.__name__


class PrimitiveType(Type):

    __metaclass__ = ABCMeta

    def __init__(self):
        super(PrimitiveType, self).__init__()


class Int8(PrimitiveType):

    def __init__(self):
        super(Int8, self).__init__()


class Int16(PrimitiveType):

    def __init__(self):
        super(Int16, self).__init__()


class Int32(PrimitiveType):

    def __init__(self):
        super(Int32, self).__init__()


class Int64(PrimitiveType):

    def __init__(self):
        super(Int64, self).__init__()


class UInt8(PrimitiveType):

    def __init__(self):
        super(UInt8, self).__init__()


class UInt16(PrimitiveType):

    def __init__(self):
        super(UInt16, self).__init__()


class UInt32(PrimitiveType):

    def __init__(self):
        super(UInt32, self).__init__()


class UInt64(PrimitiveType):

    def __init__(self):
        super(UInt64, self).__init__()


class Boolean(PrimitiveType):

    def __init__(self):
        super(Boolean, self).__init__()


class Float(PrimitiveType):

    def __init__(self):
        super(Float, self).__init__()


class Double(PrimitiveType):

    def __init__(self):
        super(Double, self).__init__()


class String(PrimitiveType):

    def __init__(self):
        super(String, self).__init__()


class ByteBuffer(PrimitiveType):

    def __init__(self):
        super(ByteBuffer, self).__init__()


class ComplexType(Type):

    __metaclass__ = ABCMeta

    def __init__(self):
        super(ComplexType, self).__init__()
        self.namespace = None


class Enumeration(ComplexType):

    def __init__(self, name, enumerators=None, extends=None, flags=None):
        super(Enumeration, self).__init__()
        self.name = name
        self.enumerators = enumerators if enumerators else OrderedDict()
        self.extends = extends
        self.flags = flags if flags else []         # Unused


class Enumerator(object):

    def __init__(self, name, value=None):
        self.name = name
        self.value = value


class Struct(ComplexType):

    def __init__(self, name, fields=None, extends=None, flags=None):
        super(Struct, self).__init__()
        self.name = name
        self.fields = fields if fields else OrderedDict()
        self.extends = extends
        self.flags = flags if flags else []


class StructField(object):

    def __init__(self, name, field_type):
        self.name = name
        self.type = field_type


class Array(ComplexType):

    def __init__(self, name, element_type):
        super(Array, self).__init__()
        self.name = name            # None for implicit arrays.
        self.type = element_type


class Map(ComplexType):

    def __init__(self, name, key_type, value_type):
        super(Map, self).__init__()
        self.name = name
        self.key_type = key_type
        self.value_type = value_type


class CustomType(Type):

    def __init__(self, name):
        super(CustomType, self).__init__()
        self.name = name
        self.reference = None


class Interface(Namespace):

    def __init__(self, name, flags=None, version=None, attributes=None,
                 methods=None, broadcasts=None, extends=None):
        super(Interface, self).__init__(name=name, flags=flags, version=version)
        self.attributes = attributes if attributes else OrderedDict()
        self.methods = methods if methods else OrderedDict()
        self.broadcasts = broadcasts if broadcasts else OrderedDict()
        self.extends = extends

        for item in self.attributes.values():
            item.namespace = self
        for item in self.methods.values():
            item.namespace = self
        for item in self.broadcasts.values():
            item.namespace = self


class Version(object):

    def __init__(self, major, minor):
        self.major = major
        self.minor = minor


class Attribute(object):

    def __init__(self, name, attr_type, flags=None):
        self.namespace = None
        self.name = name
        self.type = attr_type
        self.flags = flags if flags else []


class Method(object):

    def __init__(self, name, flags=None,
                 in_args=None, out_args=None, errors=None):
        self.namespace = None
        self.name = name
        self.flags = flags if flags else []
        self.in_args = in_args if in_args else OrderedDict()
        self.out_args = out_args if out_args else OrderedDict()
        # Errors can be an OrderedDict() or a CustomType enumeration reference.
        self.errors = errors if errors else OrderedDict()


class Broadcast(object):

    def __init__(self, name, flags=None, out_args=None):
        self.namespace = None
        self.name = name
        self.flags = flags if flags else []
        self.out_args = out_args if out_args else OrderedDict()


class Argument(object):

    def __init__(self, name, arg_type):
        self.name = name
        self.type = arg_type
