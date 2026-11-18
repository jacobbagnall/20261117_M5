import unittest
from calculator import calculatour


class TestOperations(unittest.TestCase):

    def setUp(self):
        self.calc =calculatour(8,2)

    
    def test_sum(self):
        self.assertEqual(self.calc.get_sum(),10,"sum wrong"
