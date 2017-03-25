"""
Franca lexer.
"""

import ply.lex as lex


class LexerException(Exception):

    def __init__(self, message):
        super(LexerException, self).__init__()
        self.message = message

    def __str__(self):
        return self.message


class Lexer(object):
    """
    Franca IDL PLY lexer.
    """

    # Keywords
    keywords = [
        "package",
        "import",
        "from",
        "model",
        "typeCollection",
        "version",
        "major",
        "minor",
        "typedef",
        "is",
        "interface",
        "attribute",
        "readonly",
        "noSubscriptions",
        "method",
        "fireAndForget",
        "in",
        "out",
        "error",
        "broadcast",
        "selective",
        "enumeration",
        "extends",
        "struct",
        "union",
        "polymorphic",
        "array",
        "of",
        "map",
        "to",
        "const",


        # Types
        "Int8",
        "Int16",
        "Int32",
        "Int64",
        "UInt8",
        "UInt16",
        "UInt32",
        "UInt64",
        "Boolean",
        "Float",
        "Double",
        "String",
        "ByteBuffer",
    ]

    # Tokens
    tokens = [keyword.upper() for keyword in keywords] + [
        "ID",
        "INTEGER",
        "FILE_NAME",
        "DOUBLE_VAL",
        "FLOAT_VAL",
        "STRING_VAL",
        "BOOLEAN_VAL"
    ]

    # Ignored characters
    t_ignore = " \t"

    # Literals
    literals = [".", "{", "}", "*", "=", "[", "]"]

    # Identifiers and keywords
    _keyword_map = {}
    for keyword in keywords:
        _keyword_map[keyword] = keyword.upper()

    # Newlines
    # noinspection PyPep8Naming,PyIncorrectDocstring
    @staticmethod
    def t_NEWLINE(t):
        # noinspection PySingleQuotedDocstring
        r"\n+"
        t.lexer.lineno += t.value.count("\n")

    # Line comments
    # noinspection PyPep8Naming,PyIncorrectDocstring
    @staticmethod
    def t_LINE_COMMENT(t):
        # noinspection PySingleQuotedDocstring
        r"\/\/[^\r\n]*"
        t.lexer.lineno += t.value.count("\n")

    # Block comments
    # noinspection PyPep8Naming,PyIncorrectDocstring
    @staticmethod
    def t_BLOCK_COMMENT(t):
        # noinspection PySingleQuotedDocstring
        r"/\*(.|\n)*?\*/"
        t.lexer.lineno += t.value.count("\n")

    # Structured comments
    # noinspection PyPep8Naming,PyIncorrectDocstring
    @staticmethod
    def t_STRUCTURED_COMMENT(t):
        # noinspection PySingleQuotedDocstring
        r"<\*\*(.|\n)*?\*\*>"
        t.lexer.lineno += t.value.count("\n")

    # File name (quoted)
    # noinspection PyPep8Naming,PyIncorrectDocstring
    @staticmethod
    def t_FILE_NAME(t):
        # noinspection PySingleQuotedDocstring
        r"\"([^\n]|\.)*?\""
        t.value = t.value[1:-1]
        return t

    # noinspection PyPep8Naming,PyIncorrectDocstring
    @staticmethod
    def t_STRING_VAL(t):
        # noinspection PySingleQuotedDocstring
        r"\"[^\"]*\""
        t.value = t.value.replace("\"", '')
        t.value = str(t.value)
        return t

    # noinspection PyPep8Naming,PyIncorrectDocstring
    @staticmethod
    def t_FLOAT_VAL(t):
        # noinspection PySingleQuotedDocstring
        # r"[-+]?(\d+)?(\.(\d+)?([eE][-+]?\d+)?|[eE][-+]?\d+)[f]"
        # currently valid float string without leading digits (.043f) are not supported
        # result in conflict with text like org.franca... matche ".f" --> need to improve regex
        r"[-+]?(\d+)(\.(\d+)?([eE][-+]?\d+)?|[eE][-+]?\d+)[f]"
        t.value = t.value.replace("f", '')
        t.value = float(t.value)
        return t

    # noinspection PyPep8Naming,PyIncorrectDocstring
    @staticmethod
    def t_DOUBLE_VAL(t):
        # noinspection PySingleQuotedDocstring

        # r"[-+]?(\d+)?(\.(\d+)?([eE][-+]?\d+)?|[eE][-+]?\d+)[d]"
        # currently valid float string without leading digits (.043f) are not supported
        # result in conflict with text like org.franca... matche ".f" --> need to improve regex
        r"[-+]?(\d+)(\.(\d+)?([eE][-+]?\d+)?|[eE][-+]?\d+)[d]"
        t.value = t.value.replace("d", '')
        t.value = float(t.value)
        return t

    # noinspection PyPep8Naming,PyIncorrectDocstring
    @staticmethod
    def t_INTEGER(t):
        # noinspection PySingleQuotedDocstring
        r"[+-]?\d+"
        t.value = int(t.value)
        return t


    # noinspection PyPep8Naming,PyIncorrectDocstring
    @staticmethod
    def t_BOOLEAN_VAL(t):
        # noinspection PySingleQuotedDocstring
        r"(true|false)"
        t.value = t.value.strip()
        if t.value == "true":
            t.value = True
        else:
            t.value = False
        return t

    # Identifier
    # noinspection PyPep8Naming,PyIncorrectDocstring
    @staticmethod
    def t_ID(t):
        # noinspection PySingleQuotedDocstring
        r"[A-Za-z][A-Za-z0-9_]*"
        t.type = Lexer._keyword_map.get(t.value, "ID")
        return t

    @staticmethod
    def t_error(t):
        raise LexerException("Illegal character '{}' at line {}.".format(
                             t.value[0], t.lineno))

    def __init__(self, **kwargs):
        """
        Constructor.
        """
        self.lexer = lex.lex(module=self, **kwargs)

    def tokenize(self, data):
        """
        Tokenize input data to stdout for testing purposes.

        :param data: Input text to parse.
        """
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(tok)

    def tokenize_data(self, data):
        """
        Tokenize input data to stdout for testing purposes.

        :param data: Input text to parse.
        """
        self.lexer.input(data)
        tokenized_data = []
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            tokenized_data.append(tok)
        return tokenized_data

    def tokenize_file(self, fspec):
        """
        Tokenize input file to stdout for testing purposes.

        :param fspec: Input file to parse.
        """
        with open(fspec, "r") as f:
            data = f.read()
        return self.tokenize(data)
