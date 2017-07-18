"""
Pyfranca lexer tests.
"""

import unittest

from pyfranca import LexerException, Lexer


class BaseTestCase(unittest.TestCase):

    @staticmethod
    def _tokenize(data):
        lexer = Lexer()
        tokenized_data = lexer.tokenize_data(data)
        return tokenized_data

    def _assert_tokenize(self, data):
        tokenized_data = self._tokenize(data)
        self.assertIsInstance(tokenized_data)
        return tokenized_data


class TestCheckRegularExpressions(BaseTestCase):
    """Test regular expression used by the lexer """

    def test_integer_valid_syntax(self):
        """test an integer """
        tokenized_data = self._tokenize("1234\n2345\n0x1234\n0x56789\n0xabcdef\n0xABCDEF")
        self.assertEqual(tokenized_data[0].type, "INTEGER_VAL")
        self.assertEqual(tokenized_data[0].value, 1234)

        self.assertEqual(tokenized_data[1].type, "INTEGER_VAL")
        self.assertEqual(tokenized_data[1].value, 2345)

        self.assertEqual(tokenized_data[2].type, "HEX_INTEGER_VAL")
        self.assertEqual(tokenized_data[2].value, int("0x1234", 0))

        self.assertEqual(tokenized_data[3].type, "HEX_INTEGER_VAL")
        self.assertEqual(tokenized_data[3].value, int("0x56789", 0))

        self.assertEqual(tokenized_data[4].type, "HEX_INTEGER_VAL")
        self.assertEqual(tokenized_data[4].value, int("0xabcdef", 0))

        self.assertEqual(tokenized_data[5].type, "HEX_INTEGER_VAL")
        self.assertEqual(tokenized_data[5].value, int("0xABCDEF", 0))

    def test_string_valid_syntax(self):
        """test a string """
        tokenized_data = self._tokenize("\"This is a string\"")
        self.assertEqual(tokenized_data[0].type, "STRING_VAL")
        self.assertEqual(tokenized_data[0].value, "This is a string")

        tokenized_data = self._tokenize("\"This is a string \n with an newline\"")
        self.assertEqual(tokenized_data[0].type, "STRING_VAL")
        self.assertEqual(tokenized_data[0].value, "This is a string \n with an newline")

    def test_boolean_valid_syntax(self):
        """test a boolean value """
        tokenized_data = self._tokenize("true\nfalse")
        self.assertEqual(tokenized_data[0].type, "BOOLEAN_VAL")
        self.assertEqual(tokenized_data[0].value, True)
        self.assertEqual(tokenized_data[1].type, "BOOLEAN_VAL")
        self.assertEqual(tokenized_data[1].value, False)

    def test_integerinvalid_syntax(self):
        """test a boolean value """
        tokenized_data = self._tokenize("0xgabcdefg")
        for t in tokenized_data:
            self.assertNotEqual(t.type, "HEX_INTEGER_VAL")

    def test_booleaninvalid_syntax(self):
        """test a boolean value """
        tokenized_data = self._tokenize("istrue\nisfalse")
        for t in tokenized_data:
            self.assertNotEqual(t.type, "BOOLEAN_VAL")

    def test_float_valid_syntax(self):
        """test a float value """
        tokenized_data = self._tokenize("1.1f\n-2.2f\n3.3e3f\n-4.4e4f\n5.5e-5f"
                                        "-6.6e-6f\n0.00001f\n-0.000002f\n1e4f\n-1e4f"
                                        ".1f\n-.2f\n.3e3f\n-.4e4f\n.5e-5f"
                                        "-.6e-6f\n.00001f\n-.000002f"
                                        )
        cnt = 0
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[0].value, "1.1f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-2.2f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "3.3e3f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-4.4e4f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "5.5e-5f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-6.6e-6f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "0.00001f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-0.000002f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "1e4f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-1e4f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, ".1f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-.2f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, ".3e3f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-.4e4f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, ".5e-5f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-.6e-6f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, ".00001f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-.000002f")

    def test_double_valid_syntax(self):
        """test a double value """
        tokenized_data = self._tokenize("1.1d\n-2.2d\n3.3e3d\n-4.4e4d\n5.5e-5d"
                                        "-6.6e-6d\n0.00001d\n-0.000002d\n1e4d\n-1e4d"
                                        ".1d\n-.2d\n.3e3d\n-.4e4d\n.5e-5d"
                                        "-.6e-6d\n.00001d\n-.000002d"
                                        )

        cnt = 0
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[0].value, "1.1d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-2.2d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "3.3e3d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-4.4e4d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "5.5e-5d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-6.6e-6d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "0.00001d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-0.000002d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "1e4d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-1e4d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, ".1d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-.2d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, ".3e3d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-.4e4d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, ".5e-5d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-.6e-6d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, ".00001d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-.000002d")


    def test_real_valid_syntax(self):
        """test a real value """
        tokenized_data = self._tokenize("1.1\n-2.2\n3.3e3\n-4.4e4\n5.5e-5"
                                        "-6.6e-6\n0.00001\n-0.000002\n1e4\n-1e4"
                                        ".1\n-.2\n.3e3\n-.4e4\n.5e-5"
                                        "-.6e-6\n.00001\n-.000002"
                                        )

        cnt = 0
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[0].value, "1.1")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-2.2")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "3.3e3")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-4.4e4")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "5.5e-5")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-6.6e-6")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "0.00001")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-0.000002")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "1e4")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-1e4")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, ".1")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-.2")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, ".3e3")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-.4e4")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, ".5e-5")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-.6e-6")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, ".00001")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-.000002")

    def test_doublefloat_invalid_syntax(self):
        """test a text containing .f """
        tokenized_data = self._tokenize("""
                package org.franca.examples
               0ef .ef  -1ef   ef ed .ed
                }
            """)
        for t in tokenized_data:
            self.assertNotEqual(t.type, "REAL_VAL")

    def test_type_valid_syntax(self):
        """test an integer """
        tokenized_data = self._tokenize("const Boolean b1 = true")
        self.assertEqual(tokenized_data[0].type, "CONST")
        self.assertEqual(tokenized_data[0].value, 'const')
        self.assertEqual(tokenized_data[1].type, "BOOLEAN")
        self.assertEqual(tokenized_data[1].value, 'Boolean')
        self.assertEqual(tokenized_data[2].type, "ID")
        self.assertEqual(tokenized_data[2].value, 'b1')
        self.assertEqual(tokenized_data[3].type, "=")
        self.assertEqual(tokenized_data[3].value, '=')
        self.assertEqual(tokenized_data[4].type, "BOOLEAN_VAL")
        self.assertEqual(tokenized_data[4].value, True)

    def test_type_invalid_syntax(self):
        """test an integer """
        tokenized_data = self._tokenize("const boolean b1 = true")
        self.assertEqual(tokenized_data[0].type, "CONST")
        self.assertEqual(tokenized_data[0].value, 'const')
        self.assertEqual(tokenized_data[1].type, "ID")
        self.assertEqual(tokenized_data[1].value, 'boolean')
        self.assertEqual(tokenized_data[2].type, "ID")
        self.assertEqual(tokenized_data[2].value, 'b1')
        self.assertEqual(tokenized_data[3].type, "=")
        self.assertEqual(tokenized_data[3].value, '=')
        self.assertEqual(tokenized_data[4].type, "BOOLEAN_VAL")
        self.assertEqual(tokenized_data[4].value, True)

