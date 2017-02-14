
from abc import ABCMeta
from collections import OrderedDict


class ASTException(Exception):

    def __init__(self, message):
        super(ASTException, self).__init__()
        self.message = message

    def __str__(self):
        return self.message


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

    def __init__(self, name, flags=None, members=None):
        self.package = None
        self.name = name
        self.flags = flags if flags else []         # Unused
        self.version = None
        self.typedefs = OrderedDict()
        self.enumerations = OrderedDict()
        self.structs = OrderedDict()
        self.arrays = OrderedDict()
        self.maps = OrderedDict()
        if members:
            for member in members:
                self._add_member(member)

    def __contains__(self, item):
        res = item in self.typedefs or \
              item in self.enumerations or \
              item in self.structs or \
              item in self.arrays or \
              item in self.maps
        return res

    def _add_member(self, member):
        if isinstance(member, Version):
            if not self.version:
                self.version = member
            else:
                raise ASTException("Multiple version definitions.")
        elif isinstance(member, Type):
            if member.name in self:
                raise ASTException("Duplicate namespace member "
                                   "\"{}\".".format(member.name))
            if isinstance(member, Typedef):
                self.typedefs[member.name] = member
            elif isinstance(member, Enumeration):
                self.enumerations[member.name] = member
            elif isinstance(member, Struct):
                self.structs[member.name] = member
            elif isinstance(member, Array):
                self.arrays[member.name] = member
            elif isinstance(member, Map):
                self.maps[member.name] = member
            else:
                raise ASTException("Unexpected namespace member type.")
            member.namespace = self
        else:
            raise ValueError("Unexpected namespace member type.")


class TypeCollection(Namespace):

    def __init__(self, name, flags=None, members=None):
        super(TypeCollection, self).__init__(name, flags=flags,
                                             members=members)


class Type(object):

    __metaclass__ = ABCMeta

    def __init__(self, name=None):
        self.namespace = None
        self.name = name if name else self.__class__.__name__


class Typedef(Type):

    def __init__(self, name, base_type):
        super(Typedef, self).__init__(name)
        self.type = base_type


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


class Reference(Type):

    def __init__(self, name):
        super(Reference, self).__init__()
        self.name = name
        self.reference = None


class Interface(Namespace):

    def __init__(self, name, flags=None, members=None, extends=None):
        super(Interface, self).__init__(name=name, flags=flags, members=None)
        self.attributes = OrderedDict()
        self.methods = OrderedDict()
        self.broadcasts = OrderedDict()
        self.extends = extends
        if members:
            for member in members:
                self._add_member(member)

    def __contains__(self, item):
        res = super(Interface, self).__contains__(item) or \
              item in self.attributes or \
              item in self.methods or \
              item in self.broadcasts
        return res

    def _add_member(self, member):
        if isinstance(member, Type):
            if member.name in self:
                raise ASTException("Duplicate namespace member "
                                   "\"{}\".".format(member.name))
            if isinstance(member, Attribute):
                self.attributes[member.name] = member
            elif isinstance(member, Method):
                self.methods[member.name] = member
            elif isinstance(member, Broadcast):
                self.broadcasts[member.name] = member
            else:
                super(Interface, self)._add_member(member)
            member.namespace = self
        else:
            super(Interface, self)._add_member(member)


class Version(object):

    def __init__(self, major, minor):
        self.major = major
        self.minor = minor

    def __str__(self):
        return "{}.{}".format(self.major, self.minor)


class Attribute(Type):

    def __init__(self, name, attr_type, flags=None):
        super(Attribute, self).__init__(name)
        self.type = attr_type
        self.flags = flags if flags else []


class Method(Type):

    def __init__(self, name, flags=None,
                 in_args=None, out_args=None, errors=None):
        super(Method, self).__init__(name)
        self.flags = flags if flags else []
        self.in_args = in_args if in_args else OrderedDict()
        self.out_args = out_args if out_args else OrderedDict()
        # Errors can be an OrderedDict() or a Reference to an enumeration.
        self.errors = errors if errors else OrderedDict()


class Broadcast(Type):

    def __init__(self, name, flags=None, out_args=None):
        super(Broadcast, self).__init__(name)
        self.flags = flags if flags else []
        self.out_args = out_args if out_args else OrderedDict()


class Argument(object):

    def __init__(self, name, arg_type):
        self.name = name
        self.type = arg_type
