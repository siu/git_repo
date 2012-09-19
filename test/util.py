import unittest

class BaseTestCase(unittest.TestCase):
    def assertEqualSet(self, first, second):
        self.assertEqual(set(first), set(second))

