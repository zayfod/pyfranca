"""
Pyfranca lexer and parser tests.
"""

import unittest

from pyfranca import LexerException, ParserException, Parser, ast


class BaseTestCase(unittest.TestCase):

    @staticmethod
    def _parse(data):
        parser = Parser()
        package = parser.parse(data)
        return package

    def _assertParse(self, data):
        package = self._parse(data)
        self.assertIsInstance(package, ast.Package)
        return package


class TestTopLevel(BaseTestCase):
    """Test parsing top-level Franca elements."""

    def test_empty(self):
        """A package statement is expected as a minimum."""
        with self.assertRaises(ParserException) as context:
            self._parse("")
        self.assertEqual(str(context.exception),
                         "Reached unexpected end of file.")

    def test_garbage(self):
        """Invalid input."""
        with self.assertRaises(LexerException) as context:
            self._parse("%!@#")
        self.assertEqual(str(context.exception),
                         "Illegal character '%' at line 1.")

    def test_single_line_comments(self):
        self._assertParse("""
            // Package P
            package P   // This is P
            // EOF
        """)

    def test_multiline_comments(self):
        self._assertParse("""
            /* Package P
            */
            package P   /* This is P */
            /* EOF
            */
        """)

    def test_structured_comments(self):
        self._assertParse("""
            <** @description: Package P
            **>
            package P
        """)

    def test_empty_package(self):
        package = self._assertParse("package P")
        self.assertEqual(package.name, "P")
        self.assertEqual(package.files, [])
        self.assertEqual(len(package.imports), 0)
        self.assertEqual(len(package.typecollections), 0)
        self.assertEqual(len(package.interfaces), 0)

    def test_multiple_package_definitions(self):
        with self.assertRaises(ParserException) as context:
            self._parse("""
                package P
                package P2
            """)
        self.assertEqual(str(context.exception),
                         "Syntax error at line 3 near 'package'.")

    def test_import_namespace(self):
        package = self._assertParse("package P import NS from \"test.fidl\"")
        self.assertEqual(package.name, "P")
        self.assertEqual(package.files, [])
        self.assertEqual(len(package.imports), 1)
        self.assertEqual(len(package.typecollections), 0)
        self.assertEqual(len(package.interfaces), 0)
        imp = package.imports[0]
        self.assertEqual(imp.namespace, "NS")
        self.assertEqual(imp.file, "test.fidl")

    def test_import_model(self):
        package = self._assertParse("package P import model \"test.fidl\"")
        self.assertEqual(package.name, "P")
        self.assertEqual(package.files, [])
        self.assertEqual(len(package.imports), 1)
        self.assertEqual(len(package.typecollections), 0)
        self.assertEqual(len(package.interfaces), 0)
        imp = package.imports[0]
        self.assertIsNone(imp.namespace)
        self.assertEqual(imp.file, "test.fidl")

    def test_import_two_namespaces(self):
        package = self._assertParse("""
            package P
            import NS1 from "test1.fidl"
            import NS2 from "test2.fidl"
        """)
        self.assertEqual(package.name, "P")
        self.assertEqual(package.files, [])
        self.assertEqual(len(package.imports), 2)
        self.assertEqual(len(package.typecollections), 0)
        self.assertEqual(len(package.interfaces), 0)
        imp = package.imports[0]
        self.assertEqual(imp.namespace, "NS1")
        self.assertEqual(imp.file, "test1.fidl")
        imp = package.imports[1]
        self.assertEqual(imp.namespace, "NS2")
        self.assertEqual(imp.file, "test2.fidl")

    def test_empty_typecollection(self):
        package = self._assertParse("package P typeCollection TC {}")
        self.assertEqual(package.name, "P")
        self.assertEqual(package.files, [])
        self.assertEqual(len(package.imports), 0)
        self.assertEqual(len(package.typecollections), 1)
        self.assertEqual(len(package.interfaces), 0)
        self.assertTrue("TC" in package.typecollections)
        typecollection = package.typecollections["TC"]
        self.assertEqual(typecollection.package, package)
        self.assertEqual(typecollection.name, "TC")
        self.assertListEqual(typecollection.flags, [])
        self.assertIsNone(typecollection.version)
        self.assertEqual(len(typecollection.typedefs), 0)
        self.assertEqual(len(typecollection.enumerations), 0)
        self.assertEqual(len(typecollection.structs), 0)
        self.assertEqual(len(typecollection.arrays), 0)
        self.assertEqual(len(typecollection.maps), 0)

    def test_two_empty_typecollections(self):
        package = self._assertParse("""
            package P
            typeCollection TC1 {}
            typeCollection TC2 {}
        """)
        self.assertEqual(package.name, "P")
        self.assertEqual(package.files, [])
        self.assertEqual(len(package.imports), 0)
        self.assertEqual(len(package.typecollections), 2)
        self.assertEqual(len(package.interfaces), 0)
        self.assertTrue("TC1" in package.typecollections)
        typecollection = package.typecollections["TC1"]
        self.assertEqual(typecollection.package, package)
        self.assertEqual(typecollection.name, "TC1")
        self.assertListEqual(typecollection.flags, [])
        self.assertIsNone(typecollection.version)
        self.assertEqual(len(typecollection.typedefs), 0)
        self.assertEqual(len(typecollection.enumerations), 0)
        self.assertEqual(len(typecollection.structs), 0)
        self.assertEqual(len(typecollection.arrays), 0)
        self.assertEqual(len(typecollection.maps), 0)
        self.assertTrue("TC2" in package.typecollections)
        typecollection = package.typecollections["TC2"]
        self.assertEqual(typecollection.package, package)
        self.assertEqual(typecollection.name, "TC2")
        self.assertListEqual(typecollection.flags, [])
        self.assertIsNone(typecollection.version)
        self.assertEqual(len(typecollection.typedefs), 0)
        self.assertEqual(len(typecollection.enumerations), 0)
        self.assertEqual(len(typecollection.structs), 0)
        self.assertEqual(len(typecollection.arrays), 0)
        self.assertEqual(len(typecollection.maps), 0)

    def test_empty_interface(self):
        package = self._assertParse("package P interface I {}")
        self.assertEqual(package.name, "P")
        self.assertEqual(package.files, [])
        self.assertEqual(len(package.imports), 0)
        self.assertEqual(len(package.typecollections), 0)
        self.assertEqual(len(package.interfaces), 1)
        self.assertTrue("I" in package.interfaces)
        interface = package.interfaces["I"]
        self.assertEqual(interface.package, package)
        self.assertEqual(interface.name, "I")
        self.assertListEqual(interface.flags, [])
        self.assertIsNone(interface.version)
        self.assertEqual(len(interface.typedefs), 0)
        self.assertEqual(len(interface.enumerations), 0)
        self.assertEqual(len(interface.structs), 0)
        self.assertEqual(len(interface.arrays), 0)
        self.assertEqual(len(interface.maps), 0)
        self.assertEqual(len(interface.attributes), 0)
        self.assertEqual(len(interface.methods), 0)
        self.assertEqual(len(interface.broadcasts), 0)

    def test_two_empty_interfaces(self):
        package = self._assertParse("""
            package P
            interface I1 {}
            interface I2 {}
        """)
        self.assertEqual(package.name, "P")
        self.assertEqual(package.files, [])
        self.assertEqual(len(package.imports), 0)
        self.assertEqual(len(package.typecollections), 0)
        self.assertEqual(len(package.interfaces), 2)
        self.assertTrue("I1" in package.interfaces)
        interface = package.interfaces["I1"]
        self.assertEqual(interface.package, package)
        self.assertEqual(interface.name, "I1")
        self.assertListEqual(interface.flags, [])
        self.assertIsNone(interface.version)
        self.assertEqual(len(interface.typedefs), 0)
        self.assertEqual(len(interface.enumerations), 0)
        self.assertEqual(len(interface.structs), 0)
        self.assertEqual(len(interface.arrays), 0)
        self.assertEqual(len(interface.maps), 0)
        self.assertEqual(len(interface.attributes), 0)
        self.assertEqual(len(interface.methods), 0)
        self.assertEqual(len(interface.broadcasts), 0)
        self.assertTrue("I2" in package.interfaces)
        interface = package.interfaces["I2"]
        self.assertEqual(interface.package, package)
        self.assertEqual(interface.name, "I2")
        self.assertListEqual(interface.flags, [])
        self.assertIsNone(interface.version)
        self.assertEqual(len(interface.typedefs), 0)
        self.assertEqual(len(interface.enumerations), 0)
        self.assertEqual(len(interface.structs), 0)
        self.assertEqual(len(interface.arrays), 0)
        self.assertEqual(len(interface.maps), 0)
        self.assertEqual(len(interface.attributes), 0)
        self.assertEqual(len(interface.methods), 0)
        self.assertEqual(len(interface.broadcasts), 0)


