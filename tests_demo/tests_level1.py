import unittest
from calculator import calculatour


class TestOperations(unittest.TestCase):
    
    def test_sum(self):
        #arrange
        testCal = calculatour(8,2)
        #act & assert
        self.assertEqual(testCal.get_sum(), 10, "the sum is wrong")

    def test_mins(self):
        #arrange
        testCal = calculatour(8,2)
        #act & assert
        self.assertEqual(testCal.get_mins(), 6, "the muns is wrong")

    def test_dev(self):
        #arrange
        testCal = calculatour(8,2)
        #act & assert
        self.assertEqual(testCal.get_div(), 4, "the dev is wrong")

    def test_muti(self):
        #arrange
        testCal = calculatour(8,2)
        #act & assert
        self.assertEqual(testCal.get_muit(), 16, "the muti is wrong")

if __name__ == "__main__":
    unittest.main()