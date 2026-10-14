import unittest
from calculation import total
class Tests(unittest.TestCase):
    def test_total(self): self.assertEqual(total(7,3),21)
