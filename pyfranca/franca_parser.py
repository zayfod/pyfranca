"""
Franca parser.
"""

from collections import OrderedDict
from abc import ABCMeta
import ply.yacc as yacc
from pyfranca import franca_lexer
from pyfranca import ast


class ArgumentGroup(object):

    __metaclass__ = ABCMeta

    def __init__(self, arguments=None):
        self.arguments = arguments if arguments else OrderedDict()


class InArgumentGroup(ArgumentGroup):
    pass


class OutArgumentGroup(ArgumentGroup):
    pass


class ErrorArgumentGroup(ArgumentGroup):
    pass


class ParserException(Exception):

    def __init__(self, message):
        super(ParserException, self).__init__()
        self.message = message

    def __str__(self):
        return self.message


class Parser(object):
    """
    Franca IDL PLY parser.
    """

    @staticmethod
    def _package_def(members):
        imports = []
        interfaces = OrderedDict()
        typecollections = OrderedDict()
        if members:
            for member in members:
                if isinstance(member, ast.Import):
                    imports.append(member)
                elif isinstance(member, ast.Interface):
                    interfaces[member.name] = member
                elif isinstance(member, ast.TypeCollection):
                    typecollections[member.name] = member
                else:
                    raise ParserException("Unexpected package member type.")
        return imports, interfaces, typecollections

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_package_def(p):
        """
        package_def : PACKAGE fqn defs
        """
        imports, interfaces, typecollections = Parser._package_def(p[3])
        p[0] = ast.Package(name=p[2], file_name=None, imports=imports,
                           interfaces=interfaces,
                           typecollections=typecollections)

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_defs_1(p):
        """
        defs : defs def
        """
        p[0] = p[1]
        p[0].append(p[2])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_defs_2(p):
        """
        defs : def
        """
        p[0] = [p[1]]

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_defs_3(p):
        """
        defs : empty
        """

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_fqn_1(p):
        """
        fqn : ID '.' fqn
        """
        p[0] = "{}.{}".format(p[1], p[3])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_fqn_2(p):
        """
        fqn : ID
        """
        p[0] = p[1]

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_fqn_3(p):
        """
        fqn : '*'
        """
        p[0] = p[1]

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_import_def_1(p):
        """
        def : IMPORT fqn FROM FILE_NAME
        """
        p[0] = ast.Import(file_name=p[4], namespace=p[2])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_import_def_2(p):
        """
        def : IMPORT MODEL FILE_NAME
        """
        p[0] = ast.Import(file_name=p[3])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_typecollection(p):
        """
        def : TYPECOLLECTION ID '{' typecollection_members '}'
        """
        try:
            p[0] = ast.TypeCollection(name=p[2], flags=None, members=p[4])
        except ast.ASTException as e:
            raise ParserException(e.message)

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_typecollection_members_1(p):
        """
        typecollection_members : typecollection_members typecollection_member
        """
        p[0] = p[1]
        p[0].append(p[2])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_typecollection_members_2(p):
        """
        typecollection_members : typecollection_member
        """
        p[0] = [p[1]]

    # noinspection PyUnusedLocal, PyIncorrectDocstring
    @staticmethod
    def p_typecollection_members_3(p):
        """
        typecollection_members : empty
        """
        pass

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_typecollection_member(p):
        """
        typecollection_member : version_def
                              | type_def
                              | enumeration_def
                              | struct_def
                              | array_def
                              | map_def
                              | constant_def
        """
        p[0] = p[1]

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_version_def(p):
        """
        version_def : VERSION '{' MAJOR INTEGER MINOR INTEGER '}'
        """
        p[0] = ast.Version(major=p[4], minor=p[6])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_type_def(p):
        """
        type_def : TYPEDEF ID IS type
        """
        p[0] = ast.Typedef(name=p[2], base_type=p[4])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_interface_1(p):
        """
        def : INTERFACE ID '{' interface_members '}'
        """
        try:
            p[0] = ast.Interface(name=p[2], flags=None, members=p[4],
                                 extends=None)
        except ast.ASTException as e:
            raise ParserException(e.message)

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_interface_2(p):
        """
        def : INTERFACE ID EXTENDS fqn '{' interface_members '}'
        """
        try:
            p[0] = ast.Interface(name=p[2], flags=None, members=p[6],
                                 extends=p[4])
        except ast.ASTException as e:
            raise ParserException(e.message)

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_interface_members_1(p):
        """
        interface_members : interface_members interface_member
        """
        p[0] = p[1]
        p[0].append(p[2])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_interface_members_2(p):
        """
        interface_members : interface_member
        """
        p[0] = [p[1]]

    # noinspection PyUnusedLocal, PyIncorrectDocstring
    @staticmethod
    def p_interface_members_3(p):
        """
        interface_members : empty
        """
        pass

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_interface_member(p):
        """
        interface_member : version_def
                         | attribute_def
                         | method_def
                         | broadcast_def
                         | type_def
                         | enumeration_def
                         | struct_def
                         | array_def
                         | map_def
                         | constant_def
        """
        p[0] = p[1]

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_attribute_def(p):
        """
        attribute_def : ATTRIBUTE type ID flag_defs
        """
        p[0] = ast.Attribute(name=p[3], attr_type=p[2], flags=p[4])

    @staticmethod
    def _method_def(arg_groups):
        in_args = None
        out_args = None
        errors = None
        if arg_groups:
            for arg_group in arg_groups:
                if isinstance(arg_group, InArgumentGroup):
                    if not in_args:
                        in_args = arg_group.arguments
                    else:
                        raise ParserException("Multiple in argument "
                                              "definitions for a method.")
                elif isinstance(arg_group, OutArgumentGroup):
                    if not out_args:
                        out_args = arg_group.arguments
                    else:
                        raise ParserException("Multiple out argument "
                                              "definitions for a method.")
                elif isinstance(arg_group, ErrorArgumentGroup):
                    if not errors:
                        errors = arg_group.arguments
                    else:
                        raise ParserException("Multiple error definitions "
                                              "for a method.")
                else:
                    raise ParserException("Unexpected method definition "
                                          "member.")
        return in_args, out_args, errors

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_method_def(p):
        """
        method_def : METHOD ID flag_defs '{' arg_group_defs '}'
        """
        in_args, out_args, errors = Parser._method_def(p[5])
        p[0] = ast.Method(name=p[2], flags=p[3],
                          in_args=in_args, out_args=out_args, errors=errors)

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_flag_defs_1(p):
        """
        flag_defs : flag_defs flag_def
        """
        p[0] = p[1]
        p[0].append(p[2])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_flag_defs_2(p):
        """
        flag_defs : flag_def
        """
        p[0] = [p[1]]

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_flag_defs_3(p):
        """
        flag_defs : empty
        """
        pass

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_flag_def(p):
        """
        flag_def : SELECTIVE
                 | FIREANDFORGET
                 | POLYMORPHIC
                 | NOSUBSCRIPTIONS
                 | READONLY
        """
        p[0] = p[1]

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_arg_group_defs_1(p):
        """
        arg_group_defs : arg_group_defs arg_group_def
        """
        p[0] = p[1]
        p[0].append(p[2])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_arg_group_defs_2(p):
        """
        arg_group_defs : arg_group_def
        """
        p[0] = [p[1]]

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_arg_group_defs_3(p):
        """
        arg_group_defs : empty
        """
        pass

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_arg_group_def_1(p):
        """
        arg_group_def : IN '{' arg_defs '}'
        """
        p[0] = InArgumentGroup(p[3])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_arg_group_def_2(p):
        """
        arg_group_def : OUT '{' arg_defs '}'
        """
        p[0] = OutArgumentGroup(p[3])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_arg_group_def_3(p):
        """
        arg_group_def : ERROR '{' enumerators '}'
        """
        p[0] = ErrorArgumentGroup(p[3])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_arg_group_def_4(p):
        """
        arg_group_def : ERROR type
        """
        p[0] = ErrorArgumentGroup(p[2])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_broadcast_def(p):
        """
        broadcast_def : BROADCAST ID flag_defs '{' arg_group_defs '}'
        """
        in_args, out_args, errors = Parser._method_def(p[5])
        if in_args or errors:
            raise ParserException("In arguments and errors cannot be part "
                                  "of a broadcast definition.")
        p[0] = ast.Broadcast(name=p[2], flags=p[3], out_args=out_args)

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_arg_defs_1(p):
        """
        arg_defs : arg_defs arg_def
        """
        p[0] = p[1]
        if p[2].name not in p[0]:
            p[0][p[2].name] = p[2]
        else:
            raise ParserException("Duplicate argument '{}'.".format(p[2].name))

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_arg_defs_2(p):
        """
        arg_defs : arg_def
        """
        p[0] = OrderedDict()
        p[0][p[1].name] = p[1]

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_arg_def(p):
        """
        arg_def : type ID
        """
        p[0] = ast.Argument(name=p[2], arg_type=p[1])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_enumeration_def_1(p):
        """
        enumeration_def : ENUMERATION ID '{' enumerators '}'
        """
        p[0] = ast.Enumeration(name=p[2], enumerators=p[4])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_enumeration_def_2(p):
        """
        enumeration_def : ENUMERATION ID EXTENDS fqn '{' enumerators '}'
        """
        p[0] = ast.Enumeration(name=p[2], enumerators=p[6], extends=p[4])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_enumerators_1(p):
        """
        enumerators : enumerators enumerator
        """
        p[0] = p[1]
        if p[2].name not in p[0]:
            p[0][p[2].name] = p[2]
        else:
            raise ParserException(
                "Duplicate enumerator '{}'.".format(p[2].name))

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_enumerators_2(p):
        """
        enumerators : enumerator
        """
        p[0] = OrderedDict()
        p[0][p[1].name] = p[1]

    # noinspection PyUnusedLocal, PyIncorrectDocstring
    @staticmethod
    def p_enumerators_3(p):
        """
        enumerators : empty
        """
        pass

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_enumerator_1(p):
        """
        enumerator : ID
        """
        p[0] = ast.Enumerator(name=p[1])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_enumerator_2(p):
        """
        enumerator : ID '=' INTEGER
        """
        p[0] = ast.Enumerator(name=p[1], value=p[3])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_struct_def_1(p):
        """
        struct_def : STRUCT ID flag_defs '{' struct_fields '}'
        """
        p[0] = ast.Struct(name=p[2], fields=p[5], flags=p[3])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_struct_def_2(p):
        """
        struct_def : STRUCT ID EXTENDS fqn '{' struct_fields '}'
        """
        p[0] = ast.Struct(name=p[2], fields=p[6], extends=p[4])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_struct_fields_1(p):
        """
        struct_fields : struct_fields struct_field
        """
        p[0] = p[1]
        if p[2].name not in p[0]:
            p[0][p[2].name] = p[2]
        else:
            raise ParserException(
                "Duplicate structure field '{}'.".format(p[2].name))

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_struct_fields_2(p):
        """
        struct_fields : struct_field
        """
        p[0] = OrderedDict()
        p[0][p[1].name] = p[1]

    # noinspection PyUnusedLocal, PyIncorrectDocstring
    @staticmethod
    def p_struct_fields_3(p):
        """
        struct_fields : empty
        """
        pass

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_struct_field_1(p):
        """
        struct_field : type ID
        """
        p[0] = ast.StructField(name=p[2], field_type=p[1])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_array_def(p):
        """
        array_def : ARRAY ID OF type
        """
        p[0] = ast.Array(name=p[2], element_type=p[4])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_map_def(p):
        """
        map_def : MAP ID '{' type TO type '}'
        """
        p[0] = ast.Map(name=p[2], key_type=p[4], value_type=p[6])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_constant_def(p):
        """
        constant_def : CONST type ID '=' INTEGER
        """
        p[0] = ast.Constant(name=p[3], element_type=p[2], element_value=p[5])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_constant_def_1(p):
        """
        constant_def : CONST type ID '=' real
        """
        p[0] = ast.Constant(name=p[3], element_type=p[2], element_value=p[5])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_constant_def_2(p):
        """
        constant_def : CONST type ID '=' boolean
        """
        p[0] = ast.Constant(name=p[3], element_type=p[2], element_value=p[5])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_constant_def_3(p):
        """
        constant_def : CONST type ID '=' string
        """
        p[0] = ast.Constant(name=p[3], element_type=p[2], element_value=p[5])


    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_type_1(p):
        """
        type : INT8
             | INT16
             | INT32
             | INT64
             | UINT8
             | UINT16
             | UINT32
             | UINT64
             | BOOLEAN
             | FLOAT
             | DOUBLE
             | STRING
             | BYTEBUFFER
        """
        type_class = getattr(ast, p[1])
        p[0] = type_class()

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_type_2(p):
        """
        type : INT8 '[' ']'
             | INT16 '[' ']'
             | INT32 '[' ']'
             | INT64 '[' ']'
             | UINT8 '[' ']'
             | UINT16 '[' ']'
             | UINT32 '[' ']'
             | UINT64 '[' ']'
             | BOOLEAN '[' ']'
             | FLOAT '[' ']'
             | DOUBLE '[' ']'
             | STRING '[' ']'
             | BYTEBUFFER '[' ']'
        """
        type_class = getattr(ast, p[1])
        p[0] = ast.Array(name=None, element_type=type_class())

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_type_3(p):
        """
        type : fqn
        """
        p[0] = ast.Reference(name=p[1])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_type_4(p):
        """
        type : fqn '[' ']'
        """
        element_type = ast.Reference(name=p[1])
        p[0] = ast.Array(name=None, element_type=element_type)

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_real(p):
        """
        real : INTEGER '.' INTEGER ID
        """
        6.054 = wird abgeschnitten
        if p[4][0] == 'd' or p[4][0] == 'f':
            p[0] = float(str(p[1]) + "." + str(p[3]))
        elif p[4][0] == 'e':
            p[4] = p[4].replace("f", '')
            p[4] = p[4].replace("d", '')
            p[0] = float(str(p[1]) + "." + str(p[3]) + str(p[4]))
        else:
            raise ParserException("Syntax error at line {} near '{}'.".format(
                p.lineno, p.value))

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_boolean(p):
        """
        boolean : TRUE
                | FALSE
        """
        if p[1] == "true":
            p[0] = True
        elif p[1] == "false":
            p[0] = False
        else:
            raise ParserException("Syntax error in boolean constant at line {} near '{}'.".format(
                p.lineno, p.value))

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_string(p):
        """
        string : '\"' ID '\"'
        """
        p[0] = p[2]

    # noinspection PyUnusedLocal, PyIncorrectDocstring
    @staticmethod
    def p_empty(p):
        """
        empty :
        """
        pass

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_error(p):
        if p:
            raise ParserException("Syntax error at line {} near '{}'.".format(
                                  p.lineno, p.value))
        else:
            raise ParserException("Reached unexpected end of file.")

    def __init__(self, the_lexer=None, **kwargs):
        """
        Constructor.

        :param lexer: a lexer object to use.
        """
        if not the_lexer:
            the_lexer = franca_lexer.Lexer()
        self._lexer = the_lexer
        self.tokens = self._lexer.tokens
        # Disable debugging, by default.
        if "debug" not in kwargs:
            kwargs["debug"] = False
        if "write_tables" not in kwargs:
            kwargs["write_tables"] = False
        self._parser = yacc.yacc(module=self, **kwargs)

    def parse(self, fidl):
        """
        Parse input text

        :param fidl: Input text to parse.
        :return: AST representation of the input.
        """
        package = self._parser.parse(fidl)
        return package

    def parse_file(self, fspec):
        """
        Parse input file

        :param fspec: Specification of a fidl to parse.
        :return: AST representation of the input.
        """
        with open(fspec, "r") as f:
            fidl = f.read()
        package = self.parse(fidl)
        if package:
            package.file = fspec
        return package
