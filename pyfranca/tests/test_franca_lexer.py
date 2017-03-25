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
        tokenized_data = self._tokenize("1234\n2345")
        self.assertEqual(tokenized_data[0].type, "INTEGER")
        self.assertEqual(tokenized_data[0].value, 1234)

        self.assertEqual(tokenized_data[1].type, "INTEGER")
        self.assertEqual(tokenized_data[1].value, 2345)

    def test_string_valid_syntax(self):
        """test a string """
        tokenized_data = self._tokenize("\"This is a string\"")
        self.assertEqual(tokenized_data[0].type, "FILE_NAME")
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

    def test_booleaninvalid_syntax(self):
        """test a boolean value """
        tokenized_data = self._tokenize("istrue\nisfalse")
        for t in tokenized_data:
            self.assertNotEqual(t.type, "BOOLEAN_VAL")

    def test_float_valid_syntax(self):
        """test a float value """
        tokenized_data = self._tokenize("1.1f\n-2.2f\n3.3e3f\n-4.4e4f\n5.5e-5f\n-6.6e-6f\n0.00001f\n-0.000002f"
                                        "1e4f\n-1e4f")
        self.assertEqual(tokenized_data[0].type, "FLOAT_VAL")
        self.assertAlmostEqual(tokenized_data[0].value, 1.1)
        self.assertEqual(tokenized_data[1].type, "FLOAT_VAL")
        self.assertAlmostEqual(tokenized_data[1].value, -2.2)
        self.assertEqual(tokenized_data[2].type, "FLOAT_VAL")
        self.assertAlmostEqual(tokenized_data[2].value, 3.3e3)
        self.assertEqual(tokenized_data[3].type, "FLOAT_VAL")
        self.assertAlmostEqual(tokenized_data[3].value, -4.4e4)
        self.assertEqual(tokenized_data[4].type, "FLOAT_VAL")
        self.assertAlmostEqual(tokenized_data[4].value, 5.5e-5)
        self.assertEqual(tokenized_data[5].type, "FLOAT_VAL")
        self.assertAlmostEqual(tokenized_data[5].value, -6.6e-6)
        self.assertEqual(tokenized_data[6].type, "FLOAT_VAL")
        self.assertAlmostEqual(tokenized_data[6].value, 0.00001)
        self.assertEqual(tokenized_data[7].type, "FLOAT_VAL")
        self.assertAlmostEqual(tokenized_data[7].value, -0.000002)
        self.assertEqual(tokenized_data[8].type, "FLOAT_VAL")
        self.assertAlmostEqual(tokenized_data[8].value, 1e4)
        self.assertEqual(tokenized_data[9].type, "FLOAT_VAL")
        self.assertAlmostEqual(tokenized_data[9].value,-1e4)

    def test_double_valid_syntax(self):
        """test a double value """
        tokenized_data = self._tokenize("1.1d\n-2.2d\n3.3e3d\n-4.4e4d\n5.5e-5d\n-6.6e-6d\n0.00001d\n-0.000002d"
                                        "1e4d\n-1e4d")
        self.assertEqual(tokenized_data[0].type, "DOUBLE_VAL")
        self.assertAlmostEqual(tokenized_data[0].value, 1.1)
        self.assertEqual(tokenized_data[1].type, "DOUBLE_VAL")
        self.assertAlmostEqual(tokenized_data[1].value, -2.2)
        self.assertEqual(tokenized_data[2].type, "DOUBLE_VAL")
        self.assertAlmostEqual(tokenized_data[2].value, 3.3e3)
        self.assertEqual(tokenized_data[3].type, "DOUBLE_VAL")
        self.assertAlmostEqual(tokenized_data[3].value, -4.4e4)
        self.assertEqual(tokenized_data[4].type, "DOUBLE_VAL")
        self.assertAlmostEqual(tokenized_data[4].value, 5.5e-5)
        self.assertEqual(tokenized_data[5].type, "DOUBLE_VAL")
        self.assertAlmostEqual(tokenized_data[5].value, -6.6e-6)
        self.assertEqual(tokenized_data[6].type, "DOUBLE_VAL")
        self.assertAlmostEqual(tokenized_data[6].value, 0.00001)
        self.assertEqual(tokenized_data[7].type, "DOUBLE_VAL")
        self.assertAlmostEqual(tokenized_data[7].value, -0.000002)
        self.assertEqual(tokenized_data[8].type, "DOUBLE_VAL")
        self.assertAlmostEqual(tokenized_data[8].value, 1e4)
        self.assertEqual(tokenized_data[9].type, "DOUBLE_VAL")
        self.assertAlmostEqual(tokenized_data[9].value,-1e4)

    def test_text(self):
        """test a text containing .f """
        tokenized_data = self._tokenize("""
                package org.franca.examples
                interface simple.ExampleInterface {
                    // this interface can be globally accessed by the FQN
                    // org.franca.examples.simple.ExampleInterface
                }
            """)
        for t in tokenized_data:
            self.assertNotEqual(t.type, "FLOAT_VAL")
            self.assertNotEqual(t.type, "DOUBLE_VAL")

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




