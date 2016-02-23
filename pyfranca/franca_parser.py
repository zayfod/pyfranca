
import ply.yacc as yacc
from pyfranca import franca_lexer


class Parser(object):
    """
    Franca IDL PLY parser.
    """

    # noinspection PyUnusedLocal,PyIncorrectDocstring
    @staticmethod
    def p_fidl(p):
        """
        fidl : fidl def
             | def
        """
        pass

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_package_def(p):
        """
        def : PACKAGE namespace
        """
        print "pd:", p[2]
        p[0] = p[2]

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_namespace_1(p):
        """
        namespace : ID '.' namespace
        """
        p[0] = "{}.{}".format(p[1], p[3])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_namespace_2(p):
        """
        namespace : ID
        """
        p[0] = p[1]

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_namespace_3(p):
        """
        namespace : '*'
        """
        p[0] = p[1]

    # noinspection PyIncorrectDocstring
    # TODO: Support for "import model"
    @staticmethod
    def p_import_def(p):
        """
        def : IMPORT namespace FROM FILE_NAME
        """
        print "import:", p[2], p[4]

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_type_collection(p):
        """
        def : TYPECOLLECTION ID '{' type_collection_members '}'
        """
        print "tc:", p[2]

    # noinspection PyUnusedLocal, PyIncorrectDocstring
    @staticmethod
    def p_type_collection_members(p):
        """
        type_collection_members : type_collection_members type_collection_member
                                | type_collection_member
        """
        pass

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_type_collection_member_1(p):
        """
        type_collection_member : version_def
        """
        print "tc version:", p[1]

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_type_collection_member_2(p):
        """
        type_collection_member : type_def
        """
        print "tc type:", p[1]

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_type_collection_member_3(p):
        """
        type_collection_member : enumeration_def
        """
        print "tc enumeration:", p[1]

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_type_collection_member_4(p):
        """
        type_collection_member : struct_def
        """
        print "tc struct:", p[1]

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_version_def(p):
        """
        version_def : VERSION '{' MAJOR INTEGER MINOR INTEGER '}'
        """
        p[0] = (p[4], p[6])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_type_def_1(p):
        """
        type_def : TYPEDEF ID IS ID
        """
        p[0] = (p[2], p[4])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_type_def_2(p):
        """
        type_def : TYPEDEF ID IS type
        """
        p[0] = (p[2], p[4])

    # noinspection PyIncorrectDocstring
    # TODO: support for "extends"
    # TODO: "interface elements can be arranged freely"
    @staticmethod
    def p_interface(p):
        """
        def : INTERFACE ID '{' \
                version_def \
                attribute_defs \
                method_defs \
                broadcast_defs \
                enumeration_defs \
              '}'
        """
        print "i:", p[2]

    # noinspection PyUnusedLocal, PyIncorrectDocstring
    @staticmethod
    def p_attribute_defs(p):
        """
        attribute_defs : attribute_defs attribute_def
                       | attribute_def
                       | empty
        """
        pass

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_attribute_def_1(p):
        """
        attribute_def : ATTRIBUTE type ID
        """
        p[0] = (p[2], p[3])
        print "i attr1:", p[0]

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_attribute_def_2(p):
        """
        attribute_def : ATTRIBUTE ID ID
        """
        p[0] = (p[2], p[3])
        print "i attr2:", p[0]

    # noinspection PyUnusedLocal, PyIncorrectDocstring
    @staticmethod
    def p_method_defs(p):
        """
        method_defs : method_defs method_def
                    | method_def
                    | empty
        """
        pass

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_method_def_1(p):
        """
        method_def : METHOD ID '{' '}'
        """
        print "method1:", p[2], [], []

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_method_def_2(p):
        """
        method_def : METHOD ID '{' \
                        IN '{' var_defs '}' \
                     '}'
        """
        print "method2:", p[2], p[6], []

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_method_def_3(p):
        """
        method_def : METHOD ID '{' \
                        OUT '{' var_defs '}' \
                     '}'
        """
        print "method3:", p[2], [], p[6]

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_method_def_4(p):
        """
        method_def : METHOD ID '{' \
                        IN '{' var_defs '}' \
                        OUT '{' var_defs '}' \
                     '}'
        """
        print "method4:", p[2], p[6], p[10]

    # noinspection PyUnusedLocal, PyIncorrectDocstring
    @staticmethod
    def p_broadcast_defs(p):
        """
        broadcast_defs : broadcast_defs broadcast_def
                       | broadcast_def
                       | empty
        """
        pass

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_broadcast_def(p):
        """
        broadcast_def : BROADCAST ID '{' \
                            OUT '{' var_defs '}' \
                        '}'
        """
        print "boardcast:", p[2], p[6]

    # noinspection PyUnusedLocal, PyIncorrectDocstring
    @staticmethod
    def p_enumeration_defs(p):
        """
        enumeration_defs : enumeration_defs enumeration_def
                         | enumeration_def
                         | empty
        """
        pass

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_var_defs_1(p):
        """
        var_defs : var_defs var_def
        """
        p[0] = p[1]
        p[0].append(p[2])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_var_defs_2(p):
        """
        var_defs : var_def
        """
        p[0] = [p[1]]

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_var_def_1(p):
        """
        var_def : type ID
        """
        p[0] = (p[1], p[2])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_var_def_2(p):
        """
        var_def : ID ID
        """
        p[0] = (p[1], p[2])

    # noinspection PyUnusedLocal, PyIncorrectDocstring
    @staticmethod
    def p_enumeration_def_1(p):
        """
        enumeration_def : ENUMERATION ID '{' enumeration_members '}'
        """
        p[0] = (p[2], None, p[4])

    # noinspection PyUnusedLocal, PyIncorrectDocstring
    @staticmethod
    def p_enumeration_def_2(p):
        """
        enumeration_def : ENUMERATION ID EXTENDS ID '{' enumeration_members '}'
        """
        p[0] = (p[2], p[4], p[6])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_enumeration_members_1(p):
        """
        enumeration_members : enumeration_members enumeration_member
        """
        p[0] = p[1]
        p[0].append(p[2])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_enumeration_members_2(p):
        """
        enumeration_members : enumeration_member
        """
        p[0] = [p[1]]

    # noinspection PyUnusedLocal, PyIncorrectDocstring
    @staticmethod
    def p_enumeration_members_3(p):
        """
        enumeration_members : empty
        """
        pass

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_enumeration_member_1(p):
        """
        enumeration_member : ID
        """
        p[0] = (p[1], None)

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_enumeration_member_2(p):
        """
        enumeration_member : ID '=' INTEGER
        """
        p[0] = (p[1], p[3])

    # noinspection PyUnusedLocal, PyIncorrectDocstring
    @staticmethod
    def p_struct_def(p):
        """
        struct_def : STRUCT ID '{' struct_members '}'
        """
        p[0] = (p[2], p[4])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_struct_members_1(p):
        """
        struct_members : struct_members struct_member
        """
        p[0] = p[1]
        p[0].append(p[2])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_struct_members_2(p):
        """
        struct_members : struct_member
        """
        p[0] = [p[1]]

    # noinspection PyUnusedLocal, PyIncorrectDocstring
    @staticmethod
    def p_struct_members_3(p):
        """
        struct_members : empty
        """
        pass

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_struct_member_1(p):
        """
        struct_member : type ID
        """
        p[0] = (p[1], p[2])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_struct_member_2(p):
        """
        struct_member : ID ID
        """
        p[0] = (p[1], p[2])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_type(p):
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
        p[0] = p[1]

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
        print("Syntax error at '%s'".format(p.value))

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

    def parse(self, data):
        """
        Parse input text

        :param data: Input text to parse.
        :return:
        """
        return self._parser.parse(data)