class TestUnsupported(BaseTestCase):
    """Test that unsupported Franca features fail appropriately."""

    def test_dots_in_namespace_names(self):
        """Franca 0.9.2, section 5.8.2"""
        with self.assertRaises(ParserException) as context:
            self._parse("""
                package org.franca.examples
                interface simple.ExampleInterface {
                    // this interface can be globally accessed by the FQN
                    // org.franca.examples.simple.ExampleInterface
                }
            """)
        self.assertEqual(str(context.exception),
                         "Syntax error at line 3 near '.'.")

    def test_expressions(self):
        """Franca 0.9.2, section 5.2.1"""
        with self.assertRaises(ParserException) as context:
            self._parse("""
                package P
                typeCollection TC {
                    const UInt32 twentyFive = 55
                    const Boolean b2 = MAX COUNT > 3
                    const Boolean b3 = (a && b) jj foo=="bar"
                }
            """)
        self.assertEqual(str(context.exception),
                         "Syntax error at line 5 near 'MAX'.")

    def test_complex_constants(self):
        """Franca 0.9.2, section 5.2.2"""
        with self.assertRaises(ParserException) as context:
            self._parse("""
                package P
                typeCollection TC {
                    array Array1 of UInt16
                    const Array1 empty = []
                    const Array1 full = [ 1, 2, 2+3, 100*100+100 ]

                    struct Struct1 {
                        Boolean e1
                        UInt16 e2
                        String e3
                    }
                    const Struct1 s1 = { e1: true, e2: 1, e3: "foo" }

                    union Union1 {
                        UInt16 e1
                        Boolean e2
                        String e3
                    }
                    const Union1 uni1 = { e1: 1 }
                    const Union1 uni2 = { e3: "foo" }

                    map Map1 { UInt16 to String }
                    const Map1 m1 = [ 1 => "one", 2 => "two" ]
                }
            """)
        self.assertEqual(str(context.exception),
                         "Syntax error at line 5 near 'Array1'.")

    def test_unions(self):
        """Franca 0.9.2, section 5.1.6"""
        with self.assertRaises(ParserException) as context:
            self._parse("""
                package P
                typeCollection TC {
                    union ExampleUnion {
                        UInt32 element1
                        Float element2
                    }
                }
            """)
        self.assertEqual(str(context.exception),
                         "Syntax error at line 4 near 'union'.")

    def test_error_extending(self):
        """Franca 0.9.2, section 5.5.3"""
        with self.assertRaises(ParserException) as context:
            self._parse("""
                package P
                interface I {
                    method m {
                        error extends GenericErrors {
                            OVERFLOW
                            UNDERFLOW
                        }
                    }
                    enumeration GenericErrors {
                        INVALID_PARAMATERS
                    }
                }
            """)
        self.assertEqual(str(context.exception),
                         "Syntax error at line 5 near 'extends'.")

    def test_contracts(self):
        """Franca 0.9.2, section 5.5.3"""
        with self.assertRaises(ParserException) as context:
            self._parse("""
                package P
                contract {
                    PSM {
                        initial idle
                        state idle {
                            on call setActivePlayer -> working
                        }
                        state working {
                            on signal attachOutput -> idle
                        }
                    }
                }
            """)
        self.assertEqual(str(context.exception),
                         "Syntax error at line 3 near 'contract'.")


