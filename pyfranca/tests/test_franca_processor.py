"""
Pyfranca processor tests.
"""

import unittest
import os
import errno
import shutil

from pyfranca import ProcessorException, Processor, ast


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        # Create temporary file directory.
        tmp_dir = self.get_spec()
        try:
            os.makedirs(tmp_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
            # Delete and try again
            shutil.rmtree(tmp_dir)
            os.makedirs(tmp_dir)
        # Create FIDL processor.
        self.processor = Processor()
        self.processor.package_paths.append(tmp_dir)

    def tearDown(self):
        self.processor = None
        # Remove temporary file directory.
        tmp_dir = self.get_spec()
        shutil.rmtree(tmp_dir)

    @staticmethod
    def get_spec(basedir="tmp", filename=None):
        """
        Get absolute specification a directory or a file under pyfranca/tests/fidl/ .
        :param basedir: Target subdirectory.
        :param filename: File name or None to get a directory specification
        :return: Absolute specification.
        """
        script_dir = os.path.dirname(os.path.realpath(__file__))
        spec = os.path.join(script_dir, "fidl", basedir)
        if filename:
            spec = os.path.join(spec, filename)
        return spec

    def tmp_fidl(self, filename, content):
        fspec = self.get_spec(filename=filename)
        with open(fspec, "w") as f:
            f.write(content)
        return fspec

    def import_tmp_fidl(self, filename, content):
        fspec = self.tmp_fidl(filename, content)
        self.processor.import_file(fspec)


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
        self.assertEqual(p.files, ["test.fidl"])
        p2 = self.processor.files["test2.fidl"]
        self.assertEqual(p2.name, "P2")
        self.assertEqual(p2.files, ["test2.fidl"])
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

    def test_circular_dependency(self):
        fspec = self.tmp_fidl("test.fidl", """
            package P
            import model "test2.fidl"
        """)
        self.tmp_fidl("test2.fidl", """
            package P2
            import model "test.fidl"
        """)
        self.processor.import_file(fspec)
        # FIXME: What is the correct behavior?


class TestPackagesInMultipleFiles(BaseTestCase):
    """Support for packages in multiple files"""

    def test_package_in_multiple_files(self):
        self.processor.import_string("test.fidl", """
            package P
        """)
        self.processor.import_string("test2.fidl", """
            package P
        """)
        p = self.processor.packages["P"]
        self.assertEqual(p.files, ["test.fidl", "test2.fidl"])

    def test_package_in_multiple_files_reuse(self):
        self.processor.import_string("test.fidl", """
            package P
            typeCollection TC {
                typedef A is Int32
            }
        """)
        self.processor.import_string("test2.fidl", """
            package P
            import P.TC.* from "test.fidl"
            interface I {
                typedef B is A
            }
        """)
        p = self.processor.packages["P"]
        self.assertEqual(p.files, ["test.fidl", "test2.fidl"])
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

    def test_method_error_reference(self):
        self.processor.import_string("test.fidl", """
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
            self.processor.import_string("test.fidl", """
                package P
                interface I {
                    typedef E is String
                    method M { error E }
                }
            """)
        self.assertEqual(str(context.exception),
                         "Invalid error reference 'E'.")

    def test_enumeration_extension(self):
        self.processor.import_string("test.fidl", """
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
            self.processor.import_string("test.fidl", """
                package P
                interface I {
                    typedef E is String
                    enumeration E2 extends E { D E F }
                }
            """)
        self.assertEqual(str(context.exception),
                         "Invalid enumeration reference 'E'.")

    def test_struct_extension(self):
        self.processor.import_string("test.fidl", """
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
            self.processor.import_string("test.fidl", """
                package P
                interface I {
                    typedef S is String
                    struct S2 extends S { Int32 b }
                }
            """)
        self.assertEqual(str(context.exception),
                         "Invalid struct reference 'S'.")

    def test_interface_extension(self):
        self.processor.import_string("test.fidl", """
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
        self.processor.import_string("test.fidl", """
            package P
            interface I { }
        """)
        self.processor.import_string("test2.fidl", """
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
            self.processor.import_string("test.fidl", """
                package P
                typeCollection TC { typedef I is Int32 }
                interface I2 extends I { }
            """)
        self.assertEqual(str(context.exception),
                         "Unresolved namespace reference 'I'.")

    def test_anonymous_array_references(self):
        self.processor.import_string("test.fidl", """
            package P
            typeCollection TC {
                typedef TD is Int32
                typedef TDA is TD[]
                array ATDA of TD[]
                struct S { TD[] tda }
                map M { TD[] to TD[] }
                union U {S s}
                union UE extends U {ATDA a}
                const String foo = "bar"
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
        u = tc.unions["U"]
        self.assertEqual(u.fields["s"].name,"s")
        self.assertEqual(u.fields["s"].type.name,"S")
        ue = tc.unions["UE"]
        self.assertEqual(ue.fields["a"].name,"a")
        self.assertEqual(ue.fields["a"].type.name,"ATDA")
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
                os.path.join("pyfranca", "tests", "fidl", "idl", "P.fidl"))
            self.processor.import_file(
                os.path.join("pyfranca", "tests", "fidl", "idl2", "P2.fidl"))
        self.assertEqual(str(context.exception),
                         "Model 'definitions.fidl' not found.")

    def test_import_multiple_files(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        fidl_dir = os.path.join(script_dir, "fidl", "idl")
        self.processor.package_paths.append(fidl_dir)
        self.processor.import_file(
            os.path.join("P.fidl"))
        self.processor.import_file(
            os.path.join("pyfranca", "tests", "fidl", "idl2", "P2.fidl"))

    def test_import_file_chain(self):
        fspec = self.tmp_fidl("P.fidl", """
            package P
            import P.Type1.* from "Type1.fidl"
            import P.Type2.* from "Type2.fidl"
            interface I {
                version { major 1 minor 0 }
                method getData {
                    out {
                          MyStructType1 outVal
                       }
                    in {
                          MyStructType2 inVal
                       }
                }
            }
        """)
        self.tmp_fidl("Type1.fidl", """
            package P
            import P.Common.* from "common.fidl"
            typeCollection Type1 {
                version { major 1 minor 0 }
                struct MyStructType1 {
                    UInt8 val1
                    MyEnum val2
                    String  msg
                }
            }
        """)
        self.tmp_fidl("Type2.fidl", """
            package P
            import P.Common.* from "common.fidl"
            typeCollection Type2 {
                version { major 1 minor 0 }
                struct MyStructType2 {
                    UInt8 val1
                    MyEnum val2
                    String  msg
                }
            }
        """)
        self.tmp_fidl("common.fidl", """
            package P
            typeCollection Common {
                version { major 1 minor 0 }
                enumeration MyEnum {
                    abc
                    def
                    ghi
                    jkm
                }
            }
        """)
        self.processor.import_file(fspec)
