"""
Pyfranca processor tests.
"""

import unittest
import os
import shutil

from pyfranca import ProcessorException, Processor, ast


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.processor = Processor()

    def tearDown(self):
        self.processor = None

        #remove temporary fidl files
        shutil.rmtree(self.get_fidl_dir(), ignore_errors=True)

    def get_fidl_dir(self, basedir="tmp"):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        fidl_dir = os.path.join(script_dir, "fidl", basedir)
        return fidl_dir

    def import_string(self, filename, content):
        fidl_dir = self.get_fidl_dir()
        filepath = os.path.join(fidl_dir, filename)

        os.makedirs(fidl_dir, exist_ok=True)

        # create fidl
        f = open(filepath, 'w')
        f.write(content)
        f.close()

        self.processor.package_paths.append(fidl_dir)
        self.processor.import_file(filepath)


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
        self.import_string("test.fidl", """
            package P
        """)
        self.import_string("test2.fidl", """
            package P2
        """)
        # Verify file access
        self.assertEqual(len(self.processor.files), 2)
        file_test = os.path.join(self.get_fidl_dir(), "test.fidl")
        file_test2 = os.path.join(self.get_fidl_dir(), "test2.fidl")

        p = self.processor.files[file_test]
        self.assertEqual(p.name, "P")
        self.assertEqual(p.files, [file_test])
        p2 = self.processor.files[file_test2]
        self.assertEqual(p2.name, "P2")
        self.assertEqual(p2.files, [file_test2])
        # Verify package access
        self.assertEqual(len(self.processor.packages), 2)
        p = self.processor.packages["P"]
        self.assertEqual(p.name, "P")
        p2 = self.processor.packages["P2"]
        self.assertEqual(p2.name, "P2")

    def test_import_nonexistent_model(self):
        with self.assertRaises(ProcessorException) as context:
            self.import_string("test.fidl", """
                package P
                import model "nosuch.fidl"
            """)
        self.assertEqual(str(context.exception),
                         "Model 'nosuch.fidl' not found.")

    def test_import_nonexistent_model2(self):
        with self.assertRaises(ProcessorException) as context:
            self.import_string("test.fidl", """
                package P
                import P.Nonexistent.* from "nosuch.fidl"
            """)
        self.assertEqual(str(context.exception),
                         "Model 'nosuch.fidl' not found.")

    def test_import_nonexistent_namespace(self):
        with self.assertRaises(ProcessorException) as context:
            self.import_string("test.fidl", """
                package P
            """)
            self.import_string("test2.fidl", """
                package P2
                import P.Nonexistent.* from "test.fidl"
            """)
        self.assertEqual(str(context.exception),
                         "Namespace 'P.Nonexistent.*' not found.")

    # TODO: Temporary file creation needed.
    # def test_circular_dependency(self):
    #     self.import_string("test.fidl", """
    #         package P
    #
    #         import P2
    #     """)
    #     self.import_string("test2.fidl", """
    #         package P2
    #
    #         import P
    #     """)


class TestPackagesInMultipleFiles(BaseTestCase):
    """Support for packages in multiple files"""

    def test_package_in_multiple_files(self):
        self.import_string("test.fidl", """
            package P
        """)
        self.import_string("test2.fidl", """
            package P
        """)
        p = self.processor.packages["P"]
        file_test = os.path.join(self.get_fidl_dir(), "test.fidl")
        file_test2 = os.path.join(self.get_fidl_dir(), "test2.fidl")
        self.assertEqual(p.files, [file_test, file_test2])

    def test_package_in_multiple_files_reuse(self):
        self.import_string("test.fidl", """
            package P
            typeCollection TC {
                typedef A is Int32
            }
        """)
        self.import_string("test2.fidl", """
            package P
            import P.TC.* from "test.fidl"
            interface I {
                typedef B is A
            }
        """)

        file_test = os.path.join(self.get_fidl_dir(), "test.fidl")
        file_test2 = os.path.join(self.get_fidl_dir(), "test2.fidl")

        p = self.processor.packages["P"]
        self.assertEqual(p.files, [file_test, file_test2])
        a = p.typecollections["TC"].typedefs["A"]
        self.assertEqual(a.namespace.package, p)
        self.assertTrue(isinstance(a.type, ast.Int32))
        b = p.interfaces["I"].typedefs["B"]
        self.assertEqual(b.namespace.package, p)
        self.assertTrue(isinstance(b.type, ast.Reference))
        self.assertEqual(b.type.name, "A")
        self.assertEqual(b.type.reference, a)