class TestFrancaUserManualExamples(BaseTestCase):
    """Test parsing various examples from the Franca user manual."""

    def test_calculator_api(self):
        self._assertParse("""
            package P
            interface CalculatorAPI {
                method add {
                    in {
                        Float a
                        Float b
                    }
                    out {
                        Float sum
                    }
                }
            }
        """)

    def test_example_interface(self):
        self._assertParse("""
            package P
            interface ExampleInterface {
                attribute Double temperature readonly noSubscriptions
                attribute Boolean overheated
            }
        """)

    def test_calculator_divide(self):
        """Method "error extends ..." statements are not supported."""
        with self.assertRaises(ParserException) as context:
            self._parse("""
            package P
            interface Calculator {
                method divide {
                    in {
                        UInt32 dividend
                        UInt32 divisor
                    }
                    out {
                        UInt32 quotient
                        UInt32 remainder
                    }
                    error extends GenericErrors {
                        DIVISION_BY_ZERO
                        OVERFLOW
                        UNDERFLOW
                    }
                }
                enumeration GenericErrors {
                    INVALID_PARAMATERS
                    // ...
                }
            }
        """)
        self.assertEqual(str(context.exception),
                         "Syntax error at line 13 near 'extends'.")

    def test_calculator_divide2(self):
        self._assertParse("""
            package P
            interface Calculator {
                method divide {
                    in {
                        UInt32 dividend
                        UInt32 divisor
                    }
                    out {
                        UInt32 quotient
                        UInt32 remainder
                    }
                    error CalcErrors
                }
                enumeration CalcErrors {
                    DIVISION_BY_ZERO
                    OVERFLOW
                    UNDERFLOW
                }
            }
        """)

    def test_broadcast(self):
        self._assertParse("""
            package P
            interface ExampleInterface {
                broadcast buttonClicked {
                    out {
                        ButtonId id
                        Boolean isLongPress
                    }
                }
            }
        """)


