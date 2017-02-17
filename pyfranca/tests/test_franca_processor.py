
import unittest

from pyfranca import ProcessorException, Processor, ast


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.processor = Processor()

    def tearDown(self):
        self.processor = None


class TestFQNs(BaseTestCase):
    """Test FQN parsing methods."""

    def test_basename(self):
        self.assertEqual(Processor.basename("P.I.A"), "A")
        self.assertEqual(Processor.basename("A"), "A")

    def test_packagename(self):
        self.assertEqual(Processor.packagename("P.I.A"), "P.I")
        self.assertIsNone(Processor.packagename("A"))

    def test_is_fqn(self):
        self.assertTrue(Processor.is_fqn("P.P.I.A"))
        self.assertTrue(Processor.is_fqn("P.I.A"))
        self.assertFalse(Processor.is_fqn("I.A"))
        self.assertFalse(Processor.is_fqn("A"))

    def test_split_fqn(self):
        self.assertEqual(Processor.split_fqn("P.P.I.A"), ("P.P", "I", "A"))
        self.assertEqual(Processor.split_fqn("P.I.A"), ("P", "I", "A"))
        self.assertEqual(Processor.split_fqn("I.A"), (None, "I", "A"))
        self.assertEqual(Processor.split_fqn("A"), (None, None, "A"))


class TestImports(BaseTestCase):
    """Test import related features."""

    def test_basic(self):
        self.processor.import_string("test.fidl", """
            package P
        """)
        self.processor.import_string("test2.fidl", """
            package P2
        """)
        # Verify file access
        self.assertEqual(len(self.processor.files), 2)
        p = self.processor.files["test.fidl"]
        self.assertEqual(p.name, "P")
        p2 = self.processor.files["test2.fidl"]
        self.assertEqual(p2.name, "P2")
        # Verify package access
        self.assertEqual(len(self.processor.packages), 2)
        p = self.processor.packages["P"]
        self.assertEqual(p.name, "P")
        p2 = self.processor.packages["P2"]
        self.assertEqual(p2.name, "P2")

    def test_import_nonexistent_model(self):
        with self.assertRaises(ProcessorException) as context:
            self.processor.import_string("test.fidl", """
                package P
                import model "nosuch.fidl"
            """)
        self.assertEqual(str(context.exception),
                         "Model 'nosuch.fidl' not found.")

    def test_import_nonexistent_model2(self):
        with self.assertRaises(ProcessorException) as context:
            self.processor.import_string("test.fidl", """
                package P
                import P.Nonexistent.* from "nosuch.fidl"
            """)
        self.assertEqual(str(context.exception),
                         "Model 'nosuch.fidl' not found.")

    def test_import_nonexistent_namespace(self):
        with self.assertRaises(ProcessorException) as context:
            self.processor.import_string("test.fidl", """
                package P
            """)
            self.processor.import_string("test2.fidl", """
                package P2
                import P.Nonexistent.* from "test.fidl"
            """)
        self.assertEqual(str(context.exception),
                         "Namespace 'P.Nonexistent.*' not found.")

    # TODO: Temporary file creation needed.
    # def test_circular_dependency(self):
    #     self.processor.import_string("test.fidl", """
    #         package P
    #
    #         import P2
    #     """)
    #     self.processor.import_string("test2.fidl", """
    #         package P2
    #
    #         import P
    #     """)


class TestUnsupported(BaseTestCase):
    """Test that unsupported Franca features fail appropriately."""

    def test_package_in_multiple_files(self):
        with self.assertRaises(ProcessorException) as context:
            self.processor.import_string("test.fidl", """
                package P
            """)
            self.processor.import_string("test2.fidl", """
                package P
            """)
        self.assertEqual(str(context.exception),
                         "Package 'P' defined in multiple files.")


