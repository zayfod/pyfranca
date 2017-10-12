"""
PyFranca Franca IDL compliance tests.
"""

import os
import unittest
import subprocess
import shlex

from pyfranca import ProcessorException
from test_franca_processor import BaseTestCase


# TODO: Work in progress.
ENABLED = os.environ.get('PYFRANCA_COMPLIANCE_TESTS')

FRANCA_DIR = os.path.join("pyfranca", "tests", "franca")
FRANCA_TAG = "v0.11.1"


# noinspection PyPep8Naming
def setUpModule():
    if not os.path.exists(FRANCA_DIR):
        args = shlex.split("git clone --branch {} https://github.com/franca/franca {}".format(FRANCA_TAG, FRANCA_DIR))
        subprocess.check_call(args)


class BaseComplianceTestCase(BaseTestCase):

    MODEL_DIR = "."

    def _import_model(self, fname):
        fspec = os.path.join(self.MODEL_DIR, fname)
        self.processor.import_file(fspec)


@unittest.skipUnless(ENABLED, "Compliance tests disabled.")
class TestReference(BaseComplianceTestCase):
    """Test parsing reference models"""

    MODEL_DIR = os.path.join(FRANCA_DIR, "examples", "org.franca.examples.reference", "models", "org", "reference")

    def test_10_TypesInTypeCollection(self):
        self._import_model("10-TypesInTypeCollection.fidl")

    def test_15_InterTypeCollection(self):
        self._import_model("15-InterTypeCollection.fidl")

    def test_30_PrimitiveConstants(self):
        self._import_model("30-PrimitiveConstants.fidl")

    @unittest.skip("Complex constants not supported.")
    def test_32_ComplexConstants(self):
        self._import_model("32-ComplexConstants.fidl")

    @unittest.skip("Complex constants not supported.")
    def test_35_ImplicitArrayConstants(self):
        self._import_model("35-ImplicitArrayConstants.fidl")

    def test_60_Interface(self):
        self._import_model("60-Interface.fidl")

    def test_61_Interface(self):
        self._import_model("61-Interface.fidl")

    def test_65_InterfaceUsingTypeCollection(self):
        self._import_model("65-InterfaceUsingTypeCollection.fidl")

    @unittest.skip("Method overloading not supported.")
    def test_70_Overloading(self):
        self._import_model("70-Overloading.fidl")

    @unittest.skip("Method overloading not supported.")
    def test_71_Overloading(self):
        self._import_model("71-Overloading.fidl")

    @unittest.skip("Contracts not supported.")
    def test_80_Contract(self):
        self._import_model("80-Contract.fidl")


@unittest.skipUnless(ENABLED, "Compliance tests disabled.")
class TestDSLTests(BaseComplianceTestCase):
    """Test parsing invalid models"""

    MODEL_DIR = os.path.join(FRANCA_DIR, "tests", "org.franca.core.dsl.tests",
                             "src", "org", "franca", "core", "dsl", "tests", "xpect")

    def _import_model(self, fname):
        fspec = os.path.join(self.MODEL_DIR, fname)
        self.processor.import_file(fspec)

    def test_CyclicDependendyValidationTests(self):
        with self.assertRaises(ProcessorException):
            self._import_model("CyclicDependendyValidationTests.fidl.xt")

    def test_ErrorsWhenUsingErrorValuesInExpressions(self):
        with self.assertRaises(ProcessorException):
            self._import_model("ErrorsWhenUsingErrorValuesInExpressions.fidl.xt")

    def test_ErrorsWhenUsingTypesInsteadOfBooleans(self):
        with self.assertRaises(ProcessorException):
            self._import_model("ErrorsWhenUsingTypesInsteadOfBooleans.fidl.xt")

    def test_ErrorsWithErrorKeywordsUsedInsteadOfBooleans(self):
        with self.assertRaises(ProcessorException):
            self._import_model("ErrorsWithErrorKeywordsUsedInsteadOfBooleans.fidl.xt")

    def test_HiddenEnumeratorTests(self):
        with self.assertRaises(ProcessorException):
            self._import_model("HiddenEnumeratorTests.fidl.xt")

    def test_InterfaceDeprecatedOrderTests(self):
        with self.assertRaises(ProcessorException):
            self._import_model("InterfaceDeprecatedOrderTests.fidl.xt")

    def test_InterfaceValidationTests(self):
        with self.assertRaises(ProcessorException):
            self._import_model("InterfaceValidationTests.fidl.xt")

    def test_NameCollision0Tests(self):
        with self.assertRaises(ProcessorException):
            self._import_model("NameCollision0Tests.fidl.xt")

    def test_NameCollision1Tests(self):
        with self.assertRaises(ProcessorException):
            self._import_model("NameCollision1Tests.fidl.xt")

    def test_NameCollision2Tests(self):
        with self.assertRaises(ProcessorException):
            self._import_model("NameCollision2Tests.fidl.xt")

    def test_OverloadingTests(self):
        with self.assertRaises(ProcessorException):
            self._import_model("OverloadingTests.fidl.xt")

    def test_PublicTypes(self):
        with self.assertRaises(ProcessorException):
            self._import_model("PublicTypes.fidl.xt")

    def test_TypeValidationTests(self):
        with self.assertRaises(ProcessorException):
            self._import_model("TypeValidationTests.fidl.xt")

    def test_TypedElementRefs(self):
        with self.assertRaises(ProcessorException):
            self._import_model("TypedElementRefs.fidl.xt")

    def test_UsingConstantsB(self):
        with self.assertRaises(ProcessorException):
            self._import_model("UsingConstantsB.fidl.xt")

    def test_UsingConstantsC(self):
        with self.assertRaises(ProcessorException):
            self._import_model("UsingConstantsC.fidl.xt")

    def test_UsingConstantsD(self):
        with self.assertRaises(ProcessorException):
            self._import_model("UsingConstantsD.fidl.xt")

    def test_UsingConstantsE(self):
        with self.assertRaises(ProcessorException):
            self._import_model("UsingConstantsE.fidl.xt")

    def test_UsingConstantsF(self):
        with self.assertRaises(ProcessorException):
            self._import_model("UsingConstantsF.fidl.xt")

    def test_UsingTypesB(self):
        with self.assertRaises(ProcessorException) as context:
            self._import_model("UsingTypesB.fidl.xt")
        self.assertEqual(str(context.exception), "Unresolved reference 'BIF1.BIF1_Struct_1'.")

    def test_UsingTypesC(self):
        with self.assertRaises(ProcessorException):
            self._import_model("UsingTypesC.fidl.xt")

    def test_UsingTypesD(self):
        with self.assertRaises(ProcessorException):
            self._import_model("UsingTypesD.fidl.xt")

    def test_UsingTypesE(self):
        with self.assertRaises(ProcessorException):
            self._import_model("UsingTypesE.fidl.xt")

    def test_UsingTypesF(self):
        with self.assertRaises(ProcessorException):
            self._import_model("UsingTypesF.fidl.xt")