class TestMisc(BaseTestCase):
    """Test parsing various FIDL examples."""

    def test_all_supported(self):
        self._assertParse("""
            package P

            import m1.* from "m1.fidl"
            import model "m2.fidl"

            typeCollection TC {
                version { major 1 minor 0 }

                typedef MyInt8 is Int8
                typedef MyInt16 is Int16
                typedef MyInt32 is Int32
                typedef MyInt64 is Int64
                typedef MyUInt8 is UInt8
                typedef MyUInt16 is UInt16
                typedef MyUInt32 is UInt32
                typedef MyUInt64 is UInt64
                typedef MyBoolean is Boolean
                typedef MyFloat is Float
                typedef MyDouble is Double
                typedef MyString is String
                typedef MyByteBuffer is ByteBuffer

                typedef MyInt32Array is Int32[]
                typedef MyThis is MyThat

                enumeration E {
                    FALSE = 0
                    TRUE
                }
                enumeration E2 extends E {}

                struct S {
                    Int32 a
                    Int32[] b
                }
                struct S2 extends S {}
                struct S3 polymorphic {}

                array A of UInt8

                map M {
                    String to Int32
                }
                map M2 {
                    Key to Value
                }
            }

            interface I {
                version { major 1 minor 0 }

                attribute Int32 A
                attribute Int32 A2 readonly
                attribute Int32 A3 noSubscriptions

                method M {
                    in {
                        Float a
                        Float[] b
                    }
                    out {
                        Float result
                    }
                    error {
                        FAILURE = 0
                        SUCCESS
                    }
                }
                method M2 fireAndForget {}

                broadcast B {
                    out {
                        Int32 x
                    }
                }
                broadcast B2 selective {}

                typedef ITD is String

                enumeration IE {
                    FALSE = 0
                    TRUE
                }

                struct IS {
                    Int32 a
                    Int32[] b
                }

                array IA of UInt8

                map IM {
                    String to Int32
                }
            }

            interface I2 extends I {
            }
        """)


class TestTypeCollections(BaseTestCase):
    """Test parsing type collections."""

    def test_normal(self):
        package = self._assertParse("""
            package P
            typeCollection TC {
                version { major 12 minor 34 }
            }
        """)
        tc = package.typecollections["TC"]
        self.assertEqual(tc.package, package)
        self.assertEqual(tc.name, "TC")
        self.assertEqual(tc.flags, [])
        self.assertEqual(str(tc.version), "12.34")
        self.assertEqual(len(tc.typedefs), 0)
        self.assertEqual(len(tc.enumerations), 0)
        self.assertEqual(len(tc.structs), 0)
        self.assertEqual(len(tc.arrays), 0)
        self.assertEqual(len(tc.maps), 0)

    def test_multiple_versions(self):
        with self.assertRaises(ParserException) as context:
            self._parse("""
                package P
                typeCollection TC {
                    version { major 1 minor 0 }
                    version { major 2 minor 0 }
                }
            """)
        self.assertEqual(str(context.exception),
                         "Multiple version definitions.")

    def test_duplicate_member(self):
        with self.assertRaises(ParserException) as context:
            self._parse("""
                package P
                typeCollection TC {
                    typedef X is MyThat
                    array X of UInt8
                }
            """)
        self.assertEqual(str(context.exception),
                         "Duplicate namespace member 'X'.")


