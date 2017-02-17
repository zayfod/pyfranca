
import unittest


def get_suite():
    """Returns a unittest.TestSuite."""
    loader = unittest.TestLoader()
    suite = loader.discover(".")
    return suite