class TestReferences(BaseTestCase):
    """Test type references."""

    def test_reference_to_same_namespace(self):
        self.import_string("test.fidl", """
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
        self.import_string("test.fidl", """
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
        self.import_string("test.fidl", """
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
        self.import_string("test.fidl", """
            package P
            typeCollection TC {
                typedef A is Int32
            }
        """)
        self.import_string("test2.fidl", """
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
            self.import_string("test.fidl", """
                package P
                typeCollection TC {
                    typedef A is B
                    typedef B is A
                }
            """)
        self.assertEqual(str(context.exception),
                         "Circular reference 'B'.")

    def test_reference_priority(self):
        self.import_string("test.fidl", """
            package P
            typeCollection TC {
                typedef A is Int32
            }
        """)
        self.import_string("test2.fidl", """
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
        self.import_string("test.fidl", """
            package P
            typeCollection TC {
                typedef A is Int32
            }
        """)
        self.import_string("test2.fidl", """
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
            self.import_string("test.fidl", """
                package P
                typeCollection TC {
                    typedef TD is Unknown
                }
            """)
        self.assertEqual(str(context.exception),
                         "Unresolved reference 'Unknown'.")

    def test_unresolved_reference_in_struct(self):
        with self.assertRaises(ProcessorException) as context:
            self.import_string("test.fidl", """
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
            self.import_string("test.fidl", """
                package P
                typeCollection TC {
                    array A of Unknown
                }
            """)
        self.assertEqual(str(context.exception),
                         "Unresolved reference 'Unknown'.")

    def test_unresolved_reference_in_map(self):
        with self.assertRaises(ProcessorException) as context:
            self.import_string("test.fidl", """
                package P
                typeCollection TC {
                    map M { Unknown to Int32 }
                }
            """)
        self.assertEqual(str(context.exception),
                         "Unresolved reference 'Unknown'.")

    def test_unresolved_reference_in_map2(self):
        with self.assertRaises(ProcessorException) as context:
            self.import_string("test.fidl", """
                package P
                typeCollection TC {
                    map M { Int32 to Unknown }
                }
            """)
        self.assertEqual(str(context.exception),
                         "Unresolved reference 'Unknown'.")

    def test_unresolved_reference_in_attribute(self):
        with self.assertRaises(ProcessorException) as context:
            self.import_string("test.fidl", """
                package P
                interface I {
                    attribute Unknown A
                }
            """)
        self.assertEqual(str(context.exception),
                         "Unresolved reference 'Unknown'.")

    def test_unresolved_reference_in_method(self):
        with self.assertRaises(ProcessorException) as context:
            self.import_string("test.fidl", """
                package P
                interface I {
                    method M { in { Unknown a } }
                }
            """)
        self.assertEqual(str(context.exception),
                         "Unresolved reference 'Unknown'.")

    def test_unresolved_reference_in_method2(self):
        with self.assertRaises(ProcessorException) as context:
            self.import_string("test.fidl", """
                package P
                interface I {
                    method M { out { Unknown a } }
                }
            """)
        self.assertEqual(str(context.exception),
                         "Unresolved reference 'Unknown'.")

    def test_unresolved_reference_in_method3(self):
        with self.assertRaises(ProcessorException) as context:
            self.import_string("test.fidl", """
                package P
                interface I {
                    method M { error Unknown }
                }
            """)
        self.assertEqual(str(context.exception),
                         "Unresolved reference 'Unknown'.")

    def test_unresolved_reference_in_broadcast(self):
        with self.assertRaises(ProcessorException) as context:
            self.import_string("test.fidl", """
                package P
                interface I {
                    broadcast B { out { Unknown a } }
                }
            """)
        self.assertEqual(str(context.exception),
                         "Unresolved reference 'Unknown'.")

    def test_method_error_reference(self):
        self.import_string("test.fidl", """
            package P
            interface I {
                enumeration E { A B C }
                method M { error E }
            }
        """)
        e = self.processor.packages["P"].interfaces["I"].enumerations["E"]
        m = self.processor.packages["P"].interfaces["I"].methods["M"]
        me = m.errors
        self.assertTrue(isinstance(me, ast.Reference))
        self.assertEqual(me.reference, e)

    def test_invalid_method_error_reference(self):
        with self.assertRaises(ProcessorException) as context:
            self.import_string("test.fidl", """
                package P
                interface I {
                    typedef E is String
                    method M { error E }
                }
            """)
        self.assertEqual(str(context.exception),
                         "Invalid error reference 'E'.")

    def test_enumeration_extension(self):
        self.import_string("test.fidl", """
            package P
            interface I {
                enumeration E { A B C }
                enumeration E2 extends E { D E F }
            }
        """)
        e = self.processor.packages["P"].interfaces["I"].enumerations["E"]
        e2 = self.processor.packages["P"].interfaces["I"].enumerations["E2"]
        self.assertEqual(e2.reference, e)

    def test_invalid_enumeration_extension(self):
        with self.assertRaises(ProcessorException) as context:
            self.import_string("test.fidl", """
                package P
                interface I {
                    typedef E is String
                    enumeration E2 extends E { D E F }
                }
            """)
        self.assertEqual(str(context.exception),
                         "Invalid enumeration reference 'E'.")

    def test_struct_extension(self):
        self.import_string("test.fidl", """
            package P
            interface I {
                struct S { Int32 a }
                struct S2 extends S { Int32 b }
            }
        """)
        s = self.processor.packages["P"].interfaces["I"].structs["S"]
        s2 = self.processor.packages["P"].interfaces["I"].structs["S2"]
        self.assertEqual(s2.reference, s)

    def test_invalid_struct_extension(self):
        with self.assertRaises(ProcessorException) as context:
            self.import_string("test.fidl", """
                package P
                interface I {
                    typedef S is String
                    struct S2 extends S { Int32 b }
                }
            """)
        self.assertEqual(str(context.exception),
                         "Invalid struct reference 'S'.")

    def test_interface_extension(self):
        self.import_string("test.fidl", """
            package P
            interface I { }
            interface I2 extends I { }
            interface I3 extends P.I { }
        """)
        i = self.processor.packages["P"].interfaces["I"]
        i2 = self.processor.packages["P"].interfaces["I2"]
        self.assertEqual(i2.reference, i)
        i3 = self.processor.packages["P"].interfaces["I3"]
        self.assertEqual(i3.reference, i)

    def test_interface_extension2(self):
        self.import_string("test.fidl", """
            package P
            interface I { }
        """)
        self.import_string("test2.fidl", """
            package P2
            import model "test.fidl"
            interface I2 extends I { }
            interface I3 extends P.I { }
        """)
        i = self.processor.packages["P"].interfaces["I"]
        i2 = self.processor.packages["P2"].interfaces["I2"]
        self.assertEqual(i2.reference, i)
        i3 = self.processor.packages["P2"].interfaces["I3"]
        self.assertEqual(i3.reference, i)

    def test_invalid_interface_extension(self):
        with self.assertRaises(ProcessorException) as context:
            self.import_string("test.fidl", """
                package P
                typeCollection TC { typedef I is Int32 }
                interface I2 extends I { }
            """)
        self.assertEqual(str(context.exception),
                         "Unresolved namespace reference 'I'.")

    def test_anonymous_array_references(self):
        self.import_string("test.fidl", """
            package P
            typeCollection TC {
                typedef TD is Int32
                typedef TDA is TD[]
                array ATDA of TD[]
                struct S { TD[] tda }
                map M { TD[] to TD[] }
            }
            interface I {
                attribute TD[] A
                method M { in { TD[] tda } out { TD[] tda } }
                broadcast B { out { TD[] tda } }
            }
        """)
        tc = self.processor.packages["P"].typecollections["TC"]
        td = tc.typedefs["TD"]
        tda = tc.typedefs["TDA"]
        self.assertEqual(tda.type.type.reference, td)
        atda = tc.arrays["ATDA"]
        self.assertEqual(atda.type.type.reference, td)
        s = tc.structs["S"]
        self.assertEqual(s.fields["tda"].type.type.reference, td)
        m = tc.maps["M"]
        self.assertEqual(m.key_type.type.reference, td)
        self.assertEqual(m.value_type.type.reference, td)
        i = self.processor.packages["P"].interfaces["I"]
        a = i.attributes["A"]
        self.assertEqual(a.type.type.reference, td)
        m = i.methods["M"]
        self.assertEqual(m.in_args["tda"].type.type.reference, td)
        self.assertEqual(m.out_args["tda"].type.type.reference, td)
        b = i.broadcasts["B"]
        self.assertEqual(b.out_args["tda"].type.type.reference, td)

    def test_import_missing_files(self):
        # P.fidl references definitions.fidl but it is not in the package path.
        with self.assertRaises(ProcessorException) as context:
            self.processor.import_file(
                os.path.join(self.get_fidl_dir("idl"), "P.fidl"))
            self.processor.import_file(
                os.path.join(self.get_fidl_dir("idl2"), "P2.fidl"))
        self.assertEqual(str(context.exception),
                         "Model 'definitions.fidl' not found.")

    def test_import_multiple_files(self):
        fidl_dir = self.get_fidl_dir("idl")
        self.processor.package_paths.append(fidl_dir)
        self.processor.import_file(
            os.path.join("P.fidl"))
        self.processor.import_file(
            os.path.join(self.get_fidl_dir("idl2"), "P2.fidl"))

    def test_import_files_chain(self):
        filepath = os.path.join(self.get_fidl_dir("ImportChain"), "P.fidl")
        self.processor.import_file(filepath)


    def test_import_files_complex_chain(self):
        p3path = os.path.join(self.get_fidl_dir("ImportComplexChain"), "P3")
        p2path = os.path.join(self.get_fidl_dir("ImportComplexChain"), "P2")
        ppath = os.path.join(self.get_fidl_dir("ImportComplexChain"), "P")
        self.processor.package_paths.append(p3path)
        self.processor.package_paths.append(p2path)

        filepath = os.path.join(ppath, "P.fidl")
        self.processor.import_file(filepath)

        self.assertEqual(self.processor.packages["P"].name, "P")
        self.assertEqual(self.processor.packages["P"].imports[0].package_reference, self.processor.packages["P2"])
        self.assertEqual(self.processor.packages["P"].imports[0].package_reference.imports[0].package_reference, self.processor.packages["P3"])
        self.assertEqual(self.processor.packages["P2"].name, "P2")
        self.assertEqual(self.processor.packages["P3"].name, "P3")

        self.assertEqual(self.processor.packages['P'].interfaces["I"].methods["getData"].
                         out_args["p3data"].type.reference.namespace.name, "P3Types")
        self.assertEqual(self.processor.packages['P'].interfaces["I"].methods["getData"].
                         out_args["p3data"].type.reference.namespace.package.name, "P3")

        self.assertEqual(self.processor.packages['P'].interfaces["I"].methods["getData"].
                         out_args["p2data"].type.reference.namespace.name, "P2Types")
        self.assertEqual(self.processor.packages['P'].interfaces["I"].methods["getData"].
                         out_args["p2data"].type.reference.namespace.package.name, "P2")

        self.assertEqual(self.processor.packages['P'].interfaces["I"].methods["getData"].
                         out_args["pdata"].type.reference.namespace.name, "Common")
        self.assertEqual(self.processor.packages['P'].interfaces["I"].methods["getData"].
                         out_args["pdata"].type.reference.namespace.package.name, "P")

        self.assertEqual(self.processor.packages['P'].interfaces["I"].methods["getData"].
                         out_args["outVal"].type.reference.namespace.name, "Type1")
        self.assertEqual(self.processor.packages['P'].interfaces["I"].methods["getData"].
                         out_args["outVal"].type.reference.namespace.package.name, "P")

        self.assertEqual(self.processor.packages['P'].typecollections["Common"].structs["PStruct"].
                         fields["p2data"].type.reference.namespace.name, "P2Types")
        self.assertEqual(self.processor.packages['P'].typecollections["Common"].structs["PStruct"].
                         fields["p2data"].type.reference.namespace.package.name, "P2")

        self.assertEqual(self.processor.packages['P2'].typecollections["P2Types"].structs["P2Struct"].
                         fields["p3data"].type.reference.namespace.name, "P3Types")
        self.assertEqual(self.processor.packages['P2'].typecollections["P2Types"].structs["P2Struct"].
                         fields["p3data"].type.reference.namespace.package.name, "P3")