class TestInterfaces(BaseTestCase):
    """Test parsing interfaces."""

    def test_normal(self):
        package = self._assertParse("""
            package P
            interface I {
                version { major 12 minor 34 }
                method add {
                    in {
                        Float a
                        Float b
                    }
                    out {
                        Float sum
                    }
                }
            }
            interface I2 extends I {
            }
        """)
        i = package.interfaces["I"]
        self.assertEqual(i.package, package)
        self.assertEqual(i.name, "I")
        self.assertEqual(i.flags, [])
        self.assertEqual(str(i.version), "12.34")
        self.assertEqual(len(i.typedefs), 0)
        self.assertEqual(len(i.enumerations), 0)
        self.assertEqual(len(i.structs), 0)
        self.assertEqual(len(i.arrays), 0)
        self.assertEqual(len(i.maps), 0)
        self.assertEqual(len(i.attributes), 0)
        self.assertEqual(len(i.methods), 1)
        self.assertEqual(len(i.broadcasts), 0)
        self.assertIsNone(i.extends)
        i2 = package.interfaces["I2"]
        self.assertEqual(i2.package, package)
        self.assertEqual(i2.name, "I2")
        self.assertIsNone(i2.version)
        self.assertEqual(i2.extends, "I")

    def test_multiple_versions(self):
        with self.assertRaises(ParserException) as context:
            self._parse("""
                package P
                interface I {
                    version { major 1 minor 0 }
                    version { major 2 minor 0 }
                }
            """)
        self.assertEqual(str(context.exception),
                         "Multiple version definitions.")

    def test_duplicate_member(self):
        with self.assertRaises(ParserException) as context:
            self._parse("""
                package P
                interface I {
                    typedef X is MyThat
                    method X {}
                }
            """)
        self.assertEqual(str(context.exception),
                         "Duplicate namespace member 'X'.")


class TestEnumerations(BaseTestCase):
    """Test parsing enumerations."""

    def test_normal(self):
        package = self._assertParse("""
            package P
            typeCollection TC {
                enumeration E {
                    FALSE = 0
                    TRUE
                }
                enumeration E2 extends E {}
            }
        """)
        typecollection = package.typecollections["TC"]
        e = typecollection.enumerations["E"]
        self.assertEqual(e.namespace, typecollection)
        self.assertEqual(e.name, "E")
        self.assertIsNone(e.extends)
        self.assertEqual(e.flags, [])
        self.assertEqual(len(e.enumerators), 2)
        ee = e.enumerators["FALSE"]
        self.assertEqual(ee.name, "FALSE")
        self.assertEqual(ee.value, 0)
        ee = e.enumerators["TRUE"]
        self.assertEqual(ee.name, "TRUE")
        self.assertIsNone(ee.value)
        e2 = typecollection.enumerations["E2"]
        self.assertEqual(e2.namespace, typecollection)
        self.assertEqual(e2.name, "E2")
        self.assertEqual(e2.extends, "E")
        self.assertEqual(e2.flags, [])
        self.assertEqual(len(e2.enumerators), 0)

    def test_duplicate_enumerator(self):
        with self.assertRaises(ParserException) as context:
            self._parse("""
                package P
                typeCollection TC {
                    enumeration E { a a }
                }
            """)
        self.assertEqual(str(context.exception),
                         "Duplicate enumerator 'a'.")