class TestReferences(BaseTestCase):
    """Test type references."""

    def test_reference_to_same_namespace(self):
        self.processor.import_string("test.fidl", """
            package P
            typeCollection TC {
                typedef A is Int32
                typedef B is A
            }
        """)
        a = self.processor.packages["P"].typecollections["TC"].typedefs["A"]
        self.assertTrue(isinstance(a.type, ast.Int32))
        b = self.processor.packages["P"].typecollections["TC"].typedefs["B"]
        self.assertTrue(isinstance(b.type, ast.Reference))
        self.assertEqual(b.type.name, "A")
        self.assertEqual(b.type.reference, a)

    def test_fqn_reference(self):
        self.processor.import_string("test.fidl", """
            package P
            typeCollection TC {
                typedef A is Int32
                typedef B is P.TC.A
            }
        """)
        a = self.processor.packages["P"].typecollections["TC"].typedefs["A"]
        self.assertTrue(isinstance(a.type, ast.Int32))
        b = self.processor.packages["P"].typecollections["TC"].typedefs["B"]
        self.assertTrue(isinstance(b.type, ast.Reference))
        self.assertEqual(b.type.name, "P.TC.A")
        self.assertEqual(b.type.reference, a)

    def test_reference_to_different_namespace(self):
        self.processor.import_string("test.fidl", """
            package P
            typeCollection TC {
                typedef A is Int32
            }
            interface I {
                typedef B is A
            }
        """)
        a = self.processor.packages["P"].typecollections["TC"].typedefs["A"]
        self.assertTrue(isinstance(a.type, ast.Int32))
        b = self.processor.packages["P"].interfaces["I"].typedefs["B"]
        self.assertTrue(isinstance(b.type, ast.Reference))
        self.assertEqual(b.type.name, "A")
        self.assertEqual(b.type.reference, a)

    def test_reference_to_different_model(self):
        self.processor.import_string("test.fidl", """
            package P
            typeCollection TC {
                typedef A is Int32
            }
        """)
        self.processor.import_string("test2.fidl", """
            package P2
            import P.TC.* from "test.fidl"
            interface I {
                typedef B is A
            }
        """)
        a = self.processor.packages["P"].typecollections["TC"].typedefs["A"]
        self.assertTrue(isinstance(a.type, ast.Int32))
        b = self.processor.packages["P2"].interfaces["I"].typedefs["B"]
        self.assertTrue(isinstance(b.type, ast.Reference))
        self.assertEqual(b.type.name, "A")
        self.assertEqual(b.type.reference, a)

    @unittest.skip("Currently not checked.")
    def test_circular_reference(self):
        with self.assertRaises(ProcessorException) as context:
            self.processor.import_string("test.fidl", """
                package P
                typeCollection TC {
                    typedef A is B
                    typedef B is A
                }
            """)
        self.assertEqual(str(context.exception),
                         "Circular reference 'B'.")

    def test_reference_priority(self):
        self.processor.import_string("test.fidl", """
            package P
            typeCollection TC {
                typedef A is Int32
            }
        """)
        self.processor.import_string("test2.fidl", """
            package P2
            import P.TC.* from "test.fidl"
            typeCollection TC {
                typedef A is UInt32
            }
            interface I {
                typedef B is A
                typedef B2 is P.TC.A
            }
        """)
        a = self.processor.packages["P"].typecollections["TC"].typedefs["A"]
        self.assertTrue(isinstance(a.type, ast.Int32))
        a2 = self.processor.packages["P2"].typecollections["TC"].typedefs["A"]
        self.assertTrue(isinstance(a2.type, ast.UInt32))
        b = self.processor.packages["P2"].interfaces["I"].typedefs["B"]
        self.assertTrue(isinstance(b.type, ast.Reference))
        self.assertEqual(b.type.name, "A")
        self.assertEqual(b.type.reference, a2)
        b2 = self.processor.packages["P2"].interfaces["I"].typedefs["B2"]
        self.assertTrue(isinstance(b2.type, ast.Reference))
        self.assertEqual(b2.type.name, "P.TC.A")
        self.assertEqual(b2.type.reference, a)

    def test_interface_visibility(self):
        self.processor.import_string("test.fidl", """
            package P
            typeCollection TC {
                typedef A is Int32
            }
        """)
        self.processor.import_string("test2.fidl", """
            package P2
            import P.TC.* from "test.fidl"
            interface I {
                typedef A is UInt32
            }
            typeCollection TC {
                typedef B is A
            }
        """)
        a = self.processor.packages["P"].typecollections["TC"].typedefs["A"]
        self.assertTrue(isinstance(a.type, ast.Int32))
        a2 = self.processor.packages["P2"].interfaces["I"].typedefs["A"]
        self.assertTrue(isinstance(a2.type, ast.UInt32))
        b = self.processor.packages["P2"].typecollections["TC"].typedefs["B"]
        self.assertTrue(isinstance(b.type, ast.Reference))
        self.assertEqual(b.type.name, "A")
        self.assertEqual(b.type.reference, a)

    def test_unresolved_reference_in_typedef(self):
        with self.assertRaises(ProcessorException) as context:
            self.processor.import_string("test.fidl", """
                package P
                typeCollection TC {
                    typedef TD is Unknown
                }
            """)
        self.assertEqual(str(context.exception),
                         "Unresolved reference 'Unknown'.")

    def test_unresolved_reference_in_struct(self):
        with self.assertRaises(ProcessorException) as context:
            self.processor.import_string("test.fidl", """
                package P
                typeCollection TC {
                    struct S {
                        Unknown f
                    }
                }
            """)
        self.assertEqual(str(context.exception),
                         "Unresolved reference 'Unknown'.")

    def test_unresolved_reference_in_array(self):
        with self.assertRaises(ProcessorException) as context:
            self.processor.import_string("test.fidl", """
                package P
                typeCollection TC {
                    array A of Unknown
                }
            """)
        self.assertEqual(str(context.exception),
                         "Unresolved reference 'Unknown'.")

    def test_unresolved_reference_in_map(self):
        with self.assertRaises(ProcessorException) as context:
            self.processor.import_string("test.fidl", """
                package P
                typeCollection TC {
                    map M { Unknown to Int32 }
                }
            """)
        self.assertEqual(str(context.exception),
                         "Unresolved reference 'Unknown'.")

    def test_unresolved_reference_in_map2(self):
        with self.assertRaises(ProcessorException) as context:
            self.processor.import_string("test.fidl", """
                package P
                typeCollection TC {
                    map M { Int32 to Unknown }
                }
            """)
        self.assertEqual(str(context.exception),
                         "Unresolved reference 'Unknown'.")

    def test_unresolved_reference_in_attribute(self):
        with self.assertRaises(ProcessorException) as context:
            self.processor.import_string("test.fidl", """
                package P
                interface I {
                    attribute Unknown A
                }
            """)
        self.assertEqual(str(context.exception),
                         "Unresolved reference 'Unknown'.")

    def test_unresolved_reference_in_method(self):
        with self.assertRaises(ProcessorException) as context:
            self.processor.import_string("test.fidl", """
                package P
                interface I {
                    method M { in { Unknown a } }
                }
            """)
        self.assertEqual(str(context.exception),
                         "Unresolved reference 'Unknown'.")

    def test_unresolved_reference_in_method2(self):
        with self.assertRaises(ProcessorException) as context:
            self.processor.import_string("test.fidl", """
                package P
                interface I {
                    method M { out { Unknown a } }
                }
            """)
        self.assertEqual(str(context.exception),
                         "Unresolved reference 'Unknown'.")

    def test_unresolved_reference_in_method3(self):
        with self.assertRaises(ProcessorException) as context:
            self.processor.import_string("test.fidl", """
                package P
                interface I {
                    method M { error Unknown }
                }
            """)
        self.assertEqual(str(context.exception),
                         "Unresolved reference 'Unknown'.")

    def test_unresolved_reference_in_broadcast(self):
        with self.assertRaises(ProcessorException) as context:
            self.processor.import_string("test.fidl", """
                package P
                interface I {
                    broadcast B { out { Unknown a } }
                }
            """)
        self.assertEqual(str(context.exception),
                         "Unresolved reference 'Unknown'.")
