import unittest
import pandas as pd
from app import borrow_length, clean_dates




class TestOperations(unittest.TestCase):

    def test_valid_dates(self):
        df = pd.DataFrame({"checkout": ["01/06/2026", "15/06/2026", "not a date"]}, dtype="string")

        clean, failed = clean_dates(df, "checkout")

        self.assertEqual(len(clean),2)
        self.assertTrue(failed.empty)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(clean["checkout"]))
    
    def test_invalid_dates(self):
        df =pd.DataFrame({"checkout": ["01/06/2026", "32/06/2026"]}, dtype="string")

        clean, failed = clean_dates(df, "checkout")

        self.assertEqual(len(clean),1)
        self.assertEqual(len(failed),2)

    def test_no_negative_borrow(self):
        df = pd.DataFrame({"out": pd.to_datetime(["01/06/2026", "15/06/2026"], format="%d/%m/%Y"),
                         "back": pd.to_datetime(["10/06/2026", "01/06/2026"], format="%d/%m/%Y"),})
        
        clean, failed = borrow_length(df, "out", "back")

        self.assertTrue((clean["days_borrowed"]>= 0).all())
        self.assertEqual(len(failed), 1)

if __name__ == "__main__":
    unittest.main(verbosity=2)