class TestStructs(BaseTestCase):
    """Test parsing structures."""

    def test_normal(self):
        package = self._assertParse("""
            package P
            typeCollection TC {
                struct S {
                    Int32 a
                    String b
                }
                struct S2 extends S {}
                struct S3 polymorphic {}
            }
            interface I {
                struct S4 {
                    Int32 a
                    String b
                }
            }
        """)
        typecollection = package.typecollections["TC"]
        s = typecollection.structs["S"]
        self.assertEqual(s.name, "S")
        self.assertIsNone(s.extends)
        self.assertEqual(s.namespace, typecollection)
        self.assertEqual(len(s.fields), 2)
        self.assertEqual(s.fields["a"].name, "a")
        self.assertIsInstance(s.fields["a"].type, ast.Int32)
        self.assertEqual(s.fields["b"].name, "b")
        self.assertIsInstance(s.fields["b"].type, ast.String)
        self.assertEqual(len(s.flags), 0)
        s2 = typecollection.structs["S2"]
        self.assertEqual(s2.name, "S2")
        self.assertEqual(s2.extends, "S")
        self.assertEqual(len(s2.fields), 0)
        self.assertEqual(s2.namespace, typecollection)
        self.assertEqual(len(s2.flags), 0)
        s3 = typecollection.structs["S3"]
        self.assertEqual(s3.name, "S3")
        self.assertIsNone(s3.extends)
        self.assertEqual(s3.namespace, typecollection)
        self.assertEqual(len(s3.fields), 0)
        self.assertEqual(len(s3.flags), 1)
        self.assertEqual(s3.flags[0], "polymorphic")
        interface = package.interfaces["I"]
        self.assertEqual(len(interface.structs), 1)
        s4 = interface.structs["S4"]
        self.assertEqual(s4.name, "S4")
        self.assertIsNone(s4.extends)
        self.assertEqual(s4.namespace, interface)
        self.assertEqual(len(s4.fields), 2)
        self.assertEqual(s4.fields["a"].name, "a")
        self.assertIsInstance(s4.fields["a"].type, ast.Int32)
        self.assertEqual(s4.fields["b"].name, "b")
        self.assertIsInstance(s4.fields["b"].type, ast.String)
        self.assertEqual(len(s4.flags), 0)

    def test_duplicate_field(self):
        with self.assertRaises(ParserException) as context:
            self._parse("""
                package P
                typeCollection TC {
                    struct S {
                        Int32 a
                        String a
                    }
                }
            """)
        self.assertEqual(str(context.exception),
                         "Duplicate structure field 'a'.")


class TestMethods(BaseTestCase):
    """Test parsing methods."""

    def test_duplicate_argument(self):
        with self.assertRaises(ParserException) as context:
            self._parse("""
                package P
                interface I {
                    method M {
                        in {
                            Float a
                            Float a
                        }
                    }
                }
            """)
        self.assertEqual(str(context.exception),
                         "Duplicate argument 'a'.")


class TestBroadcasts(BaseTestCase):
    """Test parsing broadcasts."""

    def test_duplicate_argument(self):
        with self.assertRaises(ParserException) as context:
            self._parse("""
                package P
                interface I {
                    broadcast B {
                        out {
                            Float a
                            Float a
                        }
                    }
                }
            """)
        self.assertEqual(str(context.exception), "Duplicate argument 'a'.")


