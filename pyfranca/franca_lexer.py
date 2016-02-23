
import ply.lex as lex


class Lexer(object):
    """
    Franca IDL PLY lexer.
    """

    # Keywords
    keywords = [
        "package",
        "import",
        "from",
        "typeCollection",
        "version",
        "major",
        "minor",
        "typedef",
        "is",
        "interface",
        "attribute",
        "method",
        "in",
        "out",
        "broadcast",
        "enumeration",
        "extends",
        "struct",

        # Types
        "Int8", "Int16", "Int32", "Int64",
        "UInt8", "UInt16", "UInt32", "UInt64",
        "Boolean",
        "Float", "Double",
        "String",
        "ByteBuffer",
    ]

    # Tokens
    tokens = [keyword.upper() for keyword in keywords] + [
        "ID",
        "INTEGER",
        "FILE_NAME",
    ]

    # Ignored characters
    t_ignore = " \t"

    # Literals
    literals = [".", "{", "}", "*", "="]

    # Line comments
    t_ignore_LINE_COMMENT = r"\/\/[^\r\n]*"

    # File names
    t_FILE_NAME = r"\"([^\n]|\.)*?\""

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

    # Block comments
    # noinspection PyPep8Naming,PyIncorrectDocstring
    @staticmethod
    def t_BLOCK_COMMENT(t):
        # noinspection PySingleQuotedDocstring
        r"/\*(.|\n)*?\*/"
        t.lineno += t.value.count("\n")

    # Structured comments
    # noinspection PyPep8Naming,PyIncorrectDocstring
    @staticmethod
    def t_STRUCTURED_COMMENT(t):
        # noinspection PySingleQuotedDocstring
        r"<\*\*(.|\n)*?\*\*>"
        t.lineno += t.value.count("\n")

    # noinspection PyPep8Naming,PyIncorrectDocstring
    @staticmethod
    def t_ID(t):
        # noinspection PySingleQuotedDocstring
        r"[A-Za-z][A-Za-z0-9_]*"
        t.type = Lexer._keyword_map.get(t.value, "ID")
        return t

    # noinspection PyPep8Naming,PyIncorrectDocstring
    @staticmethod
    def t_INTEGER(t):
        # noinspection PySingleQuotedDocstring
        r"\d+"
        t.value = int(t.value)
        return t

    # noinspection PyIncorrectDocstring
    @staticmethod
    def t_newline(t):
        # noinspection PySingleQuotedDocstring
        r"\n+"
        t.lexer.lineno += t.value.count("\n")

    @staticmethod
    def t_error(t):
        # TODO: How to handle errors?
        print("Illegal character '%s'".format(t.value[0]))
        t.lexer.skip(1)

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