class TestConstants(BaseTestCase):
    """Test parsing constants."""
    def test_constants(self):
        """Franca 0.9.2, section 5.2.1"""
        package = self._parse("""
            package P
            typeCollection TC {
                const UInt32 MAX_COUNT = 10000
                const Double pi = 3.1415d
                const Float f1 = 1.2f
                const Float f2 = 6.022e23f
                const Boolean b1 = true
                const Boolean b2 = false

                const String s1 = "Hello"

                const String s2 = "Hello
                                   World"
            }
        """)
        self.assertEqual(package.name, "P")
        self.assertEqual(package.files, [])
        self.assertEqual(len(package.imports), 0)
        self.assertEqual(len(package.typecollections), 1)
        self.assertEqual(len(package.interfaces), 0)
        self.assertTrue("TC" in package.typecollections)
        typecollection = package.typecollections["TC"]
        self.assertEqual(typecollection.package, package)
        self.assertEqual(typecollection.name, "TC")
        self.assertListEqual(typecollection.flags, [])
        self.assertIsNone(typecollection.version)
        self.assertEqual(len(typecollection.typedefs), 0)
        self.assertEqual(len(typecollection.enumerations), 0)
        self.assertEqual(len(typecollection.structs), 0)
        self.assertEqual(len(typecollection.arrays), 0)
        self.assertEqual(len(typecollection.maps), 0)
        self.assertEqual(len(typecollection.constants), 8)

        self.assertEqual(typecollection.constants["MAX_COUNT"].name, "MAX_COUNT")
        self.assertEqual(typecollection.constants["MAX_COUNT"].type.name, "UInt32")
        self.assertEqual(typecollection.constants["MAX_COUNT"].value.value, 10000)
        self.assertEqual(typecollection.constants["MAX_COUNT"].value.name, "IntegerValue")

        self.assertEqual(typecollection.constants["pi"].name, "pi")
        self.assertEqual(typecollection.constants["pi"].type.name, "Double")
        self.assertEqual(typecollection.constants["pi"].value.value, 3.1415)
        self.assertEqual(typecollection.constants["pi"].value.name, "DoubleValue")

        self.assertEqual(typecollection.constants["f1"].name, "f1")
        self.assertEqual(typecollection.constants["f1"].type.name, "Float")
        self.assertAlmostEqual(typecollection.constants["f1"].value.value, 1.2)
        self.assertEqual(typecollection.constants["f1"].value.name, "FloatValue")

        self.assertEqual(typecollection.constants["f2"].name, "f2")
        self.assertEqual(typecollection.constants["f2"].type.name, "Float")
        self.assertAlmostEqual(typecollection.constants["f2"].value.value, 6.022e23)
        self.assertEqual(typecollection.constants["f2"].value.name, "FloatValue")

        self.assertEqual(typecollection.constants["b1"].name, "b1")
        self.assertEqual(typecollection.constants["b1"].type.name, "Boolean")
        self.assertEqual(typecollection.constants["b1"].value.value, True)
        self.assertEqual(typecollection.constants["b1"].value.name, "BooleanValue")

        self.assertEqual(typecollection.constants["b2"].name, "b2")
        self.assertEqual(typecollection.constants["b2"].type.name, "Boolean")
        self.assertEqual(typecollection.constants["b2"].value.value, False)
        self.assertEqual(typecollection.constants["b2"].value.name, "BooleanValue")

        self.assertEqual(typecollection.constants["s1"].name, "s1")
        self.assertEqual(typecollection.constants["s1"].type.name, "String")
        self.assertAlmostEqual(typecollection.constants["s1"].value.value, "Hello")
        self.assertEqual(typecollection.constants["s1"].value.name, "StringValue")

        self.assertEqual(typecollection.constants["s2"].name, "s2")
        self.assertEqual(typecollection.constants["s2"].type.name, "String")
        self.assertAlmostEqual(typecollection.constants["s2"].value.value,
                               "Hello\n                                   World")
        self.assertEqual(typecollection.constants["s2"].value.name, "StringValue")

    def test_constants_casting(self):
        """Franca 0.9.2, section 5.2.1"""
        package = self._parse("""
            package P
            typeCollection TC {
                const Float f1 = 123
                const Float f2 = true
                const Double d1 = 123
                const Double d2 = true
                const Boolean b1 = 123
                const Boolean b2 = 123.0f
                const Boolean b3 = 0.0d
                const Boolean b4 = "123"
                const String s1 = 123
                const String s2 = 123.0f
                const String s3 = 0.0d
                const String s4 = true
            }
        """)
        self.assertEqual(package.name, "P")
        self.assertEqual(package.files, [])
        self.assertEqual(len(package.imports), 0)
        self.assertEqual(len(package.typecollections), 1)
        self.assertEqual(len(package.interfaces), 0)
        self.assertTrue("TC" in package.typecollections)
        typecollection = package.typecollections["TC"]
        self.assertEqual(typecollection.package, package)
        self.assertEqual(typecollection.name, "TC")
        self.assertListEqual(typecollection.flags, [])
        self.assertIsNone(typecollection.version)
        self.assertEqual(len(typecollection.typedefs), 0)
        self.assertEqual(len(typecollection.enumerations), 0)
        self.assertEqual(len(typecollection.structs), 0)
        self.assertEqual(len(typecollection.arrays), 0)
        self.assertEqual(len(typecollection.maps), 0)
        self.assertEqual(len(typecollection.constants), 12)

        x = "f1"
        self.assertEqual(typecollection.constants[x].name, x)
        self.assertEqual(typecollection.constants[x].type.name, "Float")
        self.assertAlmostEqual(typecollection.constants[x].value.value, 123.0)
        self.assertEqual(typecollection.constants[x].value.name, "FloatValue")

        x = "f2"
        self.assertEqual(typecollection.constants[x].name, x)
        self.assertEqual(typecollection.constants[x].type.name, "Float")
        self.assertAlmostEqual(typecollection.constants[x].value.value, 1.0)
        self.assertEqual(typecollection.constants[x].value.name, "FloatValue")

        x = "d1"
        self.assertEqual(typecollection.constants[x].name, x)
        self.assertEqual(typecollection.constants[x].type.name, "Double")
        self.assertAlmostEqual(typecollection.constants[x].value.value, 123.0)
        self.assertEqual(typecollection.constants[x].value.name, "DoubleValue")

        x = "d2"
        self.assertEqual(typecollection.constants[x].name, x)
        self.assertEqual(typecollection.constants[x].type.name, "Double")
        self.assertAlmostEqual(typecollection.constants[x].value.value, 1.0)
        self.assertEqual(typecollection.constants[x].value.name, "DoubleValue")

        x = "b1"
        self.assertEqual(typecollection.constants[x].name, x)
        self.assertEqual(typecollection.constants[x].type.name, "Boolean")
        self.assertAlmostEqual(typecollection.constants[x].value.value, True)
        self.assertEqual(typecollection.constants[x].value.name, "BooleanValue")

        x = "b2"
        self.assertEqual(typecollection.constants[x].name, x)
        self.assertEqual(typecollection.constants[x].type.name, "Boolean")
        self.assertAlmostEqual(typecollection.constants[x].value.value, True)
        self.assertEqual(typecollection.constants[x].value.name, "BooleanValue")

        x = "b3"
        self.assertEqual(typecollection.constants[x].name, x)
        self.assertEqual(typecollection.constants[x].type.name, "Boolean")
        self.assertAlmostEqual(typecollection.constants[x].value.value, False)
        self.assertEqual(typecollection.constants[x].value.name, "BooleanValue")

        x = "b4"
        self.assertEqual(typecollection.constants[x].name, x)
        self.assertEqual(typecollection.constants[x].type.name, "Boolean")
        self.assertAlmostEqual(typecollection.constants[x].value.value, True)
        self.assertEqual(typecollection.constants[x].value.name, "BooleanValue")

        x = "s1"
        self.assertEqual(typecollection.constants[x].name, x)
        self.assertEqual(typecollection.constants[x].type.name, "String")
        self.assertAlmostEqual(typecollection.constants[x].value.value, "123")
        self.assertEqual(typecollection.constants[x].value.name, "StringValue")

        x = "s2"
        self.assertEqual(typecollection.constants[x].name, x)
        self.assertEqual(typecollection.constants[x].type.name, "String")
        self.assertAlmostEqual(typecollection.constants[x].value.value, "123.0")
        self.assertEqual(typecollection.constants[x].value.name, "StringValue")

        x = "s3"
        self.assertEqual(typecollection.constants[x].name, x)
        self.assertEqual(typecollection.constants[x].type.name, "String")
        self.assertAlmostEqual(typecollection.constants[x].value.value, "0.0")
        self.assertEqual(typecollection.constants[x].value.name, "StringValue")

        x = "s4"
        self.assertEqual(typecollection.constants[x].name, x)
        self.assertEqual(typecollection.constants[x].type.name, "String")
        self.assertAlmostEqual(typecollection.constants[x].value.value, "True")
        self.assertEqual(typecollection.constants[x].value.name, "StringValue")

    def test_constants_bad_syntax_Uint32(self):
        """Franca 0.9.2, section 5.2.1"""

        with self.assertRaises(ParserException) as context:
            self._parse("""
            package P
            typeCollection TC {
                const UInt32 MAX_COUNT = "Hello"
            }
        """)
        self.assertEqual(str(context.exception),
                         "Syntax error at line 4 near 'Hello'.")

    def test_constants_bad_syntax_String(self):
        """Franca 0.9.2, section 5.2.1"""

        with self.assertRaises(ParserException) as context:
            self._parse("""
            package P
            typeCollection TC {
                const String s1 = 123abc
            }
        """)
        self.assertEqual(str(context.exception),
                         "Syntax error at line 4 near 'abc'.")

    def test_constants_bad_syntax_Boolean(self):
        """Franca 0.9.2, section 5.2.1"""

        with self.assertRaises(ParserException) as context:
            self._parse("""
            package P
            typeCollection TC {
                const Boolean b1 = 123asc
            }
        """)
        self.assertEqual(str(context.exception),
                         "Syntax error at line 4 near 'asc'.")

    def test_constants_bad_syntax_typename(self):
        """Franca 0.9.2, section 5.2.1"""

        with self.assertRaises(ParserException) as context:
            self._parse("""
            package P
            typeCollection TC {
                const double d1 = 123.3d
            }
        """)
        self.assertEqual(str(context.exception),
                         "Syntax error at line 4 near 'double'.")
